"""
Basic integration tests for tool system.
"""

import pytest
import asyncio
from src.agents.base_agent import BaseAgent
from src.tools.registry import tool_registry
from src.tools.builtin_tools import register_builtin_tools
from src.tools.base_tool import ToolPermission


class SimpleTestAgent(BaseAgent):
    """Simple test agent implementation."""
    
    def create_crew_agent(self):
        """Create a mock CrewAI agent."""
        return None


def test_tool_registration():
    """Test that tools are registered properly."""
    # Clear and re-register tools
    tool_registry._tools.clear()
    tool_registry._permissions.clear()
    
    from src.tools.base_tool import ToolCategory
    tool_registry._categories = {
        category: set() for category in ToolCategory
    }
    
    register_builtin_tools()
    
    # Check tools are registered
    tools = tool_registry.list_tools()
    tool_names = [tool["name"] for tool in tools]
    
    assert "calculator" in tool_names
    assert "web_search" in tool_names
    assert "file_operations" in tool_names


@pytest.mark.asyncio
async def test_agent_calculator_integration():
    """Test agent executing calculator tool."""
    agent = SimpleTestAgent("calc_agent", "calculator", "Do math")
    
    # Execute calculator
    result = await agent.execute_tool("calculator", {"expression": "2 + 2"})
    
    assert result.success is True
    assert result.data["result"] == 4.0


@pytest.mark.asyncio
async def test_agent_web_search_integration():
    """Test agent executing web search tool."""
    agent = SimpleTestAgent("search_agent", "researcher", "Find info")
    
    # Execute search
    result = await agent.execute_tool("web_search", {
        "query": "test query",
        "max_results": 2
    })
    
    assert result.success is True
    assert "results" in result.data
    assert len(result.data["results"]) <= 2


def test_agent_available_tools():
    """Test that agents can list available tools."""
    agent = SimpleTestAgent("test_agent", "tester", "Test things")
    
    available_tools = agent.get_available_tools()
    tool_names = [tool["name"] for tool in available_tools]
    
    assert "calculator" in tool_names
    assert "web_search" in tool_names


def test_agent_tool_permissions():
    """Test agent tool permission system."""
    agent = SimpleTestAgent("perm_agent", "security", "Check permissions")
    
    # Should have basic permissions
    assert ToolPermission.READ in agent.available_permissions
    assert ToolPermission.EXECUTE in agent.available_permissions
    
    # Should be able to access basic tools
    assert agent.validate_tool_access("calculator") is True
    assert agent.validate_tool_access("web_search") is True