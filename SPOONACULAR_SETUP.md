# 🍎 Spoonacular API Setup for Food Image Recognition

## Why Spoonacular?

✅ **150 FREE requests per day** (perfect for testing and small projects)
✅ **Excellent food recognition** (works with Indian foods too!)
✅ **Nutrition data included**
✅ **Easy to integrate**
✅ **No credit card required** for free tier

## Quick Setup (5 minutes)

### Step 1: Get Free API Key

1. Go to: https://spoonacular.com/food-api
2. Click **"Get Started"** or **"Sign Up"**
3. Create a free account (email + password)
4. You'll get **150 free API calls per day**
5. Copy your API key (looks like: `abc123def456ghi789...`)

### Step 2: Add API Key to Project

**Option A: Environment Variable (Recommended)**
Create a `.env` file in the project root:
```env
SPOONACULAR_API_KEY=your_api_key_here
```

**Option B: Direct in Code (Quick Test)**
Edit `config.py` and add:
```python
SPOONACULAR_API_KEY: Optional[str] = Field(default="your_api_key_here")
```

### Step 3: Install Dependencies

```bash
pip install Pillow
```

### Step 4: Restart Backend

```bash
# Stop current server (Ctrl+C)
# Then restart:
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## ✅ That's It!

Now you can:
- Scan barcodes (existing feature) ✅
- Scan food images (NEW!) ✅
  - Take photo of apple → Get nutrition info
  - Take photo of roti → Get nutrition info
  - Take photo of dal → Get nutrition info
  - Works with any food!

## 🎯 How It Works

1. User uploads food image
2. Image sent to Spoonacular API
3. API recognizes food (e.g., "Apple", "Banana", "Roti")
4. API provides nutrition data
5. Our ML model predicts health level
6. Display results!

## 📊 Free Tier Limits

- **150 requests/day** (resets daily)
- Perfect for personal use and testing
- If you need more, upgrade to paid plan

## 🍛 Works With Indian Foods!

Spoonacular recognizes:
- ✅ Fruits: Apple, Banana, Mango, etc.
- ✅ Vegetables: Tomato, Onion, Potato, etc.
- ✅ Dishes: Roti, Dal, Rice, Curry, etc.
- ✅ Packaged foods: Chips, Biscuits, etc.

## 🔧 Troubleshooting

**Error: "API key not configured"**
→ Add your API key to `.env` file

**Error: "Quota exceeded"**
→ You've used all 150 free requests today (resets tomorrow)

**Error: "Could not recognize food"**
→ Try a clearer photo with better lighting

## 🚀 Ready to Use!

Once API key is set, the "Food Image" tab will work automatically!








