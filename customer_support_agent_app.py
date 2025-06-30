
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


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Initialize session state storage for complaint history
if "complaint_log" not in st.session_state:
    st.session_state.complaint_log = []

# Sample escalation rule
def should_escalate(text):
    keywords = ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"]
    red_flags = ["unacceptable", "disappointed", "garbage", "hate", "tired", "frustrated", "angry"]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords + red_flags)

# Input interface
st.subheader("📥 Submit a New Complaint for Tracking")
user_input = st.text_area("Enter complaint text", "")

if st.button("Submit Complaint"):
    escalate = should_escalate(user_input)
    keyword_triggered = next((kw for kw in ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"] if kw in user_input.lower()), "")
    st.session_state.complaint_log.append({
        "text": user_input,
        "escalated": escalate,
        "keyword": keyword_triggered
    })
    st.success("Complaint logged.")

# Convert history to DataFrame
df = pd.DataFrame(st.session_state.complaint_log)

if not df.empty:
    # Pie chart for escalation rate
    fig1, ax1 = plt.subplots()
    escalation_counts = df["escalated"].value_counts()
    labels = ["Escalated" if val else "Not Escalated" for val in escalation_counts.index]
    ax1.pie(escalation_counts, labels=labels, autopct="%1.1f%%", startangle=90)
    ax1.set_title("Escalation Rate")
    st.pyplot(fig1)

    # Bar chart for escalation keywords
    keyword_counts = Counter(df[df["escalated"]]["keyword"])
    if keyword_counts:
        fig2, ax2 = plt.subplots()
        ax2.bar(keyword_counts.keys(), keyword_counts.values())
        ax2.set_title("Top Escalation Trigger Keywords")
        ax2.set_xlabel("Keyword")
        ax2.set_ylabel("Count")
        st.pyplot(fig2)

    # Download button
    st.download_button(
        label="📥 Download Log as CSV",
        data=df.to_csv(index=False),
        file_name="escalation_log.csv",
        mime="text/csv"
    )
else:
    st.info("No complaints submitted yet.")
