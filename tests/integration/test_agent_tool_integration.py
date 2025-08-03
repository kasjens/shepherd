"""
Integration tests for agent-tool system.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path

from src.agents.base_agent import BaseAgent
from src.tools.registry import tool_registry
from src.tools.builtin_tools import register_builtin_tools
from src.tools.base_tool import ToolPermission
from src.memory.local_memory import AgentLocalMemory
from src.memory.shared_context import SharedContextPool


class MockAgent(BaseAgent):
    """Test agent implementation."""
    
    def create_crew_agent(self):
        """Create a mock CrewAI agent."""
        return None  # Mock implementation


class MockAgentToolIntegration:
    """Integration tests for agent-tool system."""
    
    @pytest.fixture(autouse=True)
    def setup_tools(self):
        """Set up tools before each test."""
        # Clear existing registrations
        tool_registry._tools.clear()
        tool_registry._permissions.clear()
        
        # Reinitialize categories
        from src.tools.base_tool import ToolCategory
        tool_registry._categories = {
            category: set() for category in ToolCategory
        }
        
        # Re-register built-in tools
        register_builtin_tools()
    
    @pytest.fixture
    def temp_project_folder(self):
        """Create a temporary project folder for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Hello, World!")
            
            config_file = Path(temp_dir) / "config.json"
            config_file.write_text('{"key": "value"}')
            
            yield temp_dir
    
    def test_agent_tool_initialization(self):
        """Test that agents initialize tool system correctly."""
        agent = MockAgent("test_agent", "tester", "Test things")
        
        # Check tool permissions
        assert ToolPermission.READ in agent.available_permissions
        assert ToolPermission.EXECUTE in agent.available_permissions
        
        # Check available tools
        available_tools = agent.get_available_tools()
        tool_names = [tool["name"] for tool in available_tools]
        
        assert "calculator" in tool_names
        assert "web_search" in tool_names
        assert "file_operations" in tool_names
    
    @pytest.mark.asyncio
    async def test_calculator_tool_execution(self):
        """Test executing calculator tool through agent."""
        agent = MockAgent("calc_agent", "calculator", "Do math")
        
        # Execute simple calculation
        result = await agent.execute_tool("calculator", {"expression": "2 + 2"})
        
        assert result.success is True
        assert result.data["result"] == 4.0
        assert result.execution_time > 0
        
        # Check that execution was stored in memory
        memory_entries = await agent.local_memory.retrieve_all()
        tool_executions = [
            entry for entry in memory_entries 
            if entry.get("metadata", {}).get("type") == "tool_execution"
        ]
        assert len(tool_executions) > 0
    
    @pytest.mark.asyncio
    async def test_web_search_tool_execution(self):
        """Test executing web search tool through agent."""
        agent = MockAgent("search_agent", "researcher", "Find information")
        
        # Execute search
        result = await agent.execute_tool("web_search", {
            "query": "artificial intelligence",
            "max_results": 3
        })
        
        assert result.success is True
        assert "results" in result.data
        assert len(result.data["results"]) <= 3
        assert result.data["query"] == "artificial intelligence"
    
    @pytest.mark.asyncio
    async def test_file_operations_tool(self, temp_project_folder):
        """Test file operations tool through agent."""
        agent = MockAgent("file_agent", "file_manager", "Manage files")
        agent.set_project_folder(temp_project_folder)
        
        # Add write permission for file operations
        agent.add_tool_permission(ToolPermission.WRITE)
        
        # Test reading a file
        result = await agent.execute_tool("file_operations", {
            "operation": "read",
            "path": "test.txt"
        })
        
        assert result.success is True
        assert result.data["content"] == "Hello, World!"
        
        # Test writing a file
        result = await agent.execute_tool("file_operations", {
            "operation": "write",
            "path": "new_file.txt",
            "content": "This is new content"
        })
        
        assert result.success is True
        
        # Verify file was created
        new_file_path = Path(temp_project_folder) / "new_file.txt"
        assert new_file_path.exists()
        assert new_file_path.read_text() == "This is new content"
        
        # Test listing directory
        result = await agent.execute_tool("file_operations", {
            "operation": "list",
            "path": "."
        })
        
        assert result.success is True
        assert result.data["count"] >= 3  # test.txt, config.json, new_file.txt
        
        file_names = [item["name"] for item in result.data["items"]]
        assert "test.txt" in file_names
        assert "config.json" in file_names
        assert "new_file.txt" in file_names
    
    @pytest.mark.asyncio
    async def test_permission_enforcement(self, temp_project_folder):
        """Test that tool permissions are enforced."""
        agent = MockAgent("restricted_agent", "restricted", "Limited access")
        agent.set_project_folder(temp_project_folder)
        
        # Remove write permission
        agent.remove_tool_permission(ToolPermission.WRITE)
        
        # Try to write a file (should fail)
        result = await agent.execute_tool("file_operations", {
            "operation": "write",
            "path": "should_fail.txt",
            "content": "This should not work"
        })
        
        assert result.success is False
        assert "permission denied" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_tool_selection_for_task(self):
        """Test automatic tool selection for tasks."""
        agent = MockAgent("smart_agent", "assistant", "Help with tasks")
        
        # Test math task
        tools = await agent.select_tools_for_task("Calculate the area of a circle")
        assert "calculator" in tools
        
        # Test file task
        tools = await agent.select_tools_for_task("Read the configuration file")
        assert "file_operations" in tools
        
        # Test search task
        tools = await agent.select_tools_for_task("Find information about Python")
        assert "web_search" in tools
    
    @pytest.mark.asyncio
    async def test_tool_usage_statistics(self):
        """Test tool usage statistics tracking."""
        agent = MockAgent("stats_agent", "analyst", "Track usage")
        
        # Execute some tools
        await agent.execute_tool("calculator", {"expression": "1 + 1"})
        await agent.execute_tool("calculator", {"expression": "2 * 2"})
        await agent.execute_tool("web_search", {"query": "test"})
        
        # Get statistics
        stats = await agent.get_tool_usage_statistics()
        
        assert stats["total_executions"] == 3
        assert stats["successful_executions"] == 3
        assert stats["success_rate"] == 1.0
        assert "calculator" in stats["tools_used"]
        assert "web_search" in stats["tools_used"]
        assert stats["tools_used"]["calculator"]["total"] == 2
        assert stats["tools_used"]["web_search"]["total"] == 1
    
    def test_tool_access_validation(self):
        """Test tool access validation."""
        agent = MockAgent("validator_agent", "validator", "Validate access")
        
        # Should have access to tools with read/execute permissions
        assert agent.validate_tool_access("calculator") is True
        assert agent.validate_tool_access("web_search") is True
        
        # File operations requires write permission which base agents don't have by default
        # But they can still access it if they have read/execute
        assert agent.validate_tool_access("file_operations") is True
        
        # Non-existent tool
        assert agent.validate_tool_access("non_existent_tool") is False
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self):
        """Test concurrent tool execution by multiple agents."""
        agents = [
            MockAgent(f"agent_{i}", "worker", f"Worker {i}")
            for i in range(3)
        ]
        
        # Execute tools concurrently
        tasks = []
        for i, agent in enumerate(agents):
            task = agent.execute_tool("calculator", {"expression": f"{i} + {i}"})
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        for i, result in enumerate(results):
            assert result.success is True
            assert result.data["result"] == float(i + i)
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test tool error handling and recovery."""
        agent = MockAgent("error_agent", "error_handler", "Handle errors")
        
        # Test calculator with invalid expression
        result = await agent.execute_tool("calculator", {"expression": "invalid"})
        assert result.success is False
        assert result.error is not None
        
        # Test file operations with invalid path
        result = await agent.execute_tool("file_operations", {
            "operation": "read",
            "path": "/nonexistent/path/file.txt"
        })
        assert result.success is False
        assert result.error is not None
        
        # Agent should still be functional after errors
        result = await agent.execute_tool("calculator", {"expression": "2 + 2"})
        assert result.success is True