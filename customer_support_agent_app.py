# Force redeploy at !:31am
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

tab1, tab2 = st.tabs(["💬 Submit Complaint", "📊 Feedback Stats"])

# --- Tab 1: Submit Complaint ---
with tab1:
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
            with st.form("confirm_reply_form"):
                edited_reply = st.text_area("AI-generated reply:", value=st.session_state.generated_reply, height=100, key="editable_reply_form")
                st.caption("⚠️ This reply is AI-generated. Please verify before sending.")
                submit_confirm = st.form_submit_button("✅ Confirm and Log")
                if submit_confirm:
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
                    del st.session_state.current_user_id
                    del st.session_state.current_complaint
                    st.success("✅ Reply logged successfully.")

    st.subheader("👍👎 Rate Agent Replies")
    df = st.session_state.log_df
    for i, row in df[df["feedback"].isnull()].head(5).iterrows():
        st.markdown(f"**{row['agent_reply']}**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Helpful", key=f"thumbs_up_{i}"):
                st.session_state.log_df.at[i, "feedback"] = "positive"
        with col2:
            if st.button("👎 Unhelpful", key=f"thumbs_down_{i}"):
                st.session_state.log_df.at[i, "feedback"] = "negative"

# --- Tab 2: Feedback Summary ---
with tab2:
    df = st.session_state.log_df
    st.markdown("### 📊 Overall Feedback Summary")
    if not df.empty:
        feedback_counts = df["feedback"].value_counts()
        if not feedback_counts.empty:
            fig, ax = plt.subplots(figsize=(2.5, 2.5))
            ax.pie(feedback_counts.values, labels=feedback_counts.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

        st.subheader("🏆 Top 3 Replies")
        top_replies = df[df["feedback"] == "positive"].head(3)
        for _, r in top_replies.iterrows():
            st.markdown(f"✅ “{r['agent_reply']}”")

        st.subheader("❌ Bottom 3 Replies")
        bottom_replies = df[df["feedback"] == "negative"].head(3)
        for _, r in bottom_replies.iterrows():
            st.markdown(f"❌ “{r['agent_reply']}”")
    else:
        st.info("No feedback data yet.")
