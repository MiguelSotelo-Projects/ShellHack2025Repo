import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.models.patient import Patient


class TestPatientModel:
    """Test cases for the Patient model."""
    
    def test_patient_creation(self, db_session, sample_patient_data):
        """Test creating a patient with valid data."""
        patient = Patient(**sample_patient_data)
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        
        assert patient.id is not None
        assert patient.first_name == sample_patient_data["first_name"]
        assert patient.last_name == sample_patient_data["last_name"]
        assert patient.phone == sample_patient_data["phone"]
        assert patient.email == sample_patient_data["email"]
        assert patient.medical_record_number == sample_patient_data["medical_record_number"]
        assert patient.created_at is not None
    
    def test_patient_required_fields(self, db_session):
        """Test that required fields are enforced."""
        # Test missing first_name
        patient = Patient(last_name="Doe")
        db_session.add(patient)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Test missing last_name
        patient = Patient(first_name="John")
        db_session.add(patient)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_patient_optional_fields(self, db_session):
        """Test that optional fields can be None."""
        patient = Patient(
            first_name="John",
            last_name="Doe"
        )
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        
        assert patient.date_of_birth is None
        assert patient.phone is None
        assert patient.email is None
        assert patient.emergency_contact is None
        assert patient.medical_record_number is None
        assert patient.insurance_id is None
    
    def test_patient_medical_record_number_unique(self, db_session, sample_patient_data):
        """Test that medical_record_number must be unique."""
        # Create first patient
        patient1 = Patient(**sample_patient_data)
        db_session.add(patient1)
        db_session.commit()
        
        # Try to create second patient with same MRN
        patient2_data = sample_patient_data.copy()
        patient2_data["first_name"] = "Jane"
        patient2_data["last_name"] = "Smith"
        patient2 = Patient(**patient2_data)
        db_session.add(patient2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_patient_repr(self, sample_patient):
        """Test the string representation of a patient."""
        expected_repr = f"<Patient(id={sample_patient.id}, name='{sample_patient.first_name} {sample_patient.last_name}')>"
        assert repr(sample_patient) == expected_repr
    
    def test_patient_relationships(self, db_session, sample_patient):
        """Test patient relationships with appointments and queue entries."""
        # Test that relationships are properly set up
        assert hasattr(sample_patient, 'appointments')
        assert hasattr(sample_patient, 'queue_entries')
        
        # Initially should be empty lists
        assert sample_patient.appointments == []
        assert sample_patient.queue_entries == []
    
    def test_patient_timestamps(self, db_session, sample_patient_data):
        """Test that created_at and updated_at timestamps work correctly."""
        patient = Patient(**sample_patient_data)
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        
        assert patient.created_at is not None
        assert isinstance(patient.created_at, datetime)
        
        # Test updated_at on modification
        original_updated_at = patient.updated_at
        patient.first_name = "Updated Name"
        db_session.commit()
        db_session.refresh(patient)
        
        # updated_at should be set after modification
        assert patient.updated_at is not None
        if original_updated_at is not None:
            assert patient.updated_at > original_updated_at
    
    def test_patient_field_lengths(self, db_session):
        """Test field length constraints."""
        # Test first_name length limit
        long_name = "A" * 101  # Exceeds 100 character limit
        patient = Patient(
            first_name=long_name,
            last_name="Doe"
        )
        db_session.add(patient)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Test last_name length limit
        patient = Patient(
            first_name="John",
            last_name=long_name
        )
        db_session.add(patient)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_patient_email_format(self, db_session):
        """Test that email field accepts various formats."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        for email in valid_emails:
            patient = Patient(
                first_name="John",
                last_name="Doe",
                email=email
            )
            db_session.add(patient)
            db_session.commit()
            db_session.refresh(patient)
            
            assert patient.email == email
            db_session.delete(patient)
            db_session.commit()
    
    def test_patient_phone_format(self, db_session):
        """Test that phone field accepts various formats."""
        valid_phones = [
            "+1-555-123-4567",
            "(555) 123-4567",
            "555.123.4567",
            "5551234567"
        ]
        
        for phone in valid_phones:
            patient = Patient(
                first_name="John",
                last_name="Doe",
                phone=phone
            )
            db_session.add(patient)
            db_session.commit()
            db_session.refresh(patient)
            
            assert patient.phone == phone
            db_session.delete(patient)
            db_session.commit()
    
    def test_patient_date_of_birth(self, db_session):
        """Test date_of_birth field with various date formats."""
        test_date = datetime(1990, 5, 15)
        
        patient = Patient(
            first_name="John",
            last_name="Doe",
            date_of_birth=test_date
        )
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        
        assert patient.date_of_birth == test_date
    
    def test_patient_query_operations(self, db_session, multiple_patients):
        """Test various query operations on patients."""
        # Test filtering by first_name
        first_patient = multiple_patients[0]
        found_patients = db_session.query(Patient).filter(
            Patient.first_name == first_patient.first_name
        ).all()
        
        assert len(found_patients) >= 1
        assert first_patient in found_patients
        
        # Test filtering by medical_record_number
        if first_patient.medical_record_number:
            found_patient = db_session.query(Patient).filter(
                Patient.medical_record_number == first_patient.medical_record_number
            ).first()
            
            assert found_patient == first_patient
        
        # Test ordering
        all_patients = db_session.query(Patient).order_by(Patient.last_name).all()
        assert len(all_patients) == len(multiple_patients)
        
        # Verify ordering
        last_names = [p.last_name for p in all_patients]
        assert last_names == sorted(last_names)
