"""
Notification Agent

Handles sending notifications, alerts, and updates to patients and staff.
"""

import asyncio
import logging
from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools import BaseTool
from ..protocol.agent_protocol import AgentProtocol, MessageType, Priority, ProtocolMessage

logger = logging.getLogger(__name__)


class NotificationTool(BaseTool):
    """Tool for sending notifications and alerts."""
    
    def __init__(self, protocol: AgentProtocol):
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
        self.protocol = AgentProtocol(self.agent_id, project_id)
        self.agent = None
        self.notification_tool = None
    
    async def initialize(self):
        """Initialize the agent and its tools."""
        await self.protocol.initialize()
        
        # Create tools
        self.notification_tool = NotificationTool(self.protocol)
        
        # Create ADK agent
        self.agent = Agent(
            name="Notification Agent",
            description="Sends notifications and alerts to patients and staff",
            tools=[self.notification_tool],
            model="gemini-1.5-flash"
        )
        
        # Register message handlers
        self.protocol.register_handler(MessageType.REQUEST, self._handle_request)
        self.protocol.register_handler(MessageType.NOTIFICATION, self._handle_notification)
        self.protocol.register_handler(MessageType.COORDINATION, self._handle_coordination)
        
        logger.info("Notification Agent initialized")
    
    async def _handle_request(self, message: ProtocolMessage):
        """Handle incoming requests."""
        logger.info(f"Notification Agent received request: {message.payload}")
        
        # Process the request using notification tool
        result = await self.notification_tool.execute(message.payload)
        
        await self.protocol.send_response(message, result)
    
    async def _handle_notification(self, message: ProtocolMessage):
        """Handle notifications from other agents."""
        event = message.payload.get("event")
        
        if event == "queue_updated":
            # Send queue update notification
            await self.notification_tool.execute({
                "action": "send_notification",
                "recipient": f"patient_{message.payload.get('patient_id')}",
                "message": f"Your position in queue: {message.payload.get('position')}. Estimated wait: {message.payload.get('estimated_wait')} minutes",
                "type": "queue_update"
            })
        
        elif event == "patient_called":
            # Send patient call notification
            await self.notification_tool.execute({
                "action": "send_alert",
                "recipient": f"patient_{message.payload.get('patient_id')}",
                "message": message.payload.get("message", "Please proceed to the consultation room"),
                "level": "high"
            })
    
    async def _handle_coordination(self, message: ProtocolMessage):
        """Handle coordination messages."""
        logger.info(f"Notification Agent received coordination: {message.payload}")
        
        # Handle coordination logic here
        flow_id = message.payload.get("flow_id")
        step_data = message.payload.get("data", {})
        
        # Process coordination step
        if step_data.get("action") == "send_notification":
            result = await self.notification_tool.execute(step_data)
            logger.info(f"Processed coordination step: {result}")
    
    async def start(self):
        """Start the agent."""
        if not self.agent:
            await self.initialize()
        
        logger.info("Starting Notification Agent...")
        
        # Start listening for messages
        await self.protocol.start_listening()
    
    async def stop(self):
        """Stop the agent."""
        await self.protocol.stop_listening()
        logger.info("Notification Agent stopped")
