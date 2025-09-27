from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Dict, Any

from ..core.database import get_db
from ..models.queue import QueueEntry, QueueStatus, QueueType
from ..models.appointment import Appointment, AppointmentStatus
from ..models.patient import Patient

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics and KPIs"""
    
    # Current queue stats
    total_waiting = db.query(QueueEntry).filter(QueueEntry.status == QueueStatus.WAITING).count()
    total_in_progress = db.query(QueueEntry).filter(QueueEntry.status == QueueStatus.IN_PROGRESS).count()
    total_called = db.query(QueueEntry).filter(QueueEntry.status == QueueStatus.CALLED).count()
    
    # Queue by type
    walk_ins_waiting = db.query(QueueEntry).filter(
        QueueEntry.status == QueueStatus.WAITING,
        QueueEntry.queue_type == QueueType.WALK_IN
    ).count()
    
    appointments_waiting = db.query(QueueEntry).filter(
        QueueEntry.status == QueueStatus.WAITING,
        QueueEntry.queue_type == QueueType.APPOINTMENT
    ).count()
    
    # Priority breakdown
    urgent_waiting = db.query(QueueEntry).filter(
        QueueEntry.status == QueueStatus.WAITING,
        QueueEntry.priority == "urgent"
    ).count()
    
    high_waiting = db.query(QueueEntry).filter(
        QueueEntry.status == QueueStatus.WAITING,
        QueueEntry.priority == "high"
    ).count()
    
    # Average wait time (for completed entries)
    avg_wait_time = db.query(func.avg(QueueEntry.actual_wait_time)).filter(
        QueueEntry.actual_wait_time.isnot(None)
    ).scalar() or 0
    
    # Today's appointments
    today = datetime.utcnow().date()
    appointments_today = db.query(Appointment).filter(
        func.date(Appointment.scheduled_time) == today
    ).count()
    
    appointments_checked_in = db.query(Appointment).filter(
        func.date(Appointment.scheduled_time) == today,
        Appointment.status == AppointmentStatus.CHECKED_IN
    ).count()
    
    appointments_completed = db.query(Appointment).filter(
        func.date(Appointment.scheduled_time) == today,
        Appointment.status == AppointmentStatus.COMPLETED
    ).count()
    
    # Recent activity (last hour)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_check_ins = db.query(QueueEntry).filter(
        QueueEntry.created_at >= one_hour_ago
    ).count()
    
    recent_completions = db.query(QueueEntry).filter(
        QueueEntry.completed_at >= one_hour_ago
    ).count()
    
    return {
        "queue_stats": {
            "total_waiting": total_waiting,
            "total_in_progress": total_in_progress,
            "total_called": total_called,
            "walk_ins_waiting": walk_ins_waiting,
            "appointments_waiting": appointments_waiting,
            "urgent_waiting": urgent_waiting,
            "high_waiting": high_waiting
        },
        "appointment_stats": {
            "total_today": appointments_today,
            "checked_in_today": appointments_checked_in,
            "completed_today": appointments_completed,
            "check_in_rate": round((appointments_checked_in / appointments_today * 100) if appointments_today > 0 else 0, 1)
        },
        "performance_metrics": {
            "average_wait_time_minutes": round(avg_wait_time, 1),
            "recent_check_ins": recent_check_ins,
            "recent_completions": recent_completions
        }
    }


@router.get("/queue-summary")
def get_queue_summary(db: Session = Depends(get_db)):
    """Get current queue summary for dashboard"""
    
    # Get waiting patients ordered by priority and time
    waiting_patients = db.query(QueueEntry).filter(
        QueueEntry.status == QueueStatus.WAITING
    ).order_by(
        QueueEntry.priority.desc(),
        QueueEntry.created_at.asc()
    ).limit(10).all()
    
    # Get in-progress patients
    in_progress_patients = db.query(QueueEntry).filter(
        QueueEntry.status == QueueStatus.IN_PROGRESS
    ).order_by(QueueEntry.started_at.asc()).all()
    
    # Get called patients
    called_patients = db.query(QueueEntry).filter(
        QueueEntry.status == QueueStatus.CALLED
    ).order_by(QueueEntry.called_at.asc()).all()
    
    def format_patient_info(entry):
        patient_name = f"{entry.patient.first_name} {entry.patient.last_name}" if entry.patient else "Unknown"
        return {
            "id": entry.id,
            "ticket_number": entry.ticket_number,
            "patient_name": patient_name,
            "reason": entry.reason,
            "priority": entry.priority,
            "queue_type": entry.queue_type,
            "wait_time_minutes": int((datetime.utcnow() - entry.created_at).total_seconds() / 60) if entry.created_at else 0,
            "estimated_wait_time": entry.estimated_wait_time
        }
    
    return {
        "waiting": [format_patient_info(entry) for entry in waiting_patients],
        "in_progress": [format_patient_info(entry) for entry in in_progress_patients],
        "called": [format_patient_info(entry) for entry in called_patients]
    }


@router.get("/kpis")
def get_kpis(db: Session = Depends(get_db)):
    """Get key performance indicators"""
    
    # Calculate KPIs for the last 24 hours
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    
    # Handoff latency (time from check-in to service start)
    handoff_times = db.query(
        func.extract('epoch', QueueEntry.started_at - QueueEntry.created_at)
    ).filter(
        QueueEntry.started_at.isnot(None),
        QueueEntry.created_at >= twenty_four_hours_ago
    ).all()
    
    avg_handoff_latency = sum([t[0] for t in handoff_times]) / len(handoff_times) if handoff_times else 0
    
    # End-to-end time (total time in system)
    e2e_times = db.query(
        func.extract('epoch', QueueEntry.completed_at - QueueEntry.created_at)
    ).filter(
        QueueEntry.completed_at.isnot(None),
        QueueEntry.created_at >= twenty_four_hours_ago
    ).all()
    
    avg_e2e_time = sum([t[0] for t in e2e_times]) / len(e2e_times) if e2e_times else 0
    
    # Auto-resolved percentage (completed without manual intervention)
    total_entries = db.query(QueueEntry).filter(
        QueueEntry.created_at >= twenty_four_hours_ago
    ).count()
    
    auto_resolved = db.query(QueueEntry).filter(
        QueueEntry.created_at >= twenty_four_hours_ago,
        QueueEntry.status == QueueStatus.COMPLETED
    ).count()
    
    auto_resolved_percentage = (auto_resolved / total_entries * 100) if total_entries > 0 else 0
    
    return {
        "handoff_latency_seconds": round(avg_handoff_latency, 1),
        "end_to_end_time_minutes": round(avg_e2e_time / 60, 1),
        "auto_resolved_percentage": round(auto_resolved_percentage, 1),
        "total_processed_24h": total_entries,
        "completed_24h": auto_resolved
    }

