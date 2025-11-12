"""
Data fetching utilities for Open Food Facts API integration.
"""

import requests
from typing import Dict, Optional
from config import settings
from utils.logger import logger


def fetch_product_by_barcode(barcode: str) -> Optional[Dict]:
    """
    Fetch product information from Open Food Facts API using barcode.
    Tries multiple barcode formats if the first attempt fails.
    
    Args:
        barcode: Product barcode (EAN-13, EAN-8, UPC-A, etc.)
        
    Returns:
        Dictionary containing product data, or None if not found
    """
    # Try the barcode as-is first
    barcode_variants = [barcode.strip()]
    
    # If it's a short numeric code (8 digits), try padding with zeros for EAN-13
    if barcode.isdigit() and len(barcode) == 8:
        # EAN-8 codes are valid, but sometimes products are stored with EAN-13 format
        # Try padding with zeros (though this is less common)
        padded = '0' * (13 - len(barcode)) + barcode
        barcode_variants.append(padded)
    
    # Try each variant
    for barcode_to_try in barcode_variants:
        url = f"{settings.OFF_API_BASE_URL}/product/{barcode_to_try}.json"
        
        try:
            logger.debug(f"Fetching product data from: {url}")
            response = requests.get(url, timeout=settings.OFF_API_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if product was found
            if data.get('status') == 1:
                logger.debug(f"Product found for barcode: {barcode_to_try}")
                return data
            else:
                logger.debug(f"Product not found for barcode: {barcode_to_try}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching product data for {barcode_to_try}: {e}")
            continue
    
    # None of the variants worked
    logger.warning(f"Product not found for barcode {barcode} (tried variants: {barcode_variants})")
    return None


def extract_product_info(product_data: Dict) -> Dict:
    """
    Extract relevant product information from API response.
    
    Args:
        product_data: Raw product data from Open Food Facts API
        
    Returns:
        Dictionary with extracted product information
    """
    if not product_data or 'product' not in product_data:
        return {}
    
    product = product_data['product']
    nutriments = product.get('nutriments', {})
    
    # Extract energy - prioritize kcal, convert kJ to kcal if needed
    energy_kcal = nutriments.get('energy-kcal_100g') or 0
    energy_kj = nutriments.get('energy-kj_100g') or nutriments.get('energy_100g') or 0
    
    # Convert kJ to kcal if we only have kJ (1 kcal = 4.184 kJ)
    if energy_kcal == 0 and energy_kj > 0:
        energy_kcal = energy_kj / 4.184
    
    # Extract product details
    info = {
        'product_name': product.get('product_name', 'Unknown Product'),
        'brand': product.get('brands', 'Unknown Brand'),
        'ingredients_text': product.get('ingredients_text', ''),
        'nutriments': {
            'energy_100g': energy_kcal,
            'fat_100g': nutriments.get('fat_100g') or 0,
            'sugars_100g': nutriments.get('sugars_100g') or 0,
            'salt_100g': nutriments.get('salt_100g') or 0,
            'fiber_100g': nutriments.get('fiber_100g') or 0,
            'proteins_100g': nutriments.get('proteins_100g') or 0
        }
    }
    
    return info

