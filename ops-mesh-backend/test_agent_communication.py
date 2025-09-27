#!/usr/bin/env python3
"""
Test Agent-to-Agent Communication

This script demonstrates and tests the agent-to-agent communication system.
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
from agents.protocol.agent_protocol import MessageType, Priority

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_agent_communication():
    """Test agent-to-agent communication."""
    logger.info("🧪 Testing Agent-to-Agent Communication...")
    
    # Get project ID
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        logger.error("❌ GOOGLE_CLOUD_PROJECT not set")
        return
    
    # Create agent manager
    manager = AgentManager(project_id)
    
    try:
        # Initialize agents
        logger.info("🔧 Initializing agents for testing...")
        await manager.initialize_all_agents()
        
        # Test 1: Patient Registration Flow
        logger.info("📝 Test 1: Patient Registration Flow")
        await test_patient_registration_flow(manager)
        
        # Test 2: Appointment Scheduling Flow
        logger.info("📅 Test 2: Appointment Scheduling Flow")
        await test_appointment_scheduling_flow(manager)
        
        # Test 3: Emergency Coordination
        logger.info("🚨 Test 3: Emergency Coordination")
        await test_emergency_coordination(manager)
        
        # Test 4: Queue Management
        logger.info("📊 Test 4: Queue Management")
        await test_queue_management(manager)
        
        logger.info("✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    finally:
        await manager.stop_all_agents()


async def test_patient_registration_flow(manager: AgentManager):
    """Test patient registration workflow."""
    logger.info("   🏥 Testing patient registration workflow...")
    
    # Simulate patient registration
    patient_data = {
        "patient_id": "PAT-001",
        "first_name": "John",
        "last_name": "Doe",
        "priority": "medium"
    }
    
    # Send message to orchestrator to start patient flow
    success = await manager.send_message_to_agent(
        target_agent="orchestrator",
        message_type="request",
        payload={
            "action": "start_patient_flow",
            "patient_data": patient_data,
            "flow_type": "walk_in"
        }
    )
    
    if success:
        logger.info("   ✅ Patient registration flow initiated")
    else:
        logger.error("   ❌ Failed to initiate patient registration flow")
    
    # Wait a bit for processing
    await asyncio.sleep(2)


async def test_appointment_scheduling_flow(manager: AgentManager):
    """Test appointment scheduling workflow."""
    logger.info("   📅 Testing appointment scheduling workflow...")
    
    # Simulate appointment scheduling
    appointment_data = {
        "patient_id": "PAT-002",
        "provider": "Dr. Smith",
        "appointment_time": "2024-01-15 10:00:00",
        "type": "routine"
    }
    
    # Send message to orchestrator to start appointment flow
    success = await manager.send_message_to_agent(
        target_agent="orchestrator",
        message_type="request",
        payload={
            "action": "start_appointment_flow",
            "appointment_data": appointment_data
        }
    )
    
    if success:
        logger.info("   ✅ Appointment scheduling flow initiated")
    else:
        logger.error("   ❌ Failed to initiate appointment scheduling flow")
    
    # Wait a bit for processing
    await asyncio.sleep(2)


async def test_emergency_coordination(manager: AgentManager):
    """Test emergency coordination."""
    logger.info("   🚨 Testing emergency coordination...")
    
    # Simulate emergency situation
    emergency_data = {
        "patient_id": "PAT-003",
        "emergency_type": "cardiac",
        "severity": "critical"
    }
    
    # Send emergency message to orchestrator
    success = await manager.send_message_to_agent(
        target_agent="orchestrator",
        message_type="request",
        payload={
            "action": "coordinate_emergency",
            "emergency_data": emergency_data
        }
    )
    
    if success:
        logger.info("   ✅ Emergency coordination initiated")
    else:
        logger.error("   ❌ Failed to initiate emergency coordination")
    
    # Wait a bit for processing
    await asyncio.sleep(2)


async def test_queue_management(manager: AgentManager):
    """Test queue management."""
    logger.info("   📊 Testing queue management...")
    
    # Test queue operations
    queue_operations = [
        {
            "action": "add_to_queue",
            "patient_id": "PAT-004",
            "priority": "high"
        },
        {
            "action": "get_queue_status"
        },
        {
            "action": "call_next_patient"
        }
    ]
    
    for operation in queue_operations:
        success = await manager.send_message_to_agent(
            target_agent="queue",
            message_type="request",
            payload=operation
        )
        
        if success:
            logger.info(f"   ✅ Queue operation '{operation['action']}' completed")
        else:
            logger.error(f"   ❌ Queue operation '{operation['action']}' failed")
        
        await asyncio.sleep(1)


async def main():
    """Main function."""
    print("🧪 Ops Mesh Agent-to-Agent Communication Test")
    print("=" * 50)
    print("This test will demonstrate:")
    print("• Patient registration workflow")
    print("• Appointment scheduling workflow")
    print("• Emergency coordination")
    print("• Queue management")
    print("=" * 50)
    print()
    
    await test_agent_communication()


if __name__ == "__main__":
    asyncio.run(main())
