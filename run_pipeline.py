"""
Master End-to-End Execution Pipeline for Smart Civic Issue Analytics.
Orchestrates: Ingestion -> Quality Audit -> Cleaning -> Feature Engineering -> ML Training -> Database Seeding.
"""

import sys
import time
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src.core.config import (
    RAW_EXCEL_PATH,
    CLEANED_CSV_PATH,
    FEATURE_CSV_PATH,
    SQLITE_DB_PATH,
    DB_TYPE,
)
from src.core.logger import get_logger
from src.core.db import get_engine
from src.data.loader import load_raw_data
from src.data.validator import DataValidator
from src.data.cleaner import DataCleaner
from src.features.engineer import FeatureEngineer
from src.models.sla_predictor import SLAPredictor
from src.models.resolution_estimator import ResolutionEstimator
from src.analytics.kpis import CivicKPIEngine

logger = get_logger("PipelineOrchestrator")


def print_banner():
    banner = """
================================================================================
           SMART CIVIC ISSUE ANALYTICS - END-TO-END PIPELINE v2.0
================================================================================
    """
    print(banner)


def run_pipeline(use_mysql: bool = False):
    start_time = time.time()
    print_banner()

    # Step 1: Ingestion
    logger.info(">>> STEP 1: Ingesting Raw Dataset...")
    raw_df = load_raw_data()
    print(f"    Raw records loaded: {raw_df.shape[0]} rows | {raw_df.shape[1]} columns\n")

    # Step 2: Quality Audit
    logger.info(">>> STEP 2: Running Automated Data Quality & Anomaly Profiling...")
    validator = DataValidator(raw_df)
    audit_report = validator.run_full_validation()
    print(f"    Data Quality Score: {audit_report['data_quality_score']}/100 ({audit_report['status']})\n")

    # Step 3: Cleaning & Imputation
    logger.info(">>> STEP 3: Cleaning & Standardizing Data...")
    cleaner = DataCleaner(raw_df)
    cleaned_df = cleaner.export()
    print(f"    Cleaned records saved: {cleaned_df.shape[0]} rows -> {CLEANED_CSV_PATH}\n")

    # Step 4: Feature Engineering
    logger.info(">>> STEP 4: Engineering 25+ Analytical & ML Features...")
    engineer = FeatureEngineer(cleaned_df)
    feature_df = engineer.export()
    print(f"    Engineered dataset saved: {feature_df.shape[0]} rows | {feature_df.shape[1]} features -> {FEATURE_CSV_PATH}\n")

    # Step 5: Machine Learning Model Training
    logger.info(">>> STEP 5: Training Supervised Machine Learning Models...")
    
    # SLA Predictor
    sla_predictor = SLAPredictor()
    sla_metrics = sla_predictor.train_and_evaluate(feature_df)
    print(f"    [ML Model 1] SLA Breach Classifier ({sla_metrics['best_algorithm']}):")
    print(f"                 ROC-AUC: {sla_metrics['roc_auc']} | Accuracy: {sla_metrics['accuracy']} | F1: {sla_metrics['f1_score']}")

    # Resolution Estimator
    res_estimator = ResolutionEstimator()
    res_metrics = res_estimator.train_and_evaluate(feature_df)
    print(f"    [ML Model 2] Resolution Turnaround Regressor:")
    print(f"                 MAE: {res_metrics['mae']} days | RMSE: {res_metrics['rmse']} days | R2: {res_metrics['r2_score']}\n")

    # Step 6: Database Seeding
    logger.info(f">>> STEP 6: Seeding Database ({'MySQL' if use_mysql else 'SQLite'})...")
    engine = get_engine(use_mysql=use_mysql)
    feature_df.to_sql(name="complaints", con=engine, if_exists="replace", index=False)
    logger.info(f"    Successfully seeded {len(feature_df)} rows to table 'complaints'.\n")

    # Step 7: Executive Summary
    logger.info(">>> STEP 7: Computing Operational Scorecard...")
    kpi_engine = CivicKPIEngine(feature_df)
    summary = kpi_engine.get_executive_summary()
    print("-" * 60)
    print(f"  Total Complaints       : {summary['total_complaints']}")
    print(f"  Resolution Rate        : {summary['resolution_rate_pct']}%")
    print(f"  SLA Compliance Rate    : {summary['sla_compliance_rate_pct']}%")
    print(f"  Avg Turnaround Time    : {summary['avg_turnaround_days']} days")
    print(f"  Avg Citizen Rating     : {summary['avg_citizen_rating']} / 5.0")
    print("-" * 60)

    elapsed = round(time.time() - start_time, 2)
    print(f"\n[SUCCESS] PIPELINE COMPLETED in {elapsed} seconds!")
    print("Run Dashboard: streamlit run dashboard/app.py\n")


if __name__ == "__main__":
    use_mysql_flag = "--mysql" in sys.argv
    run_pipeline(use_mysql=use_mysql_flag)
