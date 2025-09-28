import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from app.services.appointment_service import AppointmentService
from app.services.dashboard_service import DashboardService
from app.services.queue_service import QueueService
from app.services.walkin_service import WalkInService
from app.services.notification_service import NotificationService
from app.schemas.appointment import AppointmentCreate
from app.schemas.patient import PatientCreate
from app.schemas.queue import QueueEntryCreate, QueueEntryUpdate
from app.models.appointment import AppointmentStatus, AppointmentType
from app.models.queue import QueueStatus, QueueType, QueuePriority


class TestAppointmentService:
    """Test cases for the AppointmentService."""
    
    def test_get_appointments(self, db_session, multiple_appointments):
        """Test getting appointments through the service."""
        service = AppointmentService(db_session)
        appointments = service.get_appointments()
        
        assert len(appointments) == len(multiple_appointments)
        assert all(isinstance(apt, type(multiple_appointments[0])) for apt in appointments)
    
    def test_get_appointment_by_id(self, db_session, sample_appointment):
        """Test getting an appointment by ID through the service."""
        service = AppointmentService(db_session)
        appointment = service.get_appointment_by_id(sample_appointment.id)
        
        assert appointment is not None
        assert appointment.id == sample_appointment.id
        assert appointment.confirmation_code == sample_appointment.confirmation_code
    
    def test_get_appointment_by_confirmation_code(self, db_session, sample_appointment):
        """Test getting an appointment by confirmation code through the service."""
        service = AppointmentService(db_session)
        appointment = service.get_appointment_by_code(sample_appointment.confirmation_code)
        
        assert appointment is not None
        assert appointment.confirmation_code == sample_appointment.confirmation_code
    
    def test_create_appointment(self, db_session, sample_patient_data):
        """Test creating an appointment through the service."""
        service = AppointmentService(db_session)
        
        # Create patient first
        patient_data = sample_patient_data.copy()
        patient = service._create_patient(patient_data)
        
        appointment_data = {
            "confirmation_code": "TEST123",
            "patient_id": patient.id,
            "provider_name": "Dr. Test",
            "appointment_type": AppointmentType.ROUTINE,
            "scheduled_time": datetime.now() + timedelta(days=1),
            "duration_minutes": 30,
            "reason": "Test appointment"
        }
        
        appointment = service.create_appointment(appointment_data)
        
        assert appointment is not None
        assert appointment.provider_name == "Dr. Test"
        assert appointment.appointment_type == AppointmentType.ROUTINE
        assert appointment.patient_id is not None
    
    def test_update_appointment(self, db_session, sample_appointment):
        """Test updating an appointment through the service."""
        service = AppointmentService(db_session)
        
        update_data = {
            "provider_name": "Dr. Updated",
            "status": AppointmentStatus.CONFIRMED
        }
        
        updated_appointment = service.update_appointment(sample_appointment.id, update_data)
        
        assert updated_appointment.provider_name == "Dr. Updated"
        assert updated_appointment.status == AppointmentStatus.CONFIRMED
    
    def test_cancel_appointment(self, db_session, sample_appointment):
        """Test canceling an appointment through the service."""
        service = AppointmentService(db_session)
        
        cancelled_appointment = service.cancel_appointment(sample_appointment.id)
        
        assert cancelled_appointment.status == AppointmentStatus.CANCELLED
    
    def test_check_in_appointment(self, db_session, sample_appointment):
        """Test checking in an appointment through the service."""
        service = AppointmentService(db_session)
        
        from app.schemas.appointment import AppointmentCheckIn
        checkin_data = AppointmentCheckIn(
            confirmation_code=sample_appointment.confirmation_code,
            last_name=sample_appointment.patient.last_name
        )
        checked_in_appointment = service.check_in_appointment(checkin_data)
        
        assert checked_in_appointment.status == AppointmentStatus.CHECKED_IN
        assert checked_in_appointment.check_in_time is not None


class TestDashboardService:
    """Test cases for the DashboardService."""
    
    def test_get_dashboard_metrics(self, db_session, multiple_appointments):
        """Test getting dashboard metrics through the service."""
        service = DashboardService(db_session)
        metrics = service.get_dashboard_stats()
        
        assert "queue_stats" in metrics
        assert "appointment_stats" in metrics
        assert "performance_metrics" in metrics
    
    def test_get_queue_status(self, db_session, sample_queue_entry):
        """Test getting queue status through the service."""
        service = DashboardService(db_session)
        status = service.get_queue_summary()
        
        assert "current_queue" in status
        assert "wait_time_estimates" in status
    
    def test_get_appointment_summary(self, db_session, multiple_appointments):
        """Test getting appointment summary through the service."""
        service = DashboardService(db_session)
        summary = service.get_dashboard_stats()
        
        assert "appointment_stats" in summary
        assert "total_today" in summary["appointment_stats"]
        assert "completed_today" in summary["appointment_stats"]
        assert "cancelled_today" in summary["appointment_stats"]


class TestQueueService:
    """Test cases for the QueueService."""
    
    def test_add_to_queue(self, db_session, sample_patient, sample_appointment):
        """Test adding a patient to the queue through the service."""
        service = QueueService(db_session)
        
        queue_data = {
            "patient_id": sample_patient.id,
            "appointment_id": sample_appointment.id,
            "queue_type": QueueType.APPOINTMENT,
            "status": QueueStatus.WAITING,
            "priority": QueuePriority.MEDIUM,
            "reason": "Test queue entry",
            "estimated_wait_time": 30
        }
        
        queue_entry = service.create_queue_entry(queue_data)
        
        assert queue_entry is not None
        assert queue_entry.patient_id == sample_patient.id
        assert queue_entry.appointment_id == sample_appointment.id
        assert queue_entry.ticket_number is not None
    
    def test_remove_from_queue(self, db_session, sample_queue_entry):
        """Test removing a patient from the queue through the service."""
        service = QueueService(db_session)
        
        result = service.delete_queue_entry(sample_queue_entry.id)
        
        assert result is True
        
        # Verify it's actually removed
        removed_entry = service.get_queue_entry_by_id(sample_queue_entry.id)
        assert removed_entry is None
    
    def test_get_queue_position(self, db_session, sample_queue_entry):
        """Test getting queue position through the service."""
        service = QueueService(db_session)
        
        position_info = service.get_queue_position(sample_queue_entry.ticket_number)
        
        assert "ticket_number" in position_info
        assert "status" in position_info
        assert "position" in position_info
        assert "estimated_wait_time" in position_info
        assert position_info["ticket_number"] == sample_queue_entry.ticket_number
    
    def test_update_queue_entry(self, db_session, sample_queue_entry):
        """Test updating queue entry through the service."""
        service = QueueService(db_session)
        
        update_data = {
            "status": QueueStatus.IN_PROGRESS,
            "priority": QueuePriority.HIGH
        }
        
        updated_entry = service.update_queue_entry(sample_queue_entry.id, update_data)
        
        assert updated_entry.status == QueueStatus.IN_PROGRESS
        assert updated_entry.priority == QueuePriority.HIGH
    
    def test_call_next_patient(self, db_session, sample_queue_entry):
        """Test calling next patient through the service."""
        service = QueueService(db_session)
        
        next_patient = service.get_next_patient()
        
        assert next_patient is not None
        assert next_patient.status == QueueStatus.WAITING
    
    def test_get_dashboard_stats(self, db_session, multiple_appointments):
        """Test getting dashboard stats through the service."""
        service = QueueService(db_session)
        
        stats = service.get_queue_statistics()
        
        assert "total_waiting" in stats
        assert "total_in_progress" in stats
        assert "total_called" in stats


class TestWalkInService:
    """Test cases for the WalkInService."""
    
    def test_register_walkin(self, db_session, walkin_patient_data):
        """Test registering a walk-in patient through the service."""
        service = WalkInService(db_session)
        result = service.register_walkin(walkin_patient_data)
        
        assert "patient_id" in result
        assert "appointment_id" in result
        assert "queue_entry_id" in result
        assert "ticket_number" in result
        assert "confirmation_code" in result
    
    def test_get_walkin_queue(self, db_session, sample_queue_entry):
        """Test getting walk-in queue through the service."""
        service = WalkInService(db_session)
        queue = service.get_walkin_queue()
        
        assert isinstance(queue, list)
    
    def test_process_walkin(self, db_session, sample_appointment):
        """Test processing a walk-in patient through the service."""
        service = WalkInService(db_session)
        result = service.process_walkin(sample_appointment.id)
        
        assert "appointment_id" in result
        assert "status" in result
        assert result["status"] == "in_progress"


class TestNotificationService:
    """Test cases for the NotificationService."""
    
    def test_send_appointment_reminder(self, db_session, sample_appointment):
        """Test sending appointment reminder through the service."""
        service = NotificationService(db_session)
        result = service.send_appointment_reminder(sample_appointment.id)
        
        assert result is not None
    
    def test_send_queue_notification(self, db_session, sample_queue_entry):
        """Test sending queue notification through the service."""
        service = NotificationService(db_session)
        from app.services.notification_service import NotificationType, NotificationChannel
        result = service.send_bulk_notification(
            NotificationType.QUEUE_UPDATE,
            [sample_queue_entry.patient_id],
            "test message",
            [NotificationChannel.SMS]
        )
        
        assert result is not None
    
    def test_send_status_update(self, db_session, sample_patient):
        """Test sending status update through the service."""
        service = NotificationService(db_session)
        # Create a queue entry for the patient first
        from app.models.queue import QueueEntry, QueueType, QueuePriority, QueueStatus
        from app.models.common import generate_ticket_number
        queue_entry = QueueEntry(
            ticket_number=generate_ticket_number(),
            patient_id=sample_patient.id,
            queue_type=QueueType.WALK_IN,
            priority=QueuePriority.MEDIUM,
            status=QueueStatus.WAITING,
            reason="Test"
        )
        db_session.add(queue_entry)
        db_session.commit()
        
        result = service.send_wait_time_update(queue_entry.id, 15)
        
        assert result is not None


class TestServiceIntegration:
    """Integration tests for service layer."""
    
    def test_appointment_to_queue_flow(self, db_session, sample_patient_data):
        """Test the flow from appointment creation to queue management."""
        appointment_service = AppointmentService(db_session)
        queue_service = QueueService(db_session)
        
        # Create patient first
        patient_data = PatientCreate(**sample_patient_data)
        patient = appointment_service._create_patient(patient_data)
        
        # Create appointment
        appointment_data = AppointmentCreate(
            confirmation_code="TEST123",
            patient_id=patient.id,
            provider_name="Dr. Test",
            appointment_type=AppointmentType.ROUTINE,
            scheduled_time=datetime.now() + timedelta(days=1),
            duration_minutes=30,
            reason="Test appointment"
        )
        appointment = appointment_service.create_appointment(appointment_data)
        
        # Check in appointment (creates queue entry)
        checkin_data = AppointmentCheckIn(confirmation_code=appointment.confirmation_code)
        checked_in_appointment = appointment_service.check_in_appointment(checkin_data)
        
        assert checked_in_appointment.status == AppointmentStatus.CHECKED_IN
        
        # Verify queue entry was created
        queue_entries = queue_service.get_queue_entries()
        assert len(queue_entries) > 0
    
    def test_dashboard_data_consistency(self, db_session, multiple_appointments):
        """Test that dashboard data is consistent across services."""
        dashboard_service = DashboardService(db_session)
        queue_service = QueueService(db_session)
        
        dashboard_metrics = dashboard_service.get_dashboard_stats()
        queue_stats = queue_service.get_queue_stats()
        
        # Both should return similar structure
        assert "queue_stats" in dashboard_metrics
        assert "total_waiting" in queue_stats
        assert "appointment_stats" in dashboard_metrics
