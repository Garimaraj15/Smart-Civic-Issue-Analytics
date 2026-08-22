"""
Tests for Data Cleaning and Preprocessing module.
"""

import pytest
import pandas as pd
import numpy as np
from src.data.cleaner import DataCleaner


@pytest.fixture
def sample_raw_df():
    return pd.DataFrame(
        {
            "Complaint_ID": ["CMP001", "CMP002", "CMP002", "CMP003"],
            "Complaint_Date": ["2026-01-01", "02/01/2026", "02/01/2026", "2026-01-03"],
            "District": ["north ", "SOUTH", "SOUTH", "east"],
            "Issue_Type": ["Pothole", "Water Leakage", "Water Leakage", "Street Light Fault"],
            "Department": [np.nan, "Water Department", "Water Department", np.nan],
            "Assigned_Officer": [np.nan, "Priya Sharma", "Priya Sharma", np.nan],
            "Remarks": [np.nan, "Repaired", "Repaired", "Pending review"],
            "Latitude": [22.5, 22.6, 22.6, 22.7],
            "Longitude": [88.3, 88.4, 88.4, 88.5],
        }
    )


def test_remove_duplicates(sample_raw_df):
    cleaner = DataCleaner(sample_raw_df)
    cleaner.remove_duplicates()
    assert len(cleaner.df) == 3


def test_impute_missing_values(sample_raw_df):
    cleaner = DataCleaner(sample_raw_df)
    cleaner.remove_duplicates().impute_missing_values()

    # Department imputation from Issue_Type
    assert cleaner.df.loc[cleaner.df["Issue_Type"] == "Pothole", "Department"].values[0] == "Road Department"
    assert cleaner.df.loc[cleaner.df["Issue_Type"] == "Street Light Fault", "Department"].values[0] == "Electricity Department"

    # Officer imputation from Department
    assert cleaner.df.loc[cleaner.df["Issue_Type"] == "Pothole", "Assigned_Officer"].values[0] == "Rajesh Kumar"
    assert cleaner.df.loc[cleaner.df["Issue_Type"] == "Street Light Fault", "Assigned_Officer"].values[0] == "Amit Singh"

    # Remarks imputation
    assert cleaner.df.loc[cleaner.df["Issue_Type"] == "Pothole", "Remarks"].values[0] == "No Remarks"


def test_standardize_text(sample_raw_df):
    cleaner = DataCleaner(sample_raw_df)
    cleaner.remove_duplicates().standardize_text()
    assert cleaner.df["District"].tolist() == ["North", "South", "East"]
