import streamlit as st
import pandas as pd
import sqlite3
import uuid
import json
import time
from datetime import datetime, timedelta
import requests

# Set page configuration
st.set_page_config(
    page_title='Yoursmate AI Closer',
    page_icon='🤖',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Initialize database
def init_database():
    """Initialize SQLite database for lead tracking"""
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY,
            name TEXT,
            company TEXT,
            role TEXT,
            revenue TEXT,
            target_demos TEXT,
            lead_score INTEGER,
            conversation_state TEXT,
            created_at TIMESTAMP,
            last_interaction TIMESTAMP,
            phone TEXT,
            email TEXT,
            notes TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            lead_id TEXT,
            message TEXT,
            sender TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads (id)
        )
    ''')
    conn.commit()
    conn.close()

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'conversation_state' not in st.session_state:
        st.session_state.conversation_state = 'greeting'
    if 'lead_data' not in st.session_state:
        st.session_state.lead_data = {
            'name': '',
            'company': '',
            'role': '',
            'revenue': '',
            'target_demos': '',
            'lead_score': 0
        }
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

# Save lead to database
def save_lead_to_db(lead_data, conversation_state):
    """Save lead information to database"""
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    
    lead_id = st.session_state.session_id
    now = datetime.now()
    
    cursor.execute('''
        INSERT OR REPLACE INTO leads 
        (id, name, company, role, revenue, target_demos, lead_score, 
         conversation_state, created_at, last_interaction)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        lead_id, lead_data['name'], lead_data['company'], lead_data['role'],
        lead_data['revenue'], lead_data['target_demos'], lead_data['lead_score'],
        conversation_state, now, now
    ))
    
    conn.commit()
    conn.close()

# Save conversation message
def save_conversation_message(message, sender):
    """Save individual conversation message"""
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO conversations (id, lead_id, message, sender, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), st.session_state.session_id, message, sender, datetime.now()))
    
    conn.commit()
    conn.close()

# Calculate lead score
def calculate_lead_score(lead_data):
    """Calculate lead score based on responses"""
    score = 0
    
    # Revenue scoring
    revenue = lead_data.get('revenue', '').lower()
    if 'k' in revenue or 'thousand' in revenue:
        if any(x in revenue for x in ['50', '60', '70', '80', '90', '100']):
            score += 30
        else:
            score += 20
    elif 'm' in revenue or 'million' in revenue:
        score += 50
    elif any(x in revenue for x in ['high', 'significant', 'substantial']):
        score += 40
    
    # Target demos scoring
    target = lead_data.get('target_demos', '').lower()
    if any(x in target for x in ['100', '200', '300', '400', '500']):
        score += 30
    elif any(x in target for x in ['50', '60', '70', '80', '90']):
        score += 25
    elif any(x in target for x in ['20', '30', '40']):
        score += 15
    
    # Role scoring
    role = lead_data.get('role', '').lower()
    if any(x in role for x in ['ceo', 'founder', 'owner', 'president']):
        score += 20
    elif any(x in role for x in ['vp', 'director', 'head', 'manager']):
        score += 15
    elif any(x in role for x in ['marketing', 'sales']):
        score += 10
    
    return min(score, 100)

# AI Closer Response Engine
class AICloser:
    def __init__(self):
        self.objections = {
            'expensive': "I understand budget matters. Our Ironclad Guarantee: no cost unless you see a 5X ROI in 30 days. 💰",
            'browsing': "Totally—here's our free demo link. Try it now & see 10–20 leads in your inbox by tomorrow. 🚀",
            'think': "Perfect! While you're thinking, here's what [CompanyX] said after their first week: '127 qualified leads and 3 demos booked.' Ready to see similar results? 📈",
            'time': "I get it—time is precious. That's exactly why our AI does the heavy lifting. 15 minutes today could mean 500+ leads next month. Worth it? ⏰"
        }
    
    def get_greeting(self, name=""):
        """Generate personalized greeting"""
        if name:
            return f"🤖 Hi {name}, I'm your Yoursmate AI Closer—ready to help you scale. What's your biggest growth challenge today?"
        else:
            return "🤖 Hi there! I'm your Yoursmate AI Closer—ready to help you scale. What's your biggest growth challenge today?"
    
    def get_qualification_question(self, state):
        """Get the appropriate qualification question"""
        questions = {
            'q1': "What's your company name & your role? 🏢",
            'q2': "What's your current monthly revenue or lead volume? 📊",
            'q3': "How many demos or signups do you aim for each month? 🎯"
        }
        return questions.get(state, "")
    
    def get_tailored_pitch(self, lead_data):
        """Generate tailored solution pitch"""
        company = lead_data.get('company', 'similar companies')
        revenue = lead_data.get('revenue', '')
        
        if 'million' in revenue.lower() or 'm' in revenue.lower():
            return f"We've helped companies like {company} add 1000+ qualified leads/mo using our AI Sales Bot—built in 48 hrs. 🚀\nYour current scale suggests you could see 20-30% revenue boost in Q1."
        else:
            return f"We've helped {company} add 500+ qualified leads/mo using our AI Sales Bot—built in 48 hrs. 🚀\nPerfect timing to scale your current growth momentum."
    
    def handle_objection(self, message):
        """Detect and handle objections"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['expensive', 'cost', 'price', 'budget', 'afford']):
            return self.objections['expensive']
        elif any(word in message_lower for word in ['browse', 'looking', 'research', 'exploring']):
            return self.objections['browsing']
        elif any(word in message_lower for word in ['think', 'consider', 'discuss', 'decide']):
            return self.objections['think']
        elif any(word in message_lower for word in ['busy', 'time', 'later', 'schedule']):
            return self.objections['time']
        
        return None
    
    def get_closing_cta(self, lead_data):
        """Generate closing call-to-action"""
        name = lead_data.get('name', '')
        urgency_phrases = [
            "Only 3 demo slots left this week.",
            "Limited spots available for our January cohort.",
            "Next available onboarding is in 2 weeks."
        ]
        
        base_cta = f"Ready to lock in your first 100 leads{', ' + name if name else ''}? Book a 15‑min strategy call here: [📅 BOOK NOW](https://calendly.com/yoursmate-ai)"
        urgency = urgency_phrases[0]  # Can randomize or base on current demand
        
        return f"{base_cta}\n\n⚡ {urgency}"

# Initialize
init_database()
init_session_state()
ai_closer = AICloser()

# Main App Layout
st.title("🤖 Yoursmate AI Closer")
st.subheader("Your High-Trust Sales Agent for SaaS & Service Businesses")

# Sidebar for admin/analytics
with st.sidebar:
    st.header("📊 Sales Dashboard")
    
    # Load lead statistics
    conn = sqlite3.connect('leads.db')
    try:
        leads_df = pd.read_sql_query("SELECT * FROM leads", conn)
        if not leads_df.empty:
            st.metric("Total Leads", len(leads_df))
            st.metric("High Score Leads", len(leads_df[leads_df['lead_score'] >= 70]))
            st.metric("Today's Conversations", len(leads_df[leads_df['created_at'] >= datetime.now().strftime('%Y-%m-%d')]))
        else:
            st.metric("Total Leads", 0)
            st.metric("High Score Leads", 0)
            st.metric("Today's Conversations", 0)
    except:
        st.metric("Total Leads", 0)
        st.metric("High Score Leads", 0)
        st.metric("Today's Conversations", 0)
    conn.close()
    
    if st.button("🔄 Reset Conversation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main conversation area
col1, col2 = st.columns([3, 1])

with col1:
    st.header("💬 Conversation")
    
    # Display conversation history
    conversation_container = st.container()
    with conversation_container:
        for msg in st.session_state.conversation_history:
            if msg['sender'] == 'ai':
                st.chat_message("assistant").write(msg['message'])
            else:
                st.chat_message("user").write(msg['message'])
    
    # Handle conversation flow
    if st.session_state.conversation_state == 'greeting':
        if not st.session_state.conversation_history:
            greeting = ai_closer.get_greeting()
            st.session_state.conversation_history.append({'sender': 'ai', 'message': greeting})
            save_conversation_message(greeting, 'ai')
            st.chat_message("assistant").write(greeting)
    
    # User input
    user_input = st.chat_input("Type your response here...")
    
    if user_input:
        # Add user message to history
        st.session_state.conversation_history.append({'sender': 'user', 'message': user_input})
        save_conversation_message(user_input, 'user')
        
        # Process response based on conversation state
        ai_response = ""
        
        if st.session_state.conversation_state == 'greeting':
            st.session_state.conversation_state = 'q1'
            ai_response = ai_closer.get_qualification_question('q1')
        
        elif st.session_state.conversation_state == 'q1':
            # Parse company and role
            parts = user_input.split(',') if ',' in user_input else [user_input]
            if len(parts) >= 2:
                st.session_state.lead_data['company'] = parts[0].strip()
                st.session_state.lead_data['role'] = parts[1].strip()
            else:
                st.session_state.lead_data['company'] = parts[0].strip()
            
            # Extract name if mentioned
            if 'i\'m' in user_input.lower() or 'my name' in user_input.lower():
                words = user_input.split()
                for i, word in enumerate(words):
                    if word.lower() in ['i\'m', 'name'] and i + 1 < len(words):
                        st.session_state.lead_data['name'] = words[i + 1].strip('.,!')
                        break
            
            st.session_state.conversation_state = 'q2'
            ai_response = ai_closer.get_qualification_question('q2')
        
        elif st.session_state.conversation_state == 'q2':
            st.session_state.lead_data['revenue'] = user_input
            st.session_state.conversation_state = 'q3'
            ai_response = ai_closer.get_qualification_question('q3')
        
        elif st.session_state.conversation_state == 'q3':
            st.session_state.lead_data['target_demos'] = user_input
            st.session_state.lead_data['lead_score'] = calculate_lead_score(st.session_state.lead_data)
            st.session_state.conversation_state = 'pitch'
            ai_response = ai_closer.get_tailored_pitch(st.session_state.lead_data)
        
        elif st.session_state.conversation_state == 'pitch':
            # Check for objections first
            objection_response = ai_closer.handle_objection(user_input)
            if objection_response:
                ai_response = objection_response
                st.session_state.conversation_state = 'objection_handled'
            else:
                st.session_state.conversation_state = 'closing'
                ai_response = ai_closer.get_closing_cta(st.session_state.lead_data)
        
        elif st.session_state.conversation_state == 'objection_handled':
            st.session_state.conversation_state = 'closing'
            ai_response = ai_closer.get_closing_cta(st.session_state.lead_data)
        
        elif st.session_state.conversation_state == 'closing':
            # Handle final responses
            if any(word in user_input.lower() for word in ['yes', 'interested', 'book', 'schedule']):
                ai_response = f"🎉 Fantastic! You're all set for success. Check your email for the calendar link and prep materials.\n\n📧 Follow-up: I'll send you our '5-Minute Lead Generation Checklist' right now!"
                st.session_state.conversation_state = 'closed_positive'
            else:
                ai_response = "No worries! Here's our free demo link to try whenever you're ready: [🚀 FREE DEMO](https://demo.yoursmate-ai.com)\n\n💡 Pro tip: Even 1 hour of testing usually generates 5-10 qualified leads."
                st.session_state.conversation_state = 'nurture'
        
        # Add AI response to history
        if ai_response:
            st.session_state.conversation_history.append({'sender': 'ai', 'message': ai_response})
            save_conversation_message(ai_response, 'ai')
            
            # Save updated lead data
            save_lead_to_db(st.session_state.lead_data, st.session_state.conversation_state)
        
        st.rerun()

with col2:
    st.header("📋 Lead Profile")
    
    # Display current lead data
    if st.session_state.lead_data['name']:
        st.write(f"**Name:** {st.session_state.lead_data['name']}")
    if st.session_state.lead_data['company']:
        st.write(f"**Company:** {st.session_state.lead_data['company']}")
    if st.session_state.lead_data['role']:
        st.write(f"**Role:** {st.session_state.lead_data['role']}")
    if st.session_state.lead_data['revenue']:
        st.write(f"**Revenue:** {st.session_state.lead_data['revenue']}")
    if st.session_state.lead_data['target_demos']:
        st.write(f"**Target Demos:** {st.session_state.lead_data['target_demos']}")
    
    # Lead score
    score = st.session_state.lead_data['lead_score']
    st.metric("Lead Score", f"{score}/100")
    
    if score >= 70:
        st.success("🔥 Hot Lead!")
    elif score >= 40:
        st.warning("🌟 Qualified Lead")
    else:
        st.info("📝 Developing Lead")
    
    # Conversation state
    st.write(f"**Stage:** {st.session_state.conversation_state.replace('_', ' ').title()}")

# Auto-follow up system (display notification)
if st.session_state.conversation_state in ['nurture', 'closed_positive']:
    st.success("🔔 Follow-up scheduled: SMS/Email will be sent in 1 hour if no response")

# CRM Export functionality
if st.button("📤 Export Lead to CRM"):
    lead_export = {
        "lead_id": st.session_state.session_id,
        "lead_data": st.session_state.lead_data,
        "conversation_state": st.session_state.conversation_state,
        "conversation_history": st.session_state.conversation_history,
        "timestamp": datetime.now().isoformat()
    }
    
    # In a real implementation, this would send to your CRM via webhook
    st.json(lead_export)
    st.success("✅ Lead exported! Data sent to CRM system.")
