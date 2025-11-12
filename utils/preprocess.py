"""
Data preprocessing utilities for ScanLabel AI.
Handles data cleaning and feature extraction.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the Open Food Facts dataset by removing rows with missing nutrition data.
    
    Args:
        df: Raw DataFrame from Open Food Facts CSV
        
    Returns:
        Cleaned DataFrame with only rows containing complete nutrition information
    """
    # Required nutrition columns
    required_cols = [
        'energy_100g',
        'fat_100g',
        'sugars_100g',
        'salt_100g',
        'fiber_100g',
        'proteins_100g'
    ]
    
    # Remove rows where any required nutrition column is missing or NaN
    df_clean = df[required_cols].dropna()
    
    # Get indices of valid rows
    valid_indices = df_clean.index
    
    # Return full dataframe with only valid rows
    return df.loc[valid_indices].copy()


def create_health_label(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create health_label column based on nutrition thresholds.
    
    Health classification:
    - Healthy: low sugar (<5g), low fat (<3g), low salt (<0.3g)
    - Moderate: medium values
    - Unhealthy: high sugar (>=10g) OR high fat (>=10g) OR high salt (>=1g)
    
    Args:
        df: DataFrame with nutrition columns
        
    Returns:
        DataFrame with added 'health_label' column
    """
    df = df.copy()
    
    # Define thresholds
    SUGAR_HEALTHY = 5.0  # grams per 100g
    SUGAR_UNHEALTHY = 10.0
    FAT_HEALTHY = 3.0
    FAT_UNHEALTHY = 10.0
    SALT_HEALTHY = 0.3  # grams per 100g
    SALT_UNHEALTHY = 1.0
    
    # Initialize health labels
    health_labels = []
    
    for idx, row in df.iterrows():
        sugar = row.get('sugars_100g', 0)
        fat = row.get('fat_100g', 0)
        salt = row.get('salt_100g', 0)
        
        # Check for unhealthy conditions (high values)
        is_unhealthy = (
            sugar >= SUGAR_UNHEALTHY or
            fat >= FAT_UNHEALTHY or
            salt >= SALT_UNHEALTHY
        )
        
        # Check for healthy conditions (low values)
        is_healthy = (
            sugar < SUGAR_HEALTHY and
            fat < FAT_HEALTHY and
            salt < SALT_HEALTHY
        )
        
        # Assign label
        if is_unhealthy:
            health_labels.append('Unhealthy')
        elif is_healthy:
            health_labels.append('Healthy')
        else:
            health_labels.append('Moderate')
    
    df['health_label'] = health_labels
    return df


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract feature columns for model training.
    
    Args:
        df: DataFrame with nutrition columns
        
    Returns:
        DataFrame with only feature columns
    """
    feature_cols = [
        'energy_100g',
        'fat_100g',
        'sugars_100g',
        'salt_100g',
        'fiber_100g',
        'proteins_100g'
    ]
    
    return df[feature_cols].copy()


def preprocess_api_data(product_data: Dict) -> Optional[Dict]:
    """
    Preprocess product data from Open Food Facts API to match model input format.
    
    Args:
        product_data: Raw product data from API response
        
    Returns:
        Dictionary with preprocessed nutrition data, or None if data is incomplete
    """
    if not product_data or 'product' not in product_data:
        return None
    
    product = product_data['product']
    nutriments = product.get('nutriments', {})
    
    # Extract energy - prioritize kcal, convert kJ to kcal if needed
    energy_kcal = nutriments.get('energy-kcal_100g') or 0
    energy_kj = nutriments.get('energy-kj_100g') or nutriments.get('energy_100g') or 0
    
    # Convert kJ to kcal if we only have kJ (1 kcal = 4.184 kJ)
    if energy_kcal == 0 and energy_kj > 0:
        energy_kcal = energy_kj / 4.184
    
    # Extract nutrition values (handle missing values, use 0 as default)
    nutrition = {
        'energy_100g': energy_kcal,
        'fat_100g': nutriments.get('fat_100g') or 0,
        'sugars_100g': nutriments.get('sugars_100g') or 0,
        'salt_100g': nutriments.get('salt_100g') or 0,
        'fiber_100g': nutriments.get('fiber_100g') or 0,
        'proteins_100g': nutriments.get('proteins_100g') or 0
    }
    
    # More lenient check: accept if we have at least ONE meaningful nutrition value
    # (not all zeros, and at least one value > 0)
    has_data = any(v > 0 for v in nutrition.values())
    
    if not has_data:
        return None
    
    return nutrition

