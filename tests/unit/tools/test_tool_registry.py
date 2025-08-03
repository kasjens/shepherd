"""
Unit tests for ToolRegistry.
"""

import pytest
from src.tools.registry import ToolRegistry
from src.tools.base_tool import BaseTool, ToolCategory, ToolParameter, ToolResult, ToolPermission


class MockTool(BaseTool):
    """Mock tool for testing."""
    
    @property
    def name(self) -> str:
        return "mock_tool"
    
    @property
    def description(self) -> str:
        return "A mock tool for testing"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.COMPUTATION
    
    @property
    def parameters(self) -> list:
        return [
            ToolParameter("test_param", "str", "Test parameter", True)
        ]
    
    async def execute(self, parameters):
        return ToolResult(success=True, data={"result": "mock_result"})


class TestToolRegistry:
    """Test cases for ToolRegistry."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ToolRegistry()
    
    def test_register_tool(self):
        """Test tool registration."""
        self.registry.register_tool(MockTool)
        
        # Check tool is registered
        assert "mock_tool" in self.registry._tools
        assert "mock_tool" in self.registry._categories[ToolCategory.COMPUTATION]
        
        # Check tool can be retrieved
        tool = self.registry.get_tool("mock_tool")
        assert tool is not None
        assert tool.name == "mock_tool"
    
    def test_register_duplicate_tool(self):
        """Test registering a tool with same name."""
        self.registry.register_tool(MockTool)
        self.registry.register_tool(MockTool)  # Should overwrite
        
        # Should still have only one registration
        tools = self.registry.get_all_tools()
        mock_tools = [t for t in tools if t.name == "mock_tool"]
        assert len(mock_tools) == 1
    
    def test_unregister_tool(self):
        """Test tool unregistration."""
        self.registry.register_tool(MockTool)
        
        # Verify registered
        assert self.registry.get_tool("mock_tool") is not None
        
        # Unregister
        result = self.registry.unregister_tool("mock_tool")
        assert result is True
        
        # Verify unregistered
        assert self.registry.get_tool("mock_tool") is None
        
        # Try to unregister non-existent tool
        result = self.registry.unregister_tool("non_existent")
        assert result is False
    
    def test_get_tools_by_category(self):
        """Test getting tools by category."""
        self.registry.register_tool(MockTool)
        
        computation_tools = self.registry.get_tools_by_category(ToolCategory.COMPUTATION)
        assert len(computation_tools) == 1
        assert computation_tools[0].name == "mock_tool"
        
        # Test empty category
        info_tools = self.registry.get_tools_by_category(ToolCategory.INFORMATION)
        assert len(info_tools) == 0
    
    def test_permission_checking(self):
        """Test permission-based tool access."""
        permissions = {ToolPermission.EXECUTE}
        self.registry.register_tool(MockTool, permissions)
        
        # Should be accessible with execute permission
        can_access = self.registry.check_tool_permission(
            "mock_tool", 
            {ToolPermission.EXECUTE}
        )
        assert can_access is True
        
        # Should not be accessible without permission
        can_access = self.registry.check_tool_permission(
            "mock_tool", 
            {ToolPermission.READ}
        )
        assert can_access is False
        
        # Should be accessible with superset of permissions
        can_access = self.registry.check_tool_permission(
            "mock_tool", 
            {ToolPermission.EXECUTE, ToolPermission.READ}
        )
        assert can_access is True
    
    def test_get_tools_for_permissions(self):
        """Test getting tools filtered by permissions."""
        self.registry.register_tool(
            MockTool, 
            {ToolPermission.EXECUTE}
        )
        
        # With execute permission
        tools = self.registry.get_tools_for_permissions({ToolPermission.EXECUTE})
        assert len(tools) == 1
        assert tools[0].name == "mock_tool"
        
        # Without execute permission
        tools = self.registry.get_tools_for_permissions({ToolPermission.READ})
        assert len(tools) == 0
    
    def test_enable_disable_tool(self):
        """Test enabling and disabling tools."""
        self.registry.register_tool(MockTool)
        
        # Initially enabled
        tool = self.registry.get_tool("mock_tool")
        assert tool is not None
        
        # Disable
        result = self.registry.disable_tool("mock_tool")
        assert result is True
        
        # Should not be available when disabled
        tool = self.registry.get_tool("mock_tool")
        assert tool is None
        
        # Re-enable
        result = self.registry.enable_tool("mock_tool")
        assert result is True
        
        # Should be available again
        tool = self.registry.get_tool("mock_tool")
        assert tool is not None
    
    def test_get_tool_info(self):
        """Test getting detailed tool information."""
        self.registry.register_tool(MockTool)
        
        info = self.registry.get_tool_info("mock_tool")
        assert info is not None
        assert info["name"] == "mock_tool"
        assert info["description"] == "A mock tool for testing"
        assert info["category"] == "computation"
        assert info["enabled"] is True
        assert "parameters" in info
        assert "registered_at" in info
        
        # Non-existent tool
        info = self.registry.get_tool_info("non_existent")
        assert info is None
    
    def test_list_tools(self):
        """Test listing all tools."""
        self.registry.register_tool(MockTool)
        
        tools = self.registry.list_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "mock_tool"
        assert tools[0]["enabled"] is True
    
    def test_search_tools(self):
        """Test searching tools by name/description."""
        self.registry.register_tool(MockTool)
        
        # Search by name
        results = self.registry.search_tools("mock")
        assert len(results) == 1
        assert results[0].name == "mock_tool"
        
        # Search by description
        results = self.registry.search_tools("testing")
        assert len(results) == 1
        
        # No matches
        results = self.registry.search_tools("nonexistent")
        assert len(results) == 0
        
        # Case insensitive
        results = self.registry.search_tools("MOCK")
        assert len(results) == 1