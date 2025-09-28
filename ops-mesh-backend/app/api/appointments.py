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
from ..services.appointment_service import AppointmentService

router = APIRouter()


@router.get("/", response_model=List[AppointmentResponse])
def get_appointments(
    skip: int = 0,
    limit: int = 100,
    status: AppointmentStatus = None,
    db: Session = Depends(get_db)
):
    """Get all appointments with optional filtering"""
    service = AppointmentService(db)
    appointments = service.get_appointments(skip=skip, limit=limit, status_filter=status)
    
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


@router.post("/", response_model=AppointmentSchema, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new appointment with patient data or existing patient ID"""
    service = AppointmentService(db)
    patient_data = appointment_data.get("patient")
    
    return service.create_appointment(appointment_data, patient_data)


@router.put("/{appointment_id}", response_model=AppointmentSchema)
def update_appointment(
    appointment_update: AppointmentUpdate,
    appointment: Appointment = Depends(get_appointment),
    db: Session = Depends(get_db)
):
    """Update an appointment"""
    service = AppointmentService(db)
    update_data = appointment_update.dict(exclude_unset=True)
    
    return service.update_appointment(appointment.id, update_data)


@router.delete("/{appointment_id}")
def delete_appointment(
    appointment: Appointment = Depends(get_appointment),
    db: Session = Depends(get_db)
):
    """Delete an appointment"""
    service = AppointmentService(db)
    service.delete_appointment(appointment.id)
    
    return {"message": "Appointment deleted successfully"}


@router.post("/check-in", response_model=AppointmentSchema)
def check_in_appointment(
    check_in: AppointmentCheckIn,
    db: Session = Depends(get_db)
):
    """Check in an appointment using confirmation code and last name"""
    service = AppointmentService(db)
    return service.check_in_appointment(check_in)


@router.get("/code/{confirmation_code}", response_model=AppointmentSchema)
def get_appointment_by_confirmation_code(
    appointment: Appointment = Depends(get_appointment_by_code)
):
    """Get appointment by confirmation code"""
    return appointment


@router.post("/{appointment_id}/checkin", response_model=AppointmentSchema)
def check_in_appointment_by_id(
    appointment: Appointment = Depends(get_appointment),
    db: Session = Depends(get_db)
):
    """Check in an appointment by ID"""
    service = AppointmentService(db)
    return service.check_in_appointment_by_id(appointment.id)


@router.post("/{appointment_id}/cancel", response_model=AppointmentSchema)
def cancel_appointment(
    appointment: Appointment = Depends(get_appointment),
    db: Session = Depends(get_db)
):
    """Cancel an appointment"""
    service = AppointmentService(db)
    return service.cancel_appointment(appointment.id)


