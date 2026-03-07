from pydantic import BaseModel, Field
from typing import Literal


class RiceVarietyPredictionRequest(BaseModel):
    """Request schema for rice variety prediction"""

    # Numerical features
    pH: float = Field(..., ge=0.0, le=14.0, description="Soil pH level (0-14)")
    soil_moisture_pct: float = Field(..., ge=0.0, le=100.0, description="Soil moisture percentage (0-100)")
    EC_dS_m: float = Field(..., ge=0.0, description="Electrical conductivity (dS/m)")
    soil_temp_C: float = Field(..., ge=0.0, le=50.0, description="Soil temperature in Celsius")
    water_depth_cm: float = Field(..., ge=0.0, description="Water depth in centimeters")
    lat: float = Field(..., ge=5.0, le=10.0, description="Latitude (Sri Lanka: 5-10)")
    lon: float = Field(..., ge=79.0, le=82.0, description="Longitude (Sri Lanka: 79-82)")

    # Categorical features
    texture: Literal["loamy", "sandy", "clayey"] = Field(..., description="Soil texture type")
    prev_crop: Literal["rice", "maize", "fallow", "legume", "vegetable"] = Field(
        ..., description="Previous crop type"
    )
    season: Literal["Maha", "Yala"] = Field(..., description="Season (Maha or Yala)")
    soil_zone: Literal["Dry", "Intermediate", "Wet"] = Field(..., description="Soil zone type")

    # Optional: number of top recommendations
    top_n: int = Field(
        default=3,
        ge=1,
        le=7,
        description="Number of top variety recommendations to return",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pH": 6.0,
                "soil_moisture_pct": 45.0,
                "EC_dS_m": 1.5,
                "soil_temp_C": 28.0,
                "water_depth_cm": 5.0,
                "lat": 7.5,
                "lon": 80.5,
                "texture": "loamy",
                "prev_crop": "rice",
                "season": "Maha",
                "soil_zone": "Intermediate",
                "top_n": 3,
            }
        }


class SeedMoisturePredictionRequest(BaseModel):
    """Request schema for seed moisture prediction"""

    cap_sensor_value: float = Field(..., description="Capacitive sensor reading")
    sample_temperature: float = Field(..., description="Sample temperature (°C)")
    ambient_temperature: float = Field(..., description="Ambient temperature (°C)")
    ambient_humidity: float = Field(..., description="Ambient relative humidity (%)")
    sample_weight: float = Field(..., description="Sample weight (g)")
    bulk_density: float = Field(..., description="Bulk density (g/cm³)")

    class Config:
        json_schema_extra = {
            "example": {
                "cap_sensor_value": 523.63,
                "sample_temperature": 30.57,
                "ambient_temperature": 34.08,
                "ambient_humidity": 50.0,
                "sample_weight": 5.25,
                "bulk_density": 0.75,
            }
        }


class SeedDetectionPredictionRequest(BaseModel):
    """Request schema for paddy seed classification (image as base64)"""

    image_base64: str = Field(
        ...,
        description="Base64-encoded image string (JPEG/PNG). Optional prefix: data:image/jpeg;base64,",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
            }
        }
