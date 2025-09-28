"""
Vertex AI API Endpoints

This module provides API endpoints for interacting with Vertex AI enhanced agents.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
import asyncio
import json
import logging
from datetime import datetime

from ..agents.vertex_ai_integration import initialize_vertex_ai, VertexAIAgent, VertexAIConfig
from ..agents.vertex_ai_agents import initialize_vertex_ai_agents, get_vertex_ai_agents
from ..agents.google_adk.protocol import TaskRequest, TaskResponse, TaskStatus

router = APIRouter()
logger = logging.getLogger(__name__)

# Global Vertex AI agents instance
vertex_ai_agents = None


@router.post("/initialize")
async def initialize_vertex_ai_endpoint(config: Dict[str, Any]):
    """Initialize Vertex AI with API key and configuration."""
    try:
        api_key = config.get("api_key")
        project_id = config.get("project_id", "shellhacks2025")
        
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Initialize Vertex AI agents
        global vertex_ai_agents
        vertex_ai_agents = initialize_vertex_ai_agents(api_key, project_id)
        
        if not vertex_ai_agents or not vertex_ai_agents.initialized:
            raise HTTPException(status_code=500, detail="Failed to initialize Vertex AI")
        
        # Start all agents
        await vertex_ai_agents.start_all_agents()
        
        return {
            "success": True,
            "message": "Vertex AI initialized successfully",
            "project_id": project_id,
            "agents_count": len(vertex_ai_agents.get_all_agents()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Vertex AI initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_vertex_ai_status():
    """Get Vertex AI system status."""
    try:
        if not vertex_ai_agents:
            return {
                "success": False,
                "message": "Vertex AI not initialized",
                "initialized": False
            }
        
        status = vertex_ai_agents.get_status()
        
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get Vertex AI status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_vertex_ai_agents_list():
    """Get list of Vertex AI enhanced agents."""
    try:
        if not vertex_ai_agents:
            raise HTTPException(status_code=400, detail="Vertex AI not initialized")
        
        agents = vertex_ai_agents.get_all_agents()
        agents_info = {}
        
        for agent_name, agent in agents.items():
            if hasattr(agent, 'get_enhanced_status'):
                agents_info[agent_name] = agent.get_enhanced_status()
            elif hasattr(agent, 'get_status'):
                agents_info[agent_name] = agent.get_status()
            else:
                agents_info[agent_name] = {"name": agent_name, "status": "unknown"}
        
        return {
            "success": True,
            "agents": agents_info,
            "total_agents": len(agents),
            "vertex_ai_enabled": True
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get Vertex AI agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_name}/task")
async def execute_vertex_ai_task(agent_name: str, task_request: Dict[str, Any]):
    """Execute a task on a Vertex AI enhanced agent."""
    try:
        if not vertex_ai_agents:
            raise HTTPException(status_code=400, detail="Vertex AI not initialized")
        
        agent = vertex_ai_agents.get_agent(agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        # Create task request
        task = TaskRequest(
            task_type=task_request.get("task_type", "general"),
            parameters=task_request.get("parameters", {}),
            from_agent="api_client",
            to_agent=agent_name,
            timeout=task_request.get("timeout", 30.0)
        )
        
        # Execute task with AI enhancement
        if hasattr(agent, 'process_task_with_ai'):
            response = await agent.process_task_with_ai(task)
        else:
            response = await agent.process_task(task)
        
        return {
            "success": True,
            "task_response": response.dict() if hasattr(response, 'dict') else response,
            "agent": agent_name,
            "vertex_ai_enhanced": hasattr(agent, 'process_task_with_ai')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Vertex AI task execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_name}/conversation")
async def vertex_ai_conversation(agent_name: str, conversation_data: Dict[str, Any]):
    """Have a conversation with a Vertex AI enhanced agent."""
    try:
        if not vertex_ai_agents:
            raise HTTPException(status_code=400, detail="Vertex AI not initialized")
        
        agent = vertex_ai_agents.get_agent(agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        message = conversation_data.get("message", "")
        conversation_history = conversation_data.get("history", [])
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Use Vertex AI for conversation
        if hasattr(agent, 'vertex_ai') and agent.vertex_ai.initialized:
            response = await agent.vertex_ai.process_conversation(message, conversation_history)
        else:
            # Fallback to basic response
            response = {
                "success": True,
                "response": f"Agent {agent_name} received your message: {message}",
                "model": "fallback",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "conversation_response": response,
            "agent": agent_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Vertex AI conversation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_name}/analyze")
async def vertex_ai_analyze_data(agent_name: str, analysis_data: Dict[str, Any]):
    """Analyze data using Vertex AI."""
    try:
        if not vertex_ai_agents:
            raise HTTPException(status_code=400, detail="Vertex AI not initialized")
        
        agent = vertex_ai_agents.get_agent(agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        data = analysis_data.get("data", {})
        analysis_type = analysis_data.get("analysis_type", "general")
        
        if not data:
            raise HTTPException(status_code=400, detail="Data is required")
        
        # Use Vertex AI for analysis
        if hasattr(agent, 'vertex_ai') and agent.vertex_ai.initialized:
            response = await agent.vertex_ai.analyze_data(data, analysis_type)
        else:
            # Fallback to basic analysis
            response = {
                "success": True,
                "response": f"Basic analysis of {analysis_type} data completed",
                "model": "fallback",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "analysis_response": response,
            "agent": agent_name,
            "analysis_type": analysis_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Vertex AI analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/intelligent-patient-flow")
async def intelligent_patient_flow_workflow(workflow_data: Dict[str, Any]):
    """Execute an intelligent patient flow workflow using Vertex AI."""
    try:
        if not vertex_ai_agents:
            raise HTTPException(status_code=400, detail="Vertex AI not initialized")
        
        # Get patient information
        patient_info = workflow_data.get("patient_info", {})
        appointment_info = workflow_data.get("appointment_info", {})
        
        # Use Vertex AI to analyze and optimize the patient flow
        frontdesk_agent = vertex_ai_agents.get_agent("frontdesk")
        queue_agent = vertex_ai_agents.get_agent("queue")
        
        if not frontdesk_agent or not queue_agent:
            raise HTTPException(status_code=500, detail="Required agents not available")
        
        workflow_steps = []
        
        # Step 1: AI-enhanced patient registration
        if patient_info:
            registration_task = TaskRequest(
                task_type="tool_execution",
                parameters={
                    "tool_name": "patient_registration",
                    "parameters": patient_info
                },
                from_agent="workflow_orchestrator",
                to_agent="frontdesk"
            )
            
            if hasattr(frontdesk_agent, 'process_task_with_ai'):
                registration_response = await frontdesk_agent.process_task_with_ai(registration_task)
            else:
                registration_response = await frontdesk_agent.process_task(registration_task)
            
            workflow_steps.append({
                "step": "ai_enhanced_registration",
                "agent": "frontdesk",
                "status": registration_response.status if hasattr(registration_response, 'status') else "completed",
                "result": registration_response.dict() if hasattr(registration_response, 'dict') else registration_response
            })
        
        # Step 2: AI-enhanced queue optimization
        if appointment_info:
            queue_task = TaskRequest(
                task_type="tool_execution",
                parameters={
                    "tool_name": "optimize_queue",
                    "parameters": {
                        "department": appointment_info.get("department"),
                        "max_wait_time": 20  # AI-optimized wait time
                    }
                },
                from_agent="workflow_orchestrator",
                to_agent="queue"
            )
            
            if hasattr(queue_agent, 'process_task_with_ai'):
                queue_response = await queue_agent.process_task_with_ai(queue_task)
            else:
                queue_response = await queue_agent.process_task(queue_task)
            
            workflow_steps.append({
                "step": "ai_enhanced_queue_optimization",
                "agent": "queue",
                "status": queue_response.status if hasattr(queue_response, 'status') else "completed",
                "result": queue_response.dict() if hasattr(queue_response, 'dict') else queue_response
            })
        
        return {
            "success": True,
            "message": "Intelligent patient flow workflow completed",
            "workflow_type": "vertex_ai_enhanced",
            "workflow_steps": workflow_steps,
            "ai_enhanced": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Intelligent patient flow workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models():
    """Get available Vertex AI models."""
    try:
        # This would typically query Vertex AI for available models
        # For demo purposes, we'll return the models we're using
        models = [
            {
                "name": "gemini-1.5-flash",
                "description": "Fast and efficient model for real-time applications",
                "capabilities": ["text", "reasoning", "conversation"]
            },
            {
                "name": "gemini-1.5-pro",
                "description": "Advanced model for complex reasoning tasks",
                "capabilities": ["text", "reasoning", "analysis", "conversation"]
            }
        ]
        
        return {
            "success": True,
            "models": models,
            "current_model": "gemini-1.5-flash",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get available models: {e}")
        raise HTTPException(status_code=500, detail=str(e))
