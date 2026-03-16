import streamlit as st
import os
from groq import Groq

# ================= PAGE SETUP =================
st.set_page_config(page_title="Rod's AI Assistant", page_icon="🤖", layout="centered")

# Custom CSS for a clean, professional dark-mode look matching your portfolio
st.markdown("""
<style>
    .stChatMessage { padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .stChatMessage[data-testid="chat-message-user"] { background-color: #1e293b; color: #f8fafc; }
    .stChatMessage[data-testid="chat-message-assistant"] { background-color: #0f172a; color: #f8fafc; border: 1px solid #3b82f6; }
</style>
""", unsafe_allow_html=True)

# ================= API CONFIGURATION =================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("⚠️ API Key missing! Please set your GROQ_API_KEY in Streamlit secrets.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# ================= LOAD KNOWLEDGE BASE =================
# This function automatically reads your .txt file. 
# You never have to touch this Python code again to update your resume/info!
@st.cache_data
def load_knowledge_base():
    try:
        with open("knowledge_base.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "System Error: knowledge_base.txt not found. Defaulting to standard assistant mode."

SYSTEM_PROMPT = load_knowledge_base()

# ================= SESSION STATE INIT =================
if "messages" not in st.session_state:
    st.session_state.messages =[
        {
            "role": "assistant", 
            "content": "Hi! 👋 I'm the AI assistant for **Rod Salmeo**. I can tell you about his BPO and technical experience, his tech stack, or even his home gym setup and his 2300 Chess rating. What would you like to know?"
        }
    ]

# ================= UI: CHAT HISTORY =================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ================= UI: CHAT INPUT & LOGIC =================
if prompt := st.chat_input("Ask me anything about Rod..."):
    
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Build API Call Messages
    # Start with the System Prompt (the knowledge base), then append the conversation history
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    # 3. Call Groq API and stream/display response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=api_messages,
                    temperature=0.6, # 0.6 keeps it creative but factually grounded to your text file
                    max_tokens=1024
                )
                
                reply = response.choices[0].message.content
                st.markdown(reply)
                
                # Save assistant response to state
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
            except Exception as e:
                st.error(f"Error connecting to AI: {e}")
