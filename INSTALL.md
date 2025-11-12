# 📦 Installation Guide

## Quick Start

### Option 1: Using setup.py (Recommended)

```bash
python setup.py
```

This will automatically install all dependencies from `requirements.txt`.

### Option 2: Manual Installation

```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.10 or higher
- pip (Python package manager)

## Step-by-Step Setup

1. **Clone or download the project**
   ```bash
   cd "D:\ScanLabel AI"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or use the setup script:
   ```bash
   python setup.py
   ```

3. **Train the model** (first time only)
   ```bash
   python train_model.py
   ```
   
   This will create `model.pkl` file.

4. **Run the API server**
   ```bash
   uvicorn main:app --reload
   ```
   
   Or:
   ```bash
   python main.py
   ```

5. **Test the API**
   - Open browser: http://localhost:8000
   - API docs: http://localhost:8000/docs
   - Test endpoint: http://localhost:8000/scan?barcode=5449000000996

## Troubleshooting

### ModuleNotFoundError

If you get `ModuleNotFoundError`, install dependencies:
```bash
pip install -r requirements.txt
```

### Port already in use

If port 8000 is busy, use a different port:
```bash
uvicorn main:app --port 8001
```

### Model not found

Make sure you've trained the model first:
```bash
python train_model.py
```

## Verify Installation

Run this to verify everything works:

```bash
python -c "from config import settings; print('Config OK')"
python -c "from utils.logger import logger; logger.info('Logger OK')"
python -c "import fastapi; print('FastAPI OK')"
```

All should print OK without errors.








