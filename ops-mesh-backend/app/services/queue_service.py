from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import asyncio

from ..models.queue import QueueEntry, QueueStatus, QueueType, QueuePriority
from ..models.patient import Patient
from ..models.appointment import Appointment
from ..schemas.queue import QueueEntryCreate, QueueEntryUpdate, WalkInRequest
from ..models.common import generate_ticket_number


class QueueService:
    """Service class for queue-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def _send_websocket_update(self, update_type: str, data: Dict[str, Any]):
        """Send WebSocket update for queue changes."""
        try:
            from ..websockets.connection_manager import manager
            if update_type == "queue_update":
                await manager.send_queue_update(data)
            elif update_type == "notification":
                await manager.send_notification(data)
        except Exception as e:
            # Don't fail the main operation if WebSocket fails
            print(f"WebSocket update failed: {e}")
    
    def get_queue_entries(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[QueueStatus] = None,
        queue_type_filter: Optional[QueueType] = None,
        priority_filter: Optional[QueuePriority] = None
    ) -> List[QueueEntry]:
        """Get queue entries with various filters."""
        query = self.db.query(QueueEntry)
        
        if status_filter:
            query = query.filter(QueueEntry.status == status_filter)
        
        if queue_type_filter:
            query = query.filter(QueueEntry.queue_type == queue_type_filter)
        
        if priority_filter:
            query = query.filter(QueueEntry.priority == priority_filter)
        
        # Order by priority (urgent first) and creation time
        query = query.order_by(
            QueueEntry.priority.desc(),
            QueueEntry.created_at.asc()
        )
        
        return query.offset(skip).limit(limit).all()
    
    def get_queue_entry_by_id(self, queue_id: int) -> Optional[QueueEntry]:
        """Get queue entry by ID."""
        return self.db.query(QueueEntry).filter(QueueEntry.id == queue_id).first()
    
    def get_queue_entry_by_ticket(self, ticket_number: str) -> Optional[QueueEntry]:
        """Get queue entry by ticket number."""
        return self.db.query(QueueEntry).filter(
            QueueEntry.ticket_number == ticket_number
        ).first()
    
    def create_queue_entry(self, queue_data: Dict[str, Any]) -> QueueEntry:
        """Create a new queue entry."""
        # Validate patient exists if provided
        if queue_data.get("patient_id"):
            patient = self.db.query(Patient).filter(
                Patient.id == queue_data["patient_id"]
            ).first()
            if not patient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found"
                )
        
        # Validate appointment exists if provided
        if queue_data.get("appointment_id"):
            appointment = self.db.query(Appointment).filter(
                Appointment.id == queue_data["appointment_id"]
            ).first()
            if not appointment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Appointment not found"
                )
        
        # Generate ticket number
        ticket_number = generate_ticket_number()
        
        # Ensure ticket number is unique
        while self.db.query(QueueEntry).filter(QueueEntry.ticket_number == ticket_number).first():
            ticket_number = generate_ticket_number()
        
        queue_entry = QueueEntry(
            **queue_data,
            ticket_number=ticket_number
        )
        self.db.add(queue_entry)
        self.db.commit()
        self.db.refresh(queue_entry)
        
        return queue_entry
    
    def create_walk_in(self, walkin_data: WalkInRequest) -> QueueEntry:
        """Create a walk-in queue entry with patient."""
        # Create or find patient
        patient = self.db.query(Patient).filter(
            Patient.first_name.ilike(walkin_data.first_name),
            Patient.last_name.ilike(walkin_data.last_name)
        ).first()
        
        if not patient:
            # Create new patient
            patient = Patient(
                first_name=walkin_data.first_name,
                last_name=walkin_data.last_name,
                phone=walkin_data.phone
            )
            self.db.add(patient)
            self.db.commit()
            self.db.refresh(patient)
        
        # Generate ticket number
        ticket_number = generate_ticket_number()
        
        # Ensure ticket number is unique
        while self.db.query(QueueEntry).filter(QueueEntry.ticket_number == ticket_number).first():
            ticket_number = generate_ticket_number()
        
        # Create queue entry
        queue_entry = QueueEntry(
            patient_id=patient.id,
            queue_type=QueueType.WALK_IN,
            priority=walkin_data.priority,
            reason=walkin_data.reason,
            estimated_wait_time=30  # Default 30 minutes
        )
        queue_entry.ticket_number = ticket_number
        
        self.db.add(queue_entry)
        self.db.commit()
        self.db.refresh(queue_entry)
        
        return queue_entry
    
    def update_queue_entry(self, queue_id: int, update_data: Dict[str, Any]) -> QueueEntry:
        """Update a queue entry."""
        queue_entry = self.get_queue_entry_by_id(queue_id)
        if not queue_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queue entry not found"
            )
        
        # Calculate actual wait time if status is being updated
        if "status" in update_data:
            if update_data["status"] == QueueStatus.IN_PROGRESS and not queue_entry.started_at:
                update_data["started_at"] = datetime.utcnow()
                if queue_entry.created_at:
                    wait_time = (datetime.utcnow() - queue_entry.created_at).total_seconds() / 60
                    update_data["actual_wait_time"] = int(wait_time)
            
            elif update_data["status"] == QueueStatus.COMPLETED and not queue_entry.completed_at:
                update_data["completed_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            if hasattr(queue_entry, field):
                setattr(queue_entry, field, value)
        
        self.db.commit()
        self.db.refresh(queue_entry)
        
        return queue_entry
    
    def delete_queue_entry(self, queue_id: int) -> bool:
        """Delete a queue entry."""
        queue_entry = self.get_queue_entry_by_id(queue_id)
        if not queue_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queue entry not found"
            )
        
        self.db.delete(queue_entry)
        self.db.commit()
        return True
    
    def call_patient(self, queue_id: int) -> QueueEntry:
        """Call a patient (mark as called)."""
        queue_entry = self.get_queue_entry_by_id(queue_id)
        if not queue_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queue entry not found"
            )
        
        if queue_entry.status != QueueStatus.WAITING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient is not waiting"
            )
        
        queue_entry.status = QueueStatus.CALLED
        queue_entry.called_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(queue_entry)
        
        return queue_entry
    
    def start_service(self, queue_id: int) -> QueueEntry:
        """Start service for a patient."""
        queue_entry = self.get_queue_entry_by_id(queue_id)
        if not queue_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queue entry not found"
            )
        
        if queue_entry.status not in [QueueStatus.WAITING, QueueStatus.CALLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient is not ready for service"
            )
        
        queue_entry.status = QueueStatus.IN_PROGRESS
        queue_entry.started_at = datetime.utcnow()
        
        # Calculate actual wait time
        if queue_entry.created_at:
            wait_time = (datetime.utcnow() - queue_entry.created_at).total_seconds() / 60
            queue_entry.actual_wait_time = int(wait_time)
        
        self.db.commit()
        self.db.refresh(queue_entry)
        
        return queue_entry
    
    def complete_service(self, queue_id: int) -> QueueEntry:
        """Complete service for a patient."""
        queue_entry = self.get_queue_entry_by_id(queue_id)
        if not queue_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queue entry not found"
            )
        
        if queue_entry.status != QueueStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service is not in progress"
            )
        
        queue_entry.status = QueueStatus.COMPLETED
        queue_entry.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(queue_entry)
        
        return queue_entry
    
    def get_queue_position(self, ticket_number: str) -> Dict[str, Any]:
        """Get queue position and estimated wait time."""
        queue_entry = self.get_queue_entry_by_ticket(ticket_number)
        if not queue_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queue entry not found"
            )
        
        # Count patients ahead in queue
        patients_ahead = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING,
            QueueEntry.queue_type == queue_entry.queue_type,
            QueueEntry.created_at < queue_entry.created_at
        ).count()
        
        position = patients_ahead + 1
        estimated_wait_time = patients_ahead * 15  # 15 minutes per patient
        
        return {
            "ticket_number": ticket_number,
            "position": position,
            "estimated_wait_time": estimated_wait_time,
            "status": queue_entry.status,
            "patient_name": f"{queue_entry.patient.first_name} {queue_entry.patient.last_name}" if queue_entry.patient else None
        }
    
    def get_queue_statistics(self) -> Dict[str, Any]:
        """Get queue statistics."""
        total_waiting = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING
        ).count()
        
        total_in_progress = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.IN_PROGRESS
        ).count()
        
        total_called = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.CALLED
        ).count()
        
        total_completed = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.COMPLETED
        ).count()
        
        # Average wait time for completed entries
        avg_wait_time = self.db.query(func.avg(QueueEntry.actual_wait_time)).filter(
            QueueEntry.actual_wait_time.isnot(None)
        ).scalar() or 0
        
        # Queue by type
        walk_ins_waiting = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING,
            QueueEntry.queue_type == QueueType.WALK_IN
        ).count()
        
        appointments_waiting = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING,
            QueueEntry.queue_type == QueueType.APPOINTMENT
        ).count()
        
        return {
            "total_waiting": total_waiting,
            "total_in_progress": total_in_progress,
            "total_called": total_called,
            "total_completed": total_completed,
            "average_wait_time": round(avg_wait_time, 1),
            "walk_ins_waiting": walk_ins_waiting,
            "appointments_waiting": appointments_waiting
        }
    
    def get_priority_queue(self) -> List[QueueEntry]:
        """Get queue entries ordered by priority."""
        return self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING
        ).order_by(
            QueueEntry.priority.desc(),
            QueueEntry.created_at.asc()
        ).all()
    
    def get_next_patient(self) -> Optional[QueueEntry]:
        """Get the next patient to be called (highest priority, oldest)."""
        return self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING
        ).order_by(
            QueueEntry.priority.desc(),
            QueueEntry.created_at.asc()
        ).first()
    
    def get_waiting_patients_by_priority(self) -> Dict[str, List[QueueEntry]]:
        """Get waiting patients grouped by priority."""
        waiting_patients = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING
        ).order_by(QueueEntry.created_at.asc()).all()
        
        priority_groups = {
            "urgent": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for patient in waiting_patients:
            priority_groups[patient.priority.value].append(patient)
        
        return priority_groups
    
    def estimate_wait_time(self, queue_entry: QueueEntry) -> int:
        """Estimate wait time for a specific queue entry."""
        # Count patients ahead with same or higher priority
        patients_ahead = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING,
            QueueEntry.queue_type == queue_entry.queue_type,
            QueueEntry.priority >= queue_entry.priority,
            QueueEntry.created_at < queue_entry.created_at
        ).count()
        
        # Base time per patient (in minutes)
        base_time_per_patient = 15
        
        # Adjust based on priority
        priority_multiplier = {
            QueuePriority.URGENT: 0.5,  # Urgent patients get faster service
            QueuePriority.HIGH: 0.7,
            QueuePriority.MEDIUM: 1.0,
            QueuePriority.LOW: 1.2
        }
        
        estimated_time = int(patients_ahead * base_time_per_patient * priority_multiplier.get(queue_entry.priority, 1.0))
        
        return max(estimated_time, 5)  # Minimum 5 minutes
