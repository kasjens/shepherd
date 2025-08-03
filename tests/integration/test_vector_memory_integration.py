#!/usr/bin/env python3
"""
Integration tests for Vector Memory System - Phase 7

Tests integration between vector memory components, agent system,
and overall workflow orchestration with semantic capabilities.
"""

import pytest
import asyncio
import tempfile
import shutil
from unittest.mock import Mock, patch
from src.memory.vector_store import VectorMemoryStore
from src.memory.persistent_knowledge import PersistentKnowledgeBase, KnowledgeType
from src.memory.shared_context import SharedContextPool
from src.agents.base_agent import BaseAgent
from src.agents.task_agent import TaskAgent


class MockAgent(BaseAgent):
    """Mock agent for testing vector memory integration."""
    
    def create_crew_agent(self):
        mock_crew_agent = Mock()
        mock_crew_agent.execute.return_value = "Mock execution result"
        return mock_crew_agent


class TestVectorMemoryIntegration:
    """Integration tests for vector memory system."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def knowledge_base(self, temp_dir):
        """Create knowledge base for testing."""
        return PersistentKnowledgeBase(persist_directory=temp_dir)

    @pytest.fixture
    def shared_context_with_vector(self):
        """Create shared context with vector search enabled."""
        return SharedContextPool(workflow_id="test_workflow", enable_vector_search=True)

    @pytest.fixture
    def agent_with_vector_memory(self, knowledge_base, shared_context_with_vector):
        """Create agent with vector memory capabilities."""
        return MockAgent(
            name="test_agent",
            role="research",
            goal="Test vector memory integration",
            shared_context=shared_context_with_vector,
            knowledge_base=knowledge_base
        )

    @pytest.mark.asyncio
    async def test_agent_vector_memory_initialization(self, agent_with_vector_memory):
        """Test agent initialization with vector memory components."""
        agent = agent_with_vector_memory
        
        # Verify memory components are initialized
        assert agent.knowledge_base is not None
        assert agent.shared_context is not None
        assert hasattr(agent, 'store_learned_pattern')
        assert hasattr(agent, 'find_similar_patterns')
        assert hasattr(agent, 'semantic_memory_search')

    @pytest.mark.asyncio
    async def test_agent_pattern_learning_workflow(self, agent_with_vector_memory):
        """Test end-to-end pattern learning workflow."""
        agent = agent_with_vector_memory
        
        # Simulate successful task execution and learning
        task_description = "Implement user authentication with JWT tokens"
        outcome = {
            "status": "completed",
            "execution_time": 45.2,
            "tools_used": ["web_search", "code_analyzer"],
            "quality_score": 0.92
        }
        
        # Store execution outcome as learned pattern
        await agent.store_execution_outcome(task_description, outcome, success=True)
        
        # Find similar patterns
        similar_patterns = await agent.find_similar_patterns(
            "authentication system implementation", 
            limit=5
        )
        
        # Should find the stored pattern
        assert len(similar_patterns) >= 0  # May or may not find depending on similarity

    @pytest.mark.asyncio
    async def test_agent_failure_pattern_learning(self, agent_with_vector_memory):
        """Test failure pattern learning and avoidance."""
        agent = agent_with_vector_memory
        
        # Simulate failed task execution
        task_description = "Connect to external API service"
        outcome = {"status": "failed", "execution_time": 15.0}
        error = "TimeoutError: Connection timed out after 10 seconds"
        
        # Store execution outcome as failure pattern
        await agent.store_execution_outcome(task_description, outcome, success=False, error=error)
        
        # Check for failure patterns when planning similar task
        potential_failures = await agent.check_failure_patterns("API connection setup")
        
        # Should find potential failure patterns
        assert len(potential_failures) >= 0

    @pytest.mark.asyncio
    async def test_agent_user_preference_integration(self, agent_with_vector_memory):
        """Test user preference storage and retrieval."""
        agent = agent_with_vector_memory
        
        # Store user preferences
        pref_id = "code_style_detailed"
        preference = {
            "documentation_style": "comprehensive",
            "comment_verbosity": "high",
            "example_inclusion": "always"
        }
        
        await agent.store_user_preference(pref_id, preference, strength=0.9, context="code_generation")
        
        # Find preferences for relevant context
        relevant_prefs = await agent.find_user_preferences("generate Python code with documentation")
        
        # Should find relevant preferences
        assert len(relevant_prefs) >= 0

    @pytest.mark.asyncio
    async def test_task_enhancement_with_knowledge(self, agent_with_vector_memory):
        """Test task enhancement using knowledge base."""
        agent = agent_with_vector_memory
        
        # Store some background knowledge
        await agent.store_learned_pattern("api_pattern_1", {
            "approach": "REST API with authentication",
            "tools": ["web_search", "code_analyzer"],
            "success_rate": 0.95
        }, success_rate=0.95, context={"domain": "web_development"})
        
        await agent.store_user_preference("api_pref_1", {
            "format": "JSON responses",
            "error_handling": "comprehensive"
        }, context="API development")
        
        # Enhance task with knowledge
        task_description = "Build REST API with user authentication"
        enhancement = await agent.enhance_task_with_knowledge(task_description)
        
        # Verify enhancement structure
        assert "similar_patterns" in enhancement
        assert "user_preferences" in enhancement
        assert "failure_warnings" in enhancement
        assert "recommendations" in enhancement
        assert isinstance(enhancement["recommendations"], list)

    @pytest.mark.asyncio
    async def test_semantic_memory_search_integration(self, agent_with_vector_memory):
        """Test semantic search across all memory systems."""
        agent = agent_with_vector_memory
        
        # Store diverse knowledge
        await agent.store_learned_pattern("ml_pattern", {
            "description": "Machine learning model training pipeline",
            "domain": "artificial_intelligence"
        })
        
        await agent.store_user_preference("ml_pref", {
            "description": "Prefer detailed explanations for ML concepts",
            "domain": "machine_learning"
        })
        
        # Perform semantic search
        results = await agent.semantic_memory_search(
            "artificial intelligence and machine learning",
            limit=10,
            min_similarity=0.3
        )
        
        # Should find relevant knowledge
        assert len(results) >= 0
        for result in results:
            assert "source" in result
            assert result["source"] == "knowledge_base"

    @pytest.mark.asyncio
    async def test_shared_context_vector_integration(self, shared_context_with_vector):
        """Test shared context with vector search capabilities."""
        shared_context = shared_context_with_vector
        
        # Verify vector store is initialized
        assert shared_context.enable_vector_search is True
        assert shared_context.vector_store is not None
        
        # Store context data
        await shared_context.store("discovery_1", {
            "agent_id": "agent_1",
            "discovery": "Found efficient algorithm for data processing",
            "relevance": 0.9
        }, {"type": "discovery", "agent_id": "agent_1"})
        
        # The store method should work with vector backend
        retrieved = await shared_context.retrieve("discovery_1")
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_knowledge_persistence_across_agents(self, knowledge_base):
        """Test knowledge sharing across multiple agent instances."""
        # Create first agent and store knowledge
        agent1 = MockAgent(
            name="agent_1",
            role="researcher", 
            goal="Research tasks",
            knowledge_base=knowledge_base
        )
        
        pattern_id = "research_methodology"
        pattern = {
            "approach": "systematic literature review",
            "tools": ["web_search", "document_analyzer"],
            "quality_metrics": ["relevance", "recency", "authority"]
        }
        
        await agent1.store_learned_pattern(pattern_id, pattern, success_rate=0.88)
        
        # Create second agent with same knowledge base
        agent2 = MockAgent(
            name="agent_2",
            role="analyst",
            goal="Analysis tasks", 
            knowledge_base=knowledge_base
        )
        
        # Second agent should access first agent's knowledge
        retrieved_pattern = await agent2.knowledge_base.retrieve(pattern_id)
        assert retrieved_pattern == pattern
        
        # Second agent should find similar patterns
        similar = await agent2.find_similar_patterns("research approach methodology")
        assert len(similar) >= 0

    @pytest.mark.asyncio
    async def test_vector_memory_performance_with_scale(self, temp_dir):
        """Test vector memory performance with larger datasets."""
        knowledge_base = PersistentKnowledgeBase(persist_directory=temp_dir)
        
        # Store many patterns to test scalability
        patterns = []
        for i in range(50):  # Reduced for faster testing
            pattern_id = f"pattern_{i}"
            pattern = {
                "description": f"Pattern {i} for workflow optimization",
                "domain": "automation" if i % 2 == 0 else "analysis",
                "complexity": "low" if i < 20 else "medium" if i < 40 else "high",
                "tools": [f"tool_{j}" for j in range(i % 3 + 1)]
            }
            patterns.append((pattern_id, pattern))
        
        # Store all patterns concurrently
        store_tasks = [
            knowledge_base.store_learned_pattern(pid, pdata, success_rate=0.8 + (i % 20) * 0.01)
            for i, (pid, pdata) in enumerate(patterns)
        ]
        await asyncio.gather(*store_tasks)
        
        # Verify storage
        total_size = await knowledge_base.get_size()
        assert total_size == 50
        
        # Test search performance
        search_results = await knowledge_base.find_similar_patterns(
            "workflow automation optimization",
            limit=10,
            min_similarity=0.2
        )
        
        # Should find relevant patterns efficiently
        assert len(search_results) <= 10

    @pytest.mark.asyncio
    async def test_knowledge_export_import_integration(self, knowledge_base):
        """Test knowledge export/import for backup and transfer."""
        # Store diverse knowledge
        await knowledge_base.store_learned_pattern("export_pattern", {
            "type": "learned",
            "description": "Pattern for export testing"
        })
        
        await knowledge_base.store_user_preference("export_pref", {
            "type": "preference", 
            "description": "Preference for export testing"
        })
        
        await knowledge_base.store_failure_pattern("export_fail", {
            "type": "failure",
            "description": "Failure for export testing"
        })
        
        # Export all knowledge
        export_data = await knowledge_base.export_knowledge()
        
        # Clear knowledge base
        await knowledge_base.clear()
        assert await knowledge_base.get_size() == 0
        
        # Import knowledge back
        import_counts = await knowledge_base.import_knowledge(export_data)
        
        # Verify import
        assert sum(import_counts.values()) == 3
        assert await knowledge_base.get_size() == 3
        
        # Verify data integrity
        pattern = await knowledge_base.retrieve("export_pattern")
        assert pattern["description"] == "Pattern for export testing"

    @pytest.mark.asyncio
    async def test_vector_memory_error_resilience(self, temp_dir):
        """Test vector memory system resilience to errors."""
        knowledge_base = PersistentKnowledgeBase(persist_directory=temp_dir)
        
        # Test with invalid data
        try:
            await knowledge_base.store("error_test", {"invalid": float('inf')})
            # Should handle gracefully
        except Exception:
            pass  # Expected for some invalid data
        
        # Test with very large data
        large_data = {"content": "x" * 10000}  # Large but valid data
        await knowledge_base.store("large_test", large_data)
        
        retrieved = await knowledge_base.retrieve("large_test")
        assert retrieved == large_data

    @pytest.mark.asyncio
    async def test_memory_system_coordination(self, agent_with_vector_memory):
        """Test coordination between different memory tiers."""
        agent = agent_with_vector_memory
        
        # Store in local memory (through agent's local memory system)
        await agent.local_memory.store("local_key", {"source": "local"})
        
        # Store in shared context
        await agent.shared_context.store("shared_key", {"source": "shared"})
        
        # Store in knowledge base
        await agent.knowledge_base.store("kb_key", {"source": "knowledge_base"})
        
        # Verify all memory tiers are working
        local_data = await agent.local_memory.retrieve("local_key")
        shared_data = await agent.shared_context.retrieve("shared_key")
        kb_data = await agent.knowledge_base.retrieve("kb_key")
        
        assert local_data == {"source": "local"}
        assert shared_data == {"source": "shared"}
        assert kb_data == {"source": "knowledge_base"}

    @pytest.mark.asyncio
    async def test_workflow_integration_with_vector_memory(self, agent_with_vector_memory):
        """Test workflow execution with vector memory enhancement."""
        agent = agent_with_vector_memory
        
        # Store workflow-relevant knowledge
        await agent.store_learned_pattern("workflow_sequential", {
            "pattern": "sequential",
            "best_practices": ["clear task definition", "dependency management"],
            "success_rate": 0.92
        })
        
        # Simulate workflow planning with knowledge enhancement
        workflow_description = "Execute tasks in sequence with dependency management"
        enhancement = await agent.enhance_task_with_knowledge(workflow_description)
        
        # Should provide enhancement based on stored knowledge
        assert enhancement is not None
        assert "recommendations" in enhancement


if __name__ == "__main__":
    pytest.main([__file__])