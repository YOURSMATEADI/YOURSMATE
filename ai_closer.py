from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Optional

import requests

# Optional third-party helpers
try:
    from nameparser import HumanName  # type: ignore
except ImportError:  # pragma: no cover
    HumanName = None  # type: ignore

try:
    from twilio.rest import Client as TwilioClient  # type: ignore
except ImportError:  # pragma: no cover
    TwilioClient = None  # type: ignore

try:
    import sendgrid  # type: ignore
    from sendgrid.helpers.mail import Mail
except ImportError:  # pragma: no cover
    sendgrid = None  # type: ignore
    Mail = None  # type: ignore

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CRM_WEBHOOK_URL: str | None = os.getenv("CRM_WEBHOOK_URL")
CALENDLY_LINK: str = os.getenv(
    "CALENDLY_LINK", "https://calendly.com/your-company/15min-demo"
)
FREE_DEMO_LINK: str = os.getenv(
    "FREE_DEMO_LINK", "https://your-company.com/free-demo"
)

FOLLOW_UP_DELAY_SECONDS = 60 * 60  # 1 hour

# SMS / Email / Notification
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")

# Internal notification (e.g., Slack webhook) for new leads
NOTIFICATION_WEBHOOK_URL = os.getenv("NOTIFICATION_WEBHOOK_URL")

# ---------------------------------------------------------------------------
# Conversation State Machine
# ---------------------------------------------------------------------------


class Stage(Enum):
    """High-level milestones in the conversation."""

    GREETING_SENT = auto()
    ASKED_Q1 = auto()
    ASKED_Q2 = auto()
    ASKED_Q3 = auto()
    SOLUTION_PITCHED = auto()
    CTA_SENT = auto()
    CLOSED = auto()


@dataclass
class Lead:
    """Data we capture about a prospect during the chat."""

    name: Optional[str] = None
    company: Optional[str] = None
    revenue: Optional[str] = None
    target_demos: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    lead_score: Optional[int] = None  # Calculated later

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name or "",
            "company": self.company or "",
            "revenue": self.revenue or "",
            "targetDemos": self.target_demos or "",
            "email": self.email or "",
            "phone": self.phone or "",
            "leadScore": str(self.lead_score or ""),
        }


@dataclass
class Conversation:
    """Holds the state of a single live chat."""

    lead: Lead = field(default_factory=Lead)
    stage: Stage = Stage.GREETING_SENT
    last_user_ts: float = field(default_factory=time.time)

    # ---------------------------------------------------------------------
    # Bot logic helpers
    # ---------------------------------------------------------------------

    def _log_to_crm(self, payload: Dict[str, str]) -> None:
        # Ensure leadScore is present
        if "leadScore" not in payload and self.lead.lead_score is not None:
            payload["leadScore"] = str(self.lead.lead_score)

        if not CRM_WEBHOOK_URL:
            # Skip if not configured (development mode)
            print("[debug] CRM webhook URL not set. Skipping log.")
            return
        try:
            response = requests.post(CRM_WEBHOOK_URL, json=payload, timeout=5)
            response.raise_for_status()
        except Exception as e:
            print(f"[error] Failed to log to CRM: {e}")

    # ---------------------------------------------------------------------
    # Public API — pass each user message here
    # ---------------------------------------------------------------------

    def on_user_message(self, message: str) -> str:
        """Main entry: returns bot reply based on current stage & user input."""

        self.last_user_ts = time.time()
        message_lower = message.lower()

        # Objection handling can happen at any stage post-pitch
        if self.stage in {Stage.SOLUTION_PITCHED, Stage.CTA_SENT}:
            if "too expensive" in message_lower or "budget" in message_lower:
                return self._handle_too_expensive()
            if "just browsing" in message_lower or "looking around" in message_lower:
                return self._handle_just_browsing()
            if any(word in message_lower for word in ["yes", "sure", "let's", "ready", "book"]):
                # Positive intent — send closing CTA straight away
                return self._send_cta()

        # Regular funnel progression
        if self.stage == Stage.GREETING_SENT:
            self.stage = Stage.ASKED_Q1
            return "What's your company name & your role?"

        if self.stage == Stage.ASKED_Q1:
            self._parse_company_role(message)
            self.stage = Stage.ASKED_Q2
            return "What's your current monthly revenue or lead volume?"

        if self.stage == Stage.ASKED_Q2:
            self.lead.revenue = message.strip()
            self.stage = Stage.ASKED_Q3
            return "How many demos or signups do you aim for each month?"

        if self.stage == Stage.ASKED_Q3:
            self.lead.target_demos = message.strip()
            self.stage = Stage.SOLUTION_PITCHED
            return self._present_solution()

        # After CTA sent, if user still interacts, we treat as done
        if self.stage == Stage.CTA_SENT:
            return "Great! Looking forward to speaking. Talk soon!"

        return "🤖 Sorry—I didn't catch that. Could you please rephrase?"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_company_role(self, text: str) -> None:
        """Attempt to extract name, company, email & phone from free-form answer."""

        # ---------------- Email & phone first ---------------- #
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.[a-z]{2,}", text, re.I)
        if email_match:
            self.lead.email = email_match.group(0)

        phone_match = re.search(r"(\+?\d[\d \-()]{7,}\d)", text)
        if phone_match:
            self.lead.phone = re.sub(r"[^0-9+]", "", phone_match.group(0))

        # ---------------- Name extraction -------------------- #
        if not self.lead.name:
            # Look for "I'm <name>" or "I am <name>" etc.
            name_pattern = re.search(
                r"(?:i\s*am|i'm|my\s*name\s*is)\s+([A-Z][A-Za-z\s\-']{1,40})",
                text,
                re.I,
            )
            if name_pattern:
                raw_name = name_pattern.group(1).strip()
                if HumanName:
                    self.lead.name = HumanName(raw_name).first
                else:
                    self.lead.name = raw_name.split()[0]

        # ---------------- Company extraction ----------------- #
        if not self.lead.company:
            company_pattern = re.search(
                r"(?:at|from|with|for|of)\s+([A-Z][\w &]+(?:\s(?:Inc|Corp|LLC|Ltd|Group|Labs|Systems|Technologies))?)",
                text,
            )
            if company_pattern:
                self.lead.company = company_pattern.group(1).strip()

        # Fallback heuristics if still missing
        if not self.lead.company:
            # pick sequence of 2-3 title-cased words that isn't the extracted name
            tokens = [t for t in text.split() if t.istitle()]
            if len(tokens) >= 2:
                guess = " ".join(tokens[:3])
                if guess.lower() != (self.lead.name or "").lower():
                    self.lead.company = guess

    def _present_solution(self) -> str:
        similar_company = self.lead.company or "a similar company"
        pitch = (
            f"We've helped {similar_company} add 500+ qualified leads/mo using our AI Sales "
            "Bot—built in 48 hrs."
        )
        # Compute lead score before logging
        self.lead.lead_score = self._compute_lead_score()
        # Send to CRM now that we have major info
        self._log_to_crm({
            **self.lead.to_dict(),
            "event": "solution_pitched",
            "timestamp": int(time.time()),
        })
        # Immediately follow with CTA
        cta = self._send_cta()
        return f"{pitch}\n\n{cta}"

    def _send_cta(self) -> str:
        self.stage = Stage.CTA_SENT
        msg = (
            f"Ready to lock in your first 100 leads? Book a 15-min strategy call here: "
            f"{CALENDLY_LINK}\nOnly 3 demo slots left this week."
        )
        # Final CRM update
        self._log_to_crm({
            **self.lead.to_dict(),
            "event": "cta_sent",
            "timestamp": int(time.time()),
        })
        return msg

    def _handle_too_expensive(self) -> str:
        return (
            "I understand budget matters. Our Ironclad Guarantee: no cost unless you see a "
            "5X ROI in 30 days."
        )

    def _handle_just_browsing(self) -> str:
        return (
            f"Totally—here's our free demo link: {FREE_DEMO_LINK}. Try it now & see 10–20 "
            "leads in your inbox by tomorrow."
        )

    # ------------------------------------------------------------------
    # Housekeeping utilities
    # ------------------------------------------------------------------

    def check_need_follow_up(self) -> Optional[str]:
        """Returns follow-up message if 1h passed without user response."""
        if self.stage != Stage.CTA_SENT:
            return None
        if time.time() - self.last_user_ts >= FOLLOW_UP_DELAY_SECONDS:
            self.stage = Stage.CLOSED
            follow_up = (
                "Still curious about our free AI demo? Reply 'YES' to get started."
            )
            # Log follow-up
            self._log_to_crm({
                **self.lead.to_dict(),
                "event": "follow_up_sent",
                "timestamp": int(time.time()),
            })
            # Send actual follow-up via SMS/Email if possible
            self._send_sms_email_followup(follow_up)
            # Notify internal team of new lead
            self._send_new_lead_notification()
            return follow_up
        return None

    # ---------------------- Lead intelligence --------------------------

    def _compute_lead_score(self) -> int:
        """Very simple heuristic scoring based on revenue & targets."""
        score = 0
        # Revenue buckets
        rev_num = self._normalize_number(self.lead.revenue)
        if rev_num is not None:
            if rev_num >= 1_000_000:
                score += 50
            elif rev_num >= 500_000:
                score += 30
            elif rev_num >= 100_000:
                score += 15
            else:
                score += 5

        # Target demos
        demos_num = self._normalize_number(self.lead.target_demos)
        if demos_num is not None:
            if demos_num >= 100:
                score += 50
            elif demos_num >= 50:
                score += 30
            elif demos_num >= 20:
                score += 15
            else:
                score += 5

        # Could add more factors (industry fit, etc.)
        return score

    @staticmethod
    def _normalize_number(text: Optional[str]) -> Optional[float]:
        if not text:
            return None
        cleaned = text.lower().replace(",", "").strip()
        match = re.search(r"([0-9]*\.?[0-9]+)", cleaned)
        if not match:
            return None
        num = float(match.group(1))
        if "k" in cleaned:
            num *= 1_000
        elif "m" in cleaned:
            num *= 1_000_000
        return num

    # -------------------- Communication helpers ---------------------- #

    def _send_sms_email_followup(self, body: str) -> None:
        """Try to send SMS and email follow-ups using configured providers."""
        # SMS via Twilio
        if (
            self.lead.phone
            and TwilioClient
            and TWILIO_ACCOUNT_SID
            and TWILIO_AUTH_TOKEN
            and TWILIO_FROM_NUMBER
        ):
            try:
                client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                client.messages.create(
                    to=self.lead.phone, from_=TWILIO_FROM_NUMBER, body=body
                )
            except Exception as e:
                print(f"[error] Failed to send SMS follow-up: {e}")

        # Email via SendGrid
        if (
            self.lead.email
            and sendgrid
            and Mail
            and SENDGRID_API_KEY
            and SENDGRID_FROM_EMAIL
        ):
            try:
                sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
                mail = Mail(
                    from_email=SENDGRID_FROM_EMAIL,
                    to_emails=self.lead.email,
                    subject="Quick follow-up: free AI lead demo",
                    plain_text_content=body,
                )
                sg.send(mail)
            except Exception as e:
                print(f"[error] Failed to send email follow-up: {e}")

    # -------------------- Lead notifications ------------------------ #

    def _send_new_lead_notification(self) -> None:
        """Notify internal team via webhook when chat closes."""
        if not NOTIFICATION_WEBHOOK_URL:
            print("[debug] No notification webhook configured.")
            return
        payload = {**self.lead.to_dict(), "event": "new_lead", "timestamp": int(time.time())}
        # Add quick context preview
        payload["summary"] = (
            f"{self.lead.name or 'Someone'} from {self.lead.company or '?'} – score "
            f"{self.lead.lead_score or 'n/a'}"
        )
        try:
            requests.post(NOTIFICATION_WEBHOOK_URL, json=payload, timeout=5)
        except Exception as e:
            print(f"[error] Failed to send new-lead notification: {e}")

    def mark_closed(self) -> None:
        """Explicitly close chat and fire new-lead notification."""
        if self.stage != Stage.CLOSED:
            self.stage = Stage.CLOSED
        self._send_new_lead_notification()


# ---------------------------------------------------------------------------
# Simple CLI runner for local testing
# ---------------------------------------------------------------------------

def _cli_chat():
    conv = Conversation()
    print(
        "🤖 Hi there! I'm your Yoursmate AI Closer—ready to help you scale. "
        "What's your biggest growth challenge today?"
    )
    while conv.stage != Stage.CLOSED:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\n[session terminated]")
            conv.mark_closed()
            break
        bot_reply = conv.on_user_message(user_input)
        print(f"Bot: {bot_reply}")
        # Check follow-up automatically
        followup = conv.check_need_follow_up()
        if followup:
            print(f"Bot (follow-up): {followup}")
            conv.mark_closed()
            break


if __name__ == "__main__":
    _cli_chat()