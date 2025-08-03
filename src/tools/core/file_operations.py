"""
File operations tool for reading and writing files.

Provides safe file system operations with path validation and permission checks.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..base_tool import BaseTool, ToolCategory, ToolParameter, ToolResult, ToolPermission


class FileOperationsTool(BaseTool):
    """
    File operations tool for safe file system interactions.
    
    Features:
    - Read file contents
    - Write/update files
    - List directory contents
    - Check file existence
    - Path validation and sandboxing
    """
    
    def __init__(self, allowed_directories: Optional[List[str]] = None):
        """
        Initialize with optional directory restrictions.
        
        Args:
            allowed_directories: List of directories where operations are allowed.
                               If None, only project folder is allowed.
        """
        super().__init__()
        self.allowed_directories = allowed_directories or []
        self._project_folder: Optional[str] = None
    
    def set_project_folder(self, project_folder: str):
        """Set the project folder for file operations."""
        self._project_folder = project_folder
        if project_folder and project_folder not in self.allowed_directories:
            self.allowed_directories.append(project_folder)
    
    @property
    def name(self) -> str:
        return "file_operations"
    
    @property
    def description(self) -> str:
        return "Read, write, and manage files within allowed directories"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.FILE_SYSTEM
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="str",
                description="Operation to perform: 'read', 'write', 'list', 'exists', 'delete'",
                required=True
            ),
            ToolParameter(
                name="path",
                type="str",
                description="File or directory path (relative to project folder or absolute if allowed)",
                required=True
            ),
            ToolParameter(
                name="content",
                type="str",
                description="Content to write (required for 'write' operation)",
                required=False
            ),
            ToolParameter(
                name="encoding",
                type="str",
                description="File encoding (default: 'utf-8')",
                required=False,
                default="utf-8"
            )
        ]
    
    @property
    def required_permissions(self) -> List[ToolPermission]:
        return [ToolPermission.READ, ToolPermission.WRITE, ToolPermission.EXECUTE]
    
    @property
    def usage_examples(self) -> List[Dict[str, Any]]:
        return [
            {
                "description": "Read a file",
                "parameters": {
                    "operation": "read",
                    "path": "config.json"
                }
            },
            {
                "description": "Write to a file",
                "parameters": {
                    "operation": "write",
                    "path": "output.txt",
                    "content": "Hello, World!"
                }
            },
            {
                "description": "List directory contents",
                "parameters": {
                    "operation": "list",
                    "path": "."
                }
            }
        ]
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute file operation.
        
        Args:
            parameters: Operation parameters
            
        Returns:
            ToolResult with operation outcome
        """
        operation = parameters.get("operation", "")
        path_str = parameters.get("path", "")
        
        if not operation:
            return ToolResult(
                success=False,
                data=None,
                error="Operation is required"
            )
        
        if not path_str:
            return ToolResult(
                success=False,
                data=None,
                error="Path is required"
            )
        
        # Validate and resolve path
        try:
            safe_path = self._validate_path(path_str)
        except ValueError as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )
        
        # Execute operation
        if operation == "read":
            return await self._read_file(safe_path, parameters.get("encoding", "utf-8"))
        elif operation == "write":
            content = parameters.get("content", "")
            return await self._write_file(safe_path, content, parameters.get("encoding", "utf-8"))
        elif operation == "list":
            return await self._list_directory(safe_path)
        elif operation == "exists":
            return await self._check_exists(safe_path)
        elif operation == "delete":
            return await self._delete_file(safe_path)
        else:
            return ToolResult(
                success=False,
                data=None,
                error=f"Unknown operation: {operation}"
            )
    
    def _validate_path(self, path_str: str) -> Path:
        """
        Validate and resolve path to ensure it's within allowed directories.
        
        Args:
            path_str: Path string to validate
            
        Returns:
            Resolved safe path
            
        Raises:
            ValueError: If path is not allowed
        """
        # Convert to Path object
        path = Path(path_str)
        
        # If relative, make it relative to project folder
        if not path.is_absolute() and self._project_folder:
            path = Path(self._project_folder) / path
        
        # Resolve to absolute path
        try:
            resolved_path = path.resolve()
        except Exception:
            raise ValueError(f"Invalid path: {path_str}")
        
        # Check if path is within allowed directories
        if not self.allowed_directories:
            raise ValueError("No allowed directories configured")
        
        path_allowed = False
        for allowed_dir in self.allowed_directories:
            allowed_path = Path(allowed_dir).resolve()
            try:
                resolved_path.relative_to(allowed_path)
                path_allowed = True
                break
            except ValueError:
                continue
        
        if not path_allowed:
            raise ValueError(
                f"Path '{path_str}' is outside allowed directories. "
                f"Allowed: {', '.join(self.allowed_directories)}"
            )
        
        return resolved_path
    
    async def _read_file(self, path: Path, encoding: str) -> ToolResult:
        """Read file contents."""
        if not path.exists():
            return ToolResult(
                success=False,
                data=None,
                error=f"File not found: {path}"
            )
        
        if not path.is_file():
            return ToolResult(
                success=False,
                data=None,
                error=f"Path is not a file: {path}"
            )
        
        try:
            content = path.read_text(encoding=encoding)
            
            # Try to detect file type
            file_type = "text"
            if path.suffix == ".json":
                try:
                    json.loads(content)
                    file_type = "json"
                except:
                    pass
            
            return ToolResult(
                success=True,
                data={
                    "path": str(path),
                    "content": content,
                    "size": path.stat().st_size,
                    "type": file_type,
                    "encoding": encoding
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to read file: {str(e)}"
            )
    
    async def _write_file(self, path: Path, content: str, encoding: str) -> ToolResult:
        """Write content to file."""
        try:
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            path.write_text(content, encoding=encoding)
            
            return ToolResult(
                success=True,
                data={
                    "path": str(path),
                    "size": len(content.encode(encoding)),
                    "encoding": encoding
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to write file: {str(e)}"
            )
    
    async def _list_directory(self, path: Path) -> ToolResult:
        """List directory contents."""
        if not path.exists():
            return ToolResult(
                success=False,
                data=None,
                error=f"Directory not found: {path}"
            )
        
        if not path.is_dir():
            return ToolResult(
                success=False,
                data=None,
                error=f"Path is not a directory: {path}"
            )
        
        try:
            items = []
            for item in sorted(path.iterdir()):
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "path": str(item)
                }
                items.append(item_info)
            
            return ToolResult(
                success=True,
                data={
                    "path": str(path),
                    "count": len(items),
                    "items": items
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to list directory: {str(e)}"
            )
    
    async def _check_exists(self, path: Path) -> ToolResult:
        """Check if path exists."""
        exists = path.exists()
        
        result_data = {
            "path": str(path),
            "exists": exists
        }
        
        if exists:
            result_data["type"] = "directory" if path.is_dir() else "file"
            if path.is_file():
                result_data["size"] = path.stat().st_size
        
        return ToolResult(
            success=True,
            data=result_data
        )
    
    async def _delete_file(self, path: Path) -> ToolResult:
        """Delete a file (not directories for safety)."""
        if not path.exists():
            return ToolResult(
                success=False,
                data=None,
                error=f"File not found: {path}"
            )
        
        if path.is_dir():
            return ToolResult(
                success=False,
                data=None,
                error="Cannot delete directories for safety. Only files can be deleted."
            )
        
        try:
            path.unlink()
            return ToolResult(
                success=True,
                data={
                    "path": str(path),
                    "deleted": True
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to delete file: {str(e)}"
            )