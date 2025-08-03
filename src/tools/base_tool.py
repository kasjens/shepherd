"""
Base tool interface for all tools in Shepherd.

This module defines the abstract base class that all tools must implement,
providing a consistent interface for tool discovery, execution, and validation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import asyncio
from datetime import datetime


class ToolCategory(Enum):
    """Categories for organizing tools."""
    COMPUTATION = "computation"
    INFORMATION = "information"
    FILE_SYSTEM = "file_system"
    CODE_EXECUTION = "code_execution"
    COMMUNICATION = "communication"
    DATA_PROCESSING = "data_processing"
    SYSTEM = "system"


class ToolPermission(Enum):
    """Permission levels for tool access."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    validation: Optional[str] = None  # Regex or validation rule


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    Tools provide external capabilities to agents, enabling them to interact
    with systems, perform computations, and access information beyond their
    base LLM capabilities.
    """
    
    def __init__(self):
        self.execution_count = 0
        self.total_execution_time = 0.0
        self.last_execution = None
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifier for the tool."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the tool does."""
        pass
    
    @property
    @abstractmethod
    def category(self) -> ToolCategory:
        """Category this tool belongs to."""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """List of parameters this tool accepts."""
        pass
    
    @property
    def required_permissions(self) -> List[ToolPermission]:
        """Permissions required to use this tool."""
        return [ToolPermission.EXECUTE]
    
    @property
    def usage_examples(self) -> List[Dict[str, Any]]:
        """Examples of how to use this tool."""
        return []
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Union[bool, str]:
        """
        Validate input parameters before execution.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if valid, error message string if invalid
        """
        # Check required parameters
        for param in self.parameters:
            if param.required and param.name not in parameters:
                return f"Missing required parameter: {param.name}"
        
        # Check parameter types (basic validation)
        for param in self.parameters:
            if param.name in parameters:
                value = parameters[param.name]
                expected_type = param.type
                
                # Basic type checking
                if expected_type == "str" and not isinstance(value, str):
                    return f"Parameter {param.name} must be a string"
                elif expected_type == "int" and not isinstance(value, int):
                    return f"Parameter {param.name} must be an integer"
                elif expected_type == "float" and not isinstance(value, (int, float)):
                    return f"Parameter {param.name} must be a number"
                elif expected_type == "bool" and not isinstance(value, bool):
                    return f"Parameter {param.name} must be a boolean"
                elif expected_type == "list" and not isinstance(value, list):
                    return f"Parameter {param.name} must be a list"
                elif expected_type == "dict" and not isinstance(value, dict):
                    return f"Parameter {param.name} must be a dictionary"
        
        return True
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with given parameters.
        
        Args:
            parameters: Parameters for tool execution
            
        Returns:
            ToolResult containing execution outcome
        """
        pass
    
    async def safe_execute(self, parameters: Dict[str, Any], 
                          timeout: int = 30) -> ToolResult:
        """
        Execute tool with timeout and error handling.
        
        Args:
            parameters: Parameters for tool execution
            timeout: Maximum execution time in seconds
            
        Returns:
            ToolResult with execution outcome or error
        """
        start_time = datetime.now()
        
        # Validate parameters
        validation = self.validate_parameters(parameters)
        if validation is not True:
            return ToolResult(
                success=False,
                data=None,
                error=validation,
                execution_time=0.0
            )
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self.execute(parameters),
                timeout=timeout
            )
            
            # Update statistics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.execution_count += 1
            self.total_execution_time += execution_time
            self.last_execution = datetime.now()
            
            # Ensure execution time is set
            if result.execution_time == 0.0:
                result.execution_time = execution_time
            
            return result
            
        except asyncio.TimeoutError:
            return ToolResult(
                success=False,
                data=None,
                error=f"Tool execution timed out after {timeout} seconds",
                execution_time=(datetime.now() - start_time).total_seconds()
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Tool execution failed: {str(e)}",
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics for this tool."""
        return {
            "name": self.name,
            "execution_count": self.execution_count,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": (
                self.total_execution_time / self.execution_count
                if self.execution_count > 0 else 0
            ),
            "last_execution": self.last_execution.isoformat() if self.last_execution else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool definition to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default
                }
                for p in self.parameters
            ],
            "required_permissions": [p.value for p in self.required_permissions],
            "usage_examples": self.usage_examples
        }