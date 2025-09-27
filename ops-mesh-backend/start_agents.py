#!/usr/bin/env python3
"""
Google ADK Agent System Startup Script

This script starts the complete Google ADK-based agent system for the hospital
operations management system.
"""

import asyncio
import os
import sys
import logging
from typing import Optional

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.google_adk_agents import start_agent_system, stop_agent_system


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('agent_system.log')
        ]
    )


def get_google_cloud_config() -> tuple[str, str]:
    """Get Google Cloud configuration from environment or user input."""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    region = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not project_id:
        print("❌ Google Cloud Project ID not found!")
        print("\n🔧 You need to set up Google Cloud configuration first.")
        print("Please run the setup script:")
        print("   python setup_google_adk.py")
        print("\nOr set the environment variables manually:")
        print("   export GOOGLE_CLOUD_PROJECT='your-project-id'")
        print("   export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service-account-key.json'")
        print("\nAlternatively, enter your project ID below:")
        project_id = input("Enter your Google Cloud Project ID: ").strip()
        
        if not project_id:
            print("❌ Project ID is required. Exiting.")
            sys.exit(1)
    
    if not credentials_path:
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS not set!")
        print("Please run: python setup_google_adk.py")
        print("Or set: export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service-account-key.json'")
        sys.exit(1)
    
    if not os.path.exists(credentials_path):
        print(f"❌ Service account key file not found: {credentials_path}")
        print("Please run: python setup_google_adk.py")
        sys.exit(1)
    
    return project_id, region


def check_requirements():
    """Check if all required dependencies are available."""
    try:
        import google.cloud.aiplatform
        import google.cloud.pubsub_v1
        import google.cloud.storage
        import google.cloud.logging
        import google.cloud.monitoring_v3
        print("✅ Google Cloud dependencies available")
    except ImportError as e:
        print(f"❌ Missing Google Cloud dependencies: {e}")
        print("Please install the required packages:")
        print("pip install google-cloud-aiplatform google-cloud-pubsub google-cloud-storage google-cloud-logging google-cloud-monitoring")
        sys.exit(1)
    
    try:
        import grpc
        import google.protobuf
        print("✅ gRPC and protobuf available")
    except ImportError as e:
        print(f"❌ Missing gRPC dependencies: {e}")
        print("Please install: pip install grpcio protobuf")
        sys.exit(1)


async def main():
    """Main function to start the agent system."""
    print("🚀 Starting Google ADK Agent System...")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Check requirements
    check_requirements()
    
    # Get Google Cloud configuration
    project_id, region = get_google_cloud_config()
    
    print(f"📋 Configuration:")
    print(f"   Project ID: {project_id}")
    print(f"   Region: {region}")
    print()
    
    # Start the agent system
    try:
        success = await start_agent_system(project_id, region)
        
        if success:
            print("🎉 Agent system started successfully!")
            print()
            print("📊 Available Agents:")
            print("   • Orchestrator Agent - System coordination and flow management")
            print("   • FrontDesk Agent - Tablet interface and patient check-in")
            print("   • Scheduling Agent - Appointment management (to be implemented)")
            print("   • Insurance Agent - Coverage verification (to be implemented)")
            print("   • Hospital Agent - Bed and resource management (to be implemented)")
            print("   • Queue Agent - Patient calling system (to be implemented)")
            print("   • Staff Agent - Resource coordination (to be implemented)")
            print()
            print("🔄 System is running. Press Ctrl+C to stop.")
            print("=" * 50)
            
            # Keep the system running
            try:
                while True:
                    await asyncio.sleep(30)
                    
                    # Print status every 30 seconds
                    from app.agents.google_adk_agents import get_agent_manager
                    agent_manager = get_agent_manager()
                    metrics = agent_manager.get_system_metrics()
                    print(f"📊 Status: {metrics['running_agents']}/{metrics['total_agents']} agents running, uptime: {metrics['uptime_minutes']:.1f} minutes")
                    
            except KeyboardInterrupt:
                print("\n🛑 Shutting down agent system...")
                await stop_agent_system()
                print("✅ Agent system stopped successfully")
        
        else:
            print("❌ Failed to start agent system")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error starting agent system: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Run the main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
