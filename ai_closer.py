from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Optional

import requests

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

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name or "",
            "company": self.company or "",
            "revenue": self.revenue or "",
            "targetDemos": self.target_demos or "",
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
        """Very naive extraction of name + company from free-form answer."""
        # Expect formats like "I'm John, CEO at Acme Corp" or "Acme Corp – VP Marketing John"
        name_match = re.search(r"i(?:'|\s)?m\s+([A-Z][a-z]+)", text, re.I)
        if name_match:
            self.lead.name = name_match.group(1)
        # Extract company (looking for capitalised words followed by Corp/Inc/etc or proper case words)
        company_match = re.search(r"at\s+([A-Z][\w &]+)", text)
        if company_match:
            self.lead.company = company_match.group(1).strip()
        else:
            # fallback: take first two title-cased words
            tokens = [t for t in text.split() if t.istitle()]
            if len(tokens) >= 2:
                self.lead.company = " ".join(tokens[:2])

    def _present_solution(self) -> str:
        similar_company = self.lead.company or "a similar company"
        pitch = (
            f"We've helped {similar_company} add 500+ qualified leads/mo using our AI Sales "
            "Bot—built in 48 hrs."
        )
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
            return follow_up
        return None


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
            break
        bot_reply = conv.on_user_message(user_input)
        print(f"Bot: {bot_reply}")
        # Check follow-up automatically
        followup = conv.check_need_follow_up()
        if followup:
            print(f"Bot (follow-up): {followup}")
            break


if __name__ == "__main__":
    _cli_chat()