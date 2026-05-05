"""Drying Schedule Prediction Model (classifier + regressor)."""
from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd

from app.ml.base import MLModel
from app.utils.exceptions import ModelLoadError, PredictionError


class DryingScheduleModel(MLModel):
    """Predict drying need and estimated days to target moisture."""

    TARGET_MOISTURE = 13.0

    def __init__(self) -> None:
        self.classifier = None
        self.regressor = None
        self._loaded = False

    def load(self, model_path: str) -> None:
        try:
            artifacts = Path(model_path) / "artifacts"
            cls_file = artifacts / "drying_schedule_classifier.pkl"
            reg_file = artifacts / "drying_schedule_regressor.pkl"

            if not cls_file.exists():
                raise ModelLoadError(f"Classifier file not found: {cls_file}")
            if not reg_file.exists():
                raise ModelLoadError(f"Regressor file not found: {reg_file}")

            self.classifier = joblib.load(cls_file)
            self.regressor = joblib.load(reg_file)
            self._loaded = True
        except Exception as e:
            raise ModelLoadError(f"Failed to load drying schedule model: {str(e)}")

    def is_loaded(self) -> bool:
        return self._loaded

    def _normalize_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        moisture = float(input_data["current_moisture_pct"])
        attempt_no = int(input_data.get("attempt_no", 1))

        return {
            "attempt_no": attempt_no,
            "current_moisture_pct": moisture,
            "moisture_excess_pct": float(input_data.get("moisture_excess_pct", moisture - self.TARGET_MOISTURE)),
            "weather_temp_max_c": float(input_data["weather_temp_max_c"]),
            "weather_temp_min_c": float(input_data["weather_temp_min_c"]),
            "weather_precip_mm": float(input_data["weather_precip_mm"]),
            "weather_wind_max_kmh": float(input_data["weather_wind_max_kmh"]),
        }

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_loaded():
            raise PredictionError("Model is not loaded. Call load() first.")

        try:
            row = self._normalize_input(input_data)

            # Classifier features used in latest trained pipeline
            x_cls = pd.DataFrame([
                {
                    "current_moisture_pct": row["current_moisture_pct"],
                    "weather_temp_max_c": row["weather_temp_max_c"],
                    "weather_temp_min_c": row["weather_temp_min_c"],
                    "weather_precip_mm": row["weather_precip_mm"],
                    "weather_wind_max_kmh": row["weather_wind_max_kmh"],
                }
            ])

            # Regressor features with one-hot district alignment
            x_reg = pd.DataFrame([
                {
                    "attempt_no": row["attempt_no"],
                    "current_moisture_pct": row["current_moisture_pct"],
                    "moisture_excess_pct": row["moisture_excess_pct"],
                    "weather_temp_max_c": row["weather_temp_max_c"],
                    "weather_temp_min_c": row["weather_temp_min_c"],
                    "weather_precip_mm": row["weather_precip_mm"],
                    "weather_wind_max_kmh": row["weather_wind_max_kmh"],
                }
            ])
            if hasattr(self.regressor, "feature_names_in_"):
                expected = list(self.regressor.feature_names_in_)
                for col in expected:
                    if col not in x_reg.columns:
                        x_reg[col] = 0
                x_reg = x_reg[expected]

            label = str(self.classifier.predict(x_cls)[0])
            reg_days = float(self.regressor.predict(x_reg)[0])

            needs_drying = label == "needs_drying"
            days_to_target = max(0, int(round(reg_days))) if needs_drying else 0

            return {
                "label": label,
                "needs_drying": needs_drying,
                "days_to_target": days_to_target,
                "predicted_remaining_days": max(0.0, reg_days),
                "target_moisture": self.TARGET_MOISTURE,
            }
        except Exception as e:
            raise PredictionError(f"Failed to predict drying schedule: {str(e)}")
