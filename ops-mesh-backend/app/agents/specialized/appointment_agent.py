"""
Appointment Agent

Handles appointment scheduling, management, and coordination.
"""

import asyncio
import logging
from typing import Dict, Any
from google.adk.agents import Agent
from google.adk.tools import BaseTool
from ..protocol.agent_protocol import AgentProtocol, MessageType, Priority, ProtocolMessage

logger = logging.getLogger(__name__)


class AppointmentManagementTool(BaseTool):
    """Tool for appointment management operations."""
    
    def __init__(self, protocol: AgentProtocol):
        super().__init__(
            name="appointment_management_tool",
            description="Manages appointment scheduling and coordination"
        )
        self.protocol = protocol
        self.appointments = {}
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute appointment management operations."""
        try:
            action = parameters.get("action", "")
            
            if action == "schedule_appointment":
                return await self._schedule_appointment(parameters)
            elif action == "get_appointment":
                return await self._get_appointment(parameters)
            elif action == "update_appointment":
                return await self._update_appointment(parameters)
            elif action == "cancel_appointment":
                return await self._cancel_appointment(parameters)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error in appointment management: {e}")
            return {"success": False, "error": str(e)}
    
    async def _schedule_appointment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a new appointment."""
        patient_id = parameters.get("patient_id")
        provider = parameters.get("provider")
        appointment_time = parameters.get("appointment_time")
        appointment_type = parameters.get("type", "routine")
        
        appointment_id = f"APT-{asyncio.get_event_loop().time()}"
        
        appointment = {
            "id": appointment_id,
            "patient_id": patient_id,
            "provider": provider,
            "appointment_time": appointment_time,
            "type": appointment_type,
            "status": "scheduled",
            "created_at": asyncio.get_event_loop().time()
        }
        
        self.appointments[appointment_id] = appointment
        
        # Notify notification agent about new appointment
        await self.protocol.send_message(
            recipient_id="notification_agent",
            message_type=MessageType.NOTIFICATION,
            payload={
                "event": "appointment_scheduled",
                "patient_id": patient_id,
                "appointment_id": appointment_id,
                "appointment_time": appointment_time,
                "provider": provider
            },
            priority=Priority.MEDIUM
        )
        
        logger.info(f"Scheduled appointment {appointment_id} for patient {patient_id}")
        
        return {
            "success": True,
            "appointment_id": appointment_id,
            "message": "Appointment scheduled successfully"
        }
    
    async def _get_appointment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get appointment details."""
        appointment_id = parameters.get("appointment_id")
        
        if appointment_id in self.appointments:
            return {
                "success": True,
                "appointment": self.appointments[appointment_id]
            }
        else:
            return {
                "success": False,
                "error": "Appointment not found"
            }
    
    async def _update_appointment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing appointment."""
        appointment_id = parameters.get("appointment_id")
        updates = parameters.get("updates", {})
        
        if appointment_id in self.appointments:
            self.appointments[appointment_id].update(updates)
            
            # Notify notification agent about appointment update
            await self.protocol.send_message(
                recipient_id="notification_agent",
                message_type=MessageType.NOTIFICATION,
                payload={
                    "event": "appointment_updated",
                    "appointment_id": appointment_id,
                    "updates": updates
                },
                priority=Priority.MEDIUM
            )
            
            return {
                "success": True,
                "message": "Appointment updated successfully"
            }
        else:
            return {
                "success": False,
                "error": "Appointment not found"
            }
    
    async def _cancel_appointment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel an appointment."""
        appointment_id = parameters.get("appointment_id")
        reason = parameters.get("reason", "No reason provided")
        
        if appointment_id in self.appointments:
            self.appointments[appointment_id]["status"] = "cancelled"
            self.appointments[appointment_id]["cancellation_reason"] = reason
            
            # Notify notification agent about appointment cancellation
            await self.protocol.send_message(
                recipient_id="notification_agent",
                message_type=MessageType.NOTIFICATION,
                payload={
                    "event": "appointment_cancelled",
                    "appointment_id": appointment_id,
                    "reason": reason
                },
                priority=Priority.HIGH
            )
            
            return {
                "success": True,
                "message": "Appointment cancelled successfully"
            }
        else:
            return {
                "success": False,
                "error": "Appointment not found"
            }


class AppointmentAgent:
    """Appointment Agent for managing appointments."""
    
    def __init__(self, project_id: str = None):
        self.agent_id = "appointment_agent"
        self.protocol = AgentProtocol(self.agent_id, project_id)
        self.agent = None
        self.appointment_tool = None
    
    async def initialize(self):
        """Initialize the agent and its tools."""
        await self.protocol.initialize()
        
        # Create tools
        self.appointment_tool = AppointmentManagementTool(self.protocol)
        
        # Create ADK agent
        self.agent = Agent(
            name="Appointment Agent",
            description="Manages appointment scheduling and coordination",
            tools=[self.appointment_tool],
            model="gemini-1.5-flash"
        )
        
        # Register message handlers
        self.protocol.register_handler(MessageType.REQUEST, self._handle_request)
        self.protocol.register_handler(MessageType.COORDINATION, self._handle_coordination)
        
        logger.info("Appointment Agent initialized")
    
    async def _handle_request(self, message: ProtocolMessage):
        """Handle incoming requests."""
        logger.info(f"Appointment Agent received request: {message.payload}")
        
        # Process the request using appointment tool
        result = await self.appointment_tool.execute(message.payload)
        
        await self.protocol.send_response(message, result)
    
    async def _handle_coordination(self, message: ProtocolMessage):
        """Handle coordination messages."""
        logger.info(f"Appointment Agent received coordination: {message.payload}")
        
        # Handle coordination logic here
        flow_id = message.payload.get("flow_id")
        step_data = message.payload.get("data", {})
        
        # Process coordination step
        if step_data.get("action") == "schedule_appointment":
            result = await self.appointment_tool.execute(step_data)
            logger.info(f"Processed coordination step: {result}")
    
    async def start(self):
        """Start the agent."""
        if not self.agent:
            await self.initialize()
        
        logger.info("Starting Appointment Agent...")
        
        # Start listening for messages
        await self.protocol.start_listening()
    
    async def stop(self):
        """Stop the agent."""
        await self.protocol.stop_listening()
        logger.info("Appointment Agent stopped")
