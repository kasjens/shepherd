"""
Tool system for Shepherd agents.

This package provides the infrastructure for tools that extend agent capabilities
beyond their base LLM functionality.
"""

from .base_tool import BaseTool, ToolCategory, ToolPermission, ToolParameter, ToolResult
from .registry import ToolRegistry, tool_registry
from .execution_engine import ToolExecutionEngine, ExecutionContext, execution_engine

__all__ = [
    # Base classes
    "BaseTool",
    "ToolCategory",
    "ToolPermission",
    "ToolParameter",
    "ToolResult",
    
    # Registry
    "ToolRegistry",
    "tool_registry",
    
    # Execution
    "ToolExecutionEngine",
    "ExecutionContext",
    "execution_engine",
]