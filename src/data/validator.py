"""
Data Quality Validation and Anomaly Detection module.
Profiles raw and transformed data, checks schema invariants, and generates audit reports.
"""

import json
from typing import Dict, Any
import pandas as pd
from src.core.config import DATA_AUDIT_REPORT_PATH
from src.core.logger import get_logger

logger = get_logger("DataValidator")


class DataValidator:
    """Performs validation checks, schema verification, and anomaly profiling."""

    MANDATORY_COLS = ["Complaint_ID", "Complaint_Date", "District", "Issue_Type", "Latitude", "Longitude"]

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.report: Dict[str, Any] = {}

    def run_full_validation(self) -> Dict[str, Any]:
        """Runs comprehensive validation checks and returns summary metrics."""
        logger.info("Executing comprehensive data quality audit...")

        total_rows = len(self.df)
        total_cols = len(self.df.columns)
        duplicates = int(self.df.duplicated().sum())

        missing_summary = self.df.isnull().sum().to_dict()
        
        # Calculate missingness only on mandatory ingestion fields
        mandatory_missing = sum(
            int(self.df[col].isnull().sum()) for col in self.MANDATORY_COLS if col in self.df.columns
        )

        # Check coordinate bounds (Kolkata region roughly lat 20.0-26.0, lon 85.0-92.0)
        coord_anomalies = 0
        if "Latitude" in self.df.columns and "Longitude" in self.df.columns:
            invalid_coords = self.df[
                (self.df["Latitude"].isna())
                | (self.df["Longitude"].isna())
                | (~self.df["Latitude"].between(20.0, 26.0))
                | (~self.df["Longitude"].between(85.0, 92.0))
            ]
            coord_anomalies = len(invalid_coords)

        # Date consistency check
        date_anomalies = 0
        if "Complaint_Date" in self.df.columns and "Resolution_Date" in self.df.columns:
            valid_dates = self.df[self.df["Resolution_Date"].notna() & self.df["Complaint_Date"].notna()]
            comp_dt = pd.to_datetime(valid_dates["Complaint_Date"], errors="coerce")
            res_dt = pd.to_datetime(valid_dates["Resolution_Date"], errors="coerce")
            invalid_dates = (res_dt < comp_dt).sum()
            date_anomalies = int(invalid_dates)

        # Score calculation (100 base score minus penalty deductions)
        quality_score = max(
            0,
            100
            - (duplicates * 2)
            - (mandatory_missing * 1.5)
            - (coord_anomalies * 2)
            - (date_anomalies * 3),
        )

        self.report = {
            "total_records": total_rows,
            "total_features": total_cols,
            "duplicate_records": duplicates,
            "mandatory_missing_values": mandatory_missing,
            "missing_per_column": missing_summary,
            "geospatial_anomalies": coord_anomalies,
            "date_sequence_anomalies": date_anomalies,
            "data_quality_score": round(float(quality_score), 2),
            "status": "PASS" if quality_score >= 80 else "ACTION_REQUIRED",
        }

        # Persist report to JSON
        with open(DATA_AUDIT_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=4)

        logger.info(
            f"Audit Complete! Data Quality Score: {self.report['data_quality_score']}/100 | Status: {self.report['status']}"
        )
        return self.report
