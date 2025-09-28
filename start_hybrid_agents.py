#!/usr/bin/env python3
"""
Start Hybrid Agent System

This script starts the hybrid agent communication system that supports
both simulated and real agent communication.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "ops-mesh-backend" / "app"
sys.path.insert(0, str(app_dir))

from services.hybrid_agent_service import hybrid_agent_service, CommunicationMode

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main function to start the hybrid agent system."""
    print("=" * 60)
    print("🚀 Starting Hybrid Agent Communication System")
    print("=" * 60)
    print("This system supports both simulated and real agent communication.")
    print("It will automatically fall back to simulation if real agents")
    print("are not available.")
    print("=" * 60)
    print()
    
    try:
        # Start in simulated mode first
        logger.info("🔧 Starting hybrid agent service in simulated mode...")
        await hybrid_agent_service.start(CommunicationMode.SIMULATED)
        
        logger.info("✅ Hybrid Agent Service started successfully!")
        logger.info("🤖 Agent communication is now active")
        logger.info("📊 You can monitor the system via the web interface")
        logger.info("🌐 Visit: http://localhost:3000/hybrid-agents")
        logger.info()
        logger.info("Press Ctrl+C to stop the service...")
        
        # Keep the service running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️  Received interrupt signal, stopping service...")
        await hybrid_agent_service.stop()
        logger.info("🛑 Hybrid Agent Service stopped")
    except Exception as e:
        logger.error(f"❌ Error running hybrid agent system: {e}")
        await hybrid_agent_service.stop()
        raise


if __name__ == "__main__":
    asyncio.run(main())
