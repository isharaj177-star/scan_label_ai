"""
Tests for allergen and additive detection.
"""

import pytest
from utils.allergen_detector import (
    detect_allergens,
    detect_harmful_additives,
    detect_high_sugar_indicators,
    analyze_ingredients
)


def test_detect_allergens():
    """Test allergen detection."""
    text = "Contains milk, eggs, and gluten"
    allergens = detect_allergens(text)
    
    assert len(allergens) >= 3
    assert any('Milk' in a or 'milk' in a.lower() for a in allergens)
    assert any('Egg' in a or 'egg' in a.lower() for a in allergens)
    assert any('Gluten' in a or 'gluten' in a.lower() for a in allergens)


def test_detect_harmful_additives():
    """Test harmful additive detection."""
    text = "Contains aspartame and MSG"
    additives = detect_harmful_additives(text)
    
    assert len(additives) >= 2
    assert any('aspartame' in a.lower() for a in additives)
    assert any('msg' in a.lower() for a in additives)


def test_detect_sugar_indicators():
    """Test sugar indicator detection."""
    text = "Contains sugar, high fructose corn syrup, and honey"
    indicators = detect_high_sugar_indicators(text)
    
    assert len(indicators) >= 3
    assert any('sugar' in i.lower() for i in indicators)


def test_analyze_ingredients():
    """Test comprehensive ingredient analysis."""
    text = "Water, sugar, milk, aspartame"
    analysis = analyze_ingredients(text)
    
    assert 'allergens' in analysis
    assert 'harmful_additives' in analysis
    assert 'sugar_indicators' in analysis
    assert isinstance(analysis['allergens'], list)
    assert isinstance(analysis['harmful_additives'], list)
    assert isinstance(analysis['sugar_indicators'], list)


def test_empty_ingredients():
    """Test with empty ingredient text."""
    assert detect_allergens("") == []
    assert detect_harmful_additives("") == []
    assert detect_high_sugar_indicators("") == []








