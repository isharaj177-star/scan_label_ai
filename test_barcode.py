"""Quick test script to verify barcode fetching and preprocessing."""

from utils.data_fetch import fetch_product_by_barcode
from utils.preprocess import preprocess_api_data

# Test with known good barcode
print("Testing barcode: 3017620422003 (Nutella)")
data = fetch_product_by_barcode('3017620422003')
print(f"Found: {data is not None}")

if data:
    nut = preprocess_api_data(data)
    print(f"Has nutrition data: {nut is not None}")
    if nut:
        print(f"Nutrition values: {nut}")

print("\n" + "="*50 + "\n")

# Test with user's barcode
print("Testing barcode: 54841000")
data2 = fetch_product_by_barcode('54841000')
print(f"Found: {data2 is not None}")

if data2:
    product_name = data2.get('product', {}).get('product_name', 'N/A')
    print(f"Product name: {product_name}")
    nut2 = preprocess_api_data(data2)
    print(f"Has nutrition data: {nut2 is not None}")
    if nut2:
        print(f"Nutrition values: {nut2}")
    else:
        nutriments = data2.get('product', {}).get('nutriments', {})
        print(f"Available nutriments keys: {list(nutriments.keys())[:10]}")








