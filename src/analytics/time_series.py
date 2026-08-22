"""
Time-series and trend analytics module.
Calculates daily/weekly complaint arrival velocity, 7-day moving averages,
and seasonal patterns.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


class CivicTimeSeriesAnalyzer:
    """Analyzes temporal patterns, complaint velocities, and daily trends."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df["Complaint_Date"] = pd.to_datetime(self.df["Complaint_Date"])

    def get_daily_trend(self) -> pd.DataFrame:
        """Computes daily complaint arrivals with 7-day moving average."""
        daily = (
            self.df.groupby("Complaint_Date")
            .size()
            .reset_index(name="Daily_Complaints")
        )
        daily = daily.sort_values("Complaint_Date")
        daily["7_Day_Moving_Avg"] = (
            daily["Daily_Complaints"].rolling(window=7, min_periods=1).mean().round(2)
        )
        return daily

    def get_monthly_trend(self) -> pd.DataFrame:
        """Computes monthly complaint volume by Department."""
        monthly = (
            self.df.groupby(["Year", "Month_Num", "Month", "Department"])
            .size()
            .reset_index(name="Total_Complaints")
        )
        monthly = monthly.sort_values(["Year", "Month_Num"])
        return monthly

    def get_day_of_week_distribution(self) -> pd.DataFrame:
        """Calculates weekday complaint volume and severity."""
        days_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        weekday_stats = (
            self.df.groupby("Weekday")
            .agg(
                Total_Complaints=("Complaint_ID", "count"),
                Avg_Severity=("Complaint_Severity_Score", "mean"),
            )
            .reindex(days_order)
            .reset_index()
        )
        weekday_stats["Avg_Severity"] = weekday_stats["Avg_Severity"].round(2)
        return weekday_stats
