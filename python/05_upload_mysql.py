import os
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==========================================
# Paths
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = (
    BASE_DIR
    / "data"
    / "feature_engineered"
    / "feature_engineered_civic_complaints.csv"
)

# ==========================================
# Load CSV
# ==========================================

df = pd.read_csv(file_path)

print("Dataset Loaded Successfully!")
print(df.head())

# ==========================================
# Database Connection (MySQL / SQLite Fallback)
# ==========================================

username = os.getenv("MYSQL_USER", "root")
password = os.getenv("MYSQL_PASSWORD", "")
host = os.getenv("MYSQL_HOST", "localhost")
port = os.getenv("MYSQL_PORT", "3306")
database = os.getenv("MYSQL_DATABASE", "smart_civic_analytics")

try:
    password_encoded = quote_plus(password) if password else ""
    mysql_url = f"mysql+mysqlconnector://{username}:{password_encoded}@{host}:{port}/{database}"
    engine = create_engine(mysql_url)
    df.to_sql(name="complaints", con=engine, if_exists="replace", index=False)
    print("\n=========================================")
    print("DATA UPLOADED SUCCESSFULLY TO MYSQL!")
    print("=========================================")
except Exception as e:
    print(f"\n[Notice] MySQL connection skipped ({e}). Seeding to local SQLite database...")
    sqlite_path = BASE_DIR / "data" / "database" / "civic_analytics.db"
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
    df.to_sql(name="complaints", con=sqlite_engine, if_exists="replace", index=False)
    print("DATA UPLOADED SUCCESSFULLY TO SQLITE!")

print(f"Total Rows Processed : {len(df)}")