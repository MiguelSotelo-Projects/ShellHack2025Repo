"""
Google ADK Orchestrator Agent

This agent coordinates the entire patient flow and manages other agents
using Google ADK and the agent protocol.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ..protocol.agent_protocol import (
    AgentProtocol, ProtocolMessage, MessageType, MessagePriority,
    AgentCapability, AgentStatus, FlowInstance, FlowStatus
)
from ..protocol.flow_definitions import PatientFlowTemplates, FlowValidator


class GoogleADKOrchestratorAgent(AgentProtocol):
    """Orchestrator agent using Google ADK."""
    
    def __init__(self, project_id: str, region: str = "us-central1"):
        super().__init__(
            agent_id="orchestrator",
            agent_name="Orchestrator Agent",
            project_id=project_id,
            region=region
        )
        
        # Agent registry
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_health: Dict[str, Dict[str, Any]] = {}
        
        # Flow management
        self.flow_templates = PatientFlowTemplates.get_all_flows()
        self.active_flows: Dict[str, FlowInstance] = {}
        self.completed_flows: List[FlowInstance] = []
        self.failed_flows: List[FlowInstance] = []
        
        # System metrics
        self.system_metrics = {
            "total_flows_started": 0,
            "total_flows_completed": 0,
            "total_flows_failed": 0,
            "active_agents": 0,
            "system_uptime": datetime.utcnow()
        }
        
        # Define capabilities
        self.capabilities = [
            AgentCapability(
                name="flow_orchestration",
                version="1.0.0",
                description="Orchestrate patient flows across multiple agents",
                input_schema={
                    "type": "object",
                    "properties": {
                        "flow_type": {"type": "string"},
                        "patient_data": {"type": "object"},
                        "session_data": {"type": "object"}
                    },
                    "required": ["flow_type", "patient_data"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "flow_instance_id": {"type": "string"},
                        "status": {"type": "string"},
                        "estimated_duration": {"type": "integer"}
                    }
                }
            ),
            AgentCapability(
                name="agent_coordination",
                version="1.0.0",
                description="Coordinate communication between agents",
                input_schema={
                    "type": "object",
                    "properties": {
                        "target_agents": {"type": "array"},
                        "message_type": {"type": "string"},
                        "payload": {"type": "object"}
                    },
                    "required": ["target_agents", "message_type", "payload"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "responses": {"type": "array"},
                        "status": {"type": "string"}
                    }
                }
            ),
            AgentCapability(
                name="system_monitoring",
                version="1.0.0",
                description="Monitor system health and performance",
                input_schema={
                    "type": "object",
                    "properties": {
                        "monitoring_type": {"type": "string", "enum": ["health", "performance", "flows"]}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "system_status": {"type": "object"},
                        "metrics": {"type": "object"},
                        "recommendations": {"type": "array"}
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
            
            if message.message_type == MessageType.REGISTRATION:
                return await self._handle_agent_registration(message.payload)
            
            elif message.message_type == MessageType.DEREGISTRATION:
                return await self._handle_agent_deregistration(message.payload)
            
            elif message.message_type == MessageType.HEARTBEAT:
                return await self._handle_heartbeat(message.payload, message.sender_id)
            
            elif message.message_type == MessageType.FLOW_START:
                return await self._handle_flow_start(message.payload)
            
            elif message.message_type == MessageType.FLOW_STEP:
                return await self._handle_flow_step(message.payload)
            
            elif message.message_type == MessageType.FLOW_COMPLETE:
                return await self._handle_flow_complete(message.payload)
            
            elif message.message_type == MessageType.FLOW_FAILURE:
                return await self._handle_flow_failure(message.payload)
            
            elif message.message_type == MessageType.STATUS_UPDATE:
                return await self._handle_status_update(message.payload, message.sender_id)
            
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
    
    async def _handle_agent_registration(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent registration."""
        try:
            agent_id = payload.get("agent_id")
            agent_name = payload.get("agent_name")
            capabilities = payload.get("capabilities", [])
            
            if not agent_id:
                return {
                    "status": "error",
                    "message": "Agent ID is required",
                    "acknowledgment_required": False
                }
            
            # Register agent
            self.registered_agents[agent_id] = {
                "agent_name": agent_name,
                "capabilities": capabilities,
                "registered_at": datetime.utcnow(),
                "status": AgentStatus.ONLINE,
                "last_heartbeat": datetime.utcnow(),
                "project_id": payload.get("project_id"),
                "region": payload.get("region")
            }
            
            # Initialize health tracking
            self.agent_health[agent_id] = {
                "status": "healthy",
                "last_check": datetime.utcnow(),
                "error_count": 0,
                "response_time_avg": 0
            }
            
            self.system_metrics["active_agents"] = len(self.registered_agents)
            
            self.log_activity("agent_registered", {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "capabilities_count": len(capabilities)
            })
            
            # Send welcome message
            await self.send_message(
                recipient_id=agent_id,
                message_type=MessageType.ACKNOWLEDGMENT,
                payload={
                    "message": "Welcome to the system",
                    "system_status": "operational",
                    "registered_agents": len(self.registered_agents)
                },
                priority=MessagePriority.NORMAL
            )
            
            return {
                "status": "registered",
                "agent_id": agent_id,
                "system_status": "operational",
                "acknowledgment_required": False
            }
        
        except Exception as e:
            self.logger.error(f"Error handling agent registration: {e}")
            return {
                "status": "error",
                "message": str(e),
                "acknowledgment_required": False
            }
    
    async def _handle_agent_deregistration(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent deregistration."""
        try:
            agent_id = payload.get("agent_id")
            
            if agent_id in self.registered_agents:
                del self.registered_agents[agent_id]
            
            if agent_id in self.agent_health:
                del self.agent_health[agent_id]
            
            self.system_metrics["active_agents"] = len(self.registered_agents)
            
            self.log_activity("agent_deregistered", {"agent_id": agent_id})
            
            return {
                "status": "deregistered",
                "agent_id": agent_id,
                "acknowledgment_required": False
            }
        
        except Exception as e:
            self.logger.error(f"Error handling agent deregistration: {e}")
            return {
                "status": "error",
                "message": str(e),
                "acknowledgment_required": False
            }
    
    async def _handle_heartbeat(self, payload: Dict[str, Any], sender_id: str) -> Dict[str, Any]:
        """Handle heartbeat message."""
        try:
            if sender_id in self.registered_agents:
                self.registered_agents[sender_id]["last_heartbeat"] = datetime.utcnow()
                self.registered_agents[sender_id]["status"] = AgentStatus.ONLINE
                
                # Update health metrics
                if sender_id in self.agent_health:
                    self.agent_health[sender_id]["last_check"] = datetime.utcnow()
                    self.agent_health[sender_id]["status"] = "healthy"
            
            return {
                "status": "heartbeat_received",
                "agent_id": sender_id,
                "acknowledgment_required": False
            }
        
        except Exception as e:
            self.logger.error(f"Error handling heartbeat: {e}")
            return {
                "status": "error",
                "message": str(e),
                "acknowledgment_required": False
            }
    
    async def _handle_flow_start(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flow start request."""
        try:
            flow_type = payload.get("flow_type")
            patient_data = payload.get("patient_data", {})
            session_data = payload.get("session_data", {})
            
            if not flow_type or flow_type not in self.flow_templates:
                return {
                    "status": "error",
                    "message": f"Unknown flow type: {flow_type}",
                    "acknowledgment_required": False
                }
            
            # Get flow template
            flow_template = self.flow_templates[flow_type]
            
            # Validate flow definition
            validation_errors = FlowValidator.validate_flow_definition(flow_template)
            if validation_errors:
                return {
                    "status": "error",
                    "message": f"Flow validation failed: {validation_errors}",
                    "acknowledgment_required": False
                }
            
            # Create flow instance
            instance_id = f"flow_{datetime.utcnow().timestamp()}"
            flow_instance = FlowInstance(
                instance_id=instance_id,
                flow_definition=flow_template,
                patient_data=patient_data,
                session_data=session_data,
                current_step=0,
                status=FlowStatus.ACTIVE,
                started_at=datetime.utcnow()
            )
            
            self.active_flows[instance_id] = flow_instance
            self.system_metrics["total_flows_started"] += 1
            
            self.log_activity("flow_started", {
                "flow_instance_id": instance_id,
                "flow_type": flow_type,
                "patient_name": f"{patient_data.get('first_name')} {patient_data.get('last_name')}"
            })
            
            # Start the flow
            await self._execute_flow_step(flow_instance)
            
            return {
                "status": "flow_started",
                "flow_instance_id": instance_id,
                "flow_type": flow_type,
                "estimated_duration": flow_template.timeout_minutes,
                "acknowledgment_required": False
            }
        
        except Exception as e:
            self.logger.error(f"Error handling flow start: {e}")
            return {
                "status": "error",
                "message": str(e),
                "acknowledgment_required": False
            }
    
    async def _execute_flow_step(self, flow_instance: FlowInstance):
        """Execute the next step in a flow."""
        try:
            if flow_instance.current_step >= len(flow_instance.flow_definition.steps):
                # Flow completed
                await self._complete_flow(flow_instance)
                return
            
            # Get current step
            current_step = flow_instance.flow_definition.steps[flow_instance.current_step]
            target_agent = current_step["agent"]
            
            # Check if target agent is available
            if target_agent not in self.registered_agents:
                await self._fail_flow(flow_instance, f"Target agent {target_agent} not available")
                return
            
            # Prepare step payload
            step_payload = {
                "flow_instance_id": flow_instance.instance_id,
                "step_id": current_step["step_id"],
                "patient_data": flow_instance.patient_data,
                "session_data": flow_instance.session_data,
                "step_data": current_step
            }
            
            # Add previous step results if any
            if flow_instance.step_results:
                step_payload["previous_results"] = flow_instance.step_results
            
            # Send message to target agent
            message_type = MessageType(current_step["message_type"])
            priority = MessagePriority(current_step["priority"])
            
            await self.send_message(
                recipient_id=target_agent,
                message_type=message_type,
                payload=step_payload,
                priority=priority,
                correlation_id=flow_instance.instance_id
            )
            
            self.log_activity("flow_step_sent", {
                "flow_instance_id": flow_instance.instance_id,
                "step": flow_instance.current_step,
                "target_agent": target_agent,
                "step_id": current_step["step_id"]
            })
            
        except Exception as e:
            self.logger.error(f"Error executing flow step: {e}")
            await self._fail_flow(flow_instance, str(e))
    
    async def _handle_flow_step(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flow step completion."""
        try:
            flow_instance_id = payload.get("flow_instance_id")
            step_id = payload.get("step_id")
            step_result = payload.get("step_result", {})
            
            if flow_instance_id not in self.active_flows:
                return {
                    "status": "error",
                    "message": f"Flow instance {flow_instance_id} not found",
                    "acknowledgment_required": False
                }
            
            flow_instance = self.active_flows[flow_instance_id]
            
            # Store step result
            flow_instance.step_results.append({
                "step_id": step_id,
                "result": step_result,
                "completed_at": datetime.utcnow()
            })
            
            # Move to next step
            flow_instance.current_step += 1
            
            # Execute next step
            await self._execute_flow_step(flow_instance)
            
            return {
                "status": "step_completed",
                "flow_instance_id": flow_instance_id,
                "next_step": flow_instance.current_step,
                "acknowledgment_required": False
            }
        
        except Exception as e:
            self.logger.error(f"Error handling flow step: {e}")
            return {
                "status": "error",
                "message": str(e),
                "acknowledgment_required": False
            }
    
    async def _handle_flow_complete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flow completion."""
        try:
            flow_instance_id = payload.get("flow_instance_id")
            
            if flow_instance_id in self.active_flows:
                flow_instance = self.active_flows[flow_instance_id]
                await self._complete_flow(flow_instance)
            
            return {
                "status": "flow_completed",
                "flow_instance_id": flow_instance_id,
                "acknowledgment_required": False
            }
        
        except Exception as e:
            self.logger.error(f"Error handling flow completion: {e}")
            return {
                "status": "error",
                "message": str(e),
                "acknowledgment_required": False
            }
    
    async def _handle_flow_failure(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flow failure."""
        try:
            flow_instance_id = payload.get("flow_instance_id")
            error_message = payload.get("error_message", "Unknown error")
            
            if flow_instance_id in self.active_flows:
                flow_instance = self.active_flows[flow_instance_id]
                await self._fail_flow(flow_instance, error_message)
            
            return {
                "status": "flow_failed",
                "flow_instance_id": flow_instance_id,
                "error_message": error_message,
                "acknowledgment_required": False
            }
        
        except Exception as e:
            self.logger.error(f"Error handling flow failure: {e}")
            return {
                "status": "error",
                "message": str(e),
                "acknowledgment_required": False
            }
    
    async def _complete_flow(self, flow_instance: FlowInstance):
        """Complete a flow instance."""
        try:
            flow_instance.status = FlowStatus.COMPLETED
            flow_instance.completed_at = datetime.utcnow()
            
            # Move to completed flows
            self.completed_flows.append(flow_instance)
            del self.active_flows[flow_instance.instance_id]
            
            self.system_metrics["total_flows_completed"] += 1
            
            self.log_activity("flow_completed", {
                "flow_instance_id": flow_instance.instance_id,
                "flow_type": flow_instance.flow_definition.flow_name,
                "duration_minutes": (flow_instance.completed_at - flow_instance.started_at).total_seconds() / 60
            })
            
            # Send completion notification
            await self.send_broadcast(
                message_type=MessageType.FLOW_COMPLETE,
                payload={
                    "flow_instance_id": flow_instance.instance_id,
                    "flow_type": flow_instance.flow_definition.flow_name,
                    "patient_data": flow_instance.patient_data,
                    "completion_time": flow_instance.completed_at.isoformat()
                },
                priority=MessagePriority.NORMAL
            )
        
        except Exception as e:
            self.logger.error(f"Error completing flow: {e}")
    
    async def _fail_flow(self, flow_instance: FlowInstance, error_message: str):
        """Fail a flow instance."""
        try:
            flow_instance.status = FlowStatus.FAILED
            flow_instance.completed_at = datetime.utcnow()
            flow_instance.error_message = error_message
            
            # Move to failed flows
            self.failed_flows.append(flow_instance)
            del self.active_flows[flow_instance.instance_id]
            
            self.system_metrics["total_flows_failed"] += 1
            
            self.log_activity("flow_failed", {
                "flow_instance_id": flow_instance.instance_id,
                "flow_type": flow_instance.flow_definition.flow_name,
                "error_message": error_message
            })
            
            # Send failure notification
            await self.send_broadcast(
                message_type=MessageType.FLOW_FAILURE,
                payload={
                    "flow_instance_id": flow_instance.instance_id,
                    "flow_type": flow_instance.flow_definition.flow_name,
                    "error_message": error_message,
                    "failed_at": flow_instance.completed_at.isoformat()
                },
                priority=MessagePriority.HIGH
            )
        
        except Exception as e:
            self.logger.error(f"Error failing flow: {e}")
    
    async def _handle_status_update(self, payload: Dict[str, Any], sender_id: str) -> Dict[str, Any]:
        """Handle status update from agent."""
        try:
            if sender_id in self.registered_agents:
                self.registered_agents[sender_id].update(payload)
                self.registered_agents[sender_id]["last_update"] = datetime.utcnow()
            
            return {
                "status": "status_updated",
                "agent_id": sender_id,
                "acknowledgment_required": False
            }
        
        except Exception as e:
            self.logger.error(f"Error handling status update: {e}")
            return {
                "status": "error",
                "message": str(e),
                "acknowledgment_required": False
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "system_health": "operational",
            "registered_agents": len(self.registered_agents),
            "active_flows": len(self.active_flows),
            "completed_flows": len(self.completed_flows),
            "failed_flows": len(self.failed_flows),
            "system_metrics": self.system_metrics,
            "agent_health": self.agent_health,
            "uptime_minutes": (datetime.utcnow() - self.system_metrics["system_uptime"]).total_seconds() / 60,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_flow_status(self, flow_instance_id: Optional[str] = None) -> Dict[str, Any]:
        """Get flow status information."""
        if flow_instance_id:
            if flow_instance_id in self.active_flows:
                flow = self.active_flows[flow_instance_id]
                return {
                    "flow_instance_id": flow_instance_id,
                    "status": flow.status.value,
                    "flow_type": flow.flow_definition.flow_name,
                    "current_step": flow.current_step,
                    "total_steps": len(flow.flow_definition.steps),
                    "started_at": flow.started_at.isoformat(),
                    "patient_data": flow.patient_data
                }
            else:
                return {"error": "Flow instance not found"}
        else:
            return {
                "active_flows": len(self.active_flows),
                "completed_flows": len(self.completed_flows),
                "failed_flows": len(self.failed_flows),
                "flow_templates": list(self.flow_templates.keys())
            }
    
    async def health_check_agents(self) -> Dict[str, Any]:
        """Perform health check on all registered agents."""
        health_results = {}
        
        for agent_id in self.registered_agents:
            try:
                # Send health check message
                await self.send_message(
                    recipient_id=agent_id,
                    message_type=MessageType.HEARTBEAT,
                    payload={"health_check": True},
                    priority=MessagePriority.LOW
                )
                
                health_results[agent_id] = "healthy"
                
            except Exception as e:
                health_results[agent_id] = f"unhealthy: {str(e)}"
                self.agent_health[agent_id]["status"] = "unhealthy"
                self.agent_health[agent_id]["error_count"] += 1
        
        return {
            "health_check_results": health_results,
            "timestamp": datetime.utcnow().isoformat()
        }
