# 🤖 Yoursmate AI Closer

A high-trust, relentless AI sales agent for SaaS & service businesses. Built with Streamlit, this AI Closer handles the complete sales conversation from greeting to closing, with automatic lead scoring, objection handling, and follow-up nurturing.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://yoursmate-ai-closer.streamlit.app/)

## 🚀 Features

### Core AI Closer Capabilities
- **Warm Personalized Greetings** with immediate value proposition
- **3-Step Qualification Process** that captures key business metrics
- **Tailored Solution Pitches** based on company size and needs
- **Intelligent Objection Handling** for common sales objections
- **Compelling CTAs** with urgency and social proof
- **Automated Follow-up Nurturing** via SMS and email

### Advanced Sales Features
- **Dynamic Lead Scoring** (0-100) based on revenue, role, and targets
- **Real-time Conversation Tracking** with full history
- **CRM Integration** via webhook export
- **Sales Analytics Dashboard** with key metrics
- **Multi-channel Follow-up** automation (SMS + Email)
- **Lead Nurturing Sequences** for non-closers

### Technical Features
- **SQLite Database** for lead and conversation storage
- **Session Management** with persistent conversations
- **Responsive Design** optimized for sales teams
- **Export Functionality** for CRM integration
- **Background Daemon** for automated follow-ups

## 🎯 Conversation Flow

1. **Greeting**: "🤖 Hi [Name], I'm your Yoursmate AI Closer—ready to help you scale. What's your biggest growth challenge today?"

2. **Qualification** (3 questions):
   - Q1: "What's your company name & your role?"
   - Q2: "What's your current monthly revenue or lead volume?"
   - Q3: "How many demos or signups do you aim for each month?"

3. **Tailored Pitch**: "We've helped [similar company] add 500+ qualified leads/mo using our AI Sales Bot—built in 48 hrs."

4. **Objection Handling**:
   - Budget concerns: "Ironclad Guarantee: no cost unless you see a 5X ROI in 30 days"
   - Just browsing: "Here's our free demo link. Try it now & see 10–20 leads by tomorrow"

5. **Closing**: "Ready to lock in your first 100 leads? Book a 15‑min strategy call here: [Calendly Link]"

6. **Follow-up**: Automated SMS/Email sequences for nurturing

## 🛠️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/yoursmate-ai-closer.git
cd yoursmate-ai-closer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the AI Closer
```bash
streamlit run streamlit_app.py
```

### 4. (Optional) Start Follow-up Daemon
```bash
python follow_up_system.py
```

## 📊 Lead Scoring Algorithm

**Revenue Scoring** (0-50 points):
- $1M+ revenue: 50 points
- $100K+ revenue: 30 points  
- $50K+ revenue: 20 points

**Target Demo Scoring** (0-30 points):
- 100+ demos/month: 30 points
- 50+ demos/month: 25 points
- 20+ demos/month: 15 points

**Role Scoring** (0-20 points):
- CEO/Founder: 20 points
- VP/Director: 15 points
- Manager: 10 points

**Total Score**: Hot Lead (70+), Qualified (40+), Developing (<40)

## 🔧 Customization

### Message Templates
Edit the `AICloser` class in `streamlit_app.py` to customize:
- Greeting messages
- Qualification questions
- Objection responses
- Closing CTAs

### Follow-up Sequences
Modify `follow_up_system.py` to customize:
- SMS templates
- Email templates
- Timing intervals
- API integrations

### Lead Scoring
Adjust scoring criteria in the `calculate_lead_score()` function.

## 🔌 Integrations

### CRM Integration
- Export leads via JSON format
- Webhook support for real-time sync
- Compatible with Salesforce, HubSpot, Pipedrive

### Communication APIs
- **SMS**: Twilio, TextMagic, Plivo
- **Email**: SendGrid, Mailgun, AWS SES
- **Calendar**: Calendly, Cal.com

## 📈 Performance Metrics

The system tracks:
- **Total Leads** captured
- **Lead Score Distribution** 
- **Conversation Completion Rate**
- **Follow-up Engagement**
- **Conversion Metrics**

## 🚀 Production Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect Streamlit Cloud
3. Deploy with auto-updates

### Self-Hosted
```bash
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

### Docker (Coming Soon)
```bash
docker build -t yoursmate-ai-closer .
docker run -p 8501:8501 yoursmate-ai-closer
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Open a GitHub issue for bugs or feature requests
- **Email**: support@yoursmate-ai.com
- **Demo**: Try the live demo link above

---

**Built with ❤️ for sales teams who want to scale faster**
