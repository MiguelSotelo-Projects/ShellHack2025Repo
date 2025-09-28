"""
Notification Agent

Handles sending notifications, alerts, and updates to patients and staff.
"""

import asyncio
import logging
from typing import Dict, Any, List

# Try to import Google ADK, fallback to internal implementation
try:
    from google.adk.agents import Agent
    from google.adk.tools import BaseTool
except ImportError:
    from ..google_adk_fallback import Agent, BaseTool

from ..protocol.a2a_protocol import A2AProtocol, A2ATaskRequest, TaskStatus

logger = logging.getLogger(__name__)


class NotificationTool(BaseTool):
    """Tool for sending notifications and alerts."""
    
    def __init__(self, protocol: A2AProtocol):
        super().__init__(
            name="notification_tool",
            description="Sends notifications and alerts to patients and staff"
        )
        self.protocol = protocol
        self.notification_history = []
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification operations."""
        try:
            action = parameters.get("action", "")
            
            if action == "send_notification":
                return await self._send_notification(parameters)
            elif action == "send_alert":
                return await self._send_alert(parameters)
            elif action == "send_reminder":
                return await self._send_reminder(parameters)
            elif action == "get_notification_history":
                return await self._get_notification_history()
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error in notification: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_notification(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send a notification."""
        recipient = parameters.get("recipient")
        message = parameters.get("message")
        notification_type = parameters.get("type", "info")
        
        notification = {
            "id": f"notif-{asyncio.get_event_loop().time()}",
            "recipient": recipient,
            "message": message,
            "type": notification_type,
            "sent_at": asyncio.get_event_loop().time(),
            "status": "sent"
        }
        
        self.notification_history.append(notification)
        
        # Simulate sending notification
        logger.info(f"Sent {notification_type} notification to {recipient}: {message}")
        
        return {
            "success": True,
            "notification_id": notification["id"],
            "message": "Notification sent successfully"
        }
    
    async def _send_alert(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send an urgent alert."""
        recipient = parameters.get("recipient")
        message = parameters.get("message")
        alert_level = parameters.get("level", "high")
        
        alert = {
            "id": f"alert-{asyncio.get_event_loop().time()}",
            "recipient": recipient,
            "message": message,
            "level": alert_level,
            "sent_at": asyncio.get_event_loop().time(),
            "status": "sent"
        }
        
        self.notification_history.append(alert)
        
        logger.warning(f"Sent {alert_level} alert to {recipient}: {message}")
        
        return {
            "success": True,
            "alert_id": alert["id"],
            "message": "Alert sent successfully"
        }
    
    async def _send_reminder(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send a reminder notification."""
        recipient = parameters.get("recipient")
        message = parameters.get("message")
        reminder_type = parameters.get("reminder_type", "appointment")
        
        reminder = {
            "id": f"reminder-{asyncio.get_event_loop().time()}",
            "recipient": recipient,
            "message": message,
            "type": reminder_type,
            "sent_at": asyncio.get_event_loop().time(),
            "status": "sent"
        }
        
        self.notification_history.append(reminder)
        
        logger.info(f"Sent {reminder_type} reminder to {recipient}: {message}")
        
        return {
            "success": True,
            "reminder_id": reminder["id"],
            "message": "Reminder sent successfully"
        }
    
    async def _get_notification_history(self) -> Dict[str, Any]:
        """Get notification history."""
        return {
            "success": True,
            "notifications": self.notification_history,
            "total_count": len(self.notification_history)
        }


class NotificationAgent:
    """Notification Agent for sending alerts and updates."""
    
    def __init__(self, project_id: str = None):
        self.agent_id = "notification_agent"
        self.protocol = A2AProtocol(
            self.agent_id, 
            "ops-mesh-backend/agents/notification_agent.json"
        )
        self.agent = None
        self.notification_tool = None
    
    async def initialize(self):
        """Initialize the agent and its tools."""
        await self.protocol.start()
        
        # Create tools
        self.notification_tool = NotificationTool(self.protocol)
        
        # Create ADK agent
        try:
            self.agent = Agent(
                name="Notification Agent",
                description="Sends notifications and alerts to patients and staff",
                tools=[self.notification_tool],
                model="gemini-1.5-flash"
            )
        except TypeError:
            # Fallback for internal Agent implementation
            self.agent = Agent(
                name="Notification Agent",
                tools=[self.notification_tool]
            )
        
        # Register task handlers
        self.protocol.register_task_handler("send_notification", self._handle_send_notification)
        self.protocol.register_task_handler("send_alert", self._handle_send_alert)
        self.protocol.register_task_handler("send_reminder", self._handle_send_reminder)
        
        logger.info("Notification Agent initialized")
    
    async def _handle_send_notification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send notification task."""
        logger.info(f"Notification Agent handling send_notification: {data}")
        return await self.notification_tool.execute({
            "action": "send_notification",
            "recipient": data.get("recipient"),
            "message": data.get("message"),
            "type": data.get("type", "info")
        })
    
    async def _handle_send_alert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send alert task."""
        logger.info(f"Notification Agent handling send_alert: {data}")
        return await self.notification_tool.execute({
            "action": "send_alert",
            "recipient": data.get("recipient"),
            "message": data.get("message"),
            "level": data.get("level", "high")
        })
    
    async def _handle_send_reminder(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send reminder task."""
        logger.info(f"Notification Agent handling send_reminder: {data}")
        return await self.notification_tool.execute({
            "action": "send_reminder",
            "recipient": data.get("recipient"),
            "message": data.get("message"),
            "reminder_type": data.get("reminder_type", "appointment")
        })
    
    async def start(self):
        """Start the agent."""
        if not self.agent:
            await self.initialize()
        
        logger.info("Starting Notification Agent...")
        
        logger.info("Notification Agent started")
    
    async def stop(self):
        """Stop the agent."""
        await self.protocol.stop()
        logger.info("Notification Agent stopped")
