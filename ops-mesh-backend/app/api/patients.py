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
