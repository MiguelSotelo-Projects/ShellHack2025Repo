"""
Appointment Agent

Handles appointment scheduling, management, and coordination.
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
from app.core.database import SessionLocal
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.patient import Patient

# Try to import Google ADK, fallback to internal implementation
try:
    from google.adk.agents import Agent
    from google.adk.tools import BaseTool
except ImportError:
    from ..google_adk_fallback import Agent, BaseTool

from ..protocol.a2a_protocol import A2AProtocol, A2ATaskRequest, TaskStatus
from ..protocol.agent_protocol import MessageType, Priority, ProtocolMessage

logger = logging.getLogger(__name__)


class AppointmentManagementTool(BaseTool):
    """Tool for appointment management operations."""
    
    def __init__(self, protocol: A2AProtocol):
        super().__init__(
            name="appointment_management_tool",
            description="Manages appointment scheduling and coordination"
        )
        self.protocol = protocol
    
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
        try:
            db = SessionLocal()
            
            patient_id = parameters.get("patient_id")
            provider = parameters.get("provider")
            appointment_time = parameters.get("appointment_time")
            appointment_type = parameters.get("type", "routine")
            reason = parameters.get("reason")
            
            # Create appointment
            appointment = Appointment(
                confirmation_code=f"APT-{int(asyncio.get_event_loop().time())}",
                patient_id=patient_id,
                provider_name=provider,
                appointment_type=AppointmentType(appointment_type),
                status=AppointmentStatus.SCHEDULED,
                scheduled_time=datetime.fromisoformat(appointment_time) if isinstance(appointment_time, str) else appointment_time,
                duration_minutes=parameters.get("duration_minutes", 30),
                reason=reason
            )
            
            db.add(appointment)
            db.commit()
            db.refresh(appointment)
            
            # Notify notification agent about new appointment
            await self.protocol.send_task_request(
                recipient_id="notification_agent",
                action="send_notification",
                data={
                    "event": "appointment_scheduled",
                    "patient_id": patient_id,
                    "appointment_id": appointment.id,
                    "confirmation_code": appointment.confirmation_code,
                    "appointment_time": appointment.scheduled_time.isoformat(),
                    "provider": provider
                }
            )
            
            logger.info(f"Scheduled appointment {appointment.id} for patient {patient_id}")
            
            return {
                "success": True,
                "appointment_id": appointment.id,
                "confirmation_code": appointment.confirmation_code,
                "message": "Appointment scheduled successfully"
            }
            
        except Exception as e:
            logger.error(f"Error scheduling appointment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to schedule appointment"
            }
        finally:
            db.close()
    
    async def _get_appointment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get appointment details."""
        try:
            db = SessionLocal()
            
            appointment_id = parameters.get("appointment_id")
            
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            
            if appointment:
                return {
                    "success": True,
                    "appointment": {
                        "id": appointment.id,
                        "confirmation_code": appointment.confirmation_code,
                        "patient_id": appointment.patient_id,
                        "provider_name": appointment.provider_name,
                        "appointment_type": appointment.appointment_type.value,
                        "status": appointment.status.value,
                        "scheduled_time": appointment.scheduled_time.isoformat(),
                        "duration_minutes": appointment.duration_minutes,
                        "reason": appointment.reason
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Appointment not found"
                }
                
        except Exception as e:
            logger.error(f"Error getting appointment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get appointment"
            }
        finally:
            db.close()
    
    async def _update_appointment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing appointment."""
        try:
            db = SessionLocal()
            
            appointment_id = parameters.get("appointment_id")
            updates = parameters.get("updates", {})
            
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            
            if appointment:
                # Update appointment fields
                for key, value in updates.items():
                    if hasattr(appointment, key):
                        setattr(appointment, key, value)
                
                db.commit()
                
                # Notify notification agent about appointment update
                await self.protocol.send_task_request(
                    recipient_id="notification_agent",
                    action="send_notification",
                    data={
                        "event": "appointment_updated",
                        "appointment_id": appointment_id,
                        "updates": updates
                    }
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
                
        except Exception as e:
            logger.error(f"Error updating appointment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update appointment"
            }
        finally:
            db.close()
    
    async def _cancel_appointment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel an appointment."""
        try:
            db = SessionLocal()
            
            appointment_id = parameters.get("appointment_id")
            reason = parameters.get("reason", "No reason provided")
            
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            
            if appointment:
                appointment.status = AppointmentStatus.CANCELLED
                appointment.notes = f"Cancelled: {reason}"
                
                db.commit()
                
                # Notify notification agent about appointment cancellation
                await self.protocol.send_task_request(
                    recipient_id="notification_agent",
                    action="send_alert",
                    data={
                        "event": "appointment_cancelled",
                        "appointment_id": appointment_id,
                        "reason": reason
                    }
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
                
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to cancel appointment"
            }
        finally:
            db.close()


class AppointmentAgent:
    """Appointment Agent for managing appointments."""
    
    def __init__(self, project_id: str = None):
        self.agent_id = "appointment_agent"
        self.protocol = A2AProtocol(
            self.agent_id, 
            "ops-mesh-backend/agents/appointment_agent.json"
        )
        self.agent = None
        self.appointment_tool = None
    
    async def initialize(self):
        """Initialize the agent and its tools."""
        await self.protocol.start()
        
        # Create tools
        self.appointment_tool = AppointmentManagementTool(self.protocol)
        
        # Create ADK agent
        try:
            self.agent = Agent(
                name="Appointment Agent",
                description="Manages appointment scheduling and coordination",
                tools=[self.appointment_tool],
                model="gemini-1.5-flash"
            )
        except TypeError:
            # Fallback for internal Agent implementation
            self.agent = Agent(
                name="Appointment Agent",
                tools=[self.appointment_tool]
            )
        
        # Register task handlers
        self.protocol.register_task_handler("schedule_appointment", self._handle_schedule_appointment)
        self.protocol.register_task_handler("get_appointment", self._handle_get_appointment)
        self.protocol.register_task_handler("update_appointment", self._handle_update_appointment)
        self.protocol.register_task_handler("cancel_appointment", self._handle_cancel_appointment)
        
        logger.info("Appointment Agent initialized")
    
    async def _handle_schedule_appointment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle schedule appointment task."""
        logger.info(f"Appointment Agent handling schedule_appointment: {data}")
        return await self.appointment_tool.execute({
            "action": "schedule_appointment",
            "patient_id": data.get("patient_id"),
            "provider": data.get("provider"),
            "appointment_time": data.get("appointment_time"),
            "type": data.get("type", "routine")
        })
    
    async def _handle_get_appointment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get appointment task."""
        logger.info(f"Appointment Agent handling get_appointment: {data}")
        return await self.appointment_tool.execute({
            "action": "get_appointment",
            "appointment_id": data.get("appointment_id")
        })
    
    async def _handle_update_appointment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update appointment task."""
        logger.info(f"Appointment Agent handling update_appointment: {data}")
        return await self.appointment_tool.execute({
            "action": "update_appointment",
            "appointment_id": data.get("appointment_id"),
            "updates": data.get("updates", {})
        })
    
    async def _handle_cancel_appointment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cancel appointment task."""
        logger.info(f"Appointment Agent handling cancel_appointment: {data}")
        return await self.appointment_tool.execute({
            "action": "cancel_appointment",
            "appointment_id": data.get("appointment_id"),
            "reason": data.get("reason", "No reason provided")
        })
    
    async def start(self):
        """Start the agent."""
        if not self.agent:
            await self.initialize()
        
        logger.info("Starting Appointment Agent...")
        
        logger.info("Appointment Agent started")
    
    async def stop(self):
        """Stop the agent."""
        await self.protocol.stop()
        logger.info("Appointment Agent stopped")
