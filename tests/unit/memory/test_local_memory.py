"""
Unit tests for AgentLocalMemory implementation.
"""

import pytest
from datetime import datetime, timedelta
import asyncio

from src.memory.local_memory import AgentLocalMemory


class TestAgentLocalMemory:
    """Test suite for AgentLocalMemory."""
    
    @pytest.fixture
    def local_memory(self):
        """Create a fresh local memory instance for testing."""
        return AgentLocalMemory("test_agent_123", max_entries=5, max_history=10)
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test memory initialization with correct parameters."""
        memory = AgentLocalMemory("agent_456", max_entries=100, max_history=50)
        
        assert memory.agent_id == "agent_456"
        assert memory.max_entries == 100
        assert memory.max_history == 50
        assert await memory.get_size() == 0
        assert len(memory.recent_actions) == 0
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve(self, local_memory):
        """Test basic store and retrieve operations."""
        # Store data
        await local_memory.store("key1", {"value": "test_data"})
        
        # Retrieve data
        result = await local_memory.retrieve("key1")
        assert result == {"value": "test_data"}
        
        # Retrieve non-existent key
        result = await local_memory.retrieve("non_existent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_store_with_metadata(self, local_memory):
        """Test storing data with metadata."""
        metadata = {"type": "discovery", "priority": "high"}
        await local_memory.store("key_with_meta", "data", metadata)
        
        # Search by metadata
        results = await local_memory.search({"metadata": {"type": "discovery"}})
        assert len(results) == 1
        assert results[0]["data"] == "data"
        assert results[0]["metadata"]["priority"] == "high"
    
    @pytest.mark.asyncio
    async def test_lru_eviction(self, local_memory):
        """Test LRU eviction when memory limit is reached."""
        # Fill memory to capacity
        for i in range(5):
            await local_memory.store(f"key{i}", f"data{i}")
        
        assert await local_memory.get_size() == 5
        
        # Add one more item - should evict key0
        await local_memory.store("key5", "data5")
        
        assert await local_memory.get_size() == 5
        assert await local_memory.retrieve("key0") is None  # Evicted
        assert await local_memory.retrieve("key5") == "data5"  # New item
        
        # Access key1 to make it recently used
        await local_memory.retrieve("key1")
        
        # Add another item - should evict key2 (least recently used)
        await local_memory.store("key6", "data6")
        assert await local_memory.retrieve("key2") is None
        assert await local_memory.retrieve("key1") == "data1"  # Still there
    
    @pytest.mark.asyncio
    async def test_recent_actions_tracking(self, local_memory):
        """Test tracking of recent actions."""
        # Perform various actions
        await local_memory.store("key1", "data1")
        await local_memory.retrieve("key1")
        await local_memory.retrieve("non_existent")
        await local_memory.delete("key1")
        
        # Get recent actions
        actions = await local_memory.get_recent_actions()
        
        assert len(actions) == 4
        assert actions[0]["type"] == "delete"
        assert actions[1]["type"] == "retrieve"
        assert actions[1]["found"] == False
        assert actions[2]["type"] == "retrieve"
        assert actions[2]["found"] == True
        assert actions[3]["type"] == "store"
    
    @pytest.mark.asyncio
    async def test_search_functionality(self, local_memory):
        """Test search with various criteria."""
        # Store test data
        now = datetime.now()
        past = now - timedelta(hours=1)
        
        await local_memory.store("pattern_test_1", "data1", {"type": "test"})
        await local_memory.store("pattern_test_2", "data2", {"type": "test"})
        await local_memory.store("other_key", "data3", {"type": "other"})
        
        # Search by pattern
        results = await local_memory.search({"pattern": "pattern_*"})
        assert len(results) == 2
        
        # Search by metadata type
        results = await local_memory.search({"type": "test"})
        assert len(results) == 2
        
        # Search by combined criteria
        results = await local_memory.search({
            "pattern": "pattern_*",
            "metadata": {"type": "test"}
        })
        assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_delete_operation(self, local_memory):
        """Test delete functionality."""
        await local_memory.store("to_delete", "data")
        
        # Verify it exists
        assert await local_memory.retrieve("to_delete") == "data"
        
        # Delete it
        deleted = await local_memory.delete("to_delete")
        assert deleted is True
        
        # Verify it's gone
        assert await local_memory.retrieve("to_delete") is None
        
        # Try to delete non-existent key
        deleted = await local_memory.delete("non_existent")
        assert deleted is False
    
    @pytest.mark.asyncio
    async def test_clear_operation(self, local_memory):
        """Test clearing all memory."""
        # Add data
        await local_memory.store("key1", "data1")
        await local_memory.store("key2", "data2")
        await local_memory.add_finding("finding1", "important finding")
        
        # Verify data exists
        assert await local_memory.get_size() == 2
        assert len(await local_memory.get_findings()) == 1
        
        # Clear memory
        await local_memory.clear()
        
        # Verify everything is cleared
        assert await local_memory.get_size() == 0
        assert len(await local_memory.get_findings()) == 0
        
        # But clear action should be recorded
        actions = await local_memory.get_recent_actions()
        assert len(actions) == 1
        assert actions[0]["type"] == "clear"
    
    @pytest.mark.asyncio
    async def test_list_keys(self, local_memory):
        """Test listing keys with and without pattern."""
        await local_memory.store("prefix_key1", "data1")
        await local_memory.store("prefix_key2", "data2")
        await local_memory.store("other_key", "data3")
        
        # List all keys
        all_keys = await local_memory.list_keys()
        assert len(all_keys) == 3
        assert set(all_keys) == {"prefix_key1", "prefix_key2", "other_key"}
        
        # List with pattern
        prefix_keys = await local_memory.list_keys("prefix_*")
        assert len(prefix_keys) == 2
        assert set(prefix_keys) == {"prefix_key1", "prefix_key2"}
    
    @pytest.mark.asyncio
    async def test_findings_management(self, local_memory):
        """Test temporary findings functionality."""
        # Add findings
        await local_memory.add_finding("finding1", {"type": "bug", "severity": "high"})
        await local_memory.add_finding("finding2", {"type": "performance", "metric": 0.95})
        
        # Get all findings
        findings = await local_memory.get_findings()
        assert len(findings) == 2
        assert findings["finding1"]["type"] == "bug"
        assert findings["finding2"]["metric"] == 0.95
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, local_memory):
        """Test memory statistics."""
        # Perform various operations
        for i in range(7):  # Will trigger 2 evictions
            await local_memory.store(f"key{i}", f"data{i}")
        
        await local_memory.retrieve("key6")
        await local_memory.retrieve("non_existent")
        
        stats = local_memory.get_statistics()
        
        assert stats["stores"] == 7
        assert stats["retrieves"] == 2
        assert stats["evictions"] == 2
        assert stats["clears"] == 0
        assert stats["current_entries"] == 5
        assert stats["memory_usage_percent"] == 100.0
    
    @pytest.mark.asyncio
    async def test_exists_method(self, local_memory):
        """Test checking if key exists."""
        await local_memory.store("existing_key", "data")
        
        assert await local_memory.exists("existing_key") is True
        assert await local_memory.exists("non_existent") is False
    
    @pytest.mark.asyncio
    async def test_batch_operations(self, local_memory):
        """Test batch store and retrieve."""
        # Batch store
        batch_data = {
            "batch1": "data1",
            "batch2": "data2",
            "batch3": "data3"
        }
        await local_memory.store_batch(batch_data)
        
        # Verify all stored
        assert await local_memory.get_size() == 3
        
        # Batch retrieve
        keys = ["batch1", "batch2", "batch_missing"]
        results = await local_memory.retrieve_batch(keys)
        
        assert len(results) == 2
        assert results["batch1"] == "data1"
        assert results["batch2"] == "data2"
        assert "batch_missing" not in results
    
    @pytest.mark.asyncio
    async def test_timestamp_search(self, local_memory):
        """Test searching by timestamp criteria."""
        # Store data with slight delays
        await local_memory.store("old_data", "data1")
        await asyncio.sleep(0.1)
        
        checkpoint = datetime.now()
        await asyncio.sleep(0.1)
        
        await local_memory.store("new_data", "data2")
        
        # Search for data after checkpoint
        results = await local_memory.search({"timestamp_after": checkpoint})
        assert len(results) == 1
        assert results[0]["key"] == "new_data"
        
        # Search for data before checkpoint
        results = await local_memory.search({"timestamp_before": checkpoint})
        assert len(results) == 1
        assert results[0]["key"] == "old_data"
    
    @pytest.mark.asyncio
    async def test_memory_isolation(self):
        """Test that different agent memories are isolated."""
        memory1 = AgentLocalMemory("agent1")
        memory2 = AgentLocalMemory("agent2")
        
        await memory1.store("shared_key", "data1")
        await memory2.store("shared_key", "data2")
        
        assert await memory1.retrieve("shared_key") == "data1"
        assert await memory2.retrieve("shared_key") == "data2"