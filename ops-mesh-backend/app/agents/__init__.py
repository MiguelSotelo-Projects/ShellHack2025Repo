"""
Agents Package

This package contains the Google ADK-based agent implementations for the hospital
operations management system.
"""

from .google_adk_agents import (
    GoogleADKFrontDeskAgent,
    GoogleADKOrchestratorAgent,
    GoogleADKAgentManager,
    initialize_agent_manager,
    get_agent_manager,
    start_agent_system,
    stop_agent_system
)

from .protocol import (
    AgentProtocol,
    ProtocolMessage,
    MessageType,
    MessagePriority,
    AgentStatus,
    FlowStatus,
    AgentCapability,
    FlowDefinition,
    FlowInstance,
    GoogleADKConfig,
    GoogleADKManager,
    PatientFlowTemplates,
    FlowValidator
)

__all__ = [
    # Google ADK Agents
    "GoogleADKFrontDeskAgent",
    "GoogleADKOrchestratorAgent",
    "GoogleADKAgentManager",
    "initialize_agent_manager",
    "get_agent_manager",
    "start_agent_system",
    "stop_agent_system",
    
    # Protocol
    "AgentProtocol",
    "ProtocolMessage",
    "MessageType",
    "MessagePriority",
    "AgentStatus",
    "FlowStatus",
    "AgentCapability",
    "FlowDefinition",
    "FlowInstance",
    "GoogleADKConfig",
    "GoogleADKManager",
    "PatientFlowTemplates",
    "FlowValidator"
]
