#!/usr/bin/env python3
"""
Initialize Vertex AI with API Key

This script initializes Vertex AI integration for the hospital agents
using the provided API key.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "ops-mesh-backend"
sys.path.insert(0, str(backend_dir))

from app.agents.vertex_ai_agents import initialize_vertex_ai_agents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main function to initialize Vertex AI."""
    # Your API key
    api_key = "AQ.Ab8RN6IjxxUAW5VzdXFCyzTVq-EJRWYHmiq-BnKHRFULi4zyyw"
    project_id = "shellhacks2025"
    
    logger.info("🤖 Initializing Vertex AI for Hospital Agents...")
    logger.info("=" * 60)
    
    try:
        # Initialize Vertex AI agents
        vertex_ai_agents = initialize_vertex_ai_agents(api_key, project_id)
        
        if vertex_ai_agents and vertex_ai_agents.initialized:
            logger.info("✅ Vertex AI Hospital Agents initialized successfully!")
            
            # Start all agents
            await vertex_ai_agents.start_all_agents()
            logger.info("🚀 All Vertex AI agents started!")
            
            # Get status
            status = vertex_ai_agents.get_status()
            logger.info(f"📊 Status: {status}")
            
            logger.info("=" * 60)
            logger.info("🎉 Vertex AI integration complete!")
            logger.info("You can now use the Vertex AI enhanced agents:")
            logger.info("- FrontDesk Agent with AI reasoning")
            logger.info("- Queue Agent with AI optimization")
            logger.info("- Intelligent patient flow workflows")
            logger.info("=" * 60)
            
        else:
            logger.error("❌ Failed to initialize Vertex AI agents")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Error initializing Vertex AI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("🤖 Vertex AI Hospital Agents Initialization")
    print("=" * 50)
    print("Initializing Vertex AI integration...")
    print("This will enhance hospital agents with AI capabilities")
    print("=" * 50)
    
    asyncio.run(main())
