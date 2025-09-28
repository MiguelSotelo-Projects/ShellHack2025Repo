"""
Hybrid Agent API

API endpoints for the hybrid agent communication system that supports
both simulated and real agent communication.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
import asyncio
import json
import logging
from datetime import datetime

from ..services.hybrid_agent_service import (
    hybrid_agent_service, 
    CommunicationMode, 
    MessageType
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.on_event("startup")
async def startup_event():
    """Initialize the hybrid agent service on startup."""
    try:
        await hybrid_agent_service.start(CommunicationMode.SIMULATED)
        logger.info("✅ Hybrid Agent Service initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Hybrid Agent Service: {e}")


@router.on_event("shutdown")
async def shutdown_event():
    """Cleanup the hybrid agent service on shutdown."""
    try:
        await hybrid_agent_service.stop()
        logger.info("🛑 Hybrid Agent Service stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping Hybrid Agent Service: {e}")


@router.get("/status")
async def get_agent_status():
    """Get current status of all agents."""
    try:
        status = hybrid_agent_service.get_agent_status()
        stats = hybrid_agent_service.get_communication_stats()
        
        return {
            "success": True,
            "agents": status,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages")
async def get_message_history(limit: int = 50):
    """Get recent message history."""
    try:
        messages = hybrid_agent_service.get_message_history(limit)
        
        return {
            "success": True,
            "messages": messages,
            "count": len(messages),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting message history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-message")
async def send_agent_message(
    from_agent: str,
    to_agent: str,
    message_type: str,
    payload: Dict[str, Any]
):
    """Send a message between agents."""
    try:
        # Validate message type
        try:
            msg_type = MessageType(message_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid message type: {message_type}")
        
        # Send message
        message = await hybrid_agent_service.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=msg_type,
            payload=payload
        )
        
        return {
            "success": True,
            "message": message.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/{workflow_name}")
async def execute_workflow(
    workflow_name: str,
    parameters: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Execute a predefined workflow."""
    try:
        # Execute workflow in background
        background_tasks.add_task(
            _execute_workflow_background,
            workflow_name,
            parameters
        )
        
        return {
            "success": True,
            "message": f"Workflow '{workflow_name}' started",
            "workflow": workflow_name,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_workflow_background(workflow_name: str, parameters: Dict[str, Any]):
    """Execute workflow in background."""
    try:
        messages = await hybrid_agent_service.execute_workflow(workflow_name, parameters)
        logger.info(f"✅ Workflow '{workflow_name}' completed with {len(messages)} messages")
    except Exception as e:
        logger.error(f"❌ Workflow '{workflow_name}' failed: {e}")


@router.get("/workflows")
async def get_available_workflows():
    """Get list of available workflows."""
    try:
        workflows = list(hybrid_agent_service.workflow_templates.keys())
        
        return {
            "success": True,
            "workflows": workflows,
            "count": len(workflows),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mode")
async def set_communication_mode(mode: str):
    """Set the communication mode (simulated, real, hybrid)."""
    try:
        # Validate mode
        try:
            comm_mode = CommunicationMode(mode)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}")
        
        # Stop current service
        await hybrid_agent_service.stop()
        
        # Start with new mode
        await hybrid_agent_service.start(comm_mode)
        
        return {
            "success": True,
            "message": f"Communication mode changed to {mode}",
            "mode": mode,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error changing communication mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_communication_stats():
    """Get detailed communication statistics."""
    try:
        stats = hybrid_agent_service.get_communication_stats()
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting communication stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream")
async def stream_agent_communication():
    """Stream real-time agent communication events."""
    async def event_generator():
        """Generate Server-Sent Events for real-time communication."""
        try:
            while True:
                # Get latest messages
                messages = hybrid_agent_service.get_message_history(10)
                stats = hybrid_agent_service.get_communication_stats()
                
                # Send data as SSE
                data = {
                    "type": "update",
                    "messages": messages,
                    "stats": stats,
                    "timestamp": datetime.now().isoformat()
                }
                
                yield f"data: {json.dumps(data)}\n\n"
                
                # Wait before next update
                await asyncio.sleep(2)
                
        except asyncio.CancelledError:
            logger.info("SSE connection cancelled")
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.post("/test-communication")
async def test_agent_communication():
    """Test agent communication with a simple workflow."""
    try:
        # Test with patient registration workflow
        test_parameters = {
            "patient_name": "Test Patient",
            "patient_phone": "555-0123",
            "priority": "medium"
        }
        
        messages = await hybrid_agent_service.execute_workflow(
            "patient_registration", 
            test_parameters
        )
        
        return {
            "success": True,
            "message": "Agent communication test completed",
            "workflow": "patient_registration",
            "messages_sent": len(messages),
            "messages": [msg.to_dict() for msg in messages],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error testing agent communication: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for the hybrid agent service."""
    try:
        stats = hybrid_agent_service.get_communication_stats()
        
        return {
            "status": "healthy",
            "service": "hybrid-agent-service",
            "mode": stats["mode"],
            "is_running": stats["is_running"],
            "active_agents": stats["active_agents"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "hybrid-agent-service",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
