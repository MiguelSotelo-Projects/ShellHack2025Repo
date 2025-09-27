from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.patient import Patient
from ..models.appointment import Appointment
from ..models.queue import QueueEntry


def get_patient(patient_id: int, db: Session = Depends(get_db)) -> Patient:
    """Get patient by ID, raise 404 if not found"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    return patient


def get_appointment(appointment_id: int, db: Session = Depends(get_db)) -> Appointment:
    """Get appointment by ID, raise 404 if not found"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    return appointment


def get_appointment_by_code(confirmation_code: str, db: Session = Depends(get_db)) -> Appointment:
    """Get appointment by confirmation code, raise 404 if not found"""
    appointment = db.query(Appointment).filter(
        Appointment.confirmation_code == confirmation_code
    ).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    return appointment


def get_queue_entry(queue_id: int, db: Session = Depends(get_db)) -> QueueEntry:
    """Get queue entry by ID, raise 404 if not found"""
    queue_entry = db.query(QueueEntry).filter(QueueEntry.id == queue_id).first()
    if not queue_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue entry not found"
        )
    return queue_entry


def get_queue_entry_by_ticket(ticket_number: str, db: Session = Depends(get_db)) -> QueueEntry:
    """Get queue entry by ticket number, raise 404 if not found"""
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.ticket_number == ticket_number
    ).first()
    if not queue_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue entry not found"
        )
    return queue_entry
