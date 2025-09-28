"""
Vertex AI Enhanced Hospital Agents

This module creates enhanced hospital agents that use Vertex AI for intelligent
reasoning and natural language processing while maintaining Google ADK compatibility.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .vertex_ai_integration import initialize_vertex_ai, create_enhanced_agent
from .hospital_agents.frontdesk_agent import frontdesk_agent
from .hospital_agents.queue_agent import queue_agent

logger = logging.getLogger(__name__)


class VertexAIHospitalAgents:
    """
    Manager for Vertex AI enhanced hospital agents.
    
    This class manages all hospital agents enhanced with Vertex AI capabilities.
    """
    
    def __init__(self, api_key: str, project_id: str = "shellhacks2025"):
        """
        Initialize Vertex AI hospital agents.
        
        Args:
            api_key: Google Cloud API key
            project_id: Google Cloud project ID
        """
        self.api_key = api_key
        self.project_id = project_id
        self.initialized = False
        self.agents = {}
        
        # Initialize Vertex AI
        if initialize_vertex_ai(api_key, project_id):
            self._create_enhanced_agents()
            self.initialized = True
            logger.info("✅ Vertex AI Hospital Agents initialized successfully")
        else:
            logger.error("❌ Failed to initialize Vertex AI Hospital Agents")
    
    def _create_enhanced_agents(self) -> None:
        """Create enhanced agents with Vertex AI capabilities."""
        try:
            # Enhance FrontDesk Agent
            self.agents["frontdesk"] = create_enhanced_agent(frontdesk_agent)
            logger.info("✅ Enhanced FrontDesk Agent with Vertex AI")
            
            # Enhance Queue Agent
            self.agents["queue"] = create_enhanced_agent(queue_agent)
            logger.info("✅ Enhanced Queue Agent with Vertex AI")
            
        except Exception as e:
            logger.error(f"❌ Failed to create enhanced agents: {e}")
    
    async def start_all_agents(self) -> None:
        """Start all enhanced agents."""
        for agent_name, agent in self.agents.items():
            try:
                if hasattr(agent, 'start'):
                    await agent.start()
                elif hasattr(agent, 'base_agent') and hasattr(agent.base_agent, 'start'):
                    await agent.base_agent.start()
                logger.info(f"🚀 Started enhanced agent: {agent_name}")
            except Exception as e:
                logger.error(f"❌ Failed to start agent {agent_name}: {e}")
    
    async def stop_all_agents(self) -> None:
        """Stop all enhanced agents."""
        for agent_name, agent in self.agents.items():
            try:
                if hasattr(agent, 'stop'):
                    await agent.stop()
                elif hasattr(agent, 'base_agent') and hasattr(agent.base_agent, 'stop'):
                    await agent.base_agent.stop()
                logger.info(f"🛑 Stopped enhanced agent: {agent_name}")
            except Exception as e:
                logger.error(f"❌ Failed to stop agent {agent_name}: {e}")
    
    def get_agent(self, agent_name: str):
        """Get a specific enhanced agent."""
        return self.agents.get(agent_name)
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all enhanced agents."""
        return self.agents
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all enhanced agents."""
        status = {
            "initialized": self.initialized,
            "vertex_ai_enabled": self.initialized,
            "project_id": self.project_id,
            "agents": {}
        }
        
        for agent_name, agent in self.agents.items():
            if hasattr(agent, 'get_enhanced_status'):
                status["agents"][agent_name] = agent.get_enhanced_status()
            elif hasattr(agent, 'get_status'):
                status["agents"][agent_name] = agent.get_status()
            else:
                status["agents"][agent_name] = {"name": agent_name, "status": "unknown"}
        
        return status


# Global instance
vertex_ai_agents = None


def initialize_vertex_ai_agents(api_key: str, project_id: str = "shellhacks2025") -> VertexAIHospitalAgents:
    """
    Initialize Vertex AI hospital agents globally.
    
    Args:
        api_key: Google Cloud API key
        project_id: Google Cloud project ID
        
    Returns:
        VertexAIHospitalAgents instance
    """
    global vertex_ai_agents
    
    try:
        vertex_ai_agents = VertexAIHospitalAgents(api_key, project_id)
        logger.info("✅ Vertex AI Hospital Agents initialized globally")
        return vertex_ai_agents
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Vertex AI Hospital Agents: {e}")
        return None


def get_vertex_ai_agents() -> Optional[VertexAIHospitalAgents]:
    """Get the global Vertex AI agents instance."""
    return vertex_ai_agents
