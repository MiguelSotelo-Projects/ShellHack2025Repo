"""
Queue Agent

Manages patient queues, wait times, and queue optimization.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from app.core.database import SessionLocal
from app.models.queue import QueueEntry, QueueType, QueueStatus, QueuePriority
from app.models.patient import Patient
from app.models.appointment import Appointment

# Try to import Google ADK, fallback to internal implementation
try:
    from google.adk.agents import Agent
    from google.adk.tools import BaseTool
except ImportError:
    from ..google_adk_fallback import Agent, BaseTool

from ..protocol.a2a_protocol import A2AProtocol, A2ATaskRequest, TaskStatus

logger = logging.getLogger(__name__)


class QueueManagementTool(BaseTool):
    """Tool for queue management operations."""
    
    def __init__(self, protocol: A2AProtocol):
        super().__init__(
            name="queue_management_tool",
            description="Manages patient queues and wait times"
        )
        self.protocol = protocol
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute queue management operations."""
        try:
            action = parameters.get("action", "")
            
            if action == "add_to_queue":
                return await self._add_to_queue(parameters)
            elif action == "get_queue_status":
                return await self._get_queue_status()
            elif action == "call_next_patient":
                return await self._call_next_patient()
            elif action == "update_wait_time":
                return await self._update_wait_time(parameters)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error in queue management: {e}")
            return {"success": False, "error": str(e)}
    
    async def _add_to_queue(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Add patient to queue."""
        try:
            db = SessionLocal()
            
            patient_id = parameters.get("patient_id")
            priority = parameters.get("priority", "medium")
            queue_type = parameters.get("queue_type", "walk_in")
            appointment_id = parameters.get("appointment_id")
            
            # Create queue entry
            queue_entry = QueueEntry(
                ticket_number=f"T-{int(asyncio.get_event_loop().time())}",
                patient_id=patient_id,
                appointment_id=appointment_id,
                queue_type=QueueType(queue_type),
                priority=QueuePriority(priority),
                status=QueueStatus.WAITING,
                estimated_wait_time=self._calculate_wait_time(priority)
            )
            
            db.add(queue_entry)
            db.commit()
            db.refresh(queue_entry)
            
            # Get position in queue
            position = db.query(QueueEntry).filter(
                QueueEntry.status == QueueStatus.WAITING,
                QueueEntry.created_at <= queue_entry.created_at
            ).count()
            
            # Notify notification agent about queue update
            await self.protocol.send_task_request(
                recipient_id="notification_agent",
                action="send_notification",
                data={
                    "event": "queue_updated",
                    "patient_id": patient_id,
                    "ticket_number": queue_entry.ticket_number,
                    "position": position,
                    "estimated_wait": queue_entry.estimated_wait_time
                }
            )
            
            logger.info(f"Added patient {patient_id} to queue with priority {priority}")
            
            return {
                "success": True,
                "patient_id": patient_id,
                "ticket_number": queue_entry.ticket_number,
                "position": position,
                "estimated_wait": queue_entry.estimated_wait_time
            }
            
        except Exception as e:
            logger.error(f"Error adding patient to queue: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to add patient to queue"
            }
        finally:
            if 'db' in locals() and db:
                db.close()
    
    async def _get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        try:
            db = SessionLocal()
            
            # Get queue statistics
            waiting_count = db.query(QueueEntry).filter(QueueEntry.status == QueueStatus.WAITING).count()
            in_progress_count = db.query(QueueEntry).filter(QueueEntry.status == QueueStatus.IN_PROGRESS).count()
            completed_count = db.query(QueueEntry).filter(QueueEntry.status == QueueStatus.COMPLETED).count()
            
            # Calculate average wait time
            avg_wait_time = db.query(QueueEntry.estimated_wait_time).filter(
                QueueEntry.status == QueueStatus.WAITING
            ).all()
            average_wait = sum(wait[0] for wait in avg_wait_time if wait[0]) // len(avg_wait_time) if avg_wait_time else 0
            
            return {
                "success": True,
                "queue_status": {
                    "waiting": waiting_count,
                    "in_progress": in_progress_count,
                    "completed": completed_count,
                    "total_waiting": waiting_count,
                    "average_wait_time": average_wait
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get queue status"
            }
        finally:
            if 'db' in locals() and db:
                db.close()
    
    async def _call_next_patient(self) -> Dict[str, Any]:
        """Call the next patient in queue."""
        try:
            db = SessionLocal()
            
            # Find next patient by priority and arrival time
            next_patient = db.query(QueueEntry).filter(
                QueueEntry.status == QueueStatus.WAITING
            ).order_by(
                QueueEntry.priority.desc(),  # Urgent first
                QueueEntry.created_at.asc()  # Then by arrival time
            ).first()
            
            if not next_patient:
                return {"success": False, "error": "No patients in queue"}
            
            # Update patient status
            next_patient.status = QueueStatus.CALLED
            next_patient.called_at = datetime.now()
            
            db.commit()
            
            # Notify notification agent
            await self.protocol.send_task_request(
                recipient_id="notification_agent",
                action="send_alert",
                data={
                    "event": "patient_called",
                    "patient_id": next_patient.patient_id,
                    "ticket_number": next_patient.ticket_number,
                    "message": "Please proceed to the consultation room"
                }
            )
            
            logger.info(f"Called next patient: {next_patient.patient_id}")
            
            return {
                "success": True,
                "patient_id": next_patient.patient_id,
                "ticket_number": next_patient.ticket_number,
                "message": "Patient called successfully"
            }
            
        except Exception as e:
            logger.error(f"Error calling next patient: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to call next patient"
            }
        finally:
            if 'db' in locals() and db:
                db.close()
    
    async def _update_wait_time(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update estimated wait times."""
        try:
            db = SessionLocal()
            
            # Get all waiting patients
            waiting_patients = db.query(QueueEntry).filter(
                QueueEntry.status == QueueStatus.WAITING
            ).all()
            
            # Update wait times
            for patient in waiting_patients:
                patient.estimated_wait_time = self._calculate_wait_time(patient.priority.value)
            
            db.commit()
            
            return {
                "success": True,
                "message": "Wait times updated",
                "updated_count": len(waiting_patients)
            }
            
        except Exception as e:
            logger.error(f"Error updating wait times: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update wait times"
            }
        finally:
            if 'db' in locals() and db:
                db.close()
    
    def _calculate_wait_time(self, priority: str) -> int:
        """Calculate estimated wait time based on priority."""
        base_wait = {
            "urgent": 5,
            "high": 15,
            "medium": 30,
            "low": 45
        }
        return base_wait.get(priority, 30)
    


class QueueAgent:
    """Queue Agent for managing patient queues."""
    
    def __init__(self, project_id: str = None):
        self.agent_id = "queue_agent"
        self.protocol = A2AProtocol(
            self.agent_id, 
            "ops-mesh-backend/agents/queue_agent.json"
        )
        self.agent = None
        self.queue_tool = None
    
    async def initialize(self):
        """Initialize the agent and its tools."""
        await self.protocol.start()
        
        # Create tools
        self.queue_tool = QueueManagementTool(self.protocol)
        
        # Create ADK agent
        try:
            self.agent = Agent(
                name="Queue Agent",
                description="Manages patient queues and wait times",
                tools=[self.queue_tool],
                model="gemini-1.5-flash"
            )
        except TypeError:
            # Fallback for internal Agent implementation
            self.agent = Agent(
                name="Queue Agent",
                tools=[self.queue_tool]
            )
        
        # Register task handlers
        self.protocol.register_task_handler("add_to_queue", self._handle_add_to_queue)
        self.protocol.register_task_handler("get_queue_status", self._handle_get_queue_status)
        self.protocol.register_task_handler("call_next_patient", self._handle_call_next_patient)
        
        logger.info("Queue Agent initialized")
    
    async def _handle_add_to_queue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add to queue task."""
        logger.info(f"Queue Agent handling add_to_queue: {data}")
        return await self.queue_tool.execute({
            "action": "add_to_queue",
            "patient_id": data.get("patient_id"),
            "priority": data.get("priority", "medium"),
            "queue_type": data.get("queue_type", "walk_in")
        })
    
    async def _handle_get_queue_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get queue status task."""
        logger.info(f"Queue Agent handling get_queue_status: {data}")
        return await self.queue_tool.execute({
            "action": "get_queue_status"
        })
    
    async def _handle_call_next_patient(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle call next patient task."""
        logger.info(f"Queue Agent handling call_next_patient: {data}")
        return await self.queue_tool.execute({
            "action": "call_next_patient"
        })
    
    async def start(self):
        """Start the agent."""
        if not self.agent:
            await self.initialize()
        
        logger.info("Starting Queue Agent...")
        
        logger.info("Queue Agent started")
    
    async def stop(self):
        """Stop the agent."""
        await self.protocol.stop()
        logger.info("Queue Agent stopped")
