import streamlit as st
import os
import smtplib
from email.mime.text import MIMEText
from groq import Groq

# ================= PAGE SETUP =================
st.set_page_config(page_title="Rod's AI Assistant", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    .stChatMessage { padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .stChatMessage[data-testid="chat-message-user"] { background-color: #1e293b; color: #f8fafc; }
    .stChatMessage[data-testid="chat-message-assistant"] { background-color: #0f172a; color: #f8fafc; border: 1px solid #3b82f6; }
</style>
""", unsafe_allow_html=True)

# ================= CONFIGURATION & SECRETS =================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("⚠️ API Key missing! Please set your GROQ_API_KEY in Streamlit secrets.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# ================= EMAIL FUNCTION =================
def send_chat_to_email():
    try:
        sender_email = st.secrets["EMAIL_ADDRESS"]
        # FIXED: Now strictly matches your secrets.toml variable name
        sender_password = st.secrets["GMAIL_APP_PASSWORD"] 
        receiver_email = "varodsalm@gmail.com"  # The email where you want to RECEIVE the chat logs
        
        # Format the chat history into a readable text format
        chat_log = "Here is a recent chat transcript with your AI Portfolio Bot:\n\n"
        for msg in st.session_state.messages:
            role = "USER" if msg["role"] == "user" else "AI ASSISTANT"
            chat_log += f"{role}: {msg['content']}\n\n"
            
        # Create the email
        msg = MIMEText(chat_log)
        msg['Subject'] = "🚀 Lead Alert: New Chat on your AI Portfolio"
        msg['From'] = sender_email
        msg['To'] = receiver_email
        
        # Connect to Gmail SMTP server and send
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
        return True
    except Exception as e:
        st.error(f"Failed to send email. Check your Streamlit Secrets settings. Error: {e}")
        return False

# ================= LOAD KNOWLEDGE BASE =================
@st.cache_data
def load_knowledge_base():
    try:
        with open("knowledge_base.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "System Error: knowledge_base.txt not found."

SYSTEM_PROMPT = load_knowledge_base()

# ================= SESSION STATE INIT =================
if "messages" not in st.session_state:
    st.session_state.messages =[
        {
            "role": "assistant", 
            "content": "Hi! 👋 I'm the AI assistant for **Rod Salmeo**. I can tell you about his BPO experience, his AI tech stack, or even his home gym setup and his 2300 Chess rating. What would you like to know?"
        }
    ]

# ================= SIDEBAR: EMAIL FEATURE =================
with st.sidebar:
    st.header("Contact Rod")
    st.info("Want Rod to see this conversation? Click the button below to email him the chat logs so he can follow up!")
    if st.button("📩 Send Chat to Rod's Email"):
        with st.spinner("Sending email..."):
            success = send_chat_to_email()
            if success:
                st.success("✅ Chat successfully sent to Rod! He will review it shortly.")

# ================= UI: CHAT HISTORY =================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ================= UI: CHAT INPUT & LOGIC =================
if prompt := st.chat_input("Ask me anything about Rod..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    api_messages =[{"role": "system", "content": SYSTEM_PROMPT}]
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # FIRST TRY: The big, smart 70B model
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=api_messages,
                    temperature=0.5, 
                    max_tokens=512
                )
                reply = response.choices[0].message.content
                
            except Exception as e:
                # FALLBACK: If the 70B model hits a rate limit (429), switch to the 8B model automatically
                if "429" in str(e) or "rate_limit" in str(e):
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=api_messages,
                            temperature=0.3,
                            max_tokens=1024
                        )
                        reply = response.choices[0].message.content
                    except Exception as fallback_e:
                        reply = "I apologize, but I am currently receiving too many requests. Please contact Rod directly at varodsalm@gmail.com!"
                else:
                    reply = "I apologize, but my servers are currently undergoing maintenance. Please email Rod directly!"

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
