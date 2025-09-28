"""
Hospital FrontDesk Agent using Google ADK

This agent handles patient registration, check-in, and initial patient flow coordination
using the real Google ADK implementation with A2A protocol.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ...core.database import SessionLocal
from ...models.patient import Patient
from ...models.appointment import Appointment, AppointmentStatus
from ...models.queue import QueueEntry, QueueStatus
from ..google_adk import Agent, BaseTool, ToolContext, tool
from ..google_adk.protocol import AgentCard, TaskRequest, TaskResponse, TaskStatus

logger = logging.getLogger(__name__)


@tool(
    name="patient_registration",
    description="Register a new patient in the hospital system",
    parameters_schema={
        "type": "object",
        "properties": {
            "first_name": {"type": "string", "description": "Patient's first name"},
            "last_name": {"type": "string", "description": "Patient's last name"},
            "date_of_birth": {"type": "string", "format": "date", "description": "Patient's date of birth"},
            "phone": {"type": "string", "description": "Patient's phone number"},
            "email": {"type": "string", "format": "email", "description": "Patient's email address"},
            "insurance_provider": {"type": "string", "description": "Insurance provider name"},
            "insurance_number": {"type": "string", "description": "Insurance policy number"}
        },
        "required": ["first_name", "last_name", "date_of_birth", "phone"]
    }
)
async def patient_registration_tool(
    first_name: str,
    last_name: str,
    date_of_birth: str,
    phone: str,
    email: Optional[str] = None,
    insurance_provider: Optional[str] = None,
    insurance_number: Optional[str] = None
) -> Dict[str, Any]:
    """Register a new patient in the hospital system."""
    db = SessionLocal()
    try:
        # Check if patient already exists
        existing_patient = db.query(Patient).filter(
            Patient.first_name == first_name,
            Patient.last_name == last_name,
            Patient.date_of_birth == datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        ).first()
        
        if existing_patient:
            return {
                "success": False,
                "message": "Patient already exists",
                "patient_id": existing_patient.id,
                "existing": True
            }
        
        # Create new patient
        patient = Patient(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d"),
            phone=phone,
            email=email,
            insurance_id=insurance_number  # Map to existing field
        )
        
        db.add(patient)
        db.commit()
        db.refresh(patient)
        
        logger.info(f"✅ Registered new patient: {patient.id}")
        
        return {
            "success": True,
            "message": "Patient registered successfully",
            "patient_id": patient.id,
            "patient": {
                "id": patient.id,
                "name": f"{patient.first_name} {patient.last_name}",
                "phone": patient.phone,
                "email": patient.email
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Patient registration failed: {e}")
        return {
            "success": False,
            "message": f"Registration failed: {str(e)}",
            "error": str(e)
        }
    finally:
        db.close()


@tool(
    name="patient_checkin",
    description="Check in a patient for their appointment",
    parameters_schema={
        "type": "object",
        "properties": {
            "patient_id": {"type": "integer", "description": "Patient ID"},
            "appointment_id": {"type": "integer", "description": "Appointment ID"},
            "confirmation_code": {"type": "string", "description": "Appointment confirmation code"}
        },
        "required": ["patient_id", "appointment_id"]
    }
)
async def patient_checkin_tool(
    patient_id: int,
    appointment_id: int,
    confirmation_code: Optional[str] = None
) -> Dict[str, Any]:
    """Check in a patient for their appointment."""
    db = SessionLocal()
    try:
        # Get patient and appointment
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not patient:
            return {
                "success": False,
                "message": "Patient not found",
                "error": "INVALID_PATIENT"
            }
        
        if not appointment:
            return {
                "success": False,
                "message": "Appointment not found",
                "error": "INVALID_APPOINTMENT"
            }
        
        # Verify appointment belongs to patient
        if appointment.patient_id != patient_id:
            return {
                "success": False,
                "message": "Appointment does not belong to patient",
                "error": "APPOINTMENT_MISMATCH"
            }
        
        # Check if appointment is today
        today = datetime.utcnow().date()
        if appointment.appointment_date != today:
            return {
                "success": False,
                "message": "Appointment is not scheduled for today",
                "error": "WRONG_DATE"
            }
        
        # Update appointment status
        appointment.status = AppointmentStatus.CHECKED_IN
        appointment.checked_in_at = datetime.utcnow()
        
        # Create queue entry
        queue_entry = QueueEntry(
            patient_id=patient_id,
            appointment_id=appointment_id,
            status=QueueStatus.WAITING,
            estimated_wait_time=15,  # Default 15 minutes
            created_at=datetime.utcnow()
        )
        
        db.add(queue_entry)
        db.commit()
        db.refresh(queue_entry)
        
        logger.info(f"✅ Patient {patient_id} checked in for appointment {appointment_id}")
        
        return {
            "success": True,
            "message": "Patient checked in successfully",
            "queue_entry": {
                "id": queue_entry.id,
                "estimated_wait_time": queue_entry.estimated_wait_time,
                "status": queue_entry.status.value
            },
            "appointment": {
                "id": appointment.id,
                "time": appointment.appointment_time.isoformat(),
                "provider": appointment.provider_name,
                "department": appointment.department
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Patient check-in failed: {e}")
        return {
            "success": False,
            "message": f"Check-in failed: {str(e)}",
            "error": str(e)
        }
    finally:
        db.close()


@tool(
    name="get_patient_info",
    description="Retrieve patient information by ID or name",
    parameters_schema={
        "type": "object",
        "properties": {
            "patient_id": {"type": "integer", "description": "Patient ID"},
            "first_name": {"type": "string", "description": "Patient's first name"},
            "last_name": {"type": "string", "description": "Patient's last name"},
            "phone": {"type": "string", "description": "Patient's phone number"}
        }
    }
)
async def get_patient_info_tool(
    patient_id: Optional[int] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieve patient information."""
    db = SessionLocal()
    try:
        query = db.query(Patient)
        
        if patient_id:
            query = query.filter(Patient.id == patient_id)
        elif first_name and last_name:
            query = query.filter(
                Patient.first_name.ilike(f"%{first_name}%"),
                Patient.last_name.ilike(f"%{last_name}%")
            )
        elif phone:
            query = query.filter(Patient.phone == phone)
        else:
            return {
                "success": False,
                "message": "Please provide patient ID, name, or phone number",
                "error": "INSUFFICIENT_PARAMETERS"
            }
        
        patients = query.all()
        
        if not patients:
            return {
                "success": False,
                "message": "No patients found",
                "error": "PATIENT_NOT_FOUND"
            }
        
        patient_data = []
        for patient in patients:
            patient_data.append({
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "date_of_birth": patient.date_of_birth.isoformat(),
                "phone": patient.phone,
                "email": patient.email,
                "insurance_provider": patient.insurance_provider,
                "created_at": patient.created_at.isoformat()
            })
        
        return {
            "success": True,
            "patients": patient_data,
            "count": len(patient_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Get patient info failed: {e}")
        return {
            "success": False,
            "message": f"Failed to retrieve patient info: {str(e)}",
            "error": str(e)
        }
    finally:
        db.close()


class FrontDeskAgent:
    """
    Hospital FrontDesk Agent using Google ADK.
    
    Handles patient registration, check-in, and information retrieval.
    """
    
    def __init__(self):
        """Initialize the FrontDesk Agent."""
        self.name = "frontdesk_agent"
        self.description = "Hospital front desk agent for patient registration and check-in"
        
        # Create agent card
        self.agent_card = AgentCard(
            name=self.name,
            description=self.description,
            version="1.0.0",
            capabilities={
                "streaming": True,
                "functions": True
            },
            default_input_modes=["text/plain", "application/json"],
            default_output_modes=["application/json"],
            skills=[
                {
                    "id": "patient_registration",
                    "name": "Patient Registration",
                    "description": "Register new patients in the hospital system",
                    "tags": ["registration", "patient", "frontdesk"],
                    "examples": [
                        "Register a new patient named John Doe",
                        "Create a patient record with insurance information"
                    ]
                },
                {
                    "id": "patient_checkin",
                    "name": "Patient Check-in",
                    "description": "Check in patients for their appointments",
                    "tags": ["checkin", "appointment", "frontdesk"],
                    "examples": [
                        "Check in patient for appointment",
                        "Verify appointment and create queue entry"
                    ]
                },
                {
                    "id": "patient_lookup",
                    "name": "Patient Information Lookup",
                    "description": "Retrieve patient information by various criteria",
                    "tags": ["lookup", "patient", "information"],
                    "examples": [
                        "Find patient by name",
                        "Get patient information by phone number"
                    ]
                }
            ]
        )
        
        # Create ADK agent
        self.agent = Agent(
            name=self.name,
            description=self.description,
            model="gemini-1.5-flash",
            instruction="You are a hospital front desk agent. Help patients with registration, check-in, and information retrieval. Be professional and helpful.",
            tools=[
                patient_registration_tool,
                patient_checkin_tool,
                get_patient_info_tool
            ],
            agent_card=self.agent_card
        )
        
        logger.info(f"✅ Initialized FrontDesk Agent: {self.name}")
    
    async def start(self) -> None:
        """Start the FrontDesk Agent."""
        await self.agent.start()
        logger.info(f"🚀 FrontDesk Agent started: {self.name}")
    
    async def stop(self) -> None:
        """Stop the FrontDesk Agent."""
        await self.agent.stop()
        logger.info(f"🛑 FrontDesk Agent stopped: {self.name}")
    
    async def process_task(self, task_request: TaskRequest) -> TaskResponse:
        """Process a task request."""
        return await self.agent.process_task(task_request)
    
    def get_agent_card(self) -> AgentCard:
        """Get the agent card."""
        return self.agent_card
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return self.agent.get_status()


# Create global instance
frontdesk_agent = FrontDeskAgent()
