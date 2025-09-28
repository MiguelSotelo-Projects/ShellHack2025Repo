"""
Hospital Queue Agent using Google ADK

This agent manages patient queues, wait times, and queue optimization
using the real Google ADK implementation with A2A protocol.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from ...core.database import SessionLocal
from ...models.patient import Patient
from ...models.appointment import Appointment
from ...models.queue import QueueEntry, QueueStatus
from ..google_adk import Agent, BaseTool, ToolContext, tool
from ..google_adk.protocol import AgentCard, TaskRequest, TaskResponse, TaskStatus

logger = logging.getLogger(__name__)


@tool(
    name="get_queue_status",
    description="Get current queue status and statistics",
    parameters_schema={
        "type": "object",
        "properties": {
            "department": {"type": "string", "description": "Filter by department"},
            "status": {"type": "string", "enum": ["waiting", "in_progress", "completed", "cancelled"], "description": "Filter by queue status"}
        }
    }
)
async def get_queue_status_tool(
    department: Optional[str] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """Get current queue status and statistics."""
    db = SessionLocal()
    try:
        query = db.query(QueueEntry)
        
        # Apply filters
        if department:
            query = query.join(Appointment).filter(Appointment.department == department)
        
        if status:
            query = query.filter(QueueEntry.status == QueueStatus(status))
        
        # Get queue entries
        queue_entries = query.all()
        
        # Calculate statistics
        total_patients = len(queue_entries)
        waiting_patients = len([q for q in queue_entries if q.status == QueueStatus.WAITING])
        in_progress_patients = len([q for q in queue_entries if q.status == QueueStatus.IN_PROGRESS])
        
        # Calculate average wait time
        waiting_entries = [q for q in queue_entries if q.status == QueueStatus.WAITING]
        avg_wait_time = 0
        if waiting_entries:
            total_wait = sum(q.estimated_wait_time or 0 for q in waiting_entries)
            avg_wait_time = total_wait / len(waiting_entries)
        
        # Get next patients to be called
        next_patients = []
        for entry in waiting_entries[:5]:  # Next 5 patients
            patient = db.query(Patient).filter(Patient.id == entry.patient_id).first()
            appointment = db.query(Appointment).filter(Appointment.id == entry.appointment_id).first()
            
            if patient and appointment:
                next_patients.append({
                    "queue_id": entry.id,
                    "patient_name": f"{patient.first_name} {patient.last_name}",
                    "appointment_time": appointment.appointment_time.isoformat(),
                    "estimated_wait": entry.estimated_wait_time,
                    "department": appointment.department
                })
        
        return {
            "success": True,
            "queue_stats": {
                "total_patients": total_patients,
                "waiting": waiting_patients,
                "in_progress": in_progress_patients,
                "average_wait_time": round(avg_wait_time, 1)
            },
            "next_patients": next_patients,
            "filters": {
                "department": department,
                "status": status
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Get queue status failed: {e}")
        return {
            "success": False,
            "message": f"Failed to get queue status: {str(e)}",
            "error": str(e)
        }
    finally:
        db.close()


@tool(
    name="call_next_patient",
    description="Call the next patient in the queue",
    parameters_schema={
        "type": "object",
        "properties": {
            "department": {"type": "string", "description": "Department to call from"},
            "provider_name": {"type": "string", "description": "Name of the provider calling the patient"}
        },
        "required": ["department"]
    }
)
async def call_next_patient_tool(
    department: str,
    provider_name: Optional[str] = None
) -> Dict[str, Any]:
    """Call the next patient in the queue."""
    db = SessionLocal()
    try:
        # Find the next patient in the queue for this department
        next_entry = db.query(QueueEntry).join(Appointment).filter(
            Appointment.department == department,
            QueueEntry.status == QueueStatus.WAITING
        ).order_by(QueueEntry.created_at.asc()).first()
        
        if not next_entry:
            return {
                "success": False,
                "message": f"No patients waiting in {department} queue",
                "error": "NO_PATIENTS_WAITING"
            }
        
        # Update queue entry status
        next_entry.status = QueueStatus.IN_PROGRESS
        next_entry.called_at = datetime.utcnow()
        next_entry.called_by = provider_name or "System"
        
        # Get patient and appointment info
        patient = db.query(Patient).filter(Patient.id == next_entry.patient_id).first()
        appointment = db.query(Appointment).filter(Appointment.id == next_entry.appointment_id).first()
        
        db.commit()
        
        logger.info(f"✅ Called next patient in {department}: {patient.first_name} {patient.last_name}")
        
        return {
            "success": True,
            "message": f"Patient called successfully",
            "patient": {
                "queue_id": next_entry.id,
                "patient_id": patient.id,
                "name": f"{patient.first_name} {patient.last_name}",
                "phone": patient.phone
            },
            "appointment": {
                "id": appointment.id,
                "time": appointment.appointment_time.isoformat(),
                "provider": appointment.provider_name,
                "department": appointment.department
            },
            "queue_info": {
                "called_at": next_entry.called_at.isoformat(),
                "called_by": next_entry.called_by
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Call next patient failed: {e}")
        return {
            "success": False,
            "message": f"Failed to call next patient: {str(e)}",
            "error": str(e)
        }
    finally:
        db.close()


@tool(
    name="complete_patient_visit",
    description="Mark a patient's visit as completed",
    parameters_schema={
        "type": "object",
        "properties": {
            "queue_id": {"type": "integer", "description": "Queue entry ID"},
            "visit_notes": {"type": "string", "description": "Notes about the visit"},
            "next_appointment": {"type": "string", "format": "date", "description": "Date for next appointment if needed"}
        },
        "required": ["queue_id"]
    }
)
async def complete_patient_visit_tool(
    queue_id: int,
    visit_notes: Optional[str] = None,
    next_appointment: Optional[str] = None
) -> Dict[str, Any]:
    """Mark a patient's visit as completed."""
    db = SessionLocal()
    try:
        # Get queue entry
        queue_entry = db.query(QueueEntry).filter(QueueEntry.id == queue_id).first()
        
        if not queue_entry:
            return {
                "success": False,
                "message": "Queue entry not found",
                "error": "QUEUE_ENTRY_NOT_FOUND"
            }
        
        if queue_entry.status != QueueStatus.IN_PROGRESS:
            return {
                "success": False,
                "message": "Patient is not currently in progress",
                "error": "INVALID_STATUS"
            }
        
        # Update queue entry
        queue_entry.status = QueueStatus.COMPLETED
        queue_entry.completed_at = datetime.utcnow()
        queue_entry.visit_notes = visit_notes
        
        # Calculate actual wait time
        if queue_entry.called_at:
            actual_wait_time = (queue_entry.called_at - queue_entry.created_at).total_seconds() / 60
            queue_entry.actual_wait_time = round(actual_wait_time, 1)
        
        # Get patient and appointment info
        patient = db.query(Patient).filter(Patient.id == queue_entry.patient_id).first()
        appointment = db.query(Appointment).filter(Appointment.id == queue_entry.appointment_id).first()
        
        # Update appointment status
        appointment.status = "completed"
        
        db.commit()
        
        logger.info(f"✅ Completed visit for patient {patient.first_name} {patient.last_name}")
        
        result = {
            "success": True,
            "message": "Patient visit completed successfully",
            "patient": {
                "id": patient.id,
                "name": f"{patient.first_name} {patient.last_name}"
            },
            "visit_info": {
                "queue_id": queue_entry.id,
                "completed_at": queue_entry.completed_at.isoformat(),
                "actual_wait_time": queue_entry.actual_wait_time,
                "visit_notes": visit_notes
            }
        }
        
        # Add next appointment info if provided
        if next_appointment:
            result["next_appointment"] = {
                "suggested_date": next_appointment,
                "message": "Next appointment recommended"
            }
        
        return result
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Complete patient visit failed: {e}")
        return {
            "success": False,
            "message": f"Failed to complete visit: {str(e)}",
            "error": str(e)
        }
    finally:
        db.close()


@tool(
    name="optimize_queue",
    description="Optimize queue by adjusting wait times and priorities",
    parameters_schema={
        "type": "object",
        "properties": {
            "department": {"type": "string", "description": "Department to optimize"},
            "max_wait_time": {"type": "integer", "description": "Maximum acceptable wait time in minutes"}
        }
    }
)
async def optimize_queue_tool(
    department: Optional[str] = None,
    max_wait_time: int = 30
) -> Dict[str, Any]:
    """Optimize queue by adjusting wait times and priorities."""
    db = SessionLocal()
    try:
        query = db.query(QueueEntry).filter(QueueEntry.status == QueueStatus.WAITING)
        
        if department:
            query = query.join(Appointment).filter(Appointment.department == department)
        
        waiting_entries = query.all()
        
        if not waiting_entries:
            return {
                "success": True,
                "message": "No patients waiting in queue",
                "optimizations": []
            }
        
        optimizations = []
        current_time = datetime.utcnow()
        
        for entry in waiting_entries:
            # Calculate how long patient has been waiting
            wait_duration = (current_time - entry.created_at).total_seconds() / 60
            
            # If patient has been waiting too long, prioritize them
            if wait_duration > max_wait_time:
                # Reduce estimated wait time for long-waiting patients
                new_wait_time = max(5, entry.estimated_wait_time - 10)
                entry.estimated_wait_time = new_wait_time
                
                optimizations.append({
                    "queue_id": entry.id,
                    "patient_id": entry.patient_id,
                    "action": "prioritized",
                    "old_wait_time": entry.estimated_wait_time + 10,
                    "new_wait_time": new_wait_time,
                    "reason": f"Patient waiting {wait_duration:.1f} minutes"
                })
        
        db.commit()
        
        logger.info(f"✅ Optimized queue with {len(optimizations)} adjustments")
        
        return {
            "success": True,
            "message": f"Queue optimized with {len(optimizations)} adjustments",
            "optimizations": optimizations,
            "total_patients": len(waiting_entries)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Queue optimization failed: {e}")
        return {
            "success": False,
            "message": f"Queue optimization failed: {str(e)}",
            "error": str(e)
        }
    finally:
        db.close()


class QueueAgent:
    """
    Hospital Queue Agent using Google ADK.
    
    Manages patient queues, wait times, and queue optimization.
    """
    
    def __init__(self):
        """Initialize the Queue Agent."""
        self.name = "queue_agent"
        self.description = "Hospital queue management agent for patient flow optimization"
        
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
                    "id": "queue_status",
                    "name": "Queue Status Monitoring",
                    "description": "Monitor queue status and statistics",
                    "tags": ["queue", "monitoring", "statistics"],
                    "examples": [
                        "Show me the current queue status",
                        "How many patients are waiting in cardiology?"
                    ]
                },
                {
                    "id": "call_patient",
                    "name": "Call Next Patient",
                    "description": "Call the next patient in the queue",
                    "tags": ["queue", "calling", "patient"],
                    "examples": [
                        "Call the next patient in cardiology",
                        "Who is next in the queue?"
                    ]
                },
                {
                    "id": "complete_visit",
                    "name": "Complete Patient Visit",
                    "description": "Mark a patient's visit as completed",
                    "tags": ["completion", "visit", "queue"],
                    "examples": [
                        "Complete the visit for patient in room 5",
                        "Mark patient visit as done"
                    ]
                },
                {
                    "id": "optimize_queue",
                    "name": "Queue Optimization",
                    "description": "Optimize queue by adjusting wait times and priorities",
                    "tags": ["optimization", "queue", "efficiency"],
                    "examples": [
                        "Optimize the cardiology queue",
                        "Reduce wait times for long-waiting patients"
                    ]
                }
            ]
        )
        
        # Create ADK agent
        self.agent = Agent(
            name=self.name,
            description=self.description,
            model="gemini-1.5-flash",
            instruction="You are a hospital queue management agent. Help optimize patient flow, manage wait times, and ensure efficient queue operations. Focus on patient satisfaction and operational efficiency.",
            tools=[
                get_queue_status_tool,
                call_next_patient_tool,
                complete_patient_visit_tool,
                optimize_queue_tool
            ],
            agent_card=self.agent_card
        )
        
        logger.info(f"✅ Initialized Queue Agent: {self.name}")
    
    async def start(self) -> None:
        """Start the Queue Agent."""
        await self.agent.start()
        logger.info(f"🚀 Queue Agent started: {self.name}")
    
    async def stop(self) -> None:
        """Stop the Queue Agent."""
        await self.agent.stop()
        logger.info(f"🛑 Queue Agent stopped: {self.name}")
    
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
queue_agent = QueueAgent()
