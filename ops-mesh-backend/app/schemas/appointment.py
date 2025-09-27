from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .patient import Patient
from ..models.appointment import AppointmentStatus, AppointmentType


class AppointmentBase(BaseModel):
    confirmation_code: str
    patient_id: int
    provider_name: str
    appointment_type: AppointmentType = AppointmentType.ROUTINE
    scheduled_time: datetime
    duration_minutes: int = 30
    reason: Optional[str] = None
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    provider_name: Optional[str] = None
    appointment_type: Optional[AppointmentType] = None
    status: Optional[AppointmentStatus] = None
    scheduled_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    check_in_time: Optional[datetime] = None


class AppointmentCheckIn(BaseModel):
    confirmation_code: str
    last_name: str


class Appointment(AppointmentBase):
    id: int
    status: AppointmentStatus
    check_in_time: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    patient: Patient
    
    class Config:
        from_attributes = True


class AppointmentResponse(BaseModel):
    id: int
    confirmation_code: str
    status: AppointmentStatus
    scheduled_time: datetime
    provider_name: str
    patient_name: str
    reason: Optional[str] = None
    
    class Config:
        from_attributes = True

