"""
Model prediction utilities for health classification.
"""

import joblib
import numpy as np
import pandas as pd
from typing import Dict, Optional
import os
from utils.logger import logger


def load_model(model_path: str = 'model.pkl') -> Optional[object]:
    """
    Load the trained machine learning model from disk.
    
    Args:
        model_path: Path to the saved model file
        
    Returns:
        Loaded model object, or None if loading fails
    """
    try:
        if not os.path.exists(model_path):
            logger.error(f"Model file not found at {model_path}")
            return None
        
        logger.info(f"Loading model from {model_path}")
        model = joblib.load(model_path)
        logger.info("Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None


def predict_health(nutrition_data: Dict, model) -> Optional[str]:
    """
    Predict health label for a product based on nutrition data.
    
    Args:
        nutrition_data: Dictionary with nutrition values
        model: Trained scikit-learn model
        
    Returns:
        Predicted health label ('Healthy', 'Moderate', or 'Unhealthy'), or None if prediction fails
    """
    if model is None:
        return None
    
    try:
        # Extract features in the correct order
        feature_order = [
            'energy_100g',
            'fat_100g',
            'sugars_100g',
            'salt_100g',
            'fiber_100g',
            'proteins_100g'
        ]
        
        # Create feature array
        features = np.array([[nutrition_data.get(col, 0) for col in feature_order]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        
        logger.debug(f"Prediction made: {prediction}")
        return prediction
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        return None

