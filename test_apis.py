#!/usr/bin/env python3
"""
Simple test script to verify the Ops Mesh APIs
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_api(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"\n{'='*50}")
        print(f"Testing: {method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    print("🧪 Testing Ops Mesh APIs")
    print(f"Backend URL: {BASE_URL}")
    print(f"Time: {datetime.now()}")
    
    # Test health endpoint
    test_api("/health", "GET")
    
    # Test dashboard stats
    test_api("/dashboard/stats", "GET")
    
    # Test queue summary
    test_api("/dashboard/queue-summary", "GET")
    
    # Test KPIs
    test_api("/dashboard/kpis", "GET")
    
    # Test appointments
    test_api("/appointments/", "GET")
    
    # Test queue entries
    test_api("/queue/", "GET")
    
    # Test walk-in creation
    walk_in_data = {
        "first_name": "Test",
        "last_name": "Patient",
        "reason": "Test walk-in",
        "priority": "medium",
        "phone": "555-1234"
    }
    test_api("/queue/walk-in", "POST", walk_in_data)
    
    # Test appointment check-in
    check_in_data = {
        "confirmation_code": "KRPM-4350",  # Use a real code from the seeded data
        "last_name": "Wilson"  # Use a real last name from the seeded data
    }
    test_api("/appointments/check-in", "POST", check_in_data)
    
    print(f"\n{'='*50}")
    print("✅ API testing complete!")

if __name__ == "__main__":
    main()

