"""Service layer for paddy seed classification"""
from app.ml.registry import ModelRegistry
from app.schemas.request import SeedDetectionPredictionRequest
from app.schemas.response import SeedDetectionPredictionResponse
from app.utils.exceptions import ModelNotFoundError, PredictionError


class SeedDetectionService:
    """Service for paddy seed image classification"""

    MODEL_NAME = "seed_detection"

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

    def predict_class(
        self,
        request: SeedDetectionPredictionRequest,
    ) -> SeedDetectionPredictionResponse:
        """
        Classify paddy seed image.

        Args:
            request: Prediction request with base64-encoded image.

        Returns:
            Prediction response with predicted class and confidence.

        Raises:
            PredictionError: If prediction fails.
        """
        try:
            model = ModelRegistry.get(self.MODEL_NAME)
            input_data = request.model_dump()
            prediction_result = model.predict(input_data)

            return SeedDetectionPredictionResponse(
                predicted_class=prediction_result["predicted_class"],
                confidence=prediction_result["confidence"],
                class_id=prediction_result["class_id"],
            )
        except Exception as e:
            raise PredictionError(f"Failed to classify seed image: {str(e)}")
