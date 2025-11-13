"""
FastAPI backend for ScanLabel AI - Food health analysis system.
"""

from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional
import os

from config import settings
from utils.logger import logger
from utils.data_fetch import fetch_product_by_barcode, extract_product_info
from utils.preprocess import preprocess_api_data
from utils.predict import load_model, predict_health
from utils.allergen_detector import analyze_ingredients
from utils.food_recognition import get_food_info_from_image, get_fallback_nutrition
from utils.openrouter_client import get_alternative_with_fallback
from models.schemas import ScanResponse

def safe_print(text, **kwargs):
    """Print text handling unicode encoding errors."""
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', errors='replace').decode('ascii')
        print(safe_text, **kwargs)

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Add CORS middleware for frontend (MUST be before request logging)
# Use wildcard for development - allows all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=False,  # Must be False when using wildcard
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
    max_age=3600,
)

# Handle CORS preflight requests explicitly
@app.options("/{full_path:path}")
async def options_handler(full_path: str, request: Request):
    """Handle CORS preflight OPTIONS requests."""
    origin = request.headers.get("origin", "*")
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": origin if origin != "*" else "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "3600",
        }
    )

# Add request logging middleware (AFTER CORS)
@app.middleware("http")
async def log_requests(request, call_next):
    # Handle OPTIONS requests for CORS preflight
    if request.method == "OPTIONS":
        origin = request.headers.get("origin", "*")
        response = JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": origin if origin != "*" else "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "3600",
            }
        )
        return response
    
    # Use print() to ensure logs appear even if logger fails
    print(f"\n{'='*60}", flush=True)
    print(f"REQUEST: {request.method} {request.url.path}", flush=True)
    print(f"Origin: {request.headers.get('origin', 'N/A')}", flush=True)
    print(f"Query: {dict(request.query_params)}", flush=True)
    logger.info(f"=== REQUEST: {request.method} {request.url.path} ===")
    logger.info(f"Origin: {request.headers.get('origin', 'N/A')}")
    
    try:
        response = await call_next(request)
    except Exception as e:
        # Make sure errors also have CORS headers
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error in request: {e}")
        logger.error(f"Traceback: {error_trace}")
        print(f"ERROR in middleware: {e}", flush=True)
        print(f"Error type: {type(e).__name__}", flush=True)
        origin = request.headers.get("origin", "*")
        response = JSONResponse(
            status_code=500,
            content={"detail": str(e)},
            headers={
                "Access-Control-Allow-Origin": origin if origin != "*" else "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD",
                "Access-Control-Allow-Headers": "*",
            }
        )
        return response
    
    # ALWAYS add CORS headers - critical for frontend to work
    origin = request.headers.get("origin", "*")
    response.headers["Access-Control-Allow-Origin"] = origin if origin != "*" else "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    print(f"RESPONSE: {response.status_code}", flush=True)
    print(f"Origin: {origin}", flush=True)
    print(f"CORS Headers Added", flush=True)
    print(f"{'='*60}\n", flush=True)
    logger.info(f"=== RESPONSE: {response.status_code} ===")
    return response

# Exception handler to add CORS headers to HTTPException responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions and add CORS headers."""
    origin = request.headers.get("origin", "*")
    print(f"HTTPException: {exc.status_code} - {exc.detail}", flush=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": origin if origin != "*" else "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Global exception handler for ALL unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions and add CORS headers."""
    import traceback
    error_trace = traceback.format_exc()
    origin = request.headers.get("origin", "*")
    
    print(f"\nUNHANDLED EXCEPTION: {type(exc).__name__}: {exc}", flush=True)
    print(f"Traceback:\n{error_trace}", flush=True)
    logger.error(f"Unhandled exception: {exc}")
    logger.error(f"Traceback: {error_trace}")
    
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": origin if origin != "*" else "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Mount static files for frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Load model at startup
model = None


@app.on_event("startup")
async def startup_event():
    """Load the trained model when the server starts."""
    global model
    try:
        model_path = settings.MODEL_PATH
        logger.info(f"Loading model from {model_path}")
        model = load_model(model_path)
        
        if model is None:
            logger.warning("Model not loaded. Please run train_model.py first.")
        else:
            logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        import traceback
        logger.error(traceback.format_exc())
        model = None


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "name": "ScanLabel AI",
        "description": "Food health analysis API with AI-powered recommendations",
        "endpoints": {
            "/scan": "Scan a product by barcode",
            "/scan-image": "Scan food from image",
            "/recommend-alternatives": "Get AI-powered healthier alternatives",
            "/health": "API health check",
            "/docs": "API documentation"
        }
    }


@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML."""
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    else:
        # Fallback to API info if frontend not found
        return {
            "name": "ScanLabel AI",
            "description": "Food health analysis API",
            "endpoints": {
                "/scan": "Scan a product by barcode",
                "/docs": "API documentation",
                "/api": "API information"
            }
        }


@app.get("/scan")
async def scan_product(
    barcode: str = Query(..., description="Product barcode (EAN-13 or UPC-A)", example="5449000000996")
):
    """
    Scan a product by barcode and return health analysis.
    
    Args:
        barcode: Product barcode to scan
        
    Returns:
        JSON response with product information and health analysis
    """
    try:
        # Validate barcode
        if not barcode or not barcode.strip():
            logger.warning(f"Invalid barcode received: {barcode}")
            raise HTTPException(status_code=400, detail="Barcode is required")
        
        barcode = barcode.strip()
        print(f"\n{'='*60}", flush=True)
        print(f"SCAN BARCODE ENDPOINT CALLED", flush=True)
        print(f"Barcode: {barcode}", flush=True)
        print(f"{'='*60}", flush=True)
        logger.info(f"Scanning product with barcode: {barcode}")
        
        # Fetch product data from Open Food Facts API
        print("Fetching product from Open Food Facts...", flush=True)
        product_data = fetch_product_by_barcode(barcode)
        
        if product_data is None:
            print(f"ERROR: Product not found for barcode: {barcode}", flush=True)
            logger.warning(f"Product not found for barcode: {barcode}")
            raise HTTPException(
                status_code=404,
                detail=f"Product with barcode {barcode} not found in Open Food Facts database"
            )
        
        print("Product found!", flush=True)
        
        # Extract product information
        print("Extracting product information...", flush=True)
        product_info = extract_product_info(product_data)
        
        if not product_info:
            print("ERROR: Failed to extract product information", flush=True)
            logger.error(f"Failed to extract product info for barcode {barcode}")
            logger.error(f"Product data keys: {list(product_data.keys()) if product_data else 'None'}")
            raise HTTPException(
                status_code=500,
                detail="Failed to extract product information"
            )
        
        safe_print(f"Product info extracted: {product_info.get('product_name', 'Unknown')}", flush=True)

        # Preprocess nutrition data for model
        print("Preprocessing nutrition data...", flush=True)
        nutrition_data = preprocess_api_data(product_data)
        
        if nutrition_data is None:
            # Check if product exists but has no nutrition data
            product = product_data.get('product', {})
            nutriments = product.get('nutriments', {})
            
            print("No nutrition data available", flush=True)
            # Provide more helpful error message
            if not nutriments:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product '{product.get('product_name', 'Unknown')}' found but has no nutrition information in the database. This product may need to be updated on Open Food Facts."
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product '{product.get('product_name', 'Unknown')}' found but has insufficient nutrition data for analysis. Missing required values (energy, fat, sugars, salt, fiber, or proteins)."
                )
        
        print("Nutrition data preprocessed", flush=True)

        # Predict health level
        print("Predicting health level...", flush=True)
        health_prediction = None
        if model is not None:
            try:
                health_prediction = predict_health(nutrition_data, model)
            except Exception as e:
                logger.error(f"Error in predict_health: {e}")
                print(f"WARNING: Model prediction failed: {e}", flush=True)

        # If model prediction fails, use rule-based fallback
        if health_prediction is None:
            print("Using rule-based fallback...", flush=True)
            # Simple rule-based classification as fallback
            sugar = nutrition_data.get('sugars_100g', 0)
            fat = nutrition_data.get('fat_100g', 0)
            salt = nutrition_data.get('salt_100g', 0)
            
            if sugar >= 10 or fat >= 10 or salt >= 1:
                health_prediction = "Unhealthy"
            elif sugar < 5 and fat < 3 and salt < 0.3:
                health_prediction = "Healthy"
            else:
                health_prediction = "Moderate"
        
        print(f"Health prediction: {health_prediction}", flush=True)

        # Analyze ingredients for allergens and additives
        print("Analyzing ingredients...", flush=True)
        ingredients_text = product_info.get('ingredients_text', '')
        ingredient_analysis = analyze_ingredients(ingredients_text)
        
        # Combine detected items
        detected_items = (
            ingredient_analysis['allergens'] +
            ingredient_analysis['harmful_additives'] +
            ingredient_analysis['sugar_indicators']
        )
        
        # Generate health message
        message = generate_health_message(health_prediction, nutrition_data, detected_items)
        
        # Calculate nutrition score and daily values
        nutrition_score_data = calculate_nutrition_score(nutrition_data)
        health_insights = generate_health_insights(nutrition_data, health_prediction)
        
        # Build response using Pydantic models
        from models.schemas import Nutrients
        
        response = ScanResponse(
            product_name=product_info.get('product_name', 'Unknown'),
            brand=product_info.get('brand', 'Unknown'),
            barcode=barcode,
            health_prediction=health_prediction,
            nutrients=Nutrients(
                energy_100g=round(nutrition_data.get('energy_100g', 0), 2),
                sugars_100g=round(nutrition_data.get('sugars_100g', 0), 2),
                fat_100g=round(nutrition_data.get('fat_100g', 0), 2),
                salt_100g=round(nutrition_data.get('salt_100g', 0), 2),
                fiber_100g=round(nutrition_data.get('fiber_100g', 0), 2),
                proteins_100g=round(nutrition_data.get('proteins_100g', 0), 2)
            ),
            detected_allergens=ingredient_analysis['allergens'],
            detected_additives=ingredient_analysis['harmful_additives'],
            detected_sugar_indicators=ingredient_analysis['sugar_indicators'],
            message=message
        )
        
        # Add extra health data to response
        # Use model_dump() for Pydantic v2, fallback to dict() for v1
        try:
            response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        except Exception as e:
            print(f"WARNING: Error converting response to dict: {e}", flush=True)
            # Fallback: manually build dict
            response_dict = {
                'product_name': response.product_name,
                'brand': response.brand,
                'barcode': response.barcode,
                'health_prediction': response.health_prediction,
                'nutrients': {
                    'energy_100g': response.nutrients.energy_100g,
                    'sugars_100g': response.nutrients.sugars_100g,
                    'fat_100g': response.nutrients.fat_100g,
                    'salt_100g': response.nutrients.salt_100g,
                    'fiber_100g': response.nutrients.fiber_100g,
                    'proteins_100g': response.nutrients.proteins_100g,
                },
                'detected_allergens': response.detected_allergens,
                'detected_additives': response.detected_additives,
                'detected_sugar_indicators': response.detected_sugar_indicators,
                'message': response.message,
            }
        response_dict['nutrition_score'] = nutrition_score_data['score']
        response_dict['daily_values'] = nutrition_score_data['daily_values']
        response_dict['health_insights'] = health_insights
        
        safe_print(f"\nSUCCESS! Product analyzed: {product_info.get('product_name', 'Unknown')}", flush=True)
        print(f"   Health: {health_prediction}", flush=True)
        print(f"   Score: {nutrition_score_data['score']}/100", flush=True)
        print("=" * 60 + "\n", flush=True)
        logger.info(f"Successfully analyzed product: {product_info.get('product_name', 'Unknown')}")
        return response_dict
        
    except HTTPException:
        # Re-raise HTTP exceptions (they're already properly formatted)
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\nERROR in scan_product: {e}", flush=True)
        print(f"Traceback:\n{error_trace}", flush=True)
        logger.error(f"Error processing barcode scan: {e}")
        logger.error(f"Traceback: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing barcode: {str(e)}"
        )


def calculate_nutrition_score(nutrition_data: dict) -> dict:
    """Calculate nutrition score and daily value percentages."""
    # Daily recommended values (for adults)
    DAILY_ENERGY = 2000  # kcal
    DAILY_SUGAR = 50  # g
    DAILY_FAT = 70  # g
    DAILY_SALT = 6  # g
    DAILY_FIBER = 30  # g
    DAILY_PROTEIN = 50  # g
    
    energy = nutrition_data.get('energy_100g', 0)
    sugar = nutrition_data.get('sugars_100g', 0)
    fat = nutrition_data.get('fat_100g', 0)
    salt = nutrition_data.get('salt_100g', 0)
    fiber = nutrition_data.get('fiber_100g', 0)
    protein = nutrition_data.get('proteins_100g', 0)
    
    # Calculate daily value percentages
    dv = {
        'energy': min(100, (energy / DAILY_ENERGY) * 100),
        'sugar': min(100, (sugar / DAILY_SUGAR) * 100),
        'fat': min(100, (fat / DAILY_FAT) * 100),
        'salt': min(100, (salt / DAILY_SALT) * 100),
        'fiber': min(100, (fiber / DAILY_FIBER) * 100),
        'protein': min(100, (protein / DAILY_PROTEIN) * 100)
    }
    
    # Calculate health score (0-100)
    score = 100
    score -= min(30, dv['sugar'] * 0.3)  # Penalize high sugar
    score -= min(25, dv['fat'] * 0.25)    # Penalize high fat
    score -= min(25, dv['salt'] * 0.25)  # Penalize high salt
    score += min(10, dv['fiber'] * 0.1)  # Reward fiber
    score += min(10, dv['protein'] * 0.1)  # Reward protein
    
    score = max(0, min(100, score))
    
    return {
        'score': round(score, 1),
        'daily_values': dv,
        'warnings': []
    }

def generate_health_insights(nutrition_data: dict, health_prediction: str) -> list:
    """Generate detailed health insights."""
    insights = []
    sugar = nutrition_data.get('sugars_100g', 0)
    fat = nutrition_data.get('fat_100g', 0)
    salt = nutrition_data.get('salt_100g', 0)
    fiber = nutrition_data.get('fiber_100g', 0)
    protein = nutrition_data.get('proteins_100g', 0)
    
    # Sugar insights
    if sugar >= 22.5:
        insights.append({"type": "warning", "text": f"Very high sugar ({sugar:.1f}g) - exceeds daily limit in small portions"})
    elif sugar >= 10:
        insights.append({"type": "caution", "text": f"High sugar content ({sugar:.1f}g) - consume in moderation"})
    elif sugar < 5:
        insights.append({"type": "positive", "text": f"Low sugar content ({sugar:.1f}g) - good choice"})
    
    # Fat insights
    if fat >= 17.5:
        insights.append({"type": "warning", "text": f"Very high fat ({fat:.1f}g) - limit consumption"})
    elif fat >= 10:
        insights.append({"type": "caution", "text": f"High fat content ({fat:.1f}g)"})
    elif fat < 3:
        insights.append({"type": "positive", "text": f"Low fat content ({fat:.1f}g)"})
    
    # Salt insights
    if salt >= 1.5:
        insights.append({"type": "warning", "text": f"Very high salt ({salt:.2f}g) - may increase blood pressure"})
    elif salt >= 1:
        insights.append({"type": "caution", "text": f"High salt content ({salt:.2f}g)"})
    elif salt < 0.3:
        insights.append({"type": "positive", "text": f"Low salt content ({salt:.2f}g)"})
    
    # Fiber insights
    if fiber >= 6:
        insights.append({"type": "positive", "text": f"High fiber ({fiber:.1f}g) - supports digestion"})
    elif fiber < 3:
        insights.append({"type": "info", "text": f"Low fiber ({fiber:.1f}g) - consider adding fiber-rich foods"})
    
    # Protein insights
    if protein >= 10:
        insights.append({"type": "positive", "text": f"Good protein content ({protein:.1f}g) - supports muscle health"})
    elif protein < 3:
        insights.append({"type": "info", "text": f"Low protein ({protein:.1f}g)"})
    
    return insights

def generate_health_message(
    health_prediction: str,
    nutrition_data: dict,
    detected_items: list
) -> str:
    """
    Generate a human-readable health message based on prediction and analysis.
    
    Args:
        health_prediction: Predicted health level
        nutrition_data: Nutrition values
        detected_items: List of detected allergens/additives
        
    Returns:
        Health message string
    """
    sugar = nutrition_data.get('sugars_100g', 0)
    fat = nutrition_data.get('fat_100g', 0)
    salt = nutrition_data.get('salt_100g', 0)
    
    messages = []
    
    if health_prediction == "Healthy":
        messages.append("This product appears to be a healthy choice.")
    elif health_prediction == "Moderate":
        messages.append("This product has moderate nutritional value — consume in moderation.")
    else:
        messages.append("This product has high levels of sugar, fat, or salt — consume occasionally.")
    
    # Add specific warnings
    if sugar >= 10:
        messages.append(f"High sugar content ({sugar:.1f}g per 100g).")
    if fat >= 10:
        messages.append(f"High fat content ({fat:.1f}g per 100g).")
    if salt >= 1:
        messages.append(f"High salt content ({salt:.1f}g per 100g).")
    
    if detected_items:
        messages.append(f"Contains: {', '.join(detected_items[:5])}.")
    
    return " ".join(messages)


@app.post("/recommend-alternatives")
async def recommend_alternatives(request: Request):
    """
    Recommend healthier food alternatives for a scanned product.
    Uses AI (OpenRouter) to generate personalized, healthier options.

    Request body should contain product and nutrition data from a scan.

    Returns:
        JSON response with 3-5 healthier alternative recommendations
    """
    try:
        # Parse request body
        body = await request.json()

        # Extract required data
        product_name = body.get('product_name', 'Unknown Product')
        brand = body.get('brand', 'Unknown Brand')
        health_prediction = body.get('health_prediction', 'Moderate')

        # Extract nutrition data
        nutrients = body.get('nutrients', {})
        nutrition_data = {
            'energy_100g': nutrients.get('energy_100g', 0),
            'sugars_100g': nutrients.get('sugars_100g', 0),
            'fat_100g': nutrients.get('fat_100g', 0),
            'salt_100g': nutrients.get('salt_100g', 0),
            'fiber_100g': nutrients.get('fiber_100g', 0),
            'proteins_100g': nutrients.get('proteins_100g', 0)
        }

        # Collect detected issues
        detected_issues = []
        detected_issues.extend(body.get('detected_allergens', []))
        detected_issues.extend(body.get('detected_additives', []))
        detected_issues.extend(body.get('detected_sugar_indicators', []))

        logger.info(f"Generating alternatives for: {product_name} ({brand})")
        print(f"\n{'='*60}", flush=True)
        print(f"RECOMMEND ALTERNATIVES ENDPOINT CALLED", flush=True)
        safe_print(f"Product: {product_name}", flush=True)
        print(f"Health Level: {health_prediction}", flush=True)
        print(f"{'='*60}\n", flush=True)

        # Generate alternatives using AI (with fallback)
        alternatives_result = get_alternative_with_fallback(
            product_name=product_name,
            brand=brand,
            nutrition_data=nutrition_data,
            health_prediction=health_prediction,
            detected_issues=detected_issues
        )

        if not alternatives_result:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate healthier alternatives. Please try again."
            )

        # Add metadata
        alternatives_result['product_name'] = product_name
        alternatives_result['product_brand'] = brand
        alternatives_result['product_health_level'] = health_prediction

        print(f"SUCCESS! Generated {len(alternatives_result.get('alternatives', []))} alternatives", flush=True)
        print(f"Source: {alternatives_result.get('source', 'unknown')}", flush=True)
        print(f"{'='*60}\n", flush=True)

        logger.info(f"Successfully generated {len(alternatives_result.get('alternatives', []))} alternatives")

        return alternatives_result

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error generating alternatives: {e}")
        logger.error(f"Traceback: {error_trace}")
        print(f"\nERROR in recommend_alternatives: {e}", flush=True)
        print(f"Traceback:\n{error_trace}", flush=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating alternatives: {str(e)}"
        )


@app.options("/scan-image")
async def scan_food_image_options(request: Request):
    """Handle CORS preflight for /scan-image"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "3600",
        }
    )

@app.post("/scan-image")
async def scan_food_image(file: UploadFile = File(...)):
    """
    Scan a food image and return health analysis.
    Recognizes food items from photos (fruits, vegetables, dishes, etc.)
    
    Args:
        file: Image file (JPEG, PNG, WebP)
        
    Returns:
        JSON response with food information and health analysis
    """
    # CRITICAL: Log immediately - this proves endpoint is called
    timestamp = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "=" * 60, flush=True)
    print("SCAN-IMAGE ENDPOINT CALLED!", flush=True)
    print("=" * 60, flush=True)
    print(f"File: {file.filename}", flush=True)
    print(f"Type: {file.content_type}", flush=True)
    print(f"Time: {timestamp}", flush=True)
    print("=" * 60, flush=True)
    logger.info("=" * 60)
    logger.info("SCAN-IMAGE ENDPOINT CALLED!")
    logger.info(f"File received: {file.filename}")
    logger.info(f"Content type: {file.content_type}")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        logger.error(f"Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPEG, PNG, WebP)"
        )
    
    try:
        # Read image data
        print("Reading image data...", flush=True)
        logger.info("Reading image data...")
        image_data = await file.read()
        print(f"Image read: {len(image_data):,} bytes", flush=True)
        logger.info(f"Image data read: {len(image_data)} bytes")
        
        if len(image_data) == 0:
            print("ERROR: Empty image file!", flush=True)
            logger.error("Empty image file received")
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Recognize food from image
        print(f"\nProcessing food image...", flush=True)
        print(f"   Size: {len(image_data):,} bytes", flush=True)
        logger.info(f"Processing food image (size: {len(image_data)} bytes)")
        print(f"   Calling Google Vision API...", flush=True)
        food_info = get_food_info_from_image(image_data)

        if food_info:
            safe_print(f"Food recognized: {food_info.get('food_name', 'Unknown')}", flush=True)
        else:
            print(f"Food recognition failed!", flush=True)
        print(f"   Result: {'SUCCESS' if food_info else 'FAILED'}", flush=True)
        
        if not food_info:
            print("\n" + "=" * 60, flush=True)
            print("FOOD RECOGNITION FAILED", flush=True)
            print("=" * 60, flush=True)
            print("Possible reasons:", flush=True)
            print("  1. API key invalid or expired", flush=True)
            print("  2. API quota exceeded (free tier: 1000/month)", flush=True)
            print("  3. Image doesn't contain recognizable food", flush=True)
            print("  4. Network error", flush=True)
            print("=" * 60, flush=True)
            logger.error("Food recognition failed - no food info returned")
            logger.error("=" * 60)
            logger.error("GOOGLE VISION API FAILED")
            logger.error("=" * 60)
            logger.error("Possible reasons:")
            logger.error("  1. API key invalid or expired")
            logger.error("  2. API quota exceeded (free tier: 1000/month)")
            logger.error("  3. Image doesn't contain recognizable food")
            logger.error("  4. Network error")
            logger.error("=" * 60)
            raise HTTPException(
                status_code=400,
                detail="Could not recognize food from image. Please ensure: 1) Image shows clear food item, 2) Google Vision API key is valid, 3) API quota not exceeded. Try barcode scanning instead - it works perfectly!"
            )
        
        food_name = food_info.get('food_name', 'Unknown Food')
        nutrition_data = food_info.get('nutrition')
        
        # If no nutrition data, use fallback database
        if nutrition_data is None:
            logger.warning(f"Nutrition data not found for {food_name}, using fallback database")
            nutrition_data = get_fallback_nutrition(food_name)
            if nutrition_data:
                logger.info(f"Found nutrition in fallback database for: {food_name}")
            
            if nutrition_data is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Recognized '{food_name}' but nutrition information is not available. Please try a different food item or scan a barcode."
                )
        
        # Predict health level using ML model
        health_prediction = None
        if model is not None:
            health_prediction = predict_health(nutrition_data, model)
        
        # Fallback if model fails
        if health_prediction is None:
            sugar = nutrition_data.get('sugars_100g', 0)
            fat = nutrition_data.get('fat_100g', 0)
            salt = nutrition_data.get('salt_100g', 0)
            
            if sugar >= 10 or fat >= 10 or salt >= 1:
                health_prediction = "Unhealthy"
            elif sugar < 5 and fat < 3 and salt < 0.3:
                health_prediction = "Healthy"
            else:
                health_prediction = "Moderate"
        
        # Calculate nutrition score and insights
        nutrition_score_data = calculate_nutrition_score(nutrition_data)
        health_insights = generate_health_insights(nutrition_data, health_prediction)
        
        # Generate health message
        detected_items = []
        message = generate_health_message(health_prediction, nutrition_data, detected_items)
        
        # Build response
        from models.schemas import Nutrients
        
        response_dict = {
            'product_name': food_name,
            'brand': 'Natural Food',
            'barcode': None,
            'health_prediction': health_prediction,
            'nutrients': Nutrients(
                energy_100g=round(nutrition_data.get('energy_100g', 0), 2),
                sugars_100g=round(nutrition_data.get('sugars_100g', 0), 2),
                fat_100g=round(nutrition_data.get('fat_100g', 0), 2),
                salt_100g=round(nutrition_data.get('salt_100g', 0), 2),
                fiber_100g=round(nutrition_data.get('fiber_100g', 0), 2),
                proteins_100g=round(nutrition_data.get('proteins_100g', 0), 2)
            ),
            'detected_allergens': [],
            'detected_additives': [],
            'detected_sugar_indicators': [],
            'message': message,
            'nutrition_score': nutrition_score_data['score'],
            'daily_values': nutrition_score_data['daily_values'],
            'health_insights': health_insights,
            'source': 'image_recognition'
        }
        
        safe_print(f"\nSUCCESS! Food analyzed: {food_name}", flush=True)
        print(f"   Health: {health_prediction}", flush=True)
        print(f"   Score: {nutrition_score_data['score']}/100", flush=True)
        print("=" * 60 + "\n", flush=True)
        logger.info(f"Successfully analyzed food from image: {food_name}")
        return response_dict
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error processing food image: {e}")
        logger.error(f"Traceback: {error_trace}")
        print(f"ERROR: Exception in scan_food_image: {e}", flush=True)
        print(f"Traceback:\n{error_trace}", flush=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        print("Health check called", flush=True)
        health_data = {
            "status": "healthy" if model is not None else "unhealthy",
            "model_loaded": model is not None,
            "version": settings.API_VERSION
        }
        print(f"Health check response: {health_data}", flush=True)
        return health_data
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR in health_check: {e}", flush=True)
        print(f"Traceback:\n{error_trace}", flush=True)
        logger.error(f"Error in health check: {e}")
        logger.error(f"Traceback: {error_trace}")
        return {
            "status": "error",
            "error": str(e),
            "version": settings.API_VERSION
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", settings.PORT))
    uvicorn.run(
        app,
        host=settings.HOST,
        port=port,
        reload=settings.RELOAD
    )
