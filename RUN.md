# 🚀 How to Run ScanLabel AI

## ✅ Everything is Ready!

The model is trained and all code is complete.

## Quick Start

### 1. Start Backend (Terminal 1)

```bash
cd "D:\ScanLabel AI"
uvicorn main:app --reload
```

Backend will run at: http://localhost:8000

### 2. Open Frontend

Simply open `frontend/index.html` in your web browser.

Or serve it:
```bash
cd frontend
python -m http.server 8080
```
Then open: http://localhost:8080

## Features

✅ **Manual Input** - Type barcode manually
✅ **Camera Scan** - Use webcam to scan barcode
✅ **Photo Upload** - Upload photo with barcode
✅ **Real API** - Uses Open Food Facts API
✅ **ML Classification** - Trained model predicts health
✅ **Allergen Detection** - Detects allergens in ingredients
✅ **Additive Detection** - Finds harmful additives

## Test It

1. Open `frontend/index.html`
2. Try "Manual Input" tab - enter: `5449000000996`
3. Try "Camera Scan" tab - point at barcode
4. Try "Upload Photo" tab - upload barcode image

## API Endpoints

- http://localhost:8000/docs - API Documentation
- http://localhost:8000/health - Health check
- http://localhost:8000/scan?barcode=5449000000996 - Scan product

## Troubleshooting

**Backend not starting?**
- Check port 8000 is free
- Run: `python -m pip install -r requirements.txt`

**Frontend can't connect?**
- Make sure backend is running
- Check browser console for errors
- Verify API_BASE_URL in app.js

**Camera not working?**
- Allow camera permissions in browser
- Use HTTPS or localhost (required for camera)

**Barcode not scanning?**
- Ensure good lighting
- Hold barcode steady
- Try different angles

## Ready to Deploy?

See `DEPLOYMENT.md` for Render/Railway instructions.








