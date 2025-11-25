"""
Simple script to test the API endpoints
Run this after starting the backend to verify everything works
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"❌ Unknown method: {method}")
            return
        
        print(f"\n{'='*50}")
        print(f"{method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)[:500]}...")
            except:
                print(f"Response: {response.text[:500]}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🧪 Testing Earth's Pulse API")
    print(f"Base URL: {BASE_URL}")
    
    # Test health endpoint
    test_endpoint("GET", "/api/health")
    
    # Test root endpoint
    test_endpoint("GET", "/")
    
    # Test moods endpoint
    test_endpoint("GET", "/api/moods?limit=10")
    
    # Test stats endpoint
    test_endpoint("GET", "/api/stats")
    
    # Test summary endpoint
    test_endpoint("GET", "/api/summary")
    
    # Test refresh endpoint (this will fetch new data)
    print("\n" + "="*50)
    print("⚠️  Testing refresh endpoint (this may take a moment)...")
    test_endpoint("POST", "/api/moods/refresh")
    
    print("\n" + "="*50)
    print("✅ API testing complete!")
    print("\nIf all endpoints returned 200, your API is working correctly!")

if __name__ == "__main__":
    main()

