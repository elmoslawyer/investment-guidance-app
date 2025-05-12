import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from openai import OpenAI
import streamlit.components.v1 as components

# --- OpenAI Client ---
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# --- Session State ---
if "round" not in st.session_state:
    st.session_state.round = 1
if "recommendation_history" not in st.session_state:
    st.session_state.recommendation_history = []
if "financial_graph_data" not in st.session_state:
    st.session_state.financial_graph_data = []

def reset_session():
    st.session_state.round = 1
    st.session_state.recommendation_history = []
    st.session_state.financial_graph_data = []
    st.session_state.user_story_text = ""

# --- App UI ---
st.title("📈 AI-Powered Investment Guidance (3 Scenarios Max)")
st.caption("Get GPT advice + simulate financial outcomes for 3 customized profiles.")

# --- Microphone Integration ---
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
    recognition.lang = 'en-US'; recognition.interimResults = false;
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
    function startListening() { recognition.start(); }
    function stopListening() { recognition.stop(); }
</script>
<div style="margin-bottom: 10px;">
    <button onclick="startListening()">🎙️ Start Talking</button>
    <button onclick="stopListening()" style="margin-left: 10px;">🛑 Stop Talking</button>
    <div id="mic-status" style="margin-top: 8px; font-weight: bold; color: gray;">🎙️ Mic off</div>
</div>
""", height=200)

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv("673_Final_Dataset.csv")

data = load_data()

# --- Form Inputs ---
st.header(f"Scenario {st.session_state.round} of 3")
with st.form("user_form"):
    goals = st.multiselect("Financial Goals:", ["Homeownership", "Early Retirement", "Education Fund", "Travel", "Wealth Growth"])
    horizon = st.selectbox("Investment Horizon:", ["Short", "Medium", "Long"])
    risk = st.select_slider("Risk Tolerance:", ["Low", "Medium", "High"])
    knowledge = st.selectbox("Investment Knowledge:", ["Beginner", "Intermediate", "Advanced"])

    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input("Monthly Income ($)", min_value=0, step=100)
        return_rate = st.number_input("Expected Return (%)", -100.0, 100.0, 7.0)
    with col2:
        savings = st.number_input("Current Savings ($)", min_value=0, step=100)
        bear_loss = st.number_input("Bear Market Loss (%)", -100.0, 0.0, -15.0)

    years = st.slider("Growth Duration (Years)", 1, 50, 10)

    if "user_story_text" not in st.session_state:
        st.session_state.user_story_text = ""

    user_story = st.text_area("Optional: More about your situation", placeholder="Example: I just graduated...", value=st.session_state.user_story_text, key="user_story_text")
    submitted = st.form_submit_button("Run Scenario")

# --- Simulate Portfolio Growth ---
def simulate_growth(starting, annual_return, bear_loss, duration, bear_year=3):
    values = [starting]
    for year in range(1, duration + 1):
        last = values[-1]
        updated = last * (1 + (bear_loss if year == bear_year else annual_return) / 100)
        values.append(round(updated, 2))
    return values

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

    user_profile = f"Goals: {', '.join(goals)} | Horizon: {horizon} | Risk: {risk} | Knowledge: {knowledge}"
    context = user_story or "No additional context provided."
    strategies_summary = top_matches[['Strategy_Name', 'Goals', 'Risk_Tolerance', 'Horizon', 'Description']].to_string(index=False)

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
                {"role": "system", "content": "You are a helpful investment advisor."},
                {"role": "user", "content": gpt_prompt}
            ]
        )
        summary = response.choices[0].message.content
        st.session_state.recommendation_history.append(summary)
    except Exception as e:
        st.error("OpenAI Error")
        st.exception(e)

    # Simulate and store graph
    values = simulate_growth(savings, return_rate, bear_loss, years)
    year_range = list(range(0, years + 1))
    st.session_state.financial_graph_data.append({
        "label": f"Scenario {st.session_state.round}",
        "years": year_range,
        "values": values
    })

    # Show GPT result
    st.subheader(f"🤖 Recommendation for Scenario {st.session_state.round}")
    st.markdown(summary)

    # Show Graph
    st.subheader("📊 Projected Portfolio Value")
    fig, ax = plt.subplots()
    ax.plot(year_range, values, marker='o')
    ax.set_xlabel("Year")
    ax.set_ylabel("Value ($)")
    ax.set_title("Growth Over Time")
    st.pyplot(fig)

    st.session_state.round += 1

# --- Recommendation History ---
if st.session_state.recommendation_history:
    st.subheader("🧠 Past Recommendations")
    for i, rec in enumerate(st.session_state.recommendation_history, 1):
        st.markdown(f"### Scenario {i}")
        st.markdown(rec)

# --- Combine Graphs ---
if st.session_state.round > 2 and len(st.session_state.financial_graph_data) > 1:
    if st.button("📈 Combine Graphs"):
        st.subheader("📉 Combined Financial Simulations")
        fig, ax = plt.subplots()
        for entry in st.session_state.financial_graph_data:
            ax.plot(entry["years"], entry["values"], label=entry["label"])
        ax.set_title("Scenario Comparison")
        ax.set_xlabel("Year")
        ax.set_ylabel("Value ($)")
        ax.legend()
        st.pyplot(fig)

# --- Scenario Control ---
col1, col2 = st.columns(2)
with col1:
    if st.session_state.round <= 3:
        st.button("🔁 Different Scenario")
with col2:
    st.button("🔄 Restart", on_click=reset_session)

if st.session_state.round > 3:
    st.warning("You’ve reached the 3-scenario limit. Click 'Restart' to try a new set.")
