"""
Configuration module for Smart Civic Issue Analytics.
Manages file paths, database connections, and global constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEANED_DATA_DIR = DATA_DIR / "cleaned"
FEATURE_DATA_DIR = DATA_DIR / "feature_engineered"
DATABASE_DIR = DATA_DIR / "database"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure runtime directories exist
for directory in [DATA_DIR, RAW_DATA_DIR, CLEANED_DATA_DIR, FEATURE_DATA_DIR, DATABASE_DIR, MODELS_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File Paths
RAW_EXCEL_PATH = RAW_DATA_DIR / "Smart_Civic_Issue_Analytics_Dataset.xlsx"
CLEANED_CSV_PATH = CLEANED_DATA_DIR / "cleaned_civic_complaints.csv"
FEATURE_CSV_PATH = FEATURE_DATA_DIR / "feature_engineered_civic_complaints.csv"
SQLITE_DB_PATH = DATABASE_DIR / "civic_analytics.db"
SLA_MODEL_PATH = MODELS_DIR / "sla_risk_model.joblib"
RESOLUTION_MODEL_PATH = MODELS_DIR / "resolution_estimator.joblib"
DATA_AUDIT_REPORT_PATH = REPORTS_DIR / "data_quality_report.json"

# Database Configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "smart_civic_analytics")

# Domain Mappings
DEPARTMENT_MAPPING = {
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

OFFICER_MAPPING = {
    "Road Department": "Rajesh Kumar",
    "Water Department": "Priya Sharma",
    "Electricity Department": "Amit Singh",
    "Sanitation Department": "Neha Gupta",
    "Sewer Department": "Vikram Das",
    "Parks Department": "Arjun Roy",
    "Traffic Department": "Rahul Sen"
}

SEVERITY_MAPPING = {
    "High": 3,
    "Medium": 2,
    "Low": 1
}

SLA_THRESHOLD_DAYS = 3
