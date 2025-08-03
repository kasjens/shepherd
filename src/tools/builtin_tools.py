"""
Built-in tool registration and initialization.

This module registers all built-in tools with the global tool registry
and sets up default configurations.
"""

from .registry import tool_registry
from .execution_engine import execution_engine
from .core import CalculatorTool, WebSearchTool, FileOperationsTool
from .base_tool import ToolPermission


def register_builtin_tools():
    """Register all built-in tools with the global registry."""
    
    # Register calculator tool
    tool_registry.register_tool(
        CalculatorTool,
        permissions={ToolPermission.EXECUTE}
    )
    
    # Register web search tool  
    tool_registry.register_tool(
        WebSearchTool,
        permissions={ToolPermission.EXECUTE, ToolPermission.READ}
    )
    
    # Register file operations tool
    tool_registry.register_tool(
        FileOperationsTool,
        permissions={ToolPermission.READ, ToolPermission.WRITE, ToolPermission.EXECUTE}
    )
    
    # Set up rate limits for tools
    execution_engine.set_rate_limit("web_search", max_calls=10, window_seconds=60)
    execution_engine.set_rate_limit("file_operations", max_calls=20, window_seconds=60)
    
    print("Built-in tools registered successfully:")
    for tool_info in tool_registry.list_tools():
        print(f"  - {tool_info['name']}: {tool_info['description']}")


def get_tool_info_summary():
    """Get a summary of all registered tools."""
    tools = tool_registry.list_tools()
    
    summary = {
        "total_tools": len(tools),
        "categories": {},
        "tools": []
    }
    
    for tool_info in tools:
        category = tool_info["category"]
        if category not in summary["categories"]:
            summary["categories"][category] = 0
        summary["categories"][category] += 1
        
        # Get detailed info
        detailed_info = tool_registry.get_tool_info(tool_info["name"])
        if detailed_info:
            summary["tools"].append({
                "name": detailed_info["name"],
                "description": detailed_info["description"], 
                "category": detailed_info["category"],
                "parameters": len(detailed_info["parameters"]),
                "required_permissions": detailed_info["required_permissions"]
            })
    
    return summary


# Auto-register built-in tools when module is imported
register_builtin_tools()