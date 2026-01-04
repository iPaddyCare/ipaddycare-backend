"""Custom exceptions for the application"""


class MLModelError(Exception):
    """Base exception for ML model errors"""
    pass


class ModelNotFoundError(MLModelError):
    """Raised when a model is not found"""
    pass


class ModelLoadError(MLModelError):
    """Raised when a model fails to load"""
    pass


class PredictionError(MLModelError):
    """Raised when prediction fails"""
    pass


class InvalidInputError(MLModelError):
    """Raised when input data is invalid"""
    pass

