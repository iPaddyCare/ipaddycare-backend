"""Rice Variety Prediction Model"""
import os
import warnings
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from pathlib import Path

from app.ml.base import MLModel
from app.utils.exceptions import ModelLoadError, PredictionError, InvalidInputError


class RiceVarietyModel(MLModel):
    """Model for predicting the best rice variety based on environmental conditions"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.variety_encoder = None
        self.variety_ohe = None
        self.feature_columns = None
        self.feature_columns_with_variety = None
        self.varieties = None
        self._loaded = False
    
    def load(self, model_path: str) -> None:
        """
        Load the model and preprocessing artifacts
        
        Args:
            model_path: Path to the directory containing model artifacts
        """
        try:
            artifacts_path = Path(model_path) / "artifacts"
            
            # Suppress sklearn version mismatch warnings
            # The model was trained with sklearn 1.6.1, current version is 1.7.2
            # This is generally safe for minor version differences
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
                
                # Load model
                model_file = artifacts_path / "unified_model.pkl"
                if not model_file.exists():
                    raise ModelLoadError(f"Model file not found: {model_file}")
                self.model = joblib.load(model_file)
            
                # Load preprocessing objects
                self.scaler = joblib.load(artifacts_path / "scaler.pkl")
                self.label_encoders = joblib.load(artifacts_path / "label_encoders.pkl")
                self.variety_encoder = joblib.load(artifacts_path / "variety_encoder.pkl")
                self.variety_ohe = joblib.load(artifacts_path / "variety_ohe.pkl")
                self.feature_columns = joblib.load(artifacts_path / "feature_columns.pkl")
                self.feature_columns_with_variety = joblib.load(
                    artifacts_path / "feature_columns_with_variety.pkl"
                )
                self.varieties = joblib.load(artifacts_path / "varieties.pkl")
            
            self._loaded = True
            
        except Exception as e:
            raise ModelLoadError(f"Failed to load model: {str(e)}")
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded"""
        return self._loaded
    
    def _prepare_features(self, input_data: Dict[str, Any]) -> np.ndarray:
        """
        Prepare and preprocess input features
        
        Args:
            input_data: Dictionary containing input features
            
        Returns:
            Preprocessed feature array
        """
        # Create DataFrame from input
        features = pd.DataFrame([input_data])
        
        # Encode categorical features
        categorical_features = ['texture', 'prev_crop', 'season', 'soil_zone']
        for col in categorical_features:
            if col not in features.columns:
                raise InvalidInputError(f"Missing required feature: {col}")
            
            le = self.label_encoders[col]
            try:
                features[col + '_encoded'] = le.transform(features[col])[0]
            except ValueError as e:
                # Handle unknown categories
                raise InvalidInputError(
                    f"Invalid value for {col}: {features[col].iloc[0]}. "
                    f"Valid values: {list(le.classes_)}"
                )
            features = features.drop(columns=[col])
        
        # Create season_zone feature
        season_zone = f"{input_data['season']}_{input_data['soil_zone']}"
        le_sz = self.label_encoders['season_zone']
        try:
            features['season_zone_encoded'] = le_sz.transform([season_zone])[0]
        except ValueError:
            raise InvalidInputError(
                f"Invalid season_zone combination: {season_zone}. "
                f"Valid combinations: {list(le_sz.classes_)}"
            )
        
        # Create interaction features
        features['pH_EC_interaction'] = input_data['pH'] * input_data['EC_dS_m']
        features['moisture_temp_interaction'] = (
            input_data['soil_moisture_pct'] * input_data['soil_temp_C']
        )
        features['water_moisture_ratio'] = (
            input_data['water_depth_cm'] / (input_data['soil_moisture_pct'] + 1)
        )
        
        # Geographic feature
        features['dist_from_center'] = np.sqrt(
            (input_data['lat'] - 7.5)**2 + (input_data['lon'] - 80.5)**2
        )
        
        # Ensure correct column order
        features = features[self.feature_columns]
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        return features_scaled
    
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict the best rice variety and yields for all varieties
        
        Args:
            input_data: Dictionary containing input features and optional top_n
            
        Returns:
            Dictionary containing best variety, expected yield, and recommendations
        """
        if not self.is_loaded():
            raise PredictionError("Model is not loaded. Call load() first.")
        
        top_n = input_data.get('top_n', 3)
        
        # Prepare base features
        features_scaled = self._prepare_features(input_data)
        
        # Predict yield for each variety
        predictions = {}
        for variety in self.varieties:
            # Encode variety
            variety_encoded = self.variety_encoder.transform([variety])[0]
            
            # Handle both old and new sklearn OneHotEncoder API
            try:
                variety_ohe_features = self.variety_ohe.transform([[variety_encoded]])
            except TypeError:
                # Fallback for older sklearn versions
                variety_ohe_features = self.variety_ohe.transform(
                    np.array([[variety_encoded]])
                )
            
            # Combine base features with variety features
            features_with_variety = np.hstack([features_scaled, variety_ohe_features])
            
            # Predict yield
            predicted_yield = self.model.predict(features_with_variety)[0]
            predictions[variety] = float(predicted_yield)
        
        # Sort by predicted yield
        sorted_predictions = sorted(
            predictions.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Prepare recommendations
        recommendations = [
            {
                "variety": var,
                "predicted_yield": yield_val,
                "rank": idx + 1
            }
            for idx, (var, yield_val) in enumerate(sorted_predictions[:top_n])
        ]
        
        return {
            "best_variety": sorted_predictions[0][0],
            "expected_yield": sorted_predictions[0][1],
            "recommendations": recommendations,
            "all_predictions": predictions
        }
