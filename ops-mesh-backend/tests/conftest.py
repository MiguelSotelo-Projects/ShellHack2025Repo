import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from faker import Faker

from app.main import app
from app.core.database import get_db, Base
from app.models.patient import Patient
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.queue import QueueEntry, QueueStatus, QueueType, QueuePriority

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

fake = Faker()


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_patient_data():
    """Generate sample patient data."""
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=80),
        "phone": fake.phone_number(),
        "email": fake.email(),
        "emergency_contact": fake.name(),
        "medical_record_number": fake.bothify(text="MRN-####"),
        "insurance_id": fake.bothify(text="INS-####")
    }


@pytest.fixture
def sample_patient(db_session, sample_patient_data):
    """Create a sample patient in the database."""
    patient = Patient(**sample_patient_data)
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


@pytest.fixture
def sample_appointment_data(sample_patient):
    """Generate sample appointment data."""
    return {
        "confirmation_code": fake.bothify(text="APT-####"),
        "patient_id": sample_patient.id,
        "provider_name": fake.name(),
        "appointment_type": AppointmentType.ROUTINE,
        "status": AppointmentStatus.SCHEDULED,
        "scheduled_time": fake.future_datetime(),
        "duration_minutes": 30,
        "reason": fake.sentence(),
        "notes": fake.text()
    }


@pytest.fixture
def sample_appointment(db_session, sample_appointment_data):
    """Create a sample appointment in the database."""
    appointment = Appointment(**sample_appointment_data)
    db_session.add(appointment)
    db_session.commit()
    db_session.refresh(appointment)
    return appointment


@pytest.fixture
def multiple_patients(db_session):
    """Create multiple patients for testing."""
    patients = []
    for _ in range(5):
        patient_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=80),
            "phone": fake.phone_number(),
            "email": fake.email(),
            "medical_record_number": fake.bothify(text="MRN-####")
        }
        patient = Patient(**patient_data)
        db_session.add(patient)
        patients.append(patient)
    
    db_session.commit()
    for patient in patients:
        db_session.refresh(patient)
    return patients


@pytest.fixture
def multiple_appointments(db_session, multiple_patients):
    """Create multiple appointments for testing."""
    appointments = []
    for i, patient in enumerate(multiple_patients):
        appointment_data = {
            "confirmation_code": fake.bothify(text=f"APT-{i:04d}"),
            "patient_id": patient.id,
            "provider_name": fake.name(),
            "appointment_type": AppointmentType.ROUTINE,
            "status": AppointmentStatus.SCHEDULED,
            "scheduled_time": fake.future_datetime(),
            "duration_minutes": 30,
            "reason": fake.sentence()
        }
        appointment = Appointment(**appointment_data)
        db_session.add(appointment)
        appointments.append(appointment)
    
    db_session.commit()
    for appointment in appointments:
        db_session.refresh(appointment)
    return appointments


@pytest.fixture
def sample_queue_entry_data(sample_patient, sample_appointment):
    """Generate sample queue entry data."""
    return {
        "ticket_number": fake.bothify(text="Q-####"),
        "patient_id": sample_patient.id,
        "appointment_id": sample_appointment.id,
        "queue_type": QueueType.APPOINTMENT,
        "status": QueueStatus.WAITING,
        "priority": QueuePriority.MEDIUM,
        "reason": fake.sentence(),
        "estimated_wait_time": 30
    }


@pytest.fixture
def sample_queue_entry(db_session, sample_queue_entry_data):
    """Create a sample queue entry in the database."""
    queue_entry = QueueEntry(**sample_queue_entry_data)
    db_session.add(queue_entry)
    db_session.commit()
    db_session.refresh(queue_entry)
    return queue_entry


@pytest.fixture
def walkin_patient_data():
    """Generate walk-in patient data."""
    return {
        "patient": {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=80),
            "phone": fake.phone_number(),
            "email": fake.email(),
            "emergency_contact": fake.name(),
            "medical_record_number": fake.bothify(text="MRN-####"),
            "insurance_id": fake.bothify(text="INS-####")
        },
        "reason": fake.sentence(),
        "priority": QueuePriority.MEDIUM
    }
