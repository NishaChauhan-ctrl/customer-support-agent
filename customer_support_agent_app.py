import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict

st.set_page_config(page_title="SupportGenie", layout="wide")

# --- Initialize State ---
if "user_memory" not in st.session_state:
    st.session_state.user_memory = defaultdict(list)

if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

if "log_df" not in st.session_state:
    st.session_state.log_df = pd.DataFrame(columns=[
        "ticket_id", "timestamp", "user_id", "text", "agent_reply",
        "escalated", "trigger_keyword", "feedback"
    ])

# --- App Bar ---
st.markdown("<h1 style='color:#6342ff;'>SupportGenie 🤖</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color:gray;'>Your AI-powered customer support co-pilot</h4>", unsafe_allow_html=True)

# --- Tone Selector ---
tone = st.selectbox("Select agent tone for replies:", ["Friendly", "Apologetic", "Formal"])

# --- Submit Complaint Section ---
with st.expander("📝 Submit a Complaint", expanded=True):
    user_id = st.text_input("User ID", "")
    complaint = st.text_area("Complaint Text", placeholder="Describe your issue here...", height=100)
    if st.button("Generate Reply"):
        if user_id and complaint:
            reply = f"[{tone}] Thank you for reaching out. We understand your concern: '{complaint[:60]}...'"
            escalated = any(kw in complaint.lower() for kw in ["crash", "error", "not working", "urgent"])
            keyword = next((kw for kw in ["crash", "error", "not working", "urgent"] if kw in complaint.lower()), "")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ticket_id = f"T{len(st.session_state.log_df)+1:04}"

            # Let user edit reply before finalizing
            final_reply = st.text_area("✏️ Edit AI reply before logging:", reply)
            st.caption("⚠️ This reply is AI-generated. Please verify before sending.")

            if st.button("Confirm and Log"):
                new_row = {
                    "ticket_id": ticket_id,
                    "timestamp": timestamp,
                    "user_id": user_id,
                    "text": complaint,
                    "agent_reply": final_reply,
                    "escalated": escalated,
                    "trigger_keyword": keyword,
                    "feedback": None
                }
                st.session_state.log_df = pd.concat(
                    [st.session_state.log_df, pd.DataFrame([new_row])], ignore_index=True
                )
                st.session_state.user_memory[user_id].append((complaint, final_reply))

# --- Upload CSV Section ---
with st.expander("📂 Upload Complaints in Bulk"):
    csv_file = st.file_uploader("Upload CSV with 'user_id' and 'text' columns")
    if csv_file:
        df = pd.read_csv(csv_file)
        batch_replies = []
        for _, row in df.iterrows():
            reply = f"[{tone}] We appreciate your feedback: '{row['text'][:60]}...'"
            escalated = any(kw in row["text"].lower() for kw in ["crash", "error", "not working", "urgent"])
            keyword = next((kw for kw in ["crash", "error", "not working", "urgent"] if kw in row["text"].lower()), "")
            ticket_id = f"T{len(st.session_state.log_df)+1:04}"
            new_row = {
                "ticket_id": ticket_id,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": row["user_id"],
                "text": row["text"],
                "agent_reply": reply,
                "escalated": escalated,
                "trigger_keyword": keyword,
                "feedback": None
            }
            st.session_state.log_df = pd.concat(
                [st.session_state.log_df, pd.DataFrame([new_row])], ignore_index=True
            )
            st.session_state.user_memory[row["user_id"]].append((row["text"], reply))
        st.success("Batch replies logged.")
