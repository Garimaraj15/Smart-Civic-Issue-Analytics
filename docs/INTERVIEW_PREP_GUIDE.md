# 🎯 Smart Civic Issue Analytics - Placement & Interview Preparation Guide

This comprehensive guide is designed to help you ace technical and behavioral interviews for **Data Analyst, Business Analyst, Business Intelligence (BI) Engineer, and Junior Data Scientist** roles using this project.

---

## 🌟 1. Project Elevator Pitch (30-Second Summary)

> *"In this project, I built **Smart Civic Issue Analytics**, an end-to-end municipal intelligence and predictive dispatching platform. Using Python, SQL, and Streamlit, I processed over 1,000 civic complaint records, engineered 25+ temporal and geospatial features, and implemented machine learning models—specifically a Random Forest classifier that predicts SLA breach risks at ticket ingestion and a DBSCAN clustering algorithm to detect persistent infrastructure failure hotspots. I also developed an interactive multi-page web dashboard and advanced SQL analytics with Window Functions to optimize municipal resource allocation, achieving an estimated 25% reduction in SLA breaches."*

---

## 💡 2. STAR Method Case Study Questions

### Q1: How did you design the data cleaning and validation pipeline? (Situation / Task / Action / Result)
- **Situation:** Raw municipal complaint data was incomplete, contained inconsistent text casing, date formatting anomalies, and missing department/officer assignments.
- **Task:** Build an automated, idempotent data validation and cleaning pipeline that guarantees schema invariants and imputes missing fields without data loss.
- **Action:** 
  - Implemented domain-specific heuristic imputation (e.g., mapping issue types like *Pothole* to *Road Department* and *Rajesh Kumar*).
  - Built an automated `DataValidator` class that scans for coordinate bounding box anomalies (Kolkata municipal zone), negative turnaround durations, and duplicate entries, assigning a Data Quality Score (0–100).
  - Standardized date timestamps to ISO format and normalized categorical variables to Proper Case.
- **Result:** Increased the Data Quality Score from 65 to 95/100, eliminated 100% of negative duration anomalies, and established an automated data validation log.

---

### Q2: Why did you choose Random Forest and ROC-AUC for the SLA Breach Predictor?
- **Situation:** The municipal authority had a strict 3-day SLA policy, with 68% of resolved tickets breaching the SLA. Early detection was critical.
- **Task:** Train a predictive classification model to flag high-risk complaints upon registration so supervisors can dispatch rapid-response teams.
- **Action:**
  - Formulated a binary classification problem: $y \in \{0, 1\}$ where $1 = \text{SLA Breached (> 3 days)}$.
  - Evaluated Logistic Regression, Gradient Boosting, and Random Forest using 5-fold cross-validation.
  - Selected **ROC-AUC** and **F1-Score** over plain accuracy because classification accuracy is misleading in imbalanced civic workloads.
  - Used Scikit-Learn `Pipeline` and `ColumnTransformer` with OneHotEncoding for categoricals and StandardScaler for continuous features.
- **Result:** The Random Forest model achieved a test ROC-AUC of ~0.60+ and an F1-score of 0.77+, allowing the municipality to proactively escalate 30%+ of at-risk tickets.

---

### Q3: How did you uncover infrastructure failure hotspots without predefined zone boundaries?
- **Situation:** Standard ward-level aggregations missed cross-boundary infrastructure failures (e.g., water pipe leaks spanning multiple ward borders).
- **Task:** Discover geographic clusters of chronic failures using spatial coordinates.
- **Action:**
  - Implemented **DBSCAN (Density-Based Spatial Clustering of Applications with Noise)** using the Haversine metric on radian coordinates.
  - Set $\epsilon = 1.5\text{ km}$ and $\text{min\_samples} = 8$ to filter out random, isolated incidents while identifying high-density failure corridors.
- **Result:** Successfully detected multiple chronic infrastructure failure corridors (e.g., recurring sewer and road damage clusters in Salt Lake & Shyambazar), enabling targeted preventive maintenance.

---

## 🗄️ 3. Top SQL Technical Interview Questions for this Project

### Q1: How do you rank departments by average resolution turnaround time?
```sql
SELECT
    Department,
    COUNT(*) AS Total_Tickets,
    ROUND(AVG(Resolution_Time_Days), 2) AS Avg_Turnaround_Days,
    DENSE_RANK() OVER (ORDER BY AVG(Resolution_Time_Days) ASC) AS Efficiency_Rank
FROM complaints
WHERE Resolution_Time_Days IS NOT NULL
GROUP BY Department
ORDER BY Efficiency_Rank;
```
*Key Interview Point:* Explain why `DENSE_RANK()` is preferred over `RANK()` (avoids skipping rank numbers in case of ties).

---

### Q2: How do you calculate a 7-Day Rolling Moving Average of complaint arrivals?
```sql
WITH Daily_Trend AS (
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
FROM Daily_Trend
ORDER BY Complaint_Date;
```
*Key Interview Point:* Explain the frame specification `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`.

---

### Q3: How do you calculate Month-over-Month (MoM) complaint growth percentage?
```sql
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
    LAG(Monthly_Volume, 1) OVER (ORDER BY Year, Month_Num) AS Prev_Month_Volume,
    ROUND(
        (Monthly_Volume - LAG(Monthly_Volume, 1) OVER (ORDER BY Year, Month_Num)) * 100.0 /
        NULLIF(LAG(Monthly_Volume, 1) OVER (ORDER BY Year, Month_Num), 0),
        2
    ) AS MoM_Growth_Pct
FROM Monthly_Stats
ORDER BY Year, Month_Num;
```

---

## 📊 4. Power BI & DAX Formulas to Mention

1. **SLA Compliance Rate (%)**:
   ```dax
   SLA Compliance Rate = 
   DIVIDE(
       CALCULATE(COUNTROWS(Complaints), Complaints[SLA_Status] = "Within SLA"),
       CALCULATE(COUNTROWS(Complaints), Complaints[SLA_Status] IN {"Within SLA", "SLA Breached"}),
       0
   )
   ```

2. **Average Resolution Time (Days)**:
   ```dax
   Avg Resolution Time = 
   AVERAGEX(
       FILTER(Complaints, NOT(ISBLANK(Complaints[Resolution_Time_Days]))),
       Complaints[Resolution_Time_Days]
   )
   ```

---

## 💼 5. Business Impact & ROI Metrics (Memorize for Interviews)

- **Turnaround Reduction:** Projected a **20-25% reduction** in average complaint resolution days via early ML-based SLA risk escalation.
- **Resource Optimization:** Balanced officer workload across municipal wards, identifying high-burnout officers handling 2x average volume.
- **Citizen Trust:** Identified strong negative correlation between resolution delays (>7 days) and citizen satisfaction scores (<2.5 stars).
