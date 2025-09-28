"""
Agent Discovery Service for A2A Protocol

This service handles agent discovery, registration, and capability management
for the A2A (Agent-to-Agent) protocol.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class AgentInfo:
    """Agent information for discovery"""
    agent_id: str
    name: str
    description: str
    capabilities: List[str]
    endpoints: Dict[str, Any]
    dependencies: List[str]
    status: str
    last_heartbeat: datetime
    agent_card_path: str
    port: Optional[int] = None
    host: str = "localhost"
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['last_heartbeat'] = self.last_heartbeat.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentInfo':
        data['last_heartbeat'] = datetime.fromisoformat(data['last_heartbeat'])
        return cls(**data)


class AgentDiscoveryService:
    """Agent Discovery Service for A2A Protocol"""
    
    def __init__(self):
        self.registered_agents: Dict[str, AgentInfo] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        self.running = False
        self.heartbeat_timeout = 60  # seconds
    
    async def start(self):
        """Start the discovery service"""
        self.running = True
        logger.info("🔍 Agent Discovery Service started")
        
        # Start heartbeat monitoring
        asyncio.create_task(self._monitor_heartbeats())
        
        # Load existing agent cards
        await self._load_agent_cards()
    
    async def stop(self):
        """Stop the discovery service"""
        self.running = False
        logger.info("🛑 Agent Discovery Service stopped")
    
    async def _load_agent_cards(self):
        """Load agent cards from the agents directory"""
        agents_dir = Path("ops-mesh-backend/agents")
        if not agents_dir.exists():
            logger.warning(f"Agents directory not found: {agents_dir}")
            return
        
        for agent_card_path in agents_dir.glob("*.json"):
            try:
                await self._load_agent_card(agent_card_path)
            except Exception as e:
                logger.error(f"Error loading agent card {agent_card_path}: {e}")
    
    async def _load_agent_card(self, agent_card_path: Path):
        """Load a single agent card"""
        try:
            with open(agent_card_path, 'r') as f:
                agent_card = json.load(f)
            
            agent_id = agent_card.get("name", agent_card_path.stem)
            
            agent_info = AgentInfo(
                agent_id=agent_id,
                name=agent_card.get("name", agent_id),
                description=agent_card.get("description", ""),
                capabilities=agent_card.get("capabilities", []),
                endpoints=agent_card.get("endpoints", {}),
                dependencies=agent_card.get("dependencies", []),
                status="available",
                last_heartbeat=datetime.now(),
                agent_card_path=str(agent_card_path)
            )
            
            self.registered_agents[agent_id] = agent_info
            self.agent_capabilities[agent_id] = agent_info.capabilities
            
            logger.info(f"📋 Loaded agent card: {agent_id}")
            
        except Exception as e:
            logger.error(f"Error loading agent card {agent_card_path}: {e}")
    
    async def register_agent(self, agent_id: str, agent_info: Dict[str, Any]) -> bool:
        """Register an agent with the discovery service"""
        try:
            # Update existing agent or create new one
            if agent_id in self.registered_agents:
                existing_agent = self.registered_agents[agent_id]
                existing_agent.status = agent_info.get("status", "available")
                existing_agent.last_heartbeat = datetime.now()
            else:
                # Create new agent info
                new_agent = AgentInfo(
                    agent_id=agent_id,
                    name=agent_info.get("name", agent_id),
                    description=agent_info.get("description", ""),
                    capabilities=agent_info.get("capabilities", []),
                    endpoints=agent_info.get("endpoints", {}),
                    dependencies=agent_info.get("dependencies", []),
                    status=agent_info.get("status", "available"),
                    last_heartbeat=datetime.now(),
                    agent_card_path=agent_info.get("agent_card_path", "")
                )
                self.registered_agents[agent_id] = new_agent
                self.agent_capabilities[agent_id] = new_agent.capabilities
            
            logger.info(f"✅ Registered agent: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering agent {agent_id}: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the discovery service"""
        try:
            if agent_id in self.registered_agents:
                del self.registered_agents[agent_id]
                if agent_id in self.agent_capabilities:
                    del self.agent_capabilities[agent_id]
                logger.info(f"🗑️  Unregistered agent: {agent_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error unregistering agent {agent_id}: {e}")
            return False
    
    async def discover_agents(self) -> List[Dict[str, Any]]:
        """Discover all registered agents"""
        agents = []
        for agent_id, agent_info in self.registered_agents.items():
            if agent_info.status == "available":
                agents.append(agent_info.to_dict())
        return agents
    
    async def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific agent"""
        if agent_id in self.registered_agents:
            agent_info = self.registered_agents[agent_id]
            if agent_info.status == "available":
                return agent_info.to_dict()
        return None
    
    async def find_agents_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """Find agents that have a specific capability"""
        matching_agents = []
        for agent_id, agent_info in self.registered_agents.items():
            if agent_info.status == "available" and capability in agent_info.capabilities:
                matching_agents.append(agent_info.to_dict())
        return matching_agents
    
    async def get_agent_capabilities(self, agent_id: str) -> List[str]:
        """Get capabilities of a specific agent"""
        if agent_id in self.agent_capabilities:
            return self.agent_capabilities[agent_id]
        return []
    
    async def check_agent_health(self, agent_id: str) -> bool:
        """Check if an agent is healthy (recent heartbeat)"""
        if agent_id in self.registered_agents:
            agent_info = self.registered_agents[agent_id]
            time_since_heartbeat = datetime.now() - agent_info.last_heartbeat
            return time_since_heartbeat.total_seconds() < self.heartbeat_timeout
        return False
    
    async def _monitor_heartbeats(self):
        """Monitor agent heartbeats and mark unhealthy agents"""
        while self.running:
            try:
                current_time = datetime.now()
                unhealthy_agents = []
                
                for agent_id, agent_info in self.registered_agents.items():
                    time_since_heartbeat = current_time - agent_info.last_heartbeat
                    if time_since_heartbeat.total_seconds() > self.heartbeat_timeout:
                        if agent_info.status == "available":
                            agent_info.status = "unhealthy"
                            unhealthy_agents.append(agent_id)
                            logger.warning(f"⚠️  Agent {agent_id} marked as unhealthy (no heartbeat)")
                
                # Clean up unhealthy agents after extended timeout
                extended_timeout = self.heartbeat_timeout * 3
                for agent_id in list(self.registered_agents.keys()):
                    agent_info = self.registered_agents[agent_id]
                    time_since_heartbeat = current_time - agent_info.last_heartbeat
                    if time_since_heartbeat.total_seconds() > extended_timeout:
                        await self.unregister_agent(agent_id)
                        logger.info(f"🗑️  Removed unhealthy agent: {agent_id}")
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitoring: {e}")
                await asyncio.sleep(5)
    
    async def get_discovery_stats(self) -> Dict[str, Any]:
        """Get discovery service statistics"""
        total_agents = len(self.registered_agents)
        available_agents = len([a for a in self.registered_agents.values() if a.status == "available"])
        unhealthy_agents = len([a for a in self.registered_agents.values() if a.status == "unhealthy"])
        
        return {
            "total_agents": total_agents,
            "available_agents": available_agents,
            "unhealthy_agents": unhealthy_agents,
            "heartbeat_timeout": self.heartbeat_timeout,
            "service_status": "running" if self.running else "stopped"
        }


# Global discovery service instance
discovery_service = AgentDiscoveryService()


async def get_discovery_service() -> AgentDiscoveryService:
    """Get the global discovery service instance"""
    return discovery_service
