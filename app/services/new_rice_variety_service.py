"""Service layer for new rice variety prediction using tuned models"""
from app.ml.registry import ModelRegistry
from app.schemas.request import RiceVarietyPredictionRequest
from app.schemas.response import RiceVarietyPredictionResponse, VarietyRecommendation
from app.utils.exceptions import ModelNotFoundError, PredictionError


class NewRiceVarietyService:
    """Service for new rice variety prediction operations using tuned models"""
    
    MODEL_NAME = "rice_variety_new"
    
    def __init__(self):
        """Initialize the service"""
        self._ensure_model_loaded()
    
    def _ensure_model_loaded(self) -> None:
        """Ensure the model is loaded in the registry"""
        try:
            model = ModelRegistry.get(self.MODEL_NAME)
            if not model.is_loaded():
                raise ModelNotFoundError(f"Model '{self.MODEL_NAME}' is not loaded")
        except ModelNotFoundError:
            raise ModelNotFoundError(
                f"Model '{self.MODEL_NAME}' not found. "
                "Please ensure the model is loaded during application startup."
            )
    
    def predict_variety(
        self, 
        request: RiceVarietyPredictionRequest
    ) -> RiceVarietyPredictionResponse:
        """
        Predict the best rice variety based on input features using new tuned models
        
        Args:
            request: Prediction request with input features
            
        Returns:
            Prediction response with recommendations
            
        Raises:
            PredictionError: If prediction fails
        """
        try:
            model = ModelRegistry.get(self.MODEL_NAME)
            
            # Convert request to dict for model prediction
            input_data = request.model_dump()
            top_n = input_data.pop('top_n', 5)  # Default to 5 for new model
            input_data['top_n'] = top_n
            
            # Get prediction from model
            prediction_result = model.predict(input_data)
            
            # Convert to response schema
            recommendations = [
                VarietyRecommendation(
                    variety=rec['variety'],
                    predicted_yield=rec['predicted_yield'],
                    rank=rec['rank']
                )
                for rec in prediction_result['recommendations']
            ]
            
            return RiceVarietyPredictionResponse(
                best_variety=prediction_result['best_variety'],
                expected_yield=prediction_result['expected_yield'],
                recommendations=recommendations,
                all_predictions=prediction_result['all_predictions']
            )
            
        except Exception as e:
            raise PredictionError(f"Failed to predict rice variety: {str(e)}")
    
    def get_available_varieties(self) -> list:
        """Get list of available rice varieties"""
        try:
            model = ModelRegistry.get(self.MODEL_NAME)
            if hasattr(model, 'varieties') and model.varieties is not None:
                return model.varieties
            return []
        except ModelNotFoundError:
            return []
