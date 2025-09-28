from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..core.database import get_db
from ..models.patient import Patient
from ..models.appointment import Appointment, AppointmentStatus, AppointmentType
from ..models.queue import QueueEntry, QueueStatus, QueueType, QueuePriority
from ..schemas.patient import PatientCreate
from ..schemas.queue import WalkInRequest, QueueEntryResponse
from ..models.common import generate_ticket_number, generate_confirmation_code

router = APIRouter()


@router.post("/", response_model=dict)
def register_walkin(
    walkin_data: dict,
    db: Session = Depends(get_db)
):
    """Register a walk-in patient"""
    patient_data = walkin_data.get("patient")
    reason = walkin_data.get("reason", "Walk-in consultation")
    priority = walkin_data.get("priority", QueuePriority.MEDIUM)
    
    if not patient_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient data is required"
        )
    
    # Create or find patient
    patient = db.query(Patient).filter(
        Patient.first_name.ilike(patient_data.get("first_name", "")),
        Patient.last_name.ilike(patient_data.get("last_name", ""))
    ).first()
    
    if not patient:
        # Create new patient - convert date_of_birth string to datetime
        patient_dict = patient_data.copy()
        if "date_of_birth" in patient_dict and isinstance(patient_dict["date_of_birth"], str):
            patient_dict["date_of_birth"] = datetime.fromisoformat(patient_dict["date_of_birth"])
        
        patient = Patient(**patient_dict)
        db.add(patient)
        db.commit()
        db.refresh(patient)
    
    # Create appointment for walk-in
    appointment = Appointment(
        confirmation_code=generate_confirmation_code(),
        patient_id=patient.id,
        provider_name="Walk-in Provider",
        appointment_type=AppointmentType.ROUTINE,
        status=AppointmentStatus.SCHEDULED,
        scheduled_time=datetime.utcnow(),
        reason=reason
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    # Create queue entry
    ticket_number = generate_ticket_number()
    while db.query(QueueEntry).filter(QueueEntry.ticket_number == ticket_number).first():
        ticket_number = generate_ticket_number()
    
    queue_entry = QueueEntry(
        ticket_number=ticket_number,
        patient_id=patient.id,
        appointment_id=appointment.id,
        queue_type=QueueType.WALK_IN,
        status=QueueStatus.WAITING,
        priority=priority,
        reason=reason,
        estimated_wait_time=30
    )
    db.add(queue_entry)
    db.commit()
    db.refresh(queue_entry)
    
    return {
        "patient_id": patient.id,
        "appointment_id": appointment.id,
        "queue_entry_id": queue_entry.id,
        "ticket_number": ticket_number,
        "confirmation_code": appointment.confirmation_code,
        "reason": reason,
        "priority": priority
    }


@router.get("/queue", response_model=List[QueueEntryResponse])
def get_walkin_queue(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get walk-in queue"""
    query = db.query(QueueEntry).filter(
        QueueEntry.queue_type == QueueType.WALK_IN
    ).order_by(
        QueueEntry.priority.desc(),
        QueueEntry.created_at.asc()
    )
    
    queue_entries = query.offset(skip).limit(limit).all()
    
    result = []
    for entry in queue_entries:
        patient_name = None
        if entry.patient:
            patient_name = f"{entry.patient.first_name} {entry.patient.last_name}"
        
        result.append(QueueEntryResponse(
            id=entry.id,
            ticket_number=entry.ticket_number,
            status=entry.status,
            queue_type=entry.queue_type,
            priority=entry.priority,
            reason=entry.reason,
            estimated_wait_time=entry.estimated_wait_time,
            patient_name=patient_name,
            appointment_code=entry.appointment.confirmation_code if entry.appointment else None,
            created_at=entry.created_at
        ))
    
    return result


@router.post("/{appointment_id}/process", response_model=dict)
def process_walkin(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Process a walk-in appointment"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.status == AppointmentStatus.SCHEDULED
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walk-in appointment not found or already processed"
        )
    
    # Update appointment status
    appointment.status = AppointmentStatus.IN_PROGRESS
    
    # Update queue entry if exists
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.appointment_id == appointment_id
    ).first()
    
    if queue_entry:
        queue_entry.status = QueueStatus.IN_PROGRESS
        queue_entry.started_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "appointment_id": appointment_id,
        "status": "in_progress",
        "processed_at": datetime.utcnow()
    }


@router.get("/{appointment_id}/wait-time", response_model=dict)
def get_walkin_wait_time(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Get estimated wait time for walk-in"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Count patients ahead in queue
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.appointment_id == appointment_id
    ).first()
    
    if not queue_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue entry not found"
        )
    
    # Count patients ahead with same or higher priority
    patients_ahead = db.query(QueueEntry).filter(
        QueueEntry.status == QueueStatus.WAITING,
        QueueEntry.queue_type == QueueType.WALK_IN,
        QueueEntry.priority >= queue_entry.priority,
        QueueEntry.created_at < queue_entry.created_at
    ).count()
    
    estimated_wait_time = patients_ahead * 15  # 15 minutes per patient
    
    return {
        "appointment_id": appointment_id,
        "position_in_queue": patients_ahead + 1,
        "estimated_wait_time": estimated_wait_time
    }


@router.put("/{appointment_id}/status", response_model=dict)
def update_walkin_status(
    appointment_id: int,
    status_data: dict,
    db: Session = Depends(get_db)
):
    """Update walk-in status"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    new_status = status_data.get("status")
    if new_status:
        appointment.status = new_status
    
    # Update queue entry if exists
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.appointment_id == appointment_id
    ).first()
    
    if queue_entry and new_status:
        if new_status == AppointmentStatus.IN_PROGRESS:
            queue_entry.status = QueueStatus.IN_PROGRESS
            queue_entry.started_at = datetime.utcnow()
        elif new_status == AppointmentStatus.COMPLETED:
            queue_entry.status = QueueStatus.COMPLETED
            queue_entry.completed_at = datetime.utcnow()
        elif new_status == AppointmentStatus.CANCELLED:
            queue_entry.status = QueueStatus.CANCELLED
    
    db.commit()
    
    return {
        "appointment_id": appointment_id,
        "status": appointment.status
    }


@router.post("/{appointment_id}/cancel", response_model=dict)
def cancel_walkin(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Cancel a walk-in appointment"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment already cancelled"
        )
    
    appointment.status = AppointmentStatus.CANCELLED
    
    # Update queue entry if exists
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.appointment_id == appointment_id
    ).first()
    
    if queue_entry:
        queue_entry.status = QueueStatus.CANCELLED
    
    db.commit()
    
    return {
        "appointment_id": appointment_id,
        "status": "cancelled"
    }


@router.post("/{appointment_id}/complete", response_model=dict)
def complete_walkin(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Complete a walk-in appointment"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    if appointment.status != AppointmentStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment is not in progress"
        )
    
    appointment.status = AppointmentStatus.COMPLETED
    
    # Update queue entry if exists
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.appointment_id == appointment_id
    ).first()
    
    if queue_entry:
        queue_entry.status = QueueStatus.COMPLETED
        queue_entry.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "appointment_id": appointment_id,
        "status": "completed",
        "completed_at": datetime.utcnow()
    }
