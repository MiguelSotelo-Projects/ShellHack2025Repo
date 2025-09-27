"""
Queue Agent

Manages patient queues, wait times, and queue optimization.
"""

import asyncio
import logging
from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools import BaseTool
from ..protocol.agent_protocol import AgentProtocol, MessageType, Priority, ProtocolMessage

logger = logging.getLogger(__name__)


class QueueManagementTool(BaseTool):
    """Tool for queue management operations."""
    
    def __init__(self, protocol: AgentProtocol):
        super().__init__(
            name="queue_management_tool",
            description="Manages patient queues and wait times"
        )
        self.protocol = protocol
        self.queue_data = {
            "waiting": [],
            "in_progress": [],
            "completed": []
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute queue management operations."""
        try:
            action = parameters.get("action", "")
            
            if action == "add_to_queue":
                return await self._add_to_queue(parameters)
            elif action == "get_queue_status":
                return await self._get_queue_status()
            elif action == "call_next_patient":
                return await self._call_next_patient()
            elif action == "update_wait_time":
                return await self._update_wait_time(parameters)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error in queue management: {e}")
            return {"success": False, "error": str(e)}
    
    async def _add_to_queue(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Add patient to queue."""
        patient_id = parameters.get("patient_id")
        priority = parameters.get("priority", "medium")
        
        queue_entry = {
            "patient_id": patient_id,
            "priority": priority,
            "added_at": asyncio.get_event_loop().time(),
            "estimated_wait": self._calculate_wait_time(priority)
        }
        
        self.queue_data["waiting"].append(queue_entry)
        
        # Notify notification agent about queue update
        await self.protocol.send_message(
            recipient_id="notification_agent",
            message_type=MessageType.NOTIFICATION,
            payload={
                "event": "queue_updated",
                "patient_id": patient_id,
                "position": len(self.queue_data["waiting"]),
                "estimated_wait": queue_entry["estimated_wait"]
            },
            priority=Priority.MEDIUM
        )
        
        logger.info(f"Added patient {patient_id} to queue with priority {priority}")
        
        return {
            "success": True,
            "patient_id": patient_id,
            "position": len(self.queue_data["waiting"]),
            "estimated_wait": queue_entry["estimated_wait"]
        }
    
    async def _get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        return {
            "success": True,
            "queue_status": {
                "waiting": len(self.queue_data["waiting"]),
                "in_progress": len(self.queue_data["in_progress"]),
                "completed": len(self.queue_data["completed"]),
                "total_waiting": len(self.queue_data["waiting"]),
                "average_wait_time": self._calculate_average_wait_time()
            }
        }
    
    async def _call_next_patient(self) -> Dict[str, Any]:
        """Call the next patient in queue."""
        if not self.queue_data["waiting"]:
            return {"success": False, "error": "No patients in queue"}
        
        # Sort by priority and arrival time
        self.queue_data["waiting"].sort(
            key=lambda x: (x["priority"] == "urgent", x["added_at"])
        )
        
        next_patient = self.queue_data["waiting"].pop(0)
        self.queue_data["in_progress"].append(next_patient)
        
        # Notify notification agent
        await self.protocol.send_message(
            recipient_id="notification_agent",
            message_type=MessageType.NOTIFICATION,
            payload={
                "event": "patient_called",
                "patient_id": next_patient["patient_id"],
                "message": "Please proceed to the consultation room"
            },
            priority=Priority.HIGH
        )
        
        logger.info(f"Called next patient: {next_patient['patient_id']}")
        
        return {
            "success": True,
            "patient_id": next_patient["patient_id"],
            "message": "Patient called successfully"
        }
    
    async def _update_wait_time(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update estimated wait times."""
        # Recalculate wait times for all waiting patients
        for patient in self.queue_data["waiting"]:
            patient["estimated_wait"] = self._calculate_wait_time(patient["priority"])
        
        return {
            "success": True,
            "message": "Wait times updated",
            "updated_count": len(self.queue_data["waiting"])
        }
    
    def _calculate_wait_time(self, priority: str) -> int:
        """Calculate estimated wait time based on priority."""
        base_wait = {
            "urgent": 5,
            "high": 15,
            "medium": 30,
            "low": 45
        }
        return base_wait.get(priority, 30)
    
    def _calculate_average_wait_time(self) -> int:
        """Calculate average wait time for all waiting patients."""
        if not self.queue_data["waiting"]:
            return 0
        
        total_wait = sum(patient["estimated_wait"] for patient in self.queue_data["waiting"])
        return total_wait // len(self.queue_data["waiting"])


class QueueAgent:
    """Queue Agent for managing patient queues."""
    
    def __init__(self, project_id: str = None):
        self.agent_id = "queue_agent"
        self.protocol = AgentProtocol(self.agent_id, project_id)
        self.agent = None
        self.queue_tool = None
    
    async def initialize(self):
        """Initialize the agent and its tools."""
        await self.protocol.initialize()
        
        # Create tools
        self.queue_tool = QueueManagementTool(self.protocol)
        
        # Create ADK agent
        self.agent = Agent(
            name="Queue Agent",
            description="Manages patient queues and wait times",
            tools=[self.queue_tool],
            model="gemini-1.5-flash"
        )
        
        # Register message handlers
        self.protocol.register_handler(MessageType.REQUEST, self._handle_request)
        self.protocol.register_handler(MessageType.NOTIFICATION, self._handle_notification)
        self.protocol.register_handler(MessageType.COORDINATION, self._handle_coordination)
        
        logger.info("Queue Agent initialized")
    
    async def _handle_request(self, message: ProtocolMessage):
        """Handle incoming requests."""
        logger.info(f"Queue Agent received request: {message.payload}")
        
        # Process the request using queue tool
        result = await self.queue_tool.execute(message.payload)
        
        await self.protocol.send_response(message, result)
    
    async def _handle_notification(self, message: ProtocolMessage):
        """Handle notifications from other agents."""
        event = message.payload.get("event")
        
        if event == "patient_registered":
            # Add new patient to queue
            await self.queue_tool.execute({
                "action": "add_to_queue",
                "patient_id": message.payload.get("patient_id"),
                "priority": message.payload.get("priority", "medium")
            })
        
        elif event == "patient_checked_in":
            # Handle check-in notification
            logger.info(f"Patient {message.payload.get('patient_id')} checked in")
    
    async def _handle_coordination(self, message: ProtocolMessage):
        """Handle coordination messages."""
        logger.info(f"Queue Agent received coordination: {message.payload}")
        
        # Handle coordination logic here
        flow_id = message.payload.get("flow_id")
        step_data = message.payload.get("data", {})
        
        # Process coordination step
        if step_data.get("action") == "manage_queue":
            result = await self.queue_tool.execute(step_data)
            logger.info(f"Processed coordination step: {result}")
    
    async def start(self):
        """Start the agent."""
        if not self.agent:
            await self.initialize()
        
        logger.info("Starting Queue Agent...")
        
        # Start listening for messages
        await self.protocol.start_listening()
    
    async def stop(self):
        """Stop the agent."""
        await self.protocol.stop_listening()
        logger.info("Queue Agent stopped")
