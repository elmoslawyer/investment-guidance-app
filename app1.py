1. Investment Growth Visualization
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.subheader("Investment Growth Over Time")

initial_investment = st.number_input("Initial Investment ($)", 100, 100000, 1000, step=100)
years = st.slider("Investment Duration (Years)", 1, 40, 10)
expected_return = st.slider("Expected Annual Return (%)", 1.0, 15.0, 7.0)

# Calculate future value
years_array = np.arange(1, years + 1)
values = initial_investment * (1 + expected_return / 100) ** years_array

# Plot
fig, ax = plt.subplots()
ax.plot(years_array, values, marker="o")
ax.set_title("Projected Investment Growth")
ax.set_xlabel("Years")
ax.set_ylabel("Value ($)")
st.pyplot(fig)
2. Budgeting / Net Worth Calculator
st.subheader("Budget & Net Worth Calculator")

income = st.number_input("Monthly Income ($)", 0, 10000, 3000, step=100)
expenses = st.number_input("Monthly Expenses ($)", 0, 10000, 2000, step=100)
student_loans = st.number_input("Student Loan Balance ($)", 0, 100000, 20000, step=500)

monthly_savings = income - expenses
annual_savings = monthly_savings * 12

net_worth = annual_savings * 5 - student_loans  # 5-year projection

st.write(f"**Estimated Annual Savings:** ${annual_savings}")
st.write(f"**Estimated Net Worth in 5 Years (excluding investment returns):** ${net_worth}")
3. Add More Asset Classes
st.subheader("Explore Investment Options")

risk_profile = st.selectbox("Your Risk Profile", ["Conservative", "Moderate", "Aggressive"])

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
4. Tooltip / Explanation for Terms
with st.expander("What is an ETF?"):
    st.write("An Exchange Traded Fund (ETF) is a type of investment fund that is traded on stock exchanges, much like stocks.")

with st.expander("What is Diversification?"):
    st.write("Diversification is an investment strategy that spreads your investments across various asset classes to reduce risk.")
5. Scenario Planner: Market Return Simulations
st.subheader("Market Scenario Planner")

bear = st.slider("Bear Market Avg Return (%)", -20.0, 0.0, -5.0)
neutral = st.slider("Neutral Market Avg Return (%)", 0.0, 10.0, 5.0)
bull = st.slider("Bull Market Avg Return (%)", 5.0, 20.0, 12.0)

investment = st.number_input("Investment Amount ($)", 1000, 100000, 5000, step=500)

st.write(f"**Bear Market Future Value (10 years):** ${investment * (1 + bear/100) ** 10:.2f}")
st.write(f"**Neutral Market Future Value (10 years):** ${investment * (1 + neutral/100) ** 10:.2f}")
st.write(f"**Bull Market Future Value (10 years):** ${investment * (1 + bull/100) ** 10:.2f}")
6. Disclaimer Section
st.markdown("---")
st.markdown("### Disclaimer")
st.info("This tool is for educational purposes only and does not constitute financial advice. Please consult a licensed financial advisor before making investment decisions.")
