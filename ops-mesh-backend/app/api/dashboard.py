from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..core.database import get_db
from ..models.patient import Patient
from ..models.queue import QueueEntry, QueueStatus
from ..models.appointment import Appointment, AppointmentStatus
from sqlalchemy import func

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        # Get total patients
        total_patients = db.query(Patient).count()
        
        # Get patients served (completed appointments)
        patients_served = db.query(Appointment).filter(
            Appointment.status == AppointmentStatus.COMPLETED
        ).count()
        
        # Get queue statistics
        queue_waiting = db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING
        ).count()
        
        queue_in_progress = db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.IN_PROGRESS
        ).count()
        
        # Calculate average wait time
        avg_wait_result = db.query(func.avg(QueueEntry.estimated_wait_time)).filter(
            QueueEntry.status == QueueStatus.WAITING
        ).scalar()
        
        average_wait_time = int(avg_wait_result) if avg_wait_result else 0
        
        return {
            "success": True,
            "total_patients": total_patients,
            "patients_served": patients_served,
            "queue_waiting": queue_waiting,
            "queue_in_progress": queue_in_progress,
            "average_wait_time": average_wait_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity")
async def get_dashboard_activity(db: Session = Depends(get_db)):
    """Get recent dashboard activity"""
    try:
        # Get recent patients
        recent_patients = db.query(Patient).order_by(
            Patient.created_at.desc()
        ).limit(10).all()
        
        # Get recent queue entries
        recent_queue_entries = db.query(QueueEntry).order_by(
            QueueEntry.created_at.desc()
        ).limit(10).all()
        
        return {
            "success": True,
            "recent_patients": [
                {
                    "id": p.id,
                    "name": f"{p.first_name} {p.last_name}",
                    "created_at": p.created_at.isoformat(),
                    "medical_record_number": p.medical_record_number
                }
                for p in recent_patients
            ],
            "recent_queue_entries": [
                {
                    "id": q.id,
                    "ticket_number": q.ticket_number,
                    "status": q.status.value,
                    "priority": q.priority.value,
                    "created_at": q.created_at.isoformat()
                }
                for q in recent_queue_entries
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))