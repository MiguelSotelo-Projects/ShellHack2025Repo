from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import json

from ..models.patient import Patient
from ..models.appointment import Appointment
from ..models.queue import QueueEntry


class NotificationType(str, Enum):
    """Notification types."""
    APPOINTMENT_REMINDER = "appointment_reminder"
    APPOINTMENT_CONFIRMATION = "appointment_confirmation"
    APPOINTMENT_CANCELLATION = "appointment_cancellation"
    QUEUE_UPDATE = "queue_update"
    PATIENT_CALLED = "patient_called"
    SERVICE_STARTED = "service_started"
    SERVICE_COMPLETED = "service_completed"
    WALKIN_REGISTERED = "walkin_registered"
    WAIT_TIME_UPDATE = "wait_time_update"


class NotificationChannel(str, Enum):
    """Notification channels."""
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    IN_APP = "in_app"
    DISPLAY = "display"  # For digital displays


class NotificationService:
    """Service class for notification-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def send_appointment_reminder(
        self, 
        appointment_id: int, 
        reminder_minutes: int = 30
    ) -> Dict[str, Any]:
        """Send appointment reminder notification."""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        if appointment.status != "scheduled":
            raise ValueError(f"Appointment {appointment_id} is not scheduled")
        
        notification_data = {
            "type": NotificationType.APPOINTMENT_REMINDER,
            "appointment_id": appointment_id,
            "patient_id": appointment.patient_id,
            "message": f"Reminder: You have an appointment in {reminder_minutes} minutes",
            "channels": [NotificationChannel.SMS, NotificationChannel.EMAIL],
            "metadata": {
                "appointment_time": appointment.scheduled_time.isoformat(),
                "provider": appointment.provider_name,
                "confirmation_code": appointment.confirmation_code
            }
        }
        
        return self._send_notification(notification_data)
    
    def send_appointment_confirmation(
        self, 
        appointment_id: int
    ) -> Dict[str, Any]:
        """Send appointment confirmation notification."""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        patient = appointment.patient
        notification_data = {
            "type": NotificationType.APPOINTMENT_CONFIRMATION,
            "appointment_id": appointment_id,
            "patient_id": appointment.patient_id,
            "message": f"Appointment confirmed for {appointment.scheduled_time.strftime('%B %d, %Y at %I:%M %p')}",
            "channels": [NotificationChannel.SMS, NotificationChannel.EMAIL],
            "metadata": {
                "appointment_time": appointment.scheduled_time.isoformat(),
                "provider": appointment.provider_name,
                "confirmation_code": appointment.confirmation_code,
                "patient_name": f"{patient.first_name} {patient.last_name}"
            }
        }
        
        return self._send_notification(notification_data)
    
    def send_appointment_cancellation(
        self, 
        appointment_id: int, 
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send appointment cancellation notification."""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        patient = appointment.patient
        message = f"Your appointment scheduled for {appointment.scheduled_time.strftime('%B %d, %Y at %I:%M %p')} has been cancelled"
        if reason:
            message += f". Reason: {reason}"
        
        notification_data = {
            "type": NotificationType.APPOINTMENT_CANCELLATION,
            "appointment_id": appointment_id,
            "patient_id": appointment.patient_id,
            "message": message,
            "channels": [NotificationChannel.SMS, NotificationChannel.EMAIL],
            "metadata": {
                "appointment_time": appointment.scheduled_time.isoformat(),
                "provider": appointment.provider_name,
                "confirmation_code": appointment.confirmation_code,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "cancellation_reason": reason
            }
        }
        
        return self._send_notification(notification_data)
    
    def send_patient_called(
        self, 
        queue_entry_id: int
    ) -> Dict[str, Any]:
        """Send notification when patient is called."""
        queue_entry = self.db.query(QueueEntry).filter(
            QueueEntry.id == queue_entry_id
        ).first()
        
        if not queue_entry:
            raise ValueError(f"Queue entry {queue_entry_id} not found")
        
        patient = queue_entry.patient
        notification_data = {
            "type": NotificationType.PATIENT_CALLED,
            "queue_entry_id": queue_entry_id,
            "patient_id": queue_entry.patient_id,
            "message": f"Please proceed to the service area. Your ticket number is {queue_entry.ticket_number}",
            "channels": [NotificationChannel.DISPLAY, NotificationChannel.IN_APP],
            "metadata": {
                "ticket_number": queue_entry.ticket_number,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "queue_type": queue_entry.queue_type,
                "priority": queue_entry.priority
            }
        }
        
        return self._send_notification(notification_data)
    
    def send_service_started(
        self, 
        queue_entry_id: int
    ) -> Dict[str, Any]:
        """Send notification when service starts."""
        queue_entry = self.db.query(QueueEntry).filter(
            QueueEntry.id == queue_entry_id
        ).first()
        
        if not queue_entry:
            raise ValueError(f"Queue entry {queue_entry_id} not found")
        
        patient = queue_entry.patient
        notification_data = {
            "type": NotificationType.SERVICE_STARTED,
            "queue_entry_id": queue_entry_id,
            "patient_id": queue_entry.patient_id,
            "message": f"Service has started for {patient.first_name} {patient.last_name}",
            "channels": [NotificationChannel.IN_APP],
            "metadata": {
                "ticket_number": queue_entry.ticket_number,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "started_at": queue_entry.started_at.isoformat() if queue_entry.started_at else None
            }
        }
        
        return self._send_notification(notification_data)
    
    def send_service_completed(
        self, 
        queue_entry_id: int
    ) -> Dict[str, Any]:
        """Send notification when service is completed."""
        queue_entry = self.db.query(QueueEntry).filter(
            QueueEntry.id == queue_entry_id
        ).first()
        
        if not queue_entry:
            raise ValueError(f"Queue entry {queue_entry_id} not found")
        
        patient = queue_entry.patient
        notification_data = {
            "type": NotificationType.SERVICE_COMPLETED,
            "queue_entry_id": queue_entry_id,
            "patient_id": queue_entry.patient_id,
            "message": f"Service completed for {patient.first_name} {patient.last_name}",
            "channels": [NotificationChannel.IN_APP],
            "metadata": {
                "ticket_number": queue_entry.ticket_number,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "completed_at": queue_entry.completed_at.isoformat() if queue_entry.completed_at else None,
                "total_wait_time": queue_entry.actual_wait_time
            }
        }
        
        return self._send_notification(notification_data)
    
    def send_walkin_registered(
        self, 
        queue_entry_id: int
    ) -> Dict[str, Any]:
        """Send notification when walk-in is registered."""
        queue_entry = self.db.query(QueueEntry).filter(
            QueueEntry.id == queue_entry_id
        ).first()
        
        if not queue_entry:
            raise ValueError(f"Queue entry {queue_entry_id} not found")
        
        patient = queue_entry.patient
        notification_data = {
            "type": NotificationType.WALKIN_REGISTERED,
            "queue_entry_id": queue_entry_id,
            "patient_id": queue_entry.patient_id,
            "message": f"Walk-in registered for {patient.first_name} {patient.last_name}. Ticket: {queue_entry.ticket_number}",
            "channels": [NotificationChannel.DISPLAY, NotificationChannel.IN_APP],
            "metadata": {
                "ticket_number": queue_entry.ticket_number,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "estimated_wait_time": queue_entry.estimated_wait_time,
                "priority": queue_entry.priority
            }
        }
        
        return self._send_notification(notification_data)
    
    def send_wait_time_update(
        self, 
        queue_entry_id: int, 
        new_estimated_wait: int
    ) -> Dict[str, Any]:
        """Send wait time update notification."""
        queue_entry = self.db.query(QueueEntry).filter(
            QueueEntry.id == queue_entry_id
        ).first()
        
        if not queue_entry:
            raise ValueError(f"Queue entry {queue_entry_id} not found")
        
        patient = queue_entry.patient
        notification_data = {
            "type": NotificationType.WAIT_TIME_UPDATE,
            "queue_entry_id": queue_entry_id,
            "patient_id": queue_entry.patient_id,
            "message": f"Updated wait time: approximately {new_estimated_wait} minutes",
            "channels": [NotificationChannel.IN_APP, NotificationChannel.DISPLAY],
            "metadata": {
                "ticket_number": queue_entry.ticket_number,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "previous_wait_time": queue_entry.estimated_wait_time,
                "new_wait_time": new_estimated_wait
            }
        }
        
        # Update the queue entry with new wait time
        queue_entry.estimated_wait_time = new_estimated_wait
        self.db.commit()
        
        return self._send_notification(notification_data)
    
    def send_bulk_notification(
        self, 
        notification_type: NotificationType,
        patient_ids: List[int],
        message: str,
        channels: List[NotificationChannel],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send bulk notification to multiple patients."""
        results = []
        
        for patient_id in patient_ids:
            notification_data = {
                "type": notification_type,
                "patient_id": patient_id,
                "message": message,
                "channels": channels,
                "metadata": metadata or {}
            }
            
            try:
                result = self._send_notification(notification_data)
                results.append({"patient_id": patient_id, "status": "success", "result": result})
            except Exception as e:
                results.append({"patient_id": patient_id, "status": "error", "error": str(e)})
        
        return {
            "total_sent": len(patient_ids),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"]),
            "results": results
        }
    
    def get_notification_history(
        self, 
        patient_id: Optional[int] = None,
        notification_type: Optional[NotificationType] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get notification history (placeholder - would need notification storage)."""
        # This would typically query a notifications table
        # For now, return empty list as we don't have persistent notification storage
        return []
    
    def _send_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to send notification (placeholder implementation)."""
        # In a real implementation, this would:
        # 1. Store notification in database
        # 2. Send via appropriate channels (SMS, email, push, etc.)
        # 3. Handle delivery status and retries
        
        notification_id = f"notif_{datetime.utcnow().timestamp()}"
        
        # Simulate sending to different channels
        delivery_status = {}
        for channel in notification_data.get("channels", []):
            delivery_status[channel] = {
                "status": "sent",
                "sent_at": datetime.utcnow().isoformat(),
                "delivery_id": f"{channel}_{notification_id}"
            }
        
        return {
            "notification_id": notification_id,
            "type": notification_data["type"],
            "patient_id": notification_data.get("patient_id"),
            "message": notification_data["message"],
            "channels": notification_data.get("channels", []),
            "delivery_status": delivery_status,
            "sent_at": datetime.utcnow().isoformat(),
            "metadata": notification_data.get("metadata", {})
        }
    
    def _validate_patient_contact_info(self, patient_id: int, channels: List[NotificationChannel]) -> Dict[str, bool]:
        """Validate patient has required contact information for notification channels."""
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        
        if not patient:
            return {"valid": False, "reason": "Patient not found"}
        
        validation = {"valid": True, "channels": {}}
        
        for channel in channels:
            if channel == NotificationChannel.SMS:
                validation["channels"][channel] = bool(patient.phone)
            elif channel == NotificationChannel.EMAIL:
                validation["channels"][channel] = bool(patient.email)
            elif channel in [NotificationChannel.PUSH, NotificationChannel.IN_APP, NotificationChannel.DISPLAY]:
                validation["channels"][channel] = True  # These don't require specific contact info
        
        # Check if at least one channel is valid
        validation["valid"] = any(validation["channels"].values())
        
        return validation
