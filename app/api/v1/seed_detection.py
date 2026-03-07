"""API endpoints for paddy seed classification"""
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.request import SeedDetectionPredictionRequest
from app.schemas.response import SeedDetectionPredictionResponse, ErrorResponse
from app.services.seed_detection_service import SeedDetectionService
from app.utils.exceptions import InvalidInputError, ModelNotFoundError, PredictionError


router = APIRouter()


def get_seed_detection_service() -> SeedDetectionService:
    """Dependency to get seed detection service"""
    return SeedDetectionService()


@router.post(
    "/predict",
    response_model=SeedDetectionPredictionResponse,
    summary="Classify Paddy Seed Image",
    description=(
        "Classify a paddy seed image into one of: BG_375, Suwadel, P_Perumal, or Background.\n\n"
        "Send the image as a **base64 string** in the request body.\n"
        "Supports JPEG/PNG. Optional prefix: `data:image/jpeg;base64,`"
    ),
    responses={
        200: {
            "description": "Successful prediction",
            "model": SeedDetectionPredictionResponse,
        },
        400: {
            "description": "Invalid input (e.g. invalid base64 or image)",
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
    tags=["Seed Detection"],
)
async def predict_seed_class(
    request: SeedDetectionPredictionRequest,
    service: SeedDetectionService = Depends(get_seed_detection_service),
) -> SeedDetectionPredictionResponse:
    """
    Classify paddy seed image from base64-encoded image.
    """
    try:
        result = service.predict_class(request)
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
