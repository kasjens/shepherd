"""
Local agent memory implementation for short-term, task-specific storage.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import OrderedDict, deque
import fnmatch

from .base import BaseMemory


class AgentLocalMemory(BaseMemory):
    """
    Local memory implementation for individual agents.
    
    This memory tier is designed for short-term, task-specific storage
    that is cleared after task completion. It includes:
    - Working memory for current task context
    - Recent actions history
    - Temporary findings and intermediate results
    
    Features:
    - LRU eviction when memory limit is reached
    - Automatic timestamp tracking
    - Task-scoped isolation
    """
    
    def __init__(self, agent_id: str, max_entries: int = 1000, max_history: int = 100):
        """
        Initialize local memory for an agent.
        
        Args:
            agent_id: Unique identifier for the agent
            max_entries: Maximum number of entries in working memory
            max_history: Maximum number of recent actions to track
        """
        self.agent_id = agent_id
        self.max_entries = max_entries
        self.max_history = max_history
        
        # Working memory with LRU eviction
        self.working_memory: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        
        # Recent actions as a deque for efficient FIFO
        self.recent_actions: deque = deque(maxlen=max_history)
        
        # Temporary findings for current task
        self.temporary_findings: Dict[str, Any] = {}
        
        # Memory statistics
        self.stats = {
            "stores": 0,
            "retrieves": 0,
            "evictions": 0,
            "clears": 0
        }
    
    async def store(self, key: str, data: Any, metadata: Optional[Dict] = None) -> None:
        """Store data in local memory with automatic timestamp."""
        self.stats["stores"] += 1
        
        # Prepare entry
        entry = {
            "data": data,
            "timestamp": datetime.now(),
            "metadata": metadata or {},
            "agent_id": self.agent_id
        }
        
        # Check if we need to evict
        if len(self.working_memory) >= self.max_entries and key not in self.working_memory:
            # Evict least recently used
            self.working_memory.popitem(last=False)
            self.stats["evictions"] += 1
        
        # Store or update entry
        if key in self.working_memory:
            # Move to end (most recent)
            self.working_memory.move_to_end(key)
        
        self.working_memory[key] = entry
        
        # Track action
        action = {
            "type": "store",
            "key": key,
            "timestamp": entry["timestamp"],
            "metadata_keys": list(metadata.keys()) if metadata else []
        }
        self.recent_actions.append(action)
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from local memory."""
        self.stats["retrieves"] += 1
        
        if key in self.working_memory:
            # Move to end (most recently used)
            self.working_memory.move_to_end(key)
            
            # Track action
            action = {
                "type": "retrieve",
                "key": key,
                "timestamp": datetime.now(),
                "found": True
            }
            self.recent_actions.append(action)
            
            return self.working_memory[key]["data"]
        
        # Track failed retrieval
        action = {
            "type": "retrieve",
            "key": key,
            "timestamp": datetime.now(),
            "found": False
        }
        self.recent_actions.append(action)
        
        return None
    
    async def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search local memory based on query criteria.
        
        Supported query fields:
        - type: Match metadata type field
        - timestamp_after: Return entries after this datetime
        - timestamp_before: Return entries before this datetime
        - metadata: Dictionary of metadata fields to match
        - pattern: Pattern to match against keys
        """
        results = []
        
        for key, entry in self.working_memory.items():
            # Check key pattern
            if "pattern" in query:
                if not fnmatch.fnmatch(key, query["pattern"]):
                    continue
            
            # Check timestamp constraints
            if "timestamp_after" in query:
                if entry["timestamp"] <= query["timestamp_after"]:
                    continue
            
            if "timestamp_before" in query:
                if entry["timestamp"] >= query["timestamp_before"]:
                    continue
            
            # Check metadata matches
            if "metadata" in query:
                metadata_match = True
                for meta_key, meta_value in query["metadata"].items():
                    if entry["metadata"].get(meta_key) != meta_value:
                        metadata_match = False
                        break
                if not metadata_match:
                    continue
            
            # Check type in metadata
            if "type" in query:
                if entry["metadata"].get("type") != query["type"]:
                    continue
            
            # Entry matches all criteria
            results.append({
                "key": key,
                "data": entry["data"],
                "timestamp": entry["timestamp"],
                "metadata": entry["metadata"]
            })
        
        return results
    
    async def delete(self, key: str) -> bool:
        """Delete entry from local memory."""
        if key in self.working_memory:
            del self.working_memory[key]
            
            # Track action
            action = {
                "type": "delete",
                "key": key,
                "timestamp": datetime.now(),
                "success": True
            }
            self.recent_actions.append(action)
            
            return True
        
        return False
    
    async def clear(self) -> None:
        """Clear all local memory."""
        self.stats["clears"] += 1
        
        # Clear all memory stores
        self.working_memory.clear()
        self.recent_actions.clear()
        self.temporary_findings.clear()
        
        # Track action
        action = {
            "type": "clear",
            "timestamp": datetime.now(),
            "cleared_entries": self.stats["stores"] - self.stats["evictions"]
        }
        # Note: This action is added after clear, so it will be the only one
        self.recent_actions.append(action)
    
    async def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """List all keys in working memory."""
        keys = list(self.working_memory.keys())
        
        if pattern:
            keys = [k for k in keys if fnmatch.fnmatch(k, pattern)]
        
        return keys
    
    async def get_size(self) -> int:
        """Get number of entries in working memory."""
        return len(self.working_memory)
    
    # Additional local memory specific methods
    
    async def add_finding(self, finding_id: str, finding: Any) -> None:
        """
        Add a temporary finding for the current task.
        
        Args:
            finding_id: Unique identifier for the finding
            finding: The finding data
        """
        self.temporary_findings[finding_id] = {
            "data": finding,
            "timestamp": datetime.now()
        }
    
    async def get_findings(self) -> Dict[str, Any]:
        """Get all temporary findings."""
        return {
            fid: f["data"] 
            for fid, f in self.temporary_findings.items()
        }
    
    async def get_recent_actions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent actions performed on this memory.
        
        Args:
            limit: Maximum number of actions to return
            
        Returns:
            List of recent actions (newest first)
        """
        actions = list(self.recent_actions)
        actions.reverse()  # Newest first
        
        if limit:
            actions = actions[:limit]
        
        return actions
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        return {
            **self.stats,
            "current_entries": len(self.working_memory),
            "current_findings": len(self.temporary_findings),
            "recent_actions_count": len(self.recent_actions),
            "memory_usage_percent": (len(self.working_memory) / self.max_entries) * 100
        }