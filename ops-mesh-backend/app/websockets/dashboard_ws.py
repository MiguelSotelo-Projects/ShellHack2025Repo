"""
Dashboard WebSocket Endpoints

Real-time WebSocket endpoints for dashboard updates including
queue status, appointment changes, and system notifications.
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..core.database import get_db
from ..services.dashboard_service import DashboardService
from .connection_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket endpoint for dashboard real-time updates."""
    await manager.connect(websocket, "dashboard")
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                }, websocket)
            elif message.get("type") == "subscribe":
                # Handle subscription to specific updates
                subscription_type = message.get("subscription_type", "all")
                await manager.send_personal_message({
                    "type": "subscription_confirmed",
                    "subscription_type": subscription_type,
                    "message": f"Subscribed to {subscription_type} updates"
                }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Dashboard WebSocket disconnected")
    except Exception as e:
        logger.error(f"Dashboard WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/queue")
async def websocket_queue(websocket: WebSocket):
    """WebSocket endpoint for queue real-time updates."""
    await manager.connect(websocket, "queue")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Queue WebSocket disconnected")
    except Exception as e:
        logger.error(f"Queue WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/appointments")
async def websocket_appointments(websocket: WebSocket):
    """WebSocket endpoint for appointment real-time updates."""
    await manager.connect(websocket, "appointments")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Appointments WebSocket disconnected")
    except Exception as e:
        logger.error(f"Appointments WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/patients")
async def websocket_patients(websocket: WebSocket):
    """WebSocket endpoint for patient real-time updates."""
    await manager.connect(websocket, "patients")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Patients WebSocket disconnected")
    except Exception as e:
        logger.error(f"Patients WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket):
    """WebSocket endpoint for system notifications."""
    await manager.connect(websocket, "notifications")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Notifications WebSocket disconnected")
    except Exception as e:
        logger.error(f"Notifications WebSocket error: {e}")
        manager.disconnect(websocket)


@router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return {
        "connection_stats": manager.get_connection_stats(),
        "active_rooms": list(manager.active_connections.keys())
    }
