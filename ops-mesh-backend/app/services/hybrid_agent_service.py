"""
Hybrid Agent Communication Service

This service provides both simulated and real agent communication capabilities,
allowing the system to work with or without Google Cloud infrastructure.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import random

logger = logging.getLogger(__name__)


class CommunicationMode(Enum):
    """Communication modes for the hybrid system."""
    SIMULATED = "simulated"
    REAL = "real"
    HYBRID = "hybrid"


class MessageType(Enum):
    """Types of messages in the agent communication system."""
    DISCOVERY = "discovery"
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    HEARTBEAT = "heartbeat"
    NOTIFICATION = "notification"
    ERROR = "error"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_STEP = "workflow_step"
    WORKFLOW_COMPLETE = "workflow_complete"


class AgentMessage:
    """Represents a message between agents."""
    
    def __init__(self, message_id: str, from_agent: str, to_agent: str, 
                 message_type: MessageType, payload: Dict[str, Any], 
                 timestamp: Optional[datetime] = None):
        self.message_id = message_id
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.payload = payload
        self.timestamp = timestamp or datetime.now()
        self.status = "sent"
        self.response = None
        self.processing_time = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "response": self.response,
            "processing_time": self.processing_time
        }


class AgentStatus:
    """Represents the status of an agent."""
    
    def __init__(self, agent_id: str, name: str, status: str = "active", 
                 capabilities: List[str] = None, last_heartbeat: Optional[datetime] = None):
        self.agent_id = agent_id
        self.name = name
        self.status = status
        self.capabilities = capabilities or []
        self.last_heartbeat = last_heartbeat or datetime.now()
        self.current_task = None
        self.message_count = 0
        self.error_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent status to dictionary."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "capabilities": self.capabilities,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "current_task": self.current_task,
            "message_count": self.message_count,
            "error_count": self.error_count
        }


class HybridAgentService:
    """Hybrid agent communication service supporting both simulated and real communication."""
    
    def __init__(self):
        self.mode = CommunicationMode.SIMULATED
        self.agents: Dict[str, AgentStatus] = {}
        self.message_history: List[AgentMessage] = []
        self.message_handlers: Dict[str, Callable] = {}
        self.workflow_templates: Dict[str, List[Dict]] = {}
        self.is_running = False
        self.heartbeat_interval = 5.0  # seconds
        self._heartbeat_task = None
        
        # Initialize default agents
        self._initialize_default_agents()
        self._initialize_workflow_templates()
    
    def _initialize_default_agents(self):
        """Initialize default agent configurations."""
        default_agents = [
            {
                "agent_id": "orchestrator_agent",
                "name": "Workflow Orchestrator",
                "capabilities": ["workflow_coordination", "task_distribution", "error_handling", "security_monitoring"]
            },
            {
                "agent_id": "frontdesk_agent", 
                "name": "Front Desk Agent",
                "capabilities": ["patient_registration", "check_in", "info_update", "data_validation"]
            },
            {
                "agent_id": "queue_agent",
                "name": "Queue Management Agent", 
                "capabilities": ["queue_management", "wait_time_calculation", "patient_calling", "optimization"]
            },
            {
                "agent_id": "appointment_agent",
                "name": "Appointment Agent",
                "capabilities": ["scheduling", "rescheduling", "cancellation", "conflict_resolution"]
            },
            {
                "agent_id": "notification_agent",
                "name": "Notification Agent",
                "capabilities": ["sms", "email", "push_notifications", "delivery_tracking"]
            }
        ]
        
        for agent_data in default_agents:
            self.agents[agent_data["agent_id"]] = AgentStatus(
                agent_id=agent_data["agent_id"],
                name=agent_data["name"],
                capabilities=agent_data["capabilities"]
            )
    
    def _initialize_workflow_templates(self):
        """Initialize workflow templates for common hospital operations."""
        self.workflow_templates = {
            "patient_registration": [
                {
                    "step": 1,
                    "from": "orchestrator_agent",
                    "to": "frontdesk_agent", 
                    "action": "register_patient",
                    "description": "Register new patient in system"
                },
                {
                    "step": 2,
                    "from": "frontdesk_agent",
                    "to": "orchestrator_agent",
                    "action": "patient_registered",
                    "description": "Confirm patient registration"
                },
                {
                    "step": 3,
                    "from": "orchestrator_agent", 
                    "to": "queue_agent",
                    "action": "add_to_queue",
                    "description": "Add patient to appropriate queue"
                },
                {
                    "step": 4,
                    "from": "queue_agent",
                    "to": "orchestrator_agent",
                    "action": "patient_queued",
                    "description": "Confirm patient added to queue"
                },
                {
                    "step": 5,
                    "from": "orchestrator_agent",
                    "to": "notification_agent",
                    "action": "send_welcome_notification",
                    "description": "Send welcome notification to patient"
                }
            ],
            "appointment_scheduling": [
                {
                    "step": 1,
                    "from": "orchestrator_agent",
                    "to": "appointment_agent",
                    "action": "schedule_appointment",
                    "description": "Schedule new appointment"
                },
                {
                    "step": 2,
                    "from": "appointment_agent",
                    "to": "orchestrator_agent", 
                    "action": "appointment_scheduled",
                    "description": "Confirm appointment scheduling"
                },
                {
                    "step": 3,
                    "from": "orchestrator_agent",
                    "to": "notification_agent",
                    "action": "send_appointment_confirmation",
                    "description": "Send appointment confirmation"
                }
            ]
        }
    
    async def start(self, mode: CommunicationMode = CommunicationMode.SIMULATED):
        """Start the hybrid agent service."""
        self.mode = mode
        self.is_running = True
        
        logger.info(f"🚀 Starting Hybrid Agent Service in {mode.value} mode")
        
        # Start heartbeat monitoring
        self._heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        
        # If in real mode, try to initialize real agents
        if mode == CommunicationMode.REAL:
            await self._initialize_real_agents()
        
        logger.info("✅ Hybrid Agent Service started successfully")
    
    async def stop(self):
        """Stop the hybrid agent service."""
        self.is_running = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🛑 Hybrid Agent Service stopped")
    
    async def _initialize_real_agents(self):
        """Initialize real agents if available."""
        try:
            # Try to import and initialize real agent manager
            from ..agents.agent_manager import AgentManager
            
            self.real_agent_manager = AgentManager("ops-mesh-demo")
            await self.real_agent_manager.initialize_all_agents()
            
            logger.info("✅ Real agents initialized successfully")
            self.mode = CommunicationMode.REAL
            
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize real agents: {e}")
            logger.info("🔄 Falling back to simulated mode")
            self.mode = CommunicationMode.SIMULATED
    
    async def _heartbeat_monitor(self):
        """Monitor agent heartbeats."""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                for agent in self.agents.values():
                    # Simulate heartbeat updates
                    if self.mode == CommunicationMode.SIMULATED:
                        agent.last_heartbeat = current_time
                        
                        # Simulate occasional status changes
                        if random.random() < 0.1:  # 10% chance
                            if agent.status == "active" and random.random() < 0.05:
                                agent.status = "busy"
                            elif agent.status == "busy" and random.random() < 0.3:
                                agent.status = "active"
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(self.heartbeat_interval)
    
    async def send_message(self, from_agent: str, to_agent: str, 
                          message_type: MessageType, payload: Dict[str, Any]) -> AgentMessage:
        """Send a message between agents."""
        if not self.is_running:
            raise RuntimeError("Agent service is not running")
        
        message_id = f"{from_agent}-{to_agent}-{int(time.time() * 1000)}"
        message = AgentMessage(message_id, from_agent, to_agent, message_type, payload)
        
        # Add to message history
        self.message_history.append(message)
        
        # Update agent message counts
        if from_agent in self.agents:
            self.agents[from_agent].message_count += 1
        
        logger.info(f"📤 {from_agent} → {to_agent}: {message_type.value}")
        
        # Process message based on mode
        if self.mode == CommunicationMode.REAL and hasattr(self, 'real_agent_manager'):
            await self._process_real_message(message)
        else:
            await self._process_simulated_message(message)
        
        return message
    
    async def _process_simulated_message(self, message: AgentMessage):
        """Process a message in simulated mode."""
        start_time = time.time()
        
        # Simulate processing delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Generate realistic response based on message type
        response = await self._generate_simulated_response(message)
        
        message.response = response
        message.status = "completed"
        message.processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Update target agent status
        if message.to_agent in self.agents:
            self.agents[message.to_agent].current_task = message.payload.get("action", "processing")
            self.agents[message.to_agent].last_heartbeat = datetime.now()
    
    async def _process_real_message(self, message: AgentMessage):
        """Process a message in real mode."""
        try:
            # Use real agent manager to send message
            result = await self.real_agent_manager.send_message_to_agent(
                target_agent=message.to_agent.replace("_agent", ""),
                message_type=message.payload.get("action", "unknown"),
                payload=message.payload
            )
            
            message.response = result
            message.status = "completed"
            
        except Exception as e:
            logger.error(f"Error processing real message: {e}")
            message.response = {"error": str(e)}
            message.status = "error"
            
            if message.to_agent in self.agents:
                self.agents[message.to_agent].error_count += 1
    
    async def _generate_simulated_response(self, message: AgentMessage) -> Dict[str, Any]:
        """Generate a realistic simulated response."""
        action = message.payload.get("action", "")
        
        # Generate responses based on action type
        if action == "register_patient":
            return {
                "success": True,
                "patient_id": f"PAT-{random.randint(10000, 99999)}",
                "status": "registered",
                "message": "Patient registered successfully"
            }
        elif action == "add_to_queue":
            return {
                "success": True,
                "queue_position": random.randint(1, 10),
                "estimated_wait": random.randint(5, 30),
                "message": "Patient added to queue"
            }
        elif action == "schedule_appointment":
            return {
                "success": True,
                "appointment_id": f"APT-{random.randint(10000, 99999)}",
                "confirmation_code": f"ABC{random.randint(100, 999)}",
                "message": "Appointment scheduled successfully"
            }
        elif action == "send_notification":
            return {
                "success": True,
                "notification_id": f"NOT-{random.randint(10000, 99999)}",
                "delivery_status": "sent",
                "message": "Notification sent successfully"
            }
        else:
            return {
                "success": True,
                "message": f"Action '{action}' completed successfully",
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> List[AgentMessage]:
        """Execute a predefined workflow."""
        if workflow_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow = self.workflow_templates[workflow_name]
        messages = []
        
        logger.info(f"🔄 Starting workflow: {workflow_name}")
        
        for step in workflow:
            # Prepare payload with parameters
            payload = {
                "action": step["action"],
                "workflow": workflow_name,
                "step": step["step"],
                **parameters
            }
            
            # Send message
            message = await self.send_message(
                from_agent=step["from"],
                to_agent=step["to"],
                message_type=MessageType.TASK_REQUEST,
                payload=payload
            )
            
            messages.append(message)
            
            # Small delay between steps
            await asyncio.sleep(0.5)
        
        logger.info(f"✅ Workflow '{workflow_name}' completed with {len(messages)} steps")
        return messages
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of all agents."""
        return {
            agent_id: agent.to_dict() 
            for agent_id, agent in self.agents.items()
        }
    
    def get_message_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent message history."""
        recent_messages = self.message_history[-limit:] if self.message_history else []
        return [msg.to_dict() for msg in recent_messages]
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics."""
        total_messages = len(self.message_history)
        successful_messages = len([m for m in self.message_history if m.status == "completed"])
        error_messages = len([m for m in self.message_history if m.status == "error"])
        
        return {
            "total_messages": total_messages,
            "successful_messages": successful_messages,
            "error_messages": error_messages,
            "success_rate": (successful_messages / total_messages * 100) if total_messages > 0 else 0,
            "active_agents": len([a for a in self.agents.values() if a.status == "active"]),
            "mode": self.mode.value,
            "is_running": self.is_running
        }


# Global instance
hybrid_agent_service = HybridAgentService()
