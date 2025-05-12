import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from openai import OpenAI
import streamlit.components.v1 as components

# --- OpenAI API Key (School Project) ---
client = OpenAI(api_key="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")

# --- OpenAI Key Test ---
st.markdown("### 🔐 Test My OpenAI Key")
if st.button("Run Test"):
    try:
        test_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello in one sentence."}]
        )
        st.success("✅ API key is working!")
        st.info(f"GPT says: {test_response.choices[0].message.content}")
    except Exception as e:
        st.error("❌ There was a problem using your API key.")
        st.exception(e)

# --- App Header ---
st.title("🎓 AI-Augmented Investment Guidance for New Graduates")
st.markdown("""
This tool helps new graduates receive personalized investment guidance based on your current financial profile.
""")

# --- Microphone Input (Browser) ---
st.subheader("🎤 Speak your financial situation")
components.html("""
    <script>
        const streamlitDoc = window.parent.document;

        function sendTextToStreamlit(text) {
            const input = streamlitDoc.querySelector('input[data-testid="stTextInput"]');
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            nativeInputValueSetter.call(input, text);
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }

        var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        function startListening() {
            recognition.start();
        }

        recognition.onresult = function(event) {
            var transcript = event.results[0][0].transcript;
            sendTextToStreamlit(transcript);
        }

        recognition.onerror = function(event) {
            console.error("Speech recognition error", event.error);
        }
    </script>

    <button onclick="startListening()">🎙️ Start Talking</button>
""", height=150)

user_speech_input = st.text_input("Hidden Speech Input", key="speech_input", label_visibility="collapsed")
if user_speech_input:
    st.success(f"You said: {user_speech_input}")

# --- Text-to-Speech Output ---
def speak_browser(text):
    components.html(f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{text}");
    window.speechSynthesis.speak(msg);
    </script>
    """, height=0)

# --- Form Inputs ---
with st.form("user_form"):
    st.header("Tell Us About You")

    goals = st.multiselect(
        "What are your financial goals?",
        ["Homeownership", "Early Retirement", "Education Fund", "Travel", "Wealth Growth"]
    )

    horizon = st.selectbox("What is your investment horizon?", ["Short", "Medium", "Long"])
    risk = st.select_slider("What is your risk tolerance?", options=["Low", "Medium", "High"])

    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input("Monthly Income ($)", min_value=0, step=100)
    with col2:
        savings = st.number_input("Current Savings ($)", min_value=0, step=100)

    knowledge = st.selectbox("What is your investment knowledge level?", ["Beginner", "Intermediate", "Advanced"])

    submitted = st.form_submit_button("Get My Investment Guidance")

# --- Optional Story Input ---
st.markdown("## Optional: Add More Context")
user_story = st.text_area(
    "Briefly describe your current financial situation or any plans you'd like considered.",
    placeholder="Example: I just graduated, working part-time, expecting to go full-time soon..."
)

# --- Load Strategy Data ---
@st.cache_data
def load_data():
    return pd.read_csv("673_Final_Dataset.csv")

data = load_data()

# --- On Submit: Recommend Strategies ---
if submitted:
    st.subheader("🎯 Your Top Investment Recommendations")

    def score_row(row):
        score = 0
        if row['Risk_Tolerance'].lower() == risk.lower():
            score += 1
        if any(goal.lower() in row['Goals'].lower() for goal in goals):
            score += 1
        if horizon.lower() in row['Horizon'].lower():
            score += 1
        if row['Knowledge_Level'].lower() == knowledge.lower():
            score += 1
        return score

    data["Match_Score"] = data.apply(score_row, axis=1)
    top_matches = data.sort_values("Match_Score", ascending=False).head(3)

    if not top_matches.empty:
        st.success("✅ Based on your inputs, we recommend:")
        for _, row in top_matches.iterrows():
            st.markdown(f"### {row['Strategy_Name']}")
            st.markdown(f"**Goals:** {row['Goals']}")
            st.markdown(f"**Risk Tolerance:** {row['Risk_Tolerance']}, **Horizon:** {row['Horizon']}")
            st.markdown(f"**Description:** {row['Description']}")
            st.markdown("---")

        # --- GPT Summary ---
        strategies_summary = top_matches[['Strategy_Name', 'Goals', 'Risk_Tolerance', 'Horizon', 'Description']].to_string(index=False)
        user_profile = f"Goals: {', '.join(goals)} | Horizon: {horizon} | Risk Tolerance: {risk} | Knowledge: {knowledge}"
        context = user_story if user_story else user_speech_input or "No additional context provided."

        gpt_prompt = f"""
You are an investment assistant AI.

The user's profile is:
{user_profile}

They also shared:
{context}

Here are the top 3 matching strategies:
{strategies_summary}

Please give a short, friendly recommendation summarizing which strategy you would suggest and why, personalized to their situation.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful and friendly investment advisor for young professionals."},
                    {"role": "user", "content": gpt_prompt}
                ]
            )
            summary = response.choices[0].message.content
            st.subheader("🤖 AI-Powered Recommendation Summary")
            st.markdown(f"> {summary}")
            speak_browser(summary)
        except Exception as e:
            st.error("⚠️ Error retrieving AI recommendation.")
            st.exception(e)
    else:
        st.warning("No suitable matches found. Try adjusting your inputs.")
