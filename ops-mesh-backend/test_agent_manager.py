#!/usr/bin/env python3
"""
Test Agent Manager - Tests agent initialization and basic functionality
"""

import asyncio
import logging
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


async def test_agent_manager():
    """Test agent manager functionality"""
    logger.info("🤖 Testing Agent Manager...")
    
    try:
        # Test 1: Agent Manager Creation
        logger.info("📡 Test 1: Agent Manager Creation")
        manager = AgentManager("test-project")
        assert manager.project_id == "test-project", "Project ID incorrect"
        assert len(manager.agents) == 5, "Expected 5 agents"
        logger.info("✅ Agent Manager creation passed")
        
        # Test 2: Agent Initialization
        logger.info("🔧 Test 2: Agent Initialization")
        await manager.initialize_all_agents()
        logger.info("✅ Agent initialization passed")
        
        # Test 3: Agent Status
        logger.info("📊 Test 3: Agent Status")
        status = await manager.get_agent_status()
        assert len(status) == 5, "Expected status for 5 agents"
        logger.info("✅ Agent status check passed")
        
        # Test 4: Discovery Info
        logger.info("🔍 Test 4: Discovery Info")
        discovery_info = await manager.get_discovery_info()
        assert "discovery_stats" in discovery_info, "Discovery stats missing"
        assert "available_agents" in discovery_info, "Available agents missing"
        logger.info("✅ Discovery info check passed")
        
        # Cleanup
        await manager.stop_all_agents()
        
        logger.info("🎉 All agent manager tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


async def main():
    """Main function"""
    print("🤖 Agent Manager Test Suite")
    print("=" * 50)
    print("This test will verify agent manager functionality:")
    print("• Agent Manager creation")
    print("• Agent initialization")
    print("• Agent status monitoring")
    print("• Discovery service integration")
    print("=" * 50)
    print()
    
    success = await test_agent_manager()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Agent Manager is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())
