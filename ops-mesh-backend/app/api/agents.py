from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
import asyncio
import logging
from ..agents.agent_manager import AgentManager
from ..agents.protocol.a2a_protocol import A2AProtocol

router = APIRouter()
logger = logging.getLogger(__name__)

# Global agent manager instance
agent_manager = None

async def get_agent_manager():
    """Get or create agent manager instance"""
    global agent_manager
    if agent_manager is None:
        agent_manager = AgentManager("ops-mesh-demo")
        await agent_manager.initialize_all_agents()
    return agent_manager

@router.get("/status")
async def get_agent_status():
    """Get status of all agents"""
    try:
        manager = await get_agent_manager()
        status = await manager.get_agent_status()
        return {
            "success": True,
            "agents": status,
            "total_agents": len(status)
        }
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discovery")
async def get_discovery_info():
    """Get agent discovery information"""
    try:
        manager = await get_agent_manager()
        discovery_info = await manager.get_discovery_info()
        return {
            "success": True,
            "discovery": discovery_info
        }
    except Exception as e:
        logger.error(f"Error getting discovery info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/patient-registration")
async def start_patient_registration_workflow(
    background_tasks: BackgroundTasks,
    patient_data: Dict[str, Any]
):
    """Start a patient registration workflow using A2A protocol"""
    try:
        manager = await get_agent_manager()
        
        # Start the workflow in the background
        background_tasks.add_task(
            _execute_patient_registration_workflow,
            manager,
            patient_data
        )
        
        return {
            "success": True,
            "message": "Patient registration workflow started",
            "workflow_id": f"patient_reg_{patient_data.get('first_name', 'unknown')}_{asyncio.get_event_loop().time()}"
        }
    except Exception as e:
        logger.error(f"Error starting patient registration workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/appointment-scheduling")
async def start_appointment_scheduling_workflow(
    background_tasks: BackgroundTasks,
    appointment_data: Dict[str, Any]
):
    """Start an appointment scheduling workflow using A2A protocol"""
    try:
        manager = await get_agent_manager()
        
        # Start the workflow in the background
        background_tasks.add_task(
            _execute_appointment_scheduling_workflow,
            manager,
            appointment_data
        )
        
        return {
            "success": True,
            "message": "Appointment scheduling workflow started",
            "workflow_id": f"appointment_{appointment_data.get('patient_id', 'unknown')}_{asyncio.get_event_loop().time()}"
        }
    except Exception as e:
        logger.error(f"Error starting appointment scheduling workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/queue-management")
async def start_queue_management_workflow(
    background_tasks: BackgroundTasks,
    queue_data: Dict[str, Any]
):
    """Start a queue management workflow using A2A protocol"""
    try:
        manager = await get_agent_manager()
        
        # Start the workflow in the background
        background_tasks.add_task(
            _execute_queue_management_workflow,
            manager,
            queue_data
        )
        
        return {
            "success": True,
            "message": "Queue management workflow started",
            "workflow_id": f"queue_{queue_data.get('action', 'unknown')}_{asyncio.get_event_loop().time()}"
        }
    except Exception as e:
        logger.error(f"Error starting queue management workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/emergency-coordination")
async def start_emergency_coordination_workflow(
    background_tasks: BackgroundTasks,
    emergency_data: Dict[str, Any]
):
    """Start an emergency coordination workflow using A2A protocol"""
    try:
        manager = await get_agent_manager()
        
        # Start the workflow in the background
        background_tasks.add_task(
            _execute_emergency_coordination_workflow,
            manager,
            emergency_data
        )
        
        return {
            "success": True,
            "message": "Emergency coordination workflow started",
            "workflow_id": f"emergency_{emergency_data.get('patient_id', 'unknown')}_{asyncio.get_event_loop().time()}"
        }
    except Exception as e:
        logger.error(f"Error starting emergency coordination workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _execute_patient_registration_workflow(manager: AgentManager, patient_data: Dict[str, Any]):
    """Execute patient registration workflow"""
    try:
        logger.info(f"Starting patient registration workflow for {patient_data.get('first_name')}")
        
        # Step 1: Register patient with FrontDesk Agent
        result1 = await manager.send_message_to_agent(
            target_agent="frontdesk",
            message_type="register_patient",
            payload=patient_data
        )
        
        if result1:
            logger.info("✅ Patient registered successfully")
            
            # Step 2: Add to queue with Queue Agent
            queue_data = {
                "patient_id": patient_data.get("patient_id"),
                "priority": patient_data.get("priority", "medium"),
                "queue_type": "walk_in"
            }
            
            result2 = await manager.send_message_to_agent(
                target_agent="queue",
                message_type="add_to_queue",
                payload=queue_data
            )
            
            if result2:
                logger.info("✅ Patient added to queue successfully")
                
                # Step 3: Send notification
                notification_data = {
                    "recipient": f"patient_{patient_data.get('patient_id')}",
                    "message": f"Welcome {patient_data.get('first_name')}! You have been registered and added to the queue.",
                    "type": "welcome"
                }
                
                result3 = await manager.send_message_to_agent(
                    target_agent="notification",
                    message_type="send_notification",
                    payload=notification_data
                )
                
                if result3:
                    logger.info("✅ Welcome notification sent")
                else:
                    logger.warning("⚠️ Failed to send welcome notification")
            else:
                logger.warning("⚠️ Failed to add patient to queue")
        else:
            logger.warning("⚠️ Failed to register patient")
            
    except Exception as e:
        logger.error(f"Error in patient registration workflow: {e}")

async def _execute_appointment_scheduling_workflow(manager: AgentManager, appointment_data: Dict[str, Any]):
    """Execute appointment scheduling workflow"""
    try:
        logger.info(f"Starting appointment scheduling workflow for patient {appointment_data.get('patient_id')}")
        
        # Step 1: Schedule appointment with Appointment Agent
        result1 = await manager.send_message_to_agent(
            target_agent="appointment",
            message_type="schedule_appointment",
            payload=appointment_data
        )
        
        if result1:
            logger.info("✅ Appointment scheduled successfully")
            
            # Step 2: Send confirmation notification
            notification_data = {
                "recipient": f"patient_{appointment_data.get('patient_id')}",
                "message": f"Your appointment has been scheduled for {appointment_data.get('appointment_time')} with {appointment_data.get('provider')}.",
                "type": "appointment_confirmation"
            }
            
            result2 = await manager.send_message_to_agent(
                target_agent="notification",
                message_type="send_notification",
                payload=notification_data
            )
            
            if result2:
                logger.info("✅ Appointment confirmation sent")
            else:
                logger.warning("⚠️ Failed to send appointment confirmation")
        else:
            logger.warning("⚠️ Failed to schedule appointment")
            
    except Exception as e:
        logger.error(f"Error in appointment scheduling workflow: {e}")

async def _execute_queue_management_workflow(manager: AgentManager, queue_data: Dict[str, Any]):
    """Execute queue management workflow"""
    try:
        action = queue_data.get("action")
        logger.info(f"Starting queue management workflow: {action}")
        
        if action == "call_next_patient":
            result = await manager.send_message_to_agent(
                target_agent="queue",
                message_type="call_next_patient",
                payload={}
            )
            
            if result:
                logger.info("✅ Next patient called successfully")
            else:
                logger.warning("⚠️ Failed to call next patient")
                
        elif action == "get_queue_status":
            result = await manager.send_message_to_agent(
                target_agent="queue",
                message_type="get_queue_status",
                payload={}
            )
            
            if result:
                logger.info("✅ Queue status retrieved successfully")
            else:
                logger.warning("⚠️ Failed to get queue status")
                
    except Exception as e:
        logger.error(f"Error in queue management workflow: {e}")

async def _execute_emergency_coordination_workflow(manager: AgentManager, emergency_data: Dict[str, Any]):
    """Execute emergency coordination workflow"""
    try:
        logger.info(f"Starting emergency coordination workflow for patient {emergency_data.get('patient_id')}")
        
        # Use orchestrator to coordinate emergency response
        result = await manager.send_message_to_agent(
            target_agent="orchestrator",
            message_type="coordinate_emergency",
            payload=emergency_data
        )
        
        if result:
            logger.info("✅ Emergency coordination completed successfully")
        else:
            logger.warning("⚠️ Failed to coordinate emergency response")
            
    except Exception as e:
        logger.error(f"Error in emergency coordination workflow: {e}")

@router.get("/test-communication")
async def test_agent_communication():
    """Test basic agent-to-agent communication"""
    try:
        manager = await get_agent_manager()
        
        # Test simple communication between agents
        test_data = {
            "test": "communication",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        result = await manager.send_message_to_agent(
            target_agent="notification",
            message_type="send_notification",
            payload=test_data
        )
        
        return {
            "success": True,
            "message": "Agent communication test completed",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error testing agent communication: {e}")
        raise HTTPException(status_code=500, detail=str(e))
