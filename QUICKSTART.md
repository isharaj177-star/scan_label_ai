# 🚀 Quick Start Guide

## Installation (One-Time Setup)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Or use the setup script:
```bash
python setup.py
```

### Step 2: Train the Model

```bash
python train_model.py
```

This creates `model.pkl` (takes ~30 seconds).

### Step 3: Run the API

```bash
uvicorn main:app --reload
```

Or:
```bash
python main.py
```

### Step 4: Test It!

Open your browser:
- **API Root:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Test Scan:** http://localhost:8000/scan?barcode=5449000000996

## Quick Test Commands

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test scan endpoint
curl "http://localhost:8000/scan?barcode=5449000000996"

# Test with different barcodes
curl "http://localhost:8000/scan?barcode=3017620422003"  # Nutella
curl "http://localhost:8000/scan?barcode=3229820129488"  # Evian Water
```

## Troubleshooting

### "ModuleNotFoundError"
→ Run: `pip install -r requirements.txt`

### "Model not found"
→ Run: `python train_model.py`

### "Port already in use"
→ Use different port: `uvicorn main:app --port 8001`

## Project Structure

```
ScanLabel AI/
├── main.py              # FastAPI server
├── train_model.py       # ML model training
├── config.py            # Configuration
├── requirements.txt     # Dependencies
├── utils/               # Utility modules
│   ├── data_fetch.py   # API integration
│   ├── preprocess.py   # Data processing
│   ├── predict.py      # ML predictions
│   ├── allergen_detector.py  # NLP detection
│   └── logger.py        # Logging
├── models/              # Pydantic models
│   └── schemas.py      # API schemas
└── tests/               # Unit tests
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Train model
3. ✅ Run API
4. ✅ Test endpoints
5. 🚀 Deploy (see DEPLOYMENT.md)








