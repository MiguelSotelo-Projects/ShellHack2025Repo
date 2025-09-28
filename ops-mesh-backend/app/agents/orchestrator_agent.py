"""
Orchestrator Agent

Coordinates complex workflows between multiple specialized agents.
"""

import asyncio
import logging
from typing import Dict, Any, List

# Try to import Google ADK, fallback to internal implementation
try:
    from google.adk.agents import Agent
    from google.adk.tools import BaseTool
except ImportError:
    from .google_adk_fallback import Agent, BaseTool

from .protocol.a2a_protocol import A2AProtocol, A2ATaskRequest, TaskStatus, A2AWorkflowOrchestrator
from .protocol.agent_protocol import MessageType, Priority, ProtocolMessage

logger = logging.getLogger(__name__)


class WorkflowOrchestrationTool(BaseTool):
    """Tool for orchestrating complex workflows between agents."""
    
    def __init__(self, protocol: A2AProtocol):
        super().__init__(
            name="workflow_orchestration_tool",
            description="Orchestrates complex workflows between multiple agents"
        )
        self.protocol = protocol
        self.orchestrator = A2AWorkflowOrchestrator(protocol)
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
        await self.protocol.send_task_request(
            recipient_id="queue_agent",
            action="add_to_queue",
            data={
                "patient_id": patient_id,
                "priority": "urgent",
                "queue_type": "emergency"
            }
        )
        
        await self.protocol.send_task_request(
            recipient_id="notification_agent",
            action="send_alert",
            data={
                "recipient": f"patient_{patient_id}",
                "message": "EMERGENCY: Immediate attention required",
                "level": "critical"
            }
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
        self.protocol = A2AProtocol(
            self.agent_id, 
            "ops-mesh-backend/agents/orchestrator_agent.json"
        )
        self.agent = None
        self.orchestration_tool = None
    
    async def initialize(self):
        """Initialize the agent and its tools."""
        await self.protocol.start()
        
        # Create tools
        self.orchestration_tool = WorkflowOrchestrationTool(self.protocol)
        
        # Create ADK agent
        try:
            self.agent = Agent(
                name="Orchestrator Agent",
                description="Coordinates complex workflows between multiple agents",
                tools=[self.orchestration_tool],
                model="gemini-1.5-flash"
            )
        except TypeError:
            # Fallback for internal Agent implementation
            self.agent = Agent(
                name="Orchestrator Agent",
                tools=[self.orchestration_tool]
            )
        
        # Register task handlers
        self.protocol.register_task_handler("start_patient_flow", self._handle_start_patient_flow)
        self.protocol.register_task_handler("start_appointment_flow", self._handle_start_appointment_flow)
        self.protocol.register_task_handler("coordinate_emergency", self._handle_coordinate_emergency)
        
        logger.info("Orchestrator Agent initialized")
    
    async def _handle_start_patient_flow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle start patient flow task."""
        logger.info(f"Orchestrator Agent handling start_patient_flow: {data}")
        return await self.orchestration_tool.execute({
            "action": "start_patient_flow",
            "patient_data": data.get("patient_data", {}),
            "flow_type": data.get("flow_type", "walk_in")
        })
    
    async def _handle_start_appointment_flow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle start appointment flow task."""
        logger.info(f"Orchestrator Agent handling start_appointment_flow: {data}")
        return await self.orchestration_tool.execute({
            "action": "start_appointment_flow",
            "appointment_data": data.get("appointment_data", {})
        })
    
    async def _handle_coordinate_emergency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle coordinate emergency task."""
        logger.info(f"Orchestrator Agent handling coordinate_emergency: {data}")
        return await self.orchestration_tool.execute({
            "action": "coordinate_emergency",
            "emergency_data": data.get("emergency_data", {})
        })
    
    async def start(self):
        """Start the agent."""
        if not self.agent:
            await self.initialize()
        
        logger.info("Starting Orchestrator Agent...")
        
        logger.info("Orchestrator Agent started")
    
    async def stop(self):
        """Stop the agent."""
        await self.protocol.stop()
        logger.info("Orchestrator Agent stopped")
