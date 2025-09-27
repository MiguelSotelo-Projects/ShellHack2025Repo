"""
Orchestrator Agent

Coordinates complex workflows between multiple specialized agents.
"""

import asyncio
import logging
from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools import BaseTool
from .protocol.agent_protocol import AgentProtocol, MessageType, Priority, ProtocolMessage, FlowOrchestrator

logger = logging.getLogger(__name__)


class WorkflowOrchestrationTool(BaseTool):
    """Tool for orchestrating complex workflows between agents."""
    
    def __init__(self, protocol: AgentProtocol):
        super().__init__(
            name="workflow_orchestration_tool",
            description="Orchestrates complex workflows between multiple agents"
        )
        self.protocol = protocol
        self.orchestrator = FlowOrchestrator(protocol)
        self.active_workflows = {}
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow orchestration operations."""
        try:
            action = parameters.get("action", "")
            
            if action == "start_patient_flow":
                return await self._start_patient_flow(parameters)
            elif action == "start_appointment_flow":
                return await self._start_appointment_flow(parameters)
            elif action == "get_workflow_status":
                return await self._get_workflow_status(parameters)
            elif action == "coordinate_emergency":
                return await self._coordinate_emergency(parameters)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error in workflow orchestration: {e}")
            return {"success": False, "error": str(e)}
    
    async def _start_patient_flow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Start a complete patient flow workflow."""
        patient_data = parameters.get("patient_data", {})
        flow_type = parameters.get("flow_type", "walk_in")
        
        flow_id = f"patient_flow_{asyncio.get_event_loop().time()}"
        
        # Define the workflow steps
        workflow_definition = {
            "type": "patient_flow",
            "patient_data": patient_data,
            "flow_type": flow_type,
            "steps": [
                {
                    "step": 1,
                    "action": "register_patient",
                    "target_agent": "frontdesk_agent",
                    "data": patient_data
                },
                {
                    "step": 2,
                    "action": "add_to_queue",
                    "target_agent": "queue_agent",
                    "data": {
                        "patient_id": patient_data.get("patient_id"),
                        "priority": patient_data.get("priority", "medium")
                    }
                },
                {
                    "step": 3,
                    "action": "send_notification",
                    "target_agent": "notification_agent",
                    "data": {
                        "recipient": f"patient_{patient_data.get('patient_id')}",
                        "message": "You have been registered and added to the queue"
                    }
                }
            ]
        }
        
        # Start the workflow
        await self.orchestrator.start_flow(flow_id, workflow_definition)
        self.active_workflows[flow_id] = workflow_definition
        
        # Execute first step
        await self.orchestrator.coordinate_step(flow_id, workflow_definition["steps"][0])
        
        logger.info(f"Started patient flow workflow: {flow_id}")
        
        return {
            "success": True,
            "flow_id": flow_id,
            "message": "Patient flow workflow started"
        }
    
    async def _start_appointment_flow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Start an appointment scheduling workflow."""
        appointment_data = parameters.get("appointment_data", {})
        
        flow_id = f"appointment_flow_{asyncio.get_event_loop().time()}"
        
        # Define the workflow steps
        workflow_definition = {
            "type": "appointment_flow",
            "appointment_data": appointment_data,
            "steps": [
                {
                    "step": 1,
                    "action": "schedule_appointment",
                    "target_agent": "appointment_agent",
                    "data": appointment_data
                },
                {
                    "step": 2,
                    "action": "send_reminder",
                    "target_agent": "notification_agent",
                    "data": {
                        "recipient": f"patient_{appointment_data.get('patient_id')}",
                        "message": f"Your appointment has been scheduled for {appointment_data.get('appointment_time')}",
                        "reminder_type": "appointment"
                    }
                }
            ]
        }
        
        # Start the workflow
        await self.orchestrator.start_flow(flow_id, workflow_definition)
        self.active_workflows[flow_id] = workflow_definition
        
        # Execute first step
        await self.orchestrator.coordinate_step(flow_id, workflow_definition["steps"][0])
        
        logger.info(f"Started appointment flow workflow: {flow_id}")
        
        return {
            "success": True,
            "flow_id": flow_id,
            "message": "Appointment flow workflow started"
        }
    
    async def _get_workflow_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get the status of a workflow."""
        flow_id = parameters.get("flow_id")
        
        if flow_id:
            status = self.orchestrator.get_flow_status(flow_id)
            return {
                "success": True,
                "flow_id": flow_id,
                "status": status
            }
        else:
            return {
                "success": True,
                "active_workflows": list(self.active_workflows.keys()),
                "total_count": len(self.active_workflows)
            }
    
    async def _coordinate_emergency(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate an emergency situation."""
        emergency_data = parameters.get("emergency_data", {})
        patient_id = emergency_data.get("patient_id")
        
        # Send urgent notifications to all relevant agents
        await self.protocol.send_message(
            recipient_id="queue_agent",
            message_type=MessageType.COORDINATION,
            payload={
                "action": "emergency_priority",
                "patient_id": patient_id,
                "priority": "urgent"
            },
            priority=Priority.URGENT
        )
        
        await self.protocol.send_message(
            recipient_id="notification_agent",
            message_type=MessageType.NOTIFICATION,
            payload={
                "event": "emergency_alert",
                "patient_id": patient_id,
                "message": "EMERGENCY: Immediate attention required"
            },
            priority=Priority.URGENT
        )
        
        logger.warning(f"Coordinated emergency response for patient {patient_id}")
        
        return {
            "success": True,
            "message": "Emergency coordination initiated",
            "patient_id": patient_id
        }


class OrchestratorAgent:
    """Orchestrator Agent for coordinating complex workflows."""
    
    def __init__(self, project_id: str = None):
        self.agent_id = "orchestrator_agent"
        self.protocol = AgentProtocol(self.agent_id, project_id)
        self.agent = None
        self.orchestration_tool = None
    
    async def initialize(self):
        """Initialize the agent and its tools."""
        await self.protocol.initialize()
        
        # Create tools
        self.orchestration_tool = WorkflowOrchestrationTool(self.protocol)
        
        # Create ADK agent
        self.agent = Agent(
            name="Orchestrator Agent",
            description="Coordinates complex workflows between multiple agents",
            tools=[self.orchestration_tool],
            model="gemini-1.5-flash"
        )
        
        # Register message handlers
        self.protocol.register_handler(MessageType.REQUEST, self._handle_request)
        self.protocol.register_handler(MessageType.RESPONSE, self._handle_response)
        self.protocol.register_handler(MessageType.COORDINATION, self._handle_coordination)
        
        logger.info("Orchestrator Agent initialized")
    
    async def _handle_request(self, message: ProtocolMessage):
        """Handle incoming requests."""
        logger.info(f"Orchestrator Agent received request: {message.payload}")
        
        # Process the request using orchestration tool
        result = await self.orchestration_tool.execute(message.payload)
        
        await self.protocol.send_response(message, result)
    
    async def _handle_response(self, message: ProtocolMessage):
        """Handle responses from other agents."""
        logger.info(f"Orchestrator Agent received response: {message.payload}")
        
        # Process workflow step completion
        correlation_id = message.correlation_id
        if correlation_id:
            # Find the workflow and advance to next step
            for flow_id, workflow in self.orchestration_tool.active_workflows.items():
                if correlation_id in str(workflow):
                    # Advance to next step
                    current_step = workflow.get("current_step", 0)
                    if current_step < len(workflow["steps"]) - 1:
                        next_step = workflow["steps"][current_step + 1]
                        await self.orchestration_tool.orchestrator.coordinate_step(flow_id, next_step)
                    else:
                        # Workflow completed
                        await self.orchestration_tool.orchestrator.complete_flow(flow_id, message.payload)
    
    async def _handle_coordination(self, message: ProtocolMessage):
        """Handle coordination messages."""
        logger.info(f"Orchestrator Agent received coordination: {message.payload}")
        
        # Handle coordination logic here
        flow_id = message.payload.get("flow_id")
        step_data = message.payload.get("data", {})
        
        # Process coordination step
        if step_data.get("action") == "orchestrate_workflow":
            result = await self.orchestration_tool.execute(step_data)
            logger.info(f"Processed coordination step: {result}")
    
    async def start(self):
        """Start the agent."""
        if not self.agent:
            await self.initialize()
        
        logger.info("Starting Orchestrator Agent...")
        
        # Start listening for messages
        await self.protocol.start_listening()
    
    async def stop(self):
        """Stop the agent."""
        await self.protocol.stop_listening()
        logger.info("Orchestrator Agent stopped")
