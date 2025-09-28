#!/usr/bin/env python3
"""
Test Real Agent-to-Agent Communication

This script tests the real agent-to-agent communication system using Google Cloud Pub/Sub.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from agents.protocol.agent_protocol import AgentProtocol, MessageType, Priority, ProtocolMessage

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_real_agent_communication():
    """Test real agent-to-agent communication."""
    logger.info("🧪 Testing Real Agent-to-Agent Communication...")
    
    # Get project ID
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        logger.error("❌ GOOGLE_CLOUD_PROJECT not set")
        return
    
    # Create test protocol
    protocol = AgentProtocol("test_client", project_id)
    
    try:
        # Initialize protocol
        logger.info("🔧 Initializing communication protocol...")
        await protocol.initialize()
        
        # Test 1: Send message to frontdesk agent
        logger.info("🏥 Test 1: Patient Registration Request")
        message_id = await protocol.send_message(
            recipient_id="frontdesk_agent",
            message_type=MessageType.REQUEST,
            payload={
                "action": "register_patient",
                "patient_data": {
                    "patient_id": "PAT-TEST-001",
                    "name": "John Doe",
                    "priority": "medium"
                }
            },
            priority=Priority.MEDIUM
        )
        logger.info(f"   ✅ Sent registration request: {message_id}")
        
        await asyncio.sleep(2)
        
        # Test 2: Send message to queue agent
        logger.info("📊 Test 2: Queue Management Request")
        message_id = await protocol.send_message(
            recipient_id="queue_agent",
            message_type=MessageType.REQUEST,
            payload={
                "action": "add_to_queue",
                "patient_id": "PAT-TEST-002",
                "priority": "high"
            },
            priority=Priority.HIGH
        )
        logger.info(f"   ✅ Sent queue request: {message_id}")
        
        await asyncio.sleep(2)
        
        # Test 3: Send message to appointment agent
        logger.info("📅 Test 3: Appointment Scheduling Request")
        message_id = await protocol.send_message(
            recipient_id="appointment_agent",
            message_type=MessageType.REQUEST,
            payload={
                "action": "schedule_appointment",
                "appointment_data": {
                    "patient_id": "PAT-TEST-003",
                    "provider": "Dr. Smith",
                    "time": "2024-01-15 10:00:00"
                }
            },
            priority=Priority.MEDIUM
        )
        logger.info(f"   ✅ Sent appointment request: {message_id}")
        
        await asyncio.sleep(2)
        
        # Test 4: Send notification
        logger.info("🔔 Test 4: Notification Request")
        message_id = await protocol.send_message(
            recipient_id="notification_agent",
            message_type=MessageType.REQUEST,
            payload={
                "action": "send_notification",
                "recipient": "patient_PAT-TEST-001",
                "message": "Your appointment is confirmed"
            },
            priority=Priority.MEDIUM
        )
        logger.info(f"   ✅ Sent notification request: {message_id}")
        
        await asyncio.sleep(2)
        
        logger.info("✅ All real agent communication tests completed!")
        logger.info("🔗 Messages sent via Google Cloud Pub/Sub")
        logger.info("📡 Agents should be processing messages in real-time")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    finally:
        # Clean up
        await protocol.stop_listening()


async def main():
    """Main function."""
    print("🧪 Real Agent-to-Agent Communication Test")
    print("=" * 50)
    print("This test will send real messages to the running agents:")
    print("• Patient registration request → FrontDesk Agent")
    print("• Queue management request → Queue Agent")
    print("• Appointment scheduling request → Appointment Agent")
    print("• Notification request → Notification Agent")
    print("=" * 50)
    print("🔗 Using Google Cloud Pub/Sub for real-time communication")
    print("=" * 50)
    print()
    
    await test_real_agent_communication()


if __name__ == "__main__":
    asyncio.run(main())
