#!/usr/bin/env python3
"""
Smoke test script to verify end-to-end connectivity
Tests health, greeting, and ask endpoints
"""

import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8002")
TIMEOUT = 10

def test_health():
    """Test health check endpoint"""
    print("🔍 Testing /health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {API_BASE_URL}")
        print("   Make sure the backend server is running:")
        print("   PORT=8002 python3 run_server.py")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_greeting():
    """Test greeting endpoint"""
    print("\n🔍 Testing /api/greeting endpoint...")
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/greeting",
            params={"user_id": "test_user", "language": "en"},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("greeting"):
                print(f"✅ Greeting endpoint passed")
                print(f"   Greeting: {data['greeting'][:100]}...")
                return True
            else:
                print(f"❌ Greeting endpoint returned invalid response")
                return False
        else:
            print(f"❌ Greeting endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Greeting endpoint error: {e}")
        return False

def test_ask():
    """Test ask endpoint"""
    print("\n🔍 Testing /api/ask endpoint...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/ask",
            json={
                "question": "hi",
                "language": "en",
                "user_id": "test_user",
                "is_voice": False,
                "context_data": {}
            },
            timeout=30  # Longer timeout for LLM calls
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success") is not False and (data.get("answer") or data.get("message") or data.get("content")):
                print(f"✅ Ask endpoint passed")
                answer = data.get("answer") or data.get("message") or data.get("content", "")
                print(f"   Answer: {answer[:100]}...")
                return True
            else:
                print(f"❌ Ask endpoint returned invalid response")
                print(f"   Response: {data}")
                return False
        else:
            print(f"❌ Ask endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print(f"❌ Ask endpoint timed out (this may indicate LLM issues)")
        return False
    except Exception as e:
        print(f"❌ Ask endpoint error: {e}")
        return False

def main():
    print("=" * 60)
    print("WanderSure Smoke Test")
    print("=" * 60)
    print(f"Testing API at: {API_BASE_URL}\n")
    
    results = []
    
    # Test health
    results.append(("Health Check", test_health()))
    
    # Test greeting
    results.append(("Greeting", test_greeting()))
    
    # Test ask
    results.append(("Ask", test_ask()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 All tests passed! The system is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()

