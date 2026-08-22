"""
Resolution Time Estimator.
Supervised Regression pipeline predicting expected resolution time (in days)
based on issue type, department, workload, and severity.
"""

from typing import Dict, Any, Tuple
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.core.config import RESOLUTION_MODEL_PATH
from src.core.logger import get_logger

logger = get_logger("ResolutionEstimator")


class ResolutionEstimator:
    """Predicts resolution duration in days for civic issues."""

    CAT_FEATURES = ["District", "Issue_Type", "Department", "Priority", "Weekday"]
    NUM_FEATURES = [
        "Complaint_Severity_Score",
        "Officer_Workload_Count",
        "Area_Complaint_Density",
        "Month_Num",
    ]

    def __init__(self):
        self.model: Pipeline = None
        self.metrics: Dict[str, Any] = {}

    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Filters valid resolution time records."""
        valid_df = df[
            df["Resolution_Time_Days"].notna() & (df["Resolution_Time_Days"] >= 0)
        ].copy()
        X = valid_df[self.CAT_FEATURES + self.NUM_FEATURES]
        y = valid_df["Resolution_Time_Days"].astype(float)
        return X, y

    def train_and_evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Trains regression models and selects best performer."""
        logger.info("Training Resolution Duration Regression models...")
        X, y = self.prepare_data(df)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42
        )

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    self.CAT_FEATURES,
                ),
                ("num", StandardScaler(), self.NUM_FEATURES),
            ]
        )

        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                (
                    "regressor",
                    RandomForestRegressor(
                        n_estimators=100, max_depth=5, random_state=42
                    ),
                ),
            ]
        )

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        self.model = pipeline
        self.metrics = {
            "mae": round(float(mae), 3),
            "rmse": round(float(rmse), 3),
            "r2_score": round(float(r2), 3),
            "mean_actual_days": round(float(y.mean()), 2),
            "median_actual_days": round(float(y.median()), 2),
        }

        self.save()
        logger.info(
            f"Resolution Estimator Saved! MAE: {self.metrics['mae']} days | RMSE: {self.metrics['rmse']} days"
        )
        return self.metrics

    def predict_days(self, complaint_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Predicts estimated resolution days for a new ticket."""
        if self.model is None:
            self.load()

        df_input = pd.DataFrame([complaint_dict])
        est_days = float(self.model.predict(df_input)[0])
        est_days = max(0.5, round(est_days, 1))

        return {
            "estimated_resolution_days": est_days,
            "sla_limit_days": 3,
            "expected_sla_breach": est_days > 3.0,
        }

    def save(self, path=RESOLUTION_MODEL_PATH):
        """Saves regression model artifact."""
        joblib.dump({"model": self.model, "metrics": self.metrics}, path)

    def load(self, path=RESOLUTION_MODEL_PATH):
        """Loads regression model artifact."""
        if not path.exists():
            raise FileNotFoundError(f"Model file not found at: {path}")
        data = joblib.load(path)
        self.model = data["model"]
        self.metrics = data["metrics"]
        return self
