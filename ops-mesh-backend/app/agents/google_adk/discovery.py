"""
Agent Discovery Service

This module implements agent discovery and registry following A2A protocol specifications.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
import httpx
from dataclasses import dataclass

from .protocol import AgentCard, DiscoveryMessage, HeartbeatMessage

logger = logging.getLogger(__name__)


@dataclass
class AgentInfo:
    """Information about a discovered agent."""
    agent_card: AgentCard
    last_heartbeat: datetime
    status: str = "active"
    capabilities: Set[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = set()
            if self.agent_card.skills:
                for skill in self.agent_card.skills:
                    if "tags" in skill:
                        self.capabilities.update(skill["tags"])


class AgentRegistry:
    """
    Registry for managing discovered agents.
    
    Maintains a catalog of available agents with their capabilities and status.
    """
    
    def __init__(self):
        """Initialize the agent registry."""
        self.agents: Dict[str, AgentInfo] = {}
        self.capability_index: Dict[str, Set[str]] = {}
        self.heartbeat_timeout = timedelta(minutes=5)
    
    def register_agent(self, agent_card: AgentCard) -> None:
        """
        Register an agent in the registry.
        
        Args:
            agent_card: Agent card to register
        """
        agent_name = agent_card.name
        agent_info = AgentInfo(
            agent_card=agent_card,
            last_heartbeat=datetime.utcnow()
        )
        
        self.agents[agent_name] = agent_info
        
        # Update capability index
        for capability in agent_info.capabilities:
            if capability not in self.capability_index:
                self.capability_index[capability] = set()
            self.capability_index[capability].add(agent_name)
        
        logger.info(f"📝 Registered agent: {agent_name}")
    
    def unregister_agent(self, agent_name: str) -> None:
        """
        Unregister an agent from the registry.
        
        Args:
            agent_name: Name of agent to unregister
        """
        if agent_name in self.agents:
            agent_info = self.agents[agent_name]
            
            # Remove from capability index
            for capability in agent_info.capabilities:
                if capability in self.capability_index:
                    self.capability_index[capability].discard(agent_name)
                    if not self.capability_index[capability]:
                        del self.capability_index[capability]
            
            del self.agents[agent_name]
            logger.info(f"🗑️ Unregistered agent: {agent_name}")
    
    def update_heartbeat(self, agent_name: str) -> None:
        """
        Update the heartbeat timestamp for an agent.
        
        Args:
            agent_name: Name of the agent
        """
        if agent_name in self.agents:
            self.agents[agent_name].last_heartbeat = datetime.utcnow()
            self.agents[agent_name].status = "active"
    
    def get_agent(self, agent_name: str) -> Optional[AgentInfo]:
        """
        Get agent information by name.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            AgentInfo if found, None otherwise
        """
        return self.agents.get(agent_name)
    
    def find_agents_by_capability(self, capability: str) -> List[AgentInfo]:
        """
        Find agents that have a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of agents with the capability
        """
        agent_names = self.capability_index.get(capability, set())
        return [self.agents[name] for name in agent_names if name in self.agents]
    
    def find_agents_by_query(self, query: str) -> List[AgentInfo]:
        """
        Find agents matching a text query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching agents
        """
        query_lower = query.lower()
        matching_agents = []
        
        for agent_info in self.agents.values():
            # Search in name, description, and skills
            if (query_lower in agent_info.agent_card.name.lower() or
                query_lower in agent_info.agent_card.description.lower()):
                matching_agents.append(agent_info)
                continue
            
            # Search in skills
            if agent_info.agent_card.skills:
                for skill in agent_info.agent_card.skills:
                    if (query_lower in skill.get("name", "").lower() or
                        query_lower in skill.get("description", "").lower()):
                        matching_agents.append(agent_info)
                        break
        
        return matching_agents
    
    def get_active_agents(self) -> List[AgentInfo]:
        """Get all active agents."""
        now = datetime.utcnow()
        active_agents = []
        
        for agent_info in self.agents.values():
            if now - agent_info.last_heartbeat < self.heartbeat_timeout:
                active_agents.append(agent_info)
            else:
                agent_info.status = "inactive"
        
        return active_agents
    
    def cleanup_inactive_agents(self) -> int:
        """
        Remove inactive agents from the registry.
        
        Returns:
            Number of agents removed
        """
        now = datetime.utcnow()
        inactive_agents = []
        
        for agent_name, agent_info in self.agents.items():
            if now - agent_info.last_heartbeat >= self.heartbeat_timeout:
                inactive_agents.append(agent_name)
        
        for agent_name in inactive_agents:
            self.unregister_agent(agent_name)
        
        if inactive_agents:
            logger.info(f"🧹 Cleaned up {len(inactive_agents)} inactive agents")
        
        return len(inactive_agents)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        active_count = len(self.get_active_agents())
        total_count = len(self.agents)
        
        return {
            "total_agents": total_count,
            "active_agents": active_count,
            "inactive_agents": total_count - active_count,
            "capabilities": len(self.capability_index),
            "capability_list": list(self.capability_index.keys())
        }


class AgentDiscovery:
    """
    Agent discovery service for finding and connecting to remote agents.
    
    Implements A2A protocol discovery mechanisms.
    """
    
    def __init__(self, registry: Optional[AgentRegistry] = None):
        """
        Initialize agent discovery service.
        
        Args:
            registry: Agent registry to use (creates new one if None)
        """
        self.registry = registry or AgentRegistry()
        self.discovery_endpoints: List[str] = []
        self.httpx_client = httpx.AsyncClient(timeout=10.0)
    
    def add_discovery_endpoint(self, endpoint: str) -> None:
        """
        Add a discovery endpoint.
        
        Args:
            endpoint: URL of the discovery endpoint
        """
        if endpoint not in self.discovery_endpoints:
            self.discovery_endpoints.append(endpoint)
            logger.info(f"📡 Added discovery endpoint: {endpoint}")
    
    async def discover_agents(self, query: Optional[str] = None) -> List[AgentCard]:
        """
        Discover agents from all registered endpoints.
        
        Args:
            query: Optional search query
            
        Returns:
            List of discovered agent cards
        """
        discovered_agents = []
        
        for endpoint in self.discovery_endpoints:
            try:
                agents = await self._discover_from_endpoint(endpoint, query)
                discovered_agents.extend(agents)
            except Exception as e:
                logger.error(f"❌ Discovery failed for endpoint {endpoint}: {e}")
        
        # Register discovered agents
        for agent_card in discovered_agents:
            self.registry.register_agent(agent_card)
        
        logger.info(f"🔍 Discovered {len(discovered_agents)} agents")
        return discovered_agents
    
    async def _discover_from_endpoint(
        self, 
        endpoint: str, 
        query: Optional[str] = None
    ) -> List[AgentCard]:
        """Discover agents from a specific endpoint."""
        try:
            # Create discovery message
            discovery_message = DiscoveryMessage(
                agent_id="discovery_client",
                agent_card=AgentCard(
                    name="discovery_client",
                    description="Agent discovery client"
                ),
                query=query
            )
            
            # Send discovery request
            response = await self.httpx_client.post(
                f"{endpoint}/discover",
                json=discovery_message.dict()
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            agents_data = data.get("agents", [])
            
            # Convert to agent cards
            agent_cards = []
            for agent_data in agents_data:
                try:
                    agent_card = AgentCard.from_dict(agent_data)
                    agent_cards.append(agent_card)
                except Exception as e:
                    logger.error(f"❌ Failed to parse agent card: {e}")
            
            return agent_cards
            
        except Exception as e:
            logger.error(f"❌ Discovery request failed for {endpoint}: {e}")
            return []
    
    async def register_agent(self, agent_card: AgentCard) -> None:
        """
        Register an agent with discovery endpoints.
        
        Args:
            agent_card: Agent card to register
        """
        for endpoint in self.discovery_endpoints:
            try:
                await self._register_with_endpoint(endpoint, agent_card)
            except Exception as e:
                logger.error(f"❌ Registration failed for endpoint {endpoint}: {e}")
    
    async def _register_with_endpoint(self, endpoint: str, agent_card: AgentCard) -> None:
        """Register an agent with a specific endpoint."""
        try:
            response = await self.httpx_client.post(
                f"{endpoint}/register",
                json=agent_card.to_dict()
            )
            response.raise_for_status()
            logger.info(f"✅ Registered agent with {endpoint}")
            
        except Exception as e:
            logger.error(f"❌ Registration failed for {endpoint}: {e}")
            raise
    
    async def send_heartbeat(self, agent_name: str) -> None:
        """
        Send heartbeat to discovery endpoints.
        
        Args:
            agent_name: Name of the agent sending heartbeat
        """
        agent_info = self.registry.get_agent(agent_name)
        if not agent_info:
            logger.warning(f"❌ Agent {agent_name} not found in registry")
            return
        
        heartbeat = HeartbeatMessage(
            agent_id=agent_name,
            capabilities=list(agent_info.capabilities),
            current_tasks=0  # TODO: Get actual task count
        )
        
        for endpoint in self.discovery_endpoints:
            try:
                await self._send_heartbeat_to_endpoint(endpoint, heartbeat)
            except Exception as e:
                logger.error(f"❌ Heartbeat failed for endpoint {endpoint}: {e}")
    
    async def _send_heartbeat_to_endpoint(self, endpoint: str, heartbeat: HeartbeatMessage) -> None:
        """Send heartbeat to a specific endpoint."""
        try:
            response = await self.httpx_client.post(
                f"{endpoint}/heartbeat",
                json=heartbeat.dict()
            )
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"❌ Heartbeat failed for {endpoint}: {e}")
            raise
    
    def find_agents_by_capability(self, capability: str) -> List[AgentCard]:
        """
        Find agents with a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of agent cards with the capability
        """
        agent_infos = self.registry.find_agents_by_capability(capability)
        return [info.agent_card for info in agent_infos]
    
    def find_agents_by_query(self, query: str) -> List[AgentCard]:
        """
        Find agents matching a text query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching agent cards
        """
        agent_infos = self.registry.find_agents_by_query(query)
        return [info.agent_card for info in agent_infos]
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get discovery service statistics."""
        return self.registry.get_stats()
    
    async def start_heartbeat_monitor(self, interval: int = 60) -> None:
        """
        Start monitoring agent heartbeats.
        
        Args:
            interval: Heartbeat check interval in seconds
        """
        while True:
            try:
                # Cleanup inactive agents
                self.registry.cleanup_inactive_agents()
                
                # Wait for next check
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Heartbeat monitor error: {e}")
                await asyncio.sleep(interval)
    
    async def close(self) -> None:
        """Close the discovery service."""
        await self.httpx_client.aclose()
        logger.info("🔌 Agent discovery service closed")
