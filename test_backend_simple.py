"""
Simple test to see if backend is working and logs are visible.
"""

import requests
import sys

print("=" * 60)
print("TESTING BACKEND SERVER")
print("=" * 60)
print()

# Test 1: Can we reach the server?
print("1. Testing if server is running...")
try:
    response = requests.get("http://localhost:8001/", timeout=2)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:100]}")
    print("   OK - Server is running")
except requests.exceptions.ConnectionError:
    print("   ERROR: Cannot connect to server!")
    print("   Make sure backend is running: python run_backend.py")
    sys.exit(1)
except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

print()

# Test 2: Health endpoint
print("2. Testing /health endpoint...")
try:
    response = requests.get("http://localhost:8001/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    print(f"   Response: {response.text}")
    if response.status_code == 200:
        print("   OK - Health endpoint works")
    else:
        print(f"   ERROR - Health endpoint returned {response.status_code}")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Scan endpoint
print("3. Testing /scan endpoint...")
try:
    response = requests.get(
        "http://localhost:8001/scan?barcode=5449000000996",
        headers={"Origin": "http://localhost:8080"},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   CORS Header: {response.headers.get('Access-Control-Allow-Origin', 'MISSING')}")
    print(f"   Response (first 200 chars): {response.text[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)

