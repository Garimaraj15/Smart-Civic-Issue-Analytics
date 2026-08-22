"""
SLA Breach Risk Predictor.
Supervised Machine Learning classification pipeline predicting the probability of an SLA breach (> 3 days)
at the moment a civic complaint is lodged.
"""

from typing import Dict, Any, Tuple
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from src.core.config import SLA_MODEL_PATH
from src.core.logger import get_logger

logger = get_logger("SLAPredictor")


class SLAPredictor:
    """Trains, evaluates, and performs inference for Civic SLA Breach Prediction."""

    CAT_FEATURES = ["District", "Issue_Type", "Department", "Priority", "Weekday"]
    NUM_FEATURES = [
        "Complaint_Severity_Score",
        "Officer_Workload_Count",
        "Area_Complaint_Density",
        "Month_Num",
        "Is_Weekend",
    ]

    def __init__(self):
        self.model: Pipeline = None
        self.metrics: Dict[str, Any] = {}
        self.feature_importances: Dict[str, float] = {}

    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Filters resolved records and extracts features and target."""
        # Only evaluate tickets that have an SLA outcome (resolved tickets)
        resolved_df = df[df["SLA_Breached_Flag"].notna()].copy()
        
        X = resolved_df[self.CAT_FEATURES + self.NUM_FEATURES]
        y = resolved_df["SLA_Breached_Flag"].astype(int)
        return X, y

    def train_and_evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Trains candidate classifiers, selects best model, and evaluates metrics."""
        logger.info("Training SLA Breach Risk Classification models...")
        X, y = self.prepare_data(df)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
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

        candidates = {
            "RandomForest": RandomForestClassifier(
                n_estimators=150, max_depth=6, random_state=42
            ),
            "GradientBoosting": GradientBoostingClassifier(
                n_estimators=100, learning_rate=0.08, max_depth=4, random_state=42
            ),
            "LogisticRegression": LogisticRegression(max_iter=500, random_state=42),
        }

        best_score = -1
        best_name = ""
        best_pipeline = None

        for name, clf in candidates.items():
            pipeline = Pipeline(
                steps=[("preprocessor", preprocessor), ("classifier", clf)]
            )
            cv_scores = cross_val_score(
                pipeline, X_train, y_train, cv=5, scoring="roc_auc"
            )
            mean_cv = cv_scores.mean()
            logger.info(f"Model [{name}] - 5-Fold ROC-AUC: {mean_cv:.4f}")

            if mean_cv > best_score:
                best_score = mean_cv
                best_name = name
                best_pipeline = pipeline

        # Train best pipeline on full training set
        best_pipeline.fit(X_train, y_train)
        y_pred = best_pipeline.predict(X_test)
        y_proba = best_pipeline.predict_proba(X_test)[:, 1]

        self.model = best_pipeline
        self.metrics = {
            "best_algorithm": best_name,
            "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "cv_roc_auc_mean": round(float(best_score), 4),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        }

        # Calculate Feature Importances if tree-based
        clf_step = best_pipeline.named_steps["classifier"]
        if hasattr(clf_step, "feature_importances_"):
            cat_encoder = best_pipeline.named_steps["preprocessor"].named_transformers_["cat"]
            encoded_cat_names = cat_encoder.get_feature_names_out(self.CAT_FEATURES).tolist()
            all_feature_names = encoded_cat_names + self.NUM_FEATURES
            importances = clf_step.feature_importances_
            feat_imp = pd.Series(importances, index=all_feature_names).sort_values(
                ascending=False
            )
            self.feature_importances = feat_imp.head(10).to_dict()

        # Save model artifact
        self.save()
        logger.info(
            f"Best Model [{best_name}] Saved! Test ROC-AUC: {self.metrics['roc_auc']} | Accuracy: {self.metrics['accuracy']}"
        )
        return self.metrics

    def predict_risk(self, complaint_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts SLA breach risk probability for a single ticket.
        """
        if self.model is None:
            self.load()

        df_input = pd.DataFrame([complaint_dict])
        proba = float(self.model.predict_proba(df_input)[0, 1])
        prediction = int(proba >= 0.5)

        risk_tier = "High" if proba >= 0.65 else ("Medium" if proba >= 0.35 else "Low")

        return {
            "breach_probability": round(proba * 100, 2),
            "predicted_breach": bool(prediction),
            "risk_tier": risk_tier,
            "recommended_action": (
                "⚠️ Urgent Escalate: High risk of SLA breach. Assign priority task force."
                if risk_tier == "High"
                else (
                    "⚡ Monitor Closely: Moderate breach risk."
                    if risk_tier == "Medium"
                    else "✅ Standard Dispatch: Low breach risk, on-track."
                )
            ),
        }

    def save(self, path=SLA_MODEL_PATH):
        """Saves pipeline and metadata."""
        joblib.dump(
            {
                "model": self.model,
                "metrics": self.metrics,
                "feature_importances": self.feature_importances,
            },
            path,
        )

    def load(self, path=SLA_MODEL_PATH):
        """Loads trained pipeline."""
        if not path.exists():
            raise FileNotFoundError(f"Model file not found at: {path}")
        data = joblib.load(path)
        self.model = data["model"]
        self.metrics = data["metrics"]
        self.feature_importances = data.get("feature_importances", {})
        return self
