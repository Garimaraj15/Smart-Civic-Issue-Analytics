"""
Page 4: Applied Machine Learning Predictive Dispatcher & Risk Studio.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.utils import load_data, apply_custom_css, render_ai_copilot_sidebar
from src.models.sla_predictor import SLAPredictor
from src.models.resolution_estimator import ResolutionEstimator

st.set_page_config(page_title="AI Predictive Studio - Civic Analytics", page_icon="🤖", layout="wide")
apply_custom_css()

st.title("🤖 AI Predictive Studio & Smart Dispatcher")
st.markdown("Real-time Machine Learning inference engine to predict SLA breach risk and forecast resolution duration for incoming civic complaints.")

# Render AI Copilot in Sidebar
render_ai_copilot_sidebar("AI Predictive Studio")

# Load Models
sla_predictor = SLAPredictor()
res_estimator = ResolutionEstimator()

try:
    sla_predictor.load()
    res_estimator.load()
    models_ready = True
except Exception as e:
    models_ready = False
    st.error(f"Models not loaded: {e}. Please run the pipeline first.")

if models_ready:
    col_input, col_output = st.columns([1, 1])

    with col_input:
        st.subheader("📝 New Civic Ticket Ingestion Sandbox")
        st.caption("Simulate an incoming citizen complaint to calculate real-time risk scores:")

        with st.form("ticket_form"):
            district = st.selectbox("District", ["East", "West", "North", "South", "Central"])
            issue_type = st.selectbox(
                "Issue Type",
                [
                    "Pothole",
                    "Road Damage",
                    "Water Leakage",
                    "Street Light Fault",
                    "Garbage Overflow",
                    "Illegal Dumping",
                    "Sewer Problem",
                    "Drain Blockage",
                    "Park Maintenance",
                    "Traffic Signal Fault",
                ],
            )
            department_mapping = {
                "Pothole": "Road Department",
                "Road Damage": "Road Department",
                "Water Leakage": "Water Department",
                "Street Light Fault": "Electricity Department",
                "Garbage Overflow": "Sanitation Department",
                "Illegal Dumping": "Sanitation Department",
                "Sewer Problem": "Sewer Department",
                "Drain Blockage": "Sewer Department",
                "Park Maintenance": "Parks Department",
                "Traffic Signal Fault": "Traffic Department",
            }
            dept = department_mapping.get(issue_type, "Road Department")
            st.info(f"🏢 Auto-Assigned Department: **{dept}**")

            priority = st.select_slider("Priority Tier", options=["Low", "Medium", "High"], value="High")
            weekday = st.selectbox("Day of Week Registered", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            
            workload_val = st.slider("Assigned Officer Current Workload", 1, 50, 15)
            density_val = st.slider("Area Complaint Density", 5, 100, 35)

            submit_btn = st.form_submit_button("🚀 Run AI Risk & Turnaround Inference", use_container_width=True)

    with col_output:
        st.subheader("⚡ Real-Time Predictive Assessment")
        
        severity_val = 3 if priority == "High" else (2 if priority == "Medium" else 1)
        month_val = 3
        is_weekend_val = 1 if weekday in ["Saturday", "Sunday"] else 0

        input_dict = {
            "District": district,
            "Issue_Type": issue_type,
            "Department": dept,
            "Priority": priority,
            "Weekday": weekday,
            "Complaint_Severity_Score": severity_val,
            "Officer_Workload_Count": workload_val,
            "Area_Complaint_Density": density_val,
            "Month_Num": month_val,
            "Is_Weekend": is_weekend_val,
        }

        # Predict Risk
        risk_res = sla_predictor.predict_risk(input_dict)
        time_res = res_estimator.predict_days(input_dict)

        # Gauge Chart for Breach Risk
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=risk_res["breach_probability"],
                title={"text": "SLA Breach Probability (%)", "font": {"size": 20}},
                number={"suffix": "%", "font": {"size": 32, "color": "#38bdf8"}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#ef4444" if risk_res["breach_probability"] >= 50 else "#10b981"},
                    "steps": [
                        {"range": [0, 35], "color": "rgba(16, 185, 129, 0.2)"},
                        {"range": [35, 65], "color": "rgba(245, 158, 11, 0.2)"},
                        {"range": [65, 100], "color": "rgba(239, 68, 68, 0.2)"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 50,
                    },
                },
            )
        )
        fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Prediction Outcome Cards
        c_res1, c_res2 = st.columns(2)
        with c_res1:
            st.metric("Estimated Resolution Time", f"{time_res['estimated_resolution_days']} Days", "SLA Target: 3.0 Days")
        with c_res2:
            st.metric("Risk Classification Tier", f"{risk_res['risk_tier']} Risk")

        st.success(f"**Automated Decision:** {risk_res['recommended_action']}")

    st.markdown("---")

    # Model Transparency & Feature Importance
    st.subheader("🔍 Model Explainability & Key Drivers")
    c_fi, c_metrics = st.columns([3, 2])

    with c_fi:
        st.markdown("##### Top Predictive Features Influencing SLA Outcomes")
        if sla_predictor.feature_importances:
            fi_df = pd.DataFrame(
                list(sla_predictor.feature_importances.items()),
                columns=["Feature", "Importance Weight"],
            ).sort_values("Importance Weight", ascending=True)

            fig_fi = px.bar(
                fi_df,
                x="Importance Weight",
                y="Feature",
                orientation="h",
                color="Importance Weight",
                color_continuous_scale="Teal",
            )
            fig_fi.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_fi, use_container_width=True)
        else:
            st.info("Feature importance data available for tree models.")

    with c_metrics:
        st.markdown("##### Model Evaluation Scorecard")
        st.json(sla_predictor.metrics)
