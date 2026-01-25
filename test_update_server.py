#!/usr/bin/env python3
"""
Test script for AIMU GitHub Update Server
"""

import requests
import sys
from typing import Optional

def test_endpoint(url: str, name: str) -> bool:
    """Test a single endpoint"""
    try:
        print(f"\n🧪 Testing: {name}")
        print(f"   URL: {url}")

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            print(f"   ✅ Status: {response.status_code}")
            data = response.json()
            print(f"   📦 Response: {list(data.keys())}")
            return True
        else:
            print(f"   ❌ Status: {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print(f"   ⏱️  Timeout (service may be sleeping)")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        base_url = "http://localhost:5000"

    print("=" * 60)
    print("AIMU GitHub Update Server - Test Suite")
    print("=" * 60)
    print(f"\nBase URL: {base_url}")

    tests = [
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/api/updates/check?version=0.9.0&platform=win32&client_id=test", "Update Check"),
        (f"{base_url}/api/updates/latest", "Latest Release"),
        (f"{base_url}/api/updates/versions", "List Versions"),
        (f"{base_url}/api/updates/stats", "Statistics"),
    ]

    results = []
    for url, name in tests:
        results.append(test_endpoint(url, name))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")

    # Detailed results
    print("\nDetails:")
    for (url, name), result in zip(tests, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")

    sys.exit(0 if all(results) else 1)

if __name__ == '__main__':
    main()
