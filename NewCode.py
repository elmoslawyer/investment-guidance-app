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

# --- App Title ---
st.title("📈 AI-Powered Investment Guidance (3 Scenarios Max)")

# --- Mic Input ---
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
<div>
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

# --- Form ---
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

# --- Growth Simulation ---
def simulate_growth(starting, annual_return, bear_loss, income, duration):
    values = [starting]
    net_worths = [starting]
    bear_years = []
    for year in range(1, duration + 1):
        last = values[-1] + (income * 12)
        if year % 6 == 0:
            updated = last * (1 + bear_loss / 100)
            bear_years.append(year)
        else:
            updated = last * (1 + annual_return / 100)
        values.append(round(updated, 2))
        net_worths.append(round(updated + (income * 12 * (duration - year)), 2))
    return values, net_worths, bear_years

# --- GPT + Scenario Submission ---
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

    system_prompt = (
        "You are a helpful, friendly, and realistic investment advisor. "
        "In addition to summarizing matching strategies, give practical and detailed financial guidance. "
        "Provide specific suggestions like government bonds for low risk, ETFs or index funds for moderate growth, or high-yield savings for short-term goals. "
        "If the user's goals include retirement, recommend appropriate retirement accounts like Roth IRAs or 401(k)s. "
        "Include an example portfolio allocation tailored to their risk tolerance, goals, and knowledge level. "
        "Do not ask follow-up questions — your response should be complete and self-contained."
    )

    gpt_prompt = f"""
The user's profile:
{user_profile}

They also shared:
{context}

Here are the top 3 matching strategies:
{strategies_summary}

Please provide a complete recommendation that:
- Summarizes the most suitable strategy
- Offers specific and practical financial advice
- Includes an example portfolio allocation
- Recommends retirement accounts if applicable
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": gpt_prompt}
            ]
        )
        summary = response.choices[0].message.content
        st.session_state.recommendation_history.append(summary)
    except Exception as e:
        st.error("OpenAI Error")
        st.exception(e)

    values, net_worths, bear_years = simulate_growth(savings, return_rate, bear_loss, income, years)
    year_range = list(range(0, years + 1))
    st.session_state.financial_graph_data.append({
        "label": f"Scenario {st.session_state.round}",
        "years": year_range,
        "portfolio": values,
        "net_worth": net_worths,
        "bear_years": bear_years
    })

    st.subheader(f"🤖 Recommendation for Scenario {st.session_state.round}")
    st.markdown(summary)

    st.subheader("📊 Portfolio and Net Worth Over Time")
    fig, ax = plt.subplots()
    ax.plot(year_range, values, label="Portfolio Value", marker='o')
    ax.plot(year_range, net_worths, label="Net Worth", linestyle='--')
    for y in bear_years:
        if y < len(values):
            ax.plot(y, values[y], 'ro')
    ax.set_xlabel("Year")
    ax.set_ylabel("Value ($)")
    ax.set_title("Simulation with Bear Markets Every 6 Years")
    ax.legend()
    st.pyplot(fig)

    st.session_state.round += 1

# --- History ---
if st.session_state.recommendation_history:
    st.subheader("🧠 Previous Recommendations")
    for i, rec in enumerate(st.session_state.recommendation_history, 1):
        st.markdown(f"### Scenario {i}")
        st.markdown(rec)

# --- Combine Graphs ---
if st.session_state.round > 2 and len(st.session_state.financial_graph_data) > 1:
    if st.button("📈 Combine Graphs"):
        st.subheader("📉 Combined Portfolio Growth")
        fig1, ax1 = plt.subplots()
        for entry in st.session_state.financial_graph_data:
            ax1.plot(entry["years"], entry["portfolio"], label=entry["label"])
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Portfolio Value ($)")
        ax1.set_title("Portfolio Comparison")
        ax1.legend()
        st.pyplot(fig1)

        st.subheader("📊 Combined Net Worth Growth")
        fig2, ax2 = plt.subplots()
        for entry in st.session_state.financial_graph_data:
            ax2.plot(entry["years"], entry["net_worth"], label=entry["label"])
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Net Worth ($)")
        ax2.set_title("Net Worth Comparison")
        ax2.legend()
        st.pyplot(fig2)

# --- Controls ---
col1, col2 = st.columns(2)
with col1:
    if st.session_state.round <= 3:
        st.button("🔁 Different Scenario")
with col2:
    st.button("🔄 Restart", on_click=reset_session)

if st.session_state.round > 3:
    st.warning("You’ve reached the 3-scenario limit. Click 'Restart' to begin again.")
