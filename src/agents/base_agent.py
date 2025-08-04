from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Set
from crewai import Agent
from ..utils.logger import get_logger, log_agent_action
from ..memory.local_memory import AgentLocalMemory
from ..memory.shared_context import SharedContextPool
from ..memory.persistent_knowledge import PersistentKnowledgeBase
from ..memory.vector_store import VectorMemoryStore
from ..communication.manager import CommunicationManager
from ..communication.protocols import Message, MessageType, CommunicationProtocol
from ..tools import tool_registry, execution_engine, ExecutionContext, ToolPermission, ToolResult
from ..tools.core import FileOperationsTool
from ..learning.feedback_processor import UserFeedbackProcessor, FeedbackType
from ..learning.pattern_learner import PatternLearner
from ..learning.adaptive_system import AdaptiveBehaviorSystem
import time
import uuid
import asyncio
from datetime import datetime


class BaseAgent(ABC):
    def __init__(self, name: str, role: str, goal: str, backstory: str = "", 
                 shared_context: Optional[SharedContextPool] = None,
                 comm_manager: Optional[CommunicationManager] = None,
                 knowledge_base: Optional[PersistentKnowledgeBase] = None,
                 vector_store: Optional[VectorMemoryStore] = None,
                 enable_learning: bool = True):
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
        self.knowledge_base = knowledge_base or PersistentKnowledgeBase()
        self.vector_store = vector_store
        
        # Initialize learning systems (Phase 8)
        self.enable_learning = enable_learning
        if self.enable_learning:
            self.feedback_processor = UserFeedbackProcessor(self.knowledge_base)
            self.pattern_learner = PatternLearner(self.knowledge_base)
            self.adaptive_system = AdaptiveBehaviorSystem(self.knowledge_base, self.vector_store)
            self.logger.info(f"Learning systems enabled for agent {self.name}")
        else:
            self.feedback_processor = None
            self.pattern_learner = None
            self.adaptive_system = None
            self.logger.info(f"Learning systems disabled for agent {self.name}")
        
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
    
    # Vector Memory and Knowledge Base Methods (Phase 7)
    
    async def store_learned_pattern(self, pattern_id: str, pattern: Dict[str, Any],
                                   success_rate: float = 1.0,
                                   context: Optional[Dict] = None) -> None:
        """
        Store a learned pattern in the persistent knowledge base.
        
        Args:
            pattern_id: Unique identifier for the pattern
            pattern: Pattern data (workflow steps, decisions, etc.)
            success_rate: Success rate of this pattern (0.0 to 1.0)
            context: Context in which this pattern was successful
        """
        try:
            await self.knowledge_base.store_learned_pattern(
                pattern_id, pattern, success_rate, context
            )
            self.logger.debug(f"Stored learned pattern: {pattern_id}")
        except Exception as e:
            self.logger.error(f"Failed to store learned pattern {pattern_id}: {e}")
    
    async def find_similar_patterns(self, context: str, limit: int = 5,
                                   min_similarity: float = 0.6) -> List[Dict[str, Any]]:
        """
        Find patterns similar to the current context.
        
        Args:
            context: Description of current context or task
            limit: Maximum number of patterns to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of similar patterns with similarity scores
        """
        try:
            return await self.knowledge_base.find_similar_patterns(
                context, "learned", limit, min_similarity
            )
        except Exception as e:
            self.logger.error(f"Failed to find similar patterns: {e}")
            return []
    
    async def check_failure_patterns(self, context: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Check for failure patterns that might apply to the current context.
        
        Args:
            context: Description of current context or planned action
            limit: Maximum number of failure patterns to check
            
        Returns:
            List of relevant failure patterns to avoid
        """
        try:
            return await self.knowledge_base.check_failure_patterns(context, limit)
        except Exception as e:
            self.logger.error(f"Failed to check failure patterns: {e}")
            return []
    
    async def store_user_preference(self, preference_id: str, preference: Dict[str, Any],
                                   strength: float = 1.0, context: Optional[str] = None) -> None:
        """
        Store a user preference for future reference.
        
        Args:
            preference_id: Unique identifier for the preference
            preference: Preference data
            strength: Strength of the preference (0.0 to 1.0)
            context: Context where this preference applies
        """
        try:
            await self.knowledge_base.store_user_preference(
                preference_id, preference, strength, context
            )
            self.logger.debug(f"Stored user preference: {preference_id}")
        except Exception as e:
            self.logger.error(f"Failed to store user preference {preference_id}: {e}")
    
    async def find_user_preferences(self, context: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find user preferences relevant to the current context.
        
        Args:
            context: Current context or task description
            limit: Maximum number of preferences to return
            
        Returns:
            List of relevant user preferences
        """
        try:
            return await self.knowledge_base.find_user_preferences(context, limit)
        except Exception as e:
            self.logger.error(f"Failed to find user preferences: {e}")
            return []
    
    async def store_execution_outcome(self, task_description: str, outcome: Dict[str, Any],
                                     success: bool, error: Optional[str] = None) -> None:
        """
        Store the outcome of a task execution for learning.
        
        Args:
            task_description: Description of the task executed
            outcome: Result data from the execution
            success: Whether the execution was successful
            error: Error message if execution failed
        """
        try:
            if success:
                # Store as learned pattern
                pattern_id = f"execution_{self.name}_{int(time.time())}"
                pattern = {
                    "agent_type": self.__class__.__name__,
                    "agent_role": self.role,
                    "task_description": task_description,
                    "outcome": outcome,
                    "execution_time": outcome.get("execution_time", 0),
                    "tools_used": outcome.get("tools_used", [])
                }
                await self.store_learned_pattern(pattern_id, pattern, 1.0, {
                    "agent_name": self.name,
                    "task_type": self.role
                })
            else:
                # Store as failure pattern
                failure_id = f"failure_{self.name}_{int(time.time())}"
                failure_data = {
                    "agent_type": self.__class__.__name__,
                    "agent_role": self.role,
                    "task_description": task_description,
                    "error": error,
                    "outcome": outcome,
                    "timestamp": datetime.now().isoformat(),
                    "severity": "high" if "critical" in str(error).lower() else "medium"
                }
                await self.knowledge_base.store_failure_pattern(failure_id, failure_data)
                
        except Exception as e:
            self.logger.error(f"Failed to store execution outcome: {e}")
    
    async def enhance_task_with_knowledge(self, task_description: str) -> Dict[str, Any]:
        """
        Enhance a task with relevant knowledge from the knowledge base.
        
        Args:
            task_description: Description of the task to enhance
            
        Returns:
            Dictionary with enhancement data including patterns, preferences, and warnings
        """
        try:
            enhancement = {
                "similar_patterns": [],
                "user_preferences": [],
                "failure_warnings": [],
                "recommendations": []
            }
            
            # Find similar successful patterns
            patterns = await self.find_similar_patterns(task_description, limit=3)
            enhancement["similar_patterns"] = patterns
            
            # Get relevant user preferences
            preferences = await self.find_user_preferences(task_description, limit=5)
            enhancement["user_preferences"] = preferences
            
            # Check for potential failure patterns
            failures = await self.check_failure_patterns(task_description, limit=2)
            enhancement["failure_warnings"] = failures
            
            # Generate recommendations based on knowledge
            if patterns:
                enhancement["recommendations"].append(
                    f"Found {len(patterns)} similar successful patterns. "
                    f"Consider using similar approaches."
                )
            
            if preferences:
                enhancement["recommendations"].append(
                    f"Found {len(preferences)} relevant user preferences. "
                    f"Ensure execution aligns with user expectations."
                )
            
            if failures:
                enhancement["recommendations"].append(
                    f"Warning: Found {len(failures)} potential failure patterns. "
                    f"Review these carefully to avoid known issues."
                )
            
            return enhancement
            
        except Exception as e:
            self.logger.error(f"Failed to enhance task with knowledge: {e}")
            return {
                "similar_patterns": [],
                "user_preferences": [],
                "failure_warnings": [],
                "recommendations": ["Knowledge enhancement unavailable due to error"]
            }
    
    async def semantic_memory_search(self, query: str, memory_types: Optional[List[str]] = None,
                                    limit: int = 10, min_similarity: float = 0.5) -> List[Dict[str, Any]]:
        """
        Perform semantic search across memory systems.
        
        Args:
            query: Text query for semantic search
            memory_types: Optional list of memory types to search
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of semantically similar memory entries
        """
        try:
            # Search knowledge base
            kb_results = await self.knowledge_base.search({
                "text": query,
                "limit": limit,
                "min_similarity": min_similarity,
                "knowledge_types": memory_types
            })
            
            # Add source annotation
            for result in kb_results:
                result["source"] = "knowledge_base"
            
            return kb_results
            
        except Exception as e:
            self.logger.error(f"Failed to perform semantic memory search: {e}")
            return []
    
    # Learning System Methods (Phase 8)
    
    async def process_user_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user feedback to improve future performance.
        
        Args:
            feedback_data: Feedback containing type, content, context, etc.
            
        Returns:
            Processing result with applied changes and recommendations
        """
        if not self.enable_learning or not self.feedback_processor:
            self.logger.warning("Learning systems disabled - cannot process feedback")
            return {'success': False, 'reason': 'learning_disabled'}
        
        try:
            result = await self.feedback_processor.process_feedback(feedback_data)
            self.logger.info(f"Processed user feedback: {feedback_data.get('type', 'unknown')}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to process user feedback: {e}")
            return {'success': False, 'error': str(e)}
    
    async def learn_from_workflow_result(self, workflow_result) -> Dict[str, Any]:
        """
        Learn patterns from completed workflow execution.
        
        Args:
            workflow_result: WorkflowResult object containing execution details
            
        Returns:
            Learning analysis results
        """
        if not self.enable_learning or not self.pattern_learner:
            return {'learned': False, 'reason': 'learning_disabled'}
        
        try:
            # Learn from successful patterns
            success_result = await self.pattern_learner.analyze_workflow_success(workflow_result)
            
            # Also analyze failures to avoid them
            failure_result = await self.pattern_learner.analyze_failure_patterns(workflow_result)
            
            return {
                'success_analysis': success_result,
                'failure_analysis': failure_result,
                'learned': True
            }
        except Exception as e:
            self.logger.error(f"Failed to learn from workflow result: {e}")
            return {'learned': False, 'error': str(e)}
    
    async def get_adaptive_context(self, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get context enhanced with adaptive behaviors based on learning.
        
        Args:
            base_context: Original execution context
            
        Returns:
            Enhanced context with adaptive behaviors applied
        """
        if not self.enable_learning or not self.adaptive_system:
            return base_context
        
        try:
            # Get available adaptations
            adaptations_result = await self.adaptive_system.get_adaptations(base_context)
            adaptations = adaptations_result.get('adaptations', [])
            
            if not adaptations:
                self.logger.debug("No adaptations found for current context")
                return base_context
            
            # Apply selected adaptations
            enhanced_context = await self.adaptive_system.apply_adaptations(
                base_context, 
                adaptations[:3]  # Apply top 3 adaptations
            )
            
            self.logger.info(f"Applied {len(adaptations[:3])} adaptations to context")
            return enhanced_context
            
        except Exception as e:
            self.logger.error(f"Failed to get adaptive context: {e}")
            return base_context
    
    async def provide_feedback_on_execution(self, task_description: str, 
                                          execution_result: Dict[str, Any],
                                          user_rating: Optional[float] = None) -> None:
        """
        Provide feedback on task execution for learning purposes.
        
        Args:
            task_description: Description of the executed task
            execution_result: Results of the execution
            user_rating: Optional user rating (0.0 to 1.0)
        """
        if not self.enable_learning:
            return
        
        # Create feedback data
        feedback_data = {
            'type': 'rating',
            'task_description': task_description,
            'execution_result': execution_result,
            'agent_id': self.id,
            'agent_name': self.name,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if user_rating is not None:
            feedback_data['score'] = user_rating
            feedback_data['max_score'] = 1.0
        else:
            # Auto-generate rating based on execution success
            if execution_result.get('status') == 'completed':
                feedback_data['score'] = 0.8
            elif execution_result.get('status') == 'partial':
                feedback_data['score'] = 0.5
            else:
                feedback_data['score'] = 0.2
        
        # Process the feedback
        await self.process_user_feedback(feedback_data)
    
    async def get_pattern_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get pattern recommendations for the given context.
        
        Args:
            context: Current execution context
            
        Returns:
            List of recommended patterns with confidence scores
        """
        if not self.enable_learning or not self.pattern_learner:
            return []
        
        try:
            recommendations = await self.pattern_learner.get_pattern_recommendations(context)
            self.logger.debug(f"Found {len(recommendations)} pattern recommendations")
            return recommendations
        except Exception as e:
            self.logger.error(f"Failed to get pattern recommendations: {e}")
            return []
    
    async def record_adaptation_outcome(self, adaptation_name: str, 
                                      success: bool, 
                                      performance_score: float) -> None:
        """
        Record the outcome of applying an adaptation for future learning.
        
        Args:
            adaptation_name: Name of the adaptation that was applied
            success: Whether the execution was successful
            performance_score: Performance score (0-1)
        """
        if not self.enable_learning or not self.adaptive_system:
            return
        
        try:
            await self.adaptive_system.record_adaptation_outcome(
                adaptation_name, success, performance_score
            )
            self.logger.debug(f"Recorded adaptation outcome: {adaptation_name} = {performance_score}")
        except Exception as e:
            self.logger.error(f"Failed to record adaptation outcome: {e}")
    
    async def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get insights about the agent's learning progress and performance.
        
        Returns:
            Dictionary containing learning statistics and insights
        """
        if not self.enable_learning:
            return {'learning_enabled': False}
        
        insights = {'learning_enabled': True}
        
        try:
            # Feedback processing insights
            if self.feedback_processor:
                feedback_summary = await self.feedback_processor.get_feedback_summary()
                insights['feedback_processing'] = feedback_summary
            
            # Pattern learning insights
            if self.pattern_learner:
                learning_summary = await self.pattern_learner.get_learning_summary()
                insights['pattern_learning'] = learning_summary
            
            # Adaptive behavior insights
            if self.adaptive_system:
                adaptation_stats = await self.adaptive_system.get_adaptation_statistics()
                insights['adaptive_behavior'] = adaptation_stats
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to get learning insights: {e}")
            return {'learning_enabled': True, 'error': str(e)}
    
    def enable_learning_systems(self) -> None:
        """Enable learning systems for this agent."""
        if not self.enable_learning:
            self.enable_learning = True
            self.feedback_processor = UserFeedbackProcessor(self.knowledge_base)
            self.pattern_learner = PatternLearner(self.knowledge_base)
            self.adaptive_system = AdaptiveBehaviorSystem(self.knowledge_base, self.vector_store)
            self.logger.info(f"Learning systems enabled for agent {self.name}")
    
    def disable_learning_systems(self) -> None:
        """Disable learning systems for this agent."""
        if self.enable_learning:
            self.enable_learning = False
            self.feedback_processor = None
            self.pattern_learner = None
            self.adaptive_system = None
            self.logger.info(f"Learning systems disabled for agent {self.name}")
    
    def is_learning_enabled(self) -> bool:
        """Check if learning systems are enabled."""
        return self.enable_learning and all([
            self.feedback_processor is not None,
            self.pattern_learner is not None,
            self.adaptive_system is not None
        ])