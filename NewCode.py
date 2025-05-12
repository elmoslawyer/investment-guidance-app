import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from openai import OpenAI
import streamlit.components.v1 as components

# --- Secure API Key ---
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# --- Session State Setup ---
if "round" not in st.session_state:
    st.session_state.round = 1
if "recommendation_history" not in st.session_state:
    st.session_state.recommendation_history = []

# --- Restart Handler ---
def reset_session():
    st.session_state.round = 1
    st.session_state.recommendation_history = []
    st.session_state.user_story_text = ""

# --- App Header ---
st.title("🎓 AI-Augmented Investment Guidance for New Graduates")
st.markdown("Get tailored investment advice. Up to 3 scenario comparisons allowed per session.")

# --- Microphone + Append JS ---
components.html("""
<script>
    const streamlitDoc = window.parent.document;

    function appendTextToStreamlit(text) {
        const inputBox = streamlitDoc.querySelector('textarea[placeholder^="Example: I just graduated"]');
        if (inputBox) {
            const currentText = inputBox.value;
            const newText = currentText.trim() + (currentText ? " " : "") + text;
            inputBox.value = newText;
            inputBox.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.continuous = true;
    recognition.maxAlternatives = 1;

    recognition.onresult = function(event) {
        var transcript = event.results[event.results.length - 1][0].transcript;
        appendTextToStreamlit(transcript);
    };

    recognition.onerror = function(event) {
        document.getElementById('mic-status').innerText = "🎙️ Error occurred";
    };

    recognition.onstart = function() {
        document.getElementById('mic-status').innerText = "🎙️ Listening...";
        document.getElementById('mic-status').style.color = "red";
    };

    recognition.onend = function() {
        document.getElementById('mic-status').innerText = "🎙️ Mic off";
        document.getElementById('mic-status').style.color = "gray";
    };

    function startListening() {
        recognition.start();
    }

    function stopListening() {
        recognition.stop();
    }
</script>

<div style="margin-bottom: 10px;">
    <button onclick="startListening()">🎙️ Start Talking</button>
    <button onclick="stopListening()" style="margin-left: 10px;">🛑 Stop Talking</button>
    <div id="mic-status" style="margin-top: 8px; font-weight: bold; color: gray;">🎙️ Mic off</div>
</div>
""", height=200)

# --- Form Inputs ---
st.header(f"Scenario {st.session_state.round} of 3")

with st.form("scenario_form"):
    goals = st.multiselect("What are your financial goals?", [
        "Homeownership", "Early Retirement", "Education Fund", "Travel", "Wealth Growth"
    ])
    horizon = st.selectbox("What is your investment horizon?", ["Short", "Medium", "Long"])
    risk = st.select_slider("What is your risk tolerance?", options=["Low", "Medium", "High"])
    income = st.number_input("Monthly Income ($)", min_value=0, step=100)
    savings = st.number_input("Current Savings ($)", min_value=0, step=100)
    knowledge = st.selectbox("What is your investment knowledge level?", ["Beginner", "Intermediate", "Advanced"])

    if "user_story_text" not in st.session_state:
        st.session_state.user_story_text = ""

    user_story = st.text_area(
        "Optional: Add more about your financial situation.",
        placeholder="Example: I just graduated and will start full-time work in July.",
        value=st.session_state.user_story_text,
        key="user_story_text"
    )

    submitted = st.form_submit_button("Submit Scenario")

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv("673_Final_Dataset.csv")

data = load_data()

# --- On Submit ---
if submitted and st.session_state.round <= 3:
    def score_row(row):
        score = 0
        if row['Risk_Tolerance'].lower() == risk.lower(): score += 1
        if any(goal.lower() in row['Goals'].lower() for goal in goals): score += 1
        if horizon.lower() in row['Horizon'].lower(): score += 1
        if row['Knowledge_Level'].lower() == knowledge.lower(): score += 1
        return score

    data["Match_Score"] = data.apply(score_row, axis=1)
    top_matches = data.sort_values("Match_Score", ascending=False).head(3)

    strategies_summary = top_matches[['Strategy_Name', 'Goals', 'Risk_Tolerance', 'Horizon', 'Description']].to_string(index=False)
    user_profile = f"Goals: {', '.join(goals)} | Horizon: {horizon} | Risk Tolerance: {risk} | Knowledge: {knowledge}"
    context = st.session_state.user_story_text or "No additional context provided."

    gpt_prompt = f'''
You are an investment assistant AI.
The user's profile:
{user_profile}
They also shared:
{context}
Here are the top 3 matching strategies:
{strategies_summary}
Please give a short, friendly recommendation summarizing which strategy you would suggest and why.
'''

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and friendly investment advisor."},
                {"role": "user", "content": gpt_prompt}
            ]
        )
        summary = response.choices[0].message.content
        st.session_state.recommendation_history.append(summary)
        st.session_state.round += 1
    except Exception as e:
        st.error("Error from OpenAI:")
        st.exception(e)

# --- Show All Prior Recommendations ---
if st.session_state.recommendation_history:
    st.subheader("🧠 Recommendations")
    for idx, rec in enumerate(st.session_state.recommendation_history, 1):
        st.markdown(f"### Scenario {idx}")
        st.markdown(rec)

# --- Scenario Limit and Controls ---
col1, col2 = st.columns(2)
with col1:
    if st.session_state.round <= 3:
        st.button("🔁 Different Scenario")
with col2:
    st.button("🔄 Restart", on_click=reset_session)

if st.session_state.round > 3:
    st.warning("You've reached the 3-scenario limit. Click 'Restart' to begin a new session.")
