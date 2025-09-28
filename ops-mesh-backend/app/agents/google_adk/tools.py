"""
Google ADK Tools Implementation

This module implements the BaseTool class and ToolContext following Google ADK specifications.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


class ToolContext:
    """
    Context object passed to tools during execution.
    
    Provides access to agent information and shared resources.
    """
    
    def __init__(self, agent: 'Agent'):
        """
        Initialize tool context.
        
        Args:
            agent: The agent that owns this context
        """
        self.agent = agent
        self.shared_data: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the owning agent."""
        return {
            "name": self.agent.name,
            "description": self.agent.description,
            "model": self.agent.model
        }
    
    def set_shared_data(self, key: str, value: Any) -> None:
        """Set shared data that can be accessed by other tools."""
        self.shared_data[key] = value
    
    def get_shared_data(self, key: str, default: Any = None) -> Any:
        """Get shared data."""
        return self.shared_data.get(key, default)
    
    def log_execution(self, tool_name: str, parameters: Dict[str, Any], result: Any) -> None:
        """Log tool execution for debugging and monitoring."""
        self.execution_history.append({
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "timestamp": datetime.utcnow()
        })


class BaseTool(ABC):
    """
    Base class for ADK tools following Google ADK specifications.
    
    Tools are the building blocks that agents use to perform specific tasks.
    Each tool should inherit from this class and implement the execute method.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters_schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize a tool.
        
        Args:
            name: Unique name for the tool
            description: Human-readable description of what the tool does
            parameters_schema: JSON schema defining the tool's parameters
            **kwargs: Additional tool configuration
        """
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema or self._get_default_schema()
        self.config = kwargs
        self.execution_count = 0
        self.last_execution: Optional[datetime] = None
        
        logger.info(f"Initialized ADK Tool: {self.name}")
    
    def _get_default_schema(self) -> Dict[str, Any]:
        """Get default parameter schema for the tool."""
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    @abstractmethod
    async def execute(
        self, 
        parameters: Dict[str, Any], 
        context: ToolContext
    ) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.
        
        Args:
            parameters: Parameters for tool execution
            context: Tool context providing access to agent and shared resources
            
        Returns:
            Dictionary containing the tool execution result
            
        Raises:
            Exception: If tool execution fails
        """
        pass
    
    async def initialize(self) -> None:
        """Initialize the tool (called when agent starts)."""
        logger.debug(f"Initializing tool: {self.name}")
    
    async def cleanup(self) -> None:
        """Cleanup the tool (called when agent stops)."""
        logger.debug(f"Cleaning up tool: {self.name}")
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters against the tool's schema.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        # Simple validation - in a real implementation, this would use JSON schema validation
        required_params = self.parameters_schema.get("required", [])
        
        for param in required_params:
            if param not in parameters:
                logger.error(f"Missing required parameter '{param}' for tool '{self.name}'")
                return False
        
        return True
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's parameter schema."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tool execution statistics."""
        return {
            "name": self.name,
            "description": self.description,
            "execution_count": self.execution_count,
            "last_execution": self.last_execution,
            "schema": self.parameters_schema
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.parameters_schema,
            "stats": self.get_stats()
        }


class FunctionTool(BaseTool):
    """
    Tool that wraps a Python function.
    
    This is a convenience class for creating tools from existing functions.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        func: callable,
        parameters_schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize a function tool.
        
        Args:
            name: Tool name
            description: Tool description
            func: Python function to wrap
            parameters_schema: Parameter schema
            **kwargs: Additional configuration
        """
        super().__init__(name, description, parameters_schema, **kwargs)
        self.func = func
    
    async def execute(
        self, 
        parameters: Dict[str, Any], 
        context: ToolContext
    ) -> Dict[str, Any]:
        """Execute the wrapped function."""
        if not self.validate_parameters(parameters):
            raise ValueError(f"Invalid parameters for tool '{self.name}'")
        
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(self.func):
                result = await self.func(**parameters)
            else:
                result = self.func(**parameters)
            
            # Update execution stats
            self.execution_count += 1
            self.last_execution = datetime.utcnow()
            
            # Log execution
            context.log_execution(self.name, parameters, result)
            
            return {"result": result}
            
        except Exception as e:
            logger.error(f"Tool '{self.name}' execution failed: {e}")
            raise


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    parameters_schema: Optional[Dict[str, Any]] = None,
    **kwargs
):
    """
    Decorator for creating tools from functions.
    
    Usage:
        @tool(name="my_tool", description="Does something useful")
        async def my_function(param1: str, param2: int) -> str:
            return f"Processed {param1} with {param2}"
    """
    def decorator(func: callable) -> FunctionTool:
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or f"Tool: {tool_name}"
        
        return FunctionTool(
            name=tool_name,
            description=tool_description,
            func=func,
            parameters_schema=parameters_schema,
            **kwargs
        )
    
    return decorator
