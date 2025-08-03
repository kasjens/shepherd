"""
Tool registry for managing and discovering available tools.

This module provides a centralized registry for tool registration, discovery,
and permission management.
"""

from typing import Dict, List, Optional, Set, Type
from dataclasses import dataclass
from datetime import datetime
import logging

from .base_tool import BaseTool, ToolCategory, ToolPermission


@dataclass
class ToolRegistration:
    """Registration information for a tool."""
    tool_class: Type[BaseTool]
    instance: Optional[BaseTool] = None
    registered_at: datetime = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.registered_at is None:
            self.registered_at = datetime.now()


class ToolRegistry:
    """
    Central registry for managing tools.
    
    Provides functionality for:
    - Tool registration and discovery
    - Permission management
    - Category-based organization
    - Tool lifecycle management
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolRegistration] = {}
        self._categories: Dict[ToolCategory, Set[str]] = {
            category: set() for category in ToolCategory
        }
        self._permissions: Dict[str, Set[ToolPermission]] = {}
        self._logger = logging.getLogger(__name__)
        
    def register_tool(self, tool_class: Type[BaseTool], 
                     permissions: Optional[Set[ToolPermission]] = None) -> None:
        """
        Register a tool in the registry.
        
        Args:
            tool_class: Tool class to register
            permissions: Optional override of default permissions
        """
        # Create instance to get properties
        instance = tool_class()
        tool_name = instance.name
        
        if tool_name in self._tools:
            self._logger.warning(f"Tool {tool_name} already registered, overwriting")
        
        # Register tool
        registration = ToolRegistration(
            tool_class=tool_class,
            instance=instance
        )
        self._tools[tool_name] = registration
        
        # Register in category
        self._categories[instance.category].add(tool_name)
        
        # Set permissions
        if permissions is None:
            permissions = set(instance.required_permissions)
        self._permissions[tool_name] = permissions
        
        self._logger.info(f"Registered tool: {tool_name} in category {instance.category.value}")
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool from the registry.
        
        Args:
            tool_name: Name of tool to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        if tool_name not in self._tools:
            return False
        
        registration = self._tools[tool_name]
        category = registration.instance.category
        
        # Remove from registry
        del self._tools[tool_name]
        self._categories[category].discard(tool_name)
        if tool_name in self._permissions:
            del self._permissions[tool_name]
        
        self._logger.info(f"Unregistered tool: {tool_name}")
        return True
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a tool instance by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool instance if found and enabled, None otherwise
        """
        if tool_name not in self._tools:
            return None
        
        registration = self._tools[tool_name]
        if not registration.enabled:
            return None
        
        # Create new instance for thread safety
        return registration.tool_class()
    
    def get_tools_by_category(self, category: ToolCategory) -> List[BaseTool]:
        """
        Get all tools in a specific category.
        
        Args:
            category: Tool category
            
        Returns:
            List of tool instances in the category
        """
        tools = []
        for tool_name in self._categories.get(category, set()):
            tool = self.get_tool(tool_name)
            if tool:
                tools.append(tool)
        return tools
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all enabled tools."""
        tools = []
        for tool_name, registration in self._tools.items():
            if registration.enabled:
                tools.append(registration.tool_class())
        return tools
    
    def get_tools_for_permissions(self, 
                                 available_permissions: Set[ToolPermission]) -> List[BaseTool]:
        """
        Get tools that can be used with given permissions.
        
        Args:
            available_permissions: Set of available permissions
            
        Returns:
            List of tools that can be used
        """
        tools = []
        for tool_name, required_permissions in self._permissions.items():
            if required_permissions.issubset(available_permissions):
                tool = self.get_tool(tool_name)
                if tool:
                    tools.append(tool)
        return tools
    
    def check_tool_permission(self, tool_name: str, 
                            available_permissions: Set[ToolPermission]) -> bool:
        """
        Check if given permissions allow tool usage.
        
        Args:
            tool_name: Name of the tool
            available_permissions: Available permissions
            
        Returns:
            True if tool can be used, False otherwise
        """
        if tool_name not in self._permissions:
            return False
        
        required = self._permissions[tool_name]
        return required.issubset(available_permissions)
    
    def enable_tool(self, tool_name: str) -> bool:
        """Enable a tool."""
        if tool_name in self._tools:
            self._tools[tool_name].enabled = True
            self._logger.info(f"Enabled tool: {tool_name}")
            return True
        return False
    
    def disable_tool(self, tool_name: str) -> bool:
        """Disable a tool."""
        if tool_name in self._tools:
            self._tools[tool_name].enabled = False
            self._logger.info(f"Disabled tool: {tool_name}")
            return True
        return False
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """
        Get detailed information about a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool information dictionary or None
        """
        if tool_name not in self._tools:
            return None
        
        registration = self._tools[tool_name]
        tool = registration.instance
        
        return {
            "name": tool.name,
            "description": tool.description,
            "category": tool.category.value,
            "enabled": registration.enabled,
            "registered_at": registration.registered_at.isoformat(),
            "required_permissions": [p.value for p in self._permissions.get(tool_name, set())],
            "parameters": tool.to_dict()["parameters"],
            "usage_examples": tool.usage_examples,
            "statistics": tool.get_statistics()
        }
    
    def list_tools(self) -> List[Dict]:
        """List all registered tools with basic info."""
        tools = []
        for tool_name, registration in self._tools.items():
            tool = registration.instance
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.value,
                "enabled": registration.enabled
            })
        return tools
    
    def search_tools(self, query: str) -> List[BaseTool]:
        """
        Search for tools by name or description.
        
        Args:
            query: Search query (case-insensitive)
            
        Returns:
            List of matching tools
        """
        query_lower = query.lower()
        matches = []
        
        for registration in self._tools.values():
            if not registration.enabled:
                continue
                
            tool = registration.instance
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower()):
                matches.append(registration.tool_class())
        
        return matches


# Global registry instance
tool_registry = ToolRegistry()