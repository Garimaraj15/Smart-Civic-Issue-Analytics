"""
Page 6: Interactive SQL Analytics Studio & Interview Query Lab.
"""

import streamlit as st
import pandas as pd
from sqlalchemy import text
from dashboard.utils import apply_custom_css, render_ai_copilot_sidebar
from src.core.db import get_engine

st.set_page_config(page_title="SQL Analytics Lab - Civic Analytics", page_icon="🗄️", layout="wide")
apply_custom_css()

st.title("🗄️ SQL Analytics Studio & Placement Query Showcase")
st.markdown("Execute advanced SQL queries (Window Functions, CTEs, Rolling Averages, Partitions) against the analytical database in real time.")

# Render AI Copilot in Sidebar
render_ai_copilot_sidebar("SQL Analytics Lab")

engine = get_engine(use_mysql=False)

PRESET_QUERIES = {
    "1. [Window Function] Department Resolution Ranking (DENSE_RANK)": """-- Rank departments by average resolution speed using DENSE_RANK()
SELECT
    Department,
    COUNT(*) AS Total_Tickets,
    ROUND(AVG(Resolution_Time_Days), 2) AS Avg_Turnaround_Days,
    DENSE_RANK() OVER (ORDER BY AVG(Resolution_Time_Days) ASC) AS Efficiency_Rank
FROM complaints
WHERE Resolution_Time_Days IS NOT NULL
GROUP BY Department
ORDER BY Efficiency_Rank;""",

    "2. [Window Function] 7-Day Rolling Moving Average of Complaints": """-- Calculate 7-day rolling complaint velocity
WITH Daily_Velocity AS (
    SELECT
        Complaint_Date,
        COUNT(*) AS Daily_Count
    FROM complaints
    GROUP BY Complaint_Date
)
SELECT
    Complaint_Date,
    Daily_Count,
    ROUND(AVG(Daily_Count) OVER (
        ORDER BY Complaint_Date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS Rolling_7Day_Avg
FROM Daily_Velocity
ORDER BY Complaint_Date;""",

    "3. [CTE & Window] SLA Breach Rate by Ward (NTILE Quartiles)": """-- Categorize Wards into 4 Risk Quartiles using NTILE()
WITH Ward_SLA AS (
    SELECT
        Ward,
        District,
        COUNT(*) AS Total_Tickets,
        SUM(CASE WHEN SLA_Status = 'SLA Breached' THEN 1 ELSE 0 END) AS Breached_Tickets,
        ROUND(SUM(CASE WHEN SLA_Status = 'SLA Breached' THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2) AS Breach_Rate_Pct
    FROM complaints
    GROUP BY Ward, District
)
SELECT
    Ward,
    District,
    Total_Tickets,
    Breached_Tickets,
    Breach_Rate_Pct,
    NTILE(4) OVER (ORDER BY Breach_Rate_Pct DESC) AS Risk_Quartile_Tier
FROM Ward_SLA
ORDER BY Breach_Rate_Pct DESC;""",

    "4. [Window LAG] Month-over-Month (MoM) Complaint Growth": """-- Calculate Month-over-Month volume changes using LAG()
WITH Monthly_Agg AS (
    SELECT
        Year,
        Month_Num,
        Month,
        COUNT(*) AS Monthly_Complaints
    FROM complaints
    GROUP BY Year, Month_Num, Month
)
SELECT
    Year,
    Month,
    Monthly_Complaints,
    LAG(Monthly_Complaints, 1) OVER (ORDER BY Year, Month_Num) AS Prev_Month_Complaints,
    ROUND(
        (Monthly_Complaints - LAG(Monthly_Complaints, 1) OVER (ORDER BY Year, Month_Num)) * 100.0 /
        LAG(Monthly_Complaints, 1) OVER (ORDER BY Year, Month_Num),
    2) AS MoM_Growth_Pct
FROM Monthly_Agg
ORDER BY Year, Month_Num;""",

    "5. [CTE] Officer Workload & Rating Matrix": """-- Officer Performance Scorecard
SELECT
    Assigned_Officer,
    Department,
    COUNT(*) AS Assigned_Complaints,
    SUM(CASE WHEN Status = 'Resolved' THEN 1 ELSE 0 END) AS Resolved_Complaints,
    ROUND(AVG(Resolution_Time_Days), 2) AS Avg_Turnaround_Days,
    ROUND(AVG(Citizen_Rating), 2) AS Avg_Citizen_Rating
FROM complaints
GROUP BY Assigned_Officer, Department
ORDER BY Assigned_Complaints DESC;"""
}

# Preset Selection
st.subheader("💡 Select Placement SQL Query Template")
selected_preset_name = st.selectbox("Choose a query scenario:", list(PRESET_QUERIES.keys()))
default_query = PRESET_QUERIES[selected_preset_name]

# SQL Editor
st.subheader("⚡ Live SQL Editor")
query_text = st.text_area("SQL Query (SQLite / ANSI SQL):", value=default_query, height=220)

col_btn, col_info = st.columns([1, 4])
with col_btn:
    run_btn = st.button("▶️ Execute Query", type="primary", use_container_width=True)

if run_btn or query_text:
    try:
        with engine.connect() as conn:
            result_df = pd.read_sql(text(query_text), conn)
        
        st.success(f"Query executed successfully! Returned **{len(result_df)}** rows.")
        st.dataframe(result_df, use_container_width=True)

        # Download CSV option
        csv_data = result_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Result as CSV",
            data=csv_data,
            file_name="sql_query_result.csv",
            mime="text/csv",
        )
    except Exception as err:
        st.error(f"SQL Execution Error: {err}")
