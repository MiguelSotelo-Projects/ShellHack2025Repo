"""
Google ADK Agent Protocol

This package provides the core agent protocol implementation using Google ADK
for the hospital operations management system.
"""

from .agent_protocol import (
    AgentProtocol,
    ProtocolMessage,
    MessageType,
    MessagePriority,
    AgentStatus,
    FlowStatus,
    AgentCapability,
    FlowDefinition,
    FlowInstance
)

from .google_adk_config import (
    GoogleADKConfig,
    GoogleADKManager,
    create_google_adk_config,
    initialize_google_adk,
    get_google_adk_manager,
    shutdown_google_adk
)

from .flow_definitions import (
    PatientFlowTemplates,
    FlowValidator
)

__all__ = [
    # Core protocol classes
    "AgentProtocol",
    "ProtocolMessage",
    "MessageType",
    "MessagePriority",
    "AgentStatus",
    "FlowStatus",
    "AgentCapability",
    "FlowDefinition",
    "FlowInstance",
    
    # Google ADK configuration
    "GoogleADKConfig",
    "GoogleADKManager",
    "create_google_adk_config",
    "initialize_google_adk",
    "get_google_adk_manager",
    "shutdown_google_adk",
    
    # Flow definitions
    "PatientFlowTemplates",
    "FlowValidator"
]
