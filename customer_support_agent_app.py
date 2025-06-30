
import streamlit as st
import random
import pandas as pd

# Sample complaints (replace this with your CSV in future)
sample_data = [
    "This is garbage. App crashes every time I open it.",
    "Can you help with login issues? I'm stuck at 2FA screen.",
    "Extremely disappointed. My billing history is incorrect!",
    "Thanks for the update, however the search feature still fails.",
    "Unacceptable! All my data got wiped after the update.",
    "Just noticed notifications are overwhelming lately."
]

# Escalation rule
def should_escalate(text):
    keywords = ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"]
    red_flags = ["unacceptable", "disappointed", "garbage", "hate", "tired", "frustrated", "angry"]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords + red_flags)

# Stub for AI-generated response (replace with OpenAI API or local LLM)
def generate_response(complaint):
    if should_escalate(complaint):
        escalation = "✅ Escalation triggered"
        empathy = "I'm really sorry you experienced this — it sounds incredibly frustrating."
    else:
        escalation = "No escalation needed"
        empathy = "Thanks for your feedback! I’d be happy to help with that."

    return f"{empathy}\n\nWe'll look into this and follow up as needed.\n\n➡️ {escalation}"

# Streamlit UI
st.set_page_config(page_title="AI Customer Support Agent", layout="wide")
st.title("🤖 AI-Powered Customer Support Agent")

st.markdown("""
This AI assistant reads customer complaints and generates:
- An empathetic support reply
- An internal **escalation trigger** (based on urgency and sentiment)
""")

# Input section
st.subheader("📥 Select or type a customer complaint")
default_input = random.choice(sample_data)
user_input = st.text_area("Customer Complaint", default_input, height=100)

if st.button("Generate Agent Response"):
    with st.spinner("Thinking..."):
        reply = generate_response(user_input)
        st.markdown("### 🤖 Agent Reply")
        st.success(reply)
