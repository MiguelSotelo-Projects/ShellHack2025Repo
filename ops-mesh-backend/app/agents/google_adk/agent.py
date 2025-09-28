"""
Google ADK Agent Implementation

This module implements the core Agent class following Google ADK specifications.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
from abc import ABC, abstractmethod

from .tools import BaseTool, ToolContext
from .protocol import AgentCard, MessageType, TaskRequest, TaskResponse

logger = logging.getLogger(__name__)


class Agent:
    """
    Google ADK Agent implementation following official specifications.
    
    This class represents an intelligent agent that can process tasks,
    use tools, and communicate with other agents via A2A protocol.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        model: str = "gemini-1.5-flash",
        instruction: str = "",
        tools: Optional[List[BaseTool]] = None,
        agent_card: Optional[AgentCard] = None,
        **kwargs
    ):
        """
        Initialize an ADK Agent.
        
        Args:
            name: Unique name for the agent
            description: Human-readable description of the agent's purpose
            model: LLM model to use (default: gemini-1.5-flash)
            instruction: System instruction for the agent
            tools: List of tools available to the agent
            agent_card: Agent card defining capabilities and metadata
            **kwargs: Additional configuration parameters
        """
        self.name = name
        self.description = description
        self.model = model
        self.instruction = instruction
        self.tools = tools or []
        self.agent_card = agent_card or self._create_default_agent_card()
        self.running = False
        self.task_history: List[Dict[str, Any]] = []
        self.config = kwargs
        
        # Initialize tool context
        self.tool_context = ToolContext(agent=self)
        
        logger.info(f"Initialized ADK Agent: {self.name}")
    
    def _create_default_agent_card(self) -> AgentCard:
        """Create a default agent card for this agent."""
        return AgentCard(
            name=self.name,
            description=self.description,
            version="1.0.0",
            capabilities={
                "streaming": True,
                "functions": len(self.tools) > 0
            },
            default_input_modes=["text/plain"],
            default_output_modes=["text/plain", "application/json"],
            skills=[
                {
                    "id": f"{self.name.lower()}_task",
                    "name": f"{self.name} Task",
                    "description": self.description,
                    "tags": ["general"],
                    "examples": [f"Execute a task using {self.name}"]
                }
            ]
        )
    
    async def start(self) -> None:
        """Start the agent and initialize resources."""
        if self.running:
            logger.warning(f"Agent {self.name} is already running")
            return
        
        self.running = True
        
        # Initialize tools
        for tool in self.tools:
            if hasattr(tool, 'initialize'):
                await tool.initialize()
        
        logger.info(f"✅ ADK Agent {self.name} started successfully")
    
    async def stop(self) -> None:
        """Stop the agent and cleanup resources."""
        if not self.running:
            logger.warning(f"Agent {self.name} is not running")
            return
        
        self.running = False
        
        # Cleanup tools
        for tool in self.tools:
            if hasattr(tool, 'cleanup'):
                await tool.cleanup()
        
        logger.info(f"🛑 ADK Agent {self.name} stopped")
    
    async def process_task(self, task_request: TaskRequest) -> TaskResponse:
        """
        Process a task request and return a response.
        
        Args:
            task_request: The task to process
            
        Returns:
            TaskResponse with the result
        """
        if not self.running:
            return TaskResponse(
                task_id=task_request.task_id,
                status="error",
                result={"error": "Agent is not running"},
                timestamp=datetime.utcnow()
            )
        
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Agent {self.name} processing task: {task_request.task_id}")
            
            # Record task in history
            self.task_history.append({
                "task_id": task_request.task_id,
                "timestamp": start_time,
                "status": "processing",
                "parameters": task_request.parameters
            })
            
            # Process the task based on type
            if task_request.task_type == "tool_execution":
                result = await self._execute_tool_task(task_request)
            elif task_request.task_type == "conversation":
                result = await self._process_conversation_task(task_request)
            else:
                result = await self._process_general_task(task_request)
            
            # Create successful response
            response = TaskResponse(
                task_id=task_request.task_id,
                status="completed",
                result=result,
                timestamp=datetime.utcnow(),
                processing_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
            # Update task history
            self.task_history[-1]["status"] = "completed"
            self.task_history[-1]["result"] = result
            
            logger.info(f"✅ Agent {self.name} completed task: {task_request.task_id}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Agent {self.name} failed task {task_request.task_id}: {e}")
            
            # Create error response
            response = TaskResponse(
                task_id=task_request.task_id,
                status="error",
                result={"error": str(e)},
                timestamp=datetime.utcnow(),
                processing_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
            # Update task history
            self.task_history[-1]["status"] = "error"
            self.task_history[-1]["error"] = str(e)
            
            return response
    
    async def _execute_tool_task(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Execute a tool-based task."""
        tool_name = task_request.parameters.get("tool_name")
        tool_parameters = task_request.parameters.get("parameters", {})
        
        # Find the tool
        tool = None
        for t in self.tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # Execute the tool
        result = await tool.execute(tool_parameters, self.tool_context)
        return {"tool_result": result}
    
    async def _process_conversation_task(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Process a conversation-based task."""
        message = task_request.parameters.get("message", "")
        
        # Simple conversation processing
        # In a real implementation, this would use the specified LLM model
        response = f"Agent {self.name} processed message: {message}"
        
        return {"conversation_response": response}
    
    async def _process_general_task(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Process a general task."""
        # Default task processing
        return {
            "task_type": task_request.task_type,
            "parameters": task_request.parameters,
            "agent": self.name,
            "status": "processed"
        }
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool with this agent."""
        self.tools.append(tool)
        logger.info(f"Registered tool '{tool.name}' with agent '{self.name}'")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent."""
        return {
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "running": self.running,
            "tools_count": len(self.tools),
            "task_history_count": len(self.task_history),
            "capabilities": self.agent_card.capabilities,
            "last_activity": self.task_history[-1]["timestamp"] if self.task_history else None
        }
    
    def get_agent_card(self) -> AgentCard:
        """Get the agent card for this agent."""
        return self.agent_card
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "instruction": self.instruction,
            "tools": [tool.to_dict() for tool in self.tools],
            "agent_card": self.agent_card.to_dict(),
            "status": self.get_status()
        }
