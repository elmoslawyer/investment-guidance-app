import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import openai

# Set your OpenAI API key
openai.api_key = "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
"

st.title("AI-Augmented Investment Guidance for New Graduates")
st.markdown("""
This tool helps new graduates receive personalized investment guidance based on your current financial profile.
""")

# --- User Inputs ---
with st.form("user_form"):
    st.header("Tell Us About You")

    goals = st.multiselect(
        "What are your financial goals?",
        ["Homeownership", "Early Retirement", "Education Fund", "Travel", "Wealth Growth"]
    )

    horizon = st.selectbox("What is your investment horizon?", ["Short (1–3 years)", "Medium (3–7 years)", "Long (7+ years)"])
    risk = st.select_slider("What is your risk tolerance?", options=["Low", "Medium", "High"])

    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input("Monthly Income ($)", min_value=0, step=100)
    with col2:
        savings = st.number_input("Current Savings ($)", min_value=0, step=100)

    knowledge = st.selectbox("What is your investment knowledge level?", ["Beginner", "Intermediate", "Advanced"])

    submitted = st.form_submit_button("Get My Investment Guidance")

# --- Free Response Section ---
st.markdown("## Personal Financial Situation (Optional)")
user_story = st.text_area(
    "Briefly describe your current financial situation or any plans you'd like considered.",
    placeholder="Example: I just graduated, working part-time, expecting to go full-time soon..."
)
if user_story:
    st.write("Thanks for sharing! Here's what you entered:")
    st.info(user_story)

# --- Load Data and Match Recommendations ---
@st.cache_data
def load_data():
    return pd.read_csv("673_Final_Dataset.csv")

data = load_data()

if submitted:
    st.subheader("Your Top Investment Recommendations")

    filtered = data.copy()

    def score_row(row):
        score = 0
        if row['Risk_Tolerance'].lower() == risk.lower():
            score += 1
        if any(goal.lower() in row['Goals'].lower() for goal in goals):
            score += 1
        if horizon.lower().split()[0] in row['Horizon'].lower():
            score += 1
        if row['Knowledge_Level'].lower() == knowledge.lower():
            score += 1
        return score

    filtered["Match_Score"] = filtered.apply(score_row, axis=1)
    top_matches = filtered.sort_values("Match_Score", ascending=False).head(3)

    if not top_matches.empty:
        st.success("Top Matches Based on Your Profile:")
        for i, row in top_matches.iterrows():
            st.markdown(f"### {row['Strategy_Name']}")
            st.markdown(f"**Goals:** {row['Goals']}")
            st.markdown(f"**Risk Tolerance:** {row['Risk_Tolerance']}, **Horizon:** {row['Horizon']}")
            st.markdown(f"**Description:** {row['Description']}")
            st.markdown("---")

        # --- GPT-Based Summary ---
        strategies_summary = top_matches[['Strategy_Name', 'Goals', 'Risk_Tolerance', 'Horizon', 'Description']].to_string(index=False)
        user_profile = f"Goals: {', '.join(goals)} | Horizon: {horizon} | Risk Tolerance: {risk} | Knowledge: {knowledge}"

        gpt_prompt = f"""
You are an investment assistant AI.

The user's profile is as follows:
{user_profile}

They also shared this about their situation:
"""
{user_story if user_story else "No additional context provided."}
"""

Here are the top 3 matching investment strategies:
{strategies_summary}

Please give a short, friendly recommendation summarizing which strategy you would suggest and why, personalized to their situation.
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful and friendly investment advisor for young professionals."},
                    {"role": "user", "content": gpt_prompt}
                ]
            )
            summary = response['choices'][0]['message']['content']
            st.subheader("AI-Powered Recommendation Summary")
            st.markdown(f"> {summary}")
        except Exception as e:
            st.error("There was an error retrieving the AI recommendation.")
            st.exception(e)
    else:
        st.warning("No suitable matches found. Try broadening your criteria.")
