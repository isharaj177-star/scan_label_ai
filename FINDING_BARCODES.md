# Finding Valid Barcodes for Testing

## The Issue

Some barcodes you scan might not exist in the Open Food Facts database. This is normal - not all products worldwide are in the database.

## How to Find Valid Barcodes

### Method 1: Use Open Food Facts Website
1. Go to https://world.openfoodfacts.org/
2. Browse products or search for a product
3. Click on any product
4. The barcode is shown on the product page (usually EAN-13 format, 13 digits)

### Method 2: Test with Known Products
Here are some verified barcodes that work:

- **3017620422003** - Nutella (has complete nutrition data)
- **5449000000996** - Coca-Cola (example from docs)
- **8000500310427** - Barilla pasta (usually has good data)

### Method 3: Scan Real Products
- Use your phone camera or scanner to scan barcodes from products you have
- Most EAN-13 (13 digits) and EAN-8 (8 digits) barcodes work
- Products sold in Europe/US usually have better data coverage

## What Happens When a Barcode Isn't Found?

The system will:
1. Try the barcode as-is
2. If it's 8 digits, try padding it to 13 digits (EAN-8 → EAN-13)
3. Return a clear error message if not found

## What If Product Has No Nutrition Data?

If a product exists but has incomplete nutrition information:
- You'll see a helpful error message
- The product name will be shown (if available)
- You'll know what data is missing

## Improvements Made

✅ **More lenient nutrition checking** - Now accepts products with partial data (at least one nutrition value)
✅ **Better energy conversion** - Automatically converts kJ to kcal when needed
✅ **Multiple barcode format attempts** - Tries different formats automatically
✅ **Clearer error messages** - Tells you exactly what's wrong

## Testing Your Barcode

To test if a barcode exists:
```bash
curl "https://world.openfoodfacts.org/api/v0/product/YOUR_BARCODE.json"
```

If `"status": 1`, the product exists. If `"status": 0`, it's not in the database.








