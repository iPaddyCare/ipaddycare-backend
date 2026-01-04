"""Base class for ML models"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class MLModel(ABC):
    """Abstract base class for all ML models"""
    
    @abstractmethod
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a prediction based on input data
        
        Args:
            input_data: Dictionary containing input features
            
        Returns:
            Dictionary containing prediction results
        """
        pass
    
    @abstractmethod
    def load(self, model_path: str) -> None:
        """
        Load the model from disk
        
        Args:
            model_path: Path to the model directory
        """
        pass
    
    @abstractmethod
    def is_loaded(self) -> bool:
        """
        Check if the model is loaded
        
        Returns:
            True if model is loaded, False otherwise
        """
        pass
