-- =============================================================================
-- SMART CIVIC ISSUE ANALYTICS - ADVANCED SQL ANALYTICS SHOWCASE
-- Designed for Placement, Interview & Portfolio Evaluations
-- Covers: Window Functions, CTEs, Rolling Aggregations, MoM Trends, NTILEs
-- =============================================================================

USE smart_civic_analytics;

-- -----------------------------------------------------------------------------
-- SCENARIO 1: Department Turnaround Ranking with DENSE_RANK()
-- Business Purpose: Identify the fastest and slowest performing municipal teams.
-- -----------------------------------------------------------------------------
SELECT
    Department,
    COUNT(*) AS Total_Tickets,
    SUM(CASE WHEN Status = 'Resolved' THEN 1 ELSE 0 END) AS Resolved_Count,
    ROUND(AVG(Resolution_Time_Days), 2) AS Avg_Turnaround_Days,
    DENSE_RANK() OVER (ORDER BY AVG(Resolution_Time_Days) ASC) AS Turnaround_Speed_Rank
FROM complaints
WHERE Resolution_Time_Days IS NOT NULL
GROUP BY Department
ORDER BY Turnaround_Speed_Rank;


-- -----------------------------------------------------------------------------
-- SCENARIO 2: 7-Day Rolling Moving Average of Complaint Velocity
-- Business Purpose: Smooth out daily fluctuations to detect civic surge trends.
-- -----------------------------------------------------------------------------
WITH Daily_Trend AS (
    SELECT
        Complaint_Date,
        COUNT(*) AS Daily_Incidents
    FROM complaints
    GROUP BY Complaint_Date
)
SELECT
    Complaint_Date,
    Daily_Incidents,
    ROUND(AVG(Daily_Incidents) OVER (
        ORDER BY Complaint_Date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS Moving_7Day_Average,
    SUM(Daily_Incidents) OVER (ORDER BY Complaint_Date) AS Cumulative_Complaints_YTD
FROM Daily_Trend
ORDER BY Complaint_Date;


-- -----------------------------------------------------------------------------
-- SCENARIO 3: Month-over-Month (MoM) Growth Analysis using LAG()
-- Business Purpose: Track growth velocity in complaints across municipal quarters.
-- -----------------------------------------------------------------------------
WITH Monthly_Stats AS (
    SELECT
        Year,
        Month_Num,
        Month,
        COUNT(*) AS Monthly_Volume
    FROM complaints
    GROUP BY Year, Month_Num, Month
)
SELECT
    Year,
    Month,
    Monthly_Volume,
    LAG(Monthly_Volume, 1) OVER (ORDER BY Year, Month_Num) AS Prior_Month_Volume,
    ROUND(
        (Monthly_Volume - LAG(Monthly_Volume, 1) OVER (ORDER BY Year, Month_Num)) * 100.0 /
        NULLIF(LAG(Monthly_Volume, 1) OVER (ORDER BY Year, Month_Num), 0),
        2
    ) AS MoM_Growth_Rate_Pct
FROM Monthly_Stats
ORDER BY Year, Month_Num;


-- -----------------------------------------------------------------------------
-- SCENARIO 4: Ward Risk Segmentation using NTILE(4) Quartiles
-- Business Purpose: Identify the top 25% highest-risk wards for budget intervention.
-- -----------------------------------------------------------------------------
WITH Ward_Risk_Agg AS (
    SELECT
        District,
        Ward,
        COUNT(*) AS Total_Incidents,
        SUM(CASE WHEN Priority = 'High' THEN 1 ELSE 0 END) AS High_Priority_Tickets,
        SUM(CASE WHEN SLA_Status = 'SLA Breached' THEN 1 ELSE 0 END) AS Breached_Tickets,
        ROUND(SUM(CASE WHEN SLA_Status = 'SLA Breached' THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2) AS Breach_Rate_Pct,
        ROUND(AVG(Citizen_Rating), 2) AS Avg_Satisfaction
    FROM complaints
    GROUP BY District, Ward
)
SELECT
    District,
    Ward,
    Total_Incidents,
    Breach_Rate_Pct,
    Avg_Satisfaction,
    NTILE(4) OVER (ORDER BY Breach_Rate_Pct DESC) AS SLA_Risk_Quartile,
    CASE 
        WHEN NTILE(4) OVER (ORDER BY Breach_Rate_Pct DESC) = 1 THEN 'Tier 1 - Critical Risk'
        WHEN NTILE(4) OVER (ORDER BY Breach_Rate_Pct DESC) = 2 THEN 'Tier 2 - Elevated Risk'
        WHEN NTILE(4) OVER (ORDER BY Breach_Rate_Pct DESC) = 3 THEN 'Tier 3 - Moderate'
        ELSE 'Tier 4 - Stable'
    END AS Intervention_Category
FROM Ward_Risk_Agg
ORDER BY Breach_Rate_Pct DESC;


-- -----------------------------------------------------------------------------
-- SCENARIO 5: Department & Officer Workload vs Citizen Trust Matrix
-- Business Purpose: Evaluate if officer overload leads directly to lower satisfaction.
-- -----------------------------------------------------------------------------
WITH Officer_Metrics AS (
    SELECT
        Assigned_Officer,
        Department,
        COUNT(*) AS Assigned_Volume,
        ROUND(AVG(Resolution_Time_Days), 2) AS Avg_Turnaround,
        ROUND(AVG(Citizen_Rating), 2) AS Officer_Avg_Rating,
        ROUND(SUM(CASE WHEN SLA_Status = 'Within SLA' THEN 1.0 ELSE 0 END) / 
              NULLIF(SUM(CASE WHEN SLA_Status IN ('Within SLA', 'SLA Breached') THEN 1 ELSE 0 END), 0) * 100, 2) AS SLA_Adherence_Pct
    FROM complaints
    GROUP BY Assigned_Officer, Department
)
SELECT
    Assigned_Officer,
    Department,
    Assigned_Volume,
    Avg_Turnaround,
    Officer_Avg_Rating,
    SLA_Adherence_Pct,
    DENSE_RANK() OVER (PARTITION BY Department ORDER BY Officer_Avg_Rating DESC) AS Dept_Satisfaction_Rank
FROM Officer_Metrics
ORDER BY Department, Dept_Satisfaction_Rank;


-- -----------------------------------------------------------------------------
-- SCENARIO 6: Repeat Infrastructure Failure Analysis
-- Business Purpose: Identify areas suffering from recurring issues (>5 of same type).
-- -----------------------------------------------------------------------------
SELECT
    Area,
    Issue_Type,
    Department,
    COUNT(*) AS Recurrence_Count,
    MIN(Complaint_Date) AS Earliest_Incident,
    MAX(Complaint_Date) AS Latest_Incident,
    ROUND(AVG(Citizen_Rating), 2) AS Avg_Citizen_Rating
FROM complaints
GROUP BY Area, Issue_Type, Department
HAVING COUNT(*) >= 5
ORDER BY Recurrence_Count DESC;
