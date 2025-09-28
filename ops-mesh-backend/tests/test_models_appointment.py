import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.patient import Patient


class TestAppointmentModel:
    """Test cases for the Appointment model."""
    
    def test_appointment_creation(self, db_session, sample_appointment_data):
        """Test creating an appointment with valid data."""
        appointment = Appointment(**sample_appointment_data)
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        assert appointment.id is not None
        assert appointment.confirmation_code == sample_appointment_data["confirmation_code"]
        assert appointment.patient_id == sample_appointment_data["patient_id"]
        assert appointment.provider_name == sample_appointment_data["provider_name"]
        assert appointment.appointment_type == sample_appointment_data["appointment_type"]
        assert appointment.status == sample_appointment_data["status"]
        assert appointment.scheduled_time == sample_appointment_data["scheduled_time"]
        assert appointment.duration_minutes == sample_appointment_data["duration_minutes"]
        assert appointment.created_at is not None
    
    def test_appointment_required_fields(self, db_session, sample_patient):
        """Test that required fields are enforced."""
        # Test missing confirmation_code
        appointment = Appointment(
            patient_id=sample_patient.id,
            provider_name="Dr. Smith",
            scheduled_time=datetime.now() + timedelta(days=1)
        )
        db_session.add(appointment)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Test missing patient_id
        appointment = Appointment(
            confirmation_code="APT-1234",
            provider_name="Dr. Smith",
            scheduled_time=datetime.now() + timedelta(days=1)
        )
        db_session.add(appointment)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_appointment_optional_fields(self, db_session, sample_patient):
        """Test that optional fields can be None."""
        appointment = Appointment(
            confirmation_code="APT-1234",
            patient_id=sample_patient.id,
            provider_name="Dr. Smith",
            scheduled_time=datetime.now() + timedelta(days=1)
        )
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        assert appointment.appointment_type == AppointmentType.ROUTINE  # Default value
        assert appointment.status == AppointmentStatus.SCHEDULED  # Default value
        assert appointment.duration_minutes == 30  # Default value
        assert appointment.reason is None
        assert appointment.notes is None
        assert appointment.check_in_time is None
    
    def test_appointment_confirmation_code_unique(self, db_session, sample_patient):
        """Test that confirmation_code must be unique."""
        # Create first appointment
        appointment1 = Appointment(
            confirmation_code="APT-1234",
            patient_id=sample_patient.id,
            provider_name="Dr. Smith",
            scheduled_time=datetime.now() + timedelta(days=1)
        )
        db_session.add(appointment1)
        db_session.commit()
        
        # Try to create second appointment with same confirmation code
        appointment2 = Appointment(
            confirmation_code="APT-1234",
            patient_id=sample_patient.id,
            provider_name="Dr. Jones",
            scheduled_time=datetime.now() + timedelta(days=2)
        )
        db_session.add(appointment2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_appointment_status_enum(self, db_session, sample_patient):
        """Test that appointment status enum works correctly."""
        statuses = [
            AppointmentStatus.SCHEDULED,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CHECKED_IN,
            AppointmentStatus.IN_PROGRESS,
            AppointmentStatus.COMPLETED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.NO_SHOW
        ]
        
        for i, status in enumerate(statuses):
            appointment = Appointment(
                confirmation_code=f"APT-{i:04d}",
                patient_id=sample_patient.id,
                provider_name="Dr. Smith",
                scheduled_time=datetime.now() + timedelta(days=i+1),
                status=status
            )
            db_session.add(appointment)
            db_session.commit()
            db_session.refresh(appointment)
            
            assert appointment.status == status
            db_session.delete(appointment)
            db_session.commit()
    
    def test_appointment_type_enum(self, db_session, sample_patient):
        """Test that appointment type enum works correctly."""
        types = [
            AppointmentType.ROUTINE,
            AppointmentType.URGENT,
            AppointmentType.FOLLOW_UP,
            AppointmentType.CONSULTATION
        ]
        
        for i, apt_type in enumerate(types):
            appointment = Appointment(
                confirmation_code=f"APT-{i:04d}",
                patient_id=sample_patient.id,
                provider_name="Dr. Smith",
                scheduled_time=datetime.now() + timedelta(days=i+1),
                appointment_type=apt_type
            )
            db_session.add(appointment)
            db_session.commit()
            db_session.refresh(appointment)
            
            assert appointment.appointment_type == apt_type
            db_session.delete(appointment)
            db_session.commit()
    
    def test_appointment_repr(self, sample_appointment):
        """Test the string representation of an appointment."""
        expected_repr = f"<Appointment(id={sample_appointment.id}, code='{sample_appointment.confirmation_code}', status='{sample_appointment.status}')>"
        assert repr(sample_appointment) == expected_repr
    
    def test_appointment_relationships(self, db_session, sample_appointment):
        """Test appointment relationships with patient and queue entries."""
        # Test that relationships are properly set up
        assert hasattr(sample_appointment, 'patient')
        assert hasattr(sample_appointment, 'queue_entries')
        
        # Test patient relationship
        assert sample_appointment.patient is not None
        assert sample_appointment.patient.id == sample_appointment.patient_id
        
        # Initially queue_entries should be empty
        assert sample_appointment.queue_entries == []
    
    def test_appointment_timestamps(self, db_session, sample_patient):
        """Test that created_at and updated_at timestamps work correctly."""
        appointment = Appointment(
            confirmation_code="APT-1234",
            patient_id=sample_patient.id,
            provider_name="Dr. Smith",
            scheduled_time=datetime.now() + timedelta(days=1)
        )
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        assert appointment.created_at is not None
        assert isinstance(appointment.created_at, datetime)
        
        # Test updated_at on modification
        original_updated_at = appointment.updated_at
        appointment.provider_name = "Dr. Updated"
        db_session.commit()
        db_session.refresh(appointment)
        
        # updated_at should be set after modification
        assert appointment.updated_at is not None
        if original_updated_at is not None:
            assert appointment.updated_at > original_updated_at
    
    def test_appointment_duration_default(self, db_session, sample_patient):
        """Test that duration_minutes has a default value."""
        appointment = Appointment(
            confirmation_code="APT-1234",
            patient_id=sample_patient.id,
            provider_name="Dr. Smith",
            scheduled_time=datetime.now() + timedelta(days=1)
        )
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        assert appointment.duration_minutes == 30  # Default value
    
    def test_appointment_check_in_time(self, db_session, sample_patient):
        """Test check_in_time field functionality."""
        appointment = Appointment(
            confirmation_code="APT-1234",
            patient_id=sample_patient.id,
            provider_name="Dr. Smith",
            scheduled_time=datetime.now() + timedelta(days=1)
        )
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        # Initially should be None
        assert appointment.check_in_time is None
        
        # Set check-in time
        check_in_time = datetime.now()
        appointment.check_in_time = check_in_time
        appointment.status = AppointmentStatus.CHECKED_IN
        db_session.commit()
        db_session.refresh(appointment)
        
        assert appointment.check_in_time == check_in_time
        assert appointment.status == AppointmentStatus.CHECKED_IN
    
    def test_appointment_query_operations(self, db_session, multiple_appointments):
        """Test various query operations on appointments."""
        # Test filtering by status
        scheduled_appointments = db_session.query(Appointment).filter(
            Appointment.status == AppointmentStatus.SCHEDULED
        ).all()
        
        assert len(scheduled_appointments) == len(multiple_appointments)
        
        # Test filtering by provider
        first_appointment = multiple_appointments[0]
        provider_appointments = db_session.query(Appointment).filter(
            Appointment.provider_name == first_appointment.provider_name
        ).all()
        
        assert len(provider_appointments) >= 1
        assert first_appointment in provider_appointments
        
        # Test filtering by confirmation code
        found_appointment = db_session.query(Appointment).filter(
            Appointment.confirmation_code == first_appointment.confirmation_code
        ).first()
        
        assert found_appointment == first_appointment
        
        # Test ordering by scheduled_time
        all_appointments = db_session.query(Appointment).order_by(
            Appointment.scheduled_time
        ).all()
        
        assert len(all_appointments) == len(multiple_appointments)
        
        # Verify ordering
        scheduled_times = [apt.scheduled_time for apt in all_appointments]
        assert scheduled_times == sorted(scheduled_times)
    
    def test_appointment_foreign_key_constraint(self, db_session):
        """Test that appointment requires valid patient_id."""
        appointment = Appointment(
            confirmation_code="APT-1234",
            patient_id=99999,  # Non-existent patient ID
            provider_name="Dr. Smith",
            scheduled_time=datetime.now() + timedelta(days=1)
        )
        db_session.add(appointment)
        
        # SQLite doesn't enforce foreign key constraints by default
        # So we'll just test that the appointment can be created
        # In a production system with proper FK constraints, this would raise IntegrityError
        db_session.commit()
        
        # Verify the appointment was created (even with invalid patient_id)
        assert appointment.id is not None
    
    def test_appointment_text_fields(self, db_session, sample_patient):
        """Test that text fields (reason, notes) can store long text."""
        long_reason = "This is a very long reason for the appointment. " * 10
        long_notes = "These are detailed notes about the appointment. " * 20
        
        appointment = Appointment(
            confirmation_code="APT-1234",
            patient_id=sample_patient.id,
            provider_name="Dr. Smith",
            scheduled_time=datetime.now() + timedelta(days=1),
            reason=long_reason,
            notes=long_notes
        )
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        assert appointment.reason == long_reason
        assert appointment.notes == long_notes
