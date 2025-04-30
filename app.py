import pandas as pd
import streamlit as st

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("673_Final_Dataset.csv")

data = load_data()

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

# --- Process Input and Show Results ---
if submitted:
    st.subheader("Your Top Investment Recommendations")

    # Filter dataset (example logic)
    filtered = data.copy()

    # Simple match scoring system
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
        for i, row in top_matches.iterrows():
            st.markdown(f"### Match {i+1} - {row['Strategy_Name']}")
            st.markdown(f"**Recommended For:** {row['Goals']}")
            st.markdown(f"**Risk Tolerance:** {row['Risk_Tolerance']}, **Horizon:** {row['Horizon']}")
            st.markdown(f"**Description:** {row['Description']}")
            st.markdown("---")
    else:
        st.warning("No suitable matches found. Try broadening your criteria.")
