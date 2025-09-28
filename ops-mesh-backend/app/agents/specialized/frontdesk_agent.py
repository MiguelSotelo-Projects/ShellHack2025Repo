"""
FrontDesk Agent

Handles patient registration, check-in, and initial patient flow coordination.
Uses A2A protocol for agent-to-agent communication.
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
from app.core.database import SessionLocal
from app.models.patient import Patient
from app.models.appointment import Appointment, AppointmentStatus

# Try to import Google ADK, fallback to internal implementation
try:
    from google.adk.agents import Agent
    from google.adk.tools import BaseTool
except ImportError:
    from ..google_adk_fallback import Agent, BaseTool

from ..protocol.a2a_protocol import A2AProtocol, A2ATaskRequest, TaskStatus

logger = logging.getLogger(__name__)


class PatientRegistrationTool(BaseTool):
    """Tool for patient registration and check-in."""
    
    def __init__(self, protocol: A2AProtocol):
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
                await self.protocol.send_task_request(
                    recipient_id="queue_agent",
                    action="add_to_queue",
                    data={
                        "patient_id": result.get("patient_id"),
                        "priority": patient_data.get("priority", "medium"),
                        "queue_type": "walk_in"
                    }
                )
                
                return result
                
            elif action == "check_in_patient":
                # Check in existing patient
                result = await self._check_in_patient(patient_data)
                
                # Notify queue agent about check-in
                await self.protocol.send_task_request(
                    recipient_id="queue_agent",
                    action="add_to_queue",
                    data={
                        "patient_id": result.get("patient_id"),
                        "appointment_id": result.get("appointment_id"),
                        "priority": "high",
                        "queue_type": "appointment"
                    }
                )
                
                return result
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error in patient registration: {e}")
            return {"success": False, "error": str(e)}
    
    async def _register_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new patient."""
        try:
            db = SessionLocal()
            
            # Create new patient
            patient = Patient(
                first_name=patient_data.get("first_name"),
                last_name=patient_data.get("last_name"),
                date_of_birth=datetime.fromisoformat(patient_data.get("date_of_birth")) if patient_data.get("date_of_birth") else None,
                phone=patient_data.get("phone"),
                email=patient_data.get("email"),
                emergency_contact=patient_data.get("emergency_contact"),
                medical_record_number=f"MRN-{int(asyncio.get_event_loop().time())}"
            )
            
            db.add(patient)
            db.commit()
            db.refresh(patient)
            
            logger.info(f"Registered new patient: {patient.id}")
            
            return {
                "success": True,
                "patient_id": patient.id,
                "medical_record_number": patient.medical_record_number,
                "message": "Patient registered successfully",
                "data": {
                    "first_name": patient.first_name,
                    "last_name": patient.last_name,
                    "medical_record_number": patient.medical_record_number
                }
            }
            
        except Exception as e:
            logger.error(f"Error registering patient: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to register patient"
            }
        finally:
            if 'db' in locals() and db:
                db.close()
    
    async def _check_in_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check in an existing patient."""
        try:
            db = SessionLocal()
            
            patient_id = patient_data.get("patient_id")
            appointment_id = patient_data.get("appointment_id")
            
            # Find the appointment
            appointment = db.query(Appointment).filter(
                Appointment.id == appointment_id,
                Appointment.patient_id == patient_id
            ).first()
            
            if not appointment:
                return {
                    "success": False,
                    "error": "Appointment not found",
                    "message": "Invalid appointment ID or patient ID"
                }
            
            # Update appointment status
            appointment.status = AppointmentStatus.CHECKED_IN
            appointment.check_in_time = datetime.now()
            
            db.commit()
            
            logger.info(f"Checked in patient {patient_id} for appointment {appointment_id}")
            
            return {
                "success": True,
                "patient_id": patient_id,
                "appointment_id": appointment_id,
                "confirmation_code": appointment.confirmation_code,
                "message": "Patient checked in successfully"
            }
            
        except Exception as e:
            logger.error(f"Error checking in patient: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to check in patient"
            }
        finally:
            if 'db' in locals() and db:
                db.close()


class FrontDeskAgent:
    """FrontDesk Agent for patient registration and check-in."""
    
    def __init__(self, project_id: str = None):
        self.agent_id = "frontdesk_agent"
        self.protocol = A2AProtocol(
            self.agent_id, 
            "ops-mesh-backend/agents/frontdesk_agent.json"
        )
        self.agent = None
        self.registration_tool = None
    
    async def initialize(self):
        """Initialize the agent and its tools."""
        await self.protocol.start()
        
        # Create tools
        self.registration_tool = PatientRegistrationTool(self.protocol)
        
        # Create ADK agent
        try:
            self.agent = Agent(
                name="FrontDesk Agent",
                description="Handles patient registration and check-in processes",
                tools=[self.registration_tool],
                model="gemini-1.5-flash"
            )
        except TypeError:
            # Fallback for internal Agent implementation
            self.agent = Agent(
                name="FrontDesk Agent",
                tools=[self.registration_tool]
            )
        
        # Register task handlers
        self.protocol.register_task_handler("register_patient", self._handle_register_patient)
        self.protocol.register_task_handler("check_in_patient", self._handle_check_in_patient)
        self.protocol.register_task_handler("verify_patient", self._handle_verify_patient)
        self.protocol.register_task_handler("lookup_appointment", self._handle_lookup_appointment)
        
        logger.info("FrontDesk Agent initialized")
    
    async def _handle_register_patient(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle patient registration task."""
        logger.info(f"FrontDesk Agent handling register_patient: {data}")
        return await self.registration_tool.execute({
            "action": "register_patient",
            "patient_data": data
        })
    
    async def _handle_check_in_patient(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle patient check-in task."""
        logger.info(f"FrontDesk Agent handling check_in_patient: {data}")
        return await self.registration_tool.execute({
            "action": "check_in_patient",
            "patient_data": data
        })
    
    async def _handle_verify_patient(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle patient verification task."""
        logger.info(f"FrontDesk Agent handling verify_patient: {data}")
        # Implement patient verification logic
        return {
            "success": True,
            "patient_id": data.get("patient_id"),
            "verified": True,
            "message": "Patient verified successfully"
        }
    
    async def _handle_lookup_appointment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle appointment lookup task."""
        logger.info(f"FrontDesk Agent handling lookup_appointment: {data}")
        # Implement appointment lookup logic
        return {
            "success": True,
            "appointment_id": data.get("appointment_id"),
            "appointment": {
                "id": data.get("appointment_id"),
                "patient_id": data.get("patient_id"),
                "status": "scheduled"
            },
            "message": "Appointment found"
        }
    
    async def start(self):
        """Start the agent."""
        if not self.agent:
            await self.initialize()
        
        logger.info("Starting FrontDesk Agent...")
    
    async def stop(self):
        """Stop the agent."""
        await self.protocol.stop()
        logger.info("FrontDesk Agent stopped")
