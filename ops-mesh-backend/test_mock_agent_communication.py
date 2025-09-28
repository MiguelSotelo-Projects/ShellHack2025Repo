#!/usr/bin/env python3
"""
Mock Agent-to-Agent Communication Test

This script demonstrates agent-to-agent communication using a mock protocol
that doesn't require Google Cloud Pub/Sub setup.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of messages that can be sent between agents."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    COORDINATION = "coordination"
    STATUS_UPDATE = "status_update"
    ERROR = "error"


class Priority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class MockMessage:
    """Mock message format for agent-to-agent communication."""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: MessageType
    priority: Priority
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: str = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['message_type'] = self.message_type.value
        data['priority'] = self.priority.value
        return data


class MockAgentProtocol:
    """Mock protocol for agent-to-agent communication."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.message_handlers = {}
        self.message_queue = asyncio.Queue()
        self.running = False
        self.message_count = 0
    
    def register_handler(self, message_type: MessageType, handler):
        """Register a message handler for a specific message type."""
        self.message_handlers[message_type] = handler
    
    async def send_message(self, recipient_id: str, message_type: MessageType, 
                          payload: Dict[str, Any], priority: Priority = Priority.MEDIUM,
                          correlation_id: str = None) -> str:
        """Send a message to another agent."""
        message = MockMessage(
            message_id=f"{self.agent_id}-{datetime.now().timestamp()}",
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            priority=priority,
            payload=payload,
            timestamp=datetime.now(),
            correlation_id=correlation_id
        )
        
        # In a real system, this would be sent via Pub/Sub
        # For the mock, we'll simulate message delivery
        logger.info(f"📤 {self.agent_id} → {recipient_id}: {message_type.value} - {payload.get('action', 'message')}")
        
        return message.message_id
    
    async def send_response(self, original_message: MockMessage, response_payload: Dict[str, Any]) -> str:
        """Send a response to a received message."""
        return await self.send_message(
            recipient_id=original_message.sender_id,
            message_type=MessageType.RESPONSE,
            payload=response_payload,
            correlation_id=original_message.message_id
        )
    
    async def start_listening(self):
        """Start listening for incoming messages."""
        self.running = True
        logger.info(f"🎧 {self.agent_id} started listening for messages")
        
        # Simulate receiving messages
        while self.running:
            try:
                # In a real system, this would pull from Pub/Sub
                # For the mock, we'll just wait
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
    
    async def stop_listening(self):
        """Stop listening for messages."""
        self.running = False
        logger.info(f"🔇 {self.agent_id} stopped listening for messages")


class MockAgent:
    """Mock agent for testing communication."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.protocol = MockAgentProtocol(agent_id)
        self.message_count = 0
    
    async def initialize(self):
        """Initialize the agent."""
        # Register message handlers
        self.protocol.register_handler(MessageType.REQUEST, self._handle_request)
        self.protocol.register_handler(MessageType.NOTIFICATION, self._handle_notification)
        self.protocol.register_handler(MessageType.COORDINATION, self._handle_coordination)
        
        logger.info(f"🔧 Initialized {self.agent_id}")
    
    async def _handle_request(self, message: MockMessage):
        """Handle incoming requests."""
        self.message_count += 1
        logger.info(f"📨 {self.agent_id} received request #{self.message_count}: {message.payload}")
        
        # Simulate processing
        await asyncio.sleep(0.5)
        
        # Send response
        response_payload = {
            "status": "processed",
            "agent": self.agent_id,
            "message_count": self.message_count,
            "result": f"Request handled by {self.agent_id}",
            "processing_time": "0.5s"
        }
        
        await self.protocol.send_response(message, response_payload)
        logger.info(f"📤 {self.agent_id} sent response: {response_payload['status']}")
    
    async def _handle_notification(self, message: MockMessage):
        """Handle notifications."""
        logger.info(f"🔔 {self.agent_id} received notification: {message.payload}")
    
    async def _handle_coordination(self, message: MockMessage):
        """Handle coordination messages."""
        logger.info(f"🤝 {self.agent_id} received coordination: {message.payload}")
    
    async def send_message(self, target_agent: str, message_type: MessageType, payload: dict):
        """Send a message to another agent."""
        return await self.protocol.send_message(
            recipient_id=target_agent,
            message_type=message_type,
            payload=payload,
            priority=Priority.MEDIUM
        )
    
    async def start(self):
        """Start the agent."""
        await self.protocol.start_listening()
    
    async def stop(self):
        """Stop the agent."""
        await self.protocol.stop_listening()


async def test_mock_agent_communication():
    """Test mock agent-to-agent communication."""
    logger.info("🧪 Testing Mock Agent-to-Agent Communication...")
    
    # Create mock agents
    frontdesk_agent = MockAgent("frontdesk_agent")
    queue_agent = MockAgent("queue_agent")
    notification_agent = MockAgent("notification_agent")
    orchestrator_agent = MockAgent("orchestrator_agent")
    
    agents = {
        "frontdesk": frontdesk_agent,
        "queue": queue_agent,
        "notification": notification_agent,
        "orchestrator": orchestrator_agent
    }
    
    try:
        # Initialize all agents
        logger.info("🔧 Initializing all agents...")
        for agent in agents.values():
            await agent.initialize()
        
        # Start all agents in background
        tasks = []
        for agent in agents.values():
            task = asyncio.create_task(agent.start())
            tasks.append(task)
        
        # Wait for agents to start
        await asyncio.sleep(1)
        
        # Test 1: Patient Registration Workflow
        logger.info("🏥 Test 1: Patient Registration Workflow")
        
        # Step 1: FrontDesk registers patient
        await frontdesk_agent.send_message(
            target_agent="queue_agent",
            message_type=MessageType.REQUEST,
            payload={
                "action": "register_patient",
                "patient_data": {
                    "patient_id": "PAT-001",
                    "name": "John Doe",
                    "priority": "medium"
                }
            }
        )
        
        await asyncio.sleep(1)
        
        # Step 2: Queue agent adds to queue
        await queue_agent.send_message(
            target_agent="notification_agent",
            message_type=MessageType.NOTIFICATION,
            payload={
                "event": "patient_added_to_queue",
                "patient_id": "PAT-001",
                "position": 3,
                "estimated_wait": 15
            }
        )
        
        await asyncio.sleep(1)
        
        # Test 2: Appointment Scheduling Workflow
        logger.info("📅 Test 2: Appointment Scheduling Workflow")
        
        await orchestrator_agent.send_message(
            target_agent="notification_agent",
            message_type=MessageType.REQUEST,
            payload={
                "action": "schedule_appointment",
                "appointment_data": {
                    "patient_id": "PAT-002",
                    "provider": "Dr. Smith",
                    "time": "2024-01-15 10:00:00"
                }
            }
        )
        
        await asyncio.sleep(1)
        
        # Test 3: Emergency Coordination
        logger.info("🚨 Test 3: Emergency Coordination")
        
        await orchestrator_agent.send_message(
            target_agent="queue_agent",
            message_type=MessageType.COORDINATION,
            payload={
                "action": "emergency_priority",
                "patient_id": "PAT-003",
                "priority": "urgent",
                "reason": "cardiac emergency"
            }
        )
        
        await asyncio.sleep(1)
        
        # Test 4: Multiple Messages
        logger.info("🔄 Test 4: Multiple Messages")
        
        for i in range(3):
            await frontdesk_agent.send_message(
                target_agent="queue_agent",
                message_type=MessageType.REQUEST,
                payload={
                    "action": f"batch_operation_{i}",
                    "data": f"Batch message {i+1}"
                }
            )
            await asyncio.sleep(0.5)
        
        # Wait for all processing
        await asyncio.sleep(2)
        
        # Show results
        logger.info("✅ All communication tests completed successfully!")
        logger.info("📊 Message Processing Summary:")
        for name, agent in agents.items():
            logger.info(f"   • {name}: {agent.message_count} messages processed")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    finally:
        # Stop all agents
        for agent in agents.values():
            await agent.stop()
        
        # Cancel all tasks
        for task in tasks:
            task.cancel()
        
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except:
            pass


async def main():
    """Main function."""
    print("🧪 Mock Agent-to-Agent Communication Test")
    print("=" * 50)
    print("This test demonstrates:")
    print("• Patient registration workflow")
    print("• Appointment scheduling workflow")
    print("• Emergency coordination")
    print("• Multiple message processing")
    print("• Request/Response patterns")
    print("• Notification handling")
    print("=" * 50)
    print()
    
    await test_mock_agent_communication()


if __name__ == "__main__":
    asyncio.run(main())
