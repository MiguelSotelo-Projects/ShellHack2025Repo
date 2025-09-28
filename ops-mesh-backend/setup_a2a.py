#!/usr/bin/env python3
"""
A2A Server Setup Script for Ops Mesh

This script sets up the A2A (Agent-to-Agent) server for the Ops Mesh system.
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


class A2AServerSetup:
    """A2A Server Setup and Configuration"""
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.agent_manager = None
        self.agents_config = {
            "frontdesk_agent": {
                "enabled": True,
                "port": 8001,
                "agent_card": "ops-mesh-backend/agents/frontdesk_agent.json"
            },
            "queue_agent": {
                "enabled": True,
                "port": 8002,
                "agent_card": "ops-mesh-backend/agents/queue_agent.json"
            },
            "appointment_agent": {
                "enabled": True,
                "port": 8003,
                "agent_card": "ops-mesh-backend/agents/appointment_agent.json"
            },
            "notification_agent": {
                "enabled": True,
                "port": 8004,
                "agent_card": "ops-mesh-backend/agents/notification_agent.json"
            },
            "orchestrator_agent": {
                "enabled": True,
                "port": 8005,
                "agent_card": "ops-mesh-backend/agents/orchestrator_agent.json"
            }
        }
    
    async def setup_environment(self):
        """Set up the A2A environment"""
        logger.info("🔧 Setting up A2A environment...")
        
        # Check if Google Cloud Project is set
        if not self.project_id:
            logger.error("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
            logger.info("Please set GOOGLE_CLOUD_PROJECT in your .env file")
            return False
        
        logger.info(f"📋 Using Google Cloud Project: {self.project_id}")
        
        # Check if agent cards exist
        for agent_name, config in self.agents_config.items():
            agent_card_path = config["agent_card"]
            if not Path(agent_card_path).exists():
                logger.warning(f"⚠️  Agent card not found: {agent_card_path}")
            else:
                logger.info(f"✅ Agent card found: {agent_name}")
        
        return True
    
    async def start_a2a_server(self):
        """Start the A2A server with all agents"""
        logger.info("🚀 Starting A2A server...")
        
        try:
            # Create agent manager
            self.agent_manager = AgentManager(self.project_id)
            
            # Initialize all agents
            logger.info("🔧 Initializing all agents...")
            await self.agent_manager.initialize_all_agents()
            
            logger.info("✅ All agents initialized successfully!")
            logger.info("🤖 Starting A2A agent-to-agent communication...")
            
            # Start all agents
            await self.agent_manager.start_all_agents()
            
        except KeyboardInterrupt:
            logger.info("⏹️  Received interrupt signal, stopping A2A server...")
            await self.stop_a2a_server()
        except Exception as e:
            logger.error(f"❌ Error running A2A server: {e}")
            await self.stop_a2a_server()
            raise
    
    async def stop_a2a_server(self):
        """Stop the A2A server"""
        if self.agent_manager:
            await self.agent_manager.stop_all_agents()
        logger.info("🛑 A2A server stopped")
    
    def generate_a2a_config(self):
        """Generate A2A configuration file"""
        config = {
            "a2a_server": {
                "project_id": self.project_id,
                "region": "us-central1",
                "agents": {}
            }
        }
        
        for agent_name, agent_config in self.agents_config.items():
            if agent_config["enabled"]:
                config["a2a_server"]["agents"][agent_name] = {
                    "port": agent_config["port"],
                    "agent_card": agent_config["agent_card"],
                    "capabilities": self._get_agent_capabilities(agent_config["agent_card"])
                }
        
        # Write config file
        import json
        config_path = Path("ops-mesh-backend/a2a_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"📝 A2A configuration written to: {config_path}")
        return config_path
    
    def _get_agent_capabilities(self, agent_card_path: str) -> list:
        """Get agent capabilities from agent card"""
        try:
            import json
            with open(agent_card_path, 'r') as f:
                agent_card = json.load(f)
            return agent_card.get("capabilities", [])
        except Exception as e:
            logger.warning(f"Could not read agent card {agent_card_path}: {e}")
            return []
    
    def generate_startup_script(self):
        """Generate startup script for A2A server"""
        script_content = f"""#!/bin/bash
# A2A Server Startup Script for Ops Mesh

echo "🏥 Starting Ops Mesh A2A Server..."

# Set environment variables
export GOOGLE_CLOUD_PROJECT="{self.project_id}"
export A2A_SERVER_MODE=true

# Start the A2A server
python setup_a2a.py --start

echo "✅ A2A Server started successfully!"
"""
        
        script_path = Path("ops-mesh-backend/start_a2a_server.sh")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        logger.info(f"📝 A2A startup script written to: {script_path}")
        return script_path


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="A2A Server Setup for Ops Mesh")
    parser.add_argument("--start", action="store_true", help="Start the A2A server")
    parser.add_argument("--setup", action="store_true", help="Set up A2A environment")
    parser.add_argument("--config", action="store_true", help="Generate A2A configuration")
    
    args = parser.parse_args()
    
    print("🏥 Ops Mesh A2A Server Setup")
    print("=" * 50)
    
    # Get project ID
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
        print("Please set GOOGLE_CLOUD_PROJECT in your .env file")
        return
    
    setup = A2AServerSetup(project_id)
    
    if args.setup or not any([args.start, args.config]):
        # Set up environment
        success = await setup.setup_environment()
        if not success:
            return
        
        # Generate configuration
        setup.generate_a2a_config()
        setup.generate_startup_script()
        
        print("✅ A2A environment setup completed!")
        print("📝 Configuration files generated")
        print("🚀 Run with --start to start the A2A server")
    
    if args.config:
        setup.generate_a2a_config()
        setup.generate_startup_script()
        print("✅ A2A configuration generated!")
    
    if args.start:
        print("🤖 Starting A2A server with agents:")
        for agent_name, config in setup.agents_config.items():
            if config["enabled"]:
                print(f"   • {agent_name} (port {config['port']})")
        print("=" * 50)
        
        await setup.start_a2a_server()


if __name__ == "__main__":
    asyncio.run(main())
