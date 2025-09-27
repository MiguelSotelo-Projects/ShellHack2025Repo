"""
Agent-to-Agent Protocol Implementation using Google ADK

This module implements a standardized agent communication protocol
using Google Cloud Platform services and protobuf for message serialization.
"""

import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional, Callable, Union
import base64

# Google Cloud imports
from google.cloud import pubsub_v1
from google.cloud import aiplatform
from google.cloud import storage
from google.cloud import logging as cloud_logging
from google.cloud import monitoring_v3
from google.auth import default
from google.protobuf import message
from google.protobuf import timestamp_pb2

# Protocol imports
import grpc
from concurrent import futures


class MessageType(str, Enum):
    """Standard message types for agent communication."""
    # System messages
    HEARTBEAT = "heartbeat"
    REGISTRATION = "registration"
    DEREGISTRATION = "deregistration"
    STATUS_UPDATE = "status_update"
    
    # Patient flow messages
    PATIENT_CHECKIN = "patient_checkin"
    APPOINTMENT_LOOKUP = "appointment_lookup"
    WALKIN_REGISTRATION = "walkin_registration"
    INSURANCE_VERIFICATION = "insurance_verification"
    BED_RESERVATION = "bed_reservation"
    QUEUE_MANAGEMENT = "queue_management"
    PATIENT_CALLING = "patient_calling"
    STAFF_COORDINATION = "staff_coordination"
    
    # Response messages
    ACKNOWLEDGMENT = "acknowledgment"
    RESPONSE = "response"
    ERROR = "error"
    
    # Control messages
    FLOW_START = "flow_start"
    FLOW_STEP = "flow_step"
    FLOW_COMPLETE = "flow_complete"
    FLOW_FAILURE = "flow_failure"


class MessagePriority(int, Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    OFFLINE = "offline"
    STARTING = "starting"
    ONLINE = "online"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class FlowStatus(str, Enum):
    """Flow status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentCapability:
    """Agent capability definition."""
    name: str
    version: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ProtocolMessage:
    """Standard protocol message structure."""
    message_id: str
    correlation_id: Optional[str]
    sender_id: str
    recipient_id: str
    message_type: MessageType
    priority: MessagePriority
    payload: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProtocolMessage':
        """Create message from dictionary."""
        # Convert timestamp
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        
        # Convert enum types
        if isinstance(data.get('message_type'), str):
            data['message_type'] = MessageType(data['message_type'])
        if isinstance(data.get('priority'), str):
            data['priority'] = MessagePriority(data['priority'])
        
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def can_retry(self) -> bool:
        """Check if message can be retried."""
        return self.retry_count < self.max_retries and not self.is_expired()


@dataclass
class FlowDefinition:
    """Patient flow definition."""
    flow_id: str
    flow_name: str
    version: str
    description: str
    steps: List[Dict[str, Any]]
    timeout_minutes: int
    retry_policy: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def get_step(self, step_index: int) -> Optional[Dict[str, Any]]:
        """Get flow step by index."""
        if 0 <= step_index < len(self.steps):
            return self.steps[step_index]
        return None


@dataclass
class FlowInstance:
    """Active flow instance."""
    instance_id: str
    flow_definition: FlowDefinition
    patient_data: Dict[str, Any]
    session_data: Dict[str, Any]
    current_step: int
    status: FlowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    step_results: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.step_results is None:
            self.step_results = []


class AgentProtocol(ABC):
    """Base class for agent protocol implementation."""
    
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        project_id: str,
        region: str = "us-central1"
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.project_id = project_id
        self.region = region
        self.status = AgentStatus.OFFLINE
        self.capabilities: List[AgentCapability] = []
        self.active_flows: Dict[str, FlowInstance] = {}
        
        # Google Cloud clients
        self.publisher = None
        self.subscriber = None
        self.aiplatform_client = None
        self.storage_client = None
        self.logging_client = None
        self.monitoring_client = None
        
        # Protocol settings
        self.subscription_name = f"agent-{agent_id}-subscription"
        self.topic_name = f"agent-{agent_id}-topic"
        self.broadcast_topic = "agent-broadcast"
        
        # Message handling
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.running = False
        
        # Logging
        self.logger = logging.getLogger(f"agent.{agent_id}")
        
        # Initialize Google Cloud services
        self._initialize_google_services()
    
    def _initialize_google_services(self):
        """Initialize Google Cloud services."""
        try:
            # Initialize Pub/Sub
            self.publisher = pubsub_v1.PublisherClient()
            self.subscriber = pubsub_v1.SubscriberClient()
            
            # Initialize AI Platform
            aiplatform.init(project=self.project_id, location=self.region)
            self.aiplatform_client = aiplatform
            
            # Initialize other services
            self.storage_client = storage.Client(project=self.project_id)
            self.logging_client = cloud_logging.Client(project=self.project_id)
            self.monitoring_client = monitoring_v3.MetricServiceClient()
            
            self.logger.info("Google Cloud services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Cloud services: {e}")
            raise
    
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Return agent capabilities. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def process_message(self, message: ProtocolMessage) -> Dict[str, Any]:
        """Process incoming message. Must be implemented by subclasses."""
        pass
    
    async def start(self):
        """Start the agent."""
        try:
            self.status = AgentStatus.STARTING
            self.logger.info(f"Starting agent {self.agent_name}")
            
            # Create topics and subscriptions
            await self._setup_pubsub()
            
            # Register agent
            await self._register_agent()
            
            # Start message processing
            self.running = True
            asyncio.create_task(self._message_processing_loop())
            asyncio.create_task(self._heartbeat_loop())
            
            self.status = AgentStatus.ONLINE
            self.logger.info(f"Agent {self.agent_name} started successfully")
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"Failed to start agent: {e}")
            raise
    
    async def stop(self):
        """Stop the agent."""
        try:
            self.running = False
            self.status = AgentStatus.OFFLINE
            
            # Deregister agent
            await self._deregister_agent()
            
            self.logger.info(f"Agent {self.agent_name} stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping agent: {e}")
    
    async def _setup_pubsub(self):
        """Set up Pub/Sub topics and subscriptions."""
        try:
            # Create topic
            topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
            try:
                self.publisher.create_topic(request={"name": topic_path})
                self.logger.info(f"Created topic: {self.topic_name}")
            except Exception:
                # Topic might already exist
                pass
            
            # Create subscription
            subscription_path = self.subscriber.subscription_path(
                self.project_id, self.subscription_name
            )
            try:
                self.subscriber.create_subscription(
                    request={
                        "name": subscription_path,
                        "topic": topic_path,
                        "ack_deadline_seconds": 60
                    }
                )
                self.logger.info(f"Created subscription: {self.subscription_name}")
            except Exception:
                # Subscription might already exist
                pass
            
        except Exception as e:
            self.logger.error(f"Failed to setup Pub/Sub: {e}")
            raise
    
    async def _register_agent(self):
        """Register agent with the system."""
        try:
            registration_message = ProtocolMessage(
                message_id=str(uuid.uuid4()),
                correlation_id=None,
                sender_id=self.agent_id,
                recipient_id="orchestrator",
                message_type=MessageType.REGISTRATION,
                priority=MessagePriority.HIGH,
                payload={
                    "agent_id": self.agent_id,
                    "agent_name": self.agent_name,
                    "capabilities": [cap.__dict__ for cap in self.capabilities],
                    "status": self.status.value,
                    "project_id": self.project_id,
                    "region": self.region
                },
                metadata={},
                timestamp=datetime.utcnow()
            )
            
            await self._send_message(registration_message)
            self.logger.info("Agent registration sent")
            
        except Exception as e:
            self.logger.error(f"Failed to register agent: {e}")
            raise
    
    async def _deregister_agent(self):
        """Deregister agent from the system."""
        try:
            deregistration_message = ProtocolMessage(
                message_id=str(uuid.uuid4()),
                correlation_id=None,
                sender_id=self.agent_id,
                recipient_id="orchestrator",
                message_type=MessageType.DEREGISTRATION,
                priority=MessagePriority.HIGH,
                payload={
                    "agent_id": self.agent_id,
                    "agent_name": self.agent_name,
                    "status": self.status.value
                },
                metadata={},
                timestamp=datetime.utcnow()
            )
            
            await self._send_message(deregistration_message)
            self.logger.info("Agent deregistration sent")
            
        except Exception as e:
            self.logger.error(f"Failed to deregister agent: {e}")
    
    async def _send_message(self, message: ProtocolMessage):
        """Send message via Pub/Sub."""
        try:
            topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
            
            # Serialize message
            message_data = json.dumps(message.to_dict()).encode('utf-8')
            
            # Publish message
            future = self.publisher.publish(
                topic_path,
                message_data,
                agent_id=message.recipient_id,
                message_type=message.message_type.value,
                priority=str(message.priority.value)
            )
            
            # Wait for publish to complete
            message_id = future.result()
            self.logger.debug(f"Message sent: {message_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            raise
    
    async def send_message(
        self,
        recipient_id: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[str] = None,
        expires_in_minutes: Optional[int] = None
    ) -> str:
        """Send a message to another agent."""
        try:
            message_id = str(uuid.uuid4())
            expires_at = None
            
            if expires_in_minutes:
                expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
            
            message = ProtocolMessage(
                message_id=message_id,
                correlation_id=correlation_id,
                sender_id=self.agent_id,
                recipient_id=recipient_id,
                message_type=message_type,
                priority=priority,
                payload=payload,
                metadata={},
                timestamp=datetime.utcnow(),
                expires_at=expires_at
            )
            
            await self._send_message(message)
            return message_id
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            raise
    
    async def send_broadcast(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        exclude_agents: Optional[List[str]] = None
    ) -> str:
        """Send broadcast message to all agents."""
        try:
            message_id = str(uuid.uuid4())
            
            message = ProtocolMessage(
                message_id=message_id,
                correlation_id=None,
                sender_id=self.agent_id,
                recipient_id="*",  # Broadcast
                message_type=message_type,
                priority=priority,
                payload=payload,
                metadata={"exclude_agents": exclude_agents or []},
                timestamp=datetime.utcnow()
            )
            
            # Send to broadcast topic
            topic_path = self.publisher.topic_path(self.project_id, self.broadcast_topic)
            message_data = json.dumps(message.to_dict()).encode('utf-8')
            
            future = self.publisher.publish(
                topic_path,
                message_data,
                agent_id="*",
                message_type=message.message_type.value,
                priority=str(message.priority.value)
            )
            
            future.result()
            return message_id
            
        except Exception as e:
            self.logger.error(f"Failed to send broadcast: {e}")
            raise
    
    async def _message_processing_loop(self):
        """Main message processing loop."""
        subscription_path = self.subscriber.subscription_path(
            self.project_id, self.subscription_name
        )
        
        try:
            # Use the newer streaming pull API
            while self.running:
                try:
                    # Pull messages with timeout
                    response = self.subscriber.pull(
                        request={"subscription": subscription_path, "max_messages": 10}
                    )
                    
                    if response.received_messages:
                        for received_message in response.received_messages:
                            try:
                                # Parse message
                                message_data = json.loads(received_message.message.data.decode('utf-8'))
                                protocol_message = ProtocolMessage.from_dict(message_data)
                                
                                # Process message
                                await self._handle_message(protocol_message)
                                
                                # Acknowledge message
                                self.subscriber.acknowledge(
                                    request={"subscription": subscription_path, "ack_ids": [received_message.ack_id]}
                                )
                                
                            except Exception as e:
                                self.logger.error(f"Error processing message: {e}")
                                # Acknowledge to remove from queue even if processing failed
                                self.subscriber.acknowledge(
                                    request={"subscription": subscription_path, "ack_ids": [received_message.ack_id]}
                                )
                    
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    self.logger.error(f"Error in message pull: {e}")
                    await asyncio.sleep(1)
                    
        except Exception as e:
            self.logger.error(f"Error in message processing loop: {e}")
    
    async def _handle_message(self, message: ProtocolMessage):
        """Handle incoming message."""
        try:
            # Check if message is expired
            if message.is_expired():
                self.logger.warning(f"Message {message.message_id} expired")
                return
            
            # Update agent status if busy
            if self.status == AgentStatus.ONLINE:
                self.status = AgentStatus.BUSY
            
            # Process message
            result = await self.process_message(message)
            
            # Send acknowledgment if needed
            if result.get("acknowledgment_required", False):
                await self.send_message(
                    recipient_id=message.sender_id,
                    message_type=MessageType.ACKNOWLEDGMENT,
                    payload={"original_message_id": message.message_id, "status": "processed"},
                    correlation_id=message.correlation_id
                )
            
            # Reset status
            if self.status == AgentStatus.BUSY:
                self.status = AgentStatus.ONLINE
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            
            # Send error response
            await self.send_message(
                recipient_id=message.sender_id,
                message_type=MessageType.ERROR,
                payload={
                    "original_message_id": message.message_id,
                    "error": str(e),
                    "status": "failed"
                },
                correlation_id=message.correlation_id
            )
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages."""
        while self.running:
            try:
                await self.send_message(
                    recipient_id="orchestrator",
                    message_type=MessageType.HEARTBEAT,
                    payload={
                        "agent_id": self.agent_id,
                        "status": self.status.value,
                        "active_flows": len(self.active_flows),
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    priority=MessagePriority.LOW
                )
                
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error sending heartbeat: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def start_flow(self, flow_definition: FlowDefinition, patient_data: Dict[str, Any], session_data: Dict[str, Any]) -> str:
        """Start a new patient flow."""
        try:
            instance_id = str(uuid.uuid4())
            
            flow_instance = FlowInstance(
                instance_id=instance_id,
                flow_definition=flow_definition,
                patient_data=patient_data,
                session_data=session_data,
                current_step=0,
                status=FlowStatus.ACTIVE,
                started_at=datetime.utcnow()
            )
            
            self.active_flows[instance_id] = flow_instance
            
            # Send flow start message
            await self.send_message(
                recipient_id="orchestrator",
                message_type=MessageType.FLOW_START,
                payload={
                    "flow_instance_id": instance_id,
                    "flow_definition": flow_definition.__dict__,
                    "patient_data": patient_data,
                    "session_data": session_data
                },
                priority=MessagePriority.HIGH
            )
            
            self.logger.info(f"Started flow {flow_definition.flow_name} with instance {instance_id}")
            return instance_id
            
        except Exception as e:
            self.logger.error(f"Failed to start flow: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "capabilities": [cap.__dict__ for cap in self.capabilities],
            "active_flows": len(self.active_flows),
            "project_id": self.project_id,
            "region": self.region,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def log_activity(self, activity: str, details: Dict[str, Any] = None):
        """Log agent activity to Google Cloud Logging."""
        try:
            log_entry = {
                "agent_id": self.agent_id,
                "activity": activity,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if details:
                log_entry.update(details)
            
            # Send to Google Cloud Logging
            logger = self.logging_client.logger(f"agent-{self.agent_id}")
            logger.log_struct(log_entry)
            
            # Also log locally
            self.logger.info(f"Activity: {activity}", extra=log_entry)
            
        except Exception as e:
            self.logger.error(f"Error logging activity: {e}")
