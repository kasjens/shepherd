"""
Shared context pool for medium-term agent collaboration.
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime
from collections import defaultdict
import fnmatch
import logging

from .base import BaseMemory
from .vector_store import VectorMemoryStore

logger = logging.getLogger(__name__)


class SharedContextPool(BaseMemory):
    """
    Shared context pool for cross-agent collaboration within workflows.
    
    This memory tier enables agents to share discoveries, context, and
    artifacts during workflow execution. Features include:
    - Pub/sub mechanism for real-time updates
    - Context isolation by workflow
    - Automatic relevance scoring
    - Event-driven notifications
    
    The shared context is cleared at the end of each workflow/conversation.
    """
    
    def __init__(self, workflow_id: Optional[str] = None, enable_vector_search: bool = False):
        """
        Initialize shared context pool.
        
        Args:
            workflow_id: Optional workflow identifier for context isolation
            enable_vector_search: Whether to enable vector-based semantic search
        """
        self.workflow_id = workflow_id or "default"
        self.enable_vector_search = enable_vector_search
        
        # Main context storage
        self.conversation_context: Dict[str, Dict[str, Any]] = {}
        self.workflow_artifacts: Dict[str, Any] = {}
        self.agent_discoveries: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.execution_history: List[Dict[str, Any]] = []
        
        # Pub/sub system
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._subscriber_filters: Dict[str, Dict[str, Any]] = {}
        
        # Context metadata
        self.metadata = {
            "created_at": datetime.now(),
            "workflow_id": self.workflow_id,
            "total_updates": 0,
            "active_agents": set()
        }
        
        # Optional vector memory for semantic search
        self.vector_store: Optional[VectorMemoryStore] = None
        if enable_vector_search:
            try:
                self.vector_store = VectorMemoryStore(
                    collection_name=f"shared_context_{self.workflow_id}",
                    persist_directory=None  # Ephemeral for shared context
                )
                logger.debug(f"Enabled vector search for workflow {self.workflow_id}")
            except Exception as e:
                logger.warning(f"Failed to initialize vector store: {e}")
                self.enable_vector_search = False
    
    async def store(self, key: str, data: Any, metadata: Optional[Dict] = None) -> None:
        """Store data in shared context with broadcasting."""
        # Prepare entry
        entry = {
            "data": data,
            "timestamp": datetime.now(),
            "metadata": metadata or {},
            "workflow_id": self.workflow_id
        }
        
        # Determine context type from key prefix
        context_type = self._determine_context_type(key)
        
        # Store in appropriate location
        if context_type == "discovery":
            agent_id = metadata.get("agent_id", "unknown") if metadata else "unknown"
            self.agent_discoveries[agent_id].append({
                "key": key,
                **entry
            })
        elif context_type == "artifact":
            self.workflow_artifacts[key] = entry
        else:
            self.conversation_context[key] = entry
        
        # Update metadata
        self.metadata["total_updates"] += 1
        if metadata and "agent_id" in metadata:
            self.metadata["active_agents"].add(metadata["agent_id"])
        
        # Broadcast update to subscribers
        await self._broadcast_update(context_type, key, data, metadata)
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from shared context."""
        # Check all storage locations
        if key in self.conversation_context:
            return self.conversation_context[key]["data"]
        elif key in self.workflow_artifacts:
            return self.workflow_artifacts[key]["data"]
        else:
            # Check discoveries
            for agent_discoveries in self.agent_discoveries.values():
                for discovery in agent_discoveries:
                    if discovery["key"] == key:
                        return discovery["data"]
        
        return None
    
    async def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search shared context based on query criteria.
        
        Supported query fields:
        - context_type: "conversation", "artifact", "discovery"
        - agent_id: Filter by specific agent
        - timestamp_after: Return entries after this datetime
        - relevance_min: Minimum relevance score
        - pattern: Key pattern matching
        """
        results = []
        
        # If agent_id is specified without context_type, only search discoveries
        if "agent_id" in query and "context_type" not in query:
            query["context_type"] = "discovery"
        
        # Search conversation context
        if not query.get("context_type") or query["context_type"] == "conversation":
            results.extend(self._search_dict(self.conversation_context, query))
        
        # Search artifacts
        if not query.get("context_type") or query["context_type"] == "artifact":
            results.extend(self._search_dict(self.workflow_artifacts, query))
        
        # Search discoveries
        if not query.get("context_type") or query["context_type"] == "discovery":
            agent_filter = query.get("agent_id")
            
            for agent_id, discoveries in self.agent_discoveries.items():
                if agent_filter and agent_id != agent_filter:
                    continue
                
                for discovery in discoveries:
                    if self._matches_query(discovery, query):
                        results.append({
                            "key": discovery["key"],
                            "data": discovery["data"],
                            "timestamp": discovery["timestamp"],
                            "metadata": {**discovery["metadata"], "agent_id": agent_id}
                        })
        
        # Sort by relevance if specified
        if "relevance_min" in query:
            results = [r for r in results if r["metadata"].get("relevance", 0) >= query["relevance_min"]]
        
        return results
    
    async def delete(self, key: str) -> bool:
        """Delete entry from shared context."""
        deleted = False
        
        # Try to delete from each storage location
        if key in self.conversation_context:
            del self.conversation_context[key]
            deleted = True
        
        if key in self.workflow_artifacts:
            del self.workflow_artifacts[key]
            deleted = True
        
        # Check discoveries
        for agent_id in list(self.agent_discoveries.keys()):
            original_len = len(self.agent_discoveries[agent_id])
            self.agent_discoveries[agent_id] = [d for d in self.agent_discoveries[agent_id] if d["key"] != key]
            if len(self.agent_discoveries[agent_id]) < original_len:
                deleted = True
        
        return deleted
    
    async def clear(self) -> None:
        """Clear all shared context."""
        self.conversation_context.clear()
        self.workflow_artifacts.clear()
        self.agent_discoveries.clear()
        self.execution_history.clear()
        
        # Reset metadata
        self.metadata["total_updates"] = 0
        self.metadata["active_agents"].clear()
        
        # Notify subscribers of clear
        await self._broadcast_update("system", "clear", None, {"action": "clear"})
    
    async def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """List all keys in shared context."""
        keys = []
        
        # Collect keys from all storage locations
        keys.extend(self.conversation_context.keys())
        keys.extend(self.workflow_artifacts.keys())
        
        for discoveries in self.agent_discoveries.values():
            keys.extend([d["key"] for d in discoveries])
        
        # Remove duplicates
        keys = list(set(keys))
        
        # Apply pattern filter
        if pattern:
            keys = [k for k in keys if fnmatch.fnmatch(k, pattern)]
        
        return keys
    
    async def get_size(self) -> int:
        """Get total number of entries in shared context."""
        size = len(self.conversation_context) + len(self.workflow_artifacts)
        
        for discoveries in self.agent_discoveries.values():
            size += len(discoveries)
        
        return size
    
    # Pub/sub methods
    
    async def subscribe(self, subscriber_id: str, callback: Callable, 
                       filter_criteria: Optional[Dict[str, Any]] = None) -> None:
        """
        Subscribe to context updates.
        
        Args:
            subscriber_id: Unique identifier for the subscriber
            callback: Async function to call on updates
            filter_criteria: Optional criteria to filter updates
                           e.g., {"context_type": "discovery", "agent_id": "research_agent"}
        """
        self._subscribers[subscriber_id].append(callback)
        
        if filter_criteria:
            self._subscriber_filters[subscriber_id] = filter_criteria
        
        logger.debug(f"Subscriber {subscriber_id} registered with filters: {filter_criteria}")
    
    async def unsubscribe(self, subscriber_id: str) -> None:
        """Unsubscribe from context updates."""
        if subscriber_id in self._subscribers:
            del self._subscribers[subscriber_id]
        
        if subscriber_id in self._subscriber_filters:
            del self._subscriber_filters[subscriber_id]
        
        logger.debug(f"Subscriber {subscriber_id} unregistered")
    
    async def broadcast_update(self, update_type: str, data: Dict[str, Any]) -> None:
        """
        Manually broadcast an update to all subscribers.
        
        Args:
            update_type: Type of update (e.g., "discovery", "milestone")
            data: Update data to broadcast
        """
        await self._broadcast_update(update_type, None, None, data)
    
    # Workflow-specific methods
    
    async def add_execution_step(self, step: Dict[str, Any]) -> None:
        """Add a step to the execution history."""
        step_entry = {
            "timestamp": datetime.now(),
            "workflow_id": self.workflow_id,
            **step
        }
        self.execution_history.append(step_entry)
    
    async def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get the complete execution history."""
        return self.execution_history.copy()
    
    async def get_agent_discoveries(self, agent_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get discoveries by agent.
        
        Args:
            agent_id: Optional specific agent to filter by
            
        Returns:
            Dictionary mapping agent IDs to their discoveries
        """
        if agent_id:
            return {agent_id: self.agent_discoveries.get(agent_id, [])}
        else:
            return dict(self.agent_discoveries)
    
    async def calculate_context_relevance(self, context_key: str, 
                                        target_context: Dict[str, Any]) -> float:
        """
        Calculate relevance score between stored context and target.
        
        Args:
            context_key: Key of stored context
            target_context: Context to compare against
            
        Returns:
            Relevance score between 0 and 1
        """
        stored_data = await self.retrieve(context_key)
        if not stored_data:
            return 0.0
        
        # Simple relevance calculation based on metadata overlap
        # This can be enhanced with semantic similarity in the future
        stored_meta = self.conversation_context.get(context_key, {}).get("metadata", {})
        
        if not stored_meta or not target_context:
            return 0.5  # Neutral relevance if no metadata
        
        # Calculate overlap in metadata fields
        common_keys = set(stored_meta.keys()) & set(target_context.keys())
        if not common_keys:
            return 0.0
        
        matches = sum(1 for k in common_keys if stored_meta[k] == target_context[k])
        relevance = matches / len(common_keys)
        
        return relevance
    
    # Private helper methods
    
    def _determine_context_type(self, key: str) -> str:
        """Determine context type from key prefix."""
        if key.startswith("discovery_"):
            return "discovery"
        elif key.startswith("artifact_"):
            return "artifact"
        else:
            return "conversation"
    
    def _search_dict(self, storage: Dict[str, Dict[str, Any]], 
                     query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search a dictionary storage with query criteria."""
        results = []
        
        # Create a copy of query without agent_id for non-discovery searches
        search_query = query.copy()
        search_query.pop("agent_id", None)  # Remove agent_id as it's discovery-specific
        
        for key, entry in storage.items():
            if self._matches_query(entry, search_query):
                results.append({
                    "key": key,
                    "data": entry["data"],
                    "timestamp": entry["timestamp"],
                    "metadata": entry["metadata"]
                })
        
        return results
    
    def _matches_query(self, entry: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if entry matches query criteria."""
        # Pattern matching
        if "pattern" in query:
            key = entry.get("key", "")
            if not fnmatch.fnmatch(key, query["pattern"]):
                return False
        
        # Timestamp filtering
        if "timestamp_after" in query:
            if entry["timestamp"] <= query["timestamp_after"]:
                return False
        
        if "timestamp_before" in query:
            if entry["timestamp"] >= query["timestamp_before"]:
                return False
        
        # Metadata matching
        if "metadata" in query:
            for meta_key, meta_value in query["metadata"].items():
                if entry["metadata"].get(meta_key) != meta_value:
                    return False
        
        return True
    
    async def _broadcast_update(self, context_type: str, key: Optional[str], 
                              data: Any, metadata: Optional[Dict]) -> None:
        """Broadcast update to all relevant subscribers."""
        update = {
            "type": context_type,
            "key": key,
            "data": data,
            "metadata": metadata or {},
            "timestamp": datetime.now(),
            "workflow_id": self.workflow_id
        }
        
        # Gather tasks for concurrent notification
        tasks = []
        
        for subscriber_id, callbacks in self._subscribers.items():
            # Check if subscriber has filters
            if subscriber_id in self._subscriber_filters:
                filters = self._subscriber_filters[subscriber_id]
                
                # Apply filters
                if "context_type" in filters and filters["context_type"] != context_type:
                    continue
                
                if "agent_id" in filters and metadata:
                    if metadata.get("agent_id") != filters["agent_id"]:
                        continue
            
            # Notify all callbacks for this subscriber
            for callback in callbacks:
                tasks.append(callback(update))
        
        # Execute all notifications concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)