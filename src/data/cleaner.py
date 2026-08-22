"""
Data Cleaning and Standardization module.
Performs deduplication, missing value imputation via domain lookup,
date parsing/standardization, and text normalization.
"""

import pandas as pd
from src.core.config import (
    DEPARTMENT_MAPPING,
    OFFICER_MAPPING,
    CLEANED_CSV_PATH,
)
from src.core.logger import get_logger

logger = get_logger("DataCleaner")


class DataCleaner:
    """Standardizes, cleans, and imputes civic complaints data."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def remove_duplicates(self) -> "DataCleaner":
        """Removes duplicate rows."""
        initial_len = len(self.df)
        self.df = self.df.drop_duplicates()
        dropped = initial_len - len(self.df)
        if dropped > 0:
            logger.info(f"Removed {dropped} duplicate records.")
        return self

    def impute_missing_values(self) -> "DataCleaner":
        """Fills missing departments, assigned officers, and remarks using domain heuristics."""
        # Fill Department from Issue_Type
        if "Department" in self.df.columns and "Issue_Type" in self.df.columns:
            self.df["Department"] = self.df["Department"].fillna(
                self.df["Issue_Type"].map(DEPARTMENT_MAPPING)
            )

        # Fill Assigned Officer from Department
        if "Assigned_Officer" in self.df.columns and "Department" in self.df.columns:
            self.df["Assigned_Officer"] = self.df["Assigned_Officer"].fillna(
                self.df["Department"].map(OFFICER_MAPPING)
            )

        # Fill Remarks
        if "Remarks" in self.df.columns:
            self.df["Remarks"] = self.df["Remarks"].fillna("No Remarks")

        return self

    def standardize_dates(self) -> "DataCleaner":
        """Converts dates to standard datetime format with validation."""
        for date_col in ["Complaint_Date", "Resolution_Date"]:
            if date_col in self.df.columns:
                self.df[date_col] = pd.to_datetime(
                    self.df[date_col], format="mixed", dayfirst=True, errors="coerce"
                )
        return self

    def standardize_text(self) -> "DataCleaner":
        """Strips whitespace and converts text columns to Title Case."""
        text_columns = [
            "District",
            "Ward",
            "Area",
            "Issue_Type",
            "Department",
            "Priority",
            "Status",
            "Assigned_Officer",
            "Remarks",
        ]
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = (
                    self.df[col].astype(str).str.strip().str.title()
                )
                self.df[col] = self.df[col].replace({"Nan": None, "None": None})
        return self

    def clean(self) -> pd.DataFrame:
        """Executes full cleaning pipeline."""
        logger.info("Starting data cleaning pipeline...")
        (
            self.remove_duplicates()
            .impute_missing_values()
            .standardize_dates()
            .standardize_text()
        )
        logger.info(f"Data cleaning finished. Cleaned shape: {self.df.shape}")
        return self.df

    def export(self, output_path: str = None) -> pd.DataFrame:
        """Cleans and exports dataset to CSV."""
        cleaned_df = self.clean()
        save_path = output_path or CLEANED_CSV_PATH
        cleaned_df.to_csv(save_path, index=False)
        logger.info(f"Saved cleaned dataset to: {save_path}")
        return cleaned_df
