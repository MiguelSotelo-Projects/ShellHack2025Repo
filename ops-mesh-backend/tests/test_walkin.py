import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.models.patient import Patient
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType


class TestWalkInAPI:
    """Test cases for walk-in API endpoints."""
    
    def test_register_walkin(self, client):
        """Test registering a walk-in patient."""
        walkin_data = {
            "patient": {
                "first_name": "John",
                "last_name": "Doe",
                "phone": "555-1234",
                "email": "john.doe@example.com"
            },
            "reason": "Emergency consultation",
            "priority": "medium"
        }
        
        response = client.post("/api/v1/walkin/", json=walkin_data)
        assert response.status_code == 200
        
        walkin_info = response.json()
        assert "patient_id" in walkin_info
        assert "appointment_id" in walkin_info
        assert "queue_entry_id" in walkin_info
        assert walkin_info["reason"] == "Emergency consultation"
        assert walkin_info["priority"] == "medium"
    
    def test_register_walkin_existing_patient(self, client, sample_patient):
        """Test registering a walk-in for existing patient."""
        walkin_data = {
            "patient_id": sample_patient.id,
            "reason": "Follow-up consultation",
            "priority": 2
        }
        
        response = client.post("/api/v1/walkin/", json=walkin_data)
        assert response.status_code == 200
        
        walkin_info = response.json()
        assert walkin_info["patient_id"] == sample_patient.id
        assert walkin_info["reason"] == "Follow-up consultation"
    
    def test_register_walkin_invalid_data(self, client):
        """Test registering walk-in with invalid data."""
        # Missing required fields
        walkin_data = {
            "reason": "Emergency consultation"
        }
        
        response = client.post("/api/v1/walkin/", json=walkin_data)
        assert response.status_code == 422
    
    def test_register_walkin_invalid_patient_id(self, client):
        """Test registering walk-in with non-existent patient ID."""
        walkin_data = {
            "patient_id": 99999,
            "reason": "Emergency consultation",
            "priority": "medium"
        }
        
        response = client.post("/api/v1/walkin/", json=walkin_data)
        assert response.status_code == 400
    
    def test_get_walkin_queue(self, client, db_session, multiple_patients):
        """Test getting walk-in queue."""
        # Create walk-in queue entries
        from app.models.queue import QueueEntry, QueueType, QueuePriority, QueueStatus
        for i, patient in enumerate(multiple_patients[:3]):
            from app.models.common import generate_ticket_number
            queue_entry = QueueEntry(
                ticket_number=generate_ticket_number(),
                patient_id=patient.id,
                queue_type=QueueType.WALK_IN,
                priority=QueuePriority.MEDIUM,
                status=QueueStatus.WAITING,
                reason="Walk-in consultation"
            )
            db_session.add(queue_entry)
        
        db_session.commit()
        
        response = client.get("/api/v1/walkin/queue")
        assert response.status_code == 200
        
        queue_data = response.json()
        assert len(queue_data) == 3
        
        # Check that all entries are walk-ins
        for entry in queue_data:
            assert "Walk-in" in entry.get("reason", "")
    
    def test_get_walkin_queue_empty(self, client):
        """Test getting empty walk-in queue."""
        response = client.get("/api/v1/walkin/queue")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_process_walkin(self, client, db_session, sample_patient):
        """Test processing a walk-in patient."""
        # Create walk-in appointment
        appointment = Appointment(
            confirmation_code="WALK-0001",
            patient_id=sample_patient.id,
            provider_name="Dr. WalkIn",
            appointment_type=AppointmentType.ROUTINE,
            status=AppointmentStatus.SCHEDULED,
            scheduled_time=datetime.now(),
            reason="Walk-in consultation"
        )
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        response = client.post(f"/api/v1/walkin/{appointment.id}/process")
        assert response.status_code == 200
        
        processed_info = response.json()
        assert processed_info["status"] == "in_progress"
        assert "processed_at" in processed_info
    
    def test_process_walkin_not_found(self, client):
        """Test processing non-existent walk-in."""
        response = client.post("/api/v1/walkin/99999/process")
        assert response.status_code == 404
    
    def test_process_walkin_already_processed(self, client, db_session, sample_patient):
        """Test processing already processed walk-in."""
        # Create walk-in appointment
        appointment = Appointment(
            confirmation_code="WALK-0002",
            patient_id=sample_patient.id,
            provider_name="Dr. WalkIn",
            appointment_type=AppointmentType.ROUTINE,
            status=AppointmentStatus.IN_PROGRESS,
            scheduled_time=datetime.now(),
            reason="Walk-in consultation"
        )
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        response = client.post(f"/api/v1/walkin/{appointment.id}/process")
        assert response.status_code == 400
    
    def test_walkin_priority_handling(self, client, db_session, multiple_patients):
        """Test walk-in priority handling."""
        # Create walk-ins with different priorities
        from app.models.queue import QueueEntry, QueueType, QueuePriority, QueueStatus
        priorities = [QueuePriority.URGENT, QueuePriority.LOW, QueuePriority.HIGH]
        queue_entries = []
        
        for i, (patient, priority) in enumerate(zip(multiple_patients[:3], priorities)):
            from app.models.common import generate_ticket_number
            queue_entry = QueueEntry(
                ticket_number=generate_ticket_number(),
                patient_id=patient.id,
                queue_type=QueueType.WALK_IN,
                priority=priority,
                status=QueueStatus.WAITING,
                reason=f"Walk-in consultation (Priority {priority.value})"
            )
            db_session.add(queue_entry)
            queue_entries.append(queue_entry)
        
        db_session.commit()
        for queue_entry in queue_entries:
            db_session.refresh(queue_entry)
        
        # Get walk-in queue (should be ordered by priority)
        response = client.get("/api/v1/walkin/queue")
        assert response.status_code == 200
        
        queue_data = response.json()
        assert len(queue_data) == 3
    
    def test_walkin_estimated_wait_time(self, client, db_session, sample_patient):
        """Test walk-in estimated wait time."""
        # Create walk-in appointment
        appointment = Appointment(
            confirmation_code="WALK-0003",
            patient_id=sample_patient.id,
            provider_name="Dr. WalkIn",
            appointment_type=AppointmentType.ROUTINE,
            status=AppointmentStatus.SCHEDULED,
            scheduled_time=datetime.now(),
            reason="Walk-in consultation"
        )
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        response = client.get(f"/api/v1/walkin/{appointment.id}/wait-time")
        assert response.status_code == 200
        
        wait_time_data = response.json()
        assert "estimated_wait_time" in wait_time_data
        assert "position_in_queue" in wait_time_data
        assert isinstance(wait_time_data["estimated_wait_time"], int)
    
    def test_walkin_status_updates(self, client, db_session, sample_patient):
        """Test walk-in status updates."""
        # Create walk-in appointment
        appointment = Appointment(
            confirmation_code="WALK-0004",
            patient_id=sample_patient.id,
            provider_name="Dr. WalkIn",
            appointment_type=AppointmentType.ROUTINE,
            status=AppointmentStatus.SCHEDULED,
            scheduled_time=datetime.now(),
            reason="Walk-in consultation"
        )
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        # Update status to confirmed
        response = client.put(f"/api/v1/walkin/{appointment.id}/status", 
                            json={"status": "confirmed"})
        assert response.status_code == 200
        
        status_data = response.json()
        assert status_data["status"] == "confirmed"
    
    def test_walkin_cancellation(self, client, db_session, sample_patient):
        """Test walk-in cancellation."""
        # Create walk-in appointment
        appointment = Appointment(
            confirmation_code="WALK-0005",
            patient_id=sample_patient.id,
            provider_name="Dr. WalkIn",
            appointment_type=AppointmentType.ROUTINE,
            status=AppointmentStatus.SCHEDULED,
            scheduled_time=datetime.now(),
            reason="Walk-in consultation"
        )
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        # Cancel walk-in
        response = client.post(f"/api/v1/walkin/{appointment.id}/cancel")
        assert response.status_code == 200
        
        cancel_data = response.json()
        assert cancel_data["status"] == "cancelled"
    
    def test_walkin_completion(self, client, db_session, sample_patient):
        """Test walk-in completion."""
        # Create walk-in appointment
        appointment = Appointment(
            confirmation_code="WALK-0006",
            patient_id=sample_patient.id,
            provider_name="Dr. WalkIn",
            appointment_type=AppointmentType.ROUTINE,
            status=AppointmentStatus.IN_PROGRESS,
            scheduled_time=datetime.now(),
            reason="Walk-in consultation"
        )
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        # Complete walk-in
        response = client.post(f"/api/v1/walkin/{appointment.id}/complete")
        assert response.status_code == 200
        
        complete_data = response.json()
        assert complete_data["status"] == "completed"
        assert "completed_at" in complete_data
    
    def test_walkin_validation_errors(self, client):
        """Test walk-in validation errors."""
        # Test with invalid priority
        walkin_data = {
            "patient": {
                "first_name": "John",
                "last_name": "Doe"
            },
            "reason": "Emergency consultation",
            "priority": "urgent"  # Should be integer
        }
        
        response = client.post("/api/v1/walkin/", json=walkin_data)
        assert response.status_code == 422
    
    def test_walkin_not_found_errors(self, client):
        """Test walk-in not found errors."""
        # Test getting non-existent walk-in
        response = client.get("/api/v1/walkin/99999")
        assert response.status_code == 404
        
        # Test processing non-existent walk-in
        response = client.post("/api/v1/walkin/99999/process")
        assert response.status_code == 404
        
        # Test updating non-existent walk-in
        response = client.put("/api/v1/walkin/99999/status", json={"status": "confirmed"})
        assert response.status_code == 404
