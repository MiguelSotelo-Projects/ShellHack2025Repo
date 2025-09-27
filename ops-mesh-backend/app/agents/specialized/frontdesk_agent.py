"""
FrontDesk Agent

Handles patient registration, check-in, and initial patient flow coordination.
"""

import asyncio
import logging
from typing import Dict, Any
from google.adk.agents import Agent
from google.adk.tools import BaseTool
from ..protocol.agent_protocol import AgentProtocol, MessageType, Priority, ProtocolMessage

logger = logging.getLogger(__name__)


class PatientRegistrationTool(BaseTool):
    """Tool for patient registration and check-in."""
    
    def __init__(self, protocol: AgentProtocol):
        super().__init__(
            name="patient_registration_tool",
            description="Handles patient registration and check-in processes"
        )
        self.protocol = protocol
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute patient registration or check-in."""
        try:
            action = parameters.get("action", "")
            patient_data = parameters.get("patient_data", {})
            
            if action == "register_patient":
                # Register new patient
                result = await self._register_patient(patient_data)
                
                # Notify queue agent about new patient
                await self.protocol.send_message(
                    recipient_id="queue_agent",
                    message_type=MessageType.NOTIFICATION,
                    payload={
                        "event": "patient_registered",
                        "patient_id": result.get("patient_id"),
                        "priority": patient_data.get("priority", "medium")
                    },
                    priority=Priority.MEDIUM
                )
                
                return result
                
            elif action == "check_in_patient":
                # Check in existing patient
                result = await self._check_in_patient(patient_data)
                
                # Notify queue agent about check-in
                await self.protocol.send_message(
                    recipient_id="queue_agent",
                    message_type=MessageType.NOTIFICATION,
                    payload={
                        "event": "patient_checked_in",
                        "patient_id": result.get("patient_id"),
                        "appointment_id": result.get("appointment_id")
                    },
                    priority=Priority.HIGH
                )
                
                return result
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error in patient registration: {e}")
            return {"success": False, "error": str(e)}
    
    async def _register_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new patient."""
        # Simulate patient registration
        patient_id = f"PAT-{asyncio.get_event_loop().time()}"
        
        logger.info(f"Registered new patient: {patient_id}")
        
        return {
            "success": True,
            "patient_id": patient_id,
            "message": "Patient registered successfully",
            "data": patient_data
        }
    
    async def _check_in_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check in an existing patient."""
        patient_id = patient_data.get("patient_id")
        appointment_id = patient_data.get("appointment_id")
        
        logger.info(f"Checked in patient {patient_id} for appointment {appointment_id}")
        
        return {
            "success": True,
            "patient_id": patient_id,
            "appointment_id": appointment_id,
            "message": "Patient checked in successfully"
        }


class FrontDeskAgent:
    """FrontDesk Agent for patient registration and check-in."""
    
    def __init__(self, project_id: str = None):
        self.agent_id = "frontdesk_agent"
        self.protocol = AgentProtocol(self.agent_id, project_id)
        self.agent = None
        self.registration_tool = None
    
    async def initialize(self):
        """Initialize the agent and its tools."""
        await self.protocol.initialize()
        
        # Create tools
        self.registration_tool = PatientRegistrationTool(self.protocol)
        
        # Create ADK agent
        self.agent = Agent(
            name="FrontDesk Agent",
            description="Handles patient registration and check-in processes",
            tools=[self.registration_tool],
            model="gemini-1.5-flash"
        )
        
        # Register message handlers
        self.protocol.register_handler(MessageType.REQUEST, self._handle_request)
        self.protocol.register_handler(MessageType.COORDINATION, self._handle_coordination)
        
        logger.info("FrontDesk Agent initialized")
    
    async def _handle_request(self, message: ProtocolMessage):
        """Handle incoming requests."""
        logger.info(f"FrontDesk Agent received request: {message.payload}")
        
        # Process the request and send response
        response_payload = {
            "status": "processed",
            "agent": self.agent_id,
            "result": "Request handled by FrontDesk Agent"
        }
        
        await self.protocol.send_response(message, response_payload)
    
    async def _handle_coordination(self, message: ProtocolMessage):
        """Handle coordination messages."""
        logger.info(f"FrontDesk Agent received coordination: {message.payload}")
        
        # Handle coordination logic here
        flow_id = message.payload.get("flow_id")
        step_data = message.payload.get("data", {})
        
        # Process coordination step
        if step_data.get("action") == "register_patient":
            result = await self.registration_tool.execute(step_data)
            logger.info(f"Processed coordination step: {result}")
    
    async def start(self):
        """Start the agent."""
        if not self.agent:
            await self.initialize()
        
        logger.info("Starting FrontDesk Agent...")
        
        # Start listening for messages
        await self.protocol.start_listening()
    
    async def stop(self):
        """Stop the agent."""
        await self.protocol.stop_listening()
        logger.info("FrontDesk Agent stopped")
