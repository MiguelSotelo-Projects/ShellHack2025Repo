from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status

from ..models.patient import Patient
from ..models.appointment import Appointment, AppointmentStatus, AppointmentType
from ..models.queue import QueueEntry, QueueStatus, QueueType, QueuePriority
from ..models.common import generate_ticket_number, generate_confirmation_code


class WalkInService:
    """Service class for walk-in patient business logic."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_walkin(self, walkin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a walk-in patient with appointment and queue entry."""
        patient_data = walkin_data.get("patient")
        reason = walkin_data.get("reason", "Walk-in consultation")
        priority = walkin_data.get("priority", QueuePriority.MEDIUM)
        
        if not patient_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient data is required"
            )
        
        # Create or find patient
        patient = self._create_or_find_patient(patient_data)
        
        # Create appointment for walk-in
        appointment = self._create_walkin_appointment(patient.id, reason)
        
        # Create queue entry
        queue_entry = self._create_walkin_queue_entry(
            patient.id, appointment.id, priority, reason
        )
        
        return {
            "patient_id": patient.id,
            "appointment_id": appointment.id,
            "queue_entry_id": queue_entry.id,
            "ticket_number": queue_entry.ticket_number,
            "confirmation_code": appointment.confirmation_code,
            "reason": reason,
            "priority": priority
        }
    
    def get_walkin_queue(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status_filter: Optional[QueueStatus] = None
    ) -> List[QueueEntry]:
        """Get walk-in queue entries."""
        query = self.db.query(QueueEntry).filter(
            QueueEntry.queue_type == QueueType.WALK_IN
        )
        
        if status_filter:
            query = query.filter(QueueEntry.status == status_filter)
        
        return query.order_by(
            QueueEntry.priority.desc(),
            QueueEntry.created_at.asc()
        ).offset(skip).limit(limit).all()
    
    def process_walkin(self, appointment_id: int) -> Dict[str, Any]:
        """Process a walk-in appointment."""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.status == AppointmentStatus.SCHEDULED
        ).first()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Walk-in appointment not found or already processed"
            )
        
        # Update appointment status
        appointment.status = AppointmentStatus.IN_PROGRESS
        
        # Update queue entry if exists
        queue_entry = self.db.query(QueueEntry).filter(
            QueueEntry.appointment_id == appointment_id
        ).first()
        
        if queue_entry:
            queue_entry.status = QueueStatus.IN_PROGRESS
            queue_entry.started_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "appointment_id": appointment_id,
            "status": "in_progress",
            "processed_at": datetime.utcnow()
        }
    
    def get_walkin_wait_time(self, appointment_id: int) -> Dict[str, Any]:
        """Get estimated wait time for walk-in."""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Get queue entry
        queue_entry = self.db.query(QueueEntry).filter(
            QueueEntry.appointment_id == appointment_id
        ).first()
        
        if not queue_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queue entry not found"
            )
        
        # Count patients ahead with same or higher priority
        patients_ahead = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING,
            QueueEntry.queue_type == QueueType.WALK_IN,
            QueueEntry.priority >= queue_entry.priority,
            QueueEntry.created_at < queue_entry.created_at
        ).count()
        
        estimated_wait_time = patients_ahead * 15  # 15 minutes per patient
        
        return {
            "appointment_id": appointment_id,
            "position_in_queue": patients_ahead + 1,
            "estimated_wait_time": estimated_wait_time
        }
    
    def update_walkin_status(
        self, 
        appointment_id: int, 
        status_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update walk-in status."""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        new_status = status_data.get("status")
        if new_status:
            appointment.status = new_status
        
        # Update queue entry if exists
        queue_entry = self.db.query(QueueEntry).filter(
            QueueEntry.appointment_id == appointment_id
        ).first()
        
        if queue_entry and new_status:
            if new_status == AppointmentStatus.IN_PROGRESS:
                queue_entry.status = QueueStatus.IN_PROGRESS
                queue_entry.started_at = datetime.utcnow()
            elif new_status == AppointmentStatus.COMPLETED:
                queue_entry.status = QueueStatus.COMPLETED
                queue_entry.completed_at = datetime.utcnow()
            elif new_status == AppointmentStatus.CANCELLED:
                queue_entry.status = QueueStatus.CANCELLED
        
        self.db.commit()
        
        return {
            "appointment_id": appointment_id,
            "status": appointment.status
        }
    
    def cancel_walkin(self, appointment_id: int) -> Dict[str, Any]:
        """Cancel a walk-in appointment."""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
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
        
        appointment.status = AppointmentStatus.CANCELLED
        
        # Update queue entry if exists
        queue_entry = self.db.query(QueueEntry).filter(
            QueueEntry.appointment_id == appointment_id
        ).first()
        
        if queue_entry:
            queue_entry.status = QueueStatus.CANCELLED
        
        self.db.commit()
        
        return {
            "appointment_id": appointment_id,
            "status": "cancelled"
        }
    
    def complete_walkin(self, appointment_id: int) -> Dict[str, Any]:
        """Complete a walk-in appointment."""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        if appointment.status != AppointmentStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment is not in progress"
            )
        
        appointment.status = AppointmentStatus.COMPLETED
        
        # Update queue entry if exists
        queue_entry = self.db.query(QueueEntry).filter(
            QueueEntry.appointment_id == appointment_id
        ).first()
        
        if queue_entry:
            queue_entry.status = QueueStatus.COMPLETED
            queue_entry.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "appointment_id": appointment_id,
            "status": "completed",
            "completed_at": datetime.utcnow()
        }
    
    def get_walkin_statistics(self) -> Dict[str, Any]:
        """Get walk-in statistics."""
        total_walkins = self.db.query(QueueEntry).filter(
            QueueEntry.queue_type == QueueType.WALK_IN
        ).count()
        
        waiting_walkins = self.db.query(QueueEntry).filter(
            QueueEntry.queue_type == QueueType.WALK_IN,
            QueueEntry.status == QueueStatus.WAITING
        ).count()
        
        in_progress_walkins = self.db.query(QueueEntry).filter(
            QueueEntry.queue_type == QueueType.WALK_IN,
            QueueEntry.status == QueueStatus.IN_PROGRESS
        ).count()
        
        completed_walkins = self.db.query(QueueEntry).filter(
            QueueEntry.queue_type == QueueType.WALK_IN,
            QueueEntry.status == QueueStatus.COMPLETED
        ).count()
        
        # Average wait time for completed walk-ins
        avg_wait_time = self.db.query(
            func.avg(QueueEntry.actual_wait_time)
        ).filter(
            QueueEntry.queue_type == QueueType.WALK_IN,
            QueueEntry.actual_wait_time.isnot(None)
        ).scalar() or 0
        
        return {
            "total_walkins": total_walkins,
            "waiting_walkins": waiting_walkins,
            "in_progress_walkins": in_progress_walkins,
            "completed_walkins": completed_walkins,
            "average_wait_time": round(avg_wait_time, 1)
        }
    
    def _create_or_find_patient(self, patient_data: Dict[str, Any]) -> Patient:
        """Create or find existing patient."""
        patient = self.db.query(Patient).filter(
            Patient.first_name.ilike(patient_data.get("first_name", "")),
            Patient.last_name.ilike(patient_data.get("last_name", ""))
        ).first()
        
        if not patient:
            # Create new patient
            patient = Patient(**patient_data)
            self.db.add(patient)
            self.db.commit()
            self.db.refresh(patient)
        
        return patient
    
    def _create_walkin_appointment(self, patient_id: int, reason: str) -> Appointment:
        """Create appointment for walk-in."""
        appointment = Appointment(
            confirmation_code=generate_confirmation_code(),
            patient_id=patient_id,
            provider_name="Walk-in Provider",
            appointment_type=AppointmentType.ROUTINE,
            status=AppointmentStatus.SCHEDULED,
            scheduled_time=datetime.utcnow(),
            reason=reason
        )
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment
    
    def _create_walkin_queue_entry(
        self, 
        patient_id: int, 
        appointment_id: int, 
        priority: QueuePriority, 
        reason: str
    ) -> QueueEntry:
        """Create queue entry for walk-in."""
        ticket_number = generate_ticket_number()
        while self.db.query(QueueEntry).filter(QueueEntry.ticket_number == ticket_number).first():
            ticket_number = generate_ticket_number()
        
        queue_entry = QueueEntry(
            ticket_number=ticket_number,
            patient_id=patient_id,
            appointment_id=appointment_id,
            queue_type=QueueType.WALK_IN,
            status=QueueStatus.WAITING,
            priority=priority,
            reason=reason,
            estimated_wait_time=30
        )
        self.db.add(queue_entry)
        self.db.commit()
        self.db.refresh(queue_entry)
        return queue_entry
