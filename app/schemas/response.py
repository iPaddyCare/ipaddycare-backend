from pydantic import BaseModel, Field
from typing import List, Optional


class VarietyRecommendation(BaseModel):
    """Schema for a single variety recommendation"""

    variety: str = Field(..., description="Rice variety name")
    predicted_yield: float = Field(..., description="Predicted yield in kg/ha")
    rank: int = Field(..., description="Rank of this recommendation (1 = best)")


class RiceVarietyPredictionResponse(BaseModel):
    """Response schema for rice variety prediction"""

    best_variety: str = Field(..., description="Recommended rice variety")
    expected_yield: float = Field(..., description="Expected yield in kg/ha")
    recommendations: List[VarietyRecommendation] = Field(
        ..., description="Top N variety recommendations"
    )
    all_predictions: dict[str, float] = Field(
        ..., description="Predicted yields for all varieties"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "best_variety": "AT378",
                "expected_yield": 9486.79,
                "recommendations": [
                    {"variety": "AT378", "predicted_yield": 9486.79, "rank": 1},
                    {"variety": "AT362", "predicted_yield": 8591.04, "rank": 2},
                    {"variety": "BG374", "predicted_yield": 8195.82, "rank": 3},
                ],
                "all_predictions": {
                    "AT378": 9486.79,
                    "AT362": 8591.04,
                    "BG374": 8195.82,
                    "BG352": 7830.89,
                    "BG300": 6926.69,
                    "LD365": 5612.45,
                    "BW367": 5234.12,
                },
            }
        }


class SeedMoisturePredictionResponse(BaseModel):
    """Response schema for seed moisture prediction"""

    predicted_moisture: float = Field(
        ..., description="Predicted oven moisture content (%)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "predicted_moisture": 14.94,
            }
        }


class SeedDetectionPredictionResponse(BaseModel):
    """Response schema for paddy seed classification"""

    predicted_class: str = Field(
        ...,
        description="Predicted class: BG_375, Suwadel, P_Perumal, or Background",
    )
    confidence: float = Field(..., description="Prediction confidence (0-1)")
    class_id: int = Field(..., description="Class index (0-3)")

    class Config:
        json_schema_extra = {
            "example": {
                "predicted_class": "BG_375",
                "confidence": 0.95,
                "class_id": 0,
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema"""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")



class DryingSchedulePredictionResponse(BaseModel):
    """Response schema for drying schedule prediction"""

    label: str = Field(..., description="Predicted label: needs_drying/no_drying")
    needs_drying: bool = Field(..., description="Whether drying is needed")
    days_to_target: int = Field(..., ge=0, description="Estimated days to target moisture")
    predicted_remaining_days: float = Field(..., ge=0.0, description="Raw model output (days)")
    target_moisture: float = Field(..., description="Target moisture percentage")

    class Config:
        json_schema_extra = {
            "example": {
                "label": "needs_drying",
                "needs_drying": True,
                "days_to_target": 3,
                "predicted_remaining_days": 2.7,
                "target_moisture": 13.0
            }
        }
