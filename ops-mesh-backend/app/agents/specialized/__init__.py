"""
Specialized Hospital Agents

This module contains specialized agents for different hospital functions:
- FrontDesk Agent: Handles patient registration and check-in
- Queue Agent: Manages patient queues and wait times
- Appointment Agent: Handles appointment scheduling and management
- Notification Agent: Sends notifications and updates
"""

from .frontdesk_agent import FrontDeskAgent
from .queue_agent import QueueAgent
from .appointment_agent import AppointmentAgent
from .notification_agent import NotificationAgent

__all__ = [
    "FrontDeskAgent",
    "QueueAgent", 
    "AppointmentAgent",
    "NotificationAgent"
]
