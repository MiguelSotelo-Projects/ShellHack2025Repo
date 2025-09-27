"""
Agent Manager

Manages and coordinates all hospital agents for agent-to-agent communication.
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Any, List
from .specialized.frontdesk_agent import FrontDeskAgent
from .specialized.queue_agent import QueueAgent
from .specialized.appointment_agent import AppointmentAgent
from .specialized.notification_agent import NotificationAgent
from .orchestrator_agent import OrchestratorAgent

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages all hospital agents and their communication."""
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id
        self.agents = {}
        self.running = False
        
        # Initialize all agents
        self.agents = {
            "frontdesk": FrontDeskAgent(project_id),
            "queue": QueueAgent(project_id),
            "appointment": AppointmentAgent(project_id),
            "notification": NotificationAgent(project_id),
            "orchestrator": OrchestratorAgent(project_id)
        }
    
    async def initialize_all_agents(self):
        """Initialize all agents."""
        logger.info("Initializing all agents...")
        
        for agent_name, agent in self.agents.items():
            try:
                await agent.initialize()
                logger.info(f"Initialized {agent_name} agent")
            except Exception as e:
                logger.error(f"Failed to initialize {agent_name} agent: {e}")
                raise
    
    async def start_all_agents(self):
        """Start all agents."""
        logger.info("Starting all agents...")
        
        # Start all agents concurrently
        tasks = []
        for agent_name, agent in self.agents.items():
            task = asyncio.create_task(agent.start())
            tasks.append(task)
            logger.info(f"Started {agent_name} agent")
        
        self.running = True
        
        # Wait for all agents to complete
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping agents...")
            await self.stop_all_agents()
    
    async def stop_all_agents(self):
        """Stop all agents."""
        logger.info("Stopping all agents...")
        
        self.running = False
        
        for agent_name, agent in self.agents.items():
            try:
                await agent.stop()
                logger.info(f"Stopped {agent_name} agent")
            except Exception as e:
                logger.error(f"Error stopping {agent_name} agent: {e}")
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        status = {}
        
        for agent_name, agent in self.agents.items():
            try:
                # Check if agent is running
                status[agent_name] = {
                    "running": hasattr(agent, 'protocol') and agent.protocol.running,
                    "agent_id": agent.agent_id if hasattr(agent, 'agent_id') else None
                }
            except Exception as e:
                status[agent_name] = {
                    "running": False,
                    "error": str(e)
                }
        
        return status
    
    async def send_message_to_agent(self, target_agent: str, message_type: str, 
                                   payload: Dict[str, Any]) -> bool:
        """Send a message to a specific agent."""
        if target_agent not in self.agents:
            logger.error(f"Agent {target_agent} not found")
            return False
        
        try:
            agent = self.agents[target_agent]
            if hasattr(agent, 'protocol'):
                # This would need to be implemented based on the specific agent protocol
                logger.info(f"Sent message to {target_agent}: {payload}")
                return True
            else:
                logger.error(f"Agent {target_agent} has no protocol")
                return False
        except Exception as e:
            logger.error(f"Error sending message to {target_agent}: {e}")
            return False
    
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.stop_all_agents())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main function to run the agent manager."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting Ops Mesh Agent Manager...")
    
    # Get project ID from environment
    import os
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    if not project_id:
        logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
        return
    
    # Create and start agent manager
    manager = AgentManager(project_id)
    manager.setup_signal_handlers()
    
    try:
        await manager.initialize_all_agents()
        await manager.start_all_agents()
    except Exception as e:
        logger.error(f"Error running agent manager: {e}")
        await manager.stop_all_agents()


if __name__ == "__main__":
    asyncio.run(main())
