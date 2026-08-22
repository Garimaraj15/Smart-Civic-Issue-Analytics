"""
Feature Engineering module for civic complaints.
Extracts temporal, operational, SLA, geospatial density, and risk index features.
"""

import pandas as pd
import numpy as np
from src.core.config import (
    SEVERITY_MAPPING,
    SLA_THRESHOLD_DAYS,
    FEATURE_CSV_PATH,
)
from src.core.logger import get_logger

logger = get_logger("FeatureEngineer")


class FeatureEngineer:
    """Computes analytical features and ML predictors from cleaned complaints data."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def engineer_temporal_features(self) -> "FeatureEngineer":
        """Extracts date-derived features."""
        comp_date = pd.to_datetime(self.df["Complaint_Date"])
        self.df["Month"] = comp_date.dt.month_name()
        self.df["Month_Num"] = comp_date.dt.month
        self.df["Year"] = comp_date.dt.year
        self.df["Weekday"] = comp_date.dt.day_name()
        self.df["Is_Weekend"] = comp_date.dt.weekday.isin([5, 6]).astype(int)
        self.df["Quarter"] = "Q" + comp_date.dt.quarter.astype(str)
        self.df["Day_of_Month"] = comp_date.dt.day
        return self

    def engineer_resolution_features(self) -> "FeatureEngineer":
        """Calculates resolution turnaround time and SLA compliance."""
        comp_date = pd.to_datetime(self.df["Complaint_Date"])
        res_date = pd.to_datetime(self.df["Resolution_Date"])

        # Resolution Time
        self.df["Resolution_Time_Days"] = (res_date - comp_date).dt.days

        # Clean invalid negative resolution dates
        self.df.loc[self.df["Resolution_Time_Days"] < 0, "Resolution_Time_Days"] = np.nan

        # Categorization
        def categorize_resolution(days):
            if pd.isna(days):
                return "Pending"
            if days <= 3:
                return "Fast"
            elif days <= 7:
                return "Medium"
            return "Slow"

        self.df["Resolution_Category"] = self.df["Resolution_Time_Days"].apply(
            categorize_resolution
        )

        # SLA Status
        def categorize_sla(days):
            if pd.isna(days):
                return "Pending"
            return "Within SLA" if days <= SLA_THRESHOLD_DAYS else "SLA Breached"

        self.df["SLA_Status"] = self.df["Resolution_Time_Days"].apply(categorize_sla)

        # Binary SLA Target for Machine Learning (1 = Breached, 0 = Within SLA, NaN = Pending)
        self.df["SLA_Breached_Flag"] = self.df["Resolution_Time_Days"].apply(
            lambda d: np.nan if pd.isna(d) else (1 if d > SLA_THRESHOLD_DAYS else 0)
        )

        # Complaint Age
        max_date = comp_date.max() if not comp_date.empty else pd.Timestamp.today()
        self.df["Complaint_Age_Days"] = (max_date - comp_date).dt.days

        # Is Resolved Flag
        self.df["Is_Resolved"] = self.df["Status"].apply(
            lambda x: "Yes" if str(x).strip().title() == "Resolved" else "No"
        )

        return self

    def engineer_civic_risk_indices(self) -> "FeatureEngineer":
        """Calculates severity scores, officer workload, and area complaint density."""
        # Severity Score
        self.df["Complaint_Severity_Score"] = (
            self.df["Priority"].map(SEVERITY_MAPPING).fillna(1).astype(int)
        )

        # Officer Workload (Total tickets per officer)
        officer_counts = self.df["Assigned_Officer"].value_counts().to_dict()
        self.df["Officer_Workload_Count"] = self.df["Assigned_Officer"].map(
            officer_counts
        ).fillna(0).astype(int)

        # Area Complaint Density (Total complaints in area)
        area_counts = self.df["Area"].value_counts().to_dict()
        self.df["Area_Complaint_Density"] = self.df["Area"].map(area_counts).fillna(0).astype(int)

        # Civic Priority Index: Severity * 10 + (Workload / 10)
        self.df["Civic_Priority_Index"] = (
            self.df["Complaint_Severity_Score"] * 10
            + (self.df["Officer_Workload_Count"] / 10.0)
        ).round(2)

        return self

    def engineer_all(self) -> pd.DataFrame:
        """Executes full feature engineering suite."""
        logger.info("Executing feature engineering pipeline...")
        (
            self.engineer_temporal_features()
            .engineer_resolution_features()
            .engineer_civic_risk_indices()
        )
        logger.info(
            f"Feature engineering complete! Shape: {self.df.shape} ({len(self.df.columns)} features)"
        )
        return self.df

    def export(self, output_path: str = None) -> pd.DataFrame:
        """Exports engineered dataset to CSV."""
        df_feat = self.engineer_all()
        save_path = output_path or FEATURE_CSV_PATH
        df_feat.to_csv(save_path, index=False)
        logger.info(f"Saved feature-engineered dataset to: {save_path}")
        return df_feat
