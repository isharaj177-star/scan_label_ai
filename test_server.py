"""
Quick test to verify the server is working and CORS is configured.
"""

import requests

print("Testing server...")
print("=" * 60)

try:
    # Test 1: Health check
    print("1. Testing /health endpoint...")
    response = requests.get("http://localhost:8001/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response Text: {response.text[:200]}")
    if response.status_code == 200:
        try:
            print(f"   Response JSON: {response.json()}")
        except:
            print(f"   Response is not JSON")
    print(f"   CORS Headers Present: {'Access-Control-Allow-Origin' in response.headers}")
    print()
    
    # Test 2: Scan endpoint with a known barcode
    print("2. Testing /scan endpoint...")
    response = requests.get(
        "http://localhost:8001/scan?barcode=5449000000996",
        headers={"Origin": "http://localhost:8080"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   CORS Headers Present: {'Access-Control-Allow-Origin' in response.headers}")
    if response.headers.get('Access-Control-Allow-Origin'):
        print(f"   CORS Header Value: {response.headers['Access-Control-Allow-Origin']}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Product: {data.get('product_name', 'N/A')}")
        print("   ✅ SUCCESS!")
    else:
        print(f"   Error: {response.text[:200]}")
        print("   ❌ FAILED")
    
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to server!")
    print("   Make sure the server is running on port 8001")
    print("   Run: python run_backend.py")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)

