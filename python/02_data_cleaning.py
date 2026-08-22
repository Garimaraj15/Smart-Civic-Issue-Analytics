# ==========================================
# SMART CIVIC ISSUE ANALYTICS PIPELINE
# Module 2 : Data Cleaning
# ==========================================

import pandas as pd
from pathlib import Path

# ------------------------------------------
# Load Dataset
# ------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "data" / "raw" / "Smart_Civic_Issue_Analytics_Dataset.xlsx"

df = pd.read_excel(file_path, sheet_name="Complaints")

print("="*60)
print("DATA CLEANING STARTED")
print("="*60)

print(f"\nOriginal Shape : {df.shape}")

# ------------------------------------------
# Remove Duplicate Records
# ------------------------------------------

duplicates = df.duplicated().sum()

print(f"\nDuplicate Records Found : {duplicates}")

df = df.drop_duplicates()

print(f"Shape After Removing Duplicates : {df.shape}")

# ------------------------------------------
# Handle Missing Values
# ------------------------------------------

print("\n" + "="*60)
print("HANDLING MISSING VALUES")
print("="*60)

print("\nMissing Values Before Cleaning:")
print(df.isnull().sum())


# Department Mapping
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


# Fill Missing Department
df["Department"] = df["Department"].fillna(
    df["Issue_Type"].map(department_mapping)
)


# Officer Mapping
officer_mapping = {
    "Road Department": "Rajesh Kumar",
    "Water Department": "Priya Sharma",
    "Electricity Department": "Amit Singh",
    "Sanitation Department": "Neha Gupta",
    "Sewer Department": "Vikram Das",
    "Parks Department": "Arjun Roy",
    "Traffic Department": "Rahul Sen"
}


# Fill Missing Officer
df["Assigned_Officer"] = df["Assigned_Officer"].fillna(
    df["Department"].map(officer_mapping)
)


# Fill Missing Remarks
df["Remarks"] = df["Remarks"].fillna("No Remarks")


print("\nMissing Values After Cleaning:")
print(df.isnull().sum())

# ------------------------------------------
# Standardize Date Format
# ------------------------------------------

print("\n" + "="*60)
print("STANDARDIZING DATE FORMAT")
print("="*60)

# Convert Complaint Date
df["Complaint_Date"] = pd.to_datetime(
    df["Complaint_Date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

# Convert Resolution Date
df["Resolution_Date"] = pd.to_datetime(
    df["Resolution_Date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

print("\nData Types After Conversion:")
print(df[["Complaint_Date", "Resolution_Date"]].dtypes)

print("\nInvalid Complaint Dates:")
print(df["Complaint_Date"].isna().sum())

print("\nInvalid Resolution Dates:")
print(df["Resolution_Date"].isna().sum())

# ------------------------------------------
# Text Standardization
# ------------------------------------------

print("\n" + "="*60)
print("TEXT STANDARDIZATION")
print("="*60)

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

for column in text_columns:
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()      # Remove extra spaces
        .str.title()      # Convert to Proper Case
    )

print("\nText Cleaning Completed Successfully!")

print("\nSample Data After Cleaning:")
print(df[text_columns].head())

# ==========================================
# Export Cleaned Dataset
# ==========================================

# ==========================================
# Export Cleaned Dataset
# ==========================================

from pathlib import Path

output_folder = BASE_DIR / "data" / "cleaned"

# Create folder automatically
output_folder.mkdir(parents=True, exist_ok=True)

output_path = output_folder / "cleaned_civic_complaints.csv"

df.to_csv(output_path, index=False)

print("\n" + "="*60)
print("CLEANED DATASET SAVED")
print("="*60)
print(output_path)