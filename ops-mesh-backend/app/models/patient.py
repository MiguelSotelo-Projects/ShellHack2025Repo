from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    emergency_contact = Column(String(255), nullable=True)
    medical_record_number = Column(String(50), unique=True, nullable=True)
    insurance_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    queue_entries = relationship("QueueEntry", back_populates="patient")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.first_name} {self.last_name}')>"
