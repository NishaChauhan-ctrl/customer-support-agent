import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict

st.set_page_config(page_title="SupportGenie", layout="wide")

# --- Initialize State ---
if "user_memory" not in st.session_state:
    st.session_state.user_memory = defaultdict(list)

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

def generate_reply(text, tone):
    if tone == "Friendly":
        return f"Hey! Thanks for sharing. We’ll look into this: “{text[:60]}...”"
    elif tone == "Apologetic":
        return f"We're really sorry about the trouble. We understand: “{text[:60]}...”"
    elif tone == "Formal":
        return f"Thank you for reporting this issue. We acknowledge: “{text[:60]}...”"
    else:
        return f"Thanks for reaching out. We understand: “{text[:60]}...”"

# --- Submit Complaint Section ---
with st.expander("📝 Submit a Complaint", expanded=True):
    user_id = st.text_input("User ID", "")
    complaint = st.text_area("Complaint Text", placeholder="Describe your issue here...", height=100)
    if st.button("Generate Reply"):
        if user_id and complaint:
            base_reply = generate_reply(complaint, tone)
            st.session_state.generated_reply = base_reply
            st.session_state.current_user_id = user_id
            st.session_state.current_complaint = complaint

    if "generated_reply" in st.session_state:
        st.markdown("### ✏️ Edit AI Reply Before Logging:")
        edited_reply = st.text_area("AI-generated reply:", value=st.session_state.generated_reply, height=100, key="editable_reply")
        st.caption("⚠️ This reply is AI-generated. Please verify before sending.")
        if st.button("Confirm and Log"):
            complaint = st.session_state.current_complaint
            reply = edited_reply
            user_id = st.session_state.current_user_id
            escalated = any(kw in complaint.lower() for kw in ["crash", "error", "not working", "urgent"])
            keyword = next((kw for kw in ["crash", "error", "not working", "urgent"] if kw in complaint.lower()), "")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ticket_id = f"T{len(st.session_state.log_df)+1:04}"
            new_row = {
                "ticket_id": ticket_id,
                "timestamp": timestamp,
                "user_id": user_id,
                "text": complaint,
                "agent_reply": reply,
                "escalated": escalated,
                "trigger_keyword": keyword,
                "feedback": None
            }
            st.session_state.log_df = pd.concat([st.session_state.log_df, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state.user_memory[user_id].append((complaint, reply))
            del st.session_state.generated_reply
