#!/usr/bin/env python3
"""
Start Real Agent-to-Agent Communication System

This script starts the real agent-to-agent communication system using Google Cloud Pub/Sub
without Google ADK dependencies.
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


class RealAgent:
    """Real agent that uses Google Cloud Pub/Sub for communication."""
    
    def __init__(self, agent_id: str, project_id: str):
        self.agent_id = agent_id
        self.project_id = project_id
        self.protocol = AgentProtocol(agent_id, project_id)
        self.message_count = 0
        self.running = False
    
    async def initialize(self):
        """Initialize the agent protocol."""
        await self.protocol.initialize()
        
        # Register message handlers
        self.protocol.register_handler(MessageType.REQUEST, self._handle_request)
        self.protocol.register_handler(MessageType.NOTIFICATION, self._handle_notification)
        self.protocol.register_handler(MessageType.COORDINATION, self._handle_coordination)
        
        logger.info(f"🔧 Initialized {self.agent_id}")
    
    async def _handle_request(self, message: ProtocolMessage):
        """Handle incoming requests."""
        self.message_count += 1
        logger.info(f"📨 {self.agent_id} received request #{self.message_count}: {message.payload}")
        
        # Simulate processing based on agent type
        if "frontdesk" in self.agent_id:
            result = await self._handle_frontdesk_request(message)
        elif "queue" in self.agent_id:
            result = await self._handle_queue_request(message)
        elif "notification" in self.agent_id:
            result = await self._handle_notification_request(message)
        elif "appointment" in self.agent_id:
            result = await self._handle_appointment_request(message)
        else:
            result = {"status": "processed", "agent": self.agent_id}
        
        # Send response
        await self.protocol.send_response(message, result)
        logger.info(f"📤 {self.agent_id} sent response: {result['status']}")
    
    async def _handle_frontdesk_request(self, message: ProtocolMessage):
        """Handle frontdesk-specific requests."""
        action = message.payload.get("action", "")
        
        if action == "register_patient":
            patient_data = message.payload.get("patient_data", {})
            patient_id = f"PAT-{asyncio.get_event_loop().time()}"
            
            # Notify queue agent
            await self.protocol.send_message(
                recipient_id="queue_agent",
                message_type=MessageType.NOTIFICATION,
                payload={
                    "event": "patient_registered",
                    "patient_id": patient_id,
                    "priority": patient_data.get("priority", "medium")
                },
                priority=Priority.MEDIUM
            )
            
            return {
                "status": "patient_registered",
                "patient_id": patient_id,
                "message": "Patient registered and added to queue"
            }
        
        return {"status": "processed", "action": action}
    
    async def _handle_queue_request(self, message: ProtocolMessage):
        """Handle queue-specific requests."""
        action = message.payload.get("action", "")
        
        if action == "add_to_queue":
            patient_id = message.payload.get("patient_id")
            priority = message.payload.get("priority", "medium")
            
            # Notify notification agent
            await self.protocol.send_message(
                recipient_id="notification_agent",
                message_type=MessageType.NOTIFICATION,
                payload={
                    "event": "queue_updated",
                    "patient_id": patient_id,
                    "position": 1,
                    "estimated_wait": 15
                },
                priority=Priority.MEDIUM
            )
            
            return {
                "status": "added_to_queue",
                "patient_id": patient_id,
                "position": 1,
                "estimated_wait": 15
            }
        
        return {"status": "processed", "action": action}
    
    async def _handle_notification_request(self, message: ProtocolMessage):
        """Handle notification-specific requests."""
        action = message.payload.get("action", "")
        
        if action == "send_notification":
            recipient = message.payload.get("recipient")
            message_text = message.payload.get("message")
            
            return {
                "status": "notification_sent",
                "recipient": recipient,
                "message": message_text
            }
        
        return {"status": "processed", "action": action}
    
    async def _handle_appointment_request(self, message: ProtocolMessage):
        """Handle appointment-specific requests."""
        action = message.payload.get("action", "")
        
        if action == "schedule_appointment":
            appointment_data = message.payload.get("appointment_data", {})
            appointment_id = f"APT-{asyncio.get_event_loop().time()}"
            
            return {
                "status": "appointment_scheduled",
                "appointment_id": appointment_id,
                "data": appointment_data
            }
        
        return {"status": "processed", "action": action}
    
    async def _handle_notification(self, message: ProtocolMessage):
        """Handle notifications."""
        event = message.payload.get("event", "")
        logger.info(f"🔔 {self.agent_id} received notification: {event}")
        
        # Handle specific events
        if event == "patient_registered" and "queue" in self.agent_id:
            # Queue agent handles patient registration
            patient_id = message.payload.get("patient_id")
            priority = message.payload.get("priority", "medium")
            
            # Add to queue
            await self.protocol.send_message(
                recipient_id="notification_agent",
                message_type=MessageType.NOTIFICATION,
                payload={
                    "event": "queue_updated",
                    "patient_id": patient_id,
                    "position": 1,
                    "estimated_wait": 15
                },
                priority=Priority.MEDIUM
            )
        
        elif event == "queue_updated" and "notification" in self.agent_id:
            # Notification agent handles queue updates
            patient_id = message.payload.get("patient_id")
            position = message.payload.get("position")
            estimated_wait = message.payload.get("estimated_wait")
            
            logger.info(f"📢 Sending queue update to patient {patient_id}: Position {position}, Wait time {estimated_wait} minutes")
    
    async def _handle_coordination(self, message: ProtocolMessage):
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
        self.running = True
        logger.info(f"🚀 Starting {self.agent_id}...")
        await self.protocol.start_listening()
    
    async def stop(self):
        """Stop the agent."""
        self.running = False
        await self.protocol.stop_listening()
        logger.info(f"🛑 Stopped {self.agent_id}")


async def main():
    """Main function to run the real agent system."""
    logger.info("🚀 Starting Ops Mesh Real Agent-to-Agent Communication System...")
    
    # Get project ID from environment
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        logger.error("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
        return
    
    logger.info(f"📋 Using Google Cloud Project: {project_id}")
    
    # Create real agents
    agents = {
        "frontdesk": RealAgent("frontdesk_agent", project_id),
        "queue": RealAgent("queue_agent", project_id),
        "notification": RealAgent("notification_agent", project_id),
        "appointment": RealAgent("appointment_agent", project_id)
    }
    
    try:
        # Initialize all agents
        logger.info("🔧 Initializing all agents...")
        for agent in agents.values():
            await agent.initialize()
        
        logger.info("✅ All agents initialized successfully!")
        logger.info("🤖 Starting agent-to-agent communication...")
        
        # Start all agents concurrently
        tasks = []
        for agent in agents.values():
            task = asyncio.create_task(agent.start())
            tasks.append(task)
        
        # Wait for all agents to complete
        await asyncio.gather(*tasks)
        
    except KeyboardInterrupt:
        logger.info("⏹️  Received interrupt signal, stopping agents...")
        for agent in agents.values():
            await agent.stop()
    except Exception as e:
        logger.error(f"❌ Error running agent system: {e}")
        for agent in agents.values():
            await agent.stop()
        raise


if __name__ == "__main__":
    print("🏥 Ops Mesh Real Agent-to-Agent Communication System")
    print("=" * 60)
    print("🤖 Starting specialized agents:")
    print("   • FrontDesk Agent - Patient registration & check-in")
    print("   • Queue Agent - Queue management & wait times")
    print("   • Appointment Agent - Appointment scheduling")
    print("   • Notification Agent - Alerts & notifications")
    print("=" * 60)
    print("🔗 Using Google Cloud Pub/Sub for real-time communication")
    print("=" * 60)
    print()
    
    asyncio.run(main())
