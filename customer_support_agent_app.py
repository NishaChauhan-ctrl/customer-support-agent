import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import random
from datetime import datetime

# Initialize memory and logs
if "user_memory" not in st.session_state:
    st.session_state.user_memory = {}

if "complaint_log" not in st.session_state:
    st.session_state.complaint_log = []

sample_data = [
    ("U001", "The app crashes when I try to upload files."),
    ("U002", "I’m getting billed twice every month."),
    ("U003", "Dark mode is not available in my settings."),
    ("U004", "The dashboard loads too slowly on my phone."),
    ("U005", "Live chat support is not responding."),
    ("U006", "My data seems to have been wiped after the update.")
]

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

# Create tab layout
tab1, tab2, tab3 = st.tabs(["📥 Live Complaints", "📁 Batch Upload", "📊 Dashboard"])

with tab1:
    st.header("Submit a New Complaint")
    user_id = st.text_input("User ID", value="U001", help="Enter a unique identifier for the user")
    user_input = st.text_area("Complaint", value=random.choice([x[1] for x in sample_data]), height=100, help="Describe the issue or complaint here")

    if st.button("Generate Reply"):
        timestamp = datetime.now().isoformat(timespec='seconds')
        history = st.session_state.user_memory[user_id]
        reply = generate_response(user_input, history)
        st.success(reply)

        st.session_state.user_memory[user_id].append(user_input)
        st.session_state.complaint_log.append({
            "ticket_id": f"TKT{len(st.session_state.complaint_log)+1:04}",
            "user_id": user_id,
            "timestamp": timestamp,
            "text": user_input,
            "history": "; ".join(history[-2:]),
            "agent_reply": reply,
            "escalated": should_escalate(user_input),
            "trigger_keyword": next((kw for kw in ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"] if kw in user_input.lower()), "")
        })

with tab2:
    st.header("Upload CSV of Complaints")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if df.empty:
            st.error("Uploaded CSV is empty.")
        else:
            columns = df.columns.tolist()
            user_col = st.selectbox("Select the User ID column", columns, index=columns.index("user_id") if "user_id" in columns else 0)
            text_col = st.selectbox("Select the Complaint Text column", columns, index=columns.index("text") if "text" in columns else 1)

            if st.button("Process Batch"):
                with st.spinner("Processing..."):
                    outputs = []
                    for idx, row in df.iterrows():
                        uid = str(row[user_col]) if pd.notnull(row[user_col]) else f"user_{idx}"
                        text = row[text_col] if pd.notnull(row[text_col]) else ""
                        timestamp = datetime.now().isoformat(timespec='seconds')

                        if uid not in st.session_state.user_memory:
                            st.session_state.user_memory[uid] = []

                        hist = st.session_state.user_memory[uid]
                        reply = generate_response(text, hist)
                        st.session_state.user_memory[uid].append(text)

                        outputs.append({
                            "ticket_id": f"TKT{len(st.session_state.complaint_log)+len(outputs)+1:04}",
                            "timestamp": timestamp,
                            "user_id": uid,
                            "text": text,
                            "history": "; ".join(hist[-2:]),
                            "agent_reply": reply,
                            "escalated": should_escalate(text),
                            "trigger_keyword": next((kw for kw in ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"] if kw in text.lower()), "")
                        })

                    batch_df = pd.DataFrame(outputs)
                    st.session_state.complaint_log.extend(outputs)
                    st.success("Batch completed!")
                    st.dataframe(batch_df[["ticket_id", "user_id", "text", "agent_reply", "escalated", "trigger_keyword"]], use_container_width=True)
                    st.download_button(
                        "📥 Download Batch Results",
                        data=batch_df.to_csv(index=False),
                        file_name="batch_responses.csv",
                        mime="text/csv"
                    )

with tab3:
    st.header("Complaint & Escalation Dashboard")
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
                ax2.set_title("Top Escalation Keywords")
                ax2.set_xlabel("Keyword")
                ax2.set_ylabel("Count")
                st.pyplot(fig2)

        st.dataframe(log_df[["ticket_id", "timestamp", "user_id", "text", "agent_reply", "escalated", "trigger_keyword"]])
        st.download_button(
            "📥 Download Complaint Log",
            data=log_df.to_csv(index=False),
            file_name="complaint_log.csv",
            mime="text/csv"
        )
    else:
        st.info("No complaints submitted yet.")
