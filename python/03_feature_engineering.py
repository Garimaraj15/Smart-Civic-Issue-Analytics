# ==========================================
# SMART CIVIC ISSUE ANALYTICS PIPELINE
# Module 3 : Feature Engineering
# ==========================================

import pandas as pd
from pathlib import Path

# ------------------------------------------
# Load Dataset
# ------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "data" / "cleaned" / "cleaned_civic_complaints.csv"

df = pd.read_csv(file_path)

# Convert Date Columns
df["Complaint_Date"] = pd.to_datetime(df["Complaint_Date"])

df["Resolution_Date"] = pd.to_datetime(df["Resolution_Date"])

# ------------------------------------------
# Basic Cleaning
# ------------------------------------------

df = df.drop_duplicates()

department_mapping = {
    "Pothole": "Road Department",
    "Road Damage": "Road Department",
    "Water Leakage": "Water Department",
    "Street Light Fault": "Electricity Department",
    "Garbage Overflow": "Sanitation Department",
    "Illegal Dumping": "Sanitation Department",
    "Sewer Problem": "Sewer Department",
    "Drain Blockage": "Sewer Department",
    "Park Maintenance": "Parks Department",
    "Traffic Signal Fault": "Traffic Department"
}

df["Department"] = df["Department"].fillna(df["Issue_Type"].map(department_mapping))

officer_mapping = {
    "Road Department": "Rajesh Kumar",
    "Water Department": "Priya Sharma",
    "Electricity Department": "Amit Singh",
    "Sanitation Department": "Neha Gupta",
    "Sewer Department": "Vikram Das",
    "Parks Department": "Arjun Roy",
    "Traffic Department": "Rahul Sen"
}

df["Assigned_Officer"] = df["Assigned_Officer"].fillna(df["Department"].map(officer_mapping))

df["Remarks"] = df["Remarks"].fillna("No Remarks")

df["Complaint_Date"] = pd.to_datetime(df["Complaint_Date"], format="mixed", dayfirst=True)
df["Resolution_Date"] = pd.to_datetime(df["Resolution_Date"], format="mixed", dayfirst=True, errors="coerce")

text_columns = [
    "District",
    "Ward",
    "Area",
    "Issue_Type",
    "Department",
    "Priority",
    "Status",
    "Assigned_Officer",
    "Remarks"
]

for col in text_columns:
    df[col] = df[col].astype(str).str.strip().str.title()

print("Dataset Ready for Feature Engineering")

# ==========================================
# FEATURE 1 : Resolution Time
# ==========================================

print("\n" + "="*60)
print("FEATURE 1 : Resolution Time")
print("="*60)

df["Resolution_Time_Days"] = (
    df["Resolution_Date"] - df["Complaint_Date"]
).dt.days

print("\nSample Resolution Time:")

# ------------------------------------------
# Fix Invalid Resolution Time
# ------------------------------------------

df.loc[df["Resolution_Time_Days"] < 0, "Resolution_Time_Days"] = pd.NA

print("\nNegative Resolution Time Fixed!")

print("\nRemaining Invalid Records:")

print((df["Resolution_Time_Days"] < 0).sum())

print(
    df[
        [
            "Complaint_Date",
            "Resolution_Date",
            "Resolution_Time_Days"
        ]
    ].head(10)
)

# ==========================================
# DATA VALIDATION
# ==========================================

print("\n" + "="*60)
print("DATA VALIDATION")
print("="*60)

# Find invalid resolution times
invalid_resolution = df[df["Resolution_Time_Days"] < 0]

print(f"\nInvalid Resolution Records : {len(invalid_resolution)}")

if len(invalid_resolution) > 0:
    print("\nSample Invalid Records")
    print(
        invalid_resolution[
            [
                "Complaint_ID",
                "Complaint_Date",
                "Resolution_Date",
                "Resolution_Time_Days"
            ]
        ].head()
    )


# ==========================================
# FEATURE 2 : Complaint Severity Score
# ==========================================

print("\n" + "="*60)
print("FEATURE 2 : Complaint Severity Score")
print("="*60)

severity_mapping = {
    "High": 3,
    "Medium": 2,
    "Low": 1
}

df["Complaint_Severity_Score"] = df["Priority"].map(severity_mapping)

print("\nSample Severity Scores")

print(
    df[
        [
            "Priority",
            "Complaint_Severity_Score"
        ]
    ].head(10)
)

# ==========================================
# FEATURE 3 : Month
# ==========================================

print("\n" + "="*60)
print("FEATURE 3 : Month")
print("="*60)

df["Month"] = df["Complaint_Date"].dt.month_name()

print(df[
    [
        "Complaint_Date",
        "Month"
    ]
].head(10))

# ==========================================
# FEATURE 4 : Year
# ==========================================

print("\n" + "="*60)
print("FEATURE 4 : Year")
print("="*60)

df["Year"] = df["Complaint_Date"].dt.year

print(df[
    [
        "Complaint_Date",
        "Year"
    ]
].head(10))

# ==========================================
# FEATURE 5 : Weekday
# ==========================================

print("\n" + "="*60)
print("FEATURE 5 : Weekday")
print("="*60)

df["Weekday"] = df["Complaint_Date"].dt.day_name()

print(df[
    [
        "Complaint_Date",
        "Weekday"
    ]
].head(10))

# ==========================================
# FEATURE 6 : Quarter
# ==========================================

print("\n" + "="*60)
print("FEATURE 6 : Quarter")
print("="*60)

df["Quarter"] = "Q" + df["Complaint_Date"].dt.quarter.astype(str)

print(df[
    [
        "Complaint_Date",
        "Quarter"
    ]
].head(10))

# ==========================================
# FEATURE 7 : Resolution Category
# ==========================================

print("\n" + "="*60)
print("FEATURE 7 : Resolution Category")
print("="*60)

def resolution_category(days):
    if pd.isna(days):
        return "Pending"
    elif days <= 3:
        return "Fast"
    elif days <= 7:
        return "Medium"
    else:
        return "Slow"

df["Resolution_Category"] = df["Resolution_Time_Days"].apply(resolution_category)

print(df[
    [
        "Resolution_Time_Days",
        "Resolution_Category"
    ]
].head(10))

# ==========================================
# FEATURE 8 : SLA Status
# ==========================================

print("\n" + "="*60)
print("FEATURE 8 : SLA Status")
print("="*60)

def sla_status(days):
    if pd.isna(days):
        return "Pending"
    elif days <= 3:
        return "Within SLA"
    else:
        return "SLA Breached"

df["SLA_Status"] = df["Resolution_Time_Days"].apply(sla_status)

print(df[
    [
        "Resolution_Time_Days",
        "SLA_Status"
    ]
].head(10))

# ==========================================
# FEATURE 9 : Complaint Age
# ==========================================

print("\n" + "="*60)
print("FEATURE 9 : Complaint Age")
print("="*60)

today = pd.Timestamp.today()

df["Complaint_Age_Days"] = (
    today - df["Complaint_Date"]
).dt.days

print(df[
    [
        "Complaint_Date",
        "Complaint_Age_Days"
    ]
].head())

# ==========================================
# FEATURE 10 : Is Resolved
# ==========================================

print("\n" + "="*60)
print("FEATURE 10 : Is Resolved")
print("="*60)

df["Is_Resolved"] = df["Status"].apply(
    lambda x: "Yes" if x == "Resolved" else "No"
)

print(df[
    [
        "Status",
        "Is_Resolved"
    ]
].head())

# ==========================================
# EXPORT FEATURE ENGINEERED DATASET
# ==========================================

output_folder = BASE_DIR / "data" / "feature_engineered"
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "feature_engineered_civic_complaints.csv"

df.to_csv(output_file, index=False)

print("\n" + "="*60)
print("FEATURE ENGINEERED DATASET SAVED")
print("="*60)
print(output_file)