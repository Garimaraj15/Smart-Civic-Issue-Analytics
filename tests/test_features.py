"""
Tests for Feature Engineering module.
"""

import pytest
import pandas as pd
import numpy as np
from src.features.engineer import FeatureEngineer


@pytest.fixture
def sample_clean_df():
    return pd.DataFrame(
        {
            "Complaint_ID": ["CMP001", "CMP002", "CMP003"],
            "Complaint_Date": ["2026-03-01", "2026-03-01", "2026-03-10"],
            "Resolution_Date": ["2026-03-03", "2026-03-08", np.nan],
            "Priority": ["High", "Medium", "Low"],
            "Status": ["Resolved", "Resolved", "Open"],
            "Assigned_Officer": ["Rajesh Kumar", "Rajesh Kumar", "Priya Sharma"],
            "Area": ["Salt Lake", "Salt Lake", "New Town"],
            "Issue_Type": ["Pothole", "Pothole", "Water Leakage"],
            "Department": ["Road Department", "Road Department", "Water Department"],
            "District": ["East", "East", "North"],
            "Weekday": ["Sunday", "Sunday", "Tuesday"],
        }
    )


def test_resolution_time_calculation(sample_clean_df):
    engineer = FeatureEngineer(sample_clean_df)
    df_feat = engineer.engineer_resolution_features().df

    assert df_feat.loc[0, "Resolution_Time_Days"] == 2
    assert df_feat.loc[1, "Resolution_Time_Days"] == 7
    assert pd.isna(df_feat.loc[2, "Resolution_Time_Days"])


def test_sla_status_assignment(sample_clean_df):
    engineer = FeatureEngineer(sample_clean_df)
    df_feat = engineer.engineer_resolution_features().df

    assert df_feat.loc[0, "SLA_Status"] == "Within SLA"
    assert df_feat.loc[0, "SLA_Breached_Flag"] == 0
    assert df_feat.loc[1, "SLA_Status"] == "SLA Breached"
    assert df_feat.loc[1, "SLA_Breached_Flag"] == 1
    assert df_feat.loc[2, "SLA_Status"] == "Pending"
    assert pd.isna(df_feat.loc[2, "SLA_Breached_Flag"])


def test_severity_score_and_workload(sample_clean_df):
    engineer = FeatureEngineer(sample_clean_df)
    df_feat = engineer.engineer_civic_risk_indices().df

    assert df_feat.loc[0, "Complaint_Severity_Score"] == 3
    assert df_feat.loc[1, "Complaint_Severity_Score"] == 2
    assert df_feat.loc[2, "Complaint_Severity_Score"] == 1

    # Officer Workload
    assert df_feat.loc[0, "Officer_Workload_Count"] == 2
    assert df_feat.loc[2, "Officer_Workload_Count"] == 1
