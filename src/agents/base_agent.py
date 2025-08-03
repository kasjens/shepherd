from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from crewai import Agent
from ..utils.logger import get_logger, log_agent_action
from ..memory.local_memory import AgentLocalMemory
from ..memory.shared_context import SharedContextPool
import time
import uuid


class BaseAgent(ABC):
    def __init__(self, name: str, role: str, goal: str, backstory: str = "", 
                 shared_context: Optional[SharedContextPool] = None):
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
        
        # Subscribe to relevant context updates
        self._setup_context_subscriptions()
    
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