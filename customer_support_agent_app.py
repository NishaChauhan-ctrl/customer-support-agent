
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import uuid

st.set_page_config(page_title="SupportGenie", page_icon="🧞", layout="wide")

# Inject custom CSS for color and branding
st.markdown("""
<style>
    header {visibility: hidden;}
    .reportview-container .main footer {visibility: hidden;}
    .main {
        background-color: #f9fbfc;
    }
    .block-container {
        padding-top: 2rem;
    }
    .supportgenie-footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        color: #888;
        text-align: center;
        padding: 10px;
    }
    .stButton>button {
        border: 1px solid #ddd;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Branding header
st.markdown("## 🧞‍♂️ SupportGenie")
st.markdown("AI-powered complaint handling agent with escalation memory and tone control.")

# Initialize session state
if "user_memory" not in st.session_state:
    st.session_state.user_memory = {}

if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

def generate_response(text, tone="neutral"):
    if tone == "friendly":
        return f"Hey there! 😊 Thanks for your message. We're on it!"
    elif tone == "formal":
        return f"Thank you for reaching out. We will address this promptly."
    elif tone == "apologetic":
        return f"We're truly sorry to hear that. Let us help you right away."
    else:
        return f"Thanks for your message. We're reviewing it now."

def log_complaint(user_id, text, reply, escalated=False, keyword=None):
    ticket_id = f"T{str(uuid.uuid4())[:4]}"
    entry = {
        "ticket_id": ticket_id,
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "text": text,
        "agent_reply": reply,
        "escalated": escalated,
        "trigger_keyword": keyword
    }
    st.session_state.feedback_log.append(entry)
    if user_id not in st.session_state.user_memory:
        st.session_state.user_memory[user_id] = []
    st.session_state.user_memory[user_id].append(entry)

tab1, tab2, tab3 = st.tabs(["🤖 Chat Interface", "📊 Feedback Stats", "📁 Batch Processor"])

with tab1:
    with st.expander("📝 Submit a Complaint", expanded=True):
        user_id = st.text_input("User ID")
        complaint = st.text_area("Describe your issue")
        tone = st.selectbox("Select Tone", ["neutral", "friendly", "formal", "apologetic"])

        if user_id and complaint:
            if st.button("Generate AI Reply"):
                st.session_state.generated_reply = generate_response(complaint, tone)

            if "generated_reply" in st.session_state:
                edited_reply = st.text_area("Edit Reply (optional)", value=st.session_state.generated_reply, key="editable_reply")

                if st.button("Confirm & Log Reply"):
                    log_complaint(user_id, complaint, edited_reply)
                    st.success("Reply logged successfully.")
                    st.markdown(f"**AI Reply:** {edited_reply}")
                    del st.session_state.generated_reply

    st.markdown("---")
    st.markdown("### 🤔 Was this reply helpful?")
    if st.session_state.feedback_log:
        last_reply = st.session_state.feedback_log[-1]
        if st.button("👍 Helpful"):
            last_reply["escalated"] = False
            st.success("Thanks for your feedback!")
        if st.button("👎 Unhelpful"):
            last_reply["escalated"] = True
            st.warning("We appreciate your honesty. Logged as unhelpful.")

with tab2:
    st.subheader("📊 Agent Feedback Summary")
    log_df = pd.DataFrame(st.session_state.feedback_log)
    if not log_df.empty:
        feedback_counts = log_df["escalated"].map({True: "Unhelpful", False: "Helpful"}).value_counts()
        with st.container():
            col1, col2 = st.columns([1, 2])
            with col1:
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.pie(feedback_counts.values, labels=feedback_counts.index, autopct='%1.1f%%', startangle=90)
                ax.axis("equal")
                st.pyplot(fig)
            with col2:
                top_replies = log_df[~log_df["escalated"]].dropna().head(3)
                worst_replies = log_df[log_df["escalated"]].dropna().head(3)
                st.markdown("**🏆 Top 3 Helpful Replies**")
                for _, row in top_replies.iterrows():
                    st.markdown(f"- {row['agent_reply']}")
                st.markdown("**❌ Bottom 3 Unhelpful Replies**")
                for _, row in worst_replies.iterrows():
                    st.markdown(f"- {row['agent_reply']}")
    else:
        st.info("No feedback logged yet.")

with tab3:
    st.subheader("📁 Upload CSV for Batch Processing")
    uploaded = st.file_uploader("Upload complaints CSV (with user_id and text columns)")
    if uploaded:
        df = pd.read_csv(uploaded)
        if "user_id" in df.columns and "text" in df.columns:
            for _, row in df.iterrows():
                reply = generate_response(row["text"])
                log_complaint(row["user_id"], row["text"], reply)
            st.success("Batch processing complete.")
        else:
            st.error("CSV must contain 'user_id' and 'text' columns.")

# Footer
st.markdown('<div class="supportgenie-footer">🔧 Built with ❤️ by Nisha | SupportGenie © 2025</div>', unsafe_allow_html=True)
