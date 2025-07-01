
# --- Feedback Metrics Section ---
with st.expander("📊 Agent Feedback Summary", expanded=True):
    if "feedback_log" in st.session_state and st.session_state["feedback_log"]:
        feedback_df = pd.DataFrame(st.session_state["feedback_log"])
        helpful_pct = 100 * feedback_df["helpful"].mean()
        st.metric("👍 Helpful Replies", f"{helpful_pct:.1f}%")

        feedback_df["timestamp"] = pd.to_datetime(feedback_df["timestamp"])
        feedback_chart = feedback_df.groupby(feedback_df["timestamp"].dt.date)["helpful"].mean() * 100
        st.line_chart(feedback_chart, use_container_width=True)
    else:
        st.info("No feedback yet. Users can rate replies with 👍 or 👎.")


# --- Feedback Metrics Section ---
with st.expander("📊 Agent Feedback Summary", expanded=True):
    if "feedback_log" in st.session_state and st.session_state["feedback_log"]:
        feedback_df = pd.DataFrame(st.session_state["feedback_log"])
        helpful_pct = 100 * feedback_df["helpful"].mean()
        st.metric("👍 Helpful Replies", f"{helpful_pct:.1f}%")

        feedback_df["timestamp"] = pd.to_datetime(feedback_df["timestamp"])
        feedback_chart = feedback_df.groupby(feedback_df["timestamp"].dt.date)["helpful"].mean() * 100
        st.line_chart(feedback_chart, use_container_width=True)
    else:
        st.info("No feedback yet. Users can rate replies with 👍 or 👎.")

import streamlit as st
import pandas as pd

# --- Branding ---
st.set_page_config(page_title="SupportGenie", page_icon="🧞‍♂️", layout="wide")

col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("supportgenie_logo.png", width=80)
with col_title:
    st.markdown("## 🧞‍♂️ SupportGenie")
    st.markdown("*AI assistant for triaging complaints, escalating critical issues, and crafting empathetic replies.*")


# --- Onboarding & App Intro ---
with st.expander("ℹ️ What does SupportGenie do?", expanded=True):
    st.markdown("""
**SupportGenie** is an AI-powered assistant that helps support teams:
- 📝 Receive and log complaints from users
- 🤖 Generate empathetic replies using AI (based on tone)
- 🚨 Escalate complaints automatically when trigger words are detected
- 📊 Track complaints, reply effectiveness, and team performance

**How It Works**
- **NPS** = Net Promoter Score (user sentiment, from 0–10)
- **Escalation** = complaint contains a risky/urgent keyword (like “refund” or “crash”)
- **Tone Selector** = lets you control how the AI replies (friendly, concise, empathetic)
- **User Memory** = the agent remembers what each user has said in the past

You can test the app by submitting a fake complaint below 👇
""")



# Agent tone selector
st.sidebar.header("🎭 Agent Personality")
persona = st.sidebar.selectbox(
    "Choose a tone for the AI agent:",
    ["Empathetic", "Concise", "Friendly"]
)

# Sidebar for escalation keyword configuration

# Sidebar for escalation keyword configuration
st.sidebar.header("🛠 Escalation Settings")
default_keywords = "refund, cancel, crash, bug, lawsuit, fraud"
if "escalation_keywords" not in st.session_state:
    st.session_state["escalation_keywords"] = [k.strip().lower() for k in default_keywords.split(",")]

keyword_input = st.sidebar.text_input(
    "Trigger Keywords (used to auto-escalate)",
    value=", ".join(st.session_state["escalation_keywords"])
)
st.session_state["escalation_keywords"] = [k.strip().lower() for k in keyword_input.split(",")]


keyword_input = st.sidebar.text_input(
    "Trigger Keywords (comma-separated)",
    value=", ".join(st.session_state["escalation_keywords"])
)
st.session_state["escalation_keywords"] = [k.strip().lower() for k in keyword_input.split(",")]

import matplotlib.pyplot as plt
from collections import Counter
import random
from datetime import datetime
import openai

# ---------- Branding ----------
st.set_page_config(page_title="AI Support Agent", page_icon="🤖", layout="wide")
st.markdown("<h1 style='text-align:center; color:#4A90E2;'>🤖 AI-Powered Customer Support Agent</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ---------- Session State ----------
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

def should_escalate(text):
    escalation_keywords = ["crash", "data", "billing", "error", "unresponsive", "delete", "lost", "freeze"]
    return any(kw in text.lower() for kw in escalation_keywords)

def rule_based_reply(text, history=[]):
    if any(word in text.lower() for word in ["crash", "freeze", "data", "delete", "billing", "error"]):
        return "I'm sorry to hear that. We're escalating your issue to our support team right away."
    if "not working" in text.lower():
        return "Thanks for reporting this. We'll investigate the issue shortly."
    return "Thanks for your feedback! We'll look into it."

def ai_reply(text, history=[], api_key=None):
    try:
        if not api_key:
            return None
        openai.api_key = api_key
        prompt = f"You are a helpful support agent. A customer just wrote: '{text}'. Reply empathetically."
        
        tone_styles = {
            "Empathetic": "Respond kindly and reassuringly, acknowledging user frustration.",
            "Concise": "Respond briefly and to the point with clear next steps.",
            "Friendly": "Be upbeat, casual, and helpful like a human support rep."
        }
        prompt_style = tone_styles.get(persona, "Respond helpfully.")


        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and empathetic customer support agent."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message["content"].strip()
    except:
        return None

# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(["📥 Live Complaints", "📁 Batch Upload", "📊 Dashboard"])

with tab1:
    st.header("Submit a New Complaint")

    st.subheader("🛠️ AI Settings")
    use_ai = st.checkbox("Use AI model for reply")
    api_key = st.text_input("OpenAI API Key (leave empty to test rule-based reply)", type="password")

    user_id = st.text_input("User ID", value="U001", help="Enter a unique identifier for the user")
    user_input = st.text_area("Complaint", value=random.choice([x[1] for x in sample_data]), height=100, help="Describe the issue or complaint here")

    if st.button("Generate Reply"):
        timestamp = datetime.now().isoformat(timespec='seconds')
        history = st.session_state.user_memory[user_id]
        escalate_flag = should_escalate(user_input)

        reply = None
        if use_ai:
            reply = ai_reply(user_input, history, api_key)
        if not reply:
            reply = rule_based_reply(user_input, history)

        badge_color = "#F44336" if escalate_flag else "#4CAF50"
        badge_label = "🚨 Escalated" if escalate_flag else "✅ Resolved"
        styled_badge = f"<span style='color:white; background-color:{badge_color}; padding:4px 8px; border-radius:5px;'>{badge_label}</span>"

        st.markdown(styled_badge, unsafe_allow_html=True)
        st.success(reply)

        feedback_col1, feedback_col2 = st.columns([1, 1])
        with feedback_col1:
            if st.button("👍", key=f"up_{timestamp}"):
                st.session_state.complaint_log[-1]["feedback"] = "up"
        with feedback_col2:
            if st.button("👎", key=f"down_{timestamp}"):
                st.session_state.complaint_log[-1]["feedback"] = "down"

        st.session_state.user_memory[user_id].append(user_input)
        st.session_state.complaint_log.append({
            "ticket_id": f"TKT{len(st.session_state.complaint_log)+1:04}",
            "user_id": user_id,
            "timestamp": timestamp,
            "text": user_input,
            "history": "; ".join(history[-2:]),
            "agent_reply": reply,
            "feedback": None,  # thumbs up/down placeholder
            "escalated": escalate_flag,
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
                        if use_ai and api_key:
                            reply = ai_reply(text, hist, api_key)
                        else:
                            reply = rule_based_reply(text, hist)

                        st.session_state.user_memory[uid].append(text)

                        outputs.append({
                            "ticket_id": f"TKT{len(st.session_state.complaint_log)+len(outputs)+1:04}",
                            "timestamp": timestamp,
                            "user_id": uid,
                            "text": text,
                            "history": "; ".join(hist[-2:]),
                            "agent_reply": reply,
            "feedback": None,  # thumbs up/down placeholder
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
                ax2.bar(list(kw_counts.keys()), list(kw_counts.values()), color="#4A90E2")
                ax2.set_title("Top Escalation Keywords")
                ax2.set_xlabel("Keyword")
                ax2.set_ylabel("Count")
                st.pyplot(fig2)

        log_df_display = log_df[["ticket_id", "timestamp", "user_id", "text", "agent_reply", "escalated", "trigger_keyword", "feedback"]]
        st.download_button(
            "📥 Download Complaint Log",
            data=log_df.to_csv(index=False),
            file_name="complaint_log.csv",
            mime="text/csv"
        )
    else:
        st.info("No complaints submitted yet.")
