from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..core.database import get_db
from ..models.queue import QueueEntry, QueueStatus, QueueType, QueuePriority
from ..models.patient import Patient
from ..models.appointment import Appointment
from ..schemas.queue import (
    QueueEntry as QueueEntrySchema,
    QueueEntryCreate,
    QueueEntryUpdate,
    QueueEntryResponse,
    WalkInRequest
)
from .deps import get_queue_entry, get_queue_entry_by_ticket
from ..models.common import generate_ticket_number

router = APIRouter()


@router.get("/", response_model=List[QueueEntryResponse])
def get_queue_entries(
    skip: int = 0,
    limit: int = 100,
    status: QueueStatus = None,
    queue_type: QueueType = None,
    db: Session = Depends(get_db)
):
    """Get all queue entries with optional filtering"""
    query = db.query(QueueEntry)
    
    if status:
        query = query.filter(QueueEntry.status == status)
    
    if queue_type:
        query = query.filter(QueueEntry.queue_type == queue_type)
    
    # Order by priority (urgent first) and creation time
    query = query.order_by(
        QueueEntry.priority.desc(),
        QueueEntry.created_at.asc()
    )
    
    queue_entries = query.offset(skip).limit(limit).all()
    
    # Convert to response format
    result = []
    for entry in queue_entries:
        patient_name = None
        appointment_code = None
        
        if entry.patient:
            patient_name = f"{entry.patient.first_name} {entry.patient.last_name}"
        
        if entry.appointment:
            appointment_code = entry.appointment.confirmation_code
        
        result.append(QueueEntryResponse(
            id=entry.id,
            ticket_number=entry.ticket_number,
            status=entry.status,
            queue_type=entry.queue_type,
            priority=entry.priority,
            reason=entry.reason,
            estimated_wait_time=entry.estimated_wait_time,
            patient_name=patient_name,
            appointment_code=appointment_code,
            created_at=entry.created_at
        ))
    
    return result


@router.get("/{queue_id}", response_model=QueueEntrySchema)
def get_queue_entry_by_id(
    queue_entry: QueueEntry = Depends(get_queue_entry)
):
    """Get queue entry by ID"""
    return queue_entry


@router.get("/ticket/{ticket_number}", response_model=QueueEntrySchema)
def get_queue_entry_by_ticket_number(
    queue_entry: QueueEntry = Depends(get_queue_entry_by_ticket)
):
    """Get queue entry by ticket number"""
    return queue_entry


@router.post("/", response_model=QueueEntrySchema, status_code=status.HTTP_201_CREATED)
def create_queue_entry(
    queue_entry: QueueEntryCreate,
    db: Session = Depends(get_db)
):
    """Create a new queue entry"""
    # Validate patient exists if provided
    if queue_entry.patient_id:
        patient = db.query(Patient).filter(Patient.id == queue_entry.patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
    
    # Validate appointment exists if provided
    if queue_entry.appointment_id:
        appointment = db.query(Appointment).filter(Appointment.id == queue_entry.appointment_id).first()
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
    
    # Generate ticket number
    ticket_number = generate_ticket_number()
    
    # Ensure ticket number is unique
    while db.query(QueueEntry).filter(QueueEntry.ticket_number == ticket_number).first():
        ticket_number = generate_ticket_number()
    
    db_queue_entry = QueueEntry(
        **queue_entry.dict(),
        ticket_number=ticket_number
    )
    db.add(db_queue_entry)
    db.commit()
    db.refresh(db_queue_entry)
    
    return db_queue_entry


@router.post("/walk-in", response_model=QueueEntrySchema)
def create_walk_in(
    walk_in: WalkInRequest,
    db: Session = Depends(get_db)
):
    """Create a walk-in queue entry with patient"""
    # Create or find patient
    patient = db.query(Patient).filter(
        Patient.first_name.ilike(walk_in.first_name),
        Patient.last_name.ilike(walk_in.last_name)
    ).first()
    
    if not patient:
        # Create new patient
        patient = Patient(
            first_name=walk_in.first_name,
            last_name=walk_in.last_name,
            phone=walk_in.phone
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
    
    # Generate ticket number
    ticket_number = generate_ticket_number()
    
    # Ensure ticket number is unique
    while db.query(QueueEntry).filter(QueueEntry.ticket_number == ticket_number).first():
        ticket_number = generate_ticket_number()
    
    # Create queue entry
    queue_entry = QueueEntry(
        patient_id=patient.id,
        queue_type=QueueType.WALK_IN,
        priority=walk_in.priority,
        reason=walk_in.reason,
        estimated_wait_time=30  # Default 30 minutes
    )
    queue_entry.ticket_number = ticket_number
    
    db.add(queue_entry)
    db.commit()
    db.refresh(queue_entry)
    
    return queue_entry


@router.put("/{queue_id}", response_model=QueueEntrySchema)
def update_queue_entry(
    queue_update: QueueEntryUpdate,
    queue_entry: QueueEntry = Depends(get_queue_entry),
    db: Session = Depends(get_db)
):
    """Update a queue entry"""
    update_data = queue_update.dict(exclude_unset=True)
    
    # Calculate actual wait time if status is being updated
    if "status" in update_data:
        if update_data["status"] == QueueStatus.IN_PROGRESS and not queue_entry.started_at:
            update_data["started_at"] = datetime.utcnow()
            if queue_entry.created_at:
                wait_time = (datetime.utcnow() - queue_entry.created_at).total_seconds() / 60
                update_data["actual_wait_time"] = int(wait_time)
        
        elif update_data["status"] == QueueStatus.COMPLETED and not queue_entry.completed_at:
            update_data["completed_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(queue_entry, field, value)
    
    db.commit()
    db.refresh(queue_entry)
    
    return queue_entry


@router.delete("/{queue_id}")
def delete_queue_entry(
    queue_entry: QueueEntry = Depends(get_queue_entry),
    db: Session = Depends(get_db)
):
    """Delete a queue entry"""
    db.delete(queue_entry)
    db.commit()
    
    return {"message": "Queue entry deleted successfully"}


@router.post("/{queue_id}/call")
def call_patient(
    queue_entry: QueueEntry = Depends(get_queue_entry),
    db: Session = Depends(get_db)
):
    """Call a patient (mark as called)"""
    if queue_entry.status != QueueStatus.WAITING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient is not waiting"
        )
    
    queue_entry.status = QueueStatus.CALLED
    queue_entry.called_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Patient called successfully", "ticket_number": queue_entry.ticket_number}


@router.post("/{queue_id}/start")
def start_service(
    queue_entry: QueueEntry = Depends(get_queue_entry),
    db: Session = Depends(get_db)
):
    """Start service for a patient"""
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
    
    db.commit()
    
    return {"message": "Service started successfully", "ticket_number": queue_entry.ticket_number}


@router.post("/{queue_id}/complete")
def complete_service(
    queue_entry: QueueEntry = Depends(get_queue_entry),
    db: Session = Depends(get_db)
):
    """Complete service for a patient"""
    if queue_entry.status != QueueStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service is not in progress"
        )
    
    queue_entry.status = QueueStatus.COMPLETED
    queue_entry.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Service completed successfully", "ticket_number": queue_entry.ticket_number}
