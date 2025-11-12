"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal


class Nutrients(BaseModel):
    """Nutrition information model."""
    energy_100g: float = Field(..., ge=0, description="Energy per 100g (kcal)")
    sugars_100g: float = Field(..., ge=0, description="Sugars per 100g (g)")
    fat_100g: float = Field(..., ge=0, description="Fat per 100g (g)")
    salt_100g: float = Field(..., ge=0, description="Salt per 100g (g)")
    fiber_100g: float = Field(..., ge=0, description="Fiber per 100g (g)")
    proteins_100g: float = Field(..., ge=0, description="Proteins per 100g (g)")


class ScanResponse(BaseModel):
    """Response model for product scan."""
    product_name: str = Field(..., description="Product name")
    brand: str = Field(..., description="Product brand")
    barcode: str = Field(..., description="Product barcode")
    health_prediction: Literal["Healthy", "Moderate", "Unhealthy"] = Field(
        ..., 
        description="Predicted health level"
    )
    nutrients: Nutrients = Field(..., description="Nutrition information")
    detected_allergens: List[str] = Field(
        default_factory=list,
        description="List of detected allergens"
    )
    detected_additives: List[str] = Field(
        default_factory=list,
        description="List of detected harmful additives"
    )
    detected_sugar_indicators: List[str] = Field(
        default_factory=list,
        description="List of detected sugar indicators"
    )
    message: str = Field(..., description="Human-readable health message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "Coca-Cola",
                "brand": "Coca-Cola Company",
                "barcode": "5449000000996",
                "health_prediction": "Unhealthy",
                "nutrients": {
                    "energy_100g": 42.0,
                    "sugars_100g": 10.6,
                    "fat_100g": 0.0,
                    "salt_100g": 0.0,
                    "fiber_100g": 0.0,
                    "proteins_100g": 0.0
                },
                "detected_allergens": [],
                "detected_additives": [],
                "detected_sugar_indicators": ["Sugar"],
                "message": "This product has high levels of sugar, fat, or salt — consume occasionally. High sugar content (10.6g per 100g). Contains: Sugar."
            }
        }


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""
    status: Literal["healthy", "unhealthy"] = Field(..., description="API status")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")
    version: str = Field(..., description="API version")
    
    class Config:
        populate_by_name = True
        protected_namespaces = ()  # Fix Pydantic v2 warning about "model_" namespace


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    status_code: int = Field(..., description="HTTP status code")

