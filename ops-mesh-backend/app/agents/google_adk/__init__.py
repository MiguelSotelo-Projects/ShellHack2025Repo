"""
Google ADK (Agent Development Kit) Implementation

This module provides a complete implementation of Google's Agent Development Kit
following the official specifications for agent creation, management, and A2A communication.
"""

from .agent import Agent
from .tools import BaseTool, ToolContext, tool
from .a2a import A2AServer, RemoteA2aAgent, A2AClient
from .protocol import A2AProtocol, AgentCard, MessageType, TaskRequest, TaskResponse
from .discovery import AgentDiscovery, AgentRegistry

__version__ = "1.0.0"
__all__ = [
    "Agent",
    "BaseTool", 
    "ToolContext",
    "tool",
    "A2AServer",
    "RemoteA2aAgent", 
    "A2AClient",
    "A2AProtocol",
    "AgentCard",
    "MessageType",
    "TaskRequest",
    "TaskResponse",
    "AgentDiscovery",
    "AgentRegistry"
]
