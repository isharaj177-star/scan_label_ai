"""
Test script for the Healthier Alternatives feature.

This script tests the /recommend-alternatives endpoint with sample product data.
Run this after starting the backend server (python run_backend.py).

Usage:
    python test_alternatives.py
"""

import requests
import json
from typing import Dict


def test_alternatives_endpoint(base_url: str = "http://localhost:8000"):
    """Test the /recommend-alternatives endpoint."""

    print("=" * 70)
    print("TESTING HEALTHIER ALTERNATIVES FEATURE")
    print("=" * 70)

    # Test Case 1: Unhealthy Soda
    print("\n📦 TEST 1: Unhealthy Soda (Coca-Cola)")
    print("-" * 70)

    test_data_1 = {
        "product_name": "Coca-Cola",
        "brand": "Coca-Cola Company",
        "health_prediction": "Unhealthy",
        "nutrients": {
            "energy_100g": 42.0,
            "sugars_100g": 10.6,
            "fat_100g": 0.0,
            "salt_100g": 0.01,
            "fiber_100g": 0.0,
            "proteins_100g": 0.0
        },
        "detected_allergens": [],
        "detected_additives": ["Caffeine", "Phosphoric Acid"],
        "detected_sugar_indicators": ["Sugar", "High Fructose Corn Syrup"]
    }

    try:
        response = requests.post(
            f"{base_url}/recommend-alternatives",
            json=test_data_1,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        print(f"✓ Request successful!")
        print(f"  Source: {result.get('source', 'unknown')}")
        print(f"  Summary: {result.get('summary', 'N/A')}")
        print(f"\n  Found {len(result.get('alternatives', []))} alternatives:")

        for i, alt in enumerate(result.get('alternatives', []), 1):
            print(f"\n  {i}. {alt['name']} ({alt['brand']})")
            print(f"     Why better: {alt['why_better']}")
            print(f"     Key benefits: {', '.join(alt['key_benefits'][:3])}")
            if 'estimated_improvements' in alt:
                print(f"     Improvements: {alt['estimated_improvements']}")

        print(f"\n  General Tips:")
        for tip in result.get('general_tips', [])[:3]:
            print(f"    • {tip}")

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server.")
        print("   Make sure the backend is running: python run_backend.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out (>30s)")
        print("   This might happen if OpenRouter API is slow or not responding")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Request failed: {e}")
        if hasattr(e.response, 'json'):
            print(f"   Details: {e.response.json()}")
        return False

    # Test Case 2: Unhealthy Snack (Chips)
    print("\n" + "=" * 70)
    print("📦 TEST 2: Unhealthy Snack (Potato Chips)")
    print("-" * 70)

    test_data_2 = {
        "product_name": "Lay's Classic Potato Chips",
        "brand": "Lay's",
        "health_prediction": "Unhealthy",
        "nutrients": {
            "energy_100g": 536.0,
            "sugars_100g": 1.0,
            "fat_100g": 35.0,
            "salt_100g": 1.5,
            "fiber_100g": 2.0,
            "proteins_100g": 6.0
        },
        "detected_allergens": [],
        "detected_additives": [],
        "detected_sugar_indicators": []
    }

    try:
        response = requests.post(
            f"{base_url}/recommend-alternatives",
            json=test_data_2,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        print(f"✓ Request successful!")
        print(f"  Source: {result.get('source', 'unknown')}")
        print(f"  Found {len(result.get('alternatives', []))} alternatives:")

        for i, alt in enumerate(result.get('alternatives', []), 1):
            print(f"\n  {i}. {alt['name']}")
            print(f"     Why: {alt['why_better'][:100]}...")

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        return False

    # Test Case 3: Moderate Product (Whole Grain Cereal)
    print("\n" + "=" * 70)
    print("📦 TEST 3: Moderate Product (Cereal)")
    print("-" * 70)

    test_data_3 = {
        "product_name": "Cheerios Original",
        "brand": "General Mills",
        "health_prediction": "Moderate",
        "nutrients": {
            "energy_100g": 367.0,
            "sugars_100g": 4.0,
            "fat_100g": 6.5,
            "salt_100g": 1.2,
            "fiber_100g": 10.0,
            "proteins_100g": 11.0
        },
        "detected_allergens": ["Gluten"],
        "detected_additives": [],
        "detected_sugar_indicators": []
    }

    try:
        response = requests.post(
            f"{base_url}/recommend-alternatives",
            json=test_data_3,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        print(f"✓ Request successful!")
        print(f"  Source: {result.get('source', 'unknown')}")
        print(f"  Found {len(result.get('alternatives', []))} alternatives")
        print(f"  Summary: {result.get('summary', 'N/A')[:120]}...")

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        return False

    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

    # Print configuration info
    print("\n📋 Configuration Info:")
    try:
        health_response = requests.get(f"{base_url}/health")
        health_data = health_response.json()
        print(f"  • Backend Status: {health_data.get('status', 'unknown')}")
        print(f"  • Model Loaded: {health_data.get('model_loaded', False)}")
        print(f"  • Version: {health_data.get('version', 'unknown')}")
    except:
        print("  • Could not fetch health status")

    print("\n💡 Notes:")
    print("  • If source is 'ai_powered': OpenRouter API is working!")
    print("  • If source is 'rule_based_fallback': Using fallback (no API key)")
    print("  • To enable AI: Set OPENROUTER_API_KEY in .env file")
    print("  • Get free key at: https://openrouter.ai/keys")

    return True


def test_with_real_barcode_scan(base_url: str = "http://localhost:8000", barcode: str = "5449000000996"):
    """
    Test end-to-end: Scan barcode -> Get alternatives.

    Args:
        base_url: Backend URL
        barcode: Product barcode (default: Coca-Cola)
    """
    print("\n" + "=" * 70)
    print(f"🔍 END-TO-END TEST: Scan barcode {barcode} and get alternatives")
    print("=" * 70)

    try:
        # Step 1: Scan the barcode
        print(f"\nStep 1: Scanning barcode {barcode}...")
        scan_response = requests.get(f"{base_url}/scan?barcode={barcode}", timeout=10)
        scan_response.raise_for_status()
        scan_data = scan_response.json()

        print(f"✓ Product found: {scan_data.get('product_name', 'Unknown')}")
        print(f"  Brand: {scan_data.get('brand', 'Unknown')}")
        print(f"  Health: {scan_data.get('health_prediction', 'Unknown')}")
        print(f"  Sugar: {scan_data.get('nutrients', {}).get('sugars_100g', 0)}g")

        # Step 2: Get alternatives
        print(f"\nStep 2: Getting healthier alternatives...")
        alt_response = requests.post(
            f"{base_url}/recommend-alternatives",
            json=scan_data,
            timeout=30
        )
        alt_response.raise_for_status()
        alt_data = alt_response.json()

        print(f"✓ Found {len(alt_data.get('alternatives', []))} alternatives!")
        print(f"  Summary: {alt_data.get('summary', 'N/A')}")

        for i, alt in enumerate(alt_data.get('alternatives', [])[:3], 1):
            print(f"\n  {i}. {alt['name']}")
            print(f"     {alt['why_better'][:80]}...")

        print("\n✅ END-TO-END TEST SUCCESSFUL!")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    import sys

    # Default to localhost
    base_url = "http://localhost:8000"

    # Allow custom URL from command line
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"\n🚀 Testing Healthier Alternatives Feature")
    print(f"📡 Backend URL: {base_url}\n")

    # Run tests
    success = test_alternatives_endpoint(base_url)

    if success:
        # Run end-to-end test with real barcode
        test_with_real_barcode_scan(base_url)

    print("\n" + "=" * 70)
    if success:
        print("🎉 All tests passed! The feature is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    print("=" * 70 + "\n")
