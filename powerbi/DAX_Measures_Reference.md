# 📊 Power BI DAX Measures & Data Model Reference

This reference documents the key DAX measures, calculated columns, and data modeling patterns used in the **Smart Civic Issue Analytics** Power BI report (`powerbi/complaints.pbix`).

---

## 📐 1. Core DAX Measures

### Measure 1: Total Complaints
```dax
Total Complaints = COUNTROWS(Complaints)
```

### Measure 2: Resolved Complaints
```dax
Resolved Complaints = 
CALCULATE(
    COUNTROWS(Complaints),
    Complaints[Status] = "Resolved"
)
```

### Measure 3: Resolution Rate (%)
```dax
Resolution Rate = 
DIVIDE(
    [Resolved Complaints],
    [Total Complaints],
    0
)
```

### Measure 4: SLA Compliance Rate (%)
```dax
SLA Compliance Rate = 
VAR ValidSLACount = CALCULATE(COUNTROWS(Complaints), Complaints[SLA_Status] IN {"Within SLA", "SLA Breached"})
VAR WithinSLACount = CALCULATE(COUNTROWS(Complaints), Complaints[SLA_Status] = "Within SLA")
RETURN
DIVIDE(WithinSLACount, ValidSLACount, 0)
```

### Measure 5: Average Resolution Turnaround Time (Days)
```dax
Avg Resolution Time = 
AVERAGEX(
    FILTER(Complaints, NOT(ISBLANK(Complaints[Resolution_Time_Days]))),
    Complaints[Resolution_Time_Days]
)
```

### Measure 6: Average Citizen Rating
```dax
Avg Citizen Rating = 
AVERAGEX(
    FILTER(Complaints, NOT(ISBLANK(Complaints[Citizen_Rating]))),
    Complaints[Citizen_Rating]
)
```

### Measure 7: High Priority Incident Ratio (%)
```dax
High Priority % = 
DIVIDE(
    CALCULATE(COUNTROWS(Complaints), Complaints[Priority] = "High"),
    [Total Complaints],
    0
)
```

---

## 🗂️ 2. Star Schema Relationships
- **Fact Table:** `Complaints` (Key: `Complaint_ID`)
- **Dimension 1:** `Dim_Geography` (Key: `Area`, connected 1-to-many to `Complaints[Area]`)
- **Dimension 2:** `Dim_Department` (Key: `Department`, connected 1-to-many to `Complaints[Department]`)
- **Dimension 3:** `Dim_Date` (Key: `Date`, connected 1-to-many to `Complaints[Complaint_Date]`)
