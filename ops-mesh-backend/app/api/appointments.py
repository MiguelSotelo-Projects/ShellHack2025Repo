from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..core.database import get_db
from ..models.appointment import Appointment, AppointmentStatus
from ..models.patient import Patient
from ..schemas.appointment import (
    Appointment as AppointmentSchema,
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentCheckIn,
    AppointmentResponse
)
from ..schemas.patient import PatientCreate
from .deps import get_appointment, get_appointment_by_code
from ..models.common import generate_confirmation_code

router = APIRouter()


@router.get("/", response_model=List[AppointmentResponse])
def get_appointments(
    skip: int = 0,
    limit: int = 100,
    status: AppointmentStatus = None,
    db: Session = Depends(get_db)
):
    """Get all appointments with optional filtering"""
    query = db.query(Appointment)
    
    if status:
        query = query.filter(Appointment.status == status)
    
    appointments = query.offset(skip).limit(limit).all()
    
    # Convert to response format
    result = []
    for apt in appointments:
        result.append(AppointmentResponse(
            id=apt.id,
            confirmation_code=apt.confirmation_code,
            status=apt.status,
            scheduled_time=apt.scheduled_time,
            provider_name=apt.provider_name,
            patient_name=f"{apt.patient.first_name} {apt.patient.last_name}",
            reason=apt.reason
        ))
    
    return result


@router.get("/{appointment_id}", response_model=AppointmentSchema)
def get_appointment_by_id(
    appointment: Appointment = Depends(get_appointment)
):
    """Get appointment by ID"""
    return appointment


@router.post("/", response_model=AppointmentSchema)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new appointment"""
    # Check if patient exists
    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Generate confirmation code if not provided
    if not appointment.confirmation_code:
        appointment.confirmation_code = generate_confirmation_code()
    
    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment


@router.put("/{appointment_id}", response_model=AppointmentSchema)
def update_appointment(
    appointment_update: AppointmentUpdate,
    appointment: Appointment = Depends(get_appointment),
    db: Session = Depends(get_db)
):
    """Update an appointment"""
    update_data = appointment_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(appointment, field, value)
    
    db.commit()
    db.refresh(appointment)
    
    return appointment


@router.delete("/{appointment_id}")
def delete_appointment(
    appointment: Appointment = Depends(get_appointment),
    db: Session = Depends(get_db)
):
    """Delete an appointment"""
    db.delete(appointment)
    db.commit()
    
    return {"message": "Appointment deleted successfully"}


@router.post("/check-in", response_model=AppointmentSchema)
def check_in_appointment(
    check_in: AppointmentCheckIn,
    db: Session = Depends(get_db)
):
    """Check in an appointment using confirmation code and last name"""
    # Find appointment by confirmation code
    appointment = db.query(Appointment).filter(
        Appointment.confirmation_code == check_in.confirmation_code
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verify last name matches
    if appointment.patient.last_name.lower() != check_in.last_name.lower():
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
    
    # Update appointment status
    appointment.status = AppointmentStatus.CHECKED_IN
    appointment.check_in_time = datetime.utcnow()
    
    db.commit()
    db.refresh(appointment)
    
    return appointment


@router.get("/code/{confirmation_code}", response_model=AppointmentSchema)
def get_appointment_by_confirmation_code(
    appointment: Appointment = Depends(get_appointment_by_code)
):
    """Get appointment by confirmation code"""
    return appointment
