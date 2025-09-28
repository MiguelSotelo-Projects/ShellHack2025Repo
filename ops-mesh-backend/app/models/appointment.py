from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentType(str, enum.Enum):
    ROUTINE = "routine"
    URGENT = "urgent"
    FOLLOW_UP = "follow_up"
    CONSULTATION = "consultation"


class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    confirmation_code = Column(String(20), unique=True, nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    provider_name = Column(String(100), nullable=False)
    appointment_type = Column(Enum(AppointmentType), default=AppointmentType.ROUTINE)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    scheduled_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    check_in_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    queue_entries = relationship("QueueEntry", back_populates="appointment")
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, code='{self.confirmation_code}', status='{self.status}')>"
