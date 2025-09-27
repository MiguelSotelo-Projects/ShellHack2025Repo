from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .patient import Patient
from .appointment import Appointment
from ..models.queue import QueueType, QueueStatus, QueuePriority


class QueueEntryBase(BaseModel):
    patient_id: Optional[int] = None
    appointment_id: Optional[int] = None
    queue_type: QueueType
    priority: QueuePriority = QueuePriority.MEDIUM
    reason: Optional[str] = None
    estimated_wait_time: Optional[int] = None


class QueueEntryCreate(QueueEntryBase):
    pass


class QueueEntryUpdate(BaseModel):
    status: Optional[QueueStatus] = None
    priority: Optional[QueuePriority] = None
    reason: Optional[str] = None
    estimated_wait_time: Optional[int] = None
    actual_wait_time: Optional[int] = None
    called_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class QueueEntry(QueueEntryBase):
    id: int
    ticket_number: str
    status: QueueStatus
    actual_wait_time: Optional[int] = None
    called_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    patient: Optional[Patient] = None
    appointment: Optional[Appointment] = None
    
    class Config:
        from_attributes = True


class QueueEntryResponse(BaseModel):
    id: int
    ticket_number: str
    status: QueueStatus
    queue_type: QueueType
    priority: QueuePriority
    reason: Optional[str] = None
    estimated_wait_time: Optional[int] = None
    patient_name: Optional[str] = None
    appointment_code: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class WalkInRequest(BaseModel):
    first_name: str
    last_name: str
    reason: str
    priority: QueuePriority = QueuePriority.MEDIUM
    phone: Optional[str] = None

