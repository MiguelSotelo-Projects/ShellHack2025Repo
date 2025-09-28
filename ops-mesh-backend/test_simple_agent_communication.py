#!/usr/bin/env python3
"""
Simple Agent-to-Agent Communication Test

This script tests the agent-to-agent communication protocol without Google ADK dependencies.
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


class SimpleTestAgent:
    """Simple test agent for demonstrating communication."""
    
    def __init__(self, agent_id: str, project_id: str):
        self.agent_id = agent_id
        self.protocol = AgentProtocol(agent_id, project_id)
        self.message_count = 0
    
    async def initialize(self):
        """Initialize the agent protocol."""
        await self.protocol.initialize()
        
        # Register message handlers
        self.protocol.register_handler(MessageType.REQUEST, self._handle_request)
        self.protocol.register_handler(MessageType.NOTIFICATION, self._handle_notification)
        
        logger.info(f"Initialized {self.agent_id}")
    
    async def _handle_request(self, message: ProtocolMessage):
        """Handle incoming requests."""
        self.message_count += 1
        logger.info(f"{self.agent_id} received request #{self.message_count}: {message.payload}")
        
        # Send response
        response_payload = {
            "status": "processed",
            "agent": self.agent_id,
            "message_count": self.message_count,
            "result": f"Request handled by {self.agent_id}"
        }
        
        await self.protocol.send_response(message, response_payload)
    
    async def _handle_notification(self, message: ProtocolMessage):
        """Handle notifications."""
        logger.info(f"{self.agent_id} received notification: {message.payload}")
    
    async def send_test_message(self, target_agent: str, message_type: MessageType, payload: dict):
        """Send a test message to another agent."""
        return await self.protocol.send_message(
            recipient_id=target_agent,
            message_type=message_type,
            payload=payload,
            priority=Priority.MEDIUM
        )
    
    async def start_listening(self):
        """Start listening for messages."""
        await self.protocol.start_listening()
    
    async def stop(self):
        """Stop the agent."""
        await self.protocol.stop_listening()


async def test_agent_communication():
    """Test agent-to-agent communication."""
    logger.info("🧪 Testing Simple Agent-to-Agent Communication...")
    
    # Get project ID
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        logger.error("❌ GOOGLE_CLOUD_PROJECT not set")
        return
    
    # Create test agents
    agent1 = SimpleTestAgent("test_agent_1", project_id)
    agent2 = SimpleTestAgent("test_agent_2", project_id)
    
    try:
        # Initialize agents
        logger.info("🔧 Initializing test agents...")
        await agent1.initialize()
        await agent2.initialize()
        
        # Start listening in background
        task1 = asyncio.create_task(agent1.start_listening())
        task2 = asyncio.create_task(agent2.start_listening())
        
        # Wait a bit for agents to start
        await asyncio.sleep(2)
        
        # Test 1: Send request from agent1 to agent2
        logger.info("📝 Test 1: Agent1 → Agent2 Request")
        message_id = await agent1.send_test_message(
            target_agent="test_agent_2",
            message_type=MessageType.REQUEST,
            payload={"action": "test_request", "data": "Hello from Agent1"}
        )
        logger.info(f"   ✅ Sent message: {message_id}")
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Test 2: Send notification from agent2 to agent1
        logger.info("📢 Test 2: Agent2 → Agent1 Notification")
        message_id = await agent2.send_test_message(
            target_agent="test_agent_1",
            message_type=MessageType.NOTIFICATION,
            payload={"event": "test_notification", "data": "Hello from Agent2"}
        )
        logger.info(f"   ✅ Sent notification: {message_id}")
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Test 3: Multiple messages
        logger.info("🔄 Test 3: Multiple Messages")
        for i in range(3):
            message_id = await agent1.send_test_message(
                target_agent="test_agent_2",
                message_type=MessageType.REQUEST,
                payload={"action": f"batch_request_{i}", "data": f"Message {i+1}"}
            )
            logger.info(f"   ✅ Sent batch message {i+1}: {message_id}")
            await asyncio.sleep(1)
        
        # Wait for all processing
        await asyncio.sleep(3)
        
        logger.info("✅ All communication tests completed successfully!")
        logger.info(f"📊 Agent1 processed {agent1.message_count} messages")
        logger.info(f"📊 Agent2 processed {agent2.message_count} messages")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    finally:
        # Stop agents
        await agent1.stop()
        await agent2.stop()
        
        # Cancel tasks
        task1.cancel()
        task2.cancel()
        
        try:
            await asyncio.gather(task1, task2, return_exceptions=True)
        except:
            pass


async def main():
    """Main function."""
    print("🧪 Simple Agent-to-Agent Communication Test")
    print("=" * 50)
    print("This test will demonstrate:")
    print("• Basic agent-to-agent messaging")
    print("• Request/Response patterns")
    print("• Notification handling")
    print("• Multiple message processing")
    print("=" * 50)
    print()
    
    await test_agent_communication()


if __name__ == "__main__":
    asyncio.run(main())
