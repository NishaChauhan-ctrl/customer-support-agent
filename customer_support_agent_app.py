
import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
from collections import Counter

# Sample complaints (used for default text)
sample_data = [
    "This is garbage. App crashes every time I open it.",
    "Can you help with login issues? I'm stuck at 2FA screen.",
    "Extremely disappointed. My billing history is incorrect!",
    "Thanks for the update, however the search feature still fails.",
    "Unacceptable! All my data got wiped after the update.",
    "Just noticed notifications are overwhelming lately."
]

# Escalation logic
def should_escalate(text):
    keywords = ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"]
    red_flags = ["unacceptable", "disappointed", "garbage", "hate", "tired", "frustrated", "angry"]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords + red_flags)

# Stubbed agent response
def generate_response(complaint):
    if should_escalate(complaint):
        escalation = "✅ Escalation triggered"
        empathy = "I'm really sorry you experienced this — it sounds incredibly frustrating."
    else:
        escalation = "No escalation needed"
        empathy = "Thanks for your feedback! I’d be happy to help with that."
    return f"{empathy}\n\nWe'll look into this and follow up as needed.\n\n➡️ {escalation}"

# Streamlit config
st.set_page_config(page_title="AI Customer Support Agent", layout="wide")
st.title("🤖 AI-Powered Customer Support Agent")

st.markdown("""
This AI assistant:
- Reads and replies to customer complaints
- Triggers escalation if needed
- Tracks live stats
- Processes CSVs in bulk
""")

# Session state for tracking complaints
if "complaint_log" not in st.session_state:
    st.session_state.complaint_log = []

# SECTION 1: Single input + reply
st.header("📥 Live Complaint Interaction")
default_input = random.choice(sample_data)
user_input = st.text_area("Type or edit a complaint below", default_input, height=100)

if st.button("Generate Agent Reply"):
    reply = generate_response(user_input)
    st.markdown("### 🤖 Agent Reply")
    st.success(reply)

    # Track it
    keyword_triggered = next((kw for kw in ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"] if kw in user_input.lower()), "")
    st.session_state.complaint_log.append({
        "text": user_input,
        "escalated": should_escalate(user_input),
        "keyword": keyword_triggered
    })

# SECTION 2: Escalation dashboard
st.header("📊 Live Escalation Dashboard")
df = pd.DataFrame(st.session_state.complaint_log)

if not df.empty:
    fig1, ax1 = plt.subplots()
    counts = df["escalated"].value_counts()
    labels = ["Escalated" if val else "Not Escalated" for val in counts.index]
    ax1.pie(counts, labels=labels, autopct="%1.1f%%", startangle=90)
    ax1.set_title("Escalation Rate")
    st.pyplot(fig1)

    kw_counts = Counter(df[df["escalated"]]["keyword"])
    if kw_counts:
        fig2, ax2 = plt.subplots()
        ax2.bar(kw_counts.keys(), kw_counts.values())
        ax2.set_title("Top Escalation Trigger Keywords")
        ax2.set_xlabel("Keyword")
        ax2.set_ylabel("Count")
        st.pyplot(fig2)

    st.download_button(
        "📥 Download Escalation Log as CSV",
        data=df.to_csv(index=False),
        file_name="escalation_log.csv",
        mime="text/csv"
    )
else:
    st.info("No complaints submitted yet.")

# SECTION 3: CSV upload + batch processing
st.header("📁 Upload CSV for Batch Processing")

uploaded_file = st.file_uploader("Upload a CSV with a 'text' column", type=["csv"])
if uploaded_file:
    batch_df = pd.read_csv(uploaded_file)
    if "text" not in batch_df.columns:
        st.error("CSV must contain a 'text' column with complaint messages.")
    else:
        with st.spinner("Generating responses..."):
            batch_df["agent_reply"] = batch_df["text"].apply(generate_response)
            batch_df["escalated"] = batch_df["text"].apply(should_escalate)
            batch_df["trigger_keyword"] = batch_df["text"].apply(
                lambda x: next((kw for kw in ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"] if kw in x.lower()), "")
            )

        st.success("Batch responses generated!")
        st.dataframe(batch_df[["text", "agent_reply", "escalated", "trigger_keyword"]])
        st.download_button(
            "📥 Download Batch Results as CSV",
            data=batch_df.to_csv(index=False),
            file_name="batch_agent_responses.csv",
            mime="text/csv"
        )
