"""
Persistent knowledge base using vector memory for semantic storage and retrieval.

This module implements long-term knowledge storage for learned patterns,
user preferences, domain knowledge, and failure patterns using semantic
vector embeddings for intelligent retrieval.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import logging

from .base import BaseMemory
from .vector_store import VectorMemoryStore

logger = logging.getLogger(__name__)


class KnowledgeType(Enum):
    """Types of knowledge stored in the persistent knowledge base."""
    LEARNED_PATTERN = "learned_pattern"
    USER_PREFERENCE = "user_preference"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    FAILURE_PATTERN = "failure_pattern"
    WORKFLOW_TEMPLATE = "workflow_template"
    AGENT_BEHAVIOR = "agent_behavior"


class PersistentKnowledgeBase(BaseMemory):
    """
    Persistent knowledge base using vector embeddings for semantic storage.
    
    This class provides long-term storage for different types of knowledge
    with semantic search capabilities, enabling the system to learn and
    improve over time.
    """
    
    def __init__(self, persist_directory: str = "data/knowledge_base"):
        """
        Initialize the persistent knowledge base.
        
        Args:
            persist_directory: Directory to persist the knowledge base
        """
        self.persist_directory = persist_directory
        
        # Initialize separate vector stores for different knowledge types
        self.stores = {}
        for knowledge_type in KnowledgeType:
            collection_name = f"shepherd_{knowledge_type.value}"
            self.stores[knowledge_type] = VectorMemoryStore(
                collection_name=collection_name,
                persist_directory=persist_directory
            )
        
        logger.info(f"Initialized persistent knowledge base with {len(self.stores)} stores")
    
    async def store(self, key: str, data: Any, metadata: Optional[Dict] = None) -> None:
        """
        Store knowledge with automatic type detection.
        
        Args:
            key: Unique identifier for the knowledge
            data: The knowledge data to store
            metadata: Optional metadata including 'knowledge_type'
        """
        # Determine knowledge type from metadata or key
        knowledge_type = self._determine_knowledge_type(key, data, metadata)
        
        # Add knowledge type to metadata
        storage_metadata = {
            "knowledge_type": knowledge_type.value,
            "storage_key": key,
            **(metadata or {})
        }
        
        # Store in appropriate vector store
        await self.stores[knowledge_type].store(key, data, storage_metadata)
        
        logger.debug(f"Stored knowledge: {key} as {knowledge_type.value}")
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve knowledge by key from all stores.
        
        Args:
            key: The key to look up
            
        Returns:
            The stored knowledge if found, None otherwise
        """
        # Search across all stores for the key
        for knowledge_type, store in self.stores.items():
            result = await store.retrieve(key)
            if result is not None:
                return result
        
        return None
    
    async def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search knowledge across all stores or specific types.
        
        Args:
            query: Search criteria including optional 'knowledge_types' filter
        
        Returns:
            List of matching knowledge entries with scores
        """
        knowledge_types = query.get("knowledge_types")
        if knowledge_types:
            # Search only specified types
            if isinstance(knowledge_types, str):
                knowledge_types = [knowledge_types]
            stores_to_search = [
                self.stores[KnowledgeType(kt)] for kt in knowledge_types
                if kt in [t.value for t in KnowledgeType]
            ]
        else:
            # Search all stores
            stores_to_search = list(self.stores.values())
        
        # Remove knowledge_types from query for vector search
        search_query = {k: v for k, v in query.items() if k != "knowledge_types"}
        
        # Search across selected stores
        all_results = []
        for store in stores_to_search:
            results = await store.search(search_query)
            all_results.extend(results)
        
        # Sort by similarity and limit if specified
        all_results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        limit = query.get("limit", len(all_results))
        return all_results[:limit]
    
    async def delete(self, key: str) -> bool:
        """
        Delete knowledge by key from all stores.
        
        Args:
            key: The key to delete
            
        Returns:
            True if any entries were deleted, False otherwise
        """
        deleted = False
        for store in self.stores.values():
            if await store.delete(key):
                deleted = True
        
        return deleted
    
    async def clear(self) -> None:
        """
        Clear all knowledge from all stores.
        """
        for store in self.stores.values():
            await store.clear()
        
        logger.info("Cleared all knowledge from persistent knowledge base")
    
    async def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        List all unique keys across all stores.
        
        Args:
            pattern: Optional pattern to filter keys
            
        Returns:
            List of unique keys
        """
        all_keys = set()
        for store in self.stores.values():
            keys = await store.list_keys(pattern)
            all_keys.update(keys)
        
        return sorted(list(all_keys))
    
    async def get_size(self) -> int:
        """
        Get total number of knowledge entries across all stores.
        
        Returns:
            Total number of stored entries
        """
        total_size = 0
        for store in self.stores.values():
            total_size += await store.get_size()
        
        return total_size
    
    def _determine_knowledge_type(self, key: str, data: Any, 
                                 metadata: Optional[Dict] = None) -> KnowledgeType:
        """
        Determine the knowledge type based on key, data, and metadata.
        
        Args:
            key: Storage key
            data: Data being stored
            metadata: Optional metadata
            
        Returns:
            Determined knowledge type
        """
        # Check explicit metadata
        if metadata and "knowledge_type" in metadata:
            try:
                return KnowledgeType(metadata["knowledge_type"])
            except ValueError:
                pass
        
        # Infer from key patterns
        key_lower = key.lower()
        if "pattern" in key_lower and "fail" in key_lower:
            return KnowledgeType.FAILURE_PATTERN
        elif "preference" in key_lower or "user" in key_lower:
            return KnowledgeType.USER_PREFERENCE
        elif "workflow" in key_lower or "template" in key_lower:
            return KnowledgeType.WORKFLOW_TEMPLATE
        elif "agent" in key_lower and "behavior" in key_lower:
            return KnowledgeType.AGENT_BEHAVIOR
        elif "pattern" in key_lower or "learned" in key_lower:
            return KnowledgeType.LEARNED_PATTERN
        
        # Infer from data structure
        if isinstance(data, dict):
            data_str = json.dumps(data).lower()
            if "error" in data_str or "failure" in data_str:
                return KnowledgeType.FAILURE_PATTERN
            elif "workflow" in data_str:
                return KnowledgeType.WORKFLOW_TEMPLATE
            elif "agent" in data_str:
                return KnowledgeType.AGENT_BEHAVIOR
        
        # Default to learned pattern
        return KnowledgeType.LEARNED_PATTERN
    
    # Specialized methods for different knowledge types
    
    async def store_learned_pattern(self, pattern_id: str, pattern: Dict[str, Any],
                                   success_rate: float = 1.0,
                                   context: Optional[Dict] = None) -> None:
        """
        Store a learned workflow pattern.
        
        Args:
            pattern_id: Unique identifier for the pattern
            pattern: Pattern data including workflow steps, agent sequence, etc.
            success_rate: Success rate of this pattern (0.0 to 1.0)
            context: Context in which this pattern was successful
        """
        metadata = {
            "knowledge_type": KnowledgeType.LEARNED_PATTERN.value,
            "success_rate": success_rate,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "pattern_type": pattern.get("workflow_type", "unknown")
        }
        
        await self.stores[KnowledgeType.LEARNED_PATTERN].store(
            pattern_id, pattern, metadata
        )
    
    async def store_user_preference(self, preference_id: str, preference: Dict[str, Any],
                                   strength: float = 1.0,
                                   context: Optional[str] = None) -> None:
        """
        Store a user preference.
        
        Args:
            preference_id: Unique identifier for the preference
            preference: Preference data
            strength: Strength of the preference (0.0 to 1.0)
            context: Context where this preference applies
        """
        metadata = {
            "knowledge_type": KnowledgeType.USER_PREFERENCE.value,
            "strength": strength,
            "context": context or "general",
            "timestamp": datetime.now().isoformat()
        }
        
        await self.stores[KnowledgeType.USER_PREFERENCE].store(
            preference_id, preference, metadata
        )
    
    async def store_failure_pattern(self, failure_id: str, failure_data: Dict[str, Any],
                                   error_type: Optional[str] = None) -> None:
        """
        Store a failure pattern to avoid in the future.
        
        Args:
            failure_id: Unique identifier for the failure
            failure_data: Data about the failure including context
            error_type: Type of error that occurred
        """
        metadata = {
            "knowledge_type": KnowledgeType.FAILURE_PATTERN.value,
            "error_type": error_type or "unknown",
            "timestamp": datetime.now().isoformat(),
            "severity": failure_data.get("severity", "medium")
        }
        
        await self.stores[KnowledgeType.FAILURE_PATTERN].store(
            failure_id, failure_data, metadata
        )
    
    async def find_similar_patterns(self, context: str, pattern_type: str = "learned",
                                   limit: int = 5, min_similarity: float = 0.6) -> List[Dict]:
        """
        Find patterns similar to the given context.
        
        Args:
            context: Context description to find similar patterns for
            pattern_type: Type of pattern to search ("learned", "failure", etc.)
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of similar patterns with similarity scores
        """
        try:
            knowledge_type = KnowledgeType(f"{pattern_type}_pattern")
        except ValueError:
            knowledge_type = KnowledgeType.LEARNED_PATTERN
        
        return await self.stores[knowledge_type].search({
            "text": context,
            "limit": limit,
            "min_similarity": min_similarity
        })
    
    async def find_user_preferences(self, context: str, limit: int = 10) -> List[Dict]:
        """
        Find user preferences relevant to the given context.
        
        Args:
            context: Context to find preferences for
            limit: Maximum number of results
            
        Returns:
            List of relevant user preferences
        """
        return await self.stores[KnowledgeType.USER_PREFERENCE].search({
            "text": context,
            "limit": limit,
            "min_similarity": 0.4  # Lower threshold for preferences
        })
    
    async def check_failure_patterns(self, context: str, limit: int = 5) -> List[Dict]:
        """
        Check for failure patterns that might apply to the given context.
        
        Args:
            context: Context to check for potential failures
            limit: Maximum number of results
            
        Returns:
            List of relevant failure patterns to avoid
        """
        return await self.stores[KnowledgeType.FAILURE_PATTERN].search({
            "text": context,
            "limit": limit,
            "min_similarity": 0.5
        })
    
    async def get_knowledge_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the knowledge base.
        
        Returns:
            Dictionary with statistics for each knowledge type
        """
        stats = {
            "total_entries": 0,
            "by_type": {},
            "overall": {
                "oldest_entry": None,
                "newest_entry": None
            }
        }
        
        all_timestamps = []
        
        for knowledge_type, store in self.stores.items():
            store_stats = await store.get_statistics()
            stats["by_type"][knowledge_type.value] = store_stats
            stats["total_entries"] += store_stats.get("total_entries", 0)
            
            # Collect timestamps
            if store_stats.get("oldest_entry"):
                all_timestamps.append(store_stats["oldest_entry"])
            if store_stats.get("newest_entry"):
                all_timestamps.append(store_stats["newest_entry"])
        
        if all_timestamps:
            stats["overall"]["oldest_entry"] = min(all_timestamps)
            stats["overall"]["newest_entry"] = max(all_timestamps)
        
        return stats
    
    async def export_knowledge(self, knowledge_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Export knowledge for backup or transfer.
        
        Args:
            knowledge_types: Optional list of knowledge types to export
            
        Returns:
            Dictionary containing exported knowledge
        """
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "knowledge": {}
        }
        
        types_to_export = knowledge_types or [t.value for t in KnowledgeType]
        
        for knowledge_type in types_to_export:
            try:
                kt = KnowledgeType(knowledge_type)
                store = self.stores[kt]
                
                # Get all entries for this type
                results = await store.search({"limit": 10000})  # Large limit
                export_data["knowledge"][knowledge_type] = results
                
            except (ValueError, KeyError):
                logger.warning(f"Unknown knowledge type for export: {knowledge_type}")
        
        return export_data
    
    async def import_knowledge(self, import_data: Dict[str, Any],
                              overwrite: bool = False) -> Dict[str, int]:
        """
        Import knowledge from exported data.
        
        Args:
            import_data: Data from export_knowledge()
            overwrite: Whether to overwrite existing entries
            
        Returns:
            Dictionary with import counts by knowledge type
        """
        import_counts = {}
        
        knowledge_data = import_data.get("knowledge", {})
        
        for knowledge_type, entries in knowledge_data.items():
            try:
                kt = KnowledgeType(knowledge_type)
                store = self.stores[kt]
                count = 0
                
                for entry in entries:
                    key = entry.get("key", f"imported_{datetime.now().timestamp()}")
                    data = entry.get("data")
                    metadata = entry.get("metadata", {})
                    
                    # Check if entry exists
                    if not overwrite and await store.retrieve(key):
                        continue
                    
                    await store.store(key, data, metadata)
                    count += 1
                
                import_counts[knowledge_type] = count
                
            except (ValueError, KeyError) as e:
                logger.error(f"Failed to import knowledge type {knowledge_type}: {e}")
        
        return import_counts