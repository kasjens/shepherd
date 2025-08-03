"""
Unit tests for SharedContextPool implementation.
"""

import pytest
from datetime import datetime, timedelta
import asyncio
from unittest.mock import AsyncMock

from src.memory.shared_context import SharedContextPool


class TestSharedContextPool:
    """Test suite for SharedContextPool."""
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context instance for testing."""
        return SharedContextPool("test_workflow_123")
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test shared context initialization."""
        context = SharedContextPool("workflow_456")
        
        assert context.workflow_id == "workflow_456"
        assert await context.get_size() == 0
        assert len(context.execution_history) == 0
        assert context.metadata["workflow_id"] == "workflow_456"
        assert len(context.metadata["active_agents"]) == 0
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve(self, shared_context):
        """Test basic store and retrieve operations."""
        # Store data
        await shared_context.store("key1", {"value": "test_data"})
        
        # Retrieve data
        result = await shared_context.retrieve("key1")
        assert result == {"value": "test_data"}
        
        # Store with metadata
        metadata = {"agent_id": "agent_123", "type": "discovery"}
        await shared_context.store("key2", "data2", metadata)
        
        # Verify metadata tracking
        assert "agent_123" in shared_context.metadata["active_agents"]
        assert shared_context.metadata["total_updates"] == 2
    
    @pytest.mark.asyncio
    async def test_context_type_storage(self, shared_context):
        """Test different context types are stored appropriately."""
        # Store discovery
        await shared_context.store(
            "discovery_agent1_pattern_123",
            {"pattern": "test_pattern"},
            {"agent_id": "agent1"}
        )
        
        # Store artifact
        await shared_context.store(
            "artifact_result_456",
            {"result": "computation"},
            {"type": "output"}
        )
        
        # Store conversation context
        await shared_context.store(
            "context_current_task",
            {"task": "analyze_code"},
            {}
        )
        
        # Verify storage locations
        assert len(shared_context.agent_discoveries["agent1"]) == 1
        assert "artifact_result_456" in shared_context.workflow_artifacts
        assert "context_current_task" in shared_context.conversation_context
    
    @pytest.mark.asyncio
    async def test_search_functionality(self, shared_context):
        """Test searching with various criteria."""
        # Store test data
        await shared_context.store(
            "discovery_agent1_bug_1",
            {"bug": "null_pointer"},
            {"agent_id": "agent1", "severity": "high"}
        )
        await shared_context.store(
            "discovery_agent2_perf_1",
            {"metric": 0.95},
            {"agent_id": "agent2", "type": "performance"}
        )
        await shared_context.store(
            "artifact_report",
            {"content": "analysis report"},
            {"format": "markdown"}
        )
        
        # Search by context type
        discoveries = await shared_context.search({"context_type": "discovery"})
        assert len(discoveries) == 2
        
        # Search by agent
        agent1_items = await shared_context.search({"agent_id": "agent1"})
        assert len(agent1_items) == 1
        assert agent1_items[0]["metadata"]["severity"] == "high"
        
        # Search by pattern
        pattern_results = await shared_context.search({"pattern": "discovery_*"})
        assert len(pattern_results) == 2
    
    @pytest.mark.asyncio
    async def test_pub_sub_mechanism(self, shared_context):
        """Test publish-subscribe functionality."""
        received_updates = []
        
        # Create subscriber callback
        async def test_callback(update):
            received_updates.append(update)
        
        # Subscribe
        await shared_context.subscribe("test_subscriber", test_callback)
        
        # Store data (should trigger broadcast)
        await shared_context.store(
            "test_key",
            {"data": "test"},
            {"agent_id": "agent1"}
        )
        
        # Allow async operations to complete
        await asyncio.sleep(0.1)
        
        # Verify update received
        assert len(received_updates) == 1
        assert received_updates[0]["type"] == "conversation"
        assert received_updates[0]["key"] == "test_key"
        assert received_updates[0]["data"]["data"] == "test"
    
    @pytest.mark.asyncio
    async def test_filtered_subscriptions(self, shared_context):
        """Test subscriptions with filters."""
        discovery_updates = []
        agent1_updates = []
        
        # Subscribe with context type filter
        async def discovery_callback(update):
            discovery_updates.append(update)
        
        await shared_context.subscribe(
            "discovery_sub",
            discovery_callback,
            {"context_type": "discovery"}
        )
        
        # Subscribe with agent filter
        async def agent1_callback(update):
            agent1_updates.append(update)
        
        await shared_context.subscribe(
            "agent1_sub",
            agent1_callback,
            {"agent_id": "agent1"}
        )
        
        # Store various data
        await shared_context.store(
            "discovery_agent1_test",
            {"finding": "test"},
            {"agent_id": "agent1"}
        )
        await shared_context.store(
            "artifact_test",
            {"artifact": "data"},
            {"agent_id": "agent2"}
        )
        
        await asyncio.sleep(0.1)
        
        # Verify filtered updates
        assert len(discovery_updates) == 1
        assert len(agent1_updates) == 1
    
    @pytest.mark.asyncio
    async def test_delete_operation(self, shared_context):
        """Test deleting entries from different storage locations."""
        # Store in different locations
        await shared_context.store("discovery_test", "data1", {"agent_id": "agent1"})
        await shared_context.store("artifact_test", "data2")
        await shared_context.store("context_test", "data3")
        
        # Delete each
        assert await shared_context.delete("discovery_test") is True
        assert await shared_context.delete("artifact_test") is True
        assert await shared_context.delete("context_test") is True
        
        # Verify deletion
        assert await shared_context.retrieve("discovery_test") is None
        assert await shared_context.retrieve("artifact_test") is None
        assert await shared_context.retrieve("context_test") is None
    
    @pytest.mark.asyncio
    async def test_clear_operation(self, shared_context):
        """Test clearing all shared context."""
        # Add data
        await shared_context.store("key1", "data1", {"agent_id": "agent1"})
        await shared_context.store("key2", "data2")
        await shared_context.add_execution_step({"step": "test_step"})
        
        # Subscribe to clear notification
        clear_received = False
        
        async def clear_callback(update):
            nonlocal clear_received
            if update["type"] == "system" and update["metadata"].get("action") == "clear":
                clear_received = True
        
        await shared_context.subscribe("clear_sub", clear_callback)
        
        # Clear
        await shared_context.clear()
        await asyncio.sleep(0.1)
        
        # Verify everything cleared
        assert await shared_context.get_size() == 0
        assert len(shared_context.execution_history) == 0
        assert shared_context.metadata["total_updates"] == 0
        assert clear_received is True
    
    @pytest.mark.asyncio
    async def test_execution_history(self, shared_context):
        """Test execution history tracking."""
        # Add execution steps
        steps = [
            {"agent": "agent1", "action": "analyze", "result": "success"},
            {"agent": "agent2", "action": "validate", "result": "success"},
            {"agent": "agent1", "action": "report", "result": "completed"}
        ]
        
        for step in steps:
            await shared_context.add_execution_step(step)
        
        # Get history
        history = await shared_context.get_execution_history()
        
        assert len(history) == 3
        assert all("timestamp" in h for h in history)
        assert all("workflow_id" in h for h in history)
        assert history[0]["action"] == "analyze"
    
    @pytest.mark.asyncio
    async def test_agent_discoveries(self, shared_context):
        """Test agent discovery management."""
        # Add discoveries for different agents
        await shared_context.store(
            "discovery_agent1_1",
            {"finding": "bug1"},
            {"agent_id": "agent1"}
        )
        await shared_context.store(
            "discovery_agent1_2",
            {"finding": "bug2"},
            {"agent_id": "agent1"}
        )
        await shared_context.store(
            "discovery_agent2_1",
            {"finding": "perf1"},
            {"agent_id": "agent2"}
        )
        
        # Get all discoveries
        all_discoveries = await shared_context.get_agent_discoveries()
        assert len(all_discoveries) == 2
        assert len(all_discoveries["agent1"]) == 2
        assert len(all_discoveries["agent2"]) == 1
        
        # Get specific agent discoveries
        agent1_discoveries = await shared_context.get_agent_discoveries("agent1")
        assert len(agent1_discoveries) == 1
        assert len(agent1_discoveries["agent1"]) == 2
    
    @pytest.mark.asyncio
    async def test_context_relevance_calculation(self, shared_context):
        """Test relevance calculation between contexts."""
        # Store context with metadata
        await shared_context.store(
            "context1",
            {"data": "test"},
            {"type": "analysis", "language": "python", "complexity": "high"}
        )
        
        # Calculate relevance with similar context
        similar_context = {"type": "analysis", "language": "python"}
        relevance = await shared_context.calculate_context_relevance("context1", similar_context)
        assert relevance == 1.0  # All common keys match
        
        # Calculate relevance with partially matching context
        partial_context = {"type": "analysis", "language": "javascript"}
        relevance = await shared_context.calculate_context_relevance("context1", partial_context)
        assert relevance == 0.5  # 1 out of 2 common keys match
        
        # Calculate relevance with non-matching context
        different_context = {"category": "testing", "framework": "pytest"}
        relevance = await shared_context.calculate_context_relevance("context1", different_context)
        assert relevance == 0.0  # No common keys
    
    @pytest.mark.asyncio
    async def test_list_keys(self, shared_context):
        """Test listing keys across all storage locations."""
        # Store in different locations
        await shared_context.store("discovery_key1", "data1", {"agent_id": "agent1"})
        await shared_context.store("artifact_key2", "data2")
        await shared_context.store("context_key3", "data3")
        
        # List all keys
        all_keys = await shared_context.list_keys()
        assert len(all_keys) == 3
        assert set(all_keys) == {"discovery_key1", "artifact_key2", "context_key3"}
        
        # List with pattern
        discovery_keys = await shared_context.list_keys("discovery_*")
        assert len(discovery_keys) == 1
        assert discovery_keys[0] == "discovery_key1"
    
    @pytest.mark.asyncio
    async def test_manual_broadcast(self, shared_context):
        """Test manual broadcasting."""
        received_updates = []
        
        async def callback(update):
            received_updates.append(update)
        
        await shared_context.subscribe("test_sub", callback)
        
        # Manual broadcast
        await shared_context.broadcast_update(
            "milestone",
            {"milestone": "phase_complete", "progress": 0.5}
        )
        
        await asyncio.sleep(0.1)
        
        assert len(received_updates) == 1
        assert received_updates[0]["type"] == "milestone"
        assert received_updates[0]["metadata"]["progress"] == 0.5
    
    @pytest.mark.asyncio
    async def test_unsubscribe(self, shared_context):
        """Test unsubscribing from updates."""
        received_count = 0
        
        async def callback(update):
            nonlocal received_count
            received_count += 1
        
        # Subscribe
        await shared_context.subscribe("test_sub", callback)
        
        # Store data (should receive)
        await shared_context.store("key1", "data1")
        await asyncio.sleep(0.1)
        assert received_count == 1
        
        # Unsubscribe
        await shared_context.unsubscribe("test_sub")
        
        # Store more data (should not receive)
        await shared_context.store("key2", "data2")
        await asyncio.sleep(0.1)
        assert received_count == 1  # Still 1, no new updates
    
    @pytest.mark.asyncio
    async def test_batch_operations(self, shared_context):
        """Test batch operations inherited from BaseMemory."""
        # Batch store
        batch_data = {
            "batch1": "data1",
            "batch2": "data2",
            "batch3": "data3"
        }
        await shared_context.store_batch(batch_data)
        
        assert await shared_context.get_size() == 3
        
        # Batch retrieve
        results = await shared_context.retrieve_batch(["batch1", "batch2", "missing"])
        assert len(results) == 2
        assert results["batch1"] == "data1"
        assert results["batch2"] == "data2"
    
    @pytest.mark.asyncio
    async def test_workflow_isolation(self):
        """Test that different workflows have isolated contexts."""
        context1 = SharedContextPool("workflow1")
        context2 = SharedContextPool("workflow2")
        
        await context1.store("shared_key", "data1")
        await context2.store("shared_key", "data2")
        
        assert await context1.retrieve("shared_key") == "data1"
        assert await context2.retrieve("shared_key") == "data2"
        assert context1.metadata["workflow_id"] == "workflow1"
        assert context2.metadata["workflow_id"] == "workflow2"