#!/usr/bin/env python3
"""
Minimal System Test

This script tests the A2A system with minimal dependencies.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if we can import the essential modules"""
    print("🧪 Testing Essential Imports...")
    
    tests = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("aiohttp", "Async HTTP client"),
        ("websockets", "WebSocket support"),
    ]
    
    results = []
    for module, description in tests:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
            results.append(True)
        except ImportError as e:
            print(f"❌ {module} - {description} (Error: {e})")
            results.append(False)
    
    return results

def test_a2a_protocol():
    """Test A2A protocol with fallback implementation"""
    print("\n🤖 Testing A2A Protocol...")
    
    try:
        # Add the app directory to the Python path
        app_dir = Path(__file__).parent / "app"
        sys.path.insert(0, str(app_dir))
        
        from agents.protocol.a2a_protocol import A2AProtocol, A2ATaskRequest
        from agents.google_adk_fallback import Agent, BaseTool
        
        print("✅ A2A Protocol imports successful")
        
        # Test creating a simple agent
        agent = Agent("test_agent", "gemini-1.5-flash")
        print("✅ Agent creation successful")
        
        # Test creating a task request
        task = A2ATaskRequest(
            task_id="test-001",
            sender_id="test_sender",
            recipient_id="test_recipient",
            action="test_action",
            data={"test": "data"}
        )
        print("✅ Task request creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ A2A Protocol test failed: {e}")
        return False

def test_agent_cards():
    """Test if agent cards exist and are valid"""
    print("\n📋 Testing Agent Cards...")
    
    agent_cards = [
        "agents/frontdesk_agent.json",
        "agents/queue_agent.json", 
        "agents/appointment_agent.json",
        "agents/notification_agent.json",
        "agents/orchestrator_agent.json"
    ]
    
    results = []
    for card_path in agent_cards:
        if Path(card_path).exists():
            print(f"✅ {card_path} exists")
            results.append(True)
        else:
            print(f"❌ {card_path} missing")
            results.append(False)
    
    return results

def main():
    print("🧪 Minimal System Test")
    print("=" * 30)
    
    # Test imports
    import_results = test_imports()
    
    # Test A2A protocol
    a2a_result = test_a2a_protocol()
    
    # Test agent cards
    card_results = test_agent_cards()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    
    import_success = sum(import_results)
    card_success = sum(card_results)
    
    print(f"📦 Imports: {import_success}/{len(import_results)} successful")
    print(f"🤖 A2A Protocol: {'✅ PASS' if a2a_result else '❌ FAIL'}")
    print(f"📋 Agent Cards: {card_success}/{len(card_results)} found")
    
    if import_success >= 3 and a2a_result and card_success >= 3:
        print("\n🎉 System is ready!")
        print("\n🚀 You can now run:")
        print("   python setup_a2a.py --setup")
        print("   python test_a2a_implementation.py")
    else:
        print("\n⚠️  System needs more setup")
        if import_success < 3:
            print("   - Install missing packages: python install_essentials.py")
        if not a2a_result:
            print("   - Check A2A protocol implementation")
        if card_success < 3:
            print("   - Check agent card files")

if __name__ == "__main__":
    main()
