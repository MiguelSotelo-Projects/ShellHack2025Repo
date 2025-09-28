#!/usr/bin/env python3
"""
Start Agent-to-Agent Communication System

This script starts all the specialized agents and enables agent-to-agent communication.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from agents.agent_manager import AgentManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main function to start the agent system."""
    logger.info("🚀 Starting Ops Mesh Agent-to-Agent Communication System...")
    
    # Check environment variables
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        logger.error("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
        logger.info("Please set GOOGLE_CLOUD_PROJECT in your .env file")
        return
    
    logger.info(f"📋 Using Google Cloud Project: {project_id}")
    
    # Create agent manager
    manager = AgentManager(project_id)
    
    try:
        logger.info("🔧 Initializing all agents...")
        await manager.initialize_all_agents()
        
        logger.info("✅ All agents initialized successfully!")
        logger.info("🤖 Starting agent-to-agent communication...")
        
        # Start all agents
        await manager.start_all_agents()
        
    except KeyboardInterrupt:
        logger.info("⏹️  Received interrupt signal, stopping agents...")
        await manager.stop_all_agents()
    except Exception as e:
        logger.error(f"❌ Error running agent system: {e}")
        await manager.stop_all_agents()
        raise


if __name__ == "__main__":
    print("🏥 Ops Mesh Agent-to-Agent Communication System")
    print("=" * 50)
    print("🤖 Starting specialized agents:")
    print("   • FrontDesk Agent - Patient registration & check-in")
    print("   • Queue Agent - Queue management & wait times")
    print("   • Appointment Agent - Appointment scheduling")
    print("   • Notification Agent - Alerts & notifications")
    print("   • Orchestrator Agent - Workflow coordination")
    print("=" * 50)
    print()
    
    asyncio.run(main())
