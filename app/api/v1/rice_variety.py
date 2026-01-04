"""API endpoints for rice variety prediction"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.schemas.request import RiceVarietyPredictionRequest
from app.schemas.response import RiceVarietyPredictionResponse, ErrorResponse
from app.services.rice_variety_service import RiceVarietyService
from app.utils.exceptions import (
    PredictionError,
    InvalidInputError,
    ModelNotFoundError
)

router = APIRouter()


def get_rice_variety_service() -> RiceVarietyService:
    """Dependency to get rice variety service"""
    return RiceVarietyService()


@router.post(
    "/predict",
    response_model=RiceVarietyPredictionResponse,
    summary="Predict Best Rice Variety",
    description="Predict the best rice variety based on environmental and soil conditions",
    responses={
        200: {
            "description": "Successful prediction",
            "model": RiceVarietyPredictionResponse
        },
        400: {
            "description": "Invalid input",
            "model": ErrorResponse
        },
        500: {
            "description": "Prediction error",
            "model": ErrorResponse
        }
    },
    tags=["Rice Variety"]
)
async def predict_rice_variety(
    request: RiceVarietyPredictionRequest,
    service: RiceVarietyService = Depends(get_rice_variety_service)
) -> RiceVarietyPredictionResponse:
    """
    Predict the best rice variety for given environmental conditions
    
    - **pH**: Soil pH level (0-14)
    - **soil_moisture_pct**: Soil moisture percentage (0-100)
    - **EC_dS_m**: Electrical conductivity (dS/m)
    - **soil_temp_C**: Soil temperature in Celsius
    - **water_depth_cm**: Water depth in centimeters
    - **lat**: Latitude (Sri Lanka: 5-10)
    - **lon**: Longitude (Sri Lanka: 79-82)
    - **texture**: Soil texture (loamy, sandy, clayey)
    - **prev_crop**: Previous crop (rice, maize, fallow, legume)
    - **season**: Season (Maha, Yala)
    - **soil_zone**: Soil zone (Dry, Intermediate, Wet)
    - **top_n**: Number of top recommendations (default: 3)
    """
    try:
        result = service.predict_variety(request)
        return result
    except InvalidInputError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except ModelNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Model not available: {str(e)}"
        )
    except PredictionError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/varieties",
    summary="Get Available Varieties",
    description="Get list of all available rice varieties",
    tags=["Rice Variety"]
)
async def get_available_varieties(
    service: RiceVarietyService = Depends(get_rice_variety_service)
):
    """
    Get list of all available rice varieties that can be predicted
    """
    try:
        from app.ml.registry import ModelRegistry
        model = ModelRegistry.get(service.MODEL_NAME)
        if hasattr(model, 'varieties') and model.varieties is not None:
            varieties = model.varieties
            return {
                "varieties": varieties,
                "count": len(varieties)
            }
        else:
            return {
                "varieties": [],
                "count": 0,
                "message": "Varieties not available"
            }
    except ModelNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Model not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get varieties: {str(e)}"
        )

