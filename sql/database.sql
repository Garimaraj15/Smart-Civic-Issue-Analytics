-- =============================================================================
-- SMART CIVIC ISSUE ANALYTICS - STANDARD DATABASE SCHEMA & QUERIES
-- =============================================================================

CREATE DATABASE IF NOT EXISTS smart_civic_analytics;
USE smart_civic_analytics;

DROP TABLE IF EXISTS complaints;

CREATE TABLE complaints (
    Complaint_ID VARCHAR(20) PRIMARY KEY,
    Complaint_Date DATE,
    District VARCHAR(50),
    Ward VARCHAR(50),
    Area VARCHAR(100),
    Issue_Type VARCHAR(100),
    Department VARCHAR(100),
    Priority VARCHAR(20),
    Status VARCHAR(30),
    Assigned_Officer VARCHAR(100),
    Resolution_Date DATE,
    Citizen_Rating INT,
    Latitude DECIMAL(10,6),
    Longitude DECIMAL(10,6),
    Remarks VARCHAR(255),
    Resolution_Time_Days INT,
    Complaint_Severity_Score INT,
    Month VARCHAR(20),
    Month_Num INT,
    Year INT,
    Weekday VARCHAR(20),
    Is_Weekend INT,
    Quarter VARCHAR(10),
    Day_of_Month INT,
    Resolution_Category VARCHAR(30),
    SLA_Status VARCHAR(30),
    SLA_Breached_Flag INT,
    Complaint_Age_Days INT,
    Is_Resolved VARCHAR(10),
    Officer_Workload_Count INT,
    Area_Complaint_Density INT,
    Civic_Priority_Index DECIMAL(10,2)
);

-- =============================================================================
-- Standard Analytical Queries
-- =============================================================================

-- 1. Total Complaints & Resolution Rate
SELECT 
    COUNT(*) AS Total_Complaints,
    SUM(CASE WHEN Status = 'Resolved' THEN 1 ELSE 0 END) AS Resolved_Complaints,
    ROUND(SUM(CASE WHEN Status = 'Resolved' THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2) AS Resolution_Rate_Pct
FROM complaints;

-- 2. Departmental Breakdown with Average Turnaround
SELECT
    Department,
    COUNT(*) AS Total_Complaints,
    ROUND(AVG(Resolution_Time_Days), 2) AS Avg_Turnaround_Days,
    ROUND(AVG(Citizen_Rating), 2) AS Avg_Rating
FROM complaints
GROUP BY Department
ORDER BY Total_Complaints DESC;

-- 3. SLA Compliance Overview
SELECT
    SLA_Status,
    COUNT(*) AS Total_Complaints,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM complaints), 2) AS Percentage
FROM complaints
GROUP BY SLA_Status;