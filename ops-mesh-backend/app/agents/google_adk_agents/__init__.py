"""
Google ADK Agents

This package provides Google ADK-based agent implementations for the hospital
operations management system.
"""

from .frontdesk_agent import GoogleADKFrontDeskAgent
from .orchestrator_agent import GoogleADKOrchestratorAgent
from .agent_manager import (
    GoogleADKAgentManager,
    initialize_agent_manager,
    get_agent_manager,
    start_agent_system,
    stop_agent_system
)

__all__ = [
    # Agent implementations
    "GoogleADKFrontDeskAgent",
    "GoogleADKOrchestratorAgent",
    
    # Agent management
    "GoogleADKAgentManager",
    "initialize_agent_manager",
    "get_agent_manager",
    "start_agent_system",
    "stop_agent_system"
]
