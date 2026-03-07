"""API endpoints for seed moisture prediction"""
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.request import SeedMoisturePredictionRequest
from app.schemas.response import SeedMoisturePredictionResponse, ErrorResponse
from app.services.seed_moisture_service import SeedMoistureService
from app.utils.exceptions import InvalidInputError, ModelNotFoundError, PredictionError


router = APIRouter()


def get_seed_moisture_service() -> SeedMoistureService:
    """Dependency to get seed moisture service"""
    return SeedMoistureService()


@router.post(
    "/predict",
    response_model=SeedMoisturePredictionResponse,
    summary="Predict Seed Moisture",
    description=(
        "Predict seed oven moisture content based on sensor readings and sample properties.\n\n"
        "- **cap_sensor_value**: Capacitive sensor reading\n"
        "- **sample_temperature**: Sample temperature (°C)\n"
        "- **ambient_temperature**: Ambient temperature (°C)\n"
        "- **ambient_humidity**: Ambient relative humidity (%)\n"
        "- **sample_weight**: Sample weight (g)\n"
        "- **bulk_density**: Bulk density (g/cm³)\n"
    ),
    responses={
        200: {
            "description": "Successful prediction",
            "model": SeedMoisturePredictionResponse,
        },
        400: {
            "description": "Invalid input",
            "model": ErrorResponse,
        },
        503: {
            "description": "Model not available",
            "model": ErrorResponse,
        },
        500: {
            "description": "Prediction error",
            "model": ErrorResponse,
        },
    },
    tags=["Seed Moisture"],
)
async def predict_seed_moisture(
    request: SeedMoisturePredictionRequest,
    service: SeedMoistureService = Depends(get_seed_moisture_service),
) -> SeedMoisturePredictionResponse:
    """
    Predict seed moisture for given sensor readings and sample properties.
    """
    try:
        result = service.predict_moisture(request)
        return result
    except InvalidInputError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except ModelNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Model not available: {str(e)}",
        )
    except PredictionError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}",
        )

