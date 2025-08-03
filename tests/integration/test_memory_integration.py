"""
Integration tests for memory system with agents.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock

from src.memory.shared_context import SharedContextPool
from tests.fixtures.mock_agents import MockTaskAgent, MockResearchAgent


class TestMemoryIntegration:
    """Test memory system integration with agents."""
    
    @pytest.mark.asyncio
    async def test_agent_memory_collaboration(self):
        """Test agents sharing discoveries through memory system."""
        # Create shared context
        shared_context = SharedContextPool("test_workflow")
        
        # Create agents with shared context
        task_agent = MockTaskAgent("task_agent_1")
        task_agent.shared_context = shared_context
        
        research_agent = MockResearchAgent("research_agent_1")
        research_agent.shared_context = shared_context
        
        # Agent 1 makes a discovery
        await task_agent.share_discovery(
            "bug_found",
            {"type": "null_pointer", "file": "main.py", "line": 42},
            relevance=0.9
        )
        
        # Agent 2 should be able to find it
        shared_discoveries = await research_agent.get_shared_context(
            context_type="discovery"
        )
        
        assert len(shared_discoveries) == 1
        assert shared_discoveries[0]["data"]["type"] == "null_pointer"
        assert shared_discoveries[0]["metadata"]["relevance"] == 0.9
    
    @pytest.mark.asyncio
    async def test_agent_local_memory_isolation(self):
        """Test that agent local memories are isolated."""
        agent1 = MockTaskAgent("agent1")
        agent2 = MockTaskAgent("agent2")
        
        # Store in local memory
        await agent1.store_memory("secret", "agent1_secret")
        await agent2.store_memory("secret", "agent2_secret")
        
        # Verify isolation
        assert await agent1.retrieve_memory("secret") == "agent1_secret"
        assert await agent2.retrieve_memory("secret") == "agent2_secret"
        
        # Verify no cross-contamination
        assert await agent1.retrieve_memory("agent2_data") is None
    
    @pytest.mark.asyncio
    async def test_workflow_execution_tracking(self):
        """Test tracking workflow execution through shared context."""
        shared_context = SharedContextPool("workflow_123")
        
        # Multiple agents working on workflow
        agents = [
            MockTaskAgent(f"agent_{i}", shared_context=shared_context)
            for i in range(3)
        ]
        
        # Each agent adds execution steps
        for i, agent in enumerate(agents):
            await shared_context.add_execution_step({
                "agent": agent.name,
                "step": f"step_{i}",
                "result": "success"
            })
        
        # Get execution history
        history = await shared_context.get_execution_history()
        
        assert len(history) == 3
        assert all(step["workflow_id"] == "workflow_123" for step in history)
        assert history[0]["step"] == "step_0"
    
    @pytest.mark.asyncio
    async def test_memory_lifecycle(self):
        """Test memory lifecycle from creation to cleanup."""
        shared_context = SharedContextPool("lifecycle_test")
        agent = MockTaskAgent("test_agent", shared_context=shared_context)
        
        # Store in local memory
        await agent.store_memory("task_data", {"status": "in_progress"})
        await agent.add_finding("finding_1", {"issue": "performance"})
        
        # Share discovery
        await agent.share_discovery(
            "optimization",
            {"improvement": "cache_added", "speedup": "2x"}
        )
        
        # Verify data exists
        assert await agent.retrieve_memory("task_data") is not None
        findings = await agent.get_findings()
        assert len(findings) == 1
        
        shared = await shared_context.search({"context_type": "discovery"})
        assert len(shared) == 1
        
        # Clear local memory
        await agent.clear_local_memory()
        
        # Verify local memory cleared but shared context remains
        assert await agent.retrieve_memory("task_data") is None
        findings = await agent.get_findings()
        assert len(findings) == 0
        
        shared = await shared_context.search({"context_type": "discovery"})
        assert len(shared) == 1  # Still there
        
        # Clear shared context
        await shared_context.clear()
        shared = await shared_context.search({"context_type": "discovery"})
        assert len(shared) == 0
    
    @pytest.mark.asyncio
    async def test_pub_sub_agent_communication(self):
        """Test agents communicating through pub/sub."""
        shared_context = SharedContextPool("pubsub_test")
        
        agent1 = MockTaskAgent("publisher", shared_context=shared_context)
        agent2 = MockTaskAgent("subscriber", shared_context=shared_context)
        
        # Track received updates
        received_updates = []
        
        async def update_handler(update):
            received_updates.append(update)
        
        # Subscribe agent2 to discoveries
        await shared_context.subscribe(
            "agent2_sub",
            update_handler,
            {"context_type": "discovery"}
        )
        
        # Agent1 shares discovery
        await agent1.share_discovery(
            "pattern_detected",
            {"pattern": "singleton", "confidence": 0.85}
        )
        
        # Allow async processing
        await asyncio.sleep(0.1)
        
        # Verify subscription worked
        assert len(received_updates) == 1
        assert received_updates[0]["type"] == "discovery"
        assert received_updates[0]["metadata"]["agent_name"] == "publisher"
    
    @pytest.mark.asyncio
    async def test_memory_statistics(self):
        """Test memory statistics tracking."""
        agent = MockTaskAgent("stats_agent")
        
        # Perform various operations
        for i in range(10):
            await agent.store_memory(f"key_{i}", f"data_{i}")
        
        await agent.retrieve_memory("key_5")
        await agent.retrieve_memory("non_existent")
        
        # Get statistics
        stats = await agent.get_memory_statistics()
        
        assert stats["local_memory"]["stores"] == 10
        assert stats["local_memory"]["retrieves"] == 2
        assert stats["local_memory"]["current_entries"] == 10
        assert stats["agent_name"] == "stats_agent"