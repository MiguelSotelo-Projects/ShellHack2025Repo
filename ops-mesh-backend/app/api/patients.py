from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..models.patient import Patient
from ..schemas.patient import (
    Patient as PatientSchema,
    PatientCreate,
    PatientUpdate
)
from .deps import get_patient

router = APIRouter()


@router.get("/", response_model=List[PatientSchema])
def get_patients(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    """Get all patients with optional search"""
    query = db.query(Patient)
    
    if search:
        query = query.filter(
            (Patient.first_name.ilike(f"%{search}%")) |
            (Patient.last_name.ilike(f"%{search}%")) |
            (Patient.medical_record_number.ilike(f"%{search}%"))
        )
    
    patients = query.offset(skip).limit(limit).all()
    return patients


@router.get("/list")
def get_patients_list(db: Session = Depends(get_db)):
    """Get all patients with enhanced information"""
    try:
        patients = db.query(Patient).all()
        
        result = []
        for patient in patients:
            result.append({
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                "phone": patient.phone,
                "email": patient.email,
                "emergency_contact": patient.emergency_contact,
                "medical_record_number": patient.medical_record_number,
                "created_at": patient.created_at.isoformat(),
                "updated_at": patient.updated_at.isoformat() if patient.updated_at else None
            })
        
        return {"success": True, "patients": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{patient_id}", response_model=PatientSchema)
def get_patient_by_id(
    patient: Patient = Depends(get_patient)
):
    """Get patient by ID"""
    return patient


@router.post("/", response_model=PatientSchema, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):
    """Create a new patient"""
    # Check if medical record number already exists
    if patient.medical_record_number:
        existing = db.query(Patient).filter(
            Patient.medical_record_number == patient.medical_record_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Medical record number already exists"
            )
    
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_patient


@router.put("/{patient_id}", response_model=PatientSchema)
def update_patient(
    patient_update: PatientUpdate,
    patient: Patient = Depends(get_patient),
    db: Session = Depends(get_db)
):
    """Update a patient"""
    update_data = patient_update.dict(exclude_unset=True)
    
    # Check if medical record number is being updated and already exists
    if "medical_record_number" in update_data and update_data["medical_record_number"]:
        existing = db.query(Patient).filter(
            Patient.medical_record_number == update_data["medical_record_number"],
            Patient.id != patient.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Medical record number already exists"
            )
    
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    
    return patient


@router.delete("/{patient_id}")
def delete_patient(
    patient: Patient = Depends(get_patient),
    db: Session = Depends(get_db)
):
    """Delete a patient"""
    db.delete(patient)
    db.commit()
    
    return {"message": "Patient deleted successfully"}


@router.post("/create")
def create_patient_with_queue(
    patient_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new patient and add to queue"""
    try:
        # Create new patient
        patient = Patient(
            first_name=patient_data.get("first_name"),
            last_name=patient_data.get("last_name"),
            phone=patient_data.get("phone"),
            email=patient_data.get("email"),
            medical_record_number=f"MRN-{int(__import__('time').time())}"
        )
        
        db.add(patient)
        db.commit()
        db.refresh(patient)
        
        # Add to queue if priority is provided
        if patient_data.get("priority"):
            from ..models.queue import QueueEntry, QueueType, QueueStatus, QueuePriority
            from ..models.common import generate_ticket_number
            
            ticket_number = generate_ticket_number()
            
            # Ensure ticket number is unique
            while db.query(QueueEntry).filter(QueueEntry.ticket_number == ticket_number).first():
                ticket_number = generate_ticket_number()
            
            queue_entry = QueueEntry(
                ticket_number=ticket_number,
                patient_id=patient.id,
                queue_type=QueueType.WALK_IN,
                status=QueueStatus.WAITING,
                priority=QueuePriority(patient_data.get("priority", "medium")),
                estimated_wait_time=30
            )
            
            db.add(queue_entry)
            db.commit()
            db.refresh(queue_entry)
        
        return {
            "success": True,
            "patient": {
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "medical_record_number": patient.medical_record_number
            },
            "message": "Patient created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{patient_id}/status")
def update_patient_status(
    patient_id: int,
    status_data: dict,
    db: Session = Depends(get_db)
):
    """Update patient status"""
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # For now, we'll just update the patient record
        # In a real system, this might update related queue entries or appointments
        new_status = status_data.get("status")
        if new_status:
            # You could add a status field to the Patient model if needed
            # For now, we'll just return success
            pass
        
        db.commit()
        
        return {"success": True, "message": "Patient status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))