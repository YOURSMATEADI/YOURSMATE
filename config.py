# Yoursmate AI Closer Configuration

# =============================================================================
# BUSINESS CONFIGURATION
# =============================================================================

COMPANY_NAME = "Yoursmate AI"
CALENDLY_LINK = "https://calendly.com/yoursmate-ai"
DEMO_LINK = "https://demo.yoursmate-ai.com"
SUPPORT_EMAIL = "support@yoursmate-ai.com"

# =============================================================================
# AI CLOSER MESSAGES
# =============================================================================

# Greeting Messages
GREETING_TEMPLATES = {
    'default': "🤖 Hi there! I'm your Yoursmate AI Closer—ready to help you scale. What's your biggest growth challenge today?",
    'with_name': "🤖 Hi {name}, I'm your Yoursmate AI Closer—ready to help you scale. What's your biggest growth challenge today?"
}

# Qualification Questions
QUALIFICATION_QUESTIONS = {
    'q1': "What's your company name & your role? 🏢",
    'q2': "What's your current monthly revenue or lead volume? 📊", 
    'q3': "How many demos or signups do you aim for each month? 🎯"
}

# Solution Pitches
PITCH_TEMPLATES = {
    'high_revenue': "We've helped companies like {company} add 1000+ qualified leads/mo using our AI Sales Bot—built in 48 hrs. 🚀\nYour current scale suggests you could see 20-30% revenue boost in Q1.",
    'standard': "We've helped {company} add 500+ qualified leads/mo using our AI Sales Bot—built in 48 hrs. 🚀\nPerfect timing to scale your current growth momentum."
}

# Objection Responses
OBJECTION_RESPONSES = {
    'expensive': "I understand budget matters. Our Ironclad Guarantee: no cost unless you see a 5X ROI in 30 days. 💰",
    'browsing': "Totally—here's our free demo link. Try it now & see 10–20 leads in your inbox by tomorrow. 🚀",
    'think': "Perfect! While you're thinking, here's what [CompanyX] said after their first week: '127 qualified leads and 3 demos booked.' Ready to see similar results? 📈",
    'time': "I get it—time is precious. That's exactly why our AI does the heavy lifting. 15 minutes today could mean 500+ leads next month. Worth it? ⏰"
}

# Closing CTAs
CLOSING_TEMPLATES = {
    'base_cta': "Ready to lock in your first 100 leads{name_insert}? Book a 15‑min strategy call here: [📅 BOOK NOW]({calendly_link})",
    'urgency_phrases': [
        "Only 3 demo slots left this week.",
        "Limited spots available for our January cohort.", 
        "Next available onboarding is in 2 weeks."
    ]
}

# Success/Nurture Messages
FINAL_RESPONSES = {
    'closed_positive': "🎉 Fantastic! You're all set for success. Check your email for the calendar link and prep materials.\n\n📧 Follow-up: I'll send you our '5-Minute Lead Generation Checklist' right now!",
    'nurture': "No worries! Here's our free demo link to try whenever you're ready: [🚀 FREE DEMO]({demo_link})\n\n💡 Pro tip: Even 1 hour of testing usually generates 5-10 qualified leads."
}

# =============================================================================
# LEAD SCORING CONFIGURATION
# =============================================================================

SCORING_CONFIG = {
    'revenue': {
        'keywords': {
            'million': 50,
            '1m': 50,
            '2m': 50,
            '100k': 30,
            '200k': 30,
            '50k': 20,
            '75k': 25,
            'high': 40,
            'significant': 40,
            'substantial': 40
        }
    },
    'target_demos': {
        'ranges': {
            '500+': 30,
            '400+': 30,
            '300+': 30,
            '200+': 30,
            '100+': 30,
            '90+': 25,
            '80+': 25,
            '70+': 25,
            '60+': 25,
            '50+': 25,
            '40+': 15,
            '30+': 15,
            '20+': 15
        }
    },
    'role': {
        'executive': ['ceo', 'founder', 'owner', 'president'],
        'senior': ['vp', 'director', 'head'],
        'manager': ['manager'],
        'specialist': ['marketing', 'sales'],
        'points': {
            'executive': 20,
            'senior': 15,
            'manager': 10,
            'specialist': 10
        }
    }
}

# Lead Score Thresholds
LEAD_SCORE_THRESHOLDS = {
    'hot': 70,      # 🔥 Hot Lead!
    'qualified': 40, # 🌟 Qualified Lead
    'developing': 0  # 📝 Developing Lead
}

# =============================================================================
# FOLLOW-UP CONFIGURATION
# =============================================================================

FOLLOWUP_TIMING = {
    'hour_1': 1,     # 1 hour after last interaction
    'day_3': 72,     # 3 days
    'day_7': 168,    # 7 days
    'day_14': 336    # 14 days
}

FOLLOWUP_MESSAGES = {
    'sms_hour_1': "Hi {name}! Still curious about our free AI demo? Reply 'YES' to get started. - Yoursmate AI 🤖",
    'email_hour_1': {
        'subject': "Your Free AI Demo is Ready",
        'body': """Hi {name},

Thanks for chatting with our AI Closer! I wanted to make sure you got the demo link:

🚀 FREE DEMO: {demo_link}

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

Book here: {calendly_link}

Best,
Yoursmate AI Team"""
    }
}

# =============================================================================
# API INTEGRATION SETTINGS
# =============================================================================

# CRM Webhook Configuration
CRM_CONFIG = {
    'webhook_url': '',  # Add your CRM webhook URL here
    'api_key': '',      # Add your CRM API key here
    'enabled': False    # Set to True when ready to use
}

# SMS API Configuration (Twilio example)
SMS_CONFIG = {
    'provider': 'twilio',  # 'twilio', 'textmagic', etc.
    'api_key': '',         # Your SMS provider API key
    'api_secret': '',      # Your SMS provider API secret
    'from_number': '',     # Your SMS sending number
    'enabled': False       # Set to True when ready to use
}

# Email API Configuration (SendGrid example)
EMAIL_CONFIG = {
    'provider': 'sendgrid',  # 'sendgrid', 'mailgun', etc.
    'api_key': '',           # Your email provider API key
    'from_email': 'noreply@yoursmate-ai.com',
    'from_name': 'Yoursmate AI Team',
    'enabled': False         # Set to True when ready to use
}

# =============================================================================
# UI CUSTOMIZATION
# =============================================================================

# Streamlit Page Configuration
PAGE_CONFIG = {
    'page_title': 'Yoursmate AI Closer',
    'page_icon': '🤖',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Color Scheme & Styling
UI_CONFIG = {
    'primary_color': '#FF6B6B',
    'background_color': '#FFFFFF',
    'secondary_background_color': '#F0F2F6',
    'text_color': '#262730'
}

# Dashboard Metrics
DASHBOARD_CONFIG = {
    'show_analytics': True,
    'show_lead_export': True,
    'show_conversation_reset': True,
    'auto_refresh_interval': 30  # seconds
}

# =============================================================================
# DEVELOPMENT/TESTING SETTINGS
# =============================================================================

# Debug Configuration
DEBUG_CONFIG = {
    'verbose_logging': False,
    'show_session_state': False,
    'enable_test_mode': False,
    'mock_api_calls': True  # Use mock responses instead of real API calls
}