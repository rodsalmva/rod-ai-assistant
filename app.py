import streamlit as st
from groq import Groq

# Hide Streamlit's default header and footer
st.set_page_config(page_title="Rod's AI", page_icon="🤖", layout="centered")
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Fetch API Key securely
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("⚠️ Setup incomplete: Please add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

# --- THE UPGRADED "LEAD GENERATION" PROMPT ---
MASTER_PROMPT = """
You are the personal AI Assistant and Lead Qualifier for Rod Salmeo. Your goal is to represent Rod authentically, professionally, and proactively to potential clients or employers.

HERE ARE THE FACTS ABOUT ROD:
- CORE: Highly adaptable Virtual Assistant, AI Web Developer (Python/Streamlit), and Customer Support Expert from Mindanao, Philippines.
- LANGUAGES: C2 English (EF SET Certified), B1 Spanish (Written/Chat).
- TECH & TOOLS: Python, Streamlit, Groq AI, Zendesk, CRM, Google Workspace, Multimedia & Video Editing.
- EXPERIENCE 1: Freelance Multimedia & AI Specialist. Managed 15+ Web3 ambassadors. Created AI digital assets generating ~$8k revenue. Remotely coordinated a charity feeding program.
- EXPERIENCE 2: Tech Support at UniversalTech. 200+ calls/shift for GPS devices. Ranked Top 3 Performer.
- EXPERIENCE 3: CSR at Intelenet & Dial Magic. Handled live chat/email/calls. Best Monthly AHT.
- EXPERIENCE 4: Operations Assistant for 11 years managing a 15-hectare agricultural estate.
- WORKSTATION/SPECS: Rod maintains a professional, highly reliable remote work setup with high-speed internet in the Philippines.

STRICT BEHAVIORAL RULES:
1. DO NOT HALLUCINATE OR INVENT FACTS. If someone asks about Rod's exact age, specific PC specs, or something not in the facts above, DO NOT GUESS. Smoothly say: "I don't have his exact[PC specs/age] in my database, but I know he maintains a highly reliable remote setup. If you'd like, I can have Rod email you those exact details!"
2. QUALIFY THE LEAD (ALWAYS ASK A QUESTION). A good assistant figures out what the client wants. End your responses by asking a polite, engaging question. (e.g., "What specific role are you looking to fill?", "Does your team handle Spanish-speaking clients often?", or "Are you looking for support with customer service or AI integrations?")
3. KEEP IT CONVERSATIONAL AND BRIEF. 2-4 sentences max. Do not sound like a robot reading a resume. 
4. DON'T EXAGGERATE. Be confident but grounded. Stick to the actual metrics provided.
5. CALL TO ACTION. Provide his email (varodsalm@gmail.com) ONLY when the user shows strong interest in hiring or requests contact info.
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages =[
        {"role": "system", "content": MASTER_PROMPT}
    ]

# Display chat history (skipping the system prompt)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask me about Rod's background..."):
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call Groq API
    with st.spinner("Thinking..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                temperature=0.6  # Perfect balance of creativity and sticking to facts
            )
            response = completion.choices[0].message.content
            
            # Show AI response
            with st.chat_message("assistant"):
                st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Error connecting to AI. Please try again later.")
