# 📱 Supported Scan Formats

## ✅ Currently Supported Formats

### Barcodes (Food Products)
- **EAN-13** (13 digits) - Most common worldwide food barcodes
  - Example: `5449000000996` (Coca-Cola)
  - Used in: Europe, Asia, most countries
  
- **EAN-8** (8 digits) - Smaller products
  - Example: `30176204` (shortened format)
  - Used for: Small packages, limited space

- **UPC-A** (12 digits) - US/Canada products
  - Example: `012345678905`
  - Used in: United States, Canada

- **UPC-E** (8 digits) - Compressed UPC
  - Example: `01234565`
  - Used for: Small US products

- **Code 128** (Alphanumeric) - Various products
  - Example: `ABC123456`
  - Used for: Some specialty products

- **Code 39** (Alphanumeric) - Industrial/retail
  - Example: `ABC-123`
  - Used for: Various retail products

- **Codabar** (Numeric + symbols) - Libraries, blood banks
  - Example: `A123456B`
  - Used for: Specialized applications

### QR Codes
- **QR Code** - Can contain barcode numbers
  - If QR code contains a valid barcode number (8-13 digits), it will be scanned
  - Example: QR code with `5449000000996` inside

## 🎯 What Works Best

### ✅ Best Results
- **EAN-13 barcodes** on food products (most common)
- Clear, well-lit barcodes
- Barcodes on flat surfaces
- High-resolution images

### ⚠️ May Have Issues
- Damaged or scratched barcodes
- Curved surfaces (bottles, cans)
- Poor lighting
- Very small barcodes
- Blurry images

## 📋 Common Food Product Barcodes

| Product Type | Format | Example |
|-------------|--------|---------|
| Soft Drinks | EAN-13 | `5449000000996` |
| Chocolate | EAN-13 | `3017620422003` |
| Water | EAN-13 | `3229820129488` |
| Snacks | EAN-13/UPC-A | `123456789012` |
| Dairy | EAN-13 | `1234567890123` |

## 🔍 How to Scan

### Method 1: Manual Input
- Type the barcode number directly
- Works with any format

### Method 2: Camera Scan
- Point camera at barcode
- Auto-detects and scans
- Works with: EAN-13, EAN-8, UPC-A, UPC-E, Code 128, Code 39, Codabar, QR codes

### Method 3: Photo Upload
- Upload photo of barcode
- Scans from image
- Supports all formats above

## 💡 Tips for Best Results

1. **Lighting**: Ensure good, even lighting
2. **Distance**: Hold camera 6-12 inches from barcode
3. **Angle**: Keep camera parallel to barcode
4. **Focus**: Wait for camera to focus
5. **Steady**: Hold camera steady
6. **Clean**: Ensure barcode is clean and undamaged

## ❌ What Doesn't Work

- **Data Matrix codes** (not currently supported)
- **PDF417 codes** (not currently supported)
- **Aztec codes** (not currently supported)
- **Custom formats** (only standard formats)

## 🔄 Adding More Formats

To add more formats, update `frontend/app.js`:
- Add readers to QuaggaJS: `readers: ['new_format_reader']`
- Update validation regex if needed
- Test with sample codes

## 📊 Format Detection

The scanner tries formats in this order:
1. QR Code (if contains numeric barcode)
2. EAN-13 (most common)
3. EAN-8
4. UPC-A
5. UPC-E
6. Code 128
7. Code 39
8. Codabar

First successful detection wins!

