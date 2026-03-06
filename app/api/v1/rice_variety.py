"""API endpoints for rice variety prediction"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.schemas.request import RiceVarietyPredictionRequest
from app.schemas.response import RiceVarietyPredictionResponse, ErrorResponse
from app.services.rice_variety_service import RiceVarietyService
from app.services.new_rice_variety_service import NewRiceVarietyService
from app.utils.exceptions import (
    PredictionError,
    InvalidInputError,
    ModelNotFoundError
)

router = APIRouter()


def get_rice_variety_service() -> RiceVarietyService:
    """Dependency to get rice variety service"""
    return RiceVarietyService()


def get_new_rice_variety_service() -> NewRiceVarietyService:
    """Dependency to get new rice variety service"""
    return NewRiceVarietyService()


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


@router.post(
    "/predict/new",
    response_model=RiceVarietyPredictionResponse,
    summary="Predict Best Rice Variety (New Models)",
    description="Predict the best rice variety using new tuned Random Forest classifier and Linear Regression models",
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
    tags=["Rice Variety - New Models"]
)
async def predict_rice_variety_new(
    request: RiceVarietyPredictionRequest,
    service: NewRiceVarietyService = Depends(get_new_rice_variety_service)
) -> RiceVarietyPredictionResponse:
    """
    Predict the best rice variety using new tuned models (Random Forest + Linear Regression)
    
    This endpoint uses the latest tuned models:
    - Tuned Random Forest Classifier with SMOTE for variety prediction
    - Multiple Linear Regression for yield prediction
    
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
    - **top_n**: Number of top recommendations (default: 5)
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
    "/varieties/new",
    summary="Get Available Varieties (New Models)",
    description="Get list of all available rice varieties from new models",
    tags=["Rice Variety - New Models"]
)
async def get_available_varieties_new(
    service: NewRiceVarietyService = Depends(get_new_rice_variety_service)
):
    """
    Get list of all available rice varieties from the new tuned models
    """
    try:
        varieties = service.get_available_varieties()
        return {
            "varieties": varieties,
            "count": len(varieties)
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

