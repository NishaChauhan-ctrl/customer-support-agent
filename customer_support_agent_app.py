
import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

# Sample complaints
sample_data = [
    ("U001", "App crashes every time I open it."),
    ("U002", "My billing history is incorrect."),
    ("U001", "Dashboard won’t load after login."),
    ("U003", "Notifications are overwhelming."),
    ("U002", "Still seeing wrong billing after update.")
]

# Escalation check
def should_escalate(text):
    keywords = ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"]
    red_flags = ["unacceptable", "disappointed", "garbage", "hate", "tired", "frustrated", "angry"]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords + red_flags)

# Memory-aware response
def generate_response(complaint, history=[]):
    if should_escalate(complaint):
        escalation = "✅ Escalation triggered"
        empathy = "I'm really sorry you experienced this — it sounds incredibly frustrating."
    else:
        escalation = "No escalation needed"
        empathy = "Thanks for your feedback! I’d be happy to help with that."

    if history:
        context = f"Previously, you reported: “{'; '.join(history[-2:])}”\n\n"
    else:
        context = ""

    return f"{context}{empathy}\n\nWe'll look into this and follow up as needed.\n\n➡️ {escalation}"

# Streamlit setup
st.set_page_config(page_title="AI Agent with Memory", layout="wide")
st.title("🧠 AI Customer Agent with Memory")

st.markdown("""
This version remembers each user’s previous complaints and includes that history in the reply.
""")

# Initialize memory storage
if "complaint_log" not in st.session_state:
    st.session_state.complaint_log = []

if "user_memory" not in st.session_state:
    st.session_state.user_memory = defaultdict(list)

# Live input
st.subheader("📥 Submit a Complaint")
user_id = st.text_input("User ID (e.g. U001)", value="U001")
user_input = st.text_area("Complaint text", value=random.choice([x[1] for x in sample_data]), height=100)

if st.button("Generate Reply"):
    history = st.session_state.user_memory[user_id]
    reply = generate_response(user_input, history)

    st.success(reply)

    # Save to memory + log
    st.session_state.user_memory[user_id].append(user_input)
    st.session_state.complaint_log.append({
        "user_id": user_id,
        "text": user_input,
        "history": "; ".join(history[-2:]),
        "agent_reply": reply,
        "escalated": should_escalate(user_input),
        "trigger_keyword": next((kw for kw in ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"] if kw in user_input.lower()), "")
    })

# Show full log
st.subheader("📜 Memory-Aware Complaint Log")
if st.session_state.complaint_log:
    df = pd.DataFrame(st.session_state.complaint_log)
    st.dataframe(df[["user_id", "text", "history", "agent_reply", "escalated", "trigger_keyword"]])
    st.download_button(
        "📥 Download Log with Memory",
        data=df.to_csv(index=False),
        file_name="memory_agent_log.csv",
        mime="text/csv"
    )
else:
    st.info("No complaints submitted yet.")
