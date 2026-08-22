"""
Page 3: Department Performance, Turnaround Analysis & Officer Scorecards.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.utils import load_data, apply_custom_css, get_filtered_data, render_ai_copilot_sidebar
from src.analytics.kpis import CivicKPIEngine

st.set_page_config(page_title="Department Deep Dive - Civic Analytics", page_icon="🏢", layout="wide")
apply_custom_css()

st.title("🏢 Departmental Efficiency & Officer Performance Scorecards")
st.markdown("Granular investigation into operational bottlenecks, resolution turnaround distributions, and officer workload.")

raw_df = load_data()
df = get_filtered_data(raw_df)

# Render AI Copilot in Sidebar
render_ai_copilot_sidebar("Department Deep Dive")

kpi_engine = CivicKPIEngine(df)
dept_scorecard = kpi_engine.get_department_scorecard()
officer_perf = kpi_engine.get_officer_performance()

# Department Leaderboard Table
st.subheader("📋 Departmental Performance Matrix")
st.dataframe(
    dept_scorecard.style.background_gradient(subset=["Resolution_Rate_Pct", "Avg_Citizen_Rating"], cmap="Blues")
    .background_gradient(subset=["SLA_Breach_Rate_Pct", "Avg_Resolution_Days"], cmap="Reds"),
    use_container_width=True,
)

st.markdown("---")

# Visualizations: Turnaround Time Distribution & Officer Efficiency
col1, col2 = st.columns(2)

with col1:
    st.subheader("⏱️ Turnaround Time Distribution (Days)")
    resolved_df = df[df["Resolution_Time_Days"].notna()]
    
    if not resolved_df.empty:
        fig_box = px.box(
            resolved_df,
            x="Department",
            y="Resolution_Time_Days",
            color="Department",
            points="all",
            labels={"Resolution_Time_Days": "Resolution Days"},
        )
        fig_box.add_hline(y=3, line_dash="dash", line_color="red", annotation_text="SLA Limit (3 Days)")
        fig_box.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("No resolved complaints in selected filter.")

with col2:
    st.subheader("👮 Assigned Officer Workload vs Rating")
    if not officer_perf.empty:
        fig_officer = px.scatter(
            officer_perf,
            x="Assigned_Tickets",
            y="Avg_Rating",
            size="Resolved_Tickets",
            color="Department",
            hover_name="Assigned_Officer",
            text="Assigned_Officer",
            labels={"Assigned_Tickets": "Total Tickets Assigned", "Avg_Rating": "Avg Citizen Rating (1-5)"},
        )
        fig_officer.update_traces(textposition="top center")
        fig_officer.update_layout(height=400)
        st.plotly_chart(fig_officer, use_container_width=True)
    else:
        st.info("No officer records available.")

st.markdown("---")

# Officer Performance Leaderboard
st.subheader("🎖️ Officer Operational Scorecard")
st.dataframe(officer_perf, use_container_width=True)
