"""Service layer for seed moisture prediction"""
from app.ml.registry import ModelRegistry
from app.schemas.request import SeedMoisturePredictionRequest
from app.schemas.response import SeedMoisturePredictionResponse
from app.utils.exceptions import ModelNotFoundError, PredictionError


class SeedMoistureService:
    """Service for seed moisture prediction operations"""

    MODEL_NAME = "seed_moisture"

    def __init__(self) -> None:
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

    def predict_moisture(
        self,
        request: SeedMoisturePredictionRequest,
    ) -> SeedMoisturePredictionResponse:
        """
        Predict seed moisture based on sensor readings.

        Args:
            request: Prediction request with input features.

        Returns:
            Prediction response with predicted moisture.

        Raises:
            PredictionError: If prediction fails.
        """
        try:
            model = ModelRegistry.get(self.MODEL_NAME)

            # Convert request to dict for model prediction
            input_data = request.model_dump()

            # Get prediction from model
            prediction_result = model.predict(input_data)

            return SeedMoisturePredictionResponse(
                predicted_moisture=prediction_result["predicted_moisture"]
            )
        except Exception as e:
            raise PredictionError(f"Failed to predict seed moisture: {str(e)}")

