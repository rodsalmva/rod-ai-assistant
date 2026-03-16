import streamlit as st
from groq import Groq
import smtplib
from email.mime.text import MIMEText
import re

# Hide Streamlit's default UI
st.set_page_config(page_title="Rod's AI", page_icon="🤖", layout="centered")
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Fetch Keys securely
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    GMAIL_PASS = st.secrets["GMAIL_APP_PASSWORD"]
    RODS_EMAIL = "varodsalm@gmail.com"
except KeyError:
    st.error("⚠️ Setup incomplete: Please add GROQ_API_KEY and GMAIL_APP_PASSWORD to Streamlit Secrets.")
    st.stop()

# --- EMAIL SENDING FUNCTION ---
def send_transcript_to_rod(chat_history, lead_email="Unknown (Abandoned Chat)", subject="🚨 New Portfolio Lead Chat"):
    msg_body = f"A client was chatting with your AI Portfolio Assistant!\nClient Email: {lead_email}\n\n--- CHAT TRANSCRIPT ---\n\n"
    
    for msg in chat_history:
        if msg["role"] != "system":
            role_name = "CLIENT" if msg["role"] == "user" else "AI ASSISTANT"
            msg_body += f"{role_name}: {msg['content']}\n\n"
            
    msg = MIMEText(msg_body)
    msg['Subject'] = subject
    msg['From'] = RODS_EMAIL
    msg['To'] = RODS_EMAIL
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(RODS_EMAIL, GMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False

# --- THE UPGRADED "LEAD CAPTURE" PROMPT ---
MASTER_PROMPT = """
You are the personal AI Assistant and Lead Qualifier for Rod Salmeo. Your goal is to represent Rod professionally and PROACTIVELY CAPTURE LEADS.

HERE ARE THE FACTS ABOUT ROD:
- CORE: Highly adaptable Virtual Assistant, AI Web Developer (Python/Streamlit), and Customer Support Expert from Mindanao, Philippines.
- LANGUAGES: C2 English (EF SET Certified), B1 Spanish (Written/Chat).
- TECH & TOOLS: Python, Streamlit, Groq AI, Zendesk, CRM, Google Workspace, Multimedia & Video Editing.
- EXPERIENCE: Managed 15+ Web3 ambassadors (generated ~$8k revenue). Tech Support at UniversalTech (200+ calls/shift, Top 3 Performer). CSR at Intelenet & Dial Magic (Best Monthly AHT). Operations Assistant for 11 years (15-hectare agricultural estate).
- WORKSTATION: Professional, highly reliable remote setup with high-speed internet.

STRICT BEHAVIORAL RULES:
1. NEVER INVENT FACTS. If you don't know something, say: "I don't have that exact detail in my database, but Rod would be happy to discuss it with you!"
2. QUALIFY AND CAPTURE: Answer the user's question, but ALWAYS end by asking a question to understand their business needs. 
3. ASK FOR THE EMAIL: Once you understand what they need (e.g., 24/7 support, admin tasks), say something like: "Rod would be a perfect fit for this. Would you like me to send a complete transcript of our conversation to his inbox so he can review your needs? If so, just reply with your email address!"
4. KEEP IT BRIEF: 2-4 sentences max per response. Be conversational and human.
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages =[{"role": "system", "content": MASTER_PROMPT}]
if "mid_chat_saved" not in st.session_state:
    st.session_state.mid_chat_saved = False
if "email_captured" not in st.session_state:
    st.session_state.email_captured = False

# Display chat history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask me about Rod's background..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # --- MAGIC TRIGGER 1: Email Detection ---
    # If the user types an email address, trigger the final send!
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', prompt)
    if email_match and not st.session_state.email_captured:
        lead_email = email_match.group(0)
        send_transcript_to_rod(st.session_state.messages, lead_email=lead_email, subject=f"🎯 STRONG LEAD CAPTURED: {lead_email}")
        st.session_state.email_captured = True
        
        # Inject a hidden instruction so the AI knows it was sent
        st.session_state.messages.append({"role": "system", "content": f"SYSTEM NOTE: The user just provided their email ({lead_email}). Acknowledge this, thank them warmly, confirm that the complete conversation transcript has just been emailed directly to Rod, and tell them Rod will reach out soon."})

    # --- MAGIC TRIGGER 2: Silent Abandoned Chat Save ---
    # If the conversation reaches 4 back-and-forth messages, save a backup just in case they hang up!
    if len(st.session_state.messages) == 8 and not st.session_state.mid_chat_saved:
        send_transcript_to_rod(st.session_state.messages, subject="👀 Chat In Progress (Abandoned Chat Backup)")
        st.session_state.mid_chat_saved = True

    # Call Groq AI
    with st.spinner("Thinking..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                temperature=0.6
            )
            response = completion.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Error connecting to AI. Please try again.")
