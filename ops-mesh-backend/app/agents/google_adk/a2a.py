"""
A2A Server and Client Implementation

This module implements the A2A server for exposing agents and the RemoteA2aAgent
for consuming remote agents following Google ADK specifications.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from datetime import datetime
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .agent import Agent
from .protocol import AgentCard, TaskRequest, TaskResponse, MessageType, TaskStatus
from .discovery import AgentDiscovery

logger = logging.getLogger(__name__)


class A2AServer:
    """
    A2A Server for exposing ADK agents over HTTP.
    
    Follows Google ADK specifications for agent exposure and communication.
    """
    
    def __init__(
        self,
        agent: Agent,
        host: str = "0.0.0.0",
        port: int = 8000,
        agent_card: Optional[AgentCard] = None,
        **kwargs
    ):
        """
        Initialize A2A server.
        
        Args:
            agent: The ADK agent to expose
            host: Host to bind to
            port: Port to bind to
            agent_card: Custom agent card (uses agent's default if None)
            **kwargs: Additional server configuration
        """
        self.agent = agent
        self.host = host
        self.port = port
        self.agent_card = agent_card or agent.get_agent_card()
        self.app = FastAPI(title=f"A2A Server - {agent.name}")
        self.running = False
        self.config = kwargs
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"Initialized A2A Server for agent: {agent.name}")
    
    def _setup_routes(self) -> None:
        """Setup FastAPI routes for A2A protocol."""
        
        @self.app.get("/.well-known/agent-card")
        async def get_agent_card():
            """Get the agent card."""
            return self.agent_card.to_dict()
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "agent": self.agent.name,
                "running": self.agent.running,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @self.app.get("/status")
        async def get_status():
            """Get agent status."""
            return self.agent.get_status()
        
        @self.app.post("/a2a/task")
        async def execute_task(request: Request):
            """Execute a task on the agent."""
            try:
                body = await request.json()
                task_request = TaskRequest(**body)
                
                # Process the task
                response = await self.agent.process_task(task_request)
                
                return response.dict()
                
            except Exception as e:
                logger.error(f"Task execution failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/a2a/stream")
        async def stream_task(request: Request):
            """Stream task execution (for long-running tasks)."""
            try:
                body = await request.json()
                task_request = TaskRequest(**body)
                
                async def generate():
                    # Start task processing
                    yield f"data: {json.dumps({'type': 'start', 'task_id': task_request.task_id})}\n\n"
                    
                    # Process task (simplified streaming)
                    response = await self.agent.process_task(task_request)
                    
                    # Send result
                    yield f"data: {json.dumps({'type': 'result', 'data': response.dict()})}\n\n"
                    yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
                return StreamingResponse(
                    generate(),
                    media_type="text/plain",
                    headers={"Cache-Control": "no-cache"}
                )
                
            except Exception as e:
                logger.error(f"Streaming task failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tools")
        async def get_tools():
            """Get available tools."""
            return {
                "tools": [tool.to_dict() for tool in self.agent.tools]
            }
        
        @self.app.get("/metrics")
        async def get_metrics():
            """Get agent metrics."""
            return {
                "agent": self.agent.get_status(),
                "server": {
                    "host": self.host,
                    "port": self.port,
                    "running": self.running
                }
            }
    
    async def start(self) -> None:
        """Start the A2A server."""
        if self.running:
            logger.warning("A2A server is already running")
            return
        
        # Start the agent
        await self.agent.start()
        
        # Start the server
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        self.running = True
        logger.info(f"🚀 A2A Server started on {self.host}:{self.port}")
        
        # Run the server
        await server.serve()
    
    async def stop(self) -> None:
        """Stop the A2A server."""
        if not self.running:
            logger.warning("A2A server is not running")
            return
        
        self.running = False
        
        # Stop the agent
        await self.agent.stop()
        
        logger.info("🛑 A2A Server stopped")


class RemoteA2aAgent:
    """
    Remote A2A Agent client for consuming remote agents.
    
    Follows Google ADK specifications for remote agent communication.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        agent_card_url: str,
        timeout: float = 30.0,
        httpx_client: Optional[httpx.AsyncClient] = None,
        **kwargs
    ):
        """
        Initialize remote A2A agent.
        
        Args:
            name: Name of the remote agent
            description: Description of the remote agent
            agent_card_url: URL to the agent card
            timeout: Request timeout in seconds
            httpx_client: Custom HTTP client
            **kwargs: Additional configuration
        """
        self.name = name
        self.description = description
        self.agent_card_url = agent_card_url
        self.timeout = timeout
        self.httpx_client = httpx_client or httpx.AsyncClient(timeout=timeout)
        self.agent_card: Optional[AgentCard] = None
        self.config = kwargs
        
        logger.info(f"Initialized Remote A2A Agent: {name}")
    
    async def initialize(self) -> None:
        """Initialize the remote agent by fetching its agent card."""
        try:
            response = await self.httpx_client.get(self.agent_card_url)
            response.raise_for_status()
            
            card_data = response.json()
            self.agent_card = AgentCard.from_dict(card_data)
            
            logger.info(f"✅ Fetched agent card for {self.name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch agent card for {self.name}: {e}")
            raise
    
    async def execute_task(
        self,
        task_type: str,
        parameters: Dict[str, Any],
        **kwargs
    ) -> TaskResponse:
        """
        Execute a task on the remote agent.
        
        Args:
            task_type: Type of task to execute
            parameters: Task parameters
            **kwargs: Additional task options
            
        Returns:
            TaskResponse with the result
        """
        if not self.agent_card:
            await self.initialize()
        
        # Create task request
        task_request = TaskRequest(
            task_type=task_type,
            parameters=parameters,
            from_agent="local_client",
            to_agent=self.name,
            **kwargs
        )
        
        try:
            # Send task request
            base_url = self.agent_card_url.replace("/.well-known/agent-card", "")
            response = await self.httpx_client.post(
                f"{base_url}/a2a/task",
                json=task_request.dict()
            )
            response.raise_for_status()
            
            # Parse response
            result_data = response.json()
            return TaskResponse(**result_data)
            
        except Exception as e:
            logger.error(f"❌ Task execution failed for {self.name}: {e}")
            return TaskResponse(
                task_id=task_request.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def stream_task(
        self,
        task_type: str,
        parameters: Dict[str, Any],
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream task execution from the remote agent.
        
        Args:
            task_type: Type of task to execute
            parameters: Task parameters
            **kwargs: Additional task options
            
        Yields:
            Streaming response chunks
        """
        if not self.agent_card:
            await self.initialize()
        
        # Create task request
        task_request = TaskRequest(
            task_type=task_type,
            parameters=parameters,
            from_agent="local_client",
            to_agent=self.name,
            **kwargs
        )
        
        try:
            # Send streaming request
            base_url = self.agent_card_url.replace("/.well-known/agent-card", "")
            async with self.httpx_client.stream(
                "POST",
                f"{base_url}/a2a/stream",
                json=task_request.dict()
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"❌ Streaming task failed for {self.name}: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the remote agent."""
        try:
            base_url = self.agent_card_url.replace("/.well-known/agent-card", "")
            response = await self.httpx_client.get(f"{base_url}/status")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"❌ Failed to get status for {self.name}: {e}")
            return {"error": str(e)}
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from the remote agent."""
        try:
            base_url = self.agent_card_url.replace("/.well-known/agent-card", "")
            response = await self.httpx_client.get(f"{base_url}/tools")
            response.raise_for_status()
            
            data = response.json()
            return data.get("tools", [])
            
        except Exception as e:
            logger.error(f"❌ Failed to get tools for {self.name}: {e}")
            return []
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.httpx_client.aclose()
    
    def __repr__(self) -> str:
        return f"RemoteA2aAgent(name='{self.name}', url='{self.agent_card_url}')"


class A2AClient:
    """
    A2A Client for managing multiple remote agents.
    
    Provides discovery, connection management, and load balancing.
    """
    
    def __init__(self, discovery_service: Optional[AgentDiscovery] = None):
        """
        Initialize A2A client.
        
        Args:
            discovery_service: Agent discovery service
        """
        self.discovery_service = discovery_service or AgentDiscovery()
        self.remote_agents: Dict[str, RemoteA2aAgent] = {}
        self.agent_registry: Dict[str, AgentCard] = {}
    
    async def discover_agents(self, query: Optional[str] = None) -> List[AgentCard]:
        """Discover available agents."""
        return await self.discovery_service.discover_agents(query)
    
    async def connect_agent(self, agent_card: AgentCard) -> RemoteA2aAgent:
        """Connect to a remote agent."""
        agent_name = agent_card.name
        
        if agent_name in self.remote_agents:
            return self.remote_agents[agent_name]
        
        # Create remote agent
        agent_card_url = f"{agent_card.url}/.well-known/agent-card"
        remote_agent = RemoteA2aAgent(
            name=agent_name,
            description=agent_card.description,
            agent_card_url=agent_card_url
        )
        
        # Initialize and store
        await remote_agent.initialize()
        self.remote_agents[agent_name] = remote_agent
        self.agent_registry[agent_name] = agent_card
        
        logger.info(f"✅ Connected to remote agent: {agent_name}")
        return remote_agent
    
    async def disconnect_agent(self, agent_name: str) -> None:
        """Disconnect from a remote agent."""
        if agent_name in self.remote_agents:
            await self.remote_agents[agent_name].close()
            del self.remote_agents[agent_name]
            del self.agent_registry[agent_name]
            logger.info(f"🔌 Disconnected from agent: {agent_name}")
    
    async def execute_task_on_agent(
        self,
        agent_name: str,
        task_type: str,
        parameters: Dict[str, Any],
        **kwargs
    ) -> TaskResponse:
        """Execute a task on a specific remote agent."""
        if agent_name not in self.remote_agents:
            raise ValueError(f"Agent '{agent_name}' not connected")
        
        return await self.remote_agents[agent_name].execute_task(
            task_type, parameters, **kwargs
        )
    
    async def close_all(self) -> None:
        """Close all remote agent connections."""
        for agent in self.remote_agents.values():
            await agent.close()
        
        self.remote_agents.clear()
        self.agent_registry.clear()
        
        logger.info("🔌 Closed all remote agent connections")
