"""
Page 1: Executive Overview & Macro Civic KPIs.
"""

import sys
from pathlib import Path

# Add project root and dashboard directory to sys.path dynamically for Streamlit Cloud
FILE_DIR = Path(__file__).resolve().parent
ROOT_DIR = FILE_DIR.parent.parent
for p in [ROOT_DIR, FILE_DIR.parent, FILE_DIR]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from dashboard.utils import load_data, apply_custom_css, render_kpi_card, get_filtered_data, render_ai_copilot_sidebar
except ImportError:
    from utils import load_data, apply_custom_css, render_kpi_card, get_filtered_data, render_ai_copilot_sidebar

from src.analytics.kpis import CivicKPIEngine
from src.analytics.time_series import CivicTimeSeriesAnalyzer

st.set_page_config(page_title="Executive Overview - Civic Analytics", page_icon="📊", layout="wide")
apply_custom_css()

st.title("📊 Executive Overview & Strategic Command Center")
st.markdown("Macro-level visibility into civic complaint resolution velocity, SLA adherence, and district health.")

raw_df = load_data()
df = get_filtered_data(raw_df)

# Render AI Copilot in Sidebar
render_ai_copilot_sidebar("Executive Overview")

kpi_engine = CivicKPIEngine(df)
summary = kpi_engine.get_executive_summary()

# Scorecards
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_kpi_card("Total Volume", f"{summary['total_complaints']:,}", "Filtered Selection")
with c2:
    render_kpi_card("Resolved Tickets", f"{summary['resolved_complaints']:,}", f"{summary['resolution_rate_pct']}% Solved")
with c3:
    render_kpi_card("SLA Compliance", f"{summary['sla_compliance_rate_pct']}%", "Threshold: <= 3 Days")
with c4:
    render_kpi_card("Avg Resolution", f"{summary['avg_turnaround_days']} Days", "Target: < 3.0 Days")
with c5:
    render_kpi_card("Citizen Rating", f"⭐ {summary['avg_citizen_rating']}", "Satisfaction Index")

st.markdown("---")

# Charts Row 1: Time Series Trend & SLA Distribution
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📈 Daily Complaint Volume & 7-Day Moving Average")
    ts_analyzer = CivicTimeSeriesAnalyzer(df)
    daily_trend = ts_analyzer.get_daily_trend()
    
    if not daily_trend.empty:
        fig_trend = px.line(
            daily_trend,
            x="Complaint_Date",
            y=["Daily_Complaints", "7_Day_Moving_Avg"],
            labels={"value": "Complaint Count", "Complaint_Date": "Date", "variable": "Metric"},
            color_discrete_map={"Daily_Complaints": "#94a3b8", "7_Day_Moving_Avg": "#38bdf8"},
        )
        fig_trend.update_layout(legend=dict(orientation="h", y=1.1), height=380)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No data available for current filter.")

with col2:
    st.subheader("🎯 SLA Status Breakdown")
    sla_counts = df["SLA_Status"].value_counts().reset_index()
    sla_counts.columns = ["Status", "Count"]
    fig_sla = px.pie(
        sla_counts,
        names="Status",
        values="Count",
        hole=0.5,
        color="Status",
        color_discrete_map={
            "Within SLA": "#10b981",
            "SLA Breached": "#ef4444",
            "Pending": "#f59e0b",
        },
    )
    fig_sla.update_layout(height=380)
    st.plotly_chart(fig_sla, use_container_width=True)

st.markdown("---")

# Charts Row 2: District Comparison & Issue Distribution
col3, col4 = st.columns(2)

with col3:
    st.subheader("🏙️ Complaints by District")
    district_df = df.groupby(["District", "Priority"]).size().reset_index(name="Count")
    fig_dist = px.bar(
        district_df,
        x="District",
        y="Count",
        color="Priority",
        barmode="stack",
        color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"},
    )
    fig_dist.update_layout(height=380)
    st.plotly_chart(fig_dist, use_container_width=True)

with col4:
    st.subheader("📋 Top Civic Issue Categories")
    issue_counts = df["Issue_Type"].value_counts().head(8).reset_index()
    issue_counts.columns = ["Issue_Type", "Complaints"]
    fig_issues = px.bar(
        issue_counts,
        x="Complaints",
        y="Issue_Type",
        orientation="h",
        color="Complaints",
        color_continuous_scale="Viridis",
        text="Complaints",
    )
    fig_issues.update_layout(height=380, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_issues, use_container_width=True)
