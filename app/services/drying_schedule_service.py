"""Service layer for drying schedule prediction."""
from app.ml.registry import ModelRegistry
from app.schemas.request import DryingSchedulePredictionRequest
from app.schemas.response import DryingSchedulePredictionResponse
from app.utils.exceptions import ModelNotFoundError, PredictionError


class DryingScheduleService:
    MODEL_NAME = "drying_schedule"

    def __init__(self) -> None:
        self._ensure_model_loaded()

    def _ensure_model_loaded(self) -> None:
        try:
            model = ModelRegistry.get(self.MODEL_NAME)
            if not model.is_loaded():
                raise ModelNotFoundError(f"Model '{self.MODEL_NAME}' is not loaded")
        except ModelNotFoundError:
            raise ModelNotFoundError(
                f"Model '{self.MODEL_NAME}' not found. "
                "Please ensure the model is loaded during application startup."
            )

    def predict(self, request: DryingSchedulePredictionRequest) -> DryingSchedulePredictionResponse:
        try:
            model = ModelRegistry.get(self.MODEL_NAME)
            result = model.predict(request.model_dump())
            return DryingSchedulePredictionResponse(**result)
        except Exception as e:
            raise PredictionError(f"Failed to predict drying schedule: {str(e)}")
