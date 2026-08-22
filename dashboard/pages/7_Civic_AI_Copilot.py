"""
Page 7: Dedicated Civic AI Copilot & Interactive Project Tutor.
"""

import streamlit as st
import pandas as pd
from dashboard.utils import load_data, apply_custom_css
from src.analytics.ai_copilot import CivicAICopilot
from src.analytics.kpis import CivicKPIEngine

st.set_page_config(page_title="Civic AI Copilot - Assistant", page_icon="🤖", layout="wide")
apply_custom_css()

st.title("🤖 Civic AI Copilot & Interactive Project Tutor")
st.markdown("Your interactive AI assistant to explain every graph, metric, machine learning model, and SQL query in simple English or Hinglish.")

df = load_data()
kpi_engine = CivicKPIEngine(df)
summary = kpi_engine.get_executive_summary()

# Pre-defined Suggested Questions
st.subheader("💡 Click a Suggested Question to Get an Instant Explanation:")
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("📊 1. Explain All Executive KPIs & Metrics", use_container_width=True):
        st.session_state["main_copilot_q"] = "Explain all executive KPIs and metrics"
    if st.button("🗺️ 2. How does DBSCAN Hotspot Clustering work?", use_container_width=True):
        st.session_state["main_copilot_q"] = "How does DBSCAN hotspot clustering work and why haversine?"

with c2:
    if st.button("⏱️ 3. Why is SLA Breach so high (68%)?", use_container_width=True):
        st.session_state["main_copilot_q"] = "Why is SLA breach high and how do we solve it?"
    if st.button("🤖 4. How does the Random Forest Model work?", use_container_width=True):
        st.session_state["main_copilot_q"] = "How does the Random Forest ML classifier work?"

with c3:
    if st.button("🗄️ 5. Explain SQL Window Functions (DENSE_RANK, LAG)", use_container_width=True):
        st.session_state["main_copilot_q"] = "Explain SQL Window Functions DENSE_RANK and LAG"
    if st.button("💼 6. How should I explain this project in an Interview?", use_container_width=True):
        st.session_state["main_copilot_q"] = "How should I explain this project in a placement interview?"

st.markdown("---")

# Custom Query Chat Box
st.subheader("💬 Ask Your Own Question (Hinglish or English):")

default_val = st.session_state.get("main_copilot_q", "")
user_input = st.text_input(
    "Type your question here:",
    value=default_val,
    placeholder="e.g. Ye project kis problem ko solve karta hai? / What does turnaround time mean?",
)

if user_input:
    response = CivicAICopilot.answer_query(user_input)
    st.markdown("### 💡 AI Explanation:")
    st.info(response)

st.markdown("---")

# Project Summary Cheat Sheet
with st.expander("📚 Complete Project Architecture & Formula Cheat Sheet", expanded=False):
    st.markdown("""
    ### 🏗️ 1. Pipeline Flow:
    1. **Raw Ingestion:** Ingests Excel dataset with 1,000+ complaints across 5 districts.
    2. **Automated Validator (`validator.py`):** Checks duplicates, negative durations, and GPS coordinates; generates a Data Quality Score (PASS at 78-95/100).
    3. **Cleaning & Imputation (`cleaner.py`):** Automatically maps missing departments and assigned officers using domain lookup tables.
    4. **Feature Engineering (`engineer.py`):** Computes 25+ features (SLA Breached Flag, Resolution Days, Weekday, Severity Score, Officer Workload).
    5. **Machine Learning (`sla_predictor.py`, `resolution_estimator.py`):** Trains Random Forest to predict SLA risk at ingestion (F1-score: 0.78) and Regressor for repair turnaround.
    6. **Geospatial Hotspots (`cluster_analyzer.py`):** Uses DBSCAN Haversine density clustering to group recurring infrastructure failures.
    7. **Enterprise SQL (`sql/`):** Star Schema, Indexes, Reporting Views, and Window Functions (`DENSE_RANK`, `LAG`, `NTILE`, rolling averages).
    8. **Multi-Page Web App (`dashboard/`):** 7 interactive Streamlit pages with Plotly visuals and AI Copilot explainers.
    """)
