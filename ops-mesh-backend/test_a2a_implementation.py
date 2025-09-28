#!/usr/bin/env python3
"""
Test A2A Implementation

This script tests the complete A2A (Agent-to-Agent) implementation for Ops Mesh.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from agents.agent_manager import AgentManager
from agents.discovery_service import discovery_service
from agents.adk_tools import AgentDiscoveryTool, A2ACommunicationTool, HospitalOperationsTool
from agents.protocol.a2a_protocol import A2AProtocol, A2ATaskRequest, TaskStatus

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class A2AImplementationTester:
    """Test the A2A implementation"""
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.agent_manager = None
        self.test_results = {}
    
    async def run_all_tests(self):
        """Run all A2A implementation tests"""
        logger.info("🧪 Starting A2A Implementation Tests...")
        
        try:
            # Test 1: Discovery Service
            await self.test_discovery_service()
            
            # Test 2: Agent Registration
            await self.test_agent_registration()
            
            # Test 3: Agent Manager
            await self.test_agent_manager()
            
            # Test 4: ADK Tools
            await self.test_adk_tools()
            
            # Test 5: A2A Communication
            await self.test_a2a_communication()
            
            # Test 6: End-to-End Workflow
            await self.test_end_to_end_workflow()
            
            # Print results
            self.print_test_results()
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            raise
        finally:
            if self.agent_manager:
                await self.agent_manager.stop_all_agents()
    
    async def test_discovery_service(self):
        """Test the discovery service"""
        logger.info("🔍 Testing Discovery Service...")
        
        try:
            # Start discovery service
            await discovery_service.start()
            
            # Test agent registration
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
            
            # Test agent discovery
            agents = await discovery_service.discover_agents()
            assert len(agents) > 0, "No agents discovered"
            
            # Test capability search
            matching_agents = await discovery_service.find_agents_by_capability("test_capability")
            assert len(matching_agents) > 0, "No agents found with test capability"
            
            # Test health check
            is_healthy = await discovery_service.check_agent_health("test_agent")
            assert is_healthy, "Agent health check failed"
            
            # Test stats
            stats = await discovery_service.get_discovery_stats()
            assert stats["total_agents"] > 0, "Discovery stats incorrect"
            
            self.test_results["discovery_service"] = "✅ PASSED"
            logger.info("✅ Discovery Service test passed")
            
        except Exception as e:
            self.test_results["discovery_service"] = f"❌ FAILED: {e}"
            logger.error(f"❌ Discovery Service test failed: {e}")
            raise
    
    async def test_agent_registration(self):
        """Test agent registration and card loading"""
        logger.info("📋 Testing Agent Registration...")
        
        try:
            # Check if agent cards exist
            agent_cards = [
                "ops-mesh-backend/agents/frontdesk_agent.json",
                "ops-mesh-backend/agents/queue_agent.json",
                "ops-mesh-backend/agents/appointment_agent.json",
                "ops-mesh-backend/agents/notification_agent.json",
                "ops-mesh-backend/agents/orchestrator_agent.json"
            ]
            
            for card_path in agent_cards:
                assert Path(card_path).exists(), f"Agent card not found: {card_path}"
            
            # Test loading agent cards
            await discovery_service._load_agent_cards()
            
            # Verify agents are loaded
            agents = await discovery_service.discover_agents()
            expected_agents = ["frontdesk_agent", "queue_agent", "appointment_agent", 
                             "notification_agent", "orchestrator_agent"]
            
            loaded_agent_ids = [agent["agent_id"] for agent in agents]
            for expected_agent in expected_agents:
                assert expected_agent in loaded_agent_ids, f"Agent {expected_agent} not loaded"
            
            self.test_results["agent_registration"] = "✅ PASSED"
            logger.info("✅ Agent Registration test passed")
            
        except Exception as e:
            self.test_results["agent_registration"] = f"❌ FAILED: {e}"
            logger.error(f"❌ Agent Registration test failed: {e}")
            raise
    
    async def test_agent_manager(self):
        """Test the agent manager"""
        logger.info("🤖 Testing Agent Manager...")
        
        try:
            # Create agent manager
            self.agent_manager = AgentManager(self.project_id)
            
            # Test initialization
            await self.agent_manager.initialize_all_agents()
            
            # Test agent status
            status = await self.agent_manager.get_agent_status()
            assert len(status) > 0, "No agent status returned"
            
            # Test discovery info
            discovery_info = await self.agent_manager.get_discovery_info()
            assert "discovery_stats" in discovery_info, "Discovery info missing stats"
            assert "available_agents" in discovery_info, "Discovery info missing agents"
            
            self.test_results["agent_manager"] = "✅ PASSED"
            logger.info("✅ Agent Manager test passed")
            
        except Exception as e:
            self.test_results["agent_manager"] = f"❌ FAILED: {e}"
            logger.error(f"❌ Agent Manager test failed: {e}")
            raise
    
    async def test_adk_tools(self):
        """Test ADK tools"""
        logger.info("🔧 Testing ADK Tools...")
        
        try:
            # Test Agent Discovery Tool
            discovery_tool = AgentDiscoveryTool()
            result = await discovery_tool.execute({"action": "discover_agents"})
            assert result["success"], "Agent discovery tool failed"
            
            # Test A2A Communication Tool
            comm_tool = A2ACommunicationTool()
            result = await comm_tool.execute({
                "action": "send_task",
                "recipient_id": "test_agent",
                "action": "test_action",
                "data": {"test": "data"}
            })
            assert result["success"], "A2A communication tool failed"
            
            # Test Hospital Operations Tool
            ops_tool = HospitalOperationsTool()
            result = await ops_tool.execute({"operation": "get_system_status"})
            assert result["success"], "Hospital operations tool failed"
            
            self.test_results["adk_tools"] = "✅ PASSED"
            logger.info("✅ ADK Tools test passed")
            
        except Exception as e:
            self.test_results["adk_tools"] = f"❌ FAILED: {e}"
            logger.error(f"❌ ADK Tools test failed: {e}")
            raise
    
    async def test_a2a_communication(self):
        """Test A2A communication protocol"""
        logger.info("📡 Testing A2A Communication...")
        
        try:
            # Test task request creation
            task = A2ATaskRequest(
                task_id="test-task-001",
                sender_id="test_sender",
                recipient_id="test_recipient",
                action="test_action",
                data={"test": "data"}
            )
            
            assert task.task_id == "test-task-001", "Task ID incorrect"
            assert task.action == "test_action", "Task action incorrect"
            
            # Test task serialization
            task_dict = task.to_dict()
            assert "task_id" in task_dict, "Task serialization failed"
            
            # Test task deserialization
            restored_task = A2ATaskRequest.from_dict(task_dict)
            assert restored_task.task_id == task.task_id, "Task deserialization failed"
            
            # Test A2A Protocol creation
            protocol = A2AProtocol("test_agent")
            assert protocol.agent_id == "test_agent", "Protocol agent ID incorrect"
            
            self.test_results["a2a_communication"] = "✅ PASSED"
            logger.info("✅ A2A Communication test passed")
            
        except Exception as e:
            self.test_results["a2a_communication"] = f"❌ FAILED: {e}"
            logger.error(f"❌ A2A Communication test failed: {e}")
            raise
    
    async def test_end_to_end_workflow(self):
        """Test end-to-end workflow"""
        logger.info("🔄 Testing End-to-End Workflow...")
        
        try:
            # Test patient registration workflow
            from agents.protocol.a2a_protocol import A2AWorkflowOrchestrator
            
            # Create a test protocol
            protocol = A2AProtocol("test_orchestrator")
            orchestrator = A2AWorkflowOrchestrator(protocol)
            
            # Define a test workflow
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
            
            # Start workflow
            workflow_id = await orchestrator.start_workflow("test_workflow_001", workflow_definition)
            assert workflow_id == "test_workflow_001", "Workflow ID incorrect"
            
            # Check workflow status
            status = orchestrator.get_workflow_status(workflow_id)
            assert status is not None, "Workflow status not found"
            assert status["status"] == "active", "Workflow not active"
            
            # Complete workflow
            await orchestrator.complete_workflow(workflow_id, {"result": "success"})
            
            # Check completed status
            final_status = orchestrator.get_workflow_status(workflow_id)
            assert final_status["status"] == "completed", "Workflow not completed"
            
            self.test_results["end_to_end_workflow"] = "✅ PASSED"
            logger.info("✅ End-to-End Workflow test passed")
            
        except Exception as e:
            self.test_results["end_to_end_workflow"] = f"❌ FAILED: {e}"
            logger.error(f"❌ End-to-End Workflow test failed: {e}")
            raise
    
    def print_test_results(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("🧪 A2A IMPLEMENTATION TEST RESULTS")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.startswith("✅")])
        failed_tests = total_tests - passed_tests
        
        for test_name, result in self.test_results.items():
            print(f"{test_name.replace('_', ' ').title()}: {result}")
        
        print("-"*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! A2A implementation is working correctly.")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed. Please review the implementation.")
        
        print("="*60)


async def main():
    """Main function"""
    print("🧪 A2A Implementation Test Suite")
    print("="*50)
    print("This test suite will verify:")
    print("• Discovery Service functionality")
    print("• Agent registration and card loading")
    print("• Agent Manager operations")
    print("• ADK Tools functionality")
    print("• A2A Communication protocol")
    print("• End-to-end workflow execution")
    print("="*50)
    print()
    
    # Get project ID
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
        print("Please set GOOGLE_CLOUD_PROJECT in your .env file")
        return
    
    # Run tests
    tester = A2AImplementationTester(project_id)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
