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
    recommendations: List[VarietyRecommendation] = Field(..., description="Top N variety recommendations")
    all_predictions: dict[str, float] = Field(..., description="Predicted yields for all varieties")
    
    class Config:
        json_schema_extra = {
            "example": {
                "best_variety": "AT378",
                "expected_yield": 9486.79,
                "recommendations": [
                    {"variety": "AT378", "predicted_yield": 9486.79, "rank": 1},
                    {"variety": "AT362", "predicted_yield": 8591.04, "rank": 2},
                    {"variety": "BG374", "predicted_yield": 8195.82, "rank": 3}
                ],
                "all_predictions": {
                    "AT378": 9486.79,
                    "AT362": 8591.04,
                    "BG374": 8195.82,
                    "BG352": 7830.89,
                    "BG300": 6926.69,
                    "LD365": 5612.45,
                    "BW367": 5234.12
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

