"""API endpoints for drying schedule prediction."""
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.request import DryingSchedulePredictionRequest
from app.schemas.response import DryingSchedulePredictionResponse, ErrorResponse
from app.services.drying_schedule_service import DryingScheduleService
from app.utils.exceptions import ModelNotFoundError, PredictionError

router = APIRouter()


def get_drying_schedule_service() -> DryingScheduleService:
    return DryingScheduleService()


@router.post(
    "/predict",
    response_model=DryingSchedulePredictionResponse,
    summary="Predict Drying Schedule",
    description=(
        "Predict whether seed needs drying and estimated days to target moisture (13%)."
    ),
    responses={
        200: {"description": "Successful prediction", "model": DryingSchedulePredictionResponse},
        503: {"description": "Model not available", "model": ErrorResponse},
        500: {"description": "Prediction error", "model": ErrorResponse},
    },
    tags=["Drying Schedule"],
)
async def predict_drying_schedule(
    request: DryingSchedulePredictionRequest,
    service: DryingScheduleService = Depends(get_drying_schedule_service),
) -> DryingSchedulePredictionResponse:
    try:
        return service.predict(request)
    except ModelNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model not available: {str(e)}")
    except PredictionError as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
