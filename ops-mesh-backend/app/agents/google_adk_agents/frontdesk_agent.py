"""
Google ADK FrontDesk Agent

This agent handles tablet interface interactions and initial patient processing
using Google ADK and the agent protocol.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

from ..protocol.agent_protocol import (
    AgentProtocol, ProtocolMessage, MessageType, MessagePriority,
    AgentCapability, AgentStatus
)
from ...services.appointment_service import AppointmentService
from ...services.walkin_service import WalkInService
from ...core.database import SessionLocal


class GoogleADKFrontDeskAgent(AgentProtocol):
    """Front desk agent using Google ADK."""
    
    def __init__(self, project_id: str, region: str = "us-central1"):
        super().__init__(
            agent_id="frontdesk",
            agent_name="Front Desk Agent",
            project_id=project_id,
            region=region
        )
        
        # Initialize services
        self.db_session = SessionLocal()
        self.appointment_service = AppointmentService(self.db_session)
        self.walkin_service = WalkInService(self.db_session)
        
        # Current session data
        self.current_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Define capabilities
        self.capabilities = [
            AgentCapability(
                name="patient_checkin",
                version="1.0.0",
                description="Handle patient check-in at tablet interface",
                input_schema={
                    "type": "object",
                    "properties": {
                        "patient_data": {"type": "object"},
                        "checkin_type": {"type": "string", "enum": ["appointment", "walkin"]}
                    },
                    "required": ["patient_data", "checkin_type"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "integer"},
                        "appointment_id": {"type": "integer"},
                        "confirmation_code": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }
            ),
            AgentCapability(
                name="appointment_lookup",
                version="1.0.0",
                description="Look up existing appointments",
                input_schema={
                    "type": "object",
                    "properties": {
                        "patient_data": {"type": "object"},
                        "confirmation_code": {"type": "string"}
                    },
                    "required": ["patient_data"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "appointments": {"type": "array"},
                        "status": {"type": "string"}
                    }
                }
            ),
            AgentCapability(
                name="walkin_registration",
                version="1.0.0",
                description="Register walk-in patients",
                input_schema={
                    "type": "object",
                    "properties": {
                        "patient_data": {"type": "object"},
                        "urgency_level": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}
                    },
                    "required": ["patient_data", "urgency_level"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "integer"},
                        "ticket_number": {"type": "string"},
                        "confirmation_code": {"type": "string"},
                        "estimated_wait_time": {"type": "integer"}
                    }
                }
            )
        ]
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Return agent capabilities."""
        return self.capabilities
    
    async def process_message(self, message: ProtocolMessage) -> Dict[str, Any]:
        """Process incoming messages."""
        try:
            self.log_activity("message_received", {
                "message_type": message.message_type.value,
                "sender": message.sender_id,
                "correlation_id": message.correlation_id
            })
            
            if message.message_type == MessageType.PATIENT_CHECKIN:
                return await self._handle_patient_checkin(message.payload)
            
            elif message.message_type == MessageType.APPOINTMENT_LOOKUP:
                return await self._handle_appointment_lookup(message.payload)
            
            elif message.message_type == MessageType.WALKIN_REGISTRATION:
                return await self._handle_walkin_registration(message.payload)
            
            elif message.message_type == MessageType.HEARTBEAT:
                return await self._handle_heartbeat(message.payload)
            
            else:
                return {
                    "status": "error",
                    "message": f"Unknown message type: {message.message_type.value}",
                    "acknowledgment_required": False
                }
        
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return {
                "status": "error",
                "message": str(e),
                "acknowledgment_required": False
            }
    
    async def _handle_patient_checkin(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle patient check-in."""
        try:
            patient_data = payload.get("patient_data", {})
            checkin_type = payload.get("checkin_type", "appointment")
            
            self.log_activity("patient_checkin_started", {
                "patient_name": f"{patient_data.get('first_name')} {patient_data.get('last_name')}",
                "checkin_type": checkin_type
            })
            
            # Create session
            session_id = f"session_{datetime.utcnow().timestamp()}"
            self.current_sessions[session_id] = {
                "patient_data": patient_data,
                "checkin_type": checkin_type,
                "started_at": datetime.utcnow(),
                "status": "processing"
            }
            
            if checkin_type == "appointment":
                # Look up existing appointment
                result = await self._lookup_appointment(patient_data, session_id)
            else:
                # Register as walk-in
                result = await self._register_walkin(patient_data, session_id)
            
            # Update session
            self.current_sessions[session_id]["result"] = result
            self.current_sessions[session_id]["status"] = "completed"
            
            return {
                "status": "success",
                "session_id": session_id,
                "result": result,
                "acknowledgment_required": True
            }
        
        except Exception as e:
            self.logger.error(f"Error in patient check-in: {e}")
            return {
                "status": "error",
                "message": str(e),
                "acknowledgment_required": False
            }
    
    async def _lookup_appointment(self, patient_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Look up existing appointment."""
        try:
            # Search for appointments by patient name and phone
            appointments = self.appointment_service.get_appointments(limit=10)
            
            # Filter by patient name (simplified matching)
            matching_appointments = []
            for apt in appointments:
                if (apt.patient.first_name.lower() == patient_data["first_name"].lower() and
                    apt.patient.last_name.lower() == patient_data["last_name"].lower()):
                    matching_appointments.append({
                        "id": apt.id,
                        "confirmation_code": apt.confirmation_code,
                        "scheduled_time": apt.scheduled_time.isoformat(),
                        "provider": apt.provider_name,
                        "reason": apt.reason,
                        "status": apt.status.value
                    })
            
            if matching_appointments:
                # Found appointments
                self.current_sessions[session_id]["found_appointments"] = matching_appointments
                
                return {
                    "status": "appointments_found",
                    "appointments": matching_appointments,
                    "message": "Please select your appointment"
                }
            else:
                # No appointments found, treat as walk-in
                self.log_activity("no_appointment_found", {
                    "patient_name": f"{patient_data['first_name']} {patient_data['last_name']}"
                })
                return await self._register_walkin(patient_data, session_id)
        
        except Exception as e:
            self.logger.error(f"Error looking up appointment: {e}")
            raise
    
    async def _register_walkin(self, patient_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Register patient as walk-in."""
        try:
            # Create walk-in registration
            walkin_data = {
                "patient": patient_data,
                "reason": patient_data.get("reason", "Walk-in consultation"),
                "priority": patient_data.get("priority", "medium")
            }
            
            result = self.walkin_service.register_walkin(walkin_data)
            
            self.current_sessions[session_id]["walkin_result"] = result
            
            # Notify orchestrator
            await self.send_message(
                recipient_id="orchestrator",
                message_type=MessageType.FLOW_START,
                payload={
                    "flow_type": "walkin_registration",
                    "patient_data": patient_data,
                    "session_data": {
                        "walkin_result": result,
                        "session_id": session_id
                    }
                },
                priority=MessagePriority.HIGH
            )
            
            self.log_activity("walkin_registered", {
                "patient_id": result["patient_id"],
                "ticket_number": result["ticket_number"]
            })
            
            return {
                "status": "walkin_registered",
                "patient_id": result["patient_id"],
                "ticket_number": result["ticket_number"],
                "confirmation_code": result["confirmation_code"],
                "estimated_wait_time": 30,
                "message": "You have been registered as a walk-in patient"
            }
        
        except Exception as e:
            self.logger.error(f"Error registering walk-in: {e}")
            raise
    
    async def _handle_appointment_lookup(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle appointment lookup request."""
        try:
            patient_data = payload.get("patient_data", {})
            confirmation_code = payload.get("confirmation_code")
            
            if confirmation_code:
                # Look up by confirmation code
                appointments = self.appointment_service.get_appointments(limit=10)
                matching_appointments = [
                    {
                        "id": apt.id,
                        "confirmation_code": apt.confirmation_code,
                        "scheduled_time": apt.scheduled_time.isoformat(),
                        "provider": apt.provider_name,
                        "reason": apt.reason,
                        "status": apt.status.value
                    }
                    for apt in appointments
                    if apt.confirmation_code == confirmation_code
                ]
            else:
                # Look up by patient data
                return await self._lookup_appointment(patient_data, f"lookup_{datetime.utcnow().timestamp()}")
            
            return {
                "status": "success",
                "appointments": matching_appointments,
                "acknowledgment_required": True
            }
        
        except Exception as e:
            self.logger.error(f"Error in appointment lookup: {e}")
            return {
                "status": "error",
                "message": str(e),
                "acknowledgment_required": False
            }
    
    async def _handle_walkin_registration(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle walk-in registration request."""
        try:
            patient_data = payload.get("patient_data", {})
            urgency_level = payload.get("urgency_level", "medium")
            
            # Update patient data with urgency
            patient_data["priority"] = urgency_level
            
            session_id = f"walkin_{datetime.utcnow().timestamp()}"
            result = await self._register_walkin(patient_data, session_id)
            
            return {
                "status": "success",
                "result": result,
                "acknowledgment_required": True
            }
        
        except Exception as e:
            self.logger.error(f"Error in walk-in registration: {e}")
            return {
                "status": "error",
                "message": str(e),
                "acknowledgment_required": False
            }
    
    async def _handle_heartbeat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle heartbeat message."""
        return {
            "status": "alive",
            "agent_id": self.agent_id,
            "active_sessions": len(self.current_sessions),
            "acknowledgment_required": False
        }
    
    async def confirm_appointment_selection(self, session_id: str, appointment_id: int) -> Dict[str, Any]:
        """Confirm selected appointment."""
        try:
            if session_id not in self.current_sessions:
                return {"status": "error", "message": "Session not found"}
            
            session = self.current_sessions[session_id]
            found_appointments = session.get("found_appointments", [])
            
            # Find the selected appointment
            selected_appointment = None
            for apt in found_appointments:
                if apt["id"] == appointment_id:
                    selected_appointment = apt
                    break
            
            if not selected_appointment:
                return {"status": "error", "message": "Appointment not found"}
            
            # Update session data
            session["selected_appointment"] = selected_appointment
            session["status"] = "appointment_confirmed"
            
            # Start appointment check-in flow
            await self.send_message(
                recipient_id="orchestrator",
                message_type=MessageType.FLOW_START,
                payload={
                    "flow_type": "appointment_checkin",
                    "patient_data": session["patient_data"],
                    "session_data": {
                        "selected_appointment": selected_appointment,
                        "session_id": session_id
                    }
                },
                priority=MessagePriority.HIGH
            )
            
            return {
                "status": "appointment_confirmed",
                "appointment": selected_appointment,
                "message": "Appointment confirmed, processing check-in"
            }
        
        except Exception as e:
            self.logger.error(f"Error confirming appointment: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_current_sessions(self) -> Dict[str, Any]:
        """Get current active sessions."""
        return {
            "active_sessions": len(self.current_sessions),
            "sessions": {
                session_id: {
                    "patient_name": f"{session['patient_data'].get('first_name')} {session['patient_data'].get('last_name')}",
                    "checkin_type": session["checkin_type"],
                    "status": session["status"],
                    "started_at": session["started_at"].isoformat()
                }
                for session_id, session in self.current_sessions.items()
            }
        }
    
    def clear_session(self, session_id: str):
        """Clear a specific session."""
        if session_id in self.current_sessions:
            del self.current_sessions[session_id]
            self.log_activity("session_cleared", {"session_id": session_id})
    
    def clear_all_sessions(self):
        """Clear all sessions."""
        self.current_sessions.clear()
        self.log_activity("all_sessions_cleared")
    
    async def stop(self):
        """Stop the agent and cleanup resources."""
        try:
            # Clear all sessions
            self.clear_all_sessions()
            
            # Close database session
            if self.db_session:
                self.db_session.close()
            
            # Call parent stop method
            await super().stop()
            
        except Exception as e:
            self.logger.error(f"Error stopping agent: {e}")
