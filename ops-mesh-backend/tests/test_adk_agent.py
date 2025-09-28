"""
Tests for the Google ADK Agent system.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.agent.simple_root_agent import (
    SimpleOpsMeshTool,
    SimplePatientFlowTool,
    SimpleSystemStatusTool,
    simple_root_agent
)


class TestSimpleOpsMeshTool:
    """Test the SimpleOpsMeshTool."""

    @pytest.mark.asyncio
    async def test_get_dashboard_stats(self):
        """Test getting system info (dashboard stats)."""
        tool = SimpleOpsMeshTool()
        result = await tool.execute({"operation": "get_system_info"})
        
        assert result["success"] is True
        assert "data" in result
        assert "system_name" in result["data"]
        assert "status" in result["data"]
        assert "components" in result["data"]

    @pytest.mark.asyncio
    async def test_get_queue_entries(self):
        """Test getting queue status."""
        tool = SimpleOpsMeshTool()
        result = await tool.execute({"operation": "get_queue_status"})
        
        assert result["success"] is True
        assert "data" in result
        assert "total_waiting" in result["data"]
        assert "estimated_wait_time" in result["data"]

    @pytest.mark.asyncio
    async def test_get_appointments(self):
        """Test getting appointments."""
        tool = SimpleOpsMeshTool()
        result = await tool.execute({"operation": "get_appointments"})
        
        assert result["success"] is True
        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

    @pytest.mark.asyncio
    async def test_unknown_operation(self):
        """Test unknown operation."""
        tool = SimpleOpsMeshTool()
        result = await tool.execute({"operation": "unknown_operation"})
        
        assert result["success"] is False
        assert "error" in result
        assert "Unknown operation" in result["error"]

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """Test exception handling."""
        tool = SimpleOpsMeshTool()
        # Test actual exception handling in the tool
        result = await tool.execute({"operation": "invalid_operation"})
        assert result["success"] is False
        assert "error" in result


class TestSimplePatientFlowTool:
    """Test the SimplePatientFlowTool."""

    @pytest.mark.asyncio
    async def test_check_in(self):
        """Test patient check-in."""
        tool = SimplePatientFlowTool()
        result = await tool.execute({
            "action": "check_in_patient",
            "patient_data": {"patient_id": 123}
        })
        
        assert result["success"] is True
        assert "message" in result
        assert "checked in" in result["message"]

    @pytest.mark.asyncio
    async def test_call_next_patient(self):
        """Test calling next patient."""
        tool = SimplePatientFlowTool()
        result = await tool.execute({"action": "call_next_patient"})
        
        assert result["success"] is True
        assert "message" in result
        assert "called" in result["message"]

    @pytest.mark.asyncio
    async def test_unknown_action(self):
        """Test unknown action."""
        tool = SimplePatientFlowTool()
        result = await tool.execute({"action": "unknown_action"})
        
        assert result["success"] is False
        assert "error" in result
        assert "Unknown action" in result["error"]


class TestSimpleSystemStatusTool:
    """Test the SimpleSystemStatusTool."""

    @pytest.mark.asyncio
    async def test_check_all_components(self):
        """Test checking all system components."""
        tool = SimpleSystemStatusTool()
        result = await tool.execute({"component": "all"})
        
        assert result["success"] is True
        assert "data" in result
        # Check for actual keys returned by the tool
        assert "backend_api" in result["data"] or "api_server" in result["data"]
        assert "database" in result["data"]
        assert "agents" in result["data"] or "adk_agents" in result["data"]

    @pytest.mark.asyncio
    async def test_check_specific_component(self):
        """Test checking specific component."""
        tool = SimpleSystemStatusTool()
        result = await tool.execute({"component": "api_server"})
        
        assert result["success"] is True
        assert "data" in result
        # The tool returns different structure for specific components
        assert "api_server" in result["data"] or "component" in result["data"]

    @pytest.mark.asyncio
    async def test_unknown_component(self):
        """Test unknown component."""
        tool = SimpleSystemStatusTool()
        result = await tool.execute({"component": "unknown_component"})
        
        assert result["success"] is True
        assert "data" in result
        # The tool returns the component name as key
        assert "unknown_component" in result["data"]
        assert result["data"]["unknown_component"] == "unknown"


class TestSimpleRootAgent:
    """Test the simple root agent."""

    def test_agent_initialization(self):
        """Test that the agent initializes correctly."""
        assert simple_root_agent is not None
        assert simple_root_agent.name == "simple_ops_mesh_root_agent"
        assert simple_root_agent.model == "gemini-1.5-flash"
        assert len(simple_root_agent.tools) == 3

    def test_agent_tools(self):
        """Test that all required tools are present."""
        tool_names = [tool.name for tool in simple_root_agent.tools]
        assert "simple_ops_mesh_tool" in tool_names
        assert "simple_patient_flow_tool" in tool_names
        assert "simple_system_status_tool" in tool_names

    def test_agent_instruction(self):
        """Test that the agent has proper instructions."""
        assert simple_root_agent.instruction is not None
        assert "Ops Mesh" in simple_root_agent.instruction
        assert "hospital operations" in simple_root_agent.instruction
