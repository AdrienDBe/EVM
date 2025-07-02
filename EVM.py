import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import random

st.set_page_config(page_title="EVM – Biomedical Support Dashboard", layout="centered")
st.markdown("""
    <style>
        button[title="View fullscreen"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
        /* Hide link icon on headers */
        section [data-testid="stMarkdownContainer"] a[href^="#"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)
# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style/style.css")

hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Use CSS for background
with open('./style/wave.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


st.title("Earned Value Management (EVM): Concept and Industry Applications")

st.header("Project Context")
st.write("""
This dashboard illustrates the financial monitoring using Earned Value Management (EVM), a widely adopted project control technique in various industries.

As an example, we apply EVM to a **Biomedical Technical Assistance Program** that supports molecular diagnostic systems deployed in public health laboratories.
The program includes technician training, module replacement, remote support, and preventive maintenance. Ensuring budget discipline and operational efficiency is key to delivering impact while meeting donor compliance standards.
""")

# Scenario selection
scenario = st.radio("Select a project scenario:", ["Positive", "Neutral", "Negative"])

st.header("Monitoring Objectives")
st.write("""
This dashboard covers essential aspects of project financial and schedule performance, including:

- **Cost and schedule performance tracking** through Earned Value Management (EVM).
- Accurate **Actual vs. Budget comparisons** using baseline budgets.
- **Forecasting of cost at completion (EAC)** to anticipate funding needs.
- Clear variance analysis to support **strategic reporting for senior leadership**.
""")


# Simulate monthly PV first (stable baseline)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
pv_series = [round(400 * (i + 1) + random.uniform(-50, 50)) for i in range(len(months))]

# Simulate EV and AC based on scenario
ev_series, ac_series = [], []
for i, pv in enumerate(pv_series):
    if scenario == "Positive":
        ev = pv + random.uniform(20, 80)
        ac = ev - random.uniform(10, 60)
    elif scenario == "Negative":
        ev = pv - random.uniform(30, 100)
        ac = ev + random.uniform(40, 90)
    else:
        ev = pv + random.uniform(-40, 40)
        ac = ev + random.uniform(-30, 30)
    ev_series.append(max(0, round(ev)))
    ac_series.append(max(0, round(ac)))

# Use last month synthetic values for key calculations
PV = pv_series[-1]
EV = ev_series[-1]
AC = ac_series[-1]
BAC = 2500  # Fixed budget at completion for example

# Calculate performance metrics from synthetic data
CPI = EV / AC if AC else 0
SPI = EV / PV if PV else 0
CV = EV - AC
SV = EV - PV
ETC = (BAC - EV) / CPI if CPI else 0
EAC = AC + ETC

# Performance Indicators
st.header("Performance Indicators")
col1, col2 = st.columns(2)
with col1:
    st.metric("💰 Cost Performance Index (CPI)", f"{CPI:.2f}", delta=f"{CV:.0f} k€")
    st.metric("🔮 Estimate to Complete (ETC)", f"{ETC:.0f} k€")
with col2:
    st.metric("⏱ Schedule Performance Index (SPI)", f"{SPI:.2f}", delta=f"{SV:.0f} k€")
    st.metric("📊 Estimate at Completion (EAC)", f"{EAC:.0f} k€")


st.info("""
- **Cost Performance Index (CPI)**: Measures cost efficiency of the work performed. A CPI below 1 indicates cost overruns.
- **Estimate to Complete (ETC)**: Forecast of the remaining cost needed to complete the project based on current performance.
- **Schedule Performance Index (SPI)**: Measures schedule efficiency. An SPI below 1 means the project is behind schedule.
- **Estimate at Completion (EAC)**: Projected total cost of the project at completion, factoring in current trends.
""")


# Financial Status Messages
st.header("Financial Status Analysis")
col1, col2 = st.columns(2)
with col1:
    if CPI >= 1:
        st.success("✅ The project is currently under budget.")
    else:
        st.error("⚠️ The project is over budget.")
with col2:
    if SPI >= 1:
        st.success("📈 The project is ahead of schedule.")
    else:
        st.warning("📉 The project is behind schedule.")

# Financial Breakdown Chart
st.header("Financial Status & Remaining Work Overview")
cost_elements = {
    "Earned Value (Work Done)": EV,
    "Actual Cost (Spent)": AC,
    "Remaining Work (Planned – EV)": max(PV - EV, 0),
    "Remaining Budget (BAC – AC)": max(BAC - AC, 0)
}
df_combined = pd.DataFrame.from_dict(cost_elements, orient='index', columns=['k€'])
fig_combined, ax_combined = plt.subplots(figsize=(10, 5))
bars_combined = ax_combined.barh(df_combined.index, df_combined['k€'], 
                                  color=["#2ca02c", "#d62728", "#1f77b4", "#c7c7c7"])

ax_combined.axvline(BAC, color='purple', linestyle='--', linewidth=1.5, label=f'BAC ({BAC:.0f} k€)')
eac_color = 'red' if EAC > BAC else 'orange'
ax_combined.axvline(EAC, color=eac_color, linestyle='--', linewidth=1.5, label=f'EAC ({EAC:.0f} k€)')

for bar in bars_combined:
    width = bar.get_width()
    ax_combined.annotate(f'{width:.0f} k€',
                         xy=(width, bar.get_y() + bar.get_height() / 2),
                         xytext=(5, 0),
                         textcoords='offset points',
                         ha='left', va='center', fontsize=9, fontweight='bold')

ax_combined.set_xlabel("Amount (k€)")
ax_combined.set_title("🔍 Project Execution & Budget Forecast")
ax_combined.invert_yaxis()
ax_combined.legend()
st.pyplot(fig_combined)

st.info("""
This chart consolidates:  
- **Earned Value**: Progress made.  
- **Actual Cost**: What has been spent.  
- **Remaining Planned Work**: Work still to be completed.  
- **Remaining Budget**: Budget available to complete the work.  
- **BAC / EAC Lines**: Show original and projected total costs.  

⚠️ If **EAC exceeds BAC**, the red line signals a budget overrun risk.
""")


# EVM Trends Plot with scenario data
st.header("Simulated EVM Trends Over Time")

df_evm = pd.DataFrame({
    "Month": months,
    "Planned Value (PV)": pv_series,
    "Earned Value (EV)": ev_series,
    "Actual Cost (AC)": ac_series
})

fig_evm, ax_evm = plt.subplots(figsize=(10, 5))
ax_evm.plot(df_evm["Month"], df_evm["Planned Value (PV)"], marker='o', label="PV", color="#1f77b4")
ax_evm.plot(df_evm["Month"], df_evm["Earned Value (EV)"], marker='o', label="EV", color="#2ca02c")
ax_evm.plot(df_evm["Month"], df_evm["Actual Cost (AC)"], marker='o', label="AC", color="#d62728")

for i in range(len(months)):
    x = df_evm["Month"][i]
    if df_evm["Earned Value (EV)"][i] < df_evm["Planned Value (PV)"][i]:
        ax_evm.plot(x, df_evm["Earned Value (EV)"][i], 'ro', markersize=10, markeredgecolor='black')
        ax_evm.annotate("Behind Schedule", xy=(x, df_evm["Earned Value (EV)"][i]),
                        xytext=(0, -30), textcoords="offset points",
                        ha='center', fontsize=8, color='red', fontweight='bold')
    if df_evm["Actual Cost (AC)"][i] > df_evm["Earned Value (EV)"][i]:
        ax_evm.plot(x, df_evm["Actual Cost (AC)"][i], 'ro', markersize=10, markeredgecolor='black')
        ax_evm.annotate("Over Budget", xy=(x, df_evm["Actual Cost (AC)"][i]),
                        xytext=(0, 15), textcoords="offset points",
                        ha='center', fontsize=8, color='red', fontweight='bold')

ax_evm.set_ylabel("Amount (k€)")
ax_evm.set_title(f"EVM Trends – {scenario} Scenario")
ax_evm.legend()
ax_evm.grid(True)
st.pyplot(fig_evm)

st.info("""
What we can learn from this plot:  
- Visualize how planned value (PV), earned value (EV), and actual cost (AC) evolve over time.  
- Identify periods where the project is ahead or behind schedule and under or over budget.  
- Spot trends early to enable proactive management decisions and timely corrective actions.  
- Understand the overall project health to support strategic reporting and forecasting.
""")

# Variance Bar Chart (Key Indicators Overview)
st.header("Key Indicators Overview")
trend_labels = ["Cost Variance (CV)", "Schedule Variance (SV)", "ETC", "EAC"]
trend_values = [CV, SV, ETC, EAC]
colors_trend = ['#ff9896' if v < 0 else '#98df8a' for v in trend_values]

fig_trend, ax_trend = plt.subplots(figsize=(8, 4))
bars_trend = ax_trend.bar(trend_labels, trend_values, color=colors_trend)
ax_trend.axhline(0, color='gray', linewidth=0.8)
ax_trend.set_ylabel("Amount (k€)")
ax_trend.set_title("Variance & Forecast Summary")

for bar in bars_trend:
    height = bar.get_height()
    ax_trend.annotate(f'{height:.0f} k€',
                      xy=(bar.get_x() + bar.get_width() / 2, height),
                      xytext=(0, 4 if height >= 0 else -12),
                      textcoords="offset points",
                      ha='center', va='bottom' if height >= 0 else 'top',
                      fontsize=9, fontweight='bold')

st.pyplot(fig_trend)

st.write("- **Cost Variance (CV)**: Difference between planned and actual spending.")
st.info("""
A positive CV means you spent less than planned (good). A negative CV means overspending.  
**Mitigation Strategies:** Review spending categories, identify cost-saving opportunities, renegotiate supplier contracts, and reinforce budget controls.
""")

st.write("- **Schedule Variance (SV)**: Difference between planned work and work done.")
st.info("""
A positive SV means you're ahead of schedule. A negative SV means you're behind.  
**Mitigation Strategies:** Assess resource allocation, adjust timelines, increase team coordination, and prioritize critical tasks to recover delays.
""")

st.write("- **Estimate to Complete (ETC)**: Forecast of remaining costs based on current trends.")
st.info("""
Helps anticipate how much additional funding may be needed.  
**Mitigation Strategies:** Update forecasts regularly, secure contingency funds, optimize resource usage, and review project scope to control costs.
""")

st.write("- **Estimate at Completion (EAC)**: Total projected project cost compared to the original budget.")
st.info("""
Compare this to the original Budget at Completion (BAC) to identify any major budget overruns.  
**Mitigation Strategies:** Communicate risks to stakeholders, implement corrective measures, adjust project plans, and explore alternative funding options.
""")





# Future Ideas
st.header("To Go Further – Toward Real-Time Automation")
st.write("This prototype can evolve into a fully automated dashboard by integrating with the organization’s data ecosystem:")

# Define the size for the images
image_size = 150

col1, col2 = st.columns([1, 3])

# ERP or Salesforce
st.subheader("ERP or Salesforce Integration")
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Salesforce.com_logo.svg/640px-Salesforce.com_logo.svg.png", width=image_size)
with col2:
    st.write("Automatically sync budget, expenditure, and activity data to eliminate manual updates.")

# Python / Power BI
st.subheader("Python or Power BI Pipelines")
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/New_Power_BI_Logo.svg/1024px-New_Power_BI_Logo.svg.png", width=100)
with col2:
    st.write("Schedule scripts to run nightly, processing incoming data and refreshing visuals.")

# Decision Support
st.subheader("Management Decision Support")
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://doc.arcgis.com/fr/dashboards/latest/get-started/GUID-3D4DA083-56DD-4688-970E-801B54DDD32C-web.png", width=image_size)
with col2:
    st.write("Publish key indicators in real time to executive dashboards used by donors, senior leadership, and program managers.")

# Threshold Alerts
st.subheader("Threshold Alerts")
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://img.uxcel.com/tags/notifications-1700498330224-2x.jpg", width=image_size)
with col2:
    st.write("Automatically notify users when the project is overspending or delayed, with suggested corrective actions.")

