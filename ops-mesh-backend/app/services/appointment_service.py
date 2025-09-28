from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from ..models.appointment import Appointment, AppointmentStatus, AppointmentType
from ..models.patient import Patient
from ..models.queue import QueueEntry, QueueType, QueueStatus
from ..schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentCheckIn
from ..models.common import generate_confirmation_code


class AppointmentService:
    """Service class for appointment-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_appointments(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        status_filter: Optional[AppointmentStatus] = None,
        patient_id: Optional[int] = None,
        provider_name: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Appointment]:
        """Get appointments with various filters."""
        query = self.db.query(Appointment)
        
        if status_filter:
            query = query.filter(Appointment.status == status_filter)
        
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        
        if provider_name:
            query = query.filter(Appointment.provider_name.ilike(f"%{provider_name}%"))
        
        if date_from:
            query = query.filter(Appointment.scheduled_time >= date_from)
        
        if date_to:
            query = query.filter(Appointment.scheduled_time <= date_to)
        
        return query.offset(skip).limit(limit).all()
    
    def get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """Get appointment by ID."""
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    def get_appointment_by_code(self, confirmation_code: str) -> Optional[Appointment]:
        """Get appointment by confirmation code."""
        return self.db.query(Appointment).filter(
            Appointment.confirmation_code == confirmation_code
        ).first()
    
    def create_appointment(
        self, 
        appointment_data: Dict[str, Any], 
        patient_data: Optional[Dict[str, Any]] = None
    ) -> Appointment:
        """Create a new appointment, optionally creating a patient."""
        # Handle patient creation if patient data is provided
        patient_id = appointment_data.get("patient_id")
        
        if patient_data and not patient_id:
            patient = self._create_patient(patient_data)
            patient_id = patient.id
        elif not patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient ID or patient data required"
            )
        
        # Validate patient exists
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Prepare appointment data
        appointment_dict = {k: v for k, v in appointment_data.items() if k != "patient"}
        appointment_dict["patient_id"] = patient_id
        
        # Generate confirmation code if not provided
        if not appointment_dict.get("confirmation_code"):
            appointment_dict["confirmation_code"] = generate_confirmation_code()
        
        # Map appointment_date to scheduled_time if needed
        if "appointment_date" in appointment_dict:
            appointment_dict["scheduled_time"] = appointment_dict.pop("appointment_date")
        
        # Map provider to provider_name if needed
        if "provider" in appointment_dict:
            appointment_dict["provider_name"] = appointment_dict.pop("provider")
        
        # Convert scheduled_time string to datetime if needed
        if "scheduled_time" in appointment_dict and isinstance(appointment_dict["scheduled_time"], str):
            appointment_dict["scheduled_time"] = datetime.fromisoformat(
                appointment_dict["scheduled_time"].replace('Z', '+00:00')
            )
        
        # Create appointment
        appointment = Appointment(**appointment_dict)
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    def update_appointment(self, appointment_id: int, update_data: Dict[str, Any]) -> Appointment:
        """Update an appointment."""
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Convert scheduled_time string to datetime if needed
        if "scheduled_time" in update_data and isinstance(update_data["scheduled_time"], str):
            update_data["scheduled_time"] = datetime.fromisoformat(
                update_data["scheduled_time"].replace('Z', '+00:00')
            )
        
        for field, value in update_data.items():
            if hasattr(appointment, field):
                setattr(appointment, field, value)
        
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    def delete_appointment(self, appointment_id: int) -> bool:
        """Delete an appointment."""
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        self.db.delete(appointment)
        self.db.commit()
        return True
    
    def check_in_appointment(self, checkin_data: AppointmentCheckIn) -> Appointment:
        """Check in an appointment using confirmation code and last name."""
        appointment = self.get_appointment_by_code(checkin_data.confirmation_code)
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
        self._create_or_update_queue_entry(appointment)
        
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    def check_in_appointment_by_id(self, appointment_id: int) -> Appointment:
        """Check in an appointment by ID."""
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        if appointment.status == AppointmentStatus.CHECKED_IN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment already checked in"
            )
        
        if appointment.status in [AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot check in cancelled or completed appointment"
            )
        
        appointment.status = AppointmentStatus.CHECKED_IN
        appointment.check_in_time = datetime.utcnow()
        
        # Create or update queue entry
        self._create_or_update_queue_entry(appointment)
        
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    def cancel_appointment(self, appointment_id: int) -> Appointment:
        """Cancel an appointment."""
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        if appointment.status == AppointmentStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment already cancelled"
            )
        
        if appointment.status == AppointmentStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel completed appointment"
            )
        
        appointment.status = AppointmentStatus.CANCELLED
        
        # Update queue entry if exists
        queue_entry = self.db.query(QueueEntry).filter(
            QueueEntry.appointment_id == appointment_id
        ).first()
        
        if queue_entry:
            queue_entry.status = QueueStatus.CANCELLED
        
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    def get_appointments_by_patient(self, patient_id: int) -> List[Appointment]:
        """Get all appointments for a specific patient."""
        return self.db.query(Appointment).filter(
            Appointment.patient_id == patient_id
        ).order_by(Appointment.scheduled_time.desc()).all()
    
    def get_appointments_by_provider(
        self, 
        provider_name: str, 
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Appointment]:
        """Get appointments for a specific provider."""
        query = self.db.query(Appointment).filter(
            Appointment.provider_name.ilike(f"%{provider_name}%")
        )
        
        if date_from:
            query = query.filter(Appointment.scheduled_time >= date_from)
        
        if date_to:
            query = query.filter(Appointment.scheduled_time <= date_to)
        
        return query.order_by(Appointment.scheduled_time.asc()).all()
    
    def get_appointments_today(self) -> List[Appointment]:
        """Get all appointments scheduled for today."""
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        return self.db.query(Appointment).filter(
            and_(
                Appointment.scheduled_time >= start_of_day,
                Appointment.scheduled_time <= end_of_day
            )
        ).order_by(Appointment.scheduled_time.asc()).all()
    
    def get_appointments_this_week(self) -> List[Appointment]:
        """Get all appointments scheduled for this week."""
        today = datetime.utcnow().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        start_datetime = datetime.combine(start_of_week, datetime.min.time())
        end_datetime = datetime.combine(end_of_week, datetime.max.time())
        
        return self.db.query(Appointment).filter(
            and_(
                Appointment.scheduled_time >= start_datetime,
                Appointment.scheduled_time <= end_datetime
            )
        ).order_by(Appointment.scheduled_time.asc()).all()
    
    def _create_patient(self, patient_data: Dict[str, Any]) -> Patient:
        """Create a new patient."""
        # Convert date_of_birth string to datetime if needed
        if "date_of_birth" in patient_data and isinstance(patient_data["date_of_birth"], str):
            patient_data["date_of_birth"] = datetime.fromisoformat(
                patient_data["date_of_birth"].replace('Z', '+00:00')
            )
        
        patient = Patient(**patient_data)
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient
    
    def _create_or_update_queue_entry(self, appointment: Appointment):
        """Create or update queue entry for appointment."""
        from ..models.common import generate_ticket_number
        
        queue_entry = self.db.query(QueueEntry).filter(
            QueueEntry.appointment_id == appointment.id
        ).first()
        
        if not queue_entry:
            # Create new queue entry
            ticket_number = generate_ticket_number()
            while self.db.query(QueueEntry).filter(QueueEntry.ticket_number == ticket_number).first():
                ticket_number = generate_ticket_number()
            
            queue_entry = QueueEntry(
                ticket_number=ticket_number,
                patient_id=appointment.patient_id,
                appointment_id=appointment.id,
                queue_type=QueueType.APPOINTMENT,
                status=QueueStatus.WAITING,
                reason=appointment.reason
            )
            self.db.add(queue_entry)
        else:
            # Update existing queue entry
            queue_entry.status = QueueStatus.WAITING
        
        return queue_entry
