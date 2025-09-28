"""
Agent-to-Agent Communication Protocol

This module implements the core protocol for agent-to-agent communication
using Google Cloud Pub/Sub for message passing and coordination.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.message import Message
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
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
class ProtocolMessage:
    """Standard message format for agent-to-agent communication."""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: MessageType
    priority: Priority
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['message_type'] = self.message_type.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProtocolMessage':
        """Create message from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['message_type'] = MessageType(data['message_type'])
        data['priority'] = Priority(data['priority'])
        return cls(**data)


class AgentProtocol:
    """Core protocol for agent-to-agent communication."""
    
    def __init__(self, agent_id: str, project_id: str = None, region: str = "us-central1"):
        self.agent_id = agent_id
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.region = region
        self.publisher = None
        self.subscriber = None
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.running = False
        
        if not self.project_id:
            raise ValueError("Google Cloud Project ID must be provided or set in GOOGLE_CLOUD_PROJECT env var")
    
    async def initialize(self):
        """Initialize the Pub/Sub client and create topics/subscriptions."""
        try:
            self.publisher = pubsub_v1.PublisherClient()
            self.subscriber = pubsub_v1.SubscriberClient()
            
            # Create topic for this agent
            topic_path = self.publisher.topic_path(self.project_id, f"ops-mesh-{self.agent_id}")
            subscription_path = self.subscriber.subscription_path(
                self.project_id, f"ops-mesh-{self.agent_id}-sub"
            )
            
            # Create topic if it doesn't exist
            try:
                self.publisher.get_topic(request={"topic": topic_path})
            except Exception:
                self.publisher.create_topic(request={"name": topic_path})
                logger.info(f"Created topic: {topic_path}")
            
            # Create subscription if it doesn't exist
            try:
                self.subscriber.get_subscription(request={"subscription": subscription_path})
            except Exception:
                self.subscriber.create_subscription(
                    request={
                        "name": subscription_path,
                        "topic": topic_path
                    }
                )
                logger.info(f"Created subscription: {subscription_path}")
            
            self.topic_path = topic_path
            self.subscription_path = subscription_path
            
        except Exception as e:
            logger.error(f"Failed to initialize agent protocol: {e}")
            raise
    
    async def send_message(self, recipient_id: str, message_type: MessageType, 
                          payload: Dict[str, Any], priority: Priority = Priority.MEDIUM,
                          correlation_id: Optional[str] = None) -> str:
        """Send a message to another agent."""
        if not self.publisher:
            raise RuntimeError("Protocol not initialized. Call initialize() first.")
        
        message = ProtocolMessage(
            message_id=f"{self.agent_id}-{datetime.now().timestamp()}",
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            priority=priority,
            payload=payload,
            timestamp=datetime.now(),
            correlation_id=correlation_id
        )
        
        # Publish to recipient's topic
        recipient_topic = self.publisher.topic_path(self.project_id, f"ops-mesh-{recipient_id}")
        
        try:
            # Ensure topic exists
            self.publisher.get_topic(request={"topic": recipient_topic})
        except Exception:
            self.publisher.create_topic(request={"name": recipient_topic})
        
        # Publish message
        message_data = json.dumps(message.to_dict()).encode('utf-8')
        future = self.publisher.publish(recipient_topic, message_data)
        message_id = future.result()
        
        logger.info(f"Sent {message_type.value} message to {recipient_id}: {message_id}")
        return message_id
    
    async def send_response(self, original_message: ProtocolMessage, 
                           response_payload: Dict[str, Any]) -> str:
        """Send a response to a received message."""
        return await self.send_message(
            recipient_id=original_message.sender_id,
            message_type=MessageType.RESPONSE,
            payload=response_payload,
            correlation_id=original_message.message_id
        )
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a message handler for a specific message type."""
        self.message_handlers[message_type] = handler
    
    async def _handle_message(self, message: Message):
        """Handle incoming messages."""
        try:
            # Parse message
            message_data = json.loads(message.data.decode('utf-8'))
            protocol_message = ProtocolMessage.from_dict(message_data)
            
            logger.info(f"Received {protocol_message.message_type.value} from {protocol_message.sender_id}")
            
            # Find appropriate handler
            handler = self.message_handlers.get(protocol_message.message_type)
            if handler:
                await handler(protocol_message)
            else:
                logger.warning(f"No handler registered for message type: {protocol_message.message_type}")
            
            # Acknowledge message
            message.ack()
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            message.nack()
    
    async def start_listening(self):
        """Start listening for incoming messages."""
        if not self.subscriber:
            raise RuntimeError("Protocol not initialized. Call initialize() first.")
        
        self.running = True
        logger.info(f"Agent {self.agent_id} started listening for messages")
        
        # Start streaming pull
        streaming_pull_future = self.subscriber.pull(
            request={
                "subscription": self.subscription_path,
                "max_messages": 10,
            }
        )
        
        try:
            # Keep the main thread alive
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping message listener...")
            streaming_pull_future.cancel()
            self.running = False
    
    async def stop_listening(self):
        """Stop listening for messages."""
        self.running = False
        logger.info(f"Agent {self.agent_id} stopped listening for messages")


class FlowOrchestrator:
    """Orchestrates complex workflows between multiple agents."""
    
    def __init__(self, protocol: AgentProtocol):
        self.protocol = protocol
        self.active_flows: Dict[str, Dict[str, Any]] = {}
    
    async def start_flow(self, flow_id: str, flow_definition: Dict[str, Any]) -> str:
        """Start a new workflow flow."""
        self.active_flows[flow_id] = {
            "definition": flow_definition,
            "status": "active",
            "current_step": 0,
            "started_at": datetime.now(),
            "participants": set()
        }
        
        logger.info(f"Started flow {flow_id}")
        return flow_id
    
    async def coordinate_step(self, flow_id: str, step_data: Dict[str, Any]) -> bool:
        """Coordinate a step in the workflow."""
        if flow_id not in self.active_flows:
            logger.error(f"Flow {flow_id} not found")
            return False
        
        flow = self.active_flows[flow_id]
        flow["current_step"] += 1
        
        # Send coordination message to relevant agents
        await self.protocol.send_message(
            recipient_id=step_data.get("target_agent"),
            message_type=MessageType.COORDINATION,
            payload={
                "flow_id": flow_id,
                "step": flow["current_step"],
                "data": step_data
            },
            priority=Priority.HIGH
        )
        
        return True
    
    async def complete_flow(self, flow_id: str, result: Dict[str, Any]):
        """Complete a workflow flow."""
        if flow_id in self.active_flows:
            flow = self.active_flows[flow_id]
            flow["status"] = "completed"
            flow["result"] = result
            flow["completed_at"] = datetime.now()
            
            logger.info(f"Completed flow {flow_id}")
    
    def get_flow_status(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow flow."""
        return self.active_flows.get(flow_id)
