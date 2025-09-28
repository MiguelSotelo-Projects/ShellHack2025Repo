from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_record_number: Optional[str] = None
    insurance_id: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_record_number: Optional[str] = None
    insurance_id: Optional[str] = None


class Patient(PatientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
