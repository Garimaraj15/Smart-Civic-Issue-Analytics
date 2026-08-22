"""
Tests for Machine Learning prediction pipelines and spatial clustering.
"""

import pytest
import pandas as pd
import numpy as np
from src.models.sla_predictor import SLAPredictor
from src.models.resolution_estimator import ResolutionEstimator
from src.models.cluster_analyzer import GeospatialClusterAnalyzer


@pytest.fixture
def sample_feature_df():
    data = []
    for i in range(50):
        data.append(
            {
                "Complaint_ID": f"CMP{i:03d}",
                "District": "East" if i % 2 == 0 else "North",
                "Ward": f"Ward-{i%10}",
                "Area": "Salt Lake" if i % 2 == 0 else "Shyambazar",
                "Issue_Type": "Pothole" if i % 3 == 0 else "Water Leakage",
                "Department": "Road Department" if i % 3 == 0 else "Water Department",
                "Priority": "High" if i % 3 == 0 else ("Medium" if i % 3 == 1 else "Low"),
                "Weekday": "Monday",
                "Month_Num": 3,
                "Is_Weekend": 0,
                "Complaint_Severity_Score": 3 if i % 3 == 0 else (2 if i % 3 == 1 else 1),
                "Officer_Workload_Count": 10,
                "Area_Complaint_Density": 25,
                "Resolution_Time_Days": float(2 if i % 2 == 0 else 6),
                "SLA_Breached_Flag": 0 if i % 2 == 0 else 1,
                "Status": "Resolved",
                "Citizen_Rating": 4.0,
                "Latitude": 22.5726 + (i * 0.001),
                "Longitude": 88.3639 + (i * 0.001),
            }
        )
    return pd.DataFrame(data)


def test_sla_predictor_train_predict(sample_feature_df):
    predictor = SLAPredictor()
    metrics = predictor.train_and_evaluate(sample_feature_df)
    assert "accuracy" in metrics
    assert "roc_auc" in metrics

    # Test single ticket inference
    sample_ticket = {
        "District": "East",
        "Issue_Type": "Pothole",
        "Department": "Road Department",
        "Priority": "High",
        "Weekday": "Monday",
        "Complaint_Severity_Score": 3,
        "Officer_Workload_Count": 15,
        "Area_Complaint_Density": 30,
        "Month_Num": 3,
        "Is_Weekend": 0,
    }
    pred = predictor.predict_risk(sample_ticket)
    assert "breach_probability" in pred
    assert "risk_tier" in pred
    assert pred["risk_tier"] in ["High", "Medium", "Low"]


def test_resolution_estimator(sample_feature_df):
    estimator = ResolutionEstimator()
    metrics = estimator.train_and_evaluate(sample_feature_df)
    assert "mae" in metrics
    assert "rmse" in metrics

    sample_ticket = {
        "District": "East",
        "Issue_Type": "Pothole",
        "Department": "Road Department",
        "Priority": "High",
        "Weekday": "Monday",
        "Complaint_Severity_Score": 3,
        "Officer_Workload_Count": 15,
        "Area_Complaint_Density": 30,
        "Month_Num": 3,
    }
    pred = estimator.predict_days(sample_ticket)
    assert "estimated_resolution_days" in pred
    assert pred["estimated_resolution_days"] > 0


def test_geospatial_clustering(sample_feature_df):
    analyzer = GeospatialClusterAnalyzer(sample_feature_df)
    clustered_df = analyzer.find_hotspots(eps_km=1.0, min_samples=3)
    assert "Hotspot_Cluster_ID" in clustered_df.columns
    assert "Is_Hotspot" in clustered_df.columns
