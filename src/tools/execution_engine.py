"""
Tool execution engine with monitoring and safety controls.

This module provides the execution infrastructure for tools, including
monitoring, timeout handling, resource limits, and execution history.
"""

import asyncio
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import logging
import traceback

from .base_tool import BaseTool, ToolResult, ToolPermission
from .registry import tool_registry
from ..utils.logger import get_logger


@dataclass
class ExecutionContext:
    """Context for tool execution."""
    agent_id: str
    agent_name: str
    conversation_id: str
    workflow_id: Optional[str] = None
    permissions: Set[ToolPermission] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionRecord:
    """Record of a tool execution."""
    tool_name: str
    parameters: Dict[str, Any]
    context: ExecutionContext
    result: ToolResult
    started_at: datetime
    completed_at: datetime
    
    @property
    def duration(self) -> float:
        """Execution duration in seconds."""
        return (self.completed_at - self.started_at).total_seconds()


class ToolExecutionEngine:
    """
    Engine for executing tools with monitoring and safety controls.
    
    Features:
    - Permission validation
    - Execution monitoring
    - Timeout handling
    - Rate limiting
    - Execution history
    - Performance tracking
    """
    
    def __init__(self, 
                 default_timeout: int = 30,
                 max_concurrent_executions: int = 10,
                 history_size: int = 1000):
        """
        Initialize execution engine.
        
        Args:
            default_timeout: Default timeout in seconds
            max_concurrent_executions: Maximum concurrent tool executions
            history_size: Number of execution records to keep
        """
        self.default_timeout = default_timeout
        self.max_concurrent = max_concurrent_executions
        self.history_size = history_size
        
        # Execution tracking
        self._execution_history: deque = deque(maxlen=history_size)
        self._active_executions: Dict[str, asyncio.Task] = {}
        self._execution_semaphore = asyncio.Semaphore(max_concurrent_executions)
        
        # Statistics
        self._total_executions = 0
        self._successful_executions = 0
        self._failed_executions = 0
        self._total_execution_time = 0.0
        
        # Rate limiting (tool_name -> list of timestamps)
        self._rate_limit_window: Dict[str, deque] = {}
        self._rate_limits: Dict[str, tuple] = {}  # tool_name -> (max_calls, window_seconds)
        
        self.logger = get_logger(__name__)
    
    async def execute_tool(self,
                          tool_name: str,
                          parameters: Dict[str, Any],
                          context: ExecutionContext,
                          timeout: Optional[int] = None) -> ToolResult:
        """
        Execute a tool with full monitoring and safety controls.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            context: Execution context
            timeout: Optional timeout override
            
        Returns:
            ToolResult from execution
        """
        started_at = datetime.now()
        
        # Check permissions
        if not tool_registry.check_tool_permission(tool_name, context.permissions):
            self.logger.warning(
                f"Permission denied for tool {tool_name} "
                f"(agent: {context.agent_name})"
            )
            return ToolResult(
                success=False,
                data=None,
                error=f"Permission denied for tool: {tool_name}"
            )
        
        # Check rate limits
        if not self._check_rate_limit(tool_name):
            return ToolResult(
                success=False,
                data=None,
                error=f"Rate limit exceeded for tool: {tool_name}"
            )
        
        # Get tool instance
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                data=None,
                error=f"Tool not found: {tool_name}"
            )
        
        # Execute with monitoring
        execution_id = f"{context.agent_id}_{tool_name}_{started_at.timestamp()}"
        
        try:
            async with self._execution_semaphore:
                self.logger.info(
                    f"Executing tool {tool_name} for agent {context.agent_name} "
                    f"(conversation: {context.conversation_id})"
                )
                
                # Create execution task
                execution_task = asyncio.create_task(
                    self._monitored_execution(
                        tool, parameters, timeout or self.default_timeout
                    )
                )
                
                # Track active execution
                self._active_executions[execution_id] = execution_task
                
                try:
                    # Wait for execution
                    result = await execution_task
                    
                    # Update statistics
                    self._total_executions += 1
                    if result.success:
                        self._successful_executions += 1
                    else:
                        self._failed_executions += 1
                    
                    completed_at = datetime.now()
                    execution_time = (completed_at - started_at).total_seconds()
                    self._total_execution_time += execution_time
                    
                    # Record execution
                    record = ExecutionRecord(
                        tool_name=tool_name,
                        parameters=parameters,
                        context=context,
                        result=result,
                        started_at=started_at,
                        completed_at=completed_at
                    )
                    self._execution_history.append(record)
                    
                    # Log result
                    if result.success:
                        self.logger.info(
                            f"Tool {tool_name} executed successfully in {execution_time:.2f}s"
                        )
                    else:
                        self.logger.error(
                            f"Tool {tool_name} failed: {result.error}"
                        )
                    
                    return result
                    
                finally:
                    # Clean up tracking
                    self._active_executions.pop(execution_id, None)
                    
        except Exception as e:
            self.logger.error(
                f"Unexpected error executing tool {tool_name}: {str(e)}\n"
                f"{traceback.format_exc()}"
            )
            return ToolResult(
                success=False,
                data=None,
                error=f"Unexpected error: {str(e)}"
            )
    
    async def _monitored_execution(self, 
                                 tool: BaseTool,
                                 parameters: Dict[str, Any],
                                 timeout: int) -> ToolResult:
        """Execute tool with monitoring."""
        try:
            # Use tool's safe_execute method
            result = await tool.safe_execute(parameters, timeout)
            return result
        except Exception as e:
            # This should rarely happen due to safe_execute
            return ToolResult(
                success=False,
                data=None,
                error=f"Execution error: {str(e)}"
            )
    
    def set_rate_limit(self, tool_name: str, max_calls: int, 
                      window_seconds: int) -> None:
        """
        Set rate limit for a tool.
        
        Args:
            tool_name: Name of the tool
            max_calls: Maximum calls allowed
            window_seconds: Time window in seconds
        """
        self._rate_limits[tool_name] = (max_calls, window_seconds)
        if tool_name not in self._rate_limit_window:
            self._rate_limit_window[tool_name] = deque()
    
    def _check_rate_limit(self, tool_name: str) -> bool:
        """Check if tool execution is within rate limits."""
        if tool_name not in self._rate_limits:
            return True
        
        max_calls, window_seconds = self._rate_limits[tool_name]
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)
        
        # Clean old entries
        window = self._rate_limit_window[tool_name]
        while window and window[0] < cutoff:
            window.popleft()
        
        # Check limit
        if len(window) >= max_calls:
            return False
        
        # Record this call
        window.append(now)
        return True
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel an active execution.
        
        Args:
            execution_id: ID of execution to cancel
            
        Returns:
            True if cancelled, False if not found
        """
        if execution_id in self._active_executions:
            task = self._active_executions[execution_id]
            task.cancel()
            self.logger.info(f"Cancelled execution: {execution_id}")
            return True
        return False
    
    def get_active_executions(self) -> List[Dict[str, Any]]:
        """Get list of currently active executions."""
        active = []
        for exec_id, task in self._active_executions.items():
            parts = exec_id.split('_')
            active.append({
                "execution_id": exec_id,
                "agent_id": parts[0] if len(parts) > 0 else "unknown",
                "tool_name": parts[1] if len(parts) > 1 else "unknown",
                "running": not task.done()
            })
        return active
    
    def get_execution_history(self, 
                            tool_name: Optional[str] = None,
                            agent_id: Optional[str] = None,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get execution history with optional filters.
        
        Args:
            tool_name: Filter by tool name
            agent_id: Filter by agent ID
            limit: Maximum records to return
            
        Returns:
            List of execution records
        """
        records = []
        count = 0
        
        # Iterate in reverse (most recent first)
        for record in reversed(self._execution_history):
            if count >= limit:
                break
                
            # Apply filters
            if tool_name and record.tool_name != tool_name:
                continue
            if agent_id and record.context.agent_id != agent_id:
                continue
            
            records.append({
                "tool_name": record.tool_name,
                "agent_id": record.context.agent_id,
                "agent_name": record.context.agent_name,
                "started_at": record.started_at.isoformat(),
                "duration": record.duration,
                "success": record.result.success,
                "error": record.result.error
            })
            count += 1
        
        return records
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution engine statistics."""
        success_rate = (
            self._successful_executions / self._total_executions
            if self._total_executions > 0 else 0
        )
        
        avg_execution_time = (
            self._total_execution_time / self._total_executions
            if self._total_executions > 0 else 0
        )
        
        return {
            "total_executions": self._total_executions,
            "successful_executions": self._successful_executions,
            "failed_executions": self._failed_executions,
            "success_rate": success_rate,
            "total_execution_time": self._total_execution_time,
            "average_execution_time": avg_execution_time,
            "active_executions": len(self._active_executions),
            "history_size": len(self._execution_history)
        }
    
    def get_tool_statistics(self, tool_name: str) -> Dict[str, Any]:
        """Get statistics for a specific tool."""
        total = 0
        successful = 0
        total_time = 0.0
        
        for record in self._execution_history:
            if record.tool_name == tool_name:
                total += 1
                if record.result.success:
                    successful += 1
                total_time += record.duration
        
        return {
            "tool_name": tool_name,
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "total_execution_time": total_time,
            "average_execution_time": total_time / total if total > 0 else 0
        }


# Global execution engine instance
execution_engine = ToolExecutionEngine()