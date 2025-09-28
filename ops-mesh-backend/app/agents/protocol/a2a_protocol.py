"""
A2A Protocol Implementation for Ops Mesh

This module implements the official A2A (Agent-to-Agent) protocol
for agent communication using Google ADK.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path

# Try to import a2a-protocol, fallback to internal implementation
try:
    from a2a_protocol import A2AAgent as ExternalA2AAgent, A2ATask as ExternalA2ATask
    A2AAgent = ExternalA2AAgent
    A2ATask = ExternalA2ATask
    print("✅ Using external a2a-protocol package")
except ImportError:
    print("ℹ️  Using internal A2A protocol implementation")
    
    # Internal A2A Protocol implementation
    class A2AAgent:
        """Internal A2A Agent implementation"""
        def __init__(self, agent_id: str, agent_card_path: str = None):
            self.agent_id = agent_id
            self.agent_card_path = agent_card_path
            self.capabilities = []
            self.running = False

    class A2ATask:
        """Internal A2A Task implementation"""
        def __init__(self, task_id: str, action: str, data: Dict[str, Any]):
            self.task_id = task_id
            self.action = action
            self.data = data
            self.status = "pending"
            self.result = None

    class A2AMessage:
        """Internal A2A Message implementation"""
        def __init__(self, sender: str, recipient: str, message_type: str, payload: Dict[str, Any]):
            self.sender = sender
            self.recipient = recipient
            self.message_type = message_type
            self.payload = payload
            self.timestamp = datetime.now()

    class A2AStatus:
        """Internal A2A Status implementation"""
        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        FAILED = "failed"

    class AgentDiscovery:
        """Internal Agent Discovery implementation"""
        def __init__(self):
            self.agents = {}
        
        async def discover_agents(self) -> List[Dict[str, Any]]:
            return list(self.agents.values())
        
        async def register_agent(self, agent_id: str, agent_info: Dict[str, Any]):
            self.agents[agent_id] = agent_info

    class A2ASecurity:
        """Internal A2A Security implementation"""
        def __init__(self):
            self.authenticated_agents = set()
        
        async def authenticate_agent(self, agent_id: str, credentials: str) -> bool:
            # Simple authentication for development
            self.authenticated_agents.add(agent_id)
            return True

logger = logging.getLogger(__name__)

# Global task router for simulation
_task_router = {}


class MessageType(str, Enum):
    """A2A Message Types"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    CAPABILITY_DISCOVERY = "capability_discovery"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class TaskStatus(str, Enum):
    """A2A Task Status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class A2ATaskRequest:
    """A2A Task Request"""
    task_id: str
    sender_id: str
    recipient_id: str
    action: str
    data: Dict[str, Any]
    priority: str = "medium"
    timeout: int = 300  # seconds
    created_at: datetime = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2ATaskRequest':
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class A2ATaskResponse:
    """A2A Task Response"""
    task_id: str
    sender_id: str
    recipient_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['completed_at'] = self.completed_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2ATaskResponse':
        data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)


class A2AProtocol:
    """A2A Protocol Implementation"""
    
    def __init__(self, agent_id: str, agent_card_path: str = None):
        self.agent_id = agent_id
        self.agent_card_path = agent_card_path
        self.agent_card = self._load_agent_card()
        self.discovery = AgentDiscovery()
        self.security = A2ASecurity()
        self.running = False
        self.task_handlers: Dict[str, Callable] = {}
        self.active_tasks: Dict[str, A2ATaskRequest] = {}
        
        # Register this agent
        asyncio.create_task(self._register_agent())
        
        # Register with global task router
        _task_router[self.agent_id] = self
    
    def _load_agent_card(self) -> Dict[str, Any]:
        """Load agent card from JSON file"""
        if self.agent_card_path and Path(self.agent_card_path).exists():
            with open(self.agent_card_path, 'r') as f:
                return json.load(f)
        return {}
    
    async def _register_agent(self):
        """Register this agent with the discovery service"""
        agent_info = {
            "agent_id": self.agent_id,
            "capabilities": self.agent_card.get("capabilities", []),
            "endpoints": self.agent_card.get("endpoints", {}),
            "dependencies": self.agent_card.get("dependencies", []),
            "status": "available"
        }
        await self.discovery.register_agent(self.agent_id, agent_info)
        logger.info(f"Registered agent {self.agent_id} with discovery service")
    
    async def start(self):
        """Start the A2A protocol"""
        self.running = True
        logger.info(f"A2A Protocol started for agent {self.agent_id}")
        
        # Start heartbeat
        asyncio.create_task(self._heartbeat())
        
        # Start task processing
        asyncio.create_task(self._process_tasks())
    
    async def stop(self):
        """Stop the A2A protocol"""
        self.running = False
        
        # Unregister from global task router
        if self.agent_id in _task_router:
            del _task_router[self.agent_id]
        
        logger.info(f"A2A Protocol stopped for agent {self.agent_id}")
    
    async def _heartbeat(self):
        """Send periodic heartbeat"""
        while self.running:
            try:
                # Send heartbeat to discovery service
                await self.discovery.register_agent(self.agent_id, {
                    "agent_id": self.agent_id,
                    "status": "alive",
                    "last_heartbeat": datetime.now().isoformat()
                })
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(5)
    
    async def _process_tasks(self):
        """Process incoming tasks"""
        while self.running:
            try:
                # Process any pending tasks
                for task_id, task in list(self.active_tasks.items()):
                    if task.status == TaskStatus.PENDING:
                        await self._execute_task(task)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Task processing error: {e}")
                await asyncio.sleep(1)
    
    async def _execute_task(self, task: A2ATaskRequest):
        """Execute a task"""
        try:
            task.status = TaskStatus.IN_PROGRESS
            logger.info(f"Executing task {task.task_id}: {task.action}")
            
            # Find handler for this action
            handler = self.task_handlers.get(task.action)
            if handler:
                result = await handler(task.data)
                task.status = TaskStatus.COMPLETED
                task.result = result
                logger.info(f"Task {task.task_id} completed successfully")
            else:
                task.status = TaskStatus.FAILED
                task.error = f"No handler for action: {task.action}"
                logger.error(f"Task {task.task_id} failed: No handler for action {task.action}")
            
            # Send response
            await self._send_task_response(task)
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            logger.error(f"Task execution error: {e}")
            await self._send_task_response(task)
    
    async def _send_task_response(self, task: A2ATaskRequest):
        """Send task response back to sender"""
        response = A2ATaskResponse(
            task_id=task.task_id,
            sender_id=self.agent_id,
            recipient_id=task.sender_id,
            status=task.status,
            result=task.result,
            error=task.error
        )
        
        # In a real implementation, this would send via A2A protocol
        logger.info(f"Task {task.task_id} completed with status: {task.status}")
        
        # Remove from active tasks
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]
    
    def register_task_handler(self, action: str, handler: Callable):
        """Register a task handler"""
        self.task_handlers[action] = handler
        logger.info(f"Registered task handler for action: {action}")
    
    async def send_task_request(self, recipient_id: str, action: str, 
                               data: Dict[str, Any], priority: str = "medium") -> str:
        """Send a task request to another agent"""
        task_id = f"{self.agent_id}-{datetime.now().timestamp()}"
        
        task = A2ATaskRequest(
            task_id=task_id,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            action=action,
            data=data,
            priority=priority
        )
        
        # Store the task for tracking
        self.active_tasks[task_id] = task
        
        # In a real implementation, this would send via A2A protocol
        # For now, we'll simulate by directly calling the recipient's handler
        await self._simulate_task_delivery(task)
        
        logger.info(f"Sent task request {task_id} to {recipient_id}: {action}")
        
        return task_id
    
    async def _simulate_task_delivery(self, task: A2ATaskRequest):
        """Simulate task delivery to recipient agent"""
        try:
            # In a real implementation, this would be handled by the discovery service
            # and actual message passing. For now, we'll simulate it.
            logger.info(f"Simulating delivery of task {task.task_id} to {task.recipient_id}")
            
            # Find the recipient agent in the global router
            recipient_agent = _task_router.get(task.recipient_id)
            if recipient_agent:
                # Deliver the task to the recipient
                await recipient_agent.receive_task_request(task)
            else:
                logger.warning(f"Recipient agent {task.recipient_id} not found in task router")
            
        except Exception as e:
            logger.error(f"Error simulating task delivery: {e}")
    
    async def receive_task_request(self, task: A2ATaskRequest):
        """Receive a task request from another agent"""
        try:
            logger.info(f"Received task request {task.task_id} from {task.sender_id}: {task.action}")
            
            # Add to active tasks for processing
            self.active_tasks[task.task_id] = task
            
            # The task will be processed by the task processing loop
            
        except Exception as e:
            logger.error(f"Error receiving task request: {e}")
    
    async def discover_agents(self) -> List[Dict[str, Any]]:
        """Discover available agents"""
        return await self.discovery.discover_agents()
    
    async def get_agent_capabilities(self, agent_id: str) -> Dict[str, Any]:
        """Get capabilities of a specific agent"""
        agents = await self.discover_agents()
        for agent in agents:
            if agent.get("agent_id") == agent_id:
                return agent
        return {}
    
    async def authenticate(self, credentials: str) -> bool:
        """Authenticate this agent"""
        return await self.security.authenticate_agent(self.agent_id, credentials)


class A2AWorkflowOrchestrator:
    """A2A Workflow Orchestrator"""
    
    def __init__(self, protocol: A2AProtocol):
        self.protocol = protocol
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
    
    async def start_workflow(self, workflow_id: str, workflow_definition: Dict[str, Any]) -> str:
        """Start a new workflow"""
        self.active_workflows[workflow_id] = {
            "definition": workflow_definition,
            "status": "active",
            "current_step": 0,
            "started_at": datetime.now(),
            "tasks": []
        }
        
        logger.info(f"Started workflow {workflow_id}")
        
        # Execute first step
        if workflow_definition.get("steps"):
            await self._execute_workflow_step(workflow_id, workflow_definition["steps"][0])
        
        return workflow_id
    
    async def _execute_workflow_step(self, workflow_id: str, step: Dict[str, Any]):
        """Execute a workflow step"""
        workflow = self.active_workflows[workflow_id]
        
        target_agent = step.get("target_agent")
        action = step.get("action")
        data = step.get("data", {})
        
        if target_agent and action:
            task_id = await self.protocol.send_task_request(
                recipient_id=target_agent,
                action=action,
                data=data
            )
            
            workflow["tasks"].append({
                "task_id": task_id,
                "step": step,
                "status": "pending"
            })
    
    async def complete_workflow(self, workflow_id: str, result: Dict[str, Any]):
        """Complete a workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow["status"] = "completed"
            workflow["result"] = result
            workflow["completed_at"] = datetime.now()
            
            logger.info(f"Completed workflow {workflow_id}")
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        return self.active_workflows.get(workflow_id)
