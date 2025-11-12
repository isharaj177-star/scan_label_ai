"""
Pytest configuration and fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_nutrition_data():
    """Sample nutrition data for testing."""
    return {
        'energy_100g': 200.0,
        'fat_100g': 5.0,
        'sugars_100g': 8.0,
        'salt_100g': 0.5,
        'fiber_100g': 2.0,
        'proteins_100g': 10.0
    }


@pytest.fixture
def sample_product_data():
    """Sample product data from Open Food Facts API."""
    return {
        'status': 1,
        'product': {
            'product_name': 'Test Product',
            'brands': 'Test Brand',
            'ingredients_text': 'Sugar, Water, Salt',
            'nutriments': {
                'energy-kcal_100g': 200.0,
                'fat_100g': 5.0,
                'sugars_100g': 8.0,
                'salt_100g': 0.5,
                'fiber_100g': 2.0,
                'proteins_100g': 10.0
            }
        }
    }


@pytest.fixture
def healthy_nutrition_data():
    """Nutrition data for a healthy product."""
    return {
        'energy_100g': 50.0,
        'fat_100g': 1.0,
        'sugars_100g': 2.0,
        'salt_100g': 0.1,
        'fiber_100g': 5.0,
        'proteins_100g': 3.0
    }


@pytest.fixture
def unhealthy_nutrition_data():
    """Nutrition data for an unhealthy product."""
    return {
        'energy_100g': 500.0,
        'fat_100g': 25.0,
        'sugars_100g': 50.0,
        'salt_100g': 2.0,
        'fiber_100g': 0.0,
        'proteins_100g': 1.0
    }








