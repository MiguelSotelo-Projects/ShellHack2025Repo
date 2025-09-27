#!/usr/bin/env python3
"""
Seed database with realistic mock data
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from app.models.patient import Patient
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.queue import QueueEntry, QueueType, QueueStatus, QueuePriority
from app.models.common import generate_confirmation_code, generate_ticket_number

# Sample data
FIRST_NAMES = [
    "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Jessica",
    "William", "Ashley", "James", "Amanda", "Christopher", "Jennifer", "Daniel",
    "Lisa", "Matthew", "Nancy", "Anthony", "Karen", "Mark", "Betty", "Donald",
    "Helen", "Steven", "Sandra", "Paul", "Donna", "Andrew", "Carol", "Joshua",
    "Ruth", "Kenneth", "Sharon", "Kevin", "Michelle", "Brian", "Laura", "George",
    "Sarah", "Edward", "Kimberly", "Ronald", "Deborah", "Timothy", "Dorothy"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
]

PROVIDERS = [
    "Dr. Sarah Johnson", "Dr. Michael Chen", "Dr. Emily Rodriguez", "Dr. David Kim",
    "Dr. Lisa Thompson", "Dr. Robert Martinez", "Dr. Jennifer Lee", "Dr. Christopher Brown",
    "Dr. Amanda Wilson", "Dr. Daniel Garcia", "Dr. Jessica Davis", "Dr. Matthew Taylor"
]

REASONS = [
    "Annual physical exam", "Follow-up appointment", "Blood pressure check", "Diabetes management",
    "Cold symptoms", "Headache", "Back pain", "Knee pain", "Skin rash", "Allergy symptoms",
    "Medication review", "Vaccination", "Lab results review", "X-ray follow-up",
    "Physical therapy referral", "Specialist consultation", "Pre-operative clearance"
]

URGENT_REASONS = [
    "Chest pain", "Severe headache", "Difficulty breathing", "High fever",
    "Severe abdominal pain", "Allergic reaction", "Injury", "Dizziness"
]


def create_patients(db, count=50):
    """Create sample patients"""
    patients = []
    
    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        
        # Generate realistic phone number
        phone = f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
        
        # Generate email
        email = f"{first_name.lower()}.{last_name.lower()}@email.com"
        
        # Generate medical record number
        mrn = f"MRN{random.randint(100000, 999999)}"
        
        patient = Patient(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=datetime.now() - timedelta(days=random.randint(18*365, 80*365)),
            phone=phone,
            email=email,
            medical_record_number=mrn,
            insurance_id=f"INS{random.randint(100000, 999999)}"
        )
        
        db.add(patient)
        patients.append(patient)
    
    db.commit()
    return patients


def create_appointments(db, patients, count=30):
    """Create sample appointments"""
    appointments = []
    
    for i in range(count):
        patient = random.choice(patients)
        provider = random.choice(PROVIDERS)
        reason = random.choice(REASONS)
        
        # Schedule appointments in the next 30 days
        scheduled_time = datetime.now() + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(8, 17),
            minutes=random.choice([0, 15, 30, 45])
        )
        
        # Random appointment type
        appointment_type = random.choice(list(AppointmentType))
        
        # Random status (mostly scheduled, some confirmed)
        status = random.choices(
            [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED],
            weights=[70, 30]
        )[0]
        
        appointment = Appointment(
            confirmation_code=generate_confirmation_code(),
            patient_id=patient.id,
            provider_name=provider,
            appointment_type=appointment_type,
            status=status,
            scheduled_time=scheduled_time,
            duration_minutes=random.choice([15, 30, 45, 60]),
            reason=reason
        )
        
        db.add(appointment)
        appointments.append(appointment)
    
    db.commit()
    return appointments


def create_queue_entries(db, patients, appointments, count=20):
    """Create sample queue entries"""
    queue_entries = []
    
    for i in range(count):
        # Mix of walk-ins and appointments
        if random.random() < 0.6:  # 60% walk-ins
            patient = random.choice(patients)
            appointment = None
            queue_type = QueueType.WALK_IN
            reason = random.choice(REASONS + URGENT_REASONS)
        else:  # 40% appointments
            appointment = random.choice(appointments)
            patient = appointment.patient
            queue_type = QueueType.APPOINTMENT
            reason = appointment.reason
        
        # Random priority
        priority = random.choices(
            list(QueuePriority),
            weights=[20, 50, 25, 5]  # low, medium, high, urgent
        )[0]
        
        # Random status
        status = random.choices(
            [QueueStatus.WAITING, QueueStatus.CALLED, QueueStatus.IN_PROGRESS, QueueStatus.COMPLETED],
            weights=[40, 20, 20, 20]
        )[0]
        
        # Generate ticket number
        ticket_number = generate_ticket_number()
        
        # Ensure unique ticket number
        while db.query(QueueEntry).filter(QueueEntry.ticket_number == ticket_number).first():
            ticket_number = generate_ticket_number()
        
        # Set timestamps based on status
        created_at = datetime.now() - timedelta(minutes=random.randint(5, 120))
        called_at = None
        started_at = None
        completed_at = None
        actual_wait_time = None
        
        if status in [QueueStatus.CALLED, QueueStatus.IN_PROGRESS, QueueStatus.COMPLETED]:
            called_at = created_at + timedelta(minutes=random.randint(5, 30))
        
        if status in [QueueStatus.IN_PROGRESS, QueueStatus.COMPLETED]:
            started_at = called_at + timedelta(minutes=random.randint(1, 10))
            actual_wait_time = int((started_at - created_at).total_seconds() / 60)
        
        if status == QueueStatus.COMPLETED:
            completed_at = started_at + timedelta(minutes=random.randint(10, 60))
        
        queue_entry = QueueEntry(
            ticket_number=ticket_number,
            patient_id=patient.id,
            appointment_id=appointment.id if appointment else None,
            queue_type=queue_type,
            status=status,
            priority=priority,
            reason=reason,
            estimated_wait_time=random.randint(15, 60),
            actual_wait_time=actual_wait_time,
            called_at=called_at,
            started_at=started_at,
            completed_at=completed_at,
            created_at=created_at
        )
        
        db.add(queue_entry)
        queue_entries.append(queue_entry)
    
    db.commit()
    return queue_entries


def main():
    """Main seeding function"""
    print("🌱 Seeding database with mock data...")
    
    # Create database tables
    from app.core.database import Base
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create patients
        print("Creating patients...")
        patients = create_patients(db, count=50)
        print(f"✅ Created {len(patients)} patients")
        
        # Create appointments
        print("Creating appointments...")
        appointments = create_appointments(db, patients, count=30)
        print(f"✅ Created {len(appointments)} appointments")
        
        # Create queue entries
        print("Creating queue entries...")
        queue_entries = create_queue_entries(db, patients, appointments, count=20)
        print(f"✅ Created {len(queue_entries)} queue entries")
        
        print("\n🎉 Database seeded successfully!")
        print(f"📊 Summary:")
        print(f"   - Patients: {len(patients)}")
        print(f"   - Appointments: {len(appointments)}")
        print(f"   - Queue entries: {len(queue_entries)}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

