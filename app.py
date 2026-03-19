import streamlit as st
import json
from groq import Groq

# ================= PAGE SETUP =================
st.set_page_config(page_title="Rod's Assistant", page_icon="🤖")

# Custom CSS for brevity and professional look
st.markdown("""
<style>
    .stChatMessage { font-size: 0.95rem; border-radius: 12px; }
    .status-box { padding: 5px 10px; border-radius: 8px; background: #1e293b; border: 1px solid #334155; font-size: 0.8rem; color: #94a3b8; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

# API KEY
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# LOAD KNOWLEDGE BASE
with open("knowledge_base.txt", "r") as f:
    SYSTEM_PROMPT = f.read()

# SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm Rod's AI. How can I assist your business operations today?"}]

# SIDEBAR STATUS
with st.sidebar:
    st.markdown("### 🛠️ System Status")
    st.markdown("<div class='status-box'>Mode: <b>Professional Efficiency</b><br>Brevity: <b>Active</b></div>", unsafe_allow_html=True)
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# DISPLAY CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# INPUT LOGIC
if prompt := st.chat_input("Ask about Rod's experience..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
                    temperature=0.3, # Lower temperature for less yapping/hallucination
                    max_tokens=250
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except:
                st.error("Connection busy. Try again.")
