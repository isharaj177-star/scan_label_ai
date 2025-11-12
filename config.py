"""
Configuration management for ScanLabel AI.
Loads settings from environment variables with sensible defaults.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    API_TITLE: str = "ScanLabel AI"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Intelligent food-scanning and health analysis system"
    
    # Server Settings
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    DEBUG: bool = Field(default=False)
    RELOAD: bool = Field(default=False)
    
    # Model Settings
    MODEL_PATH: str = Field(default="model.pkl")
    
    # Open Food Facts API Settings
    OFF_API_BASE_URL: str = Field(default="https://world.openfoodfacts.org/api/v0")
    OFF_API_TIMEOUT: int = Field(default=10)
    
    # Spoonacular API Settings (for food image recognition - fallback)
    SPOONACULAR_API_KEY: Optional[str] = Field(default=None)
    SPOONACULAR_API_BASE_URL: str = Field(default="https://api.spoonacular.com")
    SPOONACULAR_API_TIMEOUT: int = Field(default=15)
    
    # Google Cloud Vision API Settings (primary for food image recognition)
    # Free tier: 1000 requests/month
    # Setup: https://cloud.google.com/vision/docs/setup
    GOOGLE_VISION_API_KEY: Optional[str] = Field(default=None)
    GOOGLE_VISION_API_ENABLED: bool = Field(default=True)
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Training Settings
    TRAINING_TEST_SIZE: float = Field(default=0.2)
    TRAINING_RANDOM_STATE: int = Field(default=42)
    TRAINING_N_ESTIMATORS: int = Field(default=100)
    TRAINING_MAX_DEPTH: int = Field(default=10)
    
    # Health Classification Thresholds
    SUGAR_HEALTHY_THRESHOLD: float = Field(default=5.0)
    SUGAR_UNHEALTHY_THRESHOLD: float = Field(default=10.0)
    FAT_HEALTHY_THRESHOLD: float = Field(default=3.0)
    FAT_UNHEALTHY_THRESHOLD: float = Field(default=10.0)
    SALT_HEALTHY_THRESHOLD: float = Field(default=0.3)
    SALT_UNHEALTHY_THRESHOLD: float = Field(default=1.0)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()

