from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..core.database import get_db
from ..models.patient import Patient
from ..models.appointment import Appointment, AppointmentStatus
from ..models.queue import QueueEntry, QueueStatus, QueueType
from ..schemas.appointment import AppointmentCheckIn

router = APIRouter()


@router.post("/appointment", response_model=dict)
def checkin_appointment(
    checkin_data: AppointmentCheckIn,
    db: Session = Depends(get_db)
):
    """Check in an appointment using confirmation code and last name"""
    # Find appointment by confirmation code
    appointment = db.query(Appointment).filter(
        Appointment.confirmation_code == checkin_data.confirmation_code
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verify last name matches
    if appointment.patient.last_name.lower() != checkin_data.last_name.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last name does not match"
        )
    
    # Check if already checked in
    if appointment.status == AppointmentStatus.CHECKED_IN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment already checked in"
        )
    
    # Check if appointment is cancelled or completed
    if appointment.status in [AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot check in cancelled or completed appointment"
        )
    
    # Update appointment status
    appointment.status = AppointmentStatus.CHECKED_IN
    appointment.check_in_time = datetime.utcnow()
    
    # Create or update queue entry
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.appointment_id == appointment.id
    ).first()
    
    if not queue_entry:
        # Create new queue entry for appointment
        from ..models.common import generate_ticket_number
        ticket_number = generate_ticket_number()
        while db.query(QueueEntry).filter(QueueEntry.ticket_number == ticket_number).first():
            ticket_number = generate_ticket_number()
        
        queue_entry = QueueEntry(
            ticket_number=ticket_number,
            patient_id=appointment.patient_id,
            appointment_id=appointment.id,
            queue_type=QueueType.APPOINTMENT,
            status=QueueStatus.WAITING,
            reason=appointment.reason
        )
        db.add(queue_entry)
    else:
        # Update existing queue entry
        queue_entry.status = QueueStatus.WAITING
    
    db.commit()
    db.refresh(appointment)
    db.refresh(queue_entry)
    
    return {
        "appointment_id": appointment.id,
        "confirmation_code": appointment.confirmation_code,
        "status": "checked_in",
        "check_in_time": appointment.check_in_time,
        "ticket_number": queue_entry.ticket_number,
        "patient_name": f"{appointment.patient.first_name} {appointment.patient.last_name}",
        "provider_name": appointment.provider_name,
        "scheduled_time": appointment.scheduled_time
    }


@router.post("/walkin", response_model=dict)
def checkin_walkin(
    patient_data: dict,
    db: Session = Depends(get_db)
):
    """Check in a walk-in patient"""
    first_name = patient_data.get("first_name")
    last_name = patient_data.get("last_name")
    reason = patient_data.get("reason", "Walk-in consultation")
    
    if not first_name or not last_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="First name and last name are required"
        )
    
    # Create or find patient
    patient = db.query(Patient).filter(
        Patient.first_name.ilike(first_name),
        Patient.last_name.ilike(last_name)
    ).first()
    
    if not patient:
        # Create new patient
        patient = Patient(
            first_name=first_name,
            last_name=last_name,
            phone=patient_data.get("phone"),
            email=patient_data.get("email")
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
    
    # Create appointment for walk-in
    from ..models.common import generate_confirmation_code
    appointment = Appointment(
        confirmation_code=generate_confirmation_code(),
        patient_id=patient.id,
        provider_name="Walk-in Provider",
        status=AppointmentStatus.SCHEDULED,
        scheduled_time=datetime.utcnow(),
        reason=reason
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    # Create queue entry
    from ..models.common import generate_ticket_number
    ticket_number = generate_ticket_number()
    while db.query(QueueEntry).filter(QueueEntry.ticket_number == ticket_number).first():
        ticket_number = generate_ticket_number()
    
    queue_entry = QueueEntry(
        ticket_number=ticket_number,
        patient_id=patient.id,
        appointment_id=appointment.id,
        queue_type=QueueType.WALK_IN,
        status=QueueStatus.WAITING,
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
        "status": "checked_in",
        "check_in_time": datetime.utcnow(),
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "reason": reason
    }


@router.get("/status/{confirmation_code}", response_model=dict)
def get_checkin_status(
    confirmation_code: str,
    db: Session = Depends(get_db)
):
    """Get check-in status by confirmation code"""
    appointment = db.query(Appointment).filter(
        Appointment.confirmation_code == confirmation_code
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Get queue entry if exists
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.appointment_id == appointment.id
    ).first()
    
    return {
        "appointment_id": appointment.id,
        "confirmation_code": appointment.confirmation_code,
        "status": appointment.status,
        "check_in_time": appointment.check_in_time,
        "scheduled_time": appointment.scheduled_time,
        "patient_name": f"{appointment.patient.first_name} {appointment.patient.last_name}",
        "provider_name": appointment.provider_name,
        "ticket_number": queue_entry.ticket_number if queue_entry else None,
        "queue_status": queue_entry.status if queue_entry else None,
        "estimated_wait_time": queue_entry.estimated_wait_time if queue_entry else None
    }


@router.get("/queue/position/{ticket_number}", response_model=dict)
def get_queue_position(
    ticket_number: str,
    db: Session = Depends(get_db)
):
    """Get queue position by ticket number"""
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.ticket_number == ticket_number
    ).first()
    
    if not queue_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue entry not found"
        )
    
    # Count patients ahead in queue
    patients_ahead = db.query(QueueEntry).filter(
        QueueEntry.status == QueueStatus.WAITING,
        QueueEntry.queue_type == queue_entry.queue_type,
        QueueEntry.created_at < queue_entry.created_at
    ).count()
    
    position = patients_ahead + 1
    estimated_wait_time = patients_ahead * 15  # 15 minutes per patient
    
    return {
        "ticket_number": ticket_number,
        "position": position,
        "estimated_wait_time": estimated_wait_time,
        "status": queue_entry.status,
        "patient_name": f"{queue_entry.patient.first_name} {queue_entry.patient.last_name}" if queue_entry.patient else None
    }


@router.post("/queue/{ticket_number}/call", response_model=dict)
def call_patient(
    ticket_number: str,
    db: Session = Depends(get_db)
):
    """Call a patient by ticket number"""
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.ticket_number == ticket_number
    ).first()
    
    if not queue_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue entry not found"
        )
    
    if queue_entry.status != QueueStatus.WAITING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient is not waiting"
        )
    
    queue_entry.status = QueueStatus.CALLED
    queue_entry.called_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "ticket_number": ticket_number,
        "status": "called",
        "called_at": queue_entry.called_at,
        "patient_name": f"{queue_entry.patient.first_name} {queue_entry.patient.last_name}" if queue_entry.patient else None
    }


@router.post("/queue/{ticket_number}/start", response_model=dict)
def start_service(
    ticket_number: str,
    db: Session = Depends(get_db)
):
    """Start service for a patient by ticket number"""
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.ticket_number == ticket_number
    ).first()
    
    if not queue_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue entry not found"
        )
    
    if queue_entry.status not in [QueueStatus.WAITING, QueueStatus.CALLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient is not ready for service"
        )
    
    queue_entry.status = QueueStatus.IN_PROGRESS
    queue_entry.started_at = datetime.utcnow()
    
    # Calculate actual wait time
    if queue_entry.created_at:
        wait_time = (datetime.utcnow() - queue_entry.created_at).total_seconds() / 60
        queue_entry.actual_wait_time = int(wait_time)
    
    # Update appointment status if exists
    if queue_entry.appointment:
        queue_entry.appointment.status = AppointmentStatus.IN_PROGRESS
    
    db.commit()
    
    return {
        "ticket_number": ticket_number,
        "status": "in_progress",
        "started_at": queue_entry.started_at,
        "actual_wait_time": queue_entry.actual_wait_time,
        "patient_name": f"{queue_entry.patient.first_name} {queue_entry.patient.last_name}" if queue_entry.patient else None
    }


@router.post("/queue/{ticket_number}/complete", response_model=dict)
def complete_service(
    ticket_number: str,
    db: Session = Depends(get_db)
):
    """Complete service for a patient by ticket number"""
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.ticket_number == ticket_number
    ).first()
    
    if not queue_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue entry not found"
        )
    
    if queue_entry.status != QueueStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service is not in progress"
        )
    
    queue_entry.status = QueueStatus.COMPLETED
    queue_entry.completed_at = datetime.utcnow()
    
    # Update appointment status if exists
    if queue_entry.appointment:
        queue_entry.appointment.status = AppointmentStatus.COMPLETED
    
    db.commit()
    
    return {
        "ticket_number": ticket_number,
        "status": "completed",
        "completed_at": queue_entry.completed_at,
        "patient_name": f"{queue_entry.patient.first_name} {queue_entry.patient.last_name}" if queue_entry.patient else None
    }
