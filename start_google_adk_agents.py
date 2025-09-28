#!/usr/bin/env python3
"""
Start Google ADK Hospital Agents

This script starts all hospital agents using the real Google ADK implementation
with A2A protocol for inter-agent communication.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "ops-mesh-backend"
sys.path.insert(0, str(backend_dir))

from app.agents.a2a_server import start_a2a_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('google_adk_agents.log')
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main function to start Google ADK agents."""
    logger.info("🚀 Starting Google ADK Hospital Agents...")
    logger.info("=" * 60)
    
    try:
        # Start the A2A server with all hospital agents
        await start_a2a_server(host="0.0.0.0", port=8000)
        
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"❌ Error starting Google ADK agents: {e}")
        sys.exit(1)
    finally:
        logger.info("🛑 Google ADK agents stopped")


if __name__ == "__main__":
    print("🤖 Google ADK Hospital Agents")
    print("=" * 40)
    print("Starting hospital agents with real Google ADK implementation...")
    print("Agents will be available via A2A protocol")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    asyncio.run(main())
