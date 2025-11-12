"""
Tests for preprocessing utilities.
"""

import pytest
import pandas as pd
import numpy as np
from utils.preprocess import (
    clean_dataset,
    create_health_label,
    extract_features,
    preprocess_api_data
)


def test_clean_dataset():
    """Test dataset cleaning removes rows with missing nutrition data."""
    # Create test data with some missing values
    data = {
        'energy_100g': [100, 200, np.nan, 300],
        'fat_100g': [5, 10, 15, np.nan],
        'sugars_100g': [5, 10, 15, 20],
        'salt_100g': [0.5, 1.0, 1.5, 2.0],
        'fiber_100g': [2, 3, 4, 5],
        'proteins_100g': [10, 15, 20, 25]
    }
    df = pd.DataFrame(data)
    
    cleaned = clean_dataset(df)
    
    # Should only keep rows without NaN
    assert len(cleaned) == 2
    assert cleaned.iloc[0]['energy_100g'] == 100
    assert cleaned.iloc[1]['energy_100g'] == 200


def test_create_health_label():
    """Test health label creation based on thresholds."""
    data = {
        'energy_100g': [100, 200, 300],
        'fat_100g': [1, 5, 15],
        'sugars_100g': [2, 7, 12],
        'salt_100g': [0.1, 0.5, 1.5],
        'fiber_100g': [2, 3, 4],
        'proteins_100g': [10, 15, 20]
    }
    df = pd.DataFrame(data)
    
    labeled = create_health_label(df)
    
    assert 'health_label' in labeled.columns
    assert labeled.iloc[0]['health_label'] == 'Healthy'
    assert labeled.iloc[1]['health_label'] == 'Moderate'
    assert labeled.iloc[2]['health_label'] == 'Unhealthy'


def test_extract_features():
    """Test feature extraction."""
    data = {
        'energy_100g': [100],
        'fat_100g': [5],
        'sugars_100g': [10],
        'salt_100g': [1],
        'fiber_100g': [2],
        'proteins_100g': [15],
        'other_col': [999]  # Should be excluded
    }
    df = pd.DataFrame(data)
    
    features = extract_features(df)
    
    assert len(features.columns) == 6
    assert 'other_col' not in features.columns
    assert 'energy_100g' in features.columns


def test_preprocess_api_data(sample_product_data):
    """Test API data preprocessing."""
    result = preprocess_api_data(sample_product_data)
    
    assert result is not None
    assert 'energy_100g' in result
    assert 'fat_100g' in result
    assert result['energy_100g'] == 200.0


def test_preprocess_api_data_invalid():
    """Test preprocessing with invalid data."""
    result = preprocess_api_data({})
    assert result is None
    
    result = preprocess_api_data({'product': {}})
    assert result is None








