import sqlite3
import time
import requests
import json
import uuid
from datetime import datetime, timedelta

class FollowUpSystem:
    """Automated follow-up system for nurturing leads"""
    
    def __init__(self, sms_api_key="", email_api_key="", webhook_url=""):
        self.sms_api_key = sms_api_key
        self.email_api_key = email_api_key
        self.webhook_url = webhook_url
        
        # Follow-up message templates
        self.templates = {
            'sms_hour_1': "Hi {name}! Still curious about our free AI demo? Reply 'YES' to get started. - Yoursmate AI 🤖",
            'email_hour_1': {
                'subject': "Your Free AI Demo is Ready",
                'body': """Hi {name},

Thanks for chatting with our AI Closer! I wanted to make sure you got the demo link:

🚀 FREE DEMO: https://demo.yoursmate-ai.com

What you'll see in 5 minutes:
• Live lead generation in action
• 10-20 qualified prospects in your inbox
• How we built this for {company}

Questions? Just reply to this email.

Best,
Your Yoursmate AI Team"""
            },
            'sms_day_3': "Hi {name}! How did the demo go? Need help setting up your first campaign? Reply 'HELP' for instant support. 📞",
            'email_day_7': {
                'subject': "Still interested in 500+ leads/month?",
                'body': """Hi {name},

Quick check-in from your Yoursmate AI team.

I noticed you haven't booked your strategy call yet. No pressure!

But I wanted to share what happened this week:
• Client A: 47 new demos booked
• Client B: $23K in new revenue  
• Client C: 127 qualified leads

Ready to see similar results for {company}?

Book here: https://calendly.com/yoursmate-ai

Best,
Yoursmate AI Team"""
            }
        }
    
    def check_and_send_followups(self):
        """Check database for leads needing follow-up and send messages"""
        conn = sqlite3.connect('leads.db')
        cursor = conn.cursor()
        
        now = datetime.now()
        
        # Get leads that need follow-up
        cursor.execute('''
            SELECT * FROM leads 
            WHERE conversation_state IN ('nurture', 'closed_positive')
            AND last_interaction < ?
        ''', (now - timedelta(hours=1),))
        
        leads = cursor.fetchall()
        
        for lead in leads:
            lead_id, name, company, role, revenue, target_demos, lead_score, \
            conversation_state, created_at, last_interaction, phone, email, notes = lead
            
            # Calculate time since last interaction
            last_interaction_dt = datetime.fromisoformat(last_interaction)
            hours_since = (now - last_interaction_dt).total_seconds() / 3600
            
            # Send appropriate follow-up based on time elapsed
            if 1 <= hours_since < 2:
                self.send_hour_1_followup(lead_id, name, company, phone, email)
            elif 3*24 <= hours_since < 3*24 + 1:  # 3 days
                self.send_day_3_followup(lead_id, name, company, phone, email)
            elif 7*24 <= hours_since < 7*24 + 1:  # 7 days
                self.send_day_7_followup(lead_id, name, company, phone, email)
        
        conn.close()
    
    def send_hour_1_followup(self, lead_id, name, company, phone, email):
        """Send 1-hour follow-up via SMS and email"""
        # SMS follow-up
        if phone:
            sms_message = self.templates['sms_hour_1'].format(name=name or 'there')
            self.send_sms(phone, sms_message)
        
        # Email follow-up
        if email:
            email_template = self.templates['email_hour_1']
            subject = email_template['subject']
            body = email_template['body'].format(
                name=name or 'there',
                company=company or 'your business'
            )
            self.send_email(email, subject, body)
        
        # Log follow-up
        self.log_followup_sent(lead_id, 'hour_1', 'sms_email')
    
    def send_day_3_followup(self, lead_id, name, company, phone, email):
        """Send 3-day follow-up via SMS"""
        if phone:
            sms_message = self.templates['sms_day_3'].format(name=name or 'there')
            self.send_sms(phone, sms_message)
            self.log_followup_sent(lead_id, 'day_3', 'sms')
    
    def send_day_7_followup(self, lead_id, name, company, phone, email):
        """Send 7-day follow-up via email"""
        if email:
            email_template = self.templates['email_day_7']
            subject = email_template['subject']
            body = email_template['body'].format(
                name=name or 'there',
                company=company or 'your business'
            )
            self.send_email(email, subject, body)
            self.log_followup_sent(lead_id, 'day_7', 'email')
    
    def send_sms(self, phone, message):
        """Send SMS via API (placeholder - integrate with your SMS provider)"""
        # Example using Twilio API
        if self.sms_api_key:
            try:
                # Replace with actual SMS API call
                print(f"SMS to {phone}: {message}")
                # requests.post(SMS_API_URL, data={...})
                return True
            except Exception as e:
                print(f"SMS send error: {e}")
                return False
        return False
    
    def send_email(self, email, subject, body):
        """Send email via API (placeholder - integrate with your email provider)"""
        if self.email_api_key:
            try:
                # Replace with actual email API call (SendGrid, Mailgun, etc.)
                print(f"Email to {email}: {subject}")
                # requests.post(EMAIL_API_URL, data={...})
                return True
            except Exception as e:
                print(f"Email send error: {e}")
                return False
        return False
    
    def log_followup_sent(self, lead_id, followup_type, channel):
        """Log that a follow-up was sent"""
        conn = sqlite3.connect('leads.db')
        cursor = conn.cursor()
        
        # Create follow-ups table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS followups (
                id TEXT PRIMARY KEY,
                lead_id TEXT,
                followup_type TEXT,
                channel TEXT,
                sent_at TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
        ''')
        
        cursor.execute('''
            INSERT INTO followups (id, lead_id, followup_type, channel, sent_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), lead_id, followup_type, channel, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def send_to_crm(self, lead_data):
        """Send lead data to CRM via webhook"""
        if self.webhook_url:
            try:
                response = requests.post(
                    self.webhook_url,
                    json=lead_data,
                    headers={'Content-Type': 'application/json'}
                )
                return response.status_code == 200
            except Exception as e:
                print(f"CRM webhook error: {e}")
                return False
        return False

def run_followup_daemon():
    """Run follow-up system as a background daemon"""
    followup_system = FollowUpSystem()
    
    while True:
        try:
            followup_system.check_and_send_followups()
            print(f"Follow-up check completed at {datetime.now()}")
        except Exception as e:
            print(f"Follow-up daemon error: {e}")
        
        # Wait 1 hour before next check
        time.sleep(3600)

if __name__ == "__main__":
    # Run as standalone daemon
    print("Starting Yoursmate AI Follow-up Daemon...")
    run_followup_daemon()