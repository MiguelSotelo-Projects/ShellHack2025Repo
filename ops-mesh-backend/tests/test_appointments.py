import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.models.appointment import AppointmentStatus, AppointmentType
from app.models.patient import Patient


class TestAppointmentAPI:
    """Test cases for appointment API endpoints."""
    
    def test_get_appointments_empty(self, client):
        """Test getting appointments when none exist."""
        response = client.get("/api/v1/appointments/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_appointments_with_data(self, client, multiple_appointments):
        """Test getting appointments when data exists."""
        response = client.get("/api/v1/appointments/")
        assert response.status_code == 200
        
        appointments = response.json()
        assert len(appointments) == len(multiple_appointments)
        
        # Check that all required fields are present
        for appointment in appointments:
            assert "id" in appointment
            assert "confirmation_code" in appointment
            assert "status" in appointment
            assert "scheduled_time" in appointment
            assert "provider_name" in appointment
            assert "patient_name" in appointment
    
    def test_get_appointments_with_pagination(self, client, multiple_appointments):
        """Test getting appointments with pagination."""
        response = client.get("/api/v1/appointments/?skip=0&limit=2")
        assert response.status_code == 200
        
        appointments = response.json()
        assert len(appointments) <= 2
        
        # Test skip parameter
        response = client.get("/api/v1/appointments/?skip=2&limit=2")
        assert response.status_code == 200
        
        appointments = response.json()
        assert len(appointments) <= 2
    
    def test_get_appointments_filter_by_status(self, client, multiple_appointments):
        """Test filtering appointments by status."""
        response = client.get("/api/v1/appointments/?status=scheduled")
        assert response.status_code == 200
        
        appointments = response.json()
        for appointment in appointments:
            assert appointment["status"] == "scheduled"
    
    def test_get_appointment_by_id(self, client, sample_appointment):
        """Test getting a specific appointment by ID."""
        response = client.get(f"/api/v1/appointments/{sample_appointment.id}")
        assert response.status_code == 200
        
        appointment = response.json()
        assert appointment["id"] == sample_appointment.id
        assert appointment["confirmation_code"] == sample_appointment.confirmation_code
    
    def test_get_appointment_by_id_not_found(self, client):
        """Test getting a non-existent appointment by ID."""
        response = client.get("/api/v1/appointments/99999")
        assert response.status_code == 404
    
    def test_get_appointment_by_code(self, client, sample_appointment):
        """Test getting a specific appointment by confirmation code."""
        response = client.get(f"/api/v1/appointments/code/{sample_appointment.confirmation_code}")
        assert response.status_code == 200
        
        appointment = response.json()
        assert appointment["id"] == sample_appointment.id
        assert appointment["confirmation_code"] == sample_appointment.confirmation_code
    
    def test_get_appointment_by_code_not_found(self, client):
        """Test getting a non-existent appointment by confirmation code."""
        response = client.get("/api/v1/appointments/code/NONEXISTENT")
        assert response.status_code == 404
    
    def test_create_appointment(self, client, sample_patient):
        """Test creating a new appointment."""
        appointment_data = {
            "patient_id": sample_patient.id,
            "provider_name": "Dr. Test",
            "appointment_type": "routine",
            "scheduled_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "duration_minutes": 45,
            "reason": "Regular checkup",
            "notes": "Patient requested morning appointment"
        }
        
        response = client.post("/api/v1/appointments/", json=appointment_data)
        assert response.status_code == 201
        
        appointment = response.json()
        assert appointment["patient_id"] == sample_patient.id
        assert appointment["provider_name"] == "Dr. Test"
        assert appointment["appointment_type"] == "routine"
        assert appointment["status"] == "scheduled"
        assert appointment["duration_minutes"] == 45
        assert "confirmation_code" in appointment
        assert "id" in appointment
    
    def test_create_appointment_with_patient_creation(self, client):
        """Test creating an appointment with new patient."""
        appointment_data = {
            "patient": {
                "first_name": "Jane",
                "last_name": "Doe",
                "phone": "555-1234",
                "email": "jane.doe@example.com"
            },
            "provider_name": "Dr. Test",
            "appointment_type": "urgent",
            "scheduled_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "reason": "Emergency consultation"
        }
        
        response = client.post("/api/v1/appointments/", json=appointment_data)
        assert response.status_code == 201
        
        appointment = response.json()
        assert appointment["provider_name"] == "Dr. Test"
        assert appointment["appointment_type"] == "urgent"
        assert "patient_id" in appointment
        assert "confirmation_code" in appointment
    
    def test_create_appointment_invalid_data(self, client):
        """Test creating an appointment with invalid data."""
        # Missing required fields
        appointment_data = {
            "provider_name": "Dr. Test"
        }
        
        response = client.post("/api/v1/appointments/", json=appointment_data)
        assert response.status_code == 400
    
    def test_create_appointment_invalid_patient_id(self, client):
        """Test creating an appointment with non-existent patient ID."""
        appointment_data = {
            "patient_id": 99999,
            "provider_name": "Dr. Test",
            "scheduled_time": (datetime.now() + timedelta(days=1)).isoformat()
        }
        
        response = client.post("/api/v1/appointments/", json=appointment_data)
        assert response.status_code == 404
    
    def test_update_appointment(self, client, sample_appointment):
        """Test updating an existing appointment."""
        update_data = {
            "provider_name": "Dr. Updated",
            "status": "confirmed",
            "notes": "Updated notes"
        }
        
        response = client.put(f"/api/v1/appointments/{sample_appointment.id}", json=update_data)
        assert response.status_code == 200
        
        appointment = response.json()
        assert appointment["provider_name"] == "Dr. Updated"
        assert appointment["status"] == "confirmed"
        assert appointment["notes"] == "Updated notes"
    
    def test_update_appointment_not_found(self, client):
        """Test updating a non-existent appointment."""
        update_data = {
            "provider_name": "Dr. Updated"
        }
        
        response = client.put("/api/v1/appointments/99999", json=update_data)
        assert response.status_code == 404
    
    def test_check_in_appointment(self, client, sample_appointment):
        """Test checking in an appointment."""
        response = client.post(f"/api/v1/appointments/{sample_appointment.id}/checkin")
        assert response.status_code == 200
        
        appointment = response.json()
        assert appointment["status"] == "checked_in"
        assert "check_in_time" in appointment
    
    def test_check_in_appointment_not_found(self, client):
        """Test checking in a non-existent appointment."""
        response = client.post("/api/v1/appointments/99999/checkin")
        assert response.status_code == 404
    
    def test_check_in_appointment_already_checked_in(self, client, sample_appointment):
        """Test checking in an appointment that's already checked in."""
        # First check-in
        response = client.post(f"/api/v1/appointments/{sample_appointment.id}/checkin")
        assert response.status_code == 200
        
        # Second check-in should fail
        response = client.post(f"/api/v1/appointments/{sample_appointment.id}/checkin")
        assert response.status_code == 400
    
    def test_cancel_appointment(self, client, sample_appointment):
        """Test canceling an appointment."""
        response = client.post(f"/api/v1/appointments/{sample_appointment.id}/cancel")
        assert response.status_code == 200
        
        appointment = response.json()
        assert appointment["status"] == "cancelled"
    
    def test_cancel_appointment_not_found(self, client):
        """Test canceling a non-existent appointment."""
        response = client.post("/api/v1/appointments/99999/cancel")
        assert response.status_code == 404
    
    def test_cancel_appointment_already_cancelled(self, client, sample_appointment):
        """Test canceling an appointment that's already cancelled."""
        # First cancel
        response = client.post(f"/api/v1/appointments/{sample_appointment.id}/cancel")
        assert response.status_code == 200
        
        # Second cancel should fail
        response = client.post(f"/api/v1/appointments/{sample_appointment.id}/cancel")
        assert response.status_code == 400
    
    def test_delete_appointment(self, client, sample_appointment):
        """Test deleting an appointment."""
        response = client.delete(f"/api/v1/appointments/{sample_appointment.id}")
        assert response.status_code == 200
        
        # Verify appointment is deleted
        response = client.get(f"/api/v1/appointments/{sample_appointment.id}")
        assert response.status_code == 404
    
    def test_delete_appointment_not_found(self, client):
        """Test deleting a non-existent appointment."""
        response = client.delete("/api/v1/appointments/99999")
        assert response.status_code == 404
    
    def test_appointment_status_transitions(self, client, sample_appointment):
        """Test various appointment status transitions."""
        # Start with scheduled
        assert sample_appointment.status == AppointmentStatus.SCHEDULED
        
        # Confirm appointment
        response = client.put(f"/api/v1/appointments/{sample_appointment.id}", 
                            json={"status": "confirmed"})
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"
        
        # Check in
        response = client.post(f"/api/v1/appointments/{sample_appointment.id}/checkin")
        assert response.status_code == 200
        assert response.json()["status"] == "checked_in"
        
        # Mark as in progress
        response = client.put(f"/api/v1/appointments/{sample_appointment.id}", 
                            json={"status": "in_progress"})
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"
        
        # Complete
        response = client.put(f"/api/v1/appointments/{sample_appointment.id}", 
                            json={"status": "completed"})
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
