import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
from collections import Counter

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

# Streamlit UI setup
st.set_page_config(page_title="AI Customer Support Agent", layout="wide")
st.title("🤖 AI-Powered Customer Support Agent")

st.markdown("""
This AI assistant reads customer complaints and generates:
- An empathetic support reply
- An internal **escalation trigger** (based on urgency and sentiment)
""")

# Initialize session state for tracking complaints
if "complaint_log" not in st.session_state:
    st.session_state.complaint_log = []

# Section 1: Single complaint interaction
st.subheader("📥 Submit or select a customer complaint")
default_input = random.choice(sample_data)
user_input = st.text_area("Customer Complaint", default_input, height=100)

if st.button("Generate Agent Response"):
    reply = generate_response(user_input)
    st.markdown("### 🤖 Agent Reply")
    st.success(reply)

    # Log this complaint to escalation history
    keyword_triggered = next((kw for kw in ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"] if kw in user_input.lower()), "")
    st.session_state.complaint_log.append({
        "text": user_input,
        "escalated": should_escalate(user_input),
        "keyword": keyword_triggered
    })

# Section 2: Escalation dashboard
st.subheader("📊 Live Escalation Dashboard")

df = pd.DataFrame(st.session_state.complaint_log)

if not df.empty:
    # Pie chart
    fig1, ax1 = plt.subplots()
    escalation_counts = df["escalated"].value_counts()
    labels = ["Escalated" if val else "Not Escalated" for val in escalation_counts.index]
    ax1.pie(escalation_counts, labels=labels, autopct="%1.1f%%", startangle=90)
    ax1.set_title("Escalation Rate")
    st.pyplot(fig1)

    # Bar chart
    keyword_counts = Counter(df[df["escalated"]]["keyword"])
    if keyword_counts:
        fig2, ax2 = plt.subplots()
        ax2.bar(keyword_counts.keys(), keyword_counts.values())
        ax2.set_title("Top Escalation Trigger Keywords")
        ax2.set_xlabel("Keyword")
        ax2.set_ylabel("Count")
        st.pyplot(fig2)

    # Download
    st.download_button(
        label="📥 Download Escalation Log as CSV",
        data=df.to_csv(index=False),
        file_name="escalation_log.csv",
        mime="text/csv"
    )
else:
    st.info("No complaints submitted yet.")
