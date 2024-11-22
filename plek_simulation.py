import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calendar

# Set page configuration
st.set_page_config(
    page_title="Plek Machine Revenue Simulation",
    layout="wide"  # Expand the layout to use the full width of the screen
)

# Title and description
st.title("Plek Machine Revenue Simulation")
st.markdown("An interactive simulation to estimate revenue for your Plek machine business.")

# Input Sliders
st.sidebar.header("Simulation Parameters")
max_guitars = st.sidebar.slider("Max Guitars per Week", 1, 20, 9)
ramp_up_months = st.sidebar.slider("Ramp-Up Period (Months)", 12, 60, 42)
price_per_guitar = st.sidebar.slider("Price per Guitar ($)", 100, 500, 175)
variability = st.sidebar.slider("Variability (%)", 0, 100, 75)
timeframe_years = st.sidebar.slider("Simulation Timeframe (Years)", 1, 10, 5)

# Simulation Logic
weeks = timeframe_years * 52
ramp_up_weeks = ramp_up_months * 4
gradual_ramp_up = np.linspace(0, max_guitars, ramp_up_weeks).round().astype(int)
steady_state = [max_guitars] * (weeks - ramp_up_weeks)
guitars_per_week = list(gradual_ramp_up) + steady_state

# Introduce variability
randomized_guitars_per_week = [
    max(0, min(max_guitars, int(g * np.random.uniform(1 - variability / 100, 1 + variability / 100))))
    for g in guitars_per_week
]

# Calculate weekly and cumulative revenue
weekly_revenue = [g * price_per_guitar for g in randomized_guitars_per_week]
cumulative_revenue = np.cumsum(weekly_revenue)

# Create DataFrame for Visualization
data = {
    "Week": list(range(1, weeks + 1)),
    "Guitars per Week": randomized_guitars_per_week,
    "Weekly Revenue ($)": weekly_revenue,
    "Cumulative Revenue ($)": cumulative_revenue,
}
df = pd.DataFrame(data)

# Generate month-year labels starting from March 2025
start_year = 2025
start_month = 3
month_labels = [
    f"{calendar.month_abbr[(start_month + i - 1) % 12 + 1]} {start_year + (start_month + i - 1) // 12}"
    for i in range((weeks // 4) + 1)
]

# Adjust the DataFrame to include month labels
df["Month"] = pd.cut(df["Week"], bins=np.arange(0, weeks + 4, 4), labels=month_labels[:-1], right=False)

# Group data by month for better visualization
monthly_data = df.groupby("Month").agg({
    "Weekly Revenue ($)": "sum",
    "Cumulative Revenue ($)": "max"
}).reset_index()

# Display Results
st.write("### Weekly Revenue Table")
st.dataframe(df)

# Plot Revenue Chart
st.write("### Revenue Over Time (Monthly)")
fig, ax = plt.subplots(figsize=(16, 8))  # Set the chart width and height
ax.plot(monthly_data["Month"], monthly_data["Cumulative Revenue ($)"], label="Cumulative Revenue", marker='o')
ax.bar(monthly_data["Month"], monthly_data["Weekly Revenue ($)"], alpha=0.5, label="Monthly Revenue")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue ($)")
ax.set_xticklabels(monthly_data["Month"], rotation=90, ha="right")
ax.legend()
st.pyplot(fig)

# Summary Metrics
total_revenue = cumulative_revenue[-1]
avg_weekly_revenue = np.mean(weekly_revenue)
st.write("### Summary")
st.metric("Total Revenue ($)", f"${total_revenue:,.2f}")
st.metric("Average Weekly Revenue ($)", f"${avg_weekly_revenue:,.2f}")
