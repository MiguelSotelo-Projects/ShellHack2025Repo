from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class QueueType(str, enum.Enum):
    WALK_IN = "walk_in"
    APPOINTMENT = "appointment"
    EMERGENCY = "emergency"


class QueueStatus(str, enum.Enum):
    WAITING = "waiting"
    CALLED = "called"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class QueuePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class QueueEntry(Base):
    __tablename__ = "queue_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(20), unique=True, nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    queue_type = Column(Enum(QueueType), nullable=False)
    status = Column(Enum(QueueStatus), default=QueueStatus.WAITING)
    priority = Column(Enum(QueuePriority), default=QueuePriority.MEDIUM)
    reason = Column(Text, nullable=True)
    estimated_wait_time = Column(Integer, nullable=True)  # in minutes
    actual_wait_time = Column(Integer, nullable=True)  # in minutes
    called_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="queue_entries")
    appointment = relationship("Appointment", back_populates="queue_entries")
    
    def __repr__(self):
        return f"<QueueEntry(id={self.id}, ticket='{self.ticket_number}', status='{self.status}')>"

