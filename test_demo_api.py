#!/usr/bin/env python3
"""
Test Demo API - Quick test of the A2A protocol demo API
"""

import requests
import json
import time

def test_backend_api():
    """Test the backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing A2A Protocol Demo API")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print()
    
    # Test 2: Agent status
    print("2. Testing agent status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/agents/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Agent status endpoint working")
            print(f"   Total agents: {data.get('total_agents', 0)}")
            if 'agents' in data:
                for agent in data['agents']:
                    print(f"   - {agent.get('agent_id', 'unknown')}: {agent.get('status', 'unknown')}")
        else:
            print(f"❌ Agent status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Agent status error: {e}")
    
    print()
    
    # Test 3: Discovery info
    print("3. Testing discovery info endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/agents/discovery")
        if response.status_code == 200:
            data = response.json()
            print("✅ Discovery info endpoint working")
            if 'discovery' in data:
                discovery = data['discovery']
                print(f"   Discovery stats: {discovery.get('discovery_stats', {})}")
        else:
            print(f"❌ Discovery info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Discovery info error: {e}")
    
    print()
    
    # Test 4: Agent communication test
    print("4. Testing agent communication...")
    try:
        response = requests.get(f"{base_url}/api/v1/agents/test-communication")
        if response.status_code == 200:
            data = response.json()
            print("✅ Agent communication test passed")
            print(f"   Result: {data.get('message', 'No message')}")
        else:
            print(f"❌ Agent communication test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Agent communication error: {e}")
    
    print()
    
    # Test 5: Patient registration workflow
    print("5. Testing patient registration workflow...")
    try:
        patient_data = {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "555-0123",
            "email": "john.doe@example.com",
            "priority": "medium"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/agents/workflow/patient-registration",
            json=patient_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Patient registration workflow started")
            print(f"   Workflow ID: {data.get('workflow_id', 'No ID')}")
        else:
            print(f"❌ Patient registration failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Patient registration error: {e}")
    
    print()
    
    # Test 6: Queue management workflow
    print("6. Testing queue management workflow...")
    try:
        queue_data = {
            "action": "get_queue_status"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/agents/workflow/queue-management",
            json=queue_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Queue management workflow started")
            print(f"   Workflow ID: {data.get('workflow_id', 'No ID')}")
        else:
            print(f"❌ Queue management failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Queue management error: {e}")
    
    print()
    print("🎉 API Testing Complete!")
    print("=" * 50)
    print("If all tests passed, your A2A protocol is working correctly!")
    print()
    print("🌐 Demo URLs:")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Agent Status: http://localhost:8000/api/v1/agents/status")
    print("   • Health Check: http://localhost:8000/health")
    print()
    print("📝 To start the frontend:")
    print("   1. Open a new terminal")
    print("   2. cd ops-mesh-frontend")
    print("   3. npm install (if not done already)")
    print("   4. npm run dev")
    print("   5. Visit: http://localhost:3000/agent-demo")

if __name__ == "__main__":
    test_backend_api()
