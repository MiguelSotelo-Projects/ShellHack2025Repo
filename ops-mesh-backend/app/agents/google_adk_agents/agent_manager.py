"""
Google ADK Agent Manager

This module manages the lifecycle and coordination of all Google ADK agents
in the hospital operations system.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..protocol.google_adk_config import GoogleADKManager, initialize_google_adk, get_google_adk_manager
from ..protocol.agent_protocol import AgentProtocol, AgentStatus
from .frontdesk_agent import GoogleADKFrontDeskAgent
from .orchestrator_agent import GoogleADKOrchestratorAgent


class GoogleADKAgentManager:
    """Manages Google ADK agents lifecycle and coordination."""
    
    def __init__(self, project_id: str, region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.logger = logging.getLogger("agent_manager")
        
        # Google ADK manager
        self.google_adk_manager: Optional[GoogleADKManager] = None
        
        # Agent registry
        self.agents: Dict[str, AgentProtocol] = {}
        self.agent_status: Dict[str, AgentStatus] = {}
        
        # System state
        self.running = False
        self.startup_time: Optional[datetime] = None
        
        # Agent configurations
        self.agent_configs = {
            "orchestrator": {
                "class": GoogleADKOrchestratorAgent,
                "required": True,
                "startup_priority": 1
            },
            "frontdesk": {
                "class": GoogleADKFrontDeskAgent,
                "required": True,
                "startup_priority": 2
            },
            # Additional agents can be added here
            # "scheduling": {
            #     "class": GoogleADKSchedulingAgent,
            #     "required": True,
            #     "startup_priority": 3
            # },
            # "insurance": {
            #     "class": GoogleADKInsuranceAgent,
            #     "required": True,
            #     "startup_priority": 4
            # },
            # "hospital": {
            #     "class": GoogleADKHospitalAgent,
            #     "required": True,
            #     "startup_priority": 5
            # },
            # "queue": {
            #     "class": GoogleADKQueueAgent,
            #     "required": True,
            #     "startup_priority": 6
            # },
            # "staff": {
            #     "class": GoogleADKStaffAgent,
            #     "required": True,
            #     "startup_priority": 7
            # }
        }
    
    async def initialize(self) -> bool:
        """Initialize the agent manager and Google ADK."""
        try:
            self.logger.info("Initializing Google ADK Agent Manager...")
            
            # Initialize Google ADK
            self.google_adk_manager = await initialize_google_adk(
                project_id=self.project_id,
                region=self.region
            )
            
            if not self.google_adk_manager.is_initialized():
                self.logger.error("Failed to initialize Google ADK")
                return False
            
            self.logger.info("Google ADK Agent Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agent manager: {e}")
            return False
    
    async def start_all_agents(self) -> bool:
        """Start all configured agents."""
        try:
            self.logger.info("Starting all agents...")
            self.running = True
            self.startup_time = datetime.utcnow()
            
            # Sort agents by startup priority
            sorted_agents = sorted(
                self.agent_configs.items(),
                key=lambda x: x[1]["startup_priority"]
            )
            
            # Start agents in priority order
            for agent_id, config in sorted_agents:
                try:
                    await self._start_agent(agent_id, config)
                except Exception as e:
                    self.logger.error(f"Failed to start agent {agent_id}: {e}")
                    if config["required"]:
                        self.logger.error(f"Required agent {agent_id} failed to start. Aborting.")
                        await self.stop_all_agents()
                        return False
            
            self.logger.info(f"All agents started successfully. Total agents: {len(self.agents)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start agents: {e}")
            await self.stop_all_agents()
            return False
    
    async def _start_agent(self, agent_id: str, config: Dict[str, Any]):
        """Start a specific agent."""
        try:
            self.logger.info(f"Starting agent: {agent_id}")
            
            # Create agent instance
            agent_class = config["class"]
            agent = agent_class(
                project_id=self.project_id,
                region=self.region
            )
            
            # Start the agent
            await agent.start()
            
            # Register agent
            self.agents[agent_id] = agent
            self.agent_status[agent_id] = AgentStatus.ONLINE
            
            self.logger.info(f"Agent {agent_id} started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start agent {agent_id}: {e}")
            raise
    
    async def stop_all_agents(self):
        """Stop all running agents."""
        try:
            self.logger.info("Stopping all agents...")
            self.running = False
            
            # Stop agents in reverse priority order
            sorted_agents = sorted(
                self.agent_configs.items(),
                key=lambda x: x[1]["startup_priority"],
                reverse=True
            )
            
            for agent_id, _ in sorted_agents:
                if agent_id in self.agents:
                    try:
                        await self._stop_agent(agent_id)
                    except Exception as e:
                        self.logger.error(f"Error stopping agent {agent_id}: {e}")
            
            # Shutdown Google ADK
            if self.google_adk_manager:
                await self.google_adk_manager.shutdown()
            
            self.logger.info("All agents stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping agents: {e}")
    
    async def _stop_agent(self, agent_id: str):
        """Stop a specific agent."""
        try:
            if agent_id in self.agents:
                self.logger.info(f"Stopping agent: {agent_id}")
                
                agent = self.agents[agent_id]
                await agent.stop()
                
                del self.agents[agent_id]
                self.agent_status[agent_id] = AgentStatus.OFFLINE
                
                self.logger.info(f"Agent {agent_id} stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to stop agent {agent_id}: {e}")
            raise
    
    async def restart_agent(self, agent_id: str) -> bool:
        """Restart a specific agent."""
        try:
            self.logger.info(f"Restarting agent: {agent_id}")
            
            if agent_id not in self.agent_configs:
                self.logger.error(f"Unknown agent: {agent_id}")
                return False
            
            # Stop agent if running
            if agent_id in self.agents:
                await self._stop_agent(agent_id)
            
            # Start agent
            config = self.agent_configs[agent_id]
            await self._start_agent(agent_id, config)
            
            self.logger.info(f"Agent {agent_id} restarted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restart agent {agent_id}: {e}")
            return False
    
    def get_agent_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get agent status information."""
        if agent_id:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                return {
                    "agent_id": agent_id,
                    "status": self.agent_status.get(agent_id, AgentStatus.OFFLINE).value,
                    "agent_info": agent.get_status(),
                    "running": agent_id in self.agents
                }
            else:
                return {"error": f"Agent {agent_id} not found"}
        else:
            return {
                "total_agents": len(self.agents),
                "running_agents": len([a for a in self.agents.values() if a.status == AgentStatus.ONLINE]),
                "agent_statuses": {
                    agent_id: status.value for agent_id, status in self.agent_status.items()
                },
                "system_running": self.running,
                "startup_time": self.startup_time.isoformat() if self.startup_time else None,
                "uptime_minutes": (datetime.utcnow() - self.startup_time).total_seconds() / 60 if self.startup_time else 0
            }
    
    def get_agent(self, agent_id: str) -> Optional[AgentProtocol]:
        """Get a specific agent instance."""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all agent IDs."""
        return list(self.agents.keys())
    
    def is_agent_running(self, agent_id: str) -> bool:
        """Check if an agent is running."""
        return agent_id in self.agents and self.agent_status.get(agent_id) == AgentStatus.ONLINE
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents."""
        health_results = {}
        
        for agent_id, agent in self.agents.items():
            try:
                # Get agent status
                status = agent.get_status()
                health_results[agent_id] = {
                    "status": "healthy",
                    "agent_status": status.get("status", "unknown"),
                    "last_check": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                health_results[agent_id] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
        
        return {
            "health_check_results": health_results,
            "overall_health": "healthy" if all(
                result["status"] == "healthy" for result in health_results.values()
            ) else "degraded",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def send_message_to_agent(
        self,
        agent_id: str,
        message_type: str,
        payload: Dict[str, Any],
        priority: str = "normal"
    ) -> bool:
        """Send a message to a specific agent."""
        try:
            if agent_id not in self.agents:
                self.logger.error(f"Agent {agent_id} not found")
                return False
            
            agent = self.agents[agent_id]
            
            # This would need to be implemented based on the agent protocol
            # For now, we'll just log the attempt
            self.logger.info(f"Sending message to agent {agent_id}: {message_type}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message to agent {agent_id}: {e}")
            return False
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        return {
            "total_agents": len(self.agents),
            "running_agents": len([a for a in self.agents.values() if a.status == AgentStatus.ONLINE]),
            "system_running": self.running,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "uptime_minutes": (datetime.utcnow() - self.startup_time).total_seconds() / 60 if self.startup_time else 0,
            "google_adk_initialized": self.google_adk_manager.is_initialized() if self.google_adk_manager else False,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global agent manager instance
_agent_manager: Optional[GoogleADKAgentManager] = None


async def initialize_agent_manager(
    project_id: str,
    region: str = "us-central1"
) -> GoogleADKAgentManager:
    """Initialize the global agent manager."""
    global _agent_manager
    
    if _agent_manager is None:
        _agent_manager = GoogleADKAgentManager(project_id, region)
        await _agent_manager.initialize()
    
    return _agent_manager


def get_agent_manager() -> GoogleADKAgentManager:
    """Get the global agent manager."""
    if _agent_manager is None:
        raise RuntimeError("Agent manager not initialized. Call initialize_agent_manager() first.")
    
    return _agent_manager


async def start_agent_system(project_id: str, region: str = "us-central1") -> bool:
    """Start the complete agent system."""
    try:
        # Initialize agent manager
        agent_manager = await initialize_agent_manager(project_id, region)
        
        # Start all agents
        success = await agent_manager.start_all_agents()
        
        if success:
            print("🎉 Google ADK Agent System started successfully!")
            print(f"📊 System Status: {agent_manager.get_system_metrics()}")
        else:
            print("❌ Failed to start agent system")
        
        return success
        
    except Exception as e:
        print(f"❌ Error starting agent system: {e}")
        return False


async def stop_agent_system():
    """Stop the complete agent system."""
    global _agent_manager
    
    if _agent_manager:
        await _agent_manager.stop_all_agents()
        _agent_manager = None
        print("🛑 Agent system stopped")


if __name__ == "__main__":
    # Example usage
    import os
    
    async def main():
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
        
        # Start the agent system
        success = await start_agent_system(project_id)
        
        if success:
            try:
                # Keep the system running
                print("🔄 Agent system is running. Press Ctrl+C to stop.")
                while True:
                    await asyncio.sleep(10)
                    
                    # Print status every 10 seconds
                    agent_manager = get_agent_manager()
                    metrics = agent_manager.get_system_metrics()
                    print(f"📊 Status: {metrics['running_agents']}/{metrics['total_agents']} agents running")
                    
            except KeyboardInterrupt:
                print("\n🛑 Shutting down agent system...")
                await stop_agent_system()
        else:
            print("❌ Failed to start agent system")
    
    # Run the main function
    asyncio.run(main())
