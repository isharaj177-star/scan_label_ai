"""
Food image recognition using Google Cloud Vision API.
Recognizes food items from images and provides nutrition information.
"""

import requests
import base64
import json
from typing import Dict, Optional, List
from io import BytesIO
from PIL import Image
from urllib.parse import quote
from config import settings
from utils.logger import logger


def recognize_food_with_google_vision(image_data: bytes) -> Optional[Dict]:
    """
    Recognize food from image using Google Cloud Vision API.
    Free tier: 1000 requests/month
    
    Args:
        image_data: Image bytes data
        
    Returns:
        Dictionary with recognized food information, or None if recognition fails
    """
    if not settings.GOOGLE_VISION_API_KEY or not settings.GOOGLE_VISION_API_ENABLED:
        logger.debug("Google Vision API not configured, skipping...")
        print("DEBUG: Google Vision API key check failed", flush=True)
        print(f"DEBUG: API Key exists: {bool(settings.GOOGLE_VISION_API_KEY)}", flush=True)
        print(f"DEBUG: API Enabled: {settings.GOOGLE_VISION_API_ENABLED}", flush=True)
        return None
    
    print(f"\n{'='*60}", flush=True)
    print("GOOGLE VISION API - RECOGNIZE_FOOD CALLED", flush=True)
    print(f"Image size: {len(image_data)} bytes", flush=True)
    print(f"API Key (first 10 chars): {settings.GOOGLE_VISION_API_KEY[:10] if settings.GOOGLE_VISION_API_KEY else 'NONE'}...", flush=True)
    
    try:
        # Encode image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Google Cloud Vision API endpoint
        # Clean and validate API key
        api_key = settings.GOOGLE_VISION_API_KEY.strip()
        # Remove any quotes that might have been added accidentally
        api_key = api_key.strip('"').strip("'")
        
        # URL-encode the API key to handle any special characters
        api_key_encoded = quote(api_key, safe='')
        
        # Validate API key format (should start with AIzaSy for Google API keys)
        if not api_key.startswith('AIzaSy'):
            logger.warning(f"API key format looks incorrect. Google API keys usually start with 'AIzaSy'. Got: {api_key[:10]}...")
            print(f"WARNING: API key format may be incorrect. Expected format: AIzaSy...", flush=True)
            print(f"DEBUG: Full API key length: {len(api_key)} characters", flush=True)
        
        # Use URL-encoded key in query parameter
        url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key_encoded}"
        
        # Request payload for object detection (food detection)
        payload = {
            "requests": [
                {
                    "image": {
                        "content": image_base64
                    },
                    "features": [
                        {
                            "type": "OBJECT_LOCALIZATION",
                            "maxResults": 10
                        },
                        {
                            "type": "LABEL_DETECTION",
                            "maxResults": 10
                        }
                    ]
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        print(f"Calling Google Vision API...", flush=True)
        print(f"URL: {url[:80]}...", flush=True)
        print(f"Payload size: {len(json.dumps(payload))} bytes", flush=True)
        print(f"Timeout: 10 seconds", flush=True)
        
        # Use shorter timeout to avoid hanging
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"Response status: {response.status_code}", flush=True)
        print(f"Response headers: {dict(response.headers)}", flush=True)
        
        if response.status_code == 200:
            data = response.json()
            responses = data.get('responses', [])
            
            if not responses:
                logger.warning("Google Vision API returned empty response")
                return None
            
            first_response = responses[0]
            
            # Extract food-related labels
            labels = first_response.get('localizedObjectAnnotations', [])
            label_detections = first_response.get('labelAnnotations', [])
            
            # Look for food-related objects
            food_items = []
            for obj in labels:
                obj_name = obj.get('name', '').lower()
                score = obj.get('score', 0)
                # Common food objects
                if any(food in obj_name for food in ['food', 'fruit', 'vegetable', 'apple', 'banana', 'bread', 'dish', 'meal']):
                    food_items.append({
                        'name': obj.get('name', ''),
                        'confidence': score
                    })
            
            # Also check label detections for food-related labels
            for label in label_detections:
                label_desc = label.get('description', '').lower()
                score = label.get('score', 0)
                # Food-related keywords
                food_keywords = ['food', 'fruit', 'vegetable', 'apple', 'banana', 'orange', 'bread', 
                               'rice', 'noodle', 'pasta', 'dish', 'meal', 'snack', 'dessert']
                if any(keyword in label_desc for keyword in food_keywords) and score > 0.5:
                    food_items.append({
                        'name': label.get('description', ''),
                        'confidence': score
                    })
            
            if food_items:
                # Sort by confidence and get the best match
                food_items.sort(key=lambda x: x['confidence'], reverse=True)
                best_match = food_items[0]
                
                logger.info(f"Google Vision recognized: {best_match['name']} (confidence: {best_match['confidence']:.2f})")
                
                return {
                    'category': best_match['name'],
                    'categoryType': '',
                    'confidence': best_match['confidence'],
                    'name': best_match['name']
                }
            else:
                logger.warning("Google Vision API found no food items in image")
                return None
                
        elif response.status_code == 400:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                error_status = error_data.get('error', {}).get('status', '')
                error_details = error_data.get('error', {}).get('details', [])
                
                logger.error(f"Google Vision API error 400: {error_msg}")
                logger.error(f"Error status: {error_status}")
                print(f"ERROR 400: {error_msg}", flush=True)
                print(f"Error status: {error_status}", flush=True)
                if error_details:
                    print(f"Error details: {error_details}", flush=True)
                print(f"Full error response: {json.dumps(error_data, indent=2)}", flush=True)
                
                # Provide helpful troubleshooting info
                if 'API key' in error_msg or 'key' in error_msg.lower():
                    print("\n" + "="*60, flush=True)
                    print("TROUBLESHOOTING API KEY ISSUE:", flush=True)
                    print("="*60, flush=True)
                    print("1. Verify API key in Google Cloud Console:", flush=True)
                    print("   https://console.cloud.google.com/apis/credentials", flush=True)
                    print("2. Ensure Vision API is enabled for your project:", flush=True)
                    print("   https://console.cloud.google.com/apis/library/vision.googleapis.com", flush=True)
                    print("3. Check API key restrictions (if any):", flush=True)
                    print("   - Make sure 'Cloud Vision API' is allowed", flush=True)
                    print("4. Verify billing is enabled (required for Vision API)", flush=True)
                    print("="*60 + "\n", flush=True)
            except Exception as e:
                logger.error(f"Google Vision API error 400: {response.text[:500]}")
                logger.error(f"Failed to parse error response: {e}")
                print(f"ERROR 400 (non-JSON): {response.text[:500]}", flush=True)
            return None
        elif response.status_code == 403:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Permission denied')
                error_reason = error_data.get('error', {}).get('details', [{}])[0].get('reason', 'UNKNOWN')

                logger.error(f"Google Vision API error 403: {error_msg}")
                print(f"\n{'='*60}", flush=True)
                print("GOOGLE VISION API - ERROR 403", flush=True)
                print(f"{'='*60}", flush=True)

                if 'BILLING_DISABLED' in error_reason or 'billing' in error_msg.lower():
                    print("BILLING NOT ENABLED!", flush=True)
                    print("", flush=True)
                    print("Google Vision API requires billing to be enabled,", flush=True)
                    print("even though the first 1000 requests/month are FREE.", flush=True)
                    print("", flush=True)
                    print("TO FIX:", flush=True)
                    print("1. Go to: https://console.cloud.google.com/billing", flush=True)
                    print("2. Enable billing for your project", flush=True)
                    print("3. You can set spending limits to $0 after enabling", flush=True)
                    print("4. First 1000 Vision API calls/month are free", flush=True)
                    print("", flush=True)
                    print("ALTERNATIVE: Use barcode scanning - works perfectly!", flush=True)
                else:
                    print(f"Error: {error_msg}", flush=True)
                    print(f"Reason: {error_reason}", flush=True)

                print(f"{'='*60}", flush=True)
                logger.error(f"Full error: {error_data}")
            except Exception as e:
                logger.error(f"Google Vision API error 403: Permission denied")
                print(f"ERROR 403: Permission denied - {response.text[:500]}", flush=True)
            return None
        else:
            logger.error(f"Google Vision API error: {response.status_code} - {response.text[:200]}")
            print(f"ERROR {response.status_code}: {response.text[:500]}", flush=True)
            return None
            
    except requests.exceptions.Timeout as e:
        logger.error(f"Google Vision API timeout after 10 seconds: {e}")
        print(f"TIMEOUT: Google Vision API took too long (>10s)", flush=True)
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Google Vision API: {e}")
        print(f"ERROR: Network error: {e}", flush=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error in Google Vision recognition: {e}")
        print(f"ERROR: Unexpected error: {e}", flush=True)
        import traceback
        print(traceback.format_exc(), flush=True)
        return None


def recognize_food_with_spoonacular(image_data: bytes) -> Optional[Dict]:
    """
    DISABLED - Spoonacular API removed.
    This function is kept for compatibility but always returns None.
    """
    logger.warning("Spoonacular API is disabled - this function should not be called")
    print("ERROR: Spoonacular function called but it's disabled!", flush=True)
    return None
    
    try:
        # Use requests.Session() to maintain cookies and connection
        session = requests.Session()
        
        # Spoonacular food/images/classify endpoint
        # Documentation: https://spoonacular.com/food-api/docs#Classify-Food-Image
        url = f"{settings.SPOONACULAR_API_BASE_URL}/food/images/classify"
        print(f"Calling: {url}", flush=True)
        
        # Prepare file upload - Spoonacular expects 'file' parameter
        files = {
            'file': ('food_image.jpg', image_data, 'image/jpeg')
        }
        
        # API key should be in query parameters
        params = {
            'apiKey': settings.SPOONACULAR_API_KEY
        }
        
        # Enhanced headers to bypass Cloudflare
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://spoonacular.com/',
            'Origin': 'https://spoonacular.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        print(f"Using session with headers", flush=True)
        print(f"API Key: {params['apiKey'][:10]}...", flush=True)
        
        # First, try to get a session cookie by visiting the main page
        try:
            session.get('https://spoonacular.com/', headers=headers, timeout=5)
            print("Got session cookie", flush=True)
        except:
            print("Could not get session cookie, continuing anyway", flush=True)
        
        response = session.post(
            url,
            files=files,
            params=params,
            headers=headers,
            timeout=settings.SPOONACULAR_API_TIMEOUT,
            allow_redirects=True
        )
        
        print(f"Response status: {response.status_code}", flush=True)
        print(f"Response content-type: {response.headers.get('content-type', 'N/A')}", flush=True)
        print(f"Response text (first 300 chars): {response.text[:300]}", flush=True)
        
        logger.info(f"Spoonacular API response status: {response.status_code}")
        
        # Check if response is HTML (Cloudflare challenge)
        content_type = response.headers.get('content-type', '').lower()
        is_html = (content_type.startswith('text/html') or 
                  response.text.strip().startswith('<!DOCTYPE') or 
                  '<html' in response.text.lower() or 
                  'cloudflare' in response.text.lower() or
                  'just a moment' in response.text.lower())
        
        if is_html:
            logger.error("=" * 60)
            logger.error("CLOUDFLARE BLOCKING DETECTED!")
            logger.error("=" * 60)
            logger.error("Spoonacular API returned HTML instead of JSON")
            logger.error("")
            logger.error("SOLUTIONS:")
            logger.error("  1. Check API key on https://spoonacular.com/food-api/console")
            logger.error("  2. Verify API key is active and has quota")
            logger.error("  3. Free tier has very limited requests per day")
            logger.error("  4. Try again in a few minutes (rate limiting)")
            logger.error("")
            logger.error("Alternative: Use barcode scanning instead of image recognition")
            logger.error("=" * 60)
            print("ERROR: Cloudflare is blocking the request", flush=True)
            print("This is common with free API keys", flush=True)
            print("Try: 1) Verify API key, 2) Check quota, 3) Wait a few minutes", flush=True)
            return None
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"Spoonacular API response: {data}")
                
                # Spoonacular classify endpoint returns:
                # { "status": "success", "category": "apple", "probability": 0.95 }
                status = data.get('status', '')
                category = data.get('category', '')
                probability = data.get('probability', 0)  # Spoonacular uses 'probability' not 'confidence'
                
                if status != 'success' or not category:
                    logger.error(f"API returned failure or empty category: {data}")
                    return None
                
                # Extract food name from category
                food_name = category.strip()
                
                logger.info(f"Food recognized: {food_name} (probability: {probability:.2f})")
                
                # Return structured data
                return {
                    'category': category,
                    'categoryType': '',  # Not provided by API
                    'confidence': probability,  # Use probability as confidence
                    'name': food_name
                }
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response.text[:500]}")
                return None
        elif response.status_code == 401:
            logger.error("Spoonacular API key invalid or expired")
            return None
        elif response.status_code == 402:
            logger.error("Spoonacular API quota exceeded")
            return None
        elif response.status_code == 400:
            # API returned 400 - usually means "Could not classify image"
            try:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('message', response.text)
                logger.error(f"Spoonacular API error 400: {error_msg}")
                logger.error(f"Full response: {response.text}")
            except:
                logger.error(f"Spoonacular API error 400: {response.text}")
            logger.error("Spoonacular classify API couldn't recognize the image.")
            logger.error("NOTE: This API works better with prepared dishes than raw fruits.")
            logger.error("Try: 1) Better lighting, 2) Clearer image, 3) Different food item")
            return None
        else:
            logger.error(f"Spoonacular API error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Spoonacular API: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in food recognition: {e}")
        return None


def get_food_nutrition(food_name: str) -> Optional[Dict]:
    """
    DISABLED - Spoonacular API removed.
    This function is kept for compatibility but always returns None.
    """
    logger.warning("Spoonacular nutrition API is disabled")
    return None
    
    # OLD CODE BELOW - DISABLED
    if False:  # Never executes
        if not settings.SPOONACULAR_API_KEY:
            logger.error("Spoonacular API key not configured")
            return None
    
    logger.info(f"Getting nutrition for: {food_name}")
    
    try:
        # Step 1: Search for ingredient
        search_url = f"{settings.SPOONACULAR_API_BASE_URL}/food/ingredients/search"
        search_params = {
            'query': food_name,
            'apiKey': settings.SPOONACULAR_API_KEY,
            'number': 1,
            'sort': 'calories'
        }
        
        logger.debug(f"Searching ingredients: {search_url}?query={food_name}")
        search_response = requests.get(
            search_url,
            params=search_params,
            timeout=settings.SPOONACULAR_API_TIMEOUT
        )
        
        if search_response.status_code != 200:
            logger.error(f"Ingredient search failed: {search_response.status_code} - {search_response.text}")
            return None
        
        search_data = search_response.json()
        results = search_data.get('results', [])
        
        if not results:
            logger.warning(f"No ingredients found for: {food_name}")
            return None
        
        ingredient_id = results[0].get('id')
        ingredient_name = results[0].get('name', food_name)
        logger.info(f"Found ingredient: {ingredient_name} (ID: {ingredient_id})")
        
        # Step 2: Get detailed nutrition info per 100g
        nutrition_url = f"{settings.SPOONACULAR_API_BASE_URL}/food/ingredients/{ingredient_id}/information"
        nutrition_params = {
            'apiKey': settings.SPOONACULAR_API_KEY,
            'amount': 100,
            'unit': 'grams'
        }
        
        logger.debug(f"Getting nutrition info: {nutrition_url}")
        nutrition_response = requests.get(
            nutrition_url,
            params=nutrition_params,
            timeout=settings.SPOONACULAR_API_TIMEOUT
        )
        
        if nutrition_response.status_code == 200:
            nutrition_data = nutrition_response.json()
            logger.info(f"Got nutrition data for {ingredient_name}")
            return nutrition_data
        else:
            logger.error(f"Nutrition API failed: {nutrition_response.status_code} - {nutrition_response.text}")
            return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error getting nutrition: {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting food nutrition: {e}", exc_info=True)
        return None


def extract_nutrition_from_spoonacular(spoonacular_data: Dict) -> Optional[Dict]:
    """
    Extract nutrition data from Spoonacular API response.
    
    Args:
        spoonacular_data: Response from Spoonacular API
        
    Returns:
        Dictionary with standardized nutrition values, or None
    """
    try:
        nutrition = spoonacular_data.get('nutrition', {})
        nutrients = nutrition.get('nutrients', [])
        
        # Map Spoonacular nutrients to our format
        nutrition_dict = {
            'energy_100g': 0,
            'fat_100g': 0,
            'sugars_100g': 0,
            'salt_100g': 0,
            'fiber_100g': 0,
            'proteins_100g': 0
        }
        
        # Spoonacular provides nutrients per serving, we need per 100g
        # Get serving weight - check weightPerServing first, then weight
        weight_per_serving = nutrition.get('weightPerServing', {})
        serving_weight = weight_per_serving.get('amount', nutrition.get('weight', 100))
        
        # If serving_weight is already 100g, no conversion needed
        conversion_factor = 100.0 / serving_weight if serving_weight > 0 and serving_weight != 100 else 1.0
        
        for nutrient in nutrients:
            name = nutrient.get('name', '').lower()
            amount = nutrient.get('amount', 0)
            unit = nutrient.get('unit', '').lower()
            
            # Convert to per 100g
            amount_per_100g = amount * conversion_factor
            
            if 'calorie' in name or 'energy' in name:
                if unit == 'kcal':
                    nutrition_dict['energy_100g'] = amount_per_100g
                elif unit == 'kj':
                    nutrition_dict['energy_100g'] = amount_per_100g / 4.184
            elif 'fat' in name and 'saturated' not in name:
                if unit == 'g':
                    nutrition_dict['fat_100g'] = amount_per_100g
            elif 'sugar' in name:
                if unit == 'g':
                    nutrition_dict['sugars_100g'] = amount_per_100g
            elif 'sodium' in name:
                if unit == 'mg':
                    # Convert sodium (mg) to salt (g): salt = sodium * 2.54 / 1000
                    nutrition_dict['salt_100g'] = (amount_per_100g * 2.54) / 1000
                elif unit == 'g':
                    nutrition_dict['salt_100g'] = amount_per_100g * 2.54
            elif 'fiber' in name or 'fibre' in name:
                if unit == 'g':
                    nutrition_dict['fiber_100g'] = amount_per_100g
            elif 'protein' in name:
                if unit == 'g':
                    nutrition_dict['proteins_100g'] = amount_per_100g
        
        # Check if we have at least some nutrition data
        if any(v > 0 for v in nutrition_dict.values()):
            return nutrition_dict
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting nutrition from Spoonacular data: {e}")
        return None


def get_fallback_nutrition(food_name: str) -> Optional[Dict]:
    """
    Fallback nutrition data for common foods when API doesn't have data.
    Uses USDA nutrition database values.
    """
    food_name_lower = food_name.lower()
    
    # Common foods nutrition per 100g (from USDA)
    fallback_db = {
        'apple': {
            'energy_100g': 52,
            'fat_100g': 0.2,
            'sugars_100g': 10.4,
            'salt_100g': 0.001,
            'fiber_100g': 2.4,
            'proteins_100g': 0.3
        },
        'apples': {
            'energy_100g': 52,
            'fat_100g': 0.2,
            'sugars_100g': 10.4,
            'salt_100g': 0.001,
            'fiber_100g': 2.4,
            'proteins_100g': 0.3
        },
        'banana': {
            'energy_100g': 89,
            'fat_100g': 0.3,
            'sugars_100g': 12.2,
            'salt_100g': 0.001,
            'fiber_100g': 2.6,
            'proteins_100g': 1.1
        },
        'bananas': {
            'energy_100g': 89,
            'fat_100g': 0.3,
            'sugars_100g': 12.2,
            'salt_100g': 0.001,
            'fiber_100g': 2.6,
            'proteins_100g': 1.1
        },
        'roti': {
            'energy_100g': 297,
            'fat_100g': 7.4,
            'sugars_100g': 0,
            'salt_100g': 0.5,
            'fiber_100g': 2.7,
            'proteins_100g': 11.2
        },
        'chapati': {
            'energy_100g': 297,
            'fat_100g': 7.4,
            'sugars_100g': 0,
            'salt_100g': 0.5,
            'fiber_100g': 2.7,
            'proteins_100g': 11.2
        },
        'dal': {
            'energy_100g': 116,
            'fat_100g': 0.4,
            'sugars_100g': 0,
            'salt_100g': 0.3,
            'fiber_100g': 7.9,
            'proteins_100g': 9.0
        },
        'lentil': {
            'energy_100g': 116,
            'fat_100g': 0.4,
            'sugars_100g': 0,
            'salt_100g': 0.3,
            'fiber_100g': 7.9,
            'proteins_100g': 9.0
        },
        'rice': {
            'energy_100g': 130,
            'fat_100g': 0.3,
            'sugars_100g': 0,
            'salt_100g': 0.001,
            'fiber_100g': 0.4,
            'proteins_100g': 2.7
        },
        'tomato': {
            'energy_100g': 18,
            'fat_100g': 0.2,
            'sugars_100g': 2.6,
            'salt_100g': 0.005,
            'fiber_100g': 1.2,
            'proteins_100g': 0.9
        },
        'onion': {
            'energy_100g': 40,
            'fat_100g': 0.1,
            'sugars_100g': 4.2,
            'salt_100g': 0.004,
            'fiber_100g': 1.7,
            'proteins_100g': 1.1
        }
    }
    
    # Check exact match first
    if food_name_lower in fallback_db:
        return fallback_db[food_name_lower]
    
    # Check partial matches
    for key, value in fallback_db.items():
        if key in food_name_lower or food_name_lower in key:
            return value
    
    return None


def get_food_info_from_image(image_data: bytes) -> Optional[Dict]:
    """
    Complete pipeline: Recognize food from image and get nutrition info.
    Uses Google Vision API for recognition, then gets nutrition from fallback database.
    
    Args:
        image_data: Image bytes data
        
    Returns:
        Dictionary with food name and nutrition data, or None
    """
    # Step 1: Recognize food from image - try Google Vision first
    logger.info("Starting food recognition from image...")
    print(f"\n{'='*60}", flush=True)
    print("GET_FOOD_INFO_FROM_IMAGE - Starting recognition", flush=True)
    print(f"Google Vision API Key exists: {bool(settings.GOOGLE_VISION_API_KEY)}", flush=True)
    print(f"Google Vision API Enabled: {settings.GOOGLE_VISION_API_ENABLED}", flush=True)
    if settings.GOOGLE_VISION_API_KEY:
        print(f"API Key preview: {settings.GOOGLE_VISION_API_KEY[:20]}...", flush=True)
    recognition_result = None
    
    # Use Google Vision API (ONLY option - Spoonacular removed)
    if not settings.GOOGLE_VISION_API_KEY:
        logger.error("Google Vision API key not configured!")
        print("ERROR: Google Vision API key not found in .env file", flush=True)
        print("   Please add: GOOGLE_VISION_API_KEY=your_key_here", flush=True)
        return None
    
    if not settings.GOOGLE_VISION_API_ENABLED:
        logger.error("Google Vision API is disabled!")
        print("ERROR: Google Vision API is disabled", flush=True)
        return None
    
    logger.info("Calling Google Vision API...")
    print("Calling Google Vision API...", flush=True)
    recognition_result = recognize_food_with_google_vision(image_data)
    
    if recognition_result:
        print(f"SUCCESS: Google Vision recognized: {recognition_result.get('name', 'Unknown')}", flush=True)
    else:
        print("ERROR: Google Vision FAILED - No food recognized", flush=True)
    
    if not recognition_result:
        logger.error("Food recognition failed - API returned no result")
        logger.error("This could mean:")
        logger.error("  1. API key is invalid or expired")
        logger.error("  2. API quota exceeded")
        logger.error("  3. Image format not supported")
        logger.error("  4. Network error")
        return None
    
    # Extract food category/name
    food_category = recognition_result.get('category', '')
    food_name = recognition_result.get('name', food_category)
    confidence = recognition_result.get('confidence', 0)
    
    logger.info(f"Recognized food: {food_name} (category: {food_category}, confidence: {confidence:.2f})")
    
    if not food_name or food_name == 'Unknown Food':
        logger.error(f"Invalid food name in recognition result: {recognition_result}")
        return None
    
    # Allow empty category - API might not always provide it
    if not food_category:
        food_category = food_name  # Use food_name as category fallback
    
    # Clean food name - remove common prefixes/suffixes
    food_name_clean = food_name.lower().strip()
    
    # Try multiple variations of the food name
    search_terms = [food_name_clean]
    
    # Add variations for common foods
    if 'apple' in food_name_clean:
        search_terms.extend(['apple', 'apples', 'red apple', 'green apple'])
    elif 'banana' in food_name_clean:
        search_terms.extend(['banana', 'bananas'])
    elif 'roti' in food_name_clean or 'chapati' in food_name_clean:
        search_terms.extend(['roti', 'chapati', 'chapathi', 'flatbread'])
    elif 'dal' in food_name_clean or 'lentil' in food_name_clean:
        search_terms.extend(['lentil', 'dal', 'lentils'])
    elif 'rice' in food_name_clean:
        search_terms.extend(['rice', 'white rice', 'cooked rice'])
    
    # Step 2: Get nutrition information from fallback database
    # (Google Vision doesn't provide nutrition, so we use our fallback DB)
    logger.info(f"Getting nutrition data for: {food_name}")
    nutrition_data = get_fallback_nutrition(food_name)
    
    if nutrition_data:
        logger.info(f"Found nutrition data for: {food_name}")
        return {
            'food_name': food_name,
            'category': food_category,
            'nutrition': nutrition_data
        }
    else:
        logger.warning(f"Nutrition data not found in fallback database for: {food_name}")
        # Return basic info without nutrition - main.py will handle fallback
        return {
            'food_name': food_name,
            'category': food_category,
            'nutrition': None
        }

