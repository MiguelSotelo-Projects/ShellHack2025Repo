"""
A2A Protocol Implementation

This module implements the Agent-to-Agent (A2A) protocol following Google's specifications.
"""

import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of A2A protocol messages."""
    DISCOVERY = "discovery"
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    HEARTBEAT = "heartbeat"
    NOTIFICATION = "notification"
    ERROR = "error"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_STEP = "workflow_step"
    WORKFLOW_COMPLETE = "workflow_complete"


class TaskStatus(str, Enum):
    """Status of task execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class AgentCard:
    """
    Agent Card following A2A protocol specification.
    
    Defines an agent's capabilities, metadata, and communication interface.
    """
    name: str
    description: str
    version: str = "1.0.0"
    url: Optional[str] = None
    authentication: Optional[Dict[str, Any]] = None
    capabilities: Optional[Dict[str, Any]] = None
    default_input_modes: Optional[List[str]] = None
    default_output_modes: Optional[List[str]] = None
    skills: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Set default values after initialization."""
        if self.capabilities is None:
            self.capabilities = {
                "streaming": True,
                "functions": True
            }
        
        if self.default_input_modes is None:
            self.default_input_modes = ["text/plain"]
        
        if self.default_output_modes is None:
            self.default_output_modes = ["text/plain", "application/json"]
        
        if self.skills is None:
            self.skills = []
        
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentCard':
        """Create from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentCard':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class TaskRequest(BaseModel):
    """A2A Task Request message."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    from_agent: str
    to_agent: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    timeout: Optional[float] = None
    priority: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskResponse(BaseModel):
    """A2A Task Response message."""
    task_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HeartbeatMessage(BaseModel):
    """A2A Heartbeat message."""
    agent_id: str
    status: str = "active"
    capabilities: List[str] = Field(default_factory=list)
    current_tasks: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DiscoveryMessage(BaseModel):
    """A2A Discovery message."""
    agent_id: str
    agent_card: AgentCard
    query: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class A2AMessage(BaseModel):
    """Generic A2A message wrapper."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType
    payload: Dict[str, Any] = Field(default_factory=dict)
    from_agent: str
    to_agent: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class A2AProtocol:
    """
    A2A Protocol implementation for agent communication.
    
    Handles message serialization, validation, and protocol compliance.
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize A2A protocol.
        
        Args:
            agent_id: Unique identifier for this agent
        """
        self.agent_id = agent_id
        self.message_handlers: Dict[MessageType, callable] = {}
        self.message_history: List[A2AMessage] = []
    
    def register_handler(self, message_type: MessageType, handler: callable) -> None:
        """
        Register a message handler.
        
        Args:
            message_type: Type of message to handle
            handler: Function to handle the message
        """
        self.message_handlers[message_type] = handler
    
    def create_task_request(
        self,
        task_type: str,
        parameters: Dict[str, Any],
        to_agent: str,
        **kwargs
    ) -> TaskRequest:
        """Create a task request message."""
        return TaskRequest(
            task_type=task_type,
            parameters=parameters,
            from_agent=self.agent_id,
            to_agent=to_agent,
            **kwargs
        )
    
    def create_task_response(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        **kwargs
    ) -> TaskResponse:
        """Create a task response message."""
        return TaskResponse(
            task_id=task_id,
            status=status,
            result=result,
            error=error,
            **kwargs
        )
    
    def create_heartbeat(self, **kwargs) -> HeartbeatMessage:
        """Create a heartbeat message."""
        return HeartbeatMessage(
            agent_id=self.agent_id,
            **kwargs
        )
    
    def create_discovery_message(
        self,
        agent_card: AgentCard,
        query: Optional[str] = None,
        **kwargs
    ) -> DiscoveryMessage:
        """Create a discovery message."""
        return DiscoveryMessage(
            agent_id=self.agent_id,
            agent_card=agent_card,
            query=query,
            **kwargs
        )
    
    def serialize_message(self, message: Union[TaskRequest, TaskResponse, HeartbeatMessage, DiscoveryMessage]) -> str:
        """Serialize a message to JSON string."""
        if isinstance(message, TaskRequest):
            return message.json()
        elif isinstance(message, TaskResponse):
            return message.json()
        elif isinstance(message, HeartbeatMessage):
            return message.json()
        elif isinstance(message, DiscoveryMessage):
            return message.json()
        else:
            raise ValueError(f"Unsupported message type: {type(message)}")
    
    def deserialize_message(self, message_type: MessageType, json_str: str) -> Union[TaskRequest, TaskResponse, HeartbeatMessage, DiscoveryMessage]:
        """Deserialize a JSON string to a message object."""
        if message_type == MessageType.TASK_REQUEST:
            return TaskRequest.parse_raw(json_str)
        elif message_type == MessageType.TASK_RESPONSE:
            return TaskResponse.parse_raw(json_str)
        elif message_type == MessageType.HEARTBEAT:
            return HeartbeatMessage.parse_raw(json_str)
        elif message_type == MessageType.DISCOVERY:
            return DiscoveryMessage.parse_raw(json_str)
        else:
            raise ValueError(f"Unsupported message type: {message_type}")
    
    def validate_message(self, message: A2AMessage) -> bool:
        """Validate an A2A message."""
        # Basic validation
        if not message.message_id:
            return False
        
        if not message.from_agent or not message.to_agent:
            return False
        
        if message.message_type not in MessageType:
            return False
        
        return True
    
    def log_message(self, message: A2AMessage) -> None:
        """Log a message for debugging and monitoring."""
        self.message_history.append(message)
        
        # Keep only last 1000 messages
        if len(self.message_history) > 1000:
            self.message_history = self.message_history[-1000:]
    
    def get_message_history(self, limit: int = 100) -> List[A2AMessage]:
        """Get recent message history."""
        return self.message_history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get protocol statistics."""
        message_counts = {}
        for message in self.message_history:
            msg_type = message.message_type
            message_counts[msg_type] = message_counts.get(msg_type, 0) + 1
        
        return {
            "agent_id": self.agent_id,
            "total_messages": len(self.message_history),
            "message_counts": message_counts,
            "handlers_registered": len(self.message_handlers)
        }
