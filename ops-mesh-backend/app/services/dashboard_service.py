from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Dict, Any, List
from datetime import datetime, timedelta

from ..models.queue import QueueEntry, QueueStatus, QueueType, QueuePriority
from ..models.appointment import Appointment, AppointmentStatus
from ..models.patient import Patient


class DashboardService:
    """Service class for dashboard-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics."""
        # Current queue stats
        total_waiting = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING
        ).count()
        
        total_in_progress = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.IN_PROGRESS
        ).count()
        
        total_called = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.CALLED
        ).count()
        
        # Queue by type
        walk_ins_waiting = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING,
            QueueEntry.queue_type == QueueType.WALK_IN
        ).count()
        
        appointments_waiting = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING,
            QueueEntry.queue_type == QueueType.APPOINTMENT
        ).count()
        
        # Priority breakdown
        urgent_waiting = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING,
            QueueEntry.priority == QueuePriority.URGENT
        ).count()
        
        high_waiting = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING,
            QueueEntry.priority == QueuePriority.HIGH
        ).count()
        
        medium_waiting = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING,
            QueueEntry.priority == QueuePriority.MEDIUM
        ).count()
        
        low_waiting = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING,
            QueueEntry.priority == QueuePriority.LOW
        ).count()
        
        # Average wait time (for completed entries)
        avg_wait_time = self.db.query(func.avg(QueueEntry.actual_wait_time)).filter(
            QueueEntry.actual_wait_time.isnot(None)
        ).scalar() or 0
        
        # Today's appointments
        today = datetime.utcnow().date()
        appointments_today = self.db.query(Appointment).filter(
            func.date(Appointment.scheduled_time) == today
        ).count()
        
        completed_today = self.db.query(Appointment).filter(
            func.date(Appointment.scheduled_time) == today,
            Appointment.status == AppointmentStatus.COMPLETED
        ).count()
        
        cancelled_today = self.db.query(Appointment).filter(
            func.date(Appointment.scheduled_time) == today,
            Appointment.status == AppointmentStatus.CANCELLED
        ).count()
        
        return {
            "queue_stats": {
                "total_waiting": total_waiting,
                "total_in_progress": total_in_progress,
                "total_called": total_called,
                "walk_ins_waiting": walk_ins_waiting,
                "appointments_waiting": appointments_waiting
            },
            "priority_breakdown": {
                "urgent": urgent_waiting,
                "high": high_waiting,
                "medium": medium_waiting,
                "low": low_waiting
            },
            "appointment_stats": {
                "total_today": appointments_today,
                "completed_today": completed_today,
                "cancelled_today": cancelled_today,
                "completion_rate": round((completed_today / appointments_today * 100) if appointments_today > 0 else 0, 1)
            },
            "performance_metrics": {
                "average_wait_time": round(avg_wait_time, 1)
            }
        }
    
    def get_queue_summary(self) -> Dict[str, Any]:
        """Get detailed queue summary."""
        # Current queue entries with patient info
        current_queue = self.db.query(QueueEntry).filter(
            QueueEntry.status.in_([QueueStatus.WAITING, QueueStatus.CALLED, QueueStatus.IN_PROGRESS])
        ).order_by(
            QueueEntry.priority.desc(),
            QueueEntry.created_at.asc()
        ).all()
        
        queue_entries = []
        for entry in current_queue:
            patient_name = None
            appointment_code = None
            
            if entry.patient:
                patient_name = f"{entry.patient.first_name} {entry.patient.last_name}"
            
            if entry.appointment:
                appointment_code = entry.appointment.confirmation_code
            
            queue_entries.append({
                "id": entry.id,
                "ticket_number": entry.ticket_number,
                "status": entry.status.value,
                "queue_type": entry.queue_type.value,
                "priority": entry.priority.value,
                "reason": entry.reason,
                "estimated_wait_time": entry.estimated_wait_time,
                "patient_name": patient_name,
                "appointment_code": appointment_code,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        # Wait time estimates
        estimated_wait_times = self._calculate_wait_times()
        
        return {
            "current_queue": queue_entries,
            "wait_time_estimates": estimated_wait_times,
            "total_in_queue": len(queue_entries)
        }
    
    def get_kpis(self) -> Dict[str, Any]:
        """Get key performance indicators."""
        # Calculate KPIs for the last 24 hours
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        
        # Handoff latency (time from check-in to service start)
        handoff_times = self.db.query(
            func.extract('epoch', QueueEntry.started_at - QueueEntry.created_at)
        ).filter(
            QueueEntry.started_at.isnot(None),
            QueueEntry.created_at >= twenty_four_hours_ago
        ).all()
        
        avg_handoff_latency = sum([t[0] for t in handoff_times]) / len(handoff_times) if handoff_times else 0
        
        # End-to-end time (total time in system)
        e2e_times = self.db.query(
            func.extract('epoch', QueueEntry.completed_at - QueueEntry.created_at)
        ).filter(
            QueueEntry.completed_at.isnot(None),
            QueueEntry.created_at >= twenty_four_hours_ago
        ).all()
        
        avg_e2e_time = sum([t[0] for t in e2e_times]) / len(e2e_times) if e2e_times else 0
        
        # Auto-resolved percentage (completed without manual intervention)
        total_entries = self.db.query(QueueEntry).filter(
            QueueEntry.created_at >= twenty_four_hours_ago
        ).count()
        
        auto_resolved = self.db.query(QueueEntry).filter(
            QueueEntry.created_at >= twenty_four_hours_ago,
            QueueEntry.status == QueueStatus.COMPLETED
        ).count()
        
        auto_resolved_percentage = (auto_resolved / total_entries * 100) if total_entries > 0 else 0
        
        # Patient satisfaction metrics (placeholder - would need actual feedback data)
        patient_volume_24h = self.db.query(QueueEntry).filter(
            QueueEntry.created_at >= twenty_four_hours_ago
        ).count()
        
        return {
            "handoff_latency_seconds": round(avg_handoff_latency, 1),
            "end_to_end_time_minutes": round(avg_e2e_time / 60, 1),
            "auto_resolved_percentage": round(auto_resolved_percentage, 1),
            "total_processed_24h": total_entries,
            "completed_24h": auto_resolved,
            "patient_volume_24h": patient_volume_24h,
            "efficiency_score": self._calculate_efficiency_score(avg_handoff_latency, avg_e2e_time, auto_resolved_percentage)
        }
    
    def get_trend_data(self, days: int = 7) -> Dict[str, Any]:
        """Get trend data for the specified number of days."""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Daily appointment counts
        daily_appointments = self.db.query(
            func.date(Appointment.scheduled_time).label('date'),
            func.count(Appointment.id).label('count')
        ).filter(
            func.date(Appointment.scheduled_time) >= start_date,
            func.date(Appointment.scheduled_time) <= end_date
        ).group_by(func.date(Appointment.scheduled_time)).all()
        
        # Daily queue completions
        daily_completions = self.db.query(
            func.date(QueueEntry.completed_at).label('date'),
            func.count(QueueEntry.id).label('count')
        ).filter(
            QueueEntry.completed_at.isnot(None),
            func.date(QueueEntry.completed_at) >= start_date,
            func.date(QueueEntry.completed_at) <= end_date
        ).group_by(func.date(QueueEntry.completed_at)).all()
        
        # Daily average wait times
        daily_wait_times = self.db.query(
            func.date(QueueEntry.completed_at).label('date'),
            func.avg(QueueEntry.actual_wait_time).label('avg_wait_time')
        ).filter(
            QueueEntry.completed_at.isnot(None),
            QueueEntry.actual_wait_time.isnot(None),
            func.date(QueueEntry.completed_at) >= start_date,
            func.date(QueueEntry.completed_at) <= end_date
        ).group_by(func.date(QueueEntry.completed_at)).all()
        
        return {
            "daily_appointments": [{"date": str(d[0]), "count": d[1]} for d in daily_appointments],
            "daily_completions": [{"date": str(d[0]), "count": d[1]} for d in daily_completions],
            "daily_wait_times": [{"date": str(d[0]), "avg_wait_time": round(d[1] or 0, 1)} for d in daily_wait_times]
        }
    
    def get_provider_performance(self) -> Dict[str, Any]:
        """Get provider performance metrics."""
        # Provider appointment counts
        provider_stats = self.db.query(
            Appointment.provider_name,
            func.count(Appointment.id).label('total_appointments'),
            func.count(func.case([(Appointment.status == AppointmentStatus.COMPLETED, 1)])).label('completed'),
            func.count(func.case([(Appointment.status == AppointmentStatus.CANCELLED, 1)])).label('cancelled')
        ).filter(
            func.date(Appointment.scheduled_time) >= datetime.utcnow().date() - timedelta(days=30)
        ).group_by(Appointment.provider_name).all()
        
        provider_performance = []
        for provider in provider_stats:
            completion_rate = (provider.completed / provider.total_appointments * 100) if provider.total_appointments > 0 else 0
            cancellation_rate = (provider.cancelled / provider.total_appointments * 100) if provider.total_appointments > 0 else 0
            
            provider_performance.append({
                "provider_name": provider.provider_name,
                "total_appointments": provider.total_appointments,
                "completed": provider.completed,
                "cancelled": provider.cancelled,
                "completion_rate": round(completion_rate, 1),
                "cancellation_rate": round(cancellation_rate, 1)
            })
        
        return {
            "provider_performance": provider_performance,
            "summary": {
                "total_providers": len(provider_performance),
                "avg_completion_rate": round(sum(p["completion_rate"] for p in provider_performance) / len(provider_performance), 1) if provider_performance else 0
            }
        }
    
    def _calculate_wait_times(self) -> Dict[str, Any]:
        """Calculate estimated wait times for different queue types."""
        # Walk-in wait time
        walk_in_count = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING,
            QueueEntry.queue_type == QueueType.WALK_IN
        ).count()
        
        # Appointment wait time
        appointment_count = self.db.query(QueueEntry).filter(
            QueueEntry.status == QueueStatus.WAITING,
            QueueEntry.queue_type == QueueType.APPOINTMENT
        ).count()
        
        return {
            "walk_in_estimated_wait": walk_in_count * 15,  # 15 minutes per patient
            "appointment_estimated_wait": appointment_count * 10,  # 10 minutes per patient
            "total_estimated_wait": (walk_in_count * 15) + (appointment_count * 10)
        }
    
    def _calculate_efficiency_score(
        self, 
        handoff_latency: float, 
        e2e_time: float, 
        auto_resolved_percentage: float
    ) -> float:
        """Calculate overall efficiency score (0-100)."""
        # Normalize metrics (lower is better for latency and e2e time)
        latency_score = max(0, 100 - (handoff_latency / 60 * 10))  # Penalty for each minute of latency
        e2e_score = max(0, 100 - (e2e_time / 60 * 5))  # Penalty for each minute of e2e time
        resolution_score = auto_resolved_percentage  # Higher is better
        
        # Weighted average
        efficiency_score = (latency_score * 0.3) + (e2e_score * 0.3) + (resolution_score * 0.4)
        
        return round(max(0, min(100, efficiency_score)), 1)
