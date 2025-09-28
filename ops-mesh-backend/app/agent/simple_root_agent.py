"""
Simple Root Agent for Ops Mesh ADK Web Interface

This is a simplified version that doesn't depend on complex service imports.
"""

# Try to import Google ADK, fallback to internal implementation
try:
    from google.adk.agents import Agent
    from google.adk.tools import BaseTool
except ImportError:
    from ..agents.google_adk_fallback import Agent, BaseTool

from typing import Dict, Any
import logging
from ..agents.adk_tools import AgentDiscoveryTool, A2ACommunicationTool, HospitalOperationsTool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleOpsMeshTool(BaseTool):
    """Simple tool for interacting with the Ops Mesh system."""
    
    def __init__(self):
        super().__init__(
            name="simple_ops_mesh_tool",
            description="Simple tool for Ops Mesh hospital operations. Can provide basic system information and simulate operations."
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simple operations on the Ops Mesh system."""
        try:
            operation = parameters.get("operation", "")
            
            logger.info(f"Executing simple Ops Mesh operation: {operation}")
            
            if operation == "get_system_info":
                return {
                    "success": True,
                    "data": {
                        "system_name": "Ops Mesh Hospital Operations",
                        "version": "1.0.0",
                        "status": "operational",
                        "components": {
                            "backend_api": "running",
                            "database": "connected",
                            "agents": "active",
                            "websockets": "enabled"
                        }
                    }
                }
            
            elif operation == "get_queue_status":
                return {
                    "success": True,
                    "data": {
                        "total_waiting": 5,
                        "total_in_progress": 2,
                        "estimated_wait_time": 15,
                        "queue_types": {
                            "appointments": 3,
                            "walk_ins": 2
                        }
                    }
                }
            
            elif operation == "get_appointments":
                return {
                    "success": True,
                    "data": [
                        {
                            "id": 1,
                            "patient_name": "John Doe",
                            "time": "10:00 AM",
                            "status": "scheduled"
                        },
                        {
                            "id": 2,
                            "patient_name": "Jane Smith",
                            "time": "11:00 AM",
                            "status": "checked_in"
                        }
                    ]
                }
            
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            logger.error(f"Error in SimpleOpsMeshTool: {e}")
            return {"success": False, "error": str(e)}


class SimplePatientFlowTool(BaseTool):
    """Simple tool for managing patient flow."""
    
    def __init__(self):
        super().__init__(
            name="simple_patient_flow_tool",
            description="Simple tool for patient flow management. Can simulate check-ins and queue operations."
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simple patient flow operations."""
        try:
            action = parameters.get("action", "")
            patient_data = parameters.get("patient_data", {})
            
            logger.info(f"Executing simple patient flow action: {action}")
            
            if action == "check_in_patient":
                return {
                    "success": True,
                    "message": f"Patient {patient_data.get('name', 'Unknown')} checked in successfully",
                    "ticket_number": f"T{hash(str(patient_data)) % 10000:04d}",
                    "estimated_wait_time": 15
                }
            
            elif action == "get_wait_time":
                return {
                    "success": True,
                    "estimated_wait_time": 15,
                    "position_in_queue": 3,
                    "message": "Current wait time is approximately 15 minutes"
                }
            
            elif action == "call_next_patient":
                return {
                    "success": True,
                    "message": "Next patient called",
                    "patient_name": "John Doe",
                    "ticket_number": "T0001"
                }
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error in SimplePatientFlowTool: {e}")
            return {"success": False, "error": str(e)}


class SimpleSystemStatusTool(BaseTool):
    """Simple tool for checking system status."""
    
    def __init__(self):
        super().__init__(
            name="simple_system_status_tool",
            description="Simple tool for checking system status and health."
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Check simple system status."""
        try:
            component = parameters.get("component", "all")
            
            logger.info(f"Checking simple system status for: {component}")
            
            status = {
                "backend_api": "healthy",
                "database": "connected",
                "agents": "running",
                "websockets": "active",
                "adk_interface": "operational",
                "timestamp": "2025-09-27T17:00:00Z"
            }
            
            if component == "all":
                return {"success": True, "data": status}
            else:
                return {"success": True, "data": {component: status.get(component, "unknown")}}
                
        except Exception as e:
            logger.error(f"Error in SimpleSystemStatusTool: {e}")
            return {"success": False, "error": str(e)}


# Create the simple root agent with A2A tools
simple_root_agent = Agent(
    name="simple_ops_mesh_root_agent",
    model="gemini-1.5-flash",
    instruction="""
    You are the Ops Mesh Root Agent, responsible for coordinating hospital operations using A2A protocol.
    
    Your capabilities include:
    - Agent discovery and capability management
    - A2A communication and task coordination
    - Hospital operations management
    - Patient flow coordination
    - System monitoring and health checks
    
    Always be helpful, professional, and efficient when handling hospital operations.
    Use the available A2A tools to interact with the agent network and provide accurate information.
    
    When users ask about:
    - Agent discovery: Use the agent_discovery_tool to find available agents
    - A2A communication: Use the a2a_communication_tool for agent-to-agent tasks
    - Hospital operations: Use the hospital_operations_tool for system management
    - System status: Use hospital_operations_tool with operation "get_system_status"
    - Queue status: Use hospital_operations_tool with operation "get_queue_status"
    - Appointments: Use hospital_operations_tool with operation "get_appointments"
    - Emergency coordination: Use hospital_operations_tool with operation "emergency_coordination"
    
    Provide clear, actionable responses and always confirm successful operations.
    Leverage the A2A protocol for seamless agent coordination.
    """,
    tools=[
        AgentDiscoveryTool(),
        A2ACommunicationTool(),
        HospitalOperationsTool(),
        SimpleOpsMeshTool(),
        SimplePatientFlowTool(),
        SimpleSystemStatusTool()
    ]
)

# Export the simple root agent for ADK
__all__ = ["simple_root_agent"]
