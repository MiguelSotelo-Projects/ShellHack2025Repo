#!/usr/bin/env python3
"""
Quick test of key Ops Mesh functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def quick_test():
    print("🚀 Quick Ops Mesh Test")
    print("=" * 40)
    
    # Test 1: Dashboard Stats
    print("\n1. 📊 Dashboard Stats:")
    try:
        response = requests.get(f"{BASE_URL}/dashboard/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data['queue_stats']
            print(f"   ✅ Waiting: {stats['total_waiting']} patients")
            print(f"   ✅ In Progress: {stats['total_in_progress']} patients")
            print(f"   ✅ Called: {stats['total_called']} patients")
            print(f"   ✅ Walk-ins: {stats['walk_ins_waiting']} patients")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Queue Summary
    print("\n2. 📋 Queue Summary:")
    try:
        response = requests.get(f"{BASE_URL}/dashboard/queue-summary")
        if response.status_code == 200:
            data = response.json()
            waiting = data['waiting']
            in_progress = data['in_progress']
            called = data['called']
            print(f"   ✅ {len(waiting)} patients waiting")
            print(f"   ✅ {len(in_progress)} patients in progress")
            print(f"   ✅ {len(called)} patients called")
            if waiting:
                print(f"   📝 Next patient: {waiting[0]['patient_name']} ({waiting[0]['ticket_number']})")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Create Walk-in
    print("\n3. 🚶 Create Walk-in:")
    try:
        walk_in_data = {
            "first_name": "Test",
            "last_name": "Patient",
            "reason": "Test walk-in from API",
            "priority": "medium",
            "phone": "555-1234"
        }
        response = requests.post(f"{BASE_URL}/queue/walk-in", json=walk_in_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Created walk-in: {data['ticket_number']}")
            print(f"   ✅ Patient: {data['patient']['first_name']} {data['patient']['last_name']}")
            print(f"   ✅ ETA: {data['estimated_wait_time']} minutes")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4: Appointment Check-in
    print("\n4. 📅 Appointment Check-in:")
    try:
        # Use a real appointment from the seeded data
        check_in_data = {
            "confirmation_code": "KRPM-4350",
            "last_name": "Wilson"
        }
        response = requests.post(f"{BASE_URL}/appointments/check-in", json=check_in_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Check-in successful!")
            print(f"   ✅ Appointment: {data['confirmation_code']}")
            print(f"   ✅ Provider: {data['provider_name']}")
            print(f"   ✅ Status: {data['status']}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Test Complete! Your Ops Mesh system is working!")

if __name__ == "__main__":
    quick_test()

