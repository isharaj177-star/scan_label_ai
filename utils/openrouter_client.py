"""
OpenRouter API client for AI-powered healthier food alternatives.
Uses Gemini 2.0 Flash Experimental (free) for nutrition recommendations.
"""

import requests
import json
from typing import Dict, List, Optional
from config import settings
from utils.logger import logger


def generate_healthier_alternatives(
    product_name: str,
    brand: str,
    nutrition_data: dict,
    health_prediction: str,
    detected_issues: List[str]
) -> Optional[Dict]:
    """
    Generate healthier food alternatives using OpenRouter AI.

    Args:
        product_name: Name of the scanned product
        brand: Brand of the product
        nutrition_data: Dictionary with nutrition values per 100g
        health_prediction: Health level (Healthy/Moderate/Unhealthy)
        detected_issues: List of detected allergens, additives, etc.

    Returns:
        Dictionary with alternatives list and reasoning, or None if API fails
    """
    if not settings.OPENROUTER_API_KEY:
        logger.warning("OpenRouter API key not configured")
        return None

    try:
        # Build the prompt for the AI
        prompt = _build_alternatives_prompt(
            product_name,
            brand,
            nutrition_data,
            health_prediction,
            detected_issues
        )

        # Call OpenRouter API
        url = f"{settings.OPENROUTER_API_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://scanlabel-ai.com",  # Optional but recommended
            "X-Title": "ScanLabel AI"  # Optional but recommended
        }

        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a nutrition expert AI that recommends healthier food alternatives. Provide practical, achievable suggestions with clear reasoning based on nutritional data."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "response_format": {"type": "json_object"}  # Request JSON response
        }

        logger.info(f"Calling OpenRouter API with model: {settings.OPENROUTER_MODEL}")
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=settings.OPENROUTER_TIMEOUT
        )
        response.raise_for_status()

        result = response.json()

        # Extract the AI response
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']

            # Parse JSON response
            try:
                alternatives_data = json.loads(content)
                logger.info(f"Generated {len(alternatives_data.get('alternatives', []))} alternatives")
                return alternatives_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.error(f"Response content: {content}")
                return None
        else:
            logger.error("No choices in OpenRouter response")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Error generating alternatives: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def _build_alternatives_prompt(
    product_name: str,
    brand: str,
    nutrition_data: dict,
    health_prediction: str,
    detected_issues: List[str]
) -> str:
    """Build the prompt for AI to generate healthier alternatives."""

    # Extract nutrition values
    energy = nutrition_data.get('energy_100g', 0)
    sugar = nutrition_data.get('sugars_100g', 0)
    fat = nutrition_data.get('fat_100g', 0)
    salt = nutrition_data.get('salt_100g', 0)
    fiber = nutrition_data.get('fiber_100g', 0)
    protein = nutrition_data.get('proteins_100g', 0)

    # Identify main health concerns
    concerns = []
    if sugar >= 10:
        concerns.append(f"high sugar ({sugar:.1f}g)")
    if fat >= 10:
        concerns.append(f"high fat ({fat:.1f}g)")
    if salt >= 1:
        concerns.append(f"high salt ({salt:.2f}g)")
    if fiber < 3:
        concerns.append(f"low fiber ({fiber:.1f}g)")
    if protein < 5:
        concerns.append(f"low protein ({protein:.1f}g)")

    concerns_text = ", ".join(concerns) if concerns else "generally balanced nutrition"
    issues_text = ", ".join(detected_issues) if detected_issues else "none detected"

    prompt = f"""Analyze this food product and recommend 3-5 SPECIFIC healthier alternatives:

SCANNED PRODUCT:
- Name: {product_name}
- Brand: {brand}
- Health Level: {health_prediction}

NUTRITION (per 100g):
- Energy: {energy:.1f} kcal
- Sugar: {sugar:.1f}g
- Fat: {fat:.1f}g
- Salt: {salt:.2f}g
- Fiber: {fiber:.1f}g
- Protein: {protein:.1f}g

HEALTH CONCERNS: {concerns_text}
DETECTED ISSUES: {issues_text}

TASK: Recommend 3-5 specific, real product alternatives that are:
1. HEALTHIER - Lower in concerning nutrients (sugar/fat/salt), higher in beneficial ones (fiber/protein)
2. SIMILAR - Same food category and use case
3. AVAILABLE - Real products commonly found in supermarkets
4. SPECIFIC - Include actual brand names and product names when possible

Return your response as a JSON object with this EXACT structure:
{{
    "summary": "Brief 1-2 sentence summary of main health concerns with this product",
    "alternatives": [
        {{
            "name": "Specific product name",
            "brand": "Brand name (if known) or 'Generic'",
            "why_better": "Clear explanation of nutritional improvements",
            "key_benefits": ["benefit 1", "benefit 2", "benefit 3"],
            "estimated_improvements": {{
                "sugar": "e.g., 50% less sugar",
                "fat": "e.g., 30% less fat",
                "other": "other improvements"
            }}
        }}
    ],
    "general_tips": ["tip 1", "tip 2", "tip 3"]
}}

Ensure the response is valid JSON. Focus on practical, achievable swaps."""

    return prompt


def get_alternative_with_fallback(
    product_name: str,
    brand: str,
    nutrition_data: dict,
    health_prediction: str,
    detected_issues: List[str]
) -> Dict:
    """
    Get healthier alternatives with rule-based fallback if API fails.

    Returns:
        Dictionary with alternatives (either AI-generated or fallback)
    """
    # Try AI-powered recommendations first
    ai_result = generate_healthier_alternatives(
        product_name,
        brand,
        nutrition_data,
        health_prediction,
        detected_issues
    )

    if ai_result and 'alternatives' in ai_result:
        ai_result['source'] = 'ai_powered'
        return ai_result

    # Fallback to rule-based recommendations
    logger.info("Using rule-based fallback for alternatives")
    return _generate_fallback_alternatives(
        product_name,
        nutrition_data,
        health_prediction
    )


def _generate_fallback_alternatives(
    product_name: str,
    nutrition_data: dict,
    health_prediction: str
) -> Dict:
    """Generate simple rule-based alternatives when AI is unavailable."""

    sugar = nutrition_data.get('sugars_100g', 0)
    fat = nutrition_data.get('fat_100g', 0)
    salt = nutrition_data.get('salt_100g', 0)

    # Generic alternatives based on product category detection
    alternatives = []

    # Detect product category from name
    product_lower = product_name.lower()

    # Enhanced drink/beverage detection with common brand names and keywords
    drink_keywords = ['soda', 'cola', 'drink', 'juice', 'beverage', 'water', 'tea', 'coffee',
                      'pepsi', 'sprite', 'fanta', 'mountain dew', '7up', 'dr pepper',
                      'energy drink', 'sports drink', 'lemonade', 'iced tea', 'soft drink',
                      'carbonated', 'fizzy', 'orange soda', 'lemon', 'lime']

    if any(word in product_lower for word in drink_keywords):
        alternatives = [
            {
                "name": "100% Natural Orange Juice (No Added Sugar)",
                "brand": "Generic",
                "why_better": "Natural fruit sugars with vitamins instead of added sugars and artificial ingredients",
                "key_benefits": ["No added sugar", "Vitamin C", "Natural nutrients"],
                "estimated_improvements": {"added_sugar": "100% less", "vitamins": "High in Vitamin C"}
            },
            {
                "name": "Sparkling Water with Natural Fruit",
                "brand": "Generic",
                "why_better": "Zero sugar and calories while still providing refreshing taste",
                "key_benefits": ["No added sugar", "Zero calories", "Natural hydration"],
                "estimated_improvements": {"sugar": "100% less sugar", "calories": "100% less calories"}
            },
            {
                "name": "Unsweetened Iced Tea",
                "brand": "Generic",
                "why_better": "Natural antioxidants without added sugars",
                "key_benefits": ["No added sugar", "Contains antioxidants", "Low calorie"],
                "estimated_improvements": {"sugar": "100% less sugar", "antioxidants": "Added"}
            },
            {
                "name": "Coconut Water",
                "brand": "Generic",
                "why_better": "Natural electrolytes with naturally occurring sugars only",
                "key_benefits": ["Natural electrolytes", "Lower sugar", "Potassium rich"],
                "estimated_improvements": {"sugar": "50% less sugar", "electrolytes": "Natural"}
            }
        ]
    elif any(word in product_lower for word in ['chips', 'crisp', 'snack']):
        alternatives = [
            {
                "name": "Baked Vegetable Chips",
                "brand": "Generic",
                "why_better": "Baked instead of fried, made from real vegetables",
                "key_benefits": ["Lower fat", "More fiber", "Real vegetables"],
                "estimated_improvements": {"fat": "50% less fat", "fiber": "2x more fiber"}
            },
            {
                "name": "Air-Popped Popcorn",
                "brand": "Generic",
                "why_better": "Whole grain with minimal fat and salt",
                "key_benefits": ["Whole grain", "High fiber", "Lower calories"],
                "estimated_improvements": {"fat": "70% less fat", "fiber": "3x more fiber"}
            },
            {
                "name": "Rice Cakes",
                "brand": "Generic",
                "why_better": "Light, crunchy alternative with less fat and salt",
                "key_benefits": ["Low fat", "Low sodium", "Whole grain options"],
                "estimated_improvements": {"fat": "80% less fat", "salt": "60% less salt"}
            }
        ]
    elif any(word in product_lower for word in ['chocolate', 'candy', 'sweet']):
        alternatives = [
            {
                "name": "Dark Chocolate (70%+ cocoa)",
                "brand": "Generic",
                "why_better": "Higher cocoa content, less sugar, contains antioxidants",
                "key_benefits": ["Less sugar", "Antioxidants", "Heart-healthy"],
                "estimated_improvements": {"sugar": "40% less sugar", "antioxidants": "High"}
            },
            {
                "name": "Fresh Fruit with Yogurt",
                "brand": "Generic",
                "why_better": "Natural sugars with added protein and vitamins",
                "key_benefits": ["Natural sugars", "High protein", "Vitamins"],
                "estimated_improvements": {"sugar": "Natural only", "protein": "Added", "vitamins": "High"}
            },
            {
                "name": "Dried Fruit (no added sugar)",
                "brand": "Generic",
                "why_better": "Natural sweetness with fiber and nutrients",
                "key_benefits": ["Natural sugars", "High fiber", "Vitamins"],
                "estimated_improvements": {"fiber": "10x more fiber", "vitamins": "Added"}
            }
        ]
    else:
        # Generic healthy alternatives
        alternatives = [
            {
                "name": "Fresh Fruits and Vegetables",
                "brand": "Generic",
                "why_better": "Whole foods with natural nutrients and fiber",
                "key_benefits": ["Natural nutrients", "High fiber", "Low calories"],
                "estimated_improvements": {"fiber": "Much higher", "vitamins": "Abundant"}
            },
            {
                "name": "Whole Grain Products",
                "brand": "Generic",
                "why_better": "Complex carbohydrates and higher fiber content",
                "key_benefits": ["Whole grains", "High fiber", "Sustained energy"],
                "estimated_improvements": {"fiber": "3-5x more", "nutrients": "More complete"}
            },
            {
                "name": "Low-Fat Dairy or Plant-Based Alternatives",
                "brand": "Generic",
                "why_better": "Protein-rich with less fat and often fortified",
                "key_benefits": ["High protein", "Lower fat", "Calcium fortified"],
                "estimated_improvements": {"fat": "50-70% less", "protein": "High"}
            }
        ]

    # Build summary based on health concerns
    summary_parts = []
    if sugar >= 10:
        summary_parts.append(f"high sugar content ({sugar:.1f}g)")
    if fat >= 10:
        summary_parts.append(f"high fat ({fat:.1f}g)")
    if salt >= 1:
        summary_parts.append(f"high salt ({salt:.2f}g)")

    if summary_parts:
        summary = f"This product has {', '.join(summary_parts)}. Consider healthier alternatives to reduce intake of these nutrients."
    else:
        summary = "While this product has moderate nutrition, there are healthier options available with better nutritional profiles."

    return {
        "summary": summary,
        "alternatives": alternatives[:4],  # Return top 4 alternatives
        "general_tips": [
            "Choose products with simpler ingredient lists",
            "Look for items with higher fiber content",
            "Opt for products with less added sugars and sodium",
            "Consider whole food alternatives when possible"
        ],
        "source": "rule_based_fallback"
    }
