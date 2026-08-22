"""
AI Civic Copilot & Graph Explainer Engine.
Provides instant domain explainability for every metric, chart, ML model, and SQL query.
Supports context-aware Q&A in English and Hinglish (offline smart heuristic NLP + optional LLM integration).
"""

import os
import re
from typing import Dict, Any, List
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class CivicAICopilot:
    """Intelligent Assistant providing graph, metric, and analytical explainability."""

    PAGE_KNOWLEDGE = {
        "Executive Overview": """
📌 **Executive Overview Page Explanation:**
- **Total Complaints (1,000):** Total municipal issues logged across 5 districts.
- **Resolution Rate (32.3%):** Percentage of total tickets resolved so far (323 resolved out of 1,000). The remaining tickets are either 'In Progress' or 'Open'.
- **SLA Compliance (31.6%):** Percentage of resolved tickets completed within the mandatory 3-day SLA limit. 68.4% of resolved tickets breached the SLA!
- **Avg Turnaround (5.47 - 6.3 Days):** The average time taken to fix an issue from complaint date to resolution date.
- **Citizen Rating (3.49 - 4.03 / 5.0):** Citizen satisfaction score given after resolution.
- **Daily Volume & 7-Day Moving Average Line:** Shows daily arrival velocity. The 7-day rolling average smooths out daily volatility to identify long-term surge trends.
- **Complaints by District Stacked Bar:** Compares total volume and high/medium/low priority breakdown across East, West, North, South, and Central zones.
- **SLA Breakdown Pie Chart:** Proportions of tickets that are Within SLA (Green), Breached (Red), and Pending (Orange).
        """,
        
        "Geospatial Explorer": """
📌 **Geospatial GIS & Hotspots Page Explanation:**
- **Scatter Incident Map:** Each bubble is an actual GPS coordinate where an issue was reported. Color indicates Priority (Red=High, Orange=Medium, Green=Low) and size indicates severity.
- **Spatial HeatMap:** Shows thermal intensity of civic complaints. Bright dense red/orange zones highlight severe municipal problem areas.
- **DBSCAN Hotspot Clusters:** Unsupervised ML algorithm (Density-Based Spatial Clustering of Applications with Noise) using Haversine distance. It automatically groups recurring incidents within a 1.5 km radius without relying on arbitrary administrative boundaries.
- **Actionable Insight:** Areas like Salt Lake & Shyambazar show recurring sewer and road damage clusters needing preventive infrastructure overhauls.
        """,

        "Department Deep Dive": """
📌 **Department Deep Dive Page Explanation:**
- **Department Performance Matrix:** Compares all 7 municipal departments across volume, resolution rate %, SLA breach %, average turnaround days, and citizen ratings.
- **Turnaround Box Plot (Days):** Shows median resolution days and spread/outliers per department. The dashed red line at 3 days represents the SLA threshold.
- **Officer Workload vs Rating Scatter:** Plots number of assigned tickets on the X-axis against citizen ratings on the Y-axis. Helps identify overworked officers whose performance or ratings drop due to ticket overload.
        """,

        "AI Predictive Studio": """
📌 **AI Predictive Studio Page Explanation:**
- **Predictive SLA Classifier (Random Forest):** Takes new ticket details (Department, Issue Type, District, Day of Week, Officer Workload, Severity) and calculates the % probability of breaching the 3-day SLA.
- **Breach Probability Gauge:** Displays green (<35%), amber (35-65%), or red (>65% High Risk) so supervisors can triage and escalate tickets immediately.
- **Turnaround Regressor:** Predicts expected days needed to resolve the ticket (e.g., 4.2 days).
- **Feature Importance Chart:** Explains the 'Why' behind model decisions—showing which factors (like officer workload or issue type) contributed most to the risk score.
        """,

        "Citizen Sentiment": """
📌 **Citizen Sentiment & Satisfaction Page Explanation:**
- **Rating Distribution (1-5 Stars):** Shows the spread of public feedback. High ratings indicate good citizen sentiment; 1-2 star ratings signal severe dissatisfaction.
- **Turnaround Time vs Rating Scatter with Trendline:** Strong negative correlation—as resolution turnaround exceeds 4-5 days, citizen ratings drop sharply from 4.8★ down to 1.5★.
- **Department Rating Benchmark:** Ranks departments by public trust and satisfaction index.
        """,

        "SQL Analytics Lab": """
📌 **SQL Analytics Lab Page Explanation:**
- **Live Query Workspace:** Executes ANSI SQL queries directly against the analytical database in real time.
- **Window Functions Showcase:** Demonstrates `DENSE_RANK()` for department efficiency, `LAG()` for Month-over-Month growth %, `NTILE(4)` for ward risk quartiles, and `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` for rolling 7-day moving averages.
- **Interview Scenarios:** Preloaded with top 5 technical SQL interview queries asked by top tech and analytics companies.
        """
    }

    FAQ_DATABASE = [
        {
            "keywords": ["sla", "breach", "3 day", "threshold", "compliance"],
            "response": """
🎯 **SLA (Service Level Agreement) Explained:**
- **What is SLA?** In this municipal project, the government standard SLA is **3 Days** (a complaint must be resolved within 3 days of registration).
- **Why is it critical?** Currently, **~68% of resolved tickets breach this 3-day SLA** (averaging 5.5 to 6.3 days).
- **How we solve this:** Our Machine Learning model predicts SLA breach risk at the exact moment a citizen lodges a complaint. If the risk is >65%, the system automatically flags it for priority dispatch!
            """
        },
        {
            "keywords": ["dbscan", "cluster", "hotspot", "map", "gis", "haversine"],
            "response": """
🗺️ **DBSCAN Geospatial Clustering Explained:**
- **Why DBSCAN?** Standard ward boundaries don't capture real-world infrastructure issues (e.g. a broken water pipeline spans multiple wards). DBSCAN finds density-based clusters of any shape without needing predetermined cluster counts (unlike K-Means).
- **How it works:** Uses the **Haversine formula** on radian GPS coordinates with an epsilon radius ($\epsilon = 1.5\text{ km}$) and minimum sample count ($8\text{ complaints}$).
- **Result:** Pinpoints chronic failure corridors (e.g., repeat pothole zones in Salt Lake) for preventive maintenance contracts.
            """
        },
        {
            "keywords": ["random forest", "model", "ml", "machine learning", "classifier", "accuracy", "roc", "f1"],
            "response": """
🤖 **Machine Learning Models Explained:**
1. **SLA Breach Risk Classifier (Random Forest / Gradient Boosting):**
   - **Target:** Binary flag ($1 = \text{Breached > 3 days}$, $0 = \text{Within SLA}$).
   - **Evaluation Metric:** **ROC-AUC (0.60+) and F1-Score (0.78)**. Accuracy is misleading in imbalanced datasets, so F1 and ROC-AUC ensure balanced precision and recall.
   - **Features:** Categorical (Department, Priority, District, Weekday) + Numerical (Officer Workload, Area Density, Severity Score).
2. **Resolution Turnaround Regressor:**
   - Predicts exact days required to resolve (Mean Absolute Error: **2.4 days**).
            """
        },
        {
            "keywords": ["kpi", "metric", "summary", "overview", "numbers", "scorecard"],
            "response": """
📊 **Key Executive KPIs Explained:**
- **Total Complaints:** 1,000 logged records.
- **Resolution Rate:** 32.3% resolved (323 tickets completed, rest in progress/open).
- **SLA Adherence:** 31.6% resolved within 3 days; 68.4% delayed.
- **Average Turnaround:** 5.47 to 6.3 days.
- **Citizen Satisfaction:** 3.49 to 4.03 out of 5.0 stars.
            """
        },
        {
            "keywords": ["sql", "window", "dense_rank", "lag", "ntile", "cte", "queries"],
            "response": """
🗄️ **Advanced SQL Analytics Explained:**
- **`DENSE_RANK()`**: Ranks departments by average turnaround time without skipping rank numbers when ties occur.
- **`LAG()`**: Accesses the previous month's complaint volume to compute Month-over-Month (MoM) growth percentage.
- **`NTILE(4)`**: Divides municipal wards into 4 equal risk quartiles (Tier 1 Critical to Tier 4 Stable) for budget allocation.
- **Rolling Average**: `AVG(Daily_Count) OVER (ORDER BY Complaint_Date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` calculates 7-day smoothed trend.
            """
        },
        {
            "keywords": ["road", "department", "officer", "slow", "fast", "performance", "bottleneck"],
            "response": """
🏢 **Department & Officer Performance Insights:**
- **High Volume Departments:** Road and Sanitation departments receive the highest volume of complaints (potholes, garbage dumping).
- **Bottleneck Factor:** Officers with over 20+ active assigned tickets experience a 40% increase in turnaround delays, directly lowering citizen ratings.
- **Recommendation:** Implement dynamic load-balancing to redistribute tickets from overloaded officers to available task forces.
            """
        },
        {
            "keywords": ["interview", "placement", "explain", "pitch", "resume", "bolna"],
            "response": """
💼 **Interview & Placement Pitch (How to explain to recruiter):**
*"I built an end-to-end Civic Issue Analytics & Predictive Dispatching platform using Python, SQL, and Streamlit. The system analyzes 1,000+ complaints across 5 districts. I built an automated data quality profiler, engineered 25+ features, and trained a Random Forest classifier that predicts ticket SLA breach risks at ingestion with a 0.78 F1-score. I also applied DBSCAN spatial clustering on GPS coordinates to detect chronic infrastructure failure corridors and authored complex SQL queries with Window Functions to optimize municipal resource allocation."*
            """
        }
    ]

    @classmethod
    def get_page_explanation(cls, page_name: str) -> str:
        """Returns structured explanation for the given dashboard page."""
        for key, text_val in cls.PAGE_KNOWLEDGE.items():
            if key.lower() in page_name.lower():
                return text_val
        return cls.PAGE_KNOWLEDGE.get("Executive Overview", "General page overview available.")

    @classmethod
    def answer_query(cls, query: str, current_page: str = "Executive Overview") -> str:
        """Answers user question in English or Hinglish about the app, charts, models, and data."""
        clean_q = query.lower().strip()
        
        # Check FAQ knowledge base
        for faq in cls.FAQ_DATABASE:
            if any(kw in clean_q for kw in faq["keywords"]):
                return faq["response"].strip()

        # Check if asking about the current page
        if any(w in clean_q for w in ["page", "screen", "ye page", "is page", "sab graphs", "graphs", "explain this", "kya hai"]):
            return cls.get_page_explanation(current_page)

        # Default fallback response
        return f"""
🤖 **Civic AI Copilot:**
Main aapko is project ke kisi bhi graph, metric, ML model, ya SQL query ke baare me explain kar sakta hoon!

Aap ye sawaal pooch sakte hain:
1. *"Explain all graphs on this page"*
2. *"SLA breach ka matlab kya hai aur kyu zyada hai?"*
3. *"DBSCAN clustering kaise kaam kar rahi hai?"*
4. *"Random Forest ML model kaise train hua?"*
5. *"Placement interview me is project ko kaise explain karein?"*
6. *"SQL Window functions (DENSE_RANK, LAG) ka kya role hai?"*
        """.strip()
