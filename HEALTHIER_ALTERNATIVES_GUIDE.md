# Healthier Alternatives Feature - Setup & Usage Guide

## Overview

The **Healthier Alternatives** feature uses AI (via OpenRouter) to recommend 3-5 healthier food options when you scan a product. It analyzes the nutrition data and provides specific, actionable alternatives with clear explanations.

## Features

- **AI-Powered Recommendations**: Uses Gemini 2.0 Flash Experimental (free, fast, accurate)
- **Personalized Suggestions**: Based on your product's specific nutrition profile
- **Smart Fallback**: Works even without API key using rule-based recommendations
- **Detailed Reasoning**: Each alternative includes why it's better and key benefits
- **Estimated Improvements**: Shows specific nutritional improvements (e.g., "50% less sugar")

## Setup Instructions

### 1. Get OpenRouter API Key (Free)

1. Go to [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign up or log in (GitHub, Google, or email)
3. Click "Create Key" and give it a name (e.g., "ScanLabel AI")
4. Copy your API key (starts with `sk-or-...`)

**Note**: OpenRouter offers several FREE models including Gemini 2.0 Flash, Llama 3.3 70B, and more.

### 2. Configure Your Environment

Add the OpenRouter API key to your `.env` file:

```bash
# .env file
OPENROUTER_API_KEY=sk-or-v1-YOUR_API_KEY_HERE
```

Or set it as an environment variable:

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-YOUR_API_KEY_HERE"
```

**Windows (Command Prompt):**
```cmd
set OPENROUTER_API_KEY=sk-or-v1-YOUR_API_KEY_HERE
```

**Linux/Mac:**
```bash
export OPENROUTER_API_KEY="sk-or-v1-YOUR_API_KEY_HERE"
```

### 3. Optional: Choose a Different Model

The default model is `google/gemini-2.0-flash-exp:free` (recommended). To use a different model, add to `.env`:

```bash
# Use Llama 3.3 70B instead
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free

# Or use Nous Hermes 3 (405B parameters)
OPENROUTER_MODEL=nousresearch/hermes-3-llama-3.1-405b:free

# Or use Qwen 2.5 72B
OPENROUTER_MODEL=qwen/qwen-2.5-72b-instruct:free
```

## API Usage

### Endpoint: `POST /recommend-alternatives`

**Request Body** (same format as `/scan` response):
```json
{
  "product_name": "Coca-Cola",
  "brand": "Coca-Cola Company",
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
  "detected_sugar_indicators": ["Sugar"]
}
```

**Response**:
```json
{
  "summary": "This product has high sugar content (10.6g). Consider healthier alternatives to reduce sugar intake.",
  "alternatives": [
    {
      "name": "Sparkling Water with Natural Fruit",
      "brand": "La Croix / Generic",
      "why_better": "Zero sugar and calories while still providing refreshing carbonation and taste",
      "key_benefits": [
        "No added sugar",
        "Zero calories",
        "Natural hydration",
        "No artificial sweeteners"
      ],
      "estimated_improvements": {
        "sugar": "100% less sugar (0g vs 10.6g)",
        "calories": "100% less calories"
      }
    },
    {
      "name": "Unsweetened Iced Tea",
      "brand": "Pure Leaf / Generic",
      "why_better": "Natural antioxidants without added sugars",
      "key_benefits": [
        "No added sugar",
        "Contains antioxidants",
        "Low calorie",
        "Natural caffeine"
      ],
      "estimated_improvements": {
        "sugar": "100% less sugar",
        "antioxidants": "High polyphenols"
      }
    },
    {
      "name": "Coconut Water",
      "brand": "Vita Coco / Generic",
      "why_better": "Natural electrolytes with naturally occurring sugars only",
      "key_benefits": [
        "Natural electrolytes",
        "Lower sugar than soda",
        "Potassium rich",
        "Natural hydration"
      ],
      "estimated_improvements": {
        "sugar": "40-50% less sugar",
        "electrolytes": "High potassium and magnesium"
      }
    }
  ],
  "general_tips": [
    "Look for drinks with no added sugars",
    "Choose naturally flavored or unsweetened options",
    "Read nutrition labels - aim for <5g sugar per 100ml",
    "Consider water with fresh fruit as a natural alternative"
  ],
  "source": "ai_powered",
  "product_name": "Coca-Cola",
  "product_brand": "Coca-Cola Company",
  "product_health_level": "Unhealthy"
}
```

## Testing the Feature

### Test with curl:

```bash
curl -X POST "http://localhost:8000/recommend-alternatives" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Coca-Cola",
    "brand": "Coca-Cola Company",
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
    "detected_sugar_indicators": ["Sugar"]
  }'
```

### Test with Python:

```python
import requests

# First scan a product
scan_response = requests.get("http://localhost:8000/scan?barcode=5449000000996")
product_data = scan_response.json()

# Then get alternatives
alternatives_response = requests.post(
    "http://localhost:8000/recommend-alternatives",
    json=product_data
)

alternatives = alternatives_response.json()
print(f"Found {len(alternatives['alternatives'])} healthier alternatives!")

for alt in alternatives['alternatives']:
    print(f"\n✓ {alt['name']} ({alt['brand']})")
    print(f"  Why better: {alt['why_better']}")
    print(f"  Benefits: {', '.join(alt['key_benefits'])}")
```

## How It Works

1. **Scan a Product**: Use `/scan?barcode=XXX` to get product nutrition data
2. **Request Alternatives**: Send the scan data to `/recommend-alternatives`
3. **AI Analysis**:
   - If OpenRouter API key is configured: Uses Gemini 2.0 Flash to analyze nutrition and generate personalized recommendations
   - If no API key: Uses smart rule-based fallback with category detection
4. **Get Results**: Receive 3-5 specific alternatives with detailed explanations

## Model Comparison

| Model | Parameters | Speed | Quality | Best For |
|-------|-----------|-------|---------|----------|
| **Gemini 2.0 Flash** (default) | N/A | ⚡⚡⚡ Fastest | ⭐⭐⭐⭐ Excellent | Real-time recommendations |
| Llama 3.3 70B | 70B | ⚡⚡ Fast | ⭐⭐⭐⭐ Excellent | Balanced quality/speed |
| Nous Hermes 3 405B | 405B | ⚡ Moderate | ⭐⭐⭐⭐⭐ Best | Maximum quality |
| Qwen 2.5 72B | 72B | ⚡⚡ Fast | ⭐⭐⭐⭐ Excellent | Multilingual support |

## Troubleshooting

### Issue: "OpenRouter API key not configured"
- **Solution**: Add `OPENROUTER_API_KEY` to your `.env` file or environment variables
- **Fallback**: The app will still work using rule-based recommendations

### Issue: "Rate limit exceeded"
- **Solution**: Wait a few minutes or upgrade your OpenRouter plan
- **Free Tier**: Usually generous limits for casual use

### Issue: "Model not found"
- **Solution**: Check model name at [https://openrouter.ai/models](https://openrouter.ai/models)
- Make sure to use the full model ID (e.g., `google/gemini-2.0-flash-exp:free`)

### Issue: Slow responses
- **Solution**: Switch to Gemini 2.0 Flash (fastest TTFT)
- Or use rule-based fallback by not setting API key

## Cost & Limits

- **Free Models**: Gemini 2.0 Flash, Llama 3.3 70B, Qwen 2.5 72B, Nous Hermes 3 405B (all FREE!)
- **Rate Limits**: Depends on OpenRouter's free tier (usually very generous)
- **Fallback**: Always works even without API key

## Privacy & Security

- **Your API Key**: Stored only in `.env` file on your machine
- **Data Sent**: Only product name, brand, and nutrition values
- **No Personal Data**: No user information is sent to OpenRouter
- **Transparent**: Check the code in `utils/openrouter_client.py`

## Frontend Integration (Coming Soon)

To integrate this into your frontend:

```javascript
async function getHealthierAlternatives(scanResult) {
  const response = await fetch('http://localhost:8000/recommend-alternatives', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(scanResult)
  });

  const alternatives = await response.json();

  // Display alternatives to user
  displayAlternatives(alternatives);
}
```

## Support

If you encounter issues:
1. Check the logs in the terminal where you're running the server
2. Verify your API key is correct
3. Test with the fallback (no API key) to isolate issues
4. Check OpenRouter status: [https://status.openrouter.ai/](https://status.openrouter.ai/)

## Future Enhancements

- [ ] Frontend UI for displaying alternatives
- [ ] Save favorite alternatives
- [ ] Filter by dietary preferences (vegan, gluten-free, etc.)
- [ ] Price comparison
- [ ] Availability in local stores
- [ ] Nutritional comparison charts
