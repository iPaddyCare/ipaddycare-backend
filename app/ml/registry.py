"""Model registry for managing loaded models"""
from typing import Dict, Optional

from app.ml.base import MLModel
from app.utils.exceptions import ModelNotFoundError


class ModelRegistry:
    """Registry for managing loaded ML models"""
    
    _models: Dict[str, MLModel] = {}
    
    @classmethod
    def register(cls, name: str, model: MLModel) -> None:
        """
        Register a model in the registry
        
        Args:
            name: Name of the model
            model: ML model instance
        """
        if not isinstance(model, MLModel):
            raise ValueError(f"{model} must be an instance of MLModel")
        cls._models[name] = model
    
    @classmethod
    def get(cls, name: str) -> MLModel:
        """
        Get a model from the registry
        
        Args:
            name: Name of the model
            
        Returns:
            ML model instance
            
        Raises:
            ModelNotFoundError: If model is not found
        """
        if name not in cls._models:
            raise ModelNotFoundError(
                f"Model '{name}' not found in registry. "
                f"Available models: {list(cls._models.keys())}"
            )
        return cls._models[name]
    
    @classmethod
    def list_models(cls) -> list[str]:
        """
        List all registered models
        
        Returns:
            List of model names
        """
        return list(cls._models.keys())
    
    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Unregister a model from the registry
        
        Args:
            name: Name of the model to unregister
        """
        if name in cls._models:
            del cls._models[name]
    
    @classmethod
    def clear(cls) -> None:
        """Clear all models from the registry"""
        cls._models.clear()
