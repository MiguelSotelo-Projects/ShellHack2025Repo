"""
Vertex AI Integration for Google ADK Agents

This module integrates Google Cloud Vertex AI with our Google ADK implementation,
providing real AI capabilities for the hospital agents.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part
    from google.cloud import aiplatform
    from google.oauth2 import service_account
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    logging.warning("Vertex AI not available. Install google-cloud-aiplatform to enable.")

logger = logging.getLogger(__name__)


class VertexAIConfig:
    """Configuration for Vertex AI integration."""
    
    def __init__(self, api_key: str, project_id: str = "shellhacks2025", location: str = "us-central1"):
        """
        Initialize Vertex AI configuration.
        
        Args:
            api_key: Google Cloud API key
            project_id: Google Cloud project ID
            location: Google Cloud region
        """
        self.api_key = api_key
        self.project_id = project_id
        self.location = location
        self.initialized = False
        
        # Set up environment variables
        self._create_temp_credentials()
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        
    def _create_temp_credentials(self) -> None:
        """Set up API key for Vertex AI."""
        # For demo purposes, we'll set the API key as an environment variable
        # In production, you'd want to use proper service account credentials
        os.environ["GOOGLE_API_KEY"] = self.api_key
    
    def initialize(self) -> bool:
        """Initialize Vertex AI."""
        if not VERTEX_AI_AVAILABLE:
            logger.error("❌ Vertex AI not available. Please install google-cloud-aiplatform")
            return False
        
        try:
            # Initialize Vertex AI
            vertexai.init(project=self.project_id, location=self.location)
            aiplatform.init(project=self.project_id, location=self.location)
            
            self.initialized = True
            logger.info(f"✅ Vertex AI initialized for project: {self.project_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vertex AI: {e}")
            return False


class VertexAIAgent:
    """
    Vertex AI-powered agent that integrates with Google ADK.
    
    This class provides AI capabilities using Vertex AI's generative models
    while maintaining compatibility with the Google ADK framework.
    """
    
    def __init__(self, config: VertexAIConfig, model_name: str = "gemini-1.5-flash"):
        """
        Initialize Vertex AI agent.
        
        Args:
            config: Vertex AI configuration
            model_name: Name of the generative model to use
        """
        self.config = config
        self.model_name = model_name
        self.model = None
        self.initialized = False
        
        if not config.initialized:
            if not config.initialize():
                logger.error("❌ Failed to initialize Vertex AI configuration")
                return
        
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the generative model."""
        if not VERTEX_AI_AVAILABLE:
            logger.error("❌ Vertex AI not available")
            return
        
        try:
            self.model = GenerativeModel(self.model_name)
            self.initialized = True
            logger.info(f"✅ Vertex AI model initialized: {self.model_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vertex AI model: {e}")
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using Vertex AI.
        
        Args:
            prompt: Input prompt for the model
            context: Additional context for the model
            tools: Available tools for the model to use
            
        Returns:
            Generated response with metadata
        """
        if not self.initialized:
            return {
                "success": False,
                "error": "Vertex AI agent not initialized",
                "response": "I'm sorry, but I'm not properly initialized. Please check the configuration."
            }
        
        try:
            # Build the full prompt with context and tools
            full_prompt = self._build_prompt(prompt, context, tools)
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            # Parse the response
            result = {
                "success": True,
                "response": response.text,
                "model": self.model_name,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "candidates": len(response.candidates) if response.candidates else 0,
                    "safety_ratings": len(response.safety_ratings) if response.safety_ratings else 0
                }
            }
            
            # Add tool calls if any
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        result["tool_calls"] = [part.function_call]
            
            logger.info(f"✅ Vertex AI response generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Vertex AI generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I'm sorry, but I encountered an error while processing your request."
            }
    
    def _build_prompt(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build the full prompt with context and tools."""
        full_prompt = prompt
        
        # Add context if provided
        if context:
            context_str = json.dumps(context, indent=2)
            full_prompt = f"Context:\n{context_str}\n\nPrompt:\n{prompt}"
        
        # Add tools if provided
        if tools:
            tools_str = json.dumps(tools, indent=2)
            full_prompt = f"{full_prompt}\n\nAvailable Tools:\n{tools_str}\n\nYou can use these tools to help answer the prompt."
        
        return full_prompt
    
    async def process_conversation(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a conversation message with context.
        
        Args:
            message: Current message
            conversation_history: Previous conversation messages
            
        Returns:
            Response with conversation context
        """
        context = {
            "conversation_history": conversation_history or [],
            "current_message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Build conversation prompt
        prompt = f"Please respond to this message in the context of a hospital operations system: {message}"
        
        return await self.generate_response(prompt, context)
    
    async def analyze_data(
        self, 
        data: Dict[str, Any], 
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze data using Vertex AI.
        
        Args:
            data: Data to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        prompt = f"Please analyze this {analysis_type} data and provide insights: {json.dumps(data, indent=2)}"
        
        return await self.generate_response(prompt, {"analysis_type": analysis_type})


class VertexAIEnhancedAgent:
    """
    Enhanced Google ADK agent with Vertex AI capabilities.
    
    This class wraps the existing Google ADK agents with Vertex AI intelligence,
    providing enhanced reasoning and natural language processing capabilities.
    """
    
    def __init__(self, base_agent, vertex_config: VertexAIConfig):
        """
        Initialize enhanced agent.
        
        Args:
            base_agent: Base Google ADK agent
            vertex_config: Vertex AI configuration
        """
        self.base_agent = base_agent
        self.vertex_ai = VertexAIAgent(vertex_config)
        self.enhanced = self.vertex_ai.initialized
        
        logger.info(f"✅ Enhanced agent created: {base_agent.name} (Vertex AI: {'enabled' if self.enhanced else 'disabled'})")
    
    async def process_task_with_ai(self, task_request) -> Dict[str, Any]:
        """
        Process a task with AI-enhanced reasoning.
        
        Args:
            task_request: Task request from Google ADK
            
        Returns:
            Enhanced task response
        """
        if not self.enhanced:
            # Fallback to base agent
            return await self.base_agent.process_task(task_request)
        
        try:
            # Use Vertex AI to understand and enhance the task
            ai_prompt = f"""
            You are a hospital operations agent. Please analyze this task and provide guidance:
            
            Task Type: {task_request.task_type}
            Parameters: {json.dumps(task_request.parameters, indent=2)}
            
            Please provide:
            1. Task understanding
            2. Recommended approach
            3. Potential issues or considerations
            """
            
            ai_response = await self.vertex_ai.generate_response(ai_prompt)
            
            if ai_response["success"]:
                # Process with base agent
                base_response = await self.base_agent.process_task(task_request)
                
                # Enhance the response with AI insights
                enhanced_response = {
                    **base_response.dict(),
                    "ai_enhancement": {
                        "analysis": ai_response["response"],
                        "model": ai_response["model"],
                        "enhanced": True
                    }
                }
                
                return enhanced_response
            else:
                # Fallback to base agent if AI fails
                return await self.base_agent.process_task(task_request)
                
        except Exception as e:
            logger.error(f"❌ AI enhancement failed: {e}")
            # Fallback to base agent
            return await self.base_agent.process_task(task_request)
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """Get enhanced agent status."""
        base_status = self.base_agent.get_status()
        
        return {
            **base_status,
            "vertex_ai": {
                "enabled": self.enhanced,
                "model": self.vertex_ai.model_name if self.enhanced else None,
                "initialized": self.vertex_ai.initialized
            }
        }


# Global Vertex AI configuration
VERTEX_AI_CONFIG = None


def initialize_vertex_ai(api_key: str, project_id: str = "shellhacks2025") -> bool:
    """
    Initialize Vertex AI globally.
    
    Args:
        api_key: Google Cloud API key
        project_id: Google Cloud project ID
        
    Returns:
        True if initialization successful
    """
    global VERTEX_AI_CONFIG
    
    try:
        VERTEX_AI_CONFIG = VertexAIConfig(api_key, project_id)
        success = VERTEX_AI_CONFIG.initialize()
        
        if success:
            logger.info("✅ Vertex AI initialized globally")
        else:
            logger.error("❌ Failed to initialize Vertex AI globally")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Vertex AI initialization error: {e}")
        return False


def create_enhanced_agent(base_agent) -> VertexAIEnhancedAgent:
    """
    Create an enhanced agent with Vertex AI capabilities.
    
    Args:
        base_agent: Base Google ADK agent
        
    Returns:
        Enhanced agent with Vertex AI
    """
    if not VERTEX_AI_CONFIG:
        logger.warning("⚠️ Vertex AI not initialized. Creating base agent only.")
        return base_agent
    
    return VertexAIEnhancedAgent(base_agent, VERTEX_AI_CONFIG)
