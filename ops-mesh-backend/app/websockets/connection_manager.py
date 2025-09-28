"""
WebSocket Connection Manager for Real-time Updates

This module manages WebSocket connections and provides real-time updates
for dashboard, queue, and appointment changes.
"""

import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasting."""
    
    def __init__(self):
        # Active connections by room/channel
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "dashboard": set(),
            "queue": set(),
            "appointments": set(),
            "patients": set(),
            "notifications": set()
        }
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, room: str = "dashboard"):
        """Accept a WebSocket connection and add to room."""
        await websocket.accept()
        
        if room not in self.active_connections:
            self.active_connections[room] = set()
        
        self.active_connections[room].add(websocket)
        self.connection_metadata[websocket] = {
            "room": room,
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        logger.info(f"WebSocket connected to room '{room}'. Total connections: {len(self.active_connections[room])}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "room": room,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Connected to {room} updates"
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.connection_metadata:
            room = self.connection_metadata[websocket]["room"]
            self.active_connections[room].discard(websocket)
            del self.connection_metadata[websocket]
            
            logger.info(f"WebSocket disconnected from room '{room}'. Remaining connections: {len(self.active_connections[room])}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["last_activity"] = datetime.utcnow()
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast_to_room(self, message: dict, room: str):
        """Broadcast a message to all connections in a specific room."""
        if room not in self.active_connections:
            return
        
        disconnected = set()
        for websocket in self.active_connections[room].copy():
            try:
                await websocket.send_text(json.dumps(message))
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]["last_activity"] = datetime.utcnow()
            except Exception as e:
                logger.error(f"Error broadcasting to room '{room}': {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all active connections."""
        for room in self.active_connections:
            await self.broadcast_to_room(message, room)
    
    def get_connection_stats(self) -> dict:
        """Get statistics about active connections."""
        stats = {}
        total_connections = 0
        
        for room, connections in self.active_connections.items():
            stats[room] = len(connections)
            total_connections += len(connections)
        
        stats["total"] = total_connections
        return stats
    
    async def send_queue_update(self, queue_data: dict):
        """Send queue update to relevant rooms."""
        message = {
            "type": "queue_update",
            "data": queue_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_room(message, "queue")
        await self.broadcast_to_room(message, "dashboard")
    
    async def send_appointment_update(self, appointment_data: dict):
        """Send appointment update to relevant rooms."""
        message = {
            "type": "appointment_update",
            "data": appointment_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_room(message, "appointments")
        await self.broadcast_to_room(message, "dashboard")
    
    async def send_patient_update(self, patient_data: dict):
        """Send patient update to relevant rooms."""
        message = {
            "type": "patient_update",
            "data": patient_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_room(message, "patients")
        await self.broadcast_to_room(message, "dashboard")
    
    async def send_notification(self, notification: dict):
        """Send notification to all connections."""
        message = {
            "type": "notification",
            "data": notification,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_room(message, "notifications")
        await self.broadcast_to_room(message, "dashboard")
    
    async def send_dashboard_update(self, dashboard_data: dict):
        """Send dashboard update."""
        message = {
            "type": "dashboard_update",
            "data": dashboard_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_room(message, "dashboard")


# Global connection manager instance
manager = ConnectionManager()
