
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import uuid
from collections import defaultdict, Counter

st.set_page_config(page_title="SupportGenie - AI Customer Support Agent", layout="wide")

# --- App logo and title ---
st.image("supportgenie_logo.png", width=80)
st.title("🤖 SupportGenie: AI-Powered Customer Support Agent")

st.markdown("""
Welcome to **SupportGenie**, your AI co-pilot for customer support!

This assistant:
- Replies to user complaints with empathy and context
- Flags messages for escalation based on keyword triggers
- Tracks history and agent performance
- Supports CSV upload for batch complaint processing
- Lets you explore all ticket logs and keyword analytics

---

""")

# --- Session State Initialization ---
if "user_memory" not in st.session_state:
    st.session_state.user_memory = defaultdict(list)
if "complaint_log" not in st.session_state:
    st.session_state.complaint_log = []

# --- Helper functions ---
def detect_keywords(text):
    escalation_keywords = ["cancel", "refund", "lawsuit", "angry", "not working", "terrible", "bad", "worst", "broken"]
    for word in escalation_keywords:
        if word.lower() in text.lower():
            return word
    return None

def generate_response(complaint, history=[]):
    if any(neg in complaint.lower() for neg in ["not", "never", "no", "worst", "angry", "cancel"]):
        return "We’re really sorry to hear that. We’ve flagged this for review and someone from our team will follow up shortly."
    return "Thanks for reaching out! We’ve noted your concern and are working on it."

# --- Submit Complaint ---
with st.expander("📩 Submit a New Complaint", expanded=True):
    user_id = st.text_input("User ID")
    complaint_text = st.text_area("Complaint Text", height=100)

    if st.button("Generate Reply"):
        if not user_id or not complaint_text:
            st.warning("Please enter both User ID and Complaint.")
        else:
            history = st.session_state.user_memory[user_id]
            reply = generate_response(complaint_text, history)
            keyword = detect_keywords(complaint_text)
            ticket = {
                "ticket_id": str(uuid.uuid4())[:8],
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "user_id": user_id,
                "text": complaint_text,
                "agent_reply": reply,
                "escalated": keyword is not None,
                "trigger_keyword": keyword or ""
            }
            st.session_state.complaint_log.append(ticket)
            st.session_state.user_memory[user_id].append((complaint_text, reply))
            st.success("Response generated below 👇")
            st.markdown(f"**AI Reply:** {reply}")

# --- Upload CSV Complaints ---
with st.expander("📤 Upload Complaints in Bulk (.csv)"):
    uploaded_file = st.file_uploader("Upload a CSV with columns 'user_id' and 'text'", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if "user_id" in df.columns and "text" in df.columns:
            for _, row in df.iterrows():
                uid = str(row["user_id"])
                complaint = row["text"]
                reply = generate_response(complaint)
                keyword = detect_keywords(complaint)
                ticket = {
                    "ticket_id": str(uuid.uuid4())[:8],
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "user_id": uid,
                    "text": complaint,
                    "agent_reply": reply,
                    "escalated": keyword is not None,
                    "trigger_keyword": keyword or ""
                }
                st.session_state.complaint_log.append(ticket)
                st.session_state.user_memory[uid].append((complaint, reply))
            st.success(f"Uploaded and processed {len(df)} complaints.")
        else:
            st.error("CSV must have 'user_id' and 'text' columns.")

# --- Complaint Log and Charts ---
with st.expander("📊 Agent Feedback Summary", expanded=True):
    log_df = pd.DataFrame(st.session_state.complaint_log)
    if not log_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Escalation Trend")
            trend = log_df.groupby("timestamp")["escalated"].sum()
            fig1, ax1 = plt.subplots(figsize=(4, 3))
            trend.plot(kind="line", ax=ax1)
            ax1.set_ylabel("Escalated Tickets")
            ax1.set_xlabel("Time")
            st.pyplot(fig1)

        with col2:
            st.subheader("Top Escalation Triggers")
            kw_counts = Counter(log_df[log_df["escalated"]]["trigger_keyword"].dropna())
            fig2, ax2 = plt.subplots(figsize=(4, 3))
            ax2.bar(kw_counts.keys(), kw_counts.values())
            ax2.set_ylabel("Mentions")
            ax2.set_xlabel("Trigger Keyword")
            st.pyplot(fig2)
    else:
        st.info("No complaints submitted yet.")

# --- Ticket History Viewer ---
with st.expander("📁 View Complaint Log"):
    log_df_display = pd.DataFrame(st.session_state.complaint_log)
    if not log_df_display.empty:
        st.dataframe(log_df_display[["ticket_id", "timestamp", "user_id", "text", "agent_reply", "escalated", "trigger_keyword"]], use_container_width=True)
        st.download_button("Download CSV", data=log_df_display.to_csv(index=False), file_name="complaint_log.csv", mime="text/csv")
    else:
        st.info("No tickets to display yet.")
