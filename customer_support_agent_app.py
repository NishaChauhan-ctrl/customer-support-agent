
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

st.set_page_config(page_title="SupportGenie - AI Customer Agent", layout="wide")

# --- Theme toggle ---
theme = st.sidebar.selectbox("🎨 Select Theme", ["Light", "Dark", "SupportGenie"])

if theme == "Dark":
    st.markdown("""
        <style>
        .main {
            background-color: #0e1117;
            color: white;
        }
        .stTextInput > div > input,
        .stTextArea textarea {
            background-color: #262730;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

elif theme == "SupportGenie":
    st.markdown("""
        <style>
        .main {
            background-color: #f0f6ff;
            color: #112a46;
        }
        .stTextInput > div > input,
        .stTextArea textarea {
            background-color: #ffffff;
            color: #112a46;
        }
        </style>
    """, unsafe_allow_html=True)


# Logo and title
st.image("supportgenie_logo.png", width=80)
st.title("🤖 SupportGenie")
st.markdown("*AI assistant for triaging complaints, generating empathetic replies, and escalating risks.*")

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

# --- Session state init ---
if "log_df" not in st.session_state:
    st.session_state.log_df = pd.DataFrame(columns=["ticket_id", "timestamp", "user_id", "text", "agent_reply", "escalated", "trigger_keyword"])
if "user_memory" not in st.session_state:
    st.session_state.user_memory = {}
if "ticket_counter" not in st.session_state:
    st.session_state.ticket_counter = 1
if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

# --- Sidebar config ---
st.sidebar.header("🛠 Escalation Settings")
default_keywords = "refund, cancel, crash, bug, lawsuit, fraud"
if "escalation_keywords" not in st.session_state:
    st.session_state["escalation_keywords"] = [k.strip().lower() for k in default_keywords.split(",")]

keyword_input = st.sidebar.text_input(
    "Trigger Keywords (used to auto-escalate)",
    value=", ".join(st.session_state["escalation_keywords"])
)
st.session_state["escalation_keywords"] = [k.strip().lower() for k in keyword_input.split(",")]

# --- Complaint Submission Form ---
with st.expander("📨 Submit a Complaint", expanded=True):
    with st.form("complaint_form"):
        user_id = st.text_input("User ID")
        complaint_text = st.text_area("Complaint Text", height=100)
        tone = st.selectbox("AI Reply Tone", ["Empathetic", "Concise", "Friendly"])
        submitted = st.form_submit_button("Generate Reply")

    if submitted and user_id and complaint_text:
        # Escalation check
        escalated = False
        trigger = None
        for word in st.session_state["escalation_keywords"]:
            if word in complaint_text.lower():
                escalated = True
                trigger = word
                break

        # User memory
        history = st.session_state.user_memory.get(user_id, [])
        history.append(complaint_text)
        st.session_state.user_memory[user_id] = history

        # Placeholder reply (no API used)
        tone_text = {"Empathetic": "I understand how frustrating this must be.",
                     "Concise": "Thanks for reporting. We'll fix it.",
                     "Friendly": "Hey! Thanks for flagging this!"}
        reply = f"{tone_text[tone]} We're working on it."

        # Save log
        ticket_id = f"T-{st.session_state.ticket_counter:03}"
        st.session_state.ticket_counter += 1
        new_row = {
            "ticket_id": ticket_id,
            "timestamp": datetime.datetime.now(),
            "user_id": user_id,
            "text": complaint_text,
            "agent_reply": reply,
            "escalated": escalated,
            "trigger_keyword": trigger
        }
        st.session_state.log_df = pd.concat([st.session_state.log_df, pd.DataFrame([new_row])], ignore_index=True)

        st.success("AI Response:")
        st.write(reply)

        # Feedback
        col1, col2 = st.columns([1, 6])
        with col1:
            if st.button("👍", key=f"up_{ticket_id}"):
                st.session_state.feedback_log.append({"timestamp": datetime.datetime.now(), "helpful": 1})
        with col2:
            if st.button("👎", key=f"down_{ticket_id}"):
                st.session_state.feedback_log.append({"timestamp": datetime.datetime.now(), "helpful": 0})

# --- Feedback Metrics Section ---
if "feedback_log" in st.session_state and st.session_state["feedback_log"]:
    with st.expander("📊 Agent Feedback Summary", expanded=True):
        feedback_df = pd.DataFrame(st.session_state["feedback_log"])
        helpful_pct = 100 * feedback_df["helpful"].mean()
        st.metric("👍 Helpful Replies", f"{helpful_pct:.1f}%")

        feedback_df["timestamp"] = pd.to_datetime(feedback_df["timestamp"])
        feedback_chart = feedback_df.groupby(feedback_df["timestamp"].dt.date)["helpful"].mean() * 100
        st.line_chart(feedback_chart, use_container_width=True)
else:
    with st.expander("📊 Agent Feedback Summary", expanded=True):
        st.info("No feedback yet. Users can rate replies with 👍 or 👎.")

# --- Dashboard Logs ---
st.header("📈 Complaint Dashboard")
log_df_display = st.session_state.log_df[["ticket_id", "timestamp", "user_id", "text", "agent_reply", "escalated", "trigger_keyword"]]
st.dataframe(log_df_display, use_container_width=True)
