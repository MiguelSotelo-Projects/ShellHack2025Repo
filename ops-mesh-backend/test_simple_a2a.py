#!/usr/bin/env python3
"""
Simple A2A Test - Tests basic functionality without Google Cloud dependencies
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from agents.protocol.a2a_protocol import A2AProtocol, A2ATaskRequest, TaskStatus, A2AWorkflowOrchestrator
from agents.discovery_service import discovery_service

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_basic_a2a_functionality():
    """Test basic A2A functionality without external dependencies"""
    logger.info("🧪 Testing Basic A2A Functionality...")
    
    try:
        # Test 1: A2A Protocol Creation
        logger.info("📡 Test 1: A2A Protocol Creation")
        protocol = A2AProtocol("test_agent")
        assert protocol.agent_id == "test_agent", "Protocol agent ID incorrect"
        logger.info("✅ A2A Protocol creation passed")
        
        # Test 2: Task Request Creation
        logger.info("📋 Test 2: Task Request Creation")
        task = A2ATaskRequest(
            task_id="test-task-001",
            sender_id="test_sender",
            recipient_id="test_recipient",
            action="test_action",
            data={"test": "data"}
        )
        assert task.task_id == "test-task-001", "Task ID incorrect"
        assert task.action == "test_action", "Task action incorrect"
        logger.info("✅ Task Request creation passed")
        
        # Test 3: Task Serialization
        logger.info("🔄 Test 3: Task Serialization")
        task_dict = task.to_dict()
        assert "task_id" in task_dict, "Task serialization failed"
        
        restored_task = A2ATaskRequest.from_dict(task_dict)
        assert restored_task.task_id == task.task_id, "Task deserialization failed"
        logger.info("✅ Task serialization passed")
        
        # Test 4: Discovery Service
        logger.info("🔍 Test 4: Discovery Service")
        await discovery_service.start()
        
        # Register a test agent
        test_agent_info = {
            "name": "test_agent",
            "description": "Test agent for A2A testing",
            "capabilities": ["test_capability"],
            "endpoints": {"test_endpoint": {"description": "Test endpoint"}},
            "dependencies": [],
            "status": "available"
        }
        
        success = await discovery_service.register_agent("test_agent", test_agent_info)
        assert success, "Agent registration failed"
        
        agents = await discovery_service.discover_agents()
        assert len(agents) > 0, "No agents discovered"
        logger.info("✅ Discovery Service test passed")
        
        # Test 5: Workflow Orchestrator
        logger.info("🔄 Test 5: Workflow Orchestrator")
        orchestrator = A2AWorkflowOrchestrator(protocol)
        
        workflow_definition = {
            "type": "test_workflow",
            "steps": [
                {
                    "step": 1,
                    "action": "test_action",
                    "target_agent": "test_agent",
                    "data": {"test": "data"}
                }
            ]
        }
        
        workflow_id = await orchestrator.start_workflow("test_workflow_001", workflow_definition)
        assert workflow_id == "test_workflow_001", "Workflow ID incorrect"
        
        status = orchestrator.get_workflow_status(workflow_id)
        assert status is not None, "Workflow status not found"
        assert status["status"] == "active", "Workflow not active"
        logger.info("✅ Workflow Orchestrator test passed")
        
        # Cleanup
        await discovery_service.stop()
        
        logger.info("🎉 All basic A2A tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


async def main():
    """Main function"""
    print("🧪 Simple A2A Test Suite")
    print("=" * 50)
    print("This test will verify basic A2A functionality:")
    print("• A2A Protocol creation")
    print("• Task Request/Response handling")
    print("• Discovery Service")
    print("• Workflow Orchestration")
    print("=" * 50)
    print()
    
    success = await test_basic_a2a_functionality()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Basic A2A functionality is working.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())
