"""
Business KPI computation engine.
Computes executive scorecards, SLA compliance rates, department turnaround rankings,
and citizen satisfaction driver statistics.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


class CivicKPIEngine:
    """Computes civic performance metrics and operational KPIs."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def get_executive_summary(self) -> Dict[str, Any]:
        """Calculates top-level command center KPIs."""
        total_complaints = len(self.df)
        resolved_count = (self.df["Status"] == "Resolved").sum()
        open_count = (self.df["Status"] == "Open").sum()
        in_progress_count = (self.df["Status"] == "In Progress").sum()
        resolution_rate = (
            (resolved_count / total_complaints * 100) if total_complaints > 0 else 0
        )

        resolved_df = self.df[self.df["Status"] == "Resolved"]
        avg_turnaround_days = resolved_df["Resolution_Time_Days"].mean()
        median_turnaround_days = resolved_df["Resolution_Time_Days"].median()

        # SLA Compliance
        sla_evaluated = self.df[self.df["SLA_Status"].isin(["Within SLA", "SLA Breached"])]
        sla_within_count = (sla_evaluated["SLA_Status"] == "Within SLA").sum()
        sla_compliance_rate = (
            (sla_within_count / len(sla_evaluated) * 100)
            if len(sla_evaluated) > 0
            else 0
        )

        avg_citizen_rating = self.df["Citizen_Rating"].dropna().mean()
        high_priority_pct = (
            (self.df["Priority"] == "High").sum() / total_complaints * 100
            if total_complaints > 0
            else 0
        )

        return {
            "total_complaints": int(total_complaints),
            "resolved_complaints": int(resolved_count),
            "open_complaints": int(open_count),
            "in_progress_complaints": int(in_progress_count),
            "resolution_rate_pct": round(float(resolution_rate), 1),
            "avg_turnaround_days": round(float(avg_turnaround_days), 2) if not np.isnan(avg_turnaround_days) else 0.0,
            "median_turnaround_days": round(float(median_turnaround_days), 1) if not np.isnan(median_turnaround_days) else 0.0,
            "sla_compliance_rate_pct": round(float(sla_compliance_rate), 1),
            "avg_citizen_rating": round(float(avg_citizen_rating), 2) if not np.isnan(avg_citizen_rating) else 0.0,
            "high_priority_pct": round(float(high_priority_pct), 1),
        }

    def get_department_scorecard(self) -> pd.DataFrame:
        """Computes comprehensive department efficiency leaderboard."""
        dept_grouped = self.df.groupby("Department").agg(
            Total_Complaints=("Complaint_ID", "count"),
            Resolved_Count=("Status", lambda s: (s == "Resolved").sum()),
            Avg_Resolution_Days=("Resolution_Time_Days", "mean"),
            Median_Resolution_Days=("Resolution_Time_Days", "median"),
            SLA_Breach_Count=("SLA_Status", lambda s: (s == "SLA Breached").sum()),
            Avg_Citizen_Rating=("Citizen_Rating", "mean"),
        ).reset_index()

        dept_grouped["Resolution_Rate_Pct"] = (
            dept_grouped["Resolved_Count"] / dept_grouped["Total_Complaints"] * 100
        ).round(1)
        dept_grouped["SLA_Breach_Rate_Pct"] = (
            dept_grouped["SLA_Breach_Count"] / dept_grouped["Total_Complaints"] * 100
        ).round(1)
        dept_grouped["Avg_Resolution_Days"] = dept_grouped["Avg_Resolution_Days"].round(1)
        dept_grouped["Avg_Citizen_Rating"] = dept_grouped["Avg_Citizen_Rating"].round(2)

        return dept_grouped.sort_values(by="Total_Complaints", ascending=False)

    def get_officer_performance(self) -> pd.DataFrame:
        """Computes assigned officer resolution metrics and citizen ratings."""
        officer_df = self.df.groupby(["Assigned_Officer", "Department"]).agg(
            Assigned_Tickets=("Complaint_ID", "count"),
            Resolved_Tickets=("Status", lambda s: (s == "Resolved").sum()),
            Avg_Turnaround_Days=("Resolution_Time_Days", "mean"),
            Avg_Rating=("Citizen_Rating", "mean"),
            SLA_Breaches=("SLA_Status", lambda s: (s == "SLA Breached").sum()),
        ).reset_index()

        officer_df["Resolution_Efficiency_Pct"] = (
            officer_df["Resolved_Tickets"] / officer_df["Assigned_Tickets"] * 100
        ).round(1)
        officer_df["Avg_Turnaround_Days"] = officer_df["Avg_Turnaround_Days"].round(1)
        officer_df["Avg_Rating"] = officer_df["Avg_Rating"].round(2)

        return officer_df.sort_values(by="Assigned_Tickets", ascending=False)
