"""
Queue Calculator Utility

This module provides utilities for calculating queue metrics,
wait times, and priority-based queue management.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from ..models.queue import QueueEntry, QueueStatus, QueuePriority, QueueType


class QueueCalculator:
    """Calculator for queue metrics and wait times."""
    
    # Base wait times in minutes by priority
    BASE_WAIT_TIMES = {
        QueuePriority.URGENT: 5,
        QueuePriority.HIGH: 10,
        QueuePriority.MEDIUM: 15,
        QueuePriority.LOW: 20
    }
    
    # Average processing times in minutes by queue type
    PROCESSING_TIMES = {
        QueueType.APPOINTMENT: 30,
        QueueType.WALK_IN: 20,
        QueueType.EMERGENCY: 10
    }
    
    @staticmethod
    def calculate_wait_time(
        queue_entries: List[QueueEntry],
        current_entry: Optional[QueueEntry] = None
    ) -> int:
        """
        Calculate estimated wait time for a queue entry.
        
        Args:
            queue_entries: List of all queue entries
            current_entry: The entry to calculate wait time for
            
        Returns:
            Estimated wait time in minutes
        """
        if not queue_entries:
            return 0
        
        # Filter to waiting entries only
        waiting_entries = [
            entry for entry in queue_entries
            if entry.status == QueueStatus.WAITING
        ]
        
        if not waiting_entries:
            return 0
        
        # Sort by priority and creation time
        waiting_entries.sort(
            key=lambda x: (x.priority.value, x.created_at)
        )
        
        total_wait_time = 0
        
        for entry in waiting_entries:
            if current_entry and entry.id == current_entry.id:
                break
            
            # Calculate processing time based on queue type
            processing_time = QueueCalculator.PROCESSING_TIMES.get(
                entry.queue_type, 15
            )
            
            # Adjust based on priority
            priority_multiplier = {
                QueuePriority.URGENT: 0.5,
                QueuePriority.HIGH: 0.7,
                QueuePriority.MEDIUM: 1.0,
                QueuePriority.LOW: 1.2
            }.get(entry.priority, 1.0)
            
            total_wait_time += processing_time * priority_multiplier
        
        return int(total_wait_time)
    
    @staticmethod
    def calculate_position_in_queue(
        queue_entries: List[QueueEntry],
        current_entry: QueueEntry
    ) -> int:
        """
        Calculate position in queue for a specific entry.
        
        Args:
            queue_entries: List of all queue entries
            current_entry: The entry to find position for
            
        Returns:
            Position in queue (1-based)
        """
        if not queue_entries or not current_entry:
            return 0
        
        # Filter to waiting entries only
        waiting_entries = [
            entry for entry in queue_entries
            if entry.status == QueueStatus.WAITING
        ]
        
        if not waiting_entries:
            return 0
        
        # Sort by priority and creation time
        waiting_entries.sort(
            key=lambda x: (x.priority.value, x.created_at)
        )
        
        for i, entry in enumerate(waiting_entries):
            if entry.id == current_entry.id:
                return i + 1
        
        return 0
    
    @staticmethod
    def calculate_queue_metrics(queue_entries: List[QueueEntry]) -> Dict[str, Any]:
        """
        Calculate comprehensive queue metrics.
        
        Args:
            queue_entries: List of all queue entries
            
        Returns:
            Dictionary with queue metrics
        """
        if not queue_entries:
            return {
                "total_entries": 0,
                "waiting": 0,
                "in_progress": 0,
                "completed": 0,
                "cancelled": 0,
                "average_wait_time": 0,
                "priority_breakdown": {},
                "queue_type_breakdown": {}
            }
        
        # Count by status
        status_counts = {}
        for status in QueueStatus:
            status_counts[status.value] = len([
                entry for entry in queue_entries
                if entry.status == status
            ])
        
        # Count by priority
        priority_counts = {}
        for priority in QueuePriority:
            priority_counts[priority.value] = len([
                entry for entry in queue_entries
                if entry.status == QueueStatus.WAITING and entry.priority == priority
            ])
        
        # Count by queue type
        queue_type_counts = {}
        for queue_type in QueueType:
            queue_type_counts[queue_type.value] = len([
                entry for entry in queue_entries
                if entry.queue_type == queue_type
            ])
        
        # Calculate average wait time for completed entries
        completed_entries = [
            entry for entry in queue_entries
            if entry.status == QueueStatus.COMPLETED and entry.started_at
        ]
        
        average_wait_time = 0
        if completed_entries:
            total_wait_time = sum([
                (entry.started_at - entry.created_at).total_seconds() / 60
                for entry in completed_entries
            ])
            average_wait_time = total_wait_time / len(completed_entries)
        
        return {
            "total_entries": len(queue_entries),
            "waiting": status_counts.get(QueueStatus.WAITING.value, 0),
            "in_progress": status_counts.get(QueueStatus.IN_PROGRESS.value, 0),
            "completed": status_counts.get(QueueStatus.COMPLETED.value, 0),
            "cancelled": status_counts.get(QueueStatus.CANCELLED.value, 0),
            "called": status_counts.get(QueueStatus.CALLED.value, 0),
            "average_wait_time": round(average_wait_time, 1),
            "priority_breakdown": priority_counts,
            "queue_type_breakdown": queue_type_counts
        }
    
    @staticmethod
    def optimize_queue_order(queue_entries: List[QueueEntry]) -> List[QueueEntry]:
        """
        Optimize queue order based on priority and wait time.
        
        Args:
            queue_entries: List of queue entries to optimize
            
        Returns:
            Optimized list of queue entries
        """
        if not queue_entries:
            return []
        
        # Filter to waiting entries only
        waiting_entries = [
            entry for entry in queue_entries
            if entry.status == QueueStatus.WAITING
        ]
        
        # Sort by priority (urgent first) and then by creation time
        waiting_entries.sort(
            key=lambda x: (x.priority.value, x.created_at)
        )
        
        return waiting_entries
    
    @staticmethod
    def calculate_throughput_metrics(
        queue_entries: List[QueueEntry],
        time_period_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Calculate throughput metrics for a given time period.
        
        Args:
            queue_entries: List of queue entries
            time_period_hours: Time period in hours to analyze
            
        Returns:
            Dictionary with throughput metrics
        """
        if not queue_entries:
            return {
                "entries_processed": 0,
                "average_processing_time": 0,
                "throughput_per_hour": 0,
                "efficiency_score": 0
            }
        
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=time_period_hours)
        
        # Filter entries within time period
        recent_entries = [
            entry for entry in queue_entries
            if entry.created_at >= time_threshold
        ]
        
        # Count completed entries
        completed_entries = [
            entry for entry in recent_entries
            if entry.status == QueueStatus.COMPLETED and entry.started_at and entry.completed_at
        ]
        
        entries_processed = len(completed_entries)
        
        # Calculate average processing time
        average_processing_time = 0
        if completed_entries:
            total_processing_time = sum([
                (entry.completed_at - entry.started_at).total_seconds() / 60
                for entry in completed_entries
            ])
            average_processing_time = total_processing_time / len(completed_entries)
        
        # Calculate throughput per hour
        throughput_per_hour = entries_processed / time_period_hours if time_period_hours > 0 else 0
        
        # Calculate efficiency score (0-100)
        # Based on completion rate and processing time
        total_entries = len(recent_entries)
        completion_rate = (entries_processed / total_entries * 100) if total_entries > 0 else 0
        
        # Efficiency score combines completion rate and processing time
        # Lower processing time = higher efficiency
        time_efficiency = max(0, 100 - (average_processing_time * 2))  # Penalty for long processing
        efficiency_score = (completion_rate + time_efficiency) / 2
        
        return {
            "entries_processed": entries_processed,
            "average_processing_time": round(average_processing_time, 1),
            "throughput_per_hour": round(throughput_per_hour, 1),
            "efficiency_score": round(efficiency_score, 1),
            "completion_rate": round(completion_rate, 1)
        }
