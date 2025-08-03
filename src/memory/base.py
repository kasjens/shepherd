"""
Base memory interface for Shepherd agent memory system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime


class BaseMemory(ABC):
    """
    Abstract base class for all memory implementations.
    
    Defines the interface that all memory stores must implement,
    enabling consistent storage and retrieval across different
    memory tiers.
    """
    
    @abstractmethod
    async def store(self, key: str, data: Any, metadata: Optional[Dict] = None) -> None:
        """
        Store data in memory with an associated key.
        
        Args:
            key: Unique identifier for the stored data
            data: The data to store (any serializable type)
            metadata: Optional metadata about the stored data
        """
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve data from memory by key.
        
        Args:
            key: The key to look up
            
        Returns:
            The stored data if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search memory based on query criteria.
        
        Args:
            query: Dictionary containing search criteria
                  Examples: {"type": "discovery", "agent": "research_agent"}
                           {"timestamp_after": datetime, "relevance_min": 0.7}
        
        Returns:
            List of matching memory entries with their metadata
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete a memory entry by key.
        
        Args:
            key: The key to delete
            
        Returns:
            True if deleted, False if key not found
        """
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """
        Clear all entries from this memory store.
        
        Use with caution - this operation cannot be undone.
        """
        pass
    
    @abstractmethod
    async def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        List all keys in the memory store.
        
        Args:
            pattern: Optional pattern to filter keys (e.g., "discovery_*")
            
        Returns:
            List of keys matching the pattern (or all keys if no pattern)
        """
        pass
    
    @abstractmethod
    async def get_size(self) -> int:
        """
        Get the number of entries in the memory store.
        
        Returns:
            Number of stored entries
        """
        pass
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in the memory store.
        
        Args:
            key: The key to check
            
        Returns:
            True if key exists, False otherwise
        """
        result = await self.retrieve(key)
        return result is not None
    
    async def store_batch(self, entries: Dict[str, Any]) -> None:
        """
        Store multiple entries at once.
        
        Args:
            entries: Dictionary mapping keys to data
        """
        for key, data in entries.items():
            await self.store(key, data)
    
    async def retrieve_batch(self, keys: List[str]) -> Dict[str, Any]:
        """
        Retrieve multiple entries at once.
        
        Args:
            keys: List of keys to retrieve
            
        Returns:
            Dictionary mapping keys to their data (missing keys omitted)
        """
        results = {}
        for key in keys:
            data = await self.retrieve(key)
            if data is not None:
                results[key] = data
        return results