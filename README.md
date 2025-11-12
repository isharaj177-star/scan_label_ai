# ScanLabel AI

An intelligent food-scanning and health analysis system powered by Machine Learning and the Open Food Facts API.

## 🎯 Overview

ScanLabel AI is a Python-powered backend that:
- Scans food barcodes to fetch real data from the Open Food Facts API
- Uses a Machine Learning model (RandomForestClassifier) trained on nutrition data to predict health levels (Healthy / Moderate / Unhealthy)
- Uses NLP to detect harmful ingredients, allergens, and additives from product text
- Returns comprehensive analysis as JSON via a FastAPI endpoint

## 🏗️ Project Structure

```
scanlabel_ai/
├── main.py                 # FastAPI server with /scan endpoint
├── train_model.py          # Model training script
├── model.pkl               # Trained ML model (generated after training)
├── utils/
│   ├── __init__.py
│   ├── data_fetch.py      # Open Food Facts API integration
│   ├── preprocess.py       # Data preprocessing utilities
│   ├── predict.py         # Model prediction logic
│   └── allergen_detector.py # NLP-based allergen/additive detection
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the Model

First, train the machine learning model:

```bash
python train_model.py
```

This will:
- Load/process the Open Food Facts dataset
- Clean and preprocess the data
- Create health labels based on nutrition thresholds
- Train a RandomForestClassifier
- Save the model as `model.pkl`

**Note:** For production use, download the full Open Food Facts dataset from:
https://world.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz

The training script will create a sample dataset if no local file is found.

### 3. Run the API Server

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Test the API

Visit the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📡 API Endpoints

### GET `/scan?barcode=XXXX`

Scan a product by barcode and get health analysis.

**Parameters:**
- `barcode` (required): Product barcode (EAN-13 or UPC-A format)

**Example Request:**
```bash
curl "http://localhost:8000/scan?barcode=5449000000996"
```

**Example Response:**
```json
{
  "product_name": "Coca-Cola",
  "brand": "Coca-Cola Company",
  "barcode": "5449000000996",
  "health_prediction": "Unhealthy",
  "nutrients": {
    "energy_100g": 42.0,
    "sugars_100g": 10.6,
    "fat_100g": 0.0,
    "salt_100g": 0.0,
    "fiber_100g": 0.0,
    "proteins_100g": 0.0
  },
  "detected_allergens": [],
  "detected_additives": [],
  "detected_sugar_indicators": ["Sugar"],
  "message": "This product has high levels of sugar, fat, or salt — consume occasionally. High sugar content (10.6g per 100g). Contains: Sugar."
}
```

### GET `/health`

Health check endpoint to verify API and model status.

### GET `/`

Root endpoint with API information.

## 🧪 Test Barcodes

Try these sample barcodes:

- `5449000000996` - Coca-Cola
- `3017620422003` - Nutella
- `3229820129488` - Evian Water

## 🧠 How It Works

### Training Phase

1. **Data Collection**: Load Open Food Facts dataset (CSV/JSONL)
2. **Data Cleaning**: Remove rows with missing nutrition information
3. **Label Creation**: Classify products as Healthy/Moderate/Unhealthy based on thresholds:
   - **Healthy**: Low sugar (<5g), low fat (<3g), low salt (<0.3g)
   - **Moderate**: Medium values
   - **Unhealthy**: High sugar (≥10g) OR high fat (≥10g) OR high salt (≥1g)
4. **Model Training**: Train RandomForestClassifier on nutrition features
5. **Model Saving**: Save trained model as `model.pkl`

### Runtime Phase

1. **Barcode Scan**: User provides product barcode
2. **API Fetch**: Fetch product data from Open Food Facts API
3. **Data Extraction**: Extract nutrition facts and ingredients
4. **Health Prediction**: Use trained model to predict health level
5. **Ingredient Analysis**: Use NLP to detect allergens and harmful additives
6. **Response**: Return comprehensive JSON analysis

## 🔧 Technical Details

### Machine Learning Model

- **Algorithm**: RandomForestClassifier (scikit-learn)
- **Features**: energy_100g, fat_100g, sugars_100g, salt_100g, fiber_100g, proteins_100g
- **Target**: health_label (Healthy / Moderate / Unhealthy)
- **Model Persistence**: Joblib (.pkl format)

### NLP Detection

- **Allergens**: Gluten, dairy, nuts, eggs, soy, fish, etc.
- **Harmful Additives**: Artificial sweeteners, preservatives, colorings, MSG, etc.
- **Sugar Indicators**: Various sugar types and sweeteners
- **Method**: Keyword matching with regex patterns

### Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pandas` - Data manipulation
- `scikit-learn` - Machine learning
- `joblib` - Model serialization
- `requests` - HTTP client for API calls
- `numpy` - Numerical computing

## 📊 Health Classification Thresholds

| Nutrient | Healthy | Moderate | Unhealthy |
|----------|---------|----------|-----------|
| Sugar (g/100g) | < 5 | 5-10 | ≥ 10 |
| Fat (g/100g) | < 3 | 3-10 | ≥ 10 |
| Salt (g/100g) | < 0.3 | 0.3-1 | ≥ 1 |

A product is classified as:
- **Unhealthy** if ANY nutrient exceeds unhealthy threshold
- **Healthy** if ALL nutrients are below healthy thresholds
- **Moderate** otherwise

## 🛠️ Development

### Running Tests

Test the API with sample barcodes:

```bash
# Test Coca-Cola
curl "http://localhost:8000/scan?barcode=5449000000996"

# Test Nutella
curl "http://localhost:8000/scan?barcode=3017620422003"

# Test Evian Water
curl "http://localhost:8000/scan?barcode=3229820129488"
```

### Model Retraining

To retrain the model with new data:

```bash
python train_model.py
```

The new model will overwrite `model.pkl`.

## 📝 Notes

- The model uses synthetic data for demonstration if no dataset is provided
- For production, download the full Open Food Facts dataset
- The API includes fallback rule-based classification if the model fails to load
- All nutrition values are normalized to per-100g basis

## 🤝 Contributing

This is a research and ML project suitable for internship presentation. The code is modular, well-documented, and follows best practices.

## 📄 License

This project is for educational and research purposes.

## 🔗 Resources

- [Open Food Facts API](https://world.openfoodfacts.org/api)
- [Open Food Facts Data](https://world.openfoodfacts.org/data)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Scikit-learn Documentation](https://scikit-learn.org/)








