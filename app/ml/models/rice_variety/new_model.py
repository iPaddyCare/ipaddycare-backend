"""New Rice Variety Prediction Model using tuned Random Forest and Linear Regression"""
import os
import warnings
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from pathlib import Path

# Workaround for sklearn version checking issues
# Patch sklearn.utils before loading models to handle version incompatibilities
try:
    import sklearn.utils
    
    # Patch parse_version if missing
    if not hasattr(sklearn.utils, 'parse_version'):
        try:
            from packaging.version import parse as parse_version
            sklearn.utils.parse_version = parse_version
        except ImportError:
            def parse_version(v):
                return v
            sklearn.utils.parse_version = parse_version
    
    # Patch get_column_indices if missing (moved in newer sklearn versions)
    if not hasattr(sklearn.utils, 'get_column_indices'):
        try:
            # Try to import from the new location (sklearn >= 1.0)
            from sklearn.utils._column_transformer import _get_column_indices as get_column_indices
            sklearn.utils.get_column_indices = get_column_indices
        except (ImportError, AttributeError):
            try:
                # Try older location (sklearn < 1.0)
                from sklearn.compose._column_transformer import _get_column_indices as get_column_indices
                sklearn.utils.get_column_indices = get_column_indices
            except (ImportError, AttributeError):
                # Create a compatibility function if not found
                def get_column_indices(X, key):
                    """Compatibility wrapper for get_column_indices"""
                    if hasattr(X, 'columns'):
                        # DataFrame case
                        if isinstance(key, str):
                            return [X.columns.get_loc(key)]
                        elif isinstance(key, (list, tuple)):
                            return [X.columns.get_loc(k) for k in key]
                        else:
                            return list(range(len(X.columns)))
                    else:
                        # Array case
                        if isinstance(key, (int, np.integer)):
                            return [key]
                        elif isinstance(key, (list, tuple, np.ndarray)):
                            return list(key)
                        else:
                            return list(range(X.shape[1]))
                sklearn.utils.get_column_indices = get_column_indices
    
    # Also patch _get_column_indices which might be referenced internally
    if not hasattr(sklearn.utils, '_get_column_indices'):
        if hasattr(sklearn.utils, 'get_column_indices'):
            sklearn.utils._get_column_indices = sklearn.utils.get_column_indices
            
except (ImportError, AttributeError):
    pass

from app.ml.base import MLModel
from app.utils.exceptions import ModelLoadError, PredictionError, InvalidInputError


class NewRiceVarietyModel(MLModel):
    """New model for predicting rice variety using tuned Random Forest classifier and Linear Regression"""
    
    def __init__(self):
        self.classifier = None
        self.regressor = None
        self.label_encoder = None
        self.numeric_features = ['pH', 'soil_moisture_pct', 'EC_dS_m', 'soil_temp_C', 'water_depth_cm', 'lat', 'lon']
        self.categorical_features = ['texture', 'prev_crop', 'season', 'soil_zone']
        self.varieties = None
        self._loaded = False
    
    def load(self, model_path: str) -> None:
        """
        Load the models and preprocessing artifacts
        
        Args:
            model_path: Path to the directory containing model artifacts
        """
        try:
            models_path = Path(model_path)
            
            # Suppress sklearn version mismatch warnings
            import pickle
            
            # Ensure sklearn.utils is imported and patched before loading
            # This must happen before pickle tries to import sklearn modules
            try:
                import sklearn.utils
                # Re-apply patch if needed (in case it wasn't applied at module level)
                if not hasattr(sklearn.utils, 'get_column_indices'):
                    try:
                        from sklearn.utils._column_transformer import _get_column_indices as get_column_indices
                        sklearn.utils.get_column_indices = get_column_indices
                    except (ImportError, AttributeError):
                        # Create compatibility function
                        def get_column_indices(X, key):
                            if hasattr(X, 'columns'):
                                if isinstance(key, str):
                                    return [X.columns.get_loc(key)]
                                elif isinstance(key, (list, tuple)):
                                    return [X.columns.get_loc(k) for k in key]
                                return list(range(len(X.columns)))
                            else:
                                if isinstance(key, (int, np.integer)):
                                    return [key]
                                elif isinstance(key, (list, tuple, np.ndarray)):
                                    return list(key)
                                return list(range(X.shape[1]))
                        sklearn.utils.get_column_indices = get_column_indices
            except ImportError:
                pass
            
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                warnings.filterwarnings("ignore", category=FutureWarning)
                warnings.filterwarnings("ignore", category=DeprecationWarning)
                
                # Load classifier (tuned Random Forest with SMOTE)
                classifier_file = models_path / "final_rice_variety_classifier.pkl"
                if not classifier_file.exists():
                    raise ModelLoadError(f"Classifier file not found: {classifier_file}")
                
                # Use pickle directly (bypasses sklearn version checking in joblib)
                try:
                    with open(classifier_file, 'rb') as f:
                        self.classifier = pickle.load(f)
                except Exception as pickle_error:
                    # Fallback to joblib if pickle fails
                    try:
                        self.classifier = joblib.load(classifier_file)
                    except Exception as joblib_error:
                        raise ModelLoadError(
                            f"Failed to load classifier. "
                            f"Pickle error: {str(pickle_error)}, Joblib error: {str(joblib_error)}"
                        )
            
                # Load regressor (Linear Regression)
                regressor_file = models_path / "final_yield_regressor.pkl"
                if not regressor_file.exists():
                    raise ModelLoadError(f"Regressor file not found: {regressor_file}")
                
                # Load regressor (Linear Regression)
                regressor_file = models_path / "final_yield_regressor.pkl"
                if not regressor_file.exists():
                    raise ModelLoadError(f"Regressor file not found: {regressor_file}")
                
                try:
                    with open(regressor_file, 'rb') as f:
                        self.regressor = pickle.load(f)
                except Exception as pickle_error:
                    try:
                        self.regressor = joblib.load(regressor_file)
                    except Exception as joblib_error:
                        raise ModelLoadError(
                            f"Failed to load regressor. "
                            f"Pickle error: {str(pickle_error)}, Joblib error: {str(joblib_error)}"
                        )
            
                # Load label encoder
                encoder_file = models_path / "label_encoder.pkl"
                if not encoder_file.exists():
                    raise ModelLoadError(f"Label encoder file not found: {encoder_file}")
                
                try:
                    with open(encoder_file, 'rb') as f:
                        self.label_encoder = pickle.load(f)
                except Exception as pickle_error:
                    try:
                        self.label_encoder = joblib.load(encoder_file)
                    except Exception as joblib_error:
                        raise ModelLoadError(
                            f"Failed to load label encoder. "
                            f"Pickle error: {str(pickle_error)}, Joblib error: {str(joblib_error)}"
                        )
            
            # Get available varieties from label encoder
            self.varieties = self.label_encoder.classes_.tolist()
            
            self._loaded = True
            
        except Exception as e:
            raise ModelLoadError(f"Failed to load model: {str(e)}")
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded"""
        return self._loaded
    
    def _prepare_input_dataframe(self, input_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Prepare input data as DataFrame
        
        Args:
            input_data: Dictionary containing input features
            
        Returns:
            DataFrame with input features
        """
        # Create DataFrame from input
        df = pd.DataFrame([input_data])
        
        # Validate required features
        required_features = self.numeric_features + self.categorical_features
        for feature in required_features:
            if feature not in df.columns:
                raise InvalidInputError(f"Missing required feature: {feature}")
        
        return df
    
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
        
        top_n = input_data.get('top_n', 5)
        
        # Prepare input DataFrame
        input_df = self._prepare_input_dataframe(input_data)
        
        # Get prediction probabilities for all varieties
        try:
            probs = self.classifier.predict_proba(input_df)[0]
            classes = self.classifier.classes_
        except Exception as e:
            raise PredictionError(f"Failed to get classification probabilities: {str(e)}")
        
        # Get top N recommendations based on probabilities
        top_indices = np.argsort(probs)[-top_n:][::-1]
        top_varieties = classes[top_indices]
        top_scores = probs[top_indices]
        
        # Predict yield for each recommended variety
        # The regression model needs the variety as input
        predictions = {}
        recommendations = []
        
        for idx, (variety, score) in enumerate(zip(top_varieties, top_scores)):
            # Create input with variety included
            temp_input = input_df.copy()
            temp_input['recommended_variety'] = variety
            
            try:
                # Predict yield using regressor
                pred_yield = self.regressor.predict(temp_input)[0]
                pred_yield = float(pred_yield)
            except Exception as e:
                raise PredictionError(f"Failed to predict yield for variety {variety}: {str(e)}")
            
            predictions[variety] = pred_yield
            
            recommendations.append({
                'variety': variety,
                'predicted_yield': pred_yield,
                'confidence': float(score),
                'rank': idx + 1
            })
        
        # Also predict yields for all other varieties
        for variety in self.varieties:
            if variety not in predictions:
                temp_input = input_df.copy()
                temp_input['recommended_variety'] = variety
                try:
                    pred_yield = self.regressor.predict(temp_input)[0]
                    predictions[variety] = float(pred_yield)
                except Exception as e:
                    # If prediction fails for a variety, skip it
                    continue
        
        # Sort all predictions by yield
        sorted_predictions = sorted(
            predictions.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Get best variety (highest yield)
        best_variety = sorted_predictions[0][0]
        expected_yield = sorted_predictions[0][1]
        
        return {
            "best_variety": best_variety,
            "expected_yield": expected_yield,
            "recommendations": recommendations,
            "all_predictions": predictions
        }
