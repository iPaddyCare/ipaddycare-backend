"""Model loaders for different ML models"""
from pathlib import Path
from typing import Dict, Type

from app.ml.base import MLModel
from app.ml.models.rice_variety.model import RiceVarietyModel
from app.utils.exceptions import ModelLoadError


class ModelLoader:
    """Factory class for loading ML models"""
    
    _model_classes: Dict[str, Type[MLModel]] = {
        "rice_variety": RiceVarietyModel,
    }
    
    @classmethod
    def load_model(cls, model_name: str, model_path: str) -> MLModel:
        """
        Load a model by name
        
        Args:
            model_name: Name of the model to load
            model_path: Path to the model directory
            
        Returns:
            Loaded ML model instance
            
        Raises:
            ModelLoadError: If model name is not found or loading fails
        """
        if model_name not in cls._model_classes:
            raise ModelLoadError(
                f"Unknown model: {model_name}. "
                f"Available models: {list(cls._model_classes.keys())}"
            )
        
        model_class = cls._model_classes[model_name]
        model_instance = model_class()
        model_instance.load(model_path)
        
        return model_instance
    
    @classmethod
    def register_model(cls, name: str, model_class: Type[MLModel]) -> None:
        """
        Register a new model class
        
        Args:
            name: Name of the model
            model_class: Model class that inherits from MLModel
        """
        if not issubclass(model_class, MLModel):
            raise ValueError(f"{model_class} must inherit from MLModel")
        cls._model_classes[name] = model_class
