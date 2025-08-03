# ----------------------------
# AGILE MONTE CARLO SIMULATOR v3
# Daily Rates, Risk Drivers, Managed Services, Clear Explanations
# ----------------------------

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide", page_title="Agile Monte Carlo Simulator")

# ----------------------------
# Sidebar Inputs
# ----------------------------
st.sidebar.title("Project Configuration")

st.sidebar.subheader("Team & Daily Rates (USD)")
rate_dev = st.sidebar.number_input("Developer Rate ($/day)", value=400, step=50)
rate_qa = st.sidebar.number_input("QA Tester Rate ($/day)", value=350, step=50)
rate_pm = st.sidebar.number_input("PM Rate ($/day)", value=500, step=50)

num_dev = st.sidebar.slider("Number of Developers", 1, 4, 2)
num_qa = st.sidebar.slider("Number of QA Testers", 1, 4, 2)
num_pm = st.sidebar.slider("Number of PMs", 0, 2, 1)

st.sidebar.subheader("Project Scope (Story Points)")
base_scope = st.sidebar.number_input(
    "Expected Scope (SP)",
    value=500,
    step=50,
    help="Total effort in story points. Assuming 20 SP per sprint (2-week cycle), "
         "so 500 SP ≈ 25 sprints ≈ 12.5 months at 20 SP/sprint."
)

# Calculate estimated sprints and duration
estimated_sprints = base_scope / 20
estimated_months = estimated_sprints * 0.5
st.sidebar.info(f"Based on 20 SP per sprint: ~{estimated_sprints:.1f} sprints (~{estimated_months:.1f} months)")

# Risk Drivers (0% = stable, 100% = chaotic)
st.sidebar.subheader("Risk Levels (%)")
risk_scope = st.sidebar.slider(
    "Risk: Uncertain Scope",
    0, 100, 30,
    help="Higher % = greater initial uncertainty in requirements"
) / 100

risk_velocity = st.sidebar.slider(
    "Risk: Variable Team Speed",
    0, 100, 25,
    help="Higher % = more variation in sprint velocity (due to blockers, onboarding, etc.)"
) / 100

risk_bugs = st.sidebar.slider(
    "Risk: Hidden Bugs (Rework)",
    0, 100, 35,
    help="Higher % = more defects, technical debt, and rework effort"
) / 100

risk_changes = st.sidebar.slider(
    "Risk: Changing Priorities",
    0, 100, 20,
    help="Higher % = more mid-project scope changes or new feature requests"
) / 100

# Cloud toggle
st.sidebar.subheader("Infrastructure")
use_cloud = st.sidebar.checkbox("Include Cloud IaaS/PaaS?", value=True)
if use_cloud:
    cloud_min = st.sidebar.number_input("Cloud Min ($/month)", 500, value=1000)
    cloud_max = st.sidebar.number_input("Cloud Max ($/month)", 1000, value=5000)
else:
    cloud_min = cloud_max = 0

# Managed Service (Ongoing Support)
st.sidebar.subheader("Managed Service (Optional)")
include_managed_service = st.sidebar.checkbox(
    "Include Annual Managed Service Cost?",
    value=True,
    help="Ongoing support, monitoring, minor updates, and DevOps"
)
if include_managed_service:
    managed_service_pct = st.sidebar.slider(
        "Managed Service as % of One-Off Project Cost",
        5, 50, 15,
        help="e.g., 15% of TCO charged annually for support and maintenance"
    ) / 100
else:
    managed_service_pct = 0

n_simulations = st.sidebar.slider("Number of Simulations", 1_000, 10_000, 5_000, step=1_000)

# Constants
DAYS_PER_SPRINT = 10  # 2 weeks
WORK_DAYS_PER_MONTH = 20
BASE_VELOCITY = 20  # SP per sprint

# ----------------------------
# Run Simulation
# ----------------------------
if st.sidebar.button("Run Monte Carlo Simulation"):
    with st.spinner("Running simulation..."):

        np.random.seed(42)
        results = []

        for i in range(n_simulations):
            # --- 1. Final Scope: base + uncertainty + mid-project changes ---
            scope_volatility = np.random.normal(0, risk_scope)
            scope_change = np.random.beta(2, 5) * risk_changes  # feature creep
            final_scope = base_scope * (1 + scope_volatility + scope_change)
            final_scope = max(100, final_scope)

            # --- 2. Velocity with variability ---
            vel_std = BASE_VELOCITY * risk_velocity
            velocity = max(5, np.random.normal(BASE_VELOCITY, vel_std))

            # --- 3. Duration ---
            sprints = final_scope / velocity
            total_days = sprints * DAYS_PER_SPRINT
            duration_months = total_days / WORK_DAYS_PER_MONTH

            # --- 4. Labor Cost (from daily rates) ---
            labor_dev = num_dev * rate_dev * total_days
            labor_qa = num_qa * rate_qa * total_days
            labor_pm = num_pm * rate_pm * total_days
            labor_cost = labor_dev + labor_qa + labor_pm

            # --- 5. Rework Cost ---
            rework_factor = np.random.beta(3, 8) + np.random.exponential(risk_bugs)
            rework_factor = min(rework_factor, 1.0)
            rework_cost = rework_factor * labor_cost

            # --- 6. Cloud Cost ---
            monthly_cloud = np.random.uniform(cloud_min, cloud_max)
            cloud_cost = monthly_cloud * duration_months

            # --- 7. One-Off TCO (Initial Project Cost) ---
            tco_one_off = labor_cost + rework_cost + cloud_cost

            # --- 8. Managed Service (Annual Ongoing Cost) ---
            managed_service_annual = managed_service_pct * tco_one_off if include_managed_service else 0

            # --- 9. Total Cost of Ownership (Over Project Duration) ---
            tco_total = tco_one_off + (managed_service_annual * duration_months / 12)

            # --- 10. Revenue & Profit (Auto with 20% target markup on one-off) ---
            target_markup = 1.20
            revenue_one_off = tco_one_off * target_markup
            profit = revenue_one_off - tco_total
            profit_margin = (profit / revenue_one_off) * 100 if revenue_one_off > 0 else 0

            # --- 11. Store Results ---
            results.append({
                'Scope_SP': final_scope,
                'Velocity_SP': velocity,
                'Sprints': sprints,
                'Duration_Days': total_days,
                'Duration_Months': duration_months,
                'Labor_Cost': labor_cost,
                'Rework_Cost': rework_cost,
                'Cloud_Cost': cloud_cost,
                'Managed_Service_Annual': managed_service_annual,
                'TCO_OneOff': tco_one_off,
                'TCO_Total': tco_total,
                'Revenue': revenue_one_off,
                'Profit': profit,
                'Profit_Margin_%': profit_margin,
                'Risk_Scope': risk_scope,
                'Risk_Velocity': risk_velocity,
                'Risk_Bugs': risk_bugs,
                'Risk_Changes': risk_changes
            })

        df = pd.DataFrame(results)
        st.session_state['df'] = df

# ----------------------------
# Display Results
# ----------------------------
if 'df' in st.session_state:
    df = st.session_state['df']

    st.title("Agile Monte Carlo Simulator")
    st.subheader("Daily Rates • Risk-Driven • Managed Services • Transparent Scope")

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Median Scope", f"{df['Scope_SP'].median():.0f} SP")
    col2.metric("Median Duration", f"{df['Duration_Months'].median():.1f} mo")
    col3.metric("Median TCO (Total)", f"${df['TCO_Total'].median():,.0f}")
    col4.metric("Profit Margin", f"{df['Profit_Margin_%'].median():.1f}%")

    st.markdown("---")

    # Charts
    fig, ax = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Monte Carlo Simulation Results", fontsize=16, fontweight='bold')

    sns.histplot(df['TCO_Total'], bins=50, kde=True, ax=ax[0,0], color='skyblue')
    ax[0,0].axvline(df['TCO_Total'].median(), color='red', linestyle='--', label="Median")
    ax[0,0].legend()
    ax[0,0].set_title("Total Cost of Ownership (One-Off + Managed Service)")
    ax[0,0].set_xlabel("Cost ($)")

    sns.histplot(df['Profit'], bins=50, kde=True, ax=ax[0,1], color='lightgreen')
    ax[0,1].axvline(df['Profit'].median(), color='red', linestyle='--')
    ax[0,1].axvline(0, color='black', linewidth=1)
    ax[0,1].set_title("Profit Distribution")
    ax[0,1].set_xlabel("Profit ($)")

    sns.histplot(df['Duration_Months'], bins=50, kde=True, ax=ax[1,0], color='gold')
    ax[1,0].axvline(df['Duration_Months'].median(), color='red', linestyle='--')
    ax[1,0].set_title("Project Duration (Months)")
    ax[1,0].set_xlabel("Months")

    sns.histplot(df['Profit_Margin_%'], bins=50, kde=True, ax=ax[1,1], color='plum')
    ax[1,1].axvline(df['Profit_Margin_%'].median(), color='red', linestyle='--')
    ax[1,1].set_title("Profit Margin (%)")
    ax[1,1].set_xlabel("Margin (%)")

    plt.tight_layout()
    st.pyplot(fig)

    # Risk Summary
    st.markdown("### Risk & Confidence")
    col1, col2, col3 = st.columns(3)
    col1.write(f"✅ **P80 TCO (Total):** ${df['TCO_Total'].quantile(0.8):,.0f}")
    col2.write(f"📉 **Chance of Profit:** {(df['Profit'] > 0).mean() * 100:.1f}%")
    col3.write(f"⏱️ **P90 Duration:** {df['Duration_Months'].quantile(0.9):.1f} months")

    # Sensitivity
    st.markdown("### Sensitivity: Top Cost Drivers")
    corr = df.corr()['TCO_Total'].sort_values(key=abs, ascending=False)
    high_corr = corr[abs(corr) > 0.1]
    st.bar_chart(high_corr)

    top_risks = [k.replace('Risk_', '').replace('_', ' ') for k in ['Risk_Bugs', 'Risk_Scope', 'Risk_Velocity', 'Risk_Changes']
                 if abs(df.corr()['TCO_Total'][k]) > 0.2]
    if top_risks:
        st.write(f"⚠️ Highest impact risks: **{', '.join([r.title() for r in top_risks])}**")

    # Export
    st.markdown("### Export Results")
    csv = df[[
        'Duration_Months', 'TCO_OneOff', 'Managed_Service_Annual', 'TCO_Total',
        'Profit', 'Profit_Margin_%', 'Scope_SP', 'Sprints'
    ]].round(2).to_csv(index=False)
    st.download_button(
        "Download Results (CSV)",
        csv,
        "agile_monte_carlo_v3.csv",
        "text/csv"
    )

else:
    st.title("Agile Monte Carlo Simulator")
    st.info("Configure your project in the sidebar and click 'Run Simulation' to begin.")
