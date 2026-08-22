"""
Data loader module for civic complaint datasets.
Handles loading raw Excel/CSV spreadsheets and cached processed files.
"""

from pathlib import Path
from typing import Optional
import pandas as pd
from src.core.config import RAW_EXCEL_PATH, CLEANED_CSV_PATH, FEATURE_CSV_PATH
from src.core.logger import get_logger

logger = get_logger("DataLoader")


def load_raw_data(file_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Loads raw Excel dataset into a pandas DataFrame.
    """
    target_path = file_path or RAW_EXCEL_PATH
    if not target_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at: {target_path}")

    logger.info(f"Loading raw data from: {target_path}")
    if target_path.suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(target_path, sheet_name="Complaints")
    else:
        df = pd.read_csv(target_path)

    logger.info(f"Loaded raw dataset with shape: {df.shape}")
    return df


def load_cleaned_data(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Loads cleaned complaints dataset."""
    target_path = file_path or CLEANED_CSV_PATH
    if not target_path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at: {target_path}")
    return pd.read_csv(target_path)


def load_feature_data(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Loads feature-engineered complaints dataset."""
    target_path = file_path or FEATURE_CSV_PATH
    if not target_path.exists():
        raise FileNotFoundError(f"Feature dataset not found at: {target_path}")
    return pd.read_csv(target_path)
