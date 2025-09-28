"""
Google ADK API Endpoints

This module provides API endpoints for interacting with the real Google ADK
implementation and A2A protocol agents.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
import asyncio
import json
import logging
from datetime import datetime

from ..agents.google_adk import Agent, A2AServer, RemoteA2aAgent, AgentDiscovery
from ..agents.google_adk.protocol import TaskRequest, TaskResponse, TaskStatus, AgentCard
from ..agents.hospital_agents.frontdesk_agent import frontdesk_agent
from ..agents.hospital_agents.queue_agent import queue_agent

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize discovery service
discovery_service = AgentDiscovery()

# Available hospital agents
hospital_agents = {
    "frontdesk": frontdesk_agent,
    "queue": queue_agent
}


@router.get("/agents")
async def get_available_agents():
    """Get all available Google ADK agents."""
    try:
        agents_info = {}
        
        for agent_name, agent in hospital_agents.items():
            agents_info[agent_name] = {
                "name": agent.name,
                "description": agent.description,
                "status": agent.get_status(),
                "agent_card": agent.get_agent_card().to_dict()
            }
        
        return {
            "success": True,
            "agents": agents_info,
            "total_agents": len(hospital_agents),
            "adk_version": "1.0.0",
            "a2a_protocol": "enabled"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_name}")
async def get_agent_info(agent_name: str):
    """Get information about a specific agent."""
    try:
        if agent_name not in hospital_agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        agent = hospital_agents[agent_name]
        
        return {
            "success": True,
            "agent": {
                "name": agent.name,
                "description": agent.description,
                "status": agent.get_status(),
                "agent_card": agent.get_agent_card().to_dict(),
                "tools": [tool.to_dict() for tool in agent.agent.tools]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get agent info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_name}/task")
async def execute_agent_task(agent_name: str, task_request: Dict[str, Any]):
    """Execute a task on a specific agent."""
    try:
        if agent_name not in hospital_agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        agent = hospital_agents[agent_name]
        
        # Create task request
        task = TaskRequest(
            task_type=task_request.get("task_type", "general"),
            parameters=task_request.get("parameters", {}),
            from_agent="api_client",
            to_agent=agent_name,
            timeout=task_request.get("timeout", 30.0)
        )
        
        # Execute task
        response = await agent.process_task(task)
        
        return {
            "success": True,
            "task_response": response.dict(),
            "agent": agent_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Task execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_name}/stream")
async def stream_agent_task(agent_name: str, task_request: Dict[str, Any]):
    """Stream task execution from an agent."""
    try:
        if agent_name not in hospital_agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        agent = hospital_agents[agent_name]
        
        # Create task request
        task = TaskRequest(
            task_type=task_request.get("task_type", "general"),
            parameters=task_request.get("parameters", {}),
            from_agent="api_client",
            to_agent=agent_name,
            timeout=task_request.get("timeout", 30.0)
        )
        
        async def generate():
            # Start task
            yield f"data: {json.dumps({'type': 'start', 'task_id': task.task_id, 'agent': agent_name})}\n\n"
            
            try:
                # Execute task
                response = await agent.process_task(task)
                
                # Send result
                yield f"data: {json.dumps({'type': 'result', 'data': response.dict()})}\n\n"
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Streaming task failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discovery")
async def get_discovery_info():
    """Get agent discovery information."""
    try:
        # Get registry stats
        registry_stats = discovery_service.get_registry_stats()
        
        # Get available agents
        available_agents = []
        for agent_name, agent in hospital_agents.items():
            available_agents.append({
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.get_agent_card().capabilities,
                "skills": agent.get_agent_card().skills
            })
        
        return {
            "success": True,
            "discovery": {
                "registry_stats": registry_stats,
                "available_agents": available_agents,
                "protocol": "A2A",
                "version": "1.0.0"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get discovery info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discovery/search")
async def search_agents(query: Dict[str, Any]):
    """Search for agents by capability or query."""
    try:
        search_query = query.get("query", "")
        capability = query.get("capability", "")
        
        results = []
        
        if capability:
            # Search by capability
            for agent_name, agent in hospital_agents.items():
                agent_card = agent.get_agent_card()
                if agent_card.skills:
                    for skill in agent_card.skills:
                        if capability.lower() in [tag.lower() for tag in skill.get("tags", [])]:
                            results.append({
                                "agent": agent_name,
                                "skill": skill,
                                "match_type": "capability"
                            })
        
        if search_query:
            # Search by text query
            for agent_name, agent in hospital_agents.items():
                agent_card = agent.get_agent_card()
                
                # Search in name, description, and skills
                if (search_query.lower() in agent.name.lower() or
                    search_query.lower() in agent.description.lower()):
                    results.append({
                        "agent": agent_name,
                        "match_type": "text",
                        "matched_field": "name_or_description"
                    })
                
                # Search in skills
                if agent_card.skills:
                    for skill in agent_card.skills:
                        if (search_query.lower() in skill.get("name", "").lower() or
                            search_query.lower() in skill.get("description", "").lower()):
                            results.append({
                                "agent": agent_name,
                                "skill": skill,
                                "match_type": "text",
                                "matched_field": "skill"
                            })
        
        return {
            "success": True,
            "search_results": results,
            "query": query,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"❌ Agent search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_adk_status():
    """Get Google ADK system status."""
    try:
        agent_statuses = {}
        total_tools = 0
        
        for agent_name, agent in hospital_agents.items():
            status = agent.get_status()
            agent_statuses[agent_name] = status
            total_tools += status.get("tools_count", 0)
        
        return {
            "success": True,
            "adk_status": {
                "version": "1.0.0",
                "a2a_protocol": "enabled",
                "total_agents": len(hospital_agents),
                "total_tools": total_tools,
                "agents": agent_statuses,
                "discovery_service": discovery_service.get_registry_stats()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get ADK status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/patient-registration")
async def execute_patient_registration_workflow(workflow_data: Dict[str, Any]):
    """Execute a complete patient registration workflow using multiple agents."""
    try:
        # Step 1: Register patient with frontdesk agent
        frontdesk_task = TaskRequest(
            task_type="tool_execution",
            parameters={
                "tool_name": "patient_registration",
                "parameters": workflow_data.get("patient_info", {})
            },
            from_agent="workflow_orchestrator",
            to_agent="frontdesk"
        )
        
        frontdesk_response = await frontdesk_agent.process_task(frontdesk_task)
        
        if frontdesk_response.status != TaskStatus.COMPLETED:
            return {
                "success": False,
                "message": "Patient registration failed",
                "error": frontdesk_response.result
            }
        
        # Step 2: Check in patient if appointment exists
        if workflow_data.get("appointment_info"):
            checkin_task = TaskRequest(
                task_type="tool_execution",
                parameters={
                    "tool_name": "patient_checkin",
                    "parameters": {
                        "patient_id": frontdesk_response.result.get("patient_id"),
                        "appointment_id": workflow_data["appointment_info"].get("appointment_id")
                    }
                },
                from_agent="workflow_orchestrator",
                to_agent="frontdesk"
            )
            
            checkin_response = await frontdesk_agent.process_task(checkin_task)
            
            # Step 3: Update queue with queue agent
            if checkin_response.status == TaskStatus.COMPLETED:
                queue_task = TaskRequest(
                    task_type="tool_execution",
                    parameters={
                        "tool_name": "get_queue_status",
                        "parameters": {
                            "department": workflow_data["appointment_info"].get("department")
                        }
                    },
                    from_agent="workflow_orchestrator",
                    to_agent="queue"
                )
                
                queue_response = await queue_agent.process_task(queue_task)
                
                return {
                    "success": True,
                    "message": "Patient registration workflow completed",
                    "workflow_steps": [
                        {
                            "step": "patient_registration",
                            "agent": "frontdesk",
                            "status": frontdesk_response.status.value,
                            "result": frontdesk_response.result
                        },
                        {
                            "step": "patient_checkin",
                            "agent": "frontdesk",
                            "status": checkin_response.status.value,
                            "result": checkin_response.result
                        },
                        {
                            "step": "queue_update",
                            "agent": "queue",
                            "status": queue_response.status.value,
                            "result": queue_response.result
                        }
                    ]
                }
        
        return {
            "success": True,
            "message": "Patient registration completed",
            "workflow_steps": [
                {
                    "step": "patient_registration",
                    "agent": "frontdesk",
                    "status": frontdesk_response.status.value,
                    "result": frontdesk_response.result
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Patient registration workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
