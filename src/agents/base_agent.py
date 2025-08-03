from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Set
from crewai import Agent
from ..utils.logger import get_logger, log_agent_action
from ..memory.local_memory import AgentLocalMemory
from ..memory.shared_context import SharedContextPool
from ..communication.manager import CommunicationManager
from ..communication.protocols import Message, MessageType, CommunicationProtocol
from ..tools import tool_registry, execution_engine, ExecutionContext, ToolPermission, ToolResult
from ..tools.core import FileOperationsTool
import time
import uuid
import asyncio
from datetime import datetime


class BaseAgent(ABC):
    def __init__(self, name: str, role: str, goal: str, backstory: str = "", 
                 shared_context: Optional[SharedContextPool] = None,
                 comm_manager: Optional[CommunicationManager] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory or f"A specialized agent focused on {role}"
        self.crew_agent = None
        self.project_folder: Optional[str] = None
        self.logger = get_logger(f'agent.{name}')
        self.logger.debug(f"Agent created: {name} ({role})")
        
        # Initialize memory systems
        self.local_memory = AgentLocalMemory(self.id)
        self.shared_context = shared_context or SharedContextPool()
        
        # Initialize communication system
        self.comm_manager = comm_manager
        if comm_manager:
            comm_manager.register_agent(self.id, self.handle_message, {
                "name": self.name,
                "role": self.role,
                "capabilities": self._get_capabilities()
            })
        
        # Subscribe to relevant context updates
        self._setup_context_subscriptions()
        
        # Initialize tool system
        self.available_permissions: Set[ToolPermission] = self._get_default_permissions()
        self._setup_tools()
    
    def set_project_folder(self, project_folder: str):
        """Set the project folder context for this agent"""
        self.project_folder = project_folder
        self.logger.info(f"Project folder set for {self.name}: {project_folder}")
    
    @abstractmethod
    def create_crew_agent(self) -> Agent:
        pass
    
    def initialize(self):
        self.crew_agent = self.create_crew_agent()
    
    def execute_task(self, task_description: str) -> Dict[str, Any]:
        start_time = time.time()
        self.logger.info(f"Starting task execution: {task_description}")
        
        if not self.crew_agent:
            self.initialize()
        
        try:
            # Simulated execution for MVP
            execution_time = time.time() - start_time
            result = {
                "agent_id": self.id,
                "agent_name": self.name,
                "task": task_description,
                "status": "completed",
                "output": f"Simulated execution of: {task_description}",
                "error": None
            }
            
            log_agent_action(self.id, self.name, task_description, "completed", execution_time)
            self.logger.info(f"Task completed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            result = {
                "agent_id": self.id,
                "agent_name": self.name,
                "task": task_description,
                "status": "failed",
                "output": None,
                "error": error_msg
            }
            
            log_agent_action(self.id, self.name, task_description, "failed", execution_time, e)
            self.logger.error(f"Task failed after {execution_time:.2f}s: {error_msg}")
            return result
    
    # Memory system methods
    
    def _setup_context_subscriptions(self):
        """Set up subscriptions to shared context updates."""
        # Subscribe to context updates with this agent's callback
        async def handle_context_update(update: Dict[str, Any]):
            await self._handle_context_update(update)
        
        # Note: We'll handle the async subscription in initialize()
        self._context_update_handler = handle_context_update
    
    async def _handle_context_update(self, update: Dict[str, Any]):
        """Handle incoming context updates from other agents."""
        update_type = update.get("type")
        
        # Log the update
        self.logger.debug(f"Received context update: {update_type} from {update.get('metadata', {}).get('agent_id', 'unknown')}")
        
        # Store relevant updates in local memory for quick access
        if update_type == "discovery" and update.get("data"):
            await self.local_memory.store(
                f"shared_{update['key']}",
                update["data"],
                {"source": "shared_context", "original_key": update["key"]}
            )
    
    async def store_memory(self, key: str, data: Any, metadata: Optional[Dict] = None) -> None:
        """
        Store data in local memory.
        
        Args:
            key: Unique identifier for the data
            data: The data to store
            metadata: Optional metadata about the data
        """
        if metadata is None:
            metadata = {}
        
        metadata["agent_id"] = self.id
        metadata["agent_name"] = self.name
        
        await self.local_memory.store(key, data, metadata)
        self.logger.debug(f"Stored in local memory: {key}")
    
    async def retrieve_memory(self, key: str) -> Optional[Any]:
        """
        Retrieve data from local memory.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The stored data if found, None otherwise
        """
        data = await self.local_memory.retrieve(key)
        if data:
            self.logger.debug(f"Retrieved from local memory: {key}")
        return data
    
    async def share_discovery(self, discovery_type: str, data: Dict[str, Any], 
                            relevance: float = 0.5) -> None:
        """
        Share a discovery with other agents via shared context.
        
        Args:
            discovery_type: Type of discovery (e.g., "pattern", "insight", "issue")
            data: The discovery data
            relevance: Relevance score (0-1) for other agents
        """
        key = f"discovery_{self.name}_{discovery_type}_{int(time.time())}"
        
        metadata = {
            "agent_id": self.id,
            "agent_name": self.name,
            "discovery_type": discovery_type,
            "relevance": relevance
        }
        
        await self.shared_context.store(key, data, metadata)
        
        self.logger.info(f"Shared discovery: {discovery_type} with relevance {relevance}")
    
    async def get_shared_context(self, context_type: Optional[str] = None, 
                               agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get relevant shared context from other agents.
        
        Args:
            context_type: Optional filter by context type
            agent_id: Optional filter by specific agent
            
        Returns:
            List of relevant context entries
        """
        query = {}
        if context_type:
            query["context_type"] = context_type
        if agent_id:
            query["agent_id"] = agent_id
        
        results = await self.shared_context.search(query)
        self.logger.debug(f"Retrieved {len(results)} shared context entries")
        return results
    
    async def add_finding(self, finding_id: str, finding: Any) -> None:
        """
        Add a temporary finding for the current task.
        
        Args:
            finding_id: Unique identifier for the finding
            finding: The finding data
        """
        await self.local_memory.add_finding(finding_id, finding)
        self.logger.debug(f"Added finding: {finding_id}")
    
    async def get_findings(self) -> Dict[str, Any]:
        """Get all temporary findings for the current task."""
        findings = await self.local_memory.get_findings()
        self.logger.debug(f"Retrieved {len(findings)} findings")
        return findings
    
    async def clear_local_memory(self) -> None:
        """Clear local memory after task completion."""
        stats = self.local_memory.get_statistics()
        await self.local_memory.clear()
        self.logger.info(f"Cleared local memory. Previous stats: {stats}")
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        local_stats = self.local_memory.get_statistics()
        shared_size = await self.shared_context.get_size()
        
        return {
            "local_memory": local_stats,
            "shared_context_size": shared_size,
            "agent_id": self.id,
            "agent_name": self.name
        }
    
    # Communication system methods
    
    def _get_capabilities(self) -> List[str]:
        """
        Get list of capabilities this agent provides.
        
        Subclasses can override this to specify their capabilities.
        
        Returns:
            List of capability identifiers
        """
        return [self.role.lower(), "general"]
    
    async def handle_message(self, message: Message) -> None:
        """
        Handle incoming messages from other agents.
        
        This is the main message handler that processes different types
        of messages and delegates to appropriate methods.
        
        Args:
            message: Incoming message to handle
        """
        self.logger.debug(f"Received message: {message.message_type.value} from {message.sender}")
        
        try:
            # Handle different message types
            if message.message_type == MessageType.REQUEST:
                await self._handle_request(message)
            elif message.message_type == MessageType.DISCOVERY:
                await self._handle_discovery(message)
            elif message.message_type == MessageType.NOTIFICATION:
                await self._handle_notification(message)
            elif message.message_type == MessageType.REVIEW_REQUEST:
                await self._handle_review_request(message)
            elif message.message_type == MessageType.STATUS_UPDATE:
                await self._handle_status_update(message)
            elif message.message_type == MessageType.RESPONSE:
                # Responses are handled by the communication manager
                pass
            else:
                self.logger.warning(f"Unhandled message type: {message.message_type}")
                
        except Exception as e:
            self.logger.error(f"Error handling message from {message.sender}: {e}")
            
            # Send error response if message requires response
            if message.requires_response:
                await self.send_response(message, {"error": str(e)}, success=False)
    
    async def _handle_request(self, message: Message) -> None:
        """
        Handle request messages from other agents.
        
        Args:
            message: Request message
        """
        request_type = message.content.get("request_type")
        data = message.content.get("data", {})
        
        self.logger.info(f"Processing request: {request_type} from {message.sender}")
        
        # Process the request
        try:
            response_data = await self.process_request(request_type, data, message.sender)
            await self.send_response(message, response_data, success=True)
        except Exception as e:
            self.logger.error(f"Error processing request {request_type}: {e}")
            await self.send_response(message, {"error": str(e)}, success=False)
    
    async def _handle_discovery(self, message: Message) -> None:
        """
        Handle discovery messages from other agents.
        
        Args:
            message: Discovery message
        """
        discovery_type = message.content.get("discovery_type")
        data = message.content.get("data")
        relevance = message.content.get("relevance", 0.5)
        
        # Only process discoveries above relevance threshold
        if relevance >= 0.3:
            # Store relevant discovery in local memory
            await self.store_memory(
                f"discovery_{message.sender}_{discovery_type}",
                data,
                {"source": message.sender, "relevance": relevance, "type": "discovery"}
            )
            
            self.logger.info(f"Stored discovery: {discovery_type} from {message.sender} (relevance: {relevance})")
    
    async def _handle_notification(self, message: Message) -> None:
        """
        Handle notification messages from other agents.
        
        Args:
            message: Notification message
        """
        # Store notification for later reference
        await self.store_memory(
            f"notification_{message.sender}_{int(time.time())}",
            message.content,
            {"source": message.sender, "type": "notification"}
        )
        
        self.logger.info(f"Received notification from {message.sender}")
    
    async def _handle_review_request(self, message: Message) -> None:
        """
        Handle review request messages from other agents.
        
        Args:
            message: Review request message
        """
        content = message.content.get("content")
        criteria = message.content.get("criteria", [])
        
        self.logger.info(f"Processing review request from {message.sender}")
        
        try:
            # Perform the review
            review_result = await self.review_content(content, criteria, message.sender)
            
            # Send review response
            response_data = {
                "review": review_result,
                "reviewer": self.name,
                "criteria_used": criteria
            }
            await self.send_response(message, response_data, success=True)
            
        except Exception as e:
            self.logger.error(f"Error processing review request: {e}")
            await self.send_response(message, {"error": str(e)}, success=False)
    
    async def _handle_status_update(self, message: Message) -> None:
        """
        Handle status update messages from other agents.
        
        Args:
            message: Status update message
        """
        status = message.content.get("status")
        details = message.content.get("details", {})
        
        # Store agent status for awareness
        await self.store_memory(
            f"agent_status_{message.sender}",
            {"status": status, "details": details, "timestamp": message.timestamp},
            {"source": message.sender, "type": "status"}
        )
        
        self.logger.debug(f"Agent {message.sender} status: {status}")
    
    async def send_message_to_agent(self, recipient: str, message_type: MessageType,
                                  content: Dict[str, Any], 
                                  requires_response: bool = False,
                                  timeout: int = None) -> Optional[Message]:
        """
        Send a message to another agent.
        
        Args:
            recipient: ID of recipient agent
            message_type: Type of message to send
            content: Message content
            requires_response: Whether to wait for response
            timeout: Response timeout in seconds
            
        Returns:
            Response message if requires_response=True, None otherwise
        """
        if not self.comm_manager:
            self.logger.warning("No communication manager available")
            return None
        
        # Create message
        message = Message(
            sender=self.id,
            recipient=recipient,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            message_id=str(uuid.uuid4()),
            requires_response=requires_response,
            response_timeout=timeout
        )
        
        # Send message
        if requires_response:
            try:
                response_future = await self.comm_manager.send_message(message)
                response = await response_future
                return response
            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout waiting for response from {recipient}")
                return None
        else:
            await self.comm_manager.send_message(message)
            return None
    
    async def send_request_to_agent(self, recipient: str, request_type: str,
                                  data: Dict[str, Any], timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        Send a request to another agent and wait for response.
        
        Args:
            recipient: ID of target agent
            request_type: Type of request
            data: Request data
            timeout: Response timeout in seconds
            
        Returns:
            Response data if successful, None if failed
        """
        if not self.comm_manager:
            self.logger.warning("No communication manager available")
            return None
        
        try:
            response_data = await self.comm_manager.send_request(
                self.id, recipient, request_type, data, timeout
            )
            return response_data
        except Exception as e:
            self.logger.error(f"Request to {recipient} failed: {e}")
            return None
    
    async def send_response(self, original_message: Message, 
                          response_data: Dict[str, Any], success: bool = True) -> None:
        """
        Send a response to a received message.
        
        Args:
            original_message: The message being responded to
            response_data: Response data
            success: Whether the request was successful
        """
        if not self.comm_manager:
            self.logger.warning("No communication manager available")
            return
        
        response = CommunicationProtocol.create_response(
            original_message, self.id, response_data, success
        )
        
        await self.comm_manager.send_message(response)
    
    async def broadcast_status(self, status: str, details: Dict[str, Any] = None) -> None:
        """
        Broadcast status update to all agents.
        
        Args:
            status: Current status
            details: Additional status details
        """
        if not self.comm_manager:
            self.logger.warning("No communication manager available")
            return
        
        message = CommunicationProtocol.create_status_update(
            self.id, status, details or {}
        )
        
        await self.comm_manager.send_message(message)
        self.logger.info(f"Broadcast status: {status}")
    
    async def request_peer_review(self, reviewer_id: str, content: Dict[str, Any],
                                criteria: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Request peer review from another agent.
        
        Args:
            reviewer_id: ID of reviewing agent
            content: Content to be reviewed
            criteria: Review criteria
            
        Returns:
            Review result if successful, None if failed
        """
        if not self.comm_manager:
            self.logger.warning("No communication manager available")
            return None
        
        message = CommunicationProtocol.create_review_request(
            self.id, reviewer_id, content, criteria
        )
        
        try:
            response_future = await self.comm_manager.send_message(message)
            response = await response_future
            
            if response.content.get("success"):
                return response.content.get("data")
            else:
                self.logger.error(f"Review request failed: {response.content.get('error')}")
                return None
                
        except asyncio.TimeoutError:
            self.logger.warning(f"Review request to {reviewer_id} timed out")
            return None
    
    # Abstract methods for subclasses to implement
    
    async def process_request(self, request_type: str, data: Dict[str, Any], 
                            sender: str) -> Dict[str, Any]:
        """
        Process a request from another agent.
        
        Subclasses should override this to handle specific request types.
        
        Args:
            request_type: Type of request
            data: Request data
            sender: ID of requesting agent
            
        Returns:
            Response data
        """
        return {"message": f"Request {request_type} processed by {self.name}"}
    
    async def review_content(self, content: Dict[str, Any], criteria: List[str],
                           requester: str) -> Dict[str, Any]:
        """
        Review content from another agent.
        
        Subclasses should override this to provide specific review capabilities.
        
        Args:
            content: Content to review
            criteria: Review criteria
            requester: ID of requesting agent
            
        Returns:
            Review result
        """
        return {
            "score": 0.8,
            "feedback": f"Content reviewed by {self.name}",
            "approved": True,
            "suggestions": []
        }
    
    # Tool system methods
    
    def _get_default_permissions(self) -> Set[ToolPermission]:
        """Get default tool permissions for this agent."""
        # Base agents get read and execute permissions
        # Specific agent types can override for additional permissions
        return {ToolPermission.READ, ToolPermission.EXECUTE}
    
    def _setup_tools(self):
        """Set up tool system for this agent."""
        # Set up file operations tool with project folder if available
        if hasattr(self, 'project_folder') and self.project_folder:
            file_tool = FileOperationsTool()
            file_tool.set_project_folder(self.project_folder)
            # Note: File tool registration handled globally
        
        self.logger.debug(f"Tool system initialized for {self.name} with permissions: {[p.value for p in self.available_permissions]}")
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], 
                          timeout: Optional[int] = None) -> ToolResult:
        """
        Execute a tool with validation and monitoring.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            timeout: Optional timeout override
            
        Returns:
            ToolResult from execution
        """
        # Create execution context
        context = ExecutionContext(
            agent_id=self.id,
            agent_name=self.name,
            conversation_id=getattr(self, 'conversation_id', 'unknown'),
            workflow_id=getattr(self, 'workflow_id', None),
            permissions=self.available_permissions,
            metadata={
                "role": self.role,
                "goal": self.goal
            }
        )
        
        self.logger.info(f"Executing tool {tool_name} with parameters: {parameters}")
        
        # Execute tool
        result = await execution_engine.execute_tool(
            tool_name=tool_name,
            parameters=parameters,
            context=context,
            timeout=timeout
        )
        
        # Store result in memory for context
        await self.store_memory(
            f"tool_execution_{tool_name}_{int(time.time())}",
            {
                "tool_name": tool_name,
                "parameters": parameters,
                "result": {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                    "execution_time": result.execution_time
                }
            },
            {"type": "tool_execution", "tool": tool_name}
        )
        
        if result.success:
            self.logger.info(f"Tool {tool_name} executed successfully in {result.execution_time:.2f}s")
        else:
            self.logger.error(f"Tool {tool_name} failed: {result.error}")
        
        return result
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of tools available to this agent.
        
        Returns:
            List of tool information dictionaries
        """
        available_tools = tool_registry.get_tools_for_permissions(self.available_permissions)
        
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.value,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type,
                        "description": p.description,
                        "required": p.required
                    }
                    for p in tool.parameters
                ]
            }
            for tool in available_tools
        ]
    
    def validate_tool_access(self, tool_name: str) -> bool:
        """
        Check if this agent can access a specific tool.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool can be accessed, False otherwise
        """
        return tool_registry.check_tool_permission(tool_name, self.available_permissions)
    
    async def select_tools_for_task(self, task_description: str) -> List[str]:
        """
        Suggest tools that might be useful for a given task.
        
        Args:
            task_description: Description of the task
            
        Returns:
            List of suggested tool names
        """
        # Simple keyword-based tool selection
        # In production, this could use embedding similarity or LLM classification
        task_lower = task_description.lower()
        suggestions = []
        
        # Check available tools
        available_tools = tool_registry.get_tools_for_permissions(self.available_permissions)
        
        for tool in available_tools:
            # Basic keyword matching
            if any(keyword in task_lower for keyword in [
                # Calculator keywords
                "calculate", "math", "compute", "number", "formula", "equation",
                # File operations keywords  
                "file", "read", "write", "save", "load", "directory", "folder",
                # Web search keywords
                "search", "find", "lookup", "research", "information", "web"
            ]):
                if tool.name == "calculator" and any(kw in task_lower for kw in ["calculate", "math", "compute", "number", "formula"]):
                    suggestions.append(tool.name)
                elif tool.name == "file_operations" and any(kw in task_lower for kw in ["file", "read", "write", "save", "load"]):
                    suggestions.append(tool.name)
                elif tool.name == "web_search" and any(kw in task_lower for kw in ["search", "find", "lookup", "research"]):
                    suggestions.append(tool.name)
        
        return suggestions
    
    def add_tool_permission(self, permission: ToolPermission):
        """Add a tool permission to this agent."""
        self.available_permissions.add(permission)
        self.logger.info(f"Added tool permission {permission.value} to {self.name}")
    
    def remove_tool_permission(self, permission: ToolPermission):
        """Remove a tool permission from this agent."""
        self.available_permissions.discard(permission)
        self.logger.info(f"Removed tool permission {permission.value} from {self.name}")
    
    async def get_tool_usage_statistics(self) -> Dict[str, Any]:
        """Get statistics about tool usage by this agent."""
        history = execution_engine.get_execution_history(agent_id=self.id)
        
        if not history:
            return {
                "agent_id": self.id,
                "agent_name": self.name,
                "total_executions": 0,
                "tools_used": [],
                "success_rate": 0.0
            }
        
        tools_used = {}
        successful = 0
        
        for record in history:
            tool_name = record["tool_name"]
            if tool_name not in tools_used:
                tools_used[tool_name] = {"total": 0, "successful": 0}
            
            tools_used[tool_name]["total"] += 1
            if record["success"]:
                tools_used[tool_name]["successful"] += 1
                successful += 1
        
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "total_executions": len(history),
            "successful_executions": successful,
            "success_rate": successful / len(history),
            "tools_used": tools_used,
            "available_permissions": [p.value for p in self.available_permissions]
        }