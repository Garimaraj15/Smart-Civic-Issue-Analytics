import pandas as pd
from pathlib import Path

# Project Root
BASE_DIR = Path(__file__).resolve().parent.parent

print("Project Folder:")
print(BASE_DIR)

# Excel File Path
file_path = BASE_DIR / "data" / "raw" / "Smart_Civic_Issue_Analytics_Dataset.xlsx"

print("\nExcel File Path:")
print(file_path)

# Check if file exists
print("\nFile Exists:", file_path.exists())

# Read Excel
df = pd.read_excel(file_path, sheet_name="Complaints")

print("\nDataset Loaded Successfully!")

print(df.head())

# ==========================================
# DATA INSPECTION
# ==========================================

print("\n" + "="*60)
print("DATASET SHAPE")
print("="*60)

print(df.shape)

print("\n" + "="*60)
print("COLUMN NAMES")
print("="*60)

print(df.columns.tolist())

print("\n" + "="*60)
print("DATA TYPES")
print("="*60)

print(df.dtypes)

print("\n" + "="*60)
print("DATASET INFORMATION")
print("="*60)

df.info()

print("\n" + "="*60)
print("STATISTICAL SUMMARY")
print("="*60)

print(df.describe(include="all"))

print("\n" + "="*60)
print("MISSING VALUES")
print("="*60)

print(df.isnull().sum())

print("\n" + "="*60)
print("DUPLICATE ROWS")
print("="*60)

print(df.duplicated().sum())