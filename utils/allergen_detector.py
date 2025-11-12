"""
NLP-based allergen and harmful additive detection from ingredient text.
"""

import re
from typing import List, Set, Dict


# Common allergens and harmful additives
ALLERGENS = {
    'gluten', 'wheat', 'barley', 'rye', 'oats',
    'milk', 'lactose', 'dairy',
    'eggs', 'egg',
    'soy', 'soya', 'soybean',
    'nuts', 'peanuts', 'almonds', 'walnuts', 'cashews', 'hazelnuts',
    'fish', 'shellfish', 'crustaceans',
    'sesame', 'mustard', 'celery', 'sulphites', 'sulfites'
}

HARMFUL_ADDITIVES = {
    'aspartame', 'saccharin', 'sucralose', 'acesulfame',
    'msg', 'monosodium glutamate',
    'sodium nitrite', 'sodium nitrate',
    'bha', 'bht', 'butylated hydroxyanisole', 'butylated hydroxytoluene',
    'tartrazine', 'yellow 5', 'red 40', 'blue 1',
    'sodium benzoate', 'potassium benzoate',
    'high fructose corn syrup', 'hfcs',
    'trans fat', 'partially hydrogenated',
    'artificial flavors', 'artificial flavoring',
    'artificial colors', 'artificial coloring'
}

HIGH_SUGAR_INDICATORS = {
    'sugar', 'sucrose', 'fructose', 'glucose', 'dextrose',
    'corn syrup', 'cane sugar', 'brown sugar', 'honey',
    'molasses', 'maple syrup', 'agave'
}


def detect_allergens(ingredients_text: str) -> List[str]:
    """
    Detect allergens from ingredient text using keyword matching.
    
    Args:
        ingredients_text: Raw ingredient text from product
        
    Returns:
        List of detected allergens
    """
    if not ingredients_text:
        return []
    
    # Normalize text (lowercase, remove punctuation for better matching)
    text_lower = ingredients_text.lower()
    
    detected = []
    
    # Check for allergens
    for allergen in ALLERGENS:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(allergen.lower()) + r'\b'
        if re.search(pattern, text_lower):
            detected.append(allergen.capitalize())
    
    return list(set(detected))  # Remove duplicates


def detect_harmful_additives(ingredients_text: str) -> List[str]:
    """
    Detect harmful additives from ingredient text.
    
    Args:
        ingredients_text: Raw ingredient text from product
        
    Returns:
        List of detected harmful additives
    """
    if not ingredients_text:
        return []
    
    text_lower = ingredients_text.lower()
    detected = []
    
    # Check for harmful additives
    for additive in HARMFUL_ADDITIVES:
        pattern = r'\b' + re.escape(additive.lower()) + r'\b'
        if re.search(pattern, text_lower):
            # Format the additive name nicely
            formatted = additive.replace('_', ' ').title()
            detected.append(formatted)
    
    return list(set(detected))


def detect_high_sugar_indicators(ingredients_text: str) -> List[str]:
    """
    Detect high sugar indicators from ingredient text.
    
    Args:
        ingredients_text: Raw ingredient text from product
        
    Returns:
        List of detected sugar-related ingredients
    """
    if not ingredients_text:
        return []
    
    text_lower = ingredients_text.lower()
    detected = []
    
    for indicator in HIGH_SUGAR_INDICATORS:
        pattern = r'\b' + re.escape(indicator.lower()) + r'\b'
        if re.search(pattern, text_lower):
            formatted = indicator.replace('_', ' ').title()
            detected.append(formatted)
    
    return list(set(detected))


def analyze_ingredients(ingredients_text: str) -> Dict[str, List[str]]:
    """
    Comprehensive ingredient analysis combining all detection methods.
    
    Args:
        ingredients_text: Raw ingredient text from product
        
    Returns:
        Dictionary with detected allergens, additives, and sugar indicators
    """
    return {
        'allergens': detect_allergens(ingredients_text),
        'harmful_additives': detect_harmful_additives(ingredients_text),
        'sugar_indicators': detect_high_sugar_indicators(ingredients_text)
    }

