import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

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
        for i, row in top_matches.iterrows():
            st.markdown(f"### Match {i+1} - {row['Strategy_Name']}")
            st.markdown(f"**Recommended For:** {row['Goals']}")
            st.markdown(f"**Risk Tolerance:** {row['Risk_Tolerance']}, **Horizon:** {row['Horizon']}")
            st.markdown(f"**Description:** {row['Description']}")
            st.markdown("---")
    else:
        st.warning("No suitable matches found. Try broadening your criteria.")

# --- Investment Growth Visualization ---
st.subheader("Investment Growth Over Time")
initial_investment = st.number_input("Initial Investment ($)", 100, 100000, 1000, step=100)
years = st.slider("Investment Duration (Years)", 1, 40, 10)
expected_return = st.slider("Expected Annual Return (%)", 1.0, 15.0, 7.0)

years_array = np.arange(1, years + 1)
values = initial_investment * (1 + expected_return / 100) ** years_array

fig, ax = plt.subplots()
ax.plot(years_array, values, marker="o")
ax.set_title("Projected Investment Growth")
ax.set_xlabel("Years")
ax.set_ylabel("Value ($)")
st.pyplot(fig)

# --- Budgeting & Net Worth ---
st.subheader("Budget & Net Worth Calculator")
income_budget = st.number_input("Monthly Income for Budgeting ($)", 0, 10000, 3000, step=100)
expenses = st.number_input("Monthly Expenses ($)", 0, 10000, 2000, step=100)
student_loans = st.number_input("Student Loan Balance ($)", 0, 100000, 20000, step=500)

monthly_savings = income_budget - expenses
annual_savings = monthly_savings * 12
net_worth = annual_savings * 5 - student_loans

st.write(f"**Estimated Annual Savings:** ${annual_savings}")
st.write(f"**Estimated Net Worth in 5 Years (excluding investment returns):** ${net_worth}")

# --- Asset Allocation Guidance ---
st.subheader("Explore Investment Options")
risk_profile = st.selectbox("Your Risk Profile for Asset Allocation", ["Conservative", "Moderate", "Aggressive"])

if risk_profile == "Conservative":
    st.markdown("- **Bonds (70%)**")
    st.markdown("- **Dividend Stocks (20%)**")
    st.markdown("- **Real Estate Funds (10%)**")
elif risk_profile == "Moderate":
    st.markdown("- **Index Funds (40%)**")
    st.markdown("- **ETFs (30%)**")
    st.markdown("- **Real Estate / REITs (20%)**")
    st.markdown("- **Crypto (10%)**")
else:
    st.markdown("- **Tech Stocks / Growth ETFs (50%)**")
    st.markdown("- **Crypto (30%)**")
    st.markdown("- **Startups / Alternative Assets (20%)**")

# --- Educational Tooltips ---
with st.expander("What is an ETF?"):
    st.write("An Exchange Traded Fund (ETF) is a type of investment fund that is traded on stock exchanges, much like stocks.")

with st.expander("What is Diversification?"):
    st.write("Diversification is an investment strategy that spreads your investments across various asset classes to reduce risk.")

# --- Market Scenario Planner ---
st.subheader("Market Scenario Planner")
bear = st.slider("Bear Market Avg Return (%)", -20.0, 0.0, -5.0)
neutral = st.slider("Neutral Market Avg Return (%)", 0.0, 10.0, 5.0)
bull = st.slider("Bull Market Avg Return (%)", 5.0, 20.0, 12.0)

investment_scenario = st.number_input("Scenario Investment Amount ($)", 1000, 100000, 5000, step=500)

st.write(f"**Bear Market Future Value (10 years):** ${investment_scenario * (1 + bear/100) ** 10:.2f}")
st.write(f"**Neutral Market Future Value (10 years):** ${investment_scenario * (1 + neutral/100) ** 10:.2f}")
st.write(f"**Bull Market Future Value (10 years):** ${investment_scenario * (1 + bull/100) ** 10:.2f}")

# --- Disclaimer ---
st.markdown("---")
st.markdown("### Disclaimer")
st.info("This tool is for educational purposes only and does not constitute financial advice. Please consult a licensed financial advisor before making investment decisions.")
