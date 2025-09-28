"""
A2A Server for Hospital Agents

This module creates and manages A2A servers for all hospital agents,
exposing them for inter-agent communication using Google ADK.
"""

import asyncio
import logging
from typing import Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .google_adk import A2AServer, AgentDiscovery
from .hospital_agents.frontdesk_agent import frontdesk_agent
from .hospital_agents.queue_agent import queue_agent

logger = logging.getLogger(__name__)


class HospitalA2AServer:
    """
    Hospital A2A Server managing all hospital agents.
    
    Exposes all hospital agents via A2A protocol for inter-agent communication.
    """
    
    def __init__(self, base_port: int = 8001):
        """
        Initialize the Hospital A2A Server.
        
        Args:
            base_port: Base port for agent servers (each agent gets base_port + offset)
        """
        self.base_port = base_port
        self.agents = {
            "frontdesk": frontdesk_agent,
            "queue": queue_agent
        }
        self.servers: Dict[str, A2AServer] = {}
        self.discovery_service = AgentDiscovery()
        self.running = False
        
        logger.info("🏥 Initialized Hospital A2A Server")
    
    async def start(self) -> None:
        """Start all agent servers."""
        if self.running:
            logger.warning("Hospital A2A Server is already running")
            return
        
        self.running = True
        
        # Start each agent server
        for i, (agent_name, agent) in enumerate(self.agents.items()):
            port = self.base_port + i
            
            # Create A2A server for the agent
            server = A2AServer(
                agent=agent,
                host="0.0.0.0",
                port=port,
                agent_card=agent.get_agent_card()
            )
            
            self.servers[agent_name] = server
            
            # Start the agent
            await agent.start()
            
            # Start the server in background
            asyncio.create_task(self._run_server(server, agent_name, port))
            
            logger.info(f"🚀 Started {agent_name} agent on port {port}")
        
        # Register agents with discovery service
        await self._register_agents()
        
        logger.info("✅ All hospital agents started successfully")
    
    async def _run_server(self, server: A2AServer, agent_name: str, port: int) -> None:
        """Run an individual agent server."""
        try:
            await server.start()
        except Exception as e:
            logger.error(f"❌ Failed to start {agent_name} server on port {port}: {e}")
    
    async def _register_agents(self) -> None:
        """Register all agents with the discovery service."""
        for agent_name, agent in self.agents.items():
            try:
                await self.discovery_service.register_agent(agent.get_agent_card())
                logger.info(f"📝 Registered {agent_name} with discovery service")
            except Exception as e:
                logger.error(f"❌ Failed to register {agent_name}: {e}")
    
    async def stop(self) -> None:
        """Stop all agent servers."""
        if not self.running:
            logger.warning("Hospital A2A Server is not running")
            return
        
        self.running = False
        
        # Stop all servers
        for agent_name, server in self.servers.items():
            try:
                await server.stop()
                logger.info(f"🛑 Stopped {agent_name} server")
            except Exception as e:
                logger.error(f"❌ Error stopping {agent_name} server: {e}")
        
        # Stop all agents
        for agent_name, agent in self.agents.items():
            try:
                await agent.stop()
                logger.info(f"🛑 Stopped {agent_name} agent")
            except Exception as e:
                logger.error(f"❌ Error stopping {agent_name} agent: {e}")
        
        # Close discovery service
        await self.discovery_service.close()
        
        self.servers.clear()
        logger.info("🛑 Hospital A2A Server stopped")
    
    def get_agent_urls(self) -> Dict[str, str]:
        """Get URLs for all agent servers."""
        urls = {}
        for i, agent_name in enumerate(self.agents.keys()):
            port = self.base_port + i
            urls[agent_name] = f"http://localhost:{port}"
        return urls
    
    def get_agent_cards(self) -> Dict[str, Dict[str, Any]]:
        """Get agent cards for all agents."""
        cards = {}
        for agent_name, agent in self.agents.items():
            cards[agent_name] = agent.get_agent_card().to_dict()
        return cards
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all agents and servers."""
        status = {
            "running": self.running,
            "agents": {},
            "servers": {},
            "discovery": self.discovery_service.get_registry_stats()
        }
        
        for agent_name, agent in self.agents.items():
            status["agents"][agent_name] = agent.get_status()
        
        for agent_name, server in self.servers.items():
            status["servers"][agent_name] = {
                "running": server.running,
                "host": server.host,
                "port": server.port
            }
        
        return status


# Global instance
hospital_a2a_server = HospitalA2AServer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for A2A server."""
    # Startup
    logger.info("🚀 Starting Hospital A2A Server...")
    await hospital_a2a_server.start()
    
    yield
    
    # Shutdown
    logger.info("🛑 Stopping Hospital A2A Server...")
    await hospital_a2a_server.stop()


def create_a2a_app() -> FastAPI:
    """Create FastAPI app for A2A server management."""
    app = FastAPI(
        title="Hospital A2A Server",
        description="A2A server for hospital agents using Google ADK",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """Root endpoint with server information."""
        return {
            "message": "Hospital A2A Server",
            "description": "A2A server for hospital agents using Google ADK",
            "agents": list(hospital_a2a_server.agents.keys()),
            "status": hospital_a2a_server.get_status()
        }
    
    @app.get("/agents")
    async def get_agents():
        """Get all available agents."""
        return {
            "agents": hospital_a2a_server.get_agent_cards(),
            "urls": hospital_a2a_server.get_agent_urls()
        }
    
    @app.get("/agents/{agent_name}")
    async def get_agent(agent_name: str):
        """Get specific agent information."""
        if agent_name not in hospital_a2a_server.agents:
            return {"error": f"Agent '{agent_name}' not found"}
        
        agent = hospital_a2a_server.agents[agent_name]
        return {
            "agent": agent.get_agent_card().to_dict(),
            "status": agent.get_status(),
            "url": hospital_a2a_server.get_agent_urls()[agent_name]
        }
    
    @app.get("/status")
    async def get_status():
        """Get server status."""
        return hospital_a2a_server.get_status()
    
    @app.get("/discovery")
    async def get_discovery():
        """Get discovery service information."""
        return {
            "discovery_stats": hospital_a2a_server.discovery_service.get_registry_stats(),
            "registered_agents": list(hospital_a2a_server.agents.keys())
        }
    
    return app


# Create the FastAPI app
a2a_app = create_a2a_app()


async def start_a2a_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Start the A2A server."""
    import uvicorn
    
    config = uvicorn.Config(
        a2a_app,
        host=host,
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    logger.info(f"🚀 Starting A2A Server on {host}:{port}")
    await server.serve()


if __name__ == "__main__":
    asyncio.run(start_a2a_server())
