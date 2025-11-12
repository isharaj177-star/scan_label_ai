"""
Test script to verify everything works.
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] == True
        print("✅ Health check passed!")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_scan(barcode="5449000000996"):
    """Test scan endpoint."""
    print(f"\nTesting scan endpoint with barcode: {barcode}...")
    try:
        response = requests.get(f"{API_BASE}/scan?barcode={barcode}", timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "product_name" in data
        assert "health_prediction" in data
        assert "nutrients" in data
        assert data["health_prediction"] in ["Healthy", "Moderate", "Unhealthy"]
        
        print(f"✅ Scan successful!")
        print(f"   Product: {data['product_name']}")
        print(f"   Brand: {data['brand']}")
        print(f"   Health: {data['health_prediction']}")
        print(f"   Sugars: {data['nutrients']['sugars_100g']}g")
        return True
    except Exception as e:
        print(f"❌ Scan failed: {e}")
        return False

def test_multiple_barcodes():
    """Test multiple barcodes."""
    barcodes = [
        "5449000000996",  # Coca-Cola
        "3017620422003",  # Nutella
        "3229820129488",  # Evian
    ]
    
    print("\nTesting multiple barcodes...")
    results = []
    for barcode in barcodes:
        result = test_scan(barcode)
        results.append(result)
        time.sleep(1)  # Rate limiting
    
    success_count = sum(results)
    print(f"\n✅ {success_count}/{len(barcodes)} barcodes scanned successfully")
    return success_count == len(barcodes)

def main():
    print("=" * 60)
    print("ScanLabel AI - Full System Test")
    print("=" * 60)
    
    # Wait for server to be ready
    print("\nWaiting for server to start...")
    time.sleep(3)
    
    # Run tests
    health_ok = test_health()
    if not health_ok:
        print("\n❌ Server not ready. Make sure backend is running:")
        print("   uvicorn main:app --reload")
        return
    
    scan_ok = test_scan()
    if scan_ok:
        test_multiple_barcodes()
    
    print("\n" + "=" * 60)
    if health_ok and scan_ok:
        print("✅ ALL TESTS PASSED!")
        print("\nFrontend: http://localhost:8080")
        print("API Docs: http://localhost:8000/docs")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)

if __name__ == "__main__":
    main()








