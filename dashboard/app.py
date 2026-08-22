"""
Smart Civic Issue Analytics - Web Application Entrypoint.
A modern, production-grade analytical platform and predictive civic intelligence system.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.utils import load_data, apply_custom_css, render_kpi_card, render_ai_copilot_sidebar
from src.analytics.kpis import CivicKPIEngine

st.set_page_config(
    page_title="Smart Civic Issue Analytics",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()

# Header
st.title("🏛️ Smart Civic Issue Analytics & Predictive Dispatcher")
st.caption("Enterprise-Grade Civic Intelligence, Machine Learning & Citizen Resolution Platform")

df = load_data()
kpi_engine = CivicKPIEngine(df)
summary = kpi_engine.get_executive_summary()

# Render AI Copilot in Sidebar
render_ai_copilot_sidebar("Executive Overview")

# Top KPI Metric Cards
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_kpi_card("Total Complaints", f"{summary['total_complaints']:,}", "Logged Civic Incidents")
with col2:
    render_kpi_card("Resolution Rate", f"{summary['resolution_rate_pct']}%", f"{summary['resolved_complaints']} Resolved")
with col3:
    render_kpi_card("SLA Compliance", f"{summary['sla_compliance_rate_pct']}%", "Standard: <= 3 Days")
with col4:
    render_kpi_card("Avg Turnaround", f"{summary['avg_turnaround_days']} Days", f"Median: {summary['median_turnaround_days']} Days")
with col5:
    render_kpi_card("Citizen Rating", f"⭐ {summary['avg_citizen_rating']}", "Scale: 1.0 to 5.0")

st.markdown("---")

# Quick Overview & Navigation Cards
st.subheader("🎯 Project Navigation & Capabilities")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    #### 📊 1. Executive Analytics
    - High-level KPI scorecards & SLA breach metrics
    - Departmental workload distributions
    - Monthly & weekly trend velocities
    """)
    st.info("Navigate via the sidebar: **1_Executive_Overview**")

with c2:
    st.markdown("""
    #### 🗺️ 2. Geospatial GIS Explorer
    - Interactive OpenStreetMap & Heatmaps
    - Machine Learning DBSCAN Hotspot Detection
    - Ward-level risk and incident concentration
    """)
    st.info("Navigate via the sidebar: **2_Geospatial_Explorer**")

with c3:
    st.markdown("""
    #### 🤖 3. AI Predictive Studio & Copilot
    - Real-time SLA Breach Risk Probability
    - Turnaround Duration Estimator
    - Interactive AI Explainer & Assistant on every page!
    """)
    st.info("Navigate via the sidebar: **4_AI_Predictive_Studio**")

st.markdown("---")

# Visual Previews
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("##### 📌 Departmental Complaint Volume")
    dept_counts = df["Department"].value_counts().reset_index()
    dept_counts.columns = ["Department", "Count"]
    fig_dept = px.bar(
        dept_counts,
        x="Count",
        y="Department",
        orientation="h",
        color="Count",
        color_continuous_scale="Blues",
        text="Count",
    )
    fig_dept.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_dept, use_container_width=True)

with col_right:
    st.markdown("##### ⚖️ Priority vs Resolution Status")
    priority_status = pd.crosstab(df["Priority"], df["Status"]).reset_index()
    fig_ps = px.bar(
        priority_status,
        x="Priority",
        y=["Resolved", "In Progress", "Open"],
        barmode="group",
        color_discrete_map={"Resolved": "#10b981", "In Progress": "#f59e0b", "Open": "#ef4444"},
    )
    fig_ps.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_ps, use_container_width=True)

# Architecture Summary
with st.expander("🛠️ System Architecture & Technology Stack", expanded=False):
    st.markdown("""
    - **Data Pipeline:** Python, Pandas, NumPy, SQLAlchemy, Pydantic/Validator
    - **Machine Learning:** Scikit-Learn (Random Forest, Gradient Boosting, DBSCAN Clustering)
    - **Database & SQL:** SQLite embedded / MySQL Enterprise with Advanced Window Functions & CTEs
    - **Visualization:** Streamlit, Plotly Express, Folium GIS, Power BI (.pbix)
    - **AI Copilot:** Context-aware domain assistant explaining every graph and KPI live
    - **Testing & Quality:** Pytest automated test suite (100% pass)
    """)
