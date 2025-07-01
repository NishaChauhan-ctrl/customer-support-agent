import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import random

# Sample responses for demonstration
sample_data = [
    ("U001", "The app crashes when I try to upload files."),
    ("U002", "I’m getting billed twice every month."),
    ("U003", "Dark mode is not available in my settings."),
    ("U004", "The dashboard loads too slowly on my phone."),
    ("U005", "Live chat support is not responding."),
    ("U006", "My data seems to have been wiped after the update.")
]

# Initialize session state
if "user_memory" not in st.session_state:
    st.session_state.user_memory = {}

if "complaint_log" not in st.session_state:
    st.session_state.complaint_log = []

for user, _ in sample_data:
    if user not in st.session_state.user_memory:
        st.session_state.user_memory[user] = []

def generate_response(complaint, history=[]):
    if any(word in complaint.lower() for word in ["crash", "freeze", "data", "delete", "billing", "error"]):
        return "I'm sorry to hear that. We're escalating your issue to our support team right away."
    if "not working" in complaint.lower():
        return "Thanks for reporting this. We'll investigate the issue shortly."
    return "Thanks for your feedback! We'll look into it."

def should_escalate(text):
    escalation_keywords = ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"]
    return any(kw in text.lower() for kw in escalation_keywords)

# SECTION 1: Submit single complaint
with st.expander("📥 Submit a Complaint", expanded=True):
    st.markdown("Enter a user ID and a message. The AI will remember past complaints to generate a smart reply.")
    user_id = st.text_input("User ID", value="U001")
    user_input = st.text_area("Complaint text", value=random.choice([x[1] for x in sample_data]), height=100)

    if st.button("Generate Reply"):
        history = st.session_state.user_memory[user_id]
        reply = generate_response(user_input, history)
        st.success(reply)

        st.session_state.user_memory[user_id].append(user_input)
        st.session_state.complaint_log.append({
            "user_id": user_id,
            "text": user_input,
            "history": "; ".join(history[-2:]),
            "agent_reply": reply,
            "escalated": should_escalate(user_input),
            "trigger_keyword": next((kw for kw in ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"] if kw in user_input.lower()), "")
        })

# SECTION 2: Escalation dashboard
with st.expander("📊 Escalation Dashboard", expanded=False):
    st.markdown("See escalation rates and top complaint triggers across sessions.")
    log_df = pd.DataFrame(st.session_state.complaint_log)

    if not log_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig1, ax1 = plt.subplots(figsize=(4, 4))
            counts = log_df["escalated"].value_counts()
            labels = ["Escalated" if val else "Not Escalated" for val in counts.index]
            ax1.pie(counts, labels=labels, autopct="%1.1f%%", startangle=90)
            ax1.set_title("Escalation Rate")
            st.pyplot(fig1)

        with col2:
            kw_series = log_df[log_df["escalated"]]["trigger_keyword"].dropna().astype(str)
            kw_counts = Counter(kw_series)
            if kw_counts:
                fig2, ax2 = plt.subplots(figsize=(5, 4))
                ax2.bar(list(kw_counts.keys()), list(kw_counts.values()))
                ax2.set_title("Top Escalation Trigger Keywords")
                ax2.set_xlabel("Keyword")
                ax2.set_ylabel("Count")
                st.pyplot(fig2)

        st.download_button(
            "📥 Download Log",
            data=log_df.to_csv(index=False),
            file_name="memory_agent_log.csv",
            mime="text/csv"
        )
    else:
        st.info("No complaints submitted yet.")

# SECTION 3: Batch CSV Upload
with st.expander("📁 Upload CSV for Batch Processing", expanded=False):
    st.markdown("Upload a CSV with `user_id` and `text` to get batch replies with escalation logic and memory context.")
    uploaded_file = st.file_uploader("Upload a CSV with 'user_id' and 'text' columns", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if not {"user_id", "text"}.issubset(df.columns):
            st.error("CSV must contain 'user_id' and 'text' columns.")
        else:
            with st.spinner("Processing batch..."):
                outputs = []
                for _, row in df.iterrows():
                    uid = row["user_id"]
                    text = row["text"]
                    hist = st.session_state.user_memory[uid]
                    reply = generate_response(text, hist)
                    st.session_state.user_memory[uid].append(text)
                    outputs.append({
                        "user_id": uid,
                        "text": text,
                        "history": "; ".join(hist[-2:]),
                        "agent_reply": reply,
                        "escalated": should_escalate(text),
                        "trigger_keyword": next((kw for kw in ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"] if kw in text.lower()), "")
                    })

                result_df = pd.DataFrame(outputs)
                st.success("Batch completed!")
                st.dataframe(result_df[["user_id", "text", "agent_reply", "escalated", "trigger_keyword"]], use_container_width=True)
                st.download_button(
                    "📥 Download Batch Results",
                    data=result_df.to_csv(index=False),
                    file_name="batch_responses_with_memory.csv",
                    mime="text/csv"
                )
