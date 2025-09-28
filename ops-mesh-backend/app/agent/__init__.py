"""
Agent module for ADK integration.
"""

from .simple_root_agent import simple_root_agent

# Export the simple root agent as the main root_agent for ADK
root_agent = simple_root_agent

__all__ = ["root_agent", "simple_root_agent"]
