"""Seed Moisture Prediction Model"""
import warnings
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np

from app.ml.base import MLModel
from app.utils.exceptions import ModelLoadError, PredictionError, InvalidInputError


class SeedMoistureModel(MLModel):
    """Model for predicting seed moisture (oven moisture) from sensor readings"""

    def __init__(self) -> None:
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self._loaded = False

    def load(self, model_path: str) -> None:
        """
        Load the model and preprocessing artifacts.

        The notebook saves a dict with:
        - 'model': trained regressor
        - 'scaler': fitted StandardScaler
        - 'feature_columns': list of feature names
        - 'model_name': human readable model name
        """
        try:
            artifacts_path = Path(model_path)
            model_file = artifacts_path / "best_model_linear_regression.pkl"

            if not model_file.exists():
                raise ModelLoadError(f"Model file not found: {model_file}")

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
                model_data = joblib.load(model_file)

            self.model = model_data.get("model")
            self.scaler = model_data.get("scaler")
            self.feature_columns = model_data.get("feature_columns")

            if self.model is None or self.scaler is None or self.feature_columns is None:
                raise ModelLoadError(
                    "Loaded model data is missing required keys "
                    "('model', 'scaler', 'feature_columns')"
                )

            self._loaded = True

        except Exception as e:
            raise ModelLoadError(f"Failed to load seed moisture model: {str(e)}")

    def is_loaded(self) -> bool:
        """Check if the model is loaded"""
        return self._loaded

    def _prepare_features(self, input_data: Dict[str, Any]) -> np.ndarray:
        """
        Prepare and scale features for prediction.

        The training notebook used:
        ['cap_sensor_value', 'sample_temperature', 'ambient_temperature',
         'ambient_humidity', 'sample_weight', 'bulk_density']
        """
        if not self.feature_columns:
            raise PredictionError("Model feature_columns not initialized")

        try:
            values = []
            for col in self.feature_columns:
                if col not in input_data:
                    raise InvalidInputError(f"Missing required feature: {col}")
                values.append(float(input_data[col]))

            X = np.array([values], dtype=float)
            X_scaled = self.scaler.transform(X)
            return X_scaled
        except InvalidInputError:
            raise
        except Exception as e:
            raise PredictionError(f"Failed to prepare features: {str(e)}")

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict seed moisture percentage.

        Returns a dict with:
        - 'predicted_moisture': float
        """
        if not self.is_loaded():
            raise PredictionError("Model is not loaded. Call load() first.")

        try:
            X_scaled = self._prepare_features(input_data)
            prediction = float(self.model.predict(X_scaled)[0])
        except Exception as e:
            raise PredictionError(f"Failed to predict seed moisture: {str(e)}")

        return {"predicted_moisture": prediction}

