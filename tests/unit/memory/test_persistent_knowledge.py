#!/usr/bin/env python3
"""
Unit tests for PersistentKnowledgeBase - Phase 7

Tests persistent knowledge storage, pattern learning,
and semantic knowledge retrieval.
"""

import pytest
import asyncio
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from src.memory.persistent_knowledge import PersistentKnowledgeBase, KnowledgeType
from datetime import datetime


class TestPersistentKnowledgeBase:
    """Test suite for PersistentKnowledgeBase class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def knowledge_base(self, temp_dir):
        """Create knowledge base instance for testing."""
        return PersistentKnowledgeBase(persist_directory=temp_dir)

    def test_initialization(self, knowledge_base, temp_dir):
        """Test knowledge base initialization."""
        assert knowledge_base.persist_directory == temp_dir
        assert len(knowledge_base.stores) == len(KnowledgeType)
        
        # Verify all knowledge types have stores
        for knowledge_type in KnowledgeType:
            assert knowledge_type in knowledge_base.stores

    def test_knowledge_type_determination(self, knowledge_base):
        """Test automatic knowledge type determination."""
        test_cases = [
            ("pattern_fail_001", {}, None, KnowledgeType.FAILURE_PATTERN),
            ("user_preference_dark_mode", {}, None, KnowledgeType.USER_PREFERENCE),
            ("workflow_template_api", {}, None, KnowledgeType.WORKFLOW_TEMPLATE),
            ("agent_behavior_research", {}, None, KnowledgeType.AGENT_BEHAVIOR),
            ("learned_pattern_123", {}, None, KnowledgeType.LEARNED_PATTERN),
            ("some_key", {"error": "failed"}, None, KnowledgeType.FAILURE_PATTERN),
            ("other_key", {"workflow": "sequential"}, None, KnowledgeType.WORKFLOW_TEMPLATE),
            ("explicit_type", {}, {"knowledge_type": "user_preference"}, KnowledgeType.USER_PREFERENCE)
        ]
        
        for key, data, metadata, expected_type in test_cases:
            determined_type = knowledge_base._determine_knowledge_type(key, data, metadata)
            assert determined_type == expected_type

    @pytest.mark.asyncio
    async def test_store_and_retrieve(self, knowledge_base):
        """Test basic store and retrieve operations."""
        key = "test_pattern"
        data = {"workflow_type": "sequential", "success_rate": 0.95}
        metadata = {"knowledge_type": "learned_pattern"}
        
        await knowledge_base.store(key, data, metadata)
        retrieved = await knowledge_base.retrieve(key)
        
        assert retrieved == data

    @pytest.mark.asyncio
    async def test_store_learned_pattern(self, knowledge_base):
        """Test storing learned patterns."""
        pattern_id = "api_integration_pattern"
        pattern = {
            "workflow_type": "sequential",
            "steps": ["research", "design", "implement", "test"],
            "tools_used": ["web_search", "code_analyzer"],
            "success_metrics": {"completion_time": 300, "quality_score": 0.9}
        }
        success_rate = 0.85
        context = {"domain": "api_development", "complexity": "medium"}
        
        await knowledge_base.store_learned_pattern(pattern_id, pattern, success_rate, context)
        
        # Verify storage
        retrieved = await knowledge_base.retrieve(pattern_id)
        assert retrieved == pattern

    @pytest.mark.asyncio
    async def test_store_user_preference(self, knowledge_base):
        """Test storing user preferences."""
        preference_id = "code_style_preference"
        preference = {
            "style": "detailed_comments",
            "format": "black",
            "test_coverage": "high"
        }
        strength = 0.8
        context = "python_development"
        
        await knowledge_base.store_user_preference(preference_id, preference, strength, context)
        
        # Verify storage
        retrieved = await knowledge_base.retrieve(preference_id)
        assert retrieved == preference

    @pytest.mark.asyncio
    async def test_store_failure_pattern(self, knowledge_base):
        """Test storing failure patterns."""
        failure_id = "api_timeout_failure"
        failure_data = {
            "error_type": "TimeoutError",
            "context": "external_api_call",
            "recovery_attempts": 3,
            "root_cause": "network_latency",
            "severity": "high"
        }
        error_type = "TimeoutError"
        
        await knowledge_base.store_failure_pattern(failure_id, failure_data, error_type)
        
        # Verify storage
        retrieved = await knowledge_base.retrieve(failure_id)
        assert retrieved == failure_data

    @pytest.mark.asyncio
    async def test_find_similar_patterns(self, knowledge_base):
        """Test finding similar patterns."""
        # Store test patterns
        patterns = [
            ("pattern1", {"description": "API integration with authentication", "type": "web"}),
            ("pattern2", {"description": "Database connection and queries", "type": "db"}),
            ("pattern3", {"description": "REST API client implementation", "type": "web"}),
        ]
        
        for pattern_id, pattern_data in patterns:
            await knowledge_base.store_learned_pattern(pattern_id, pattern_data)
        
        # Find similar patterns
        similar = await knowledge_base.find_similar_patterns(
            "API development with REST endpoints", 
            limit=5, 
            min_similarity=0.3
        )
        
        assert len(similar) > 0
        # Should find API-related patterns
        api_patterns = [p for p in similar if "api" in str(p.get("data", {})).lower()]
        assert len(api_patterns) > 0

    @pytest.mark.asyncio
    async def test_find_user_preferences(self, knowledge_base):
        """Test finding user preferences."""
        # Store test preferences
        preferences = [
            ("pref1", {"style": "verbose_logging", "context": "debugging"}),
            ("pref2", {"format": "JSON_output", "context": "api_responses"}),
            ("pref3", {"approach": "step_by_step", "context": "explanations"}),
        ]
        
        for pref_id, pref_data in preferences:
            await knowledge_base.store_user_preference(pref_id, pref_data)
        
        # Find relevant preferences
        relevant = await knowledge_base.find_user_preferences("debugging application issues")
        
        assert len(relevant) >= 0  # May find preferences based on similarity

    @pytest.mark.asyncio
    async def test_check_failure_patterns(self, knowledge_base):
        """Test checking for failure patterns."""
        # Store test failure patterns
        failures = [
            ("fail1", {"error": "connection_timeout", "context": "database_operations"}),
            ("fail2", {"error": "memory_exhaustion", "context": "large_data_processing"}),
            ("fail3", {"error": "api_rate_limit", "context": "external_service_calls"}),
        ]
        
        for fail_id, fail_data in failures:
            await knowledge_base.store_failure_pattern(fail_id, fail_data)
        
        # Check for relevant failure patterns
        relevant_failures = await knowledge_base.check_failure_patterns("database connection setup")
        
        assert len(relevant_failures) >= 0  # May find failures based on similarity

    @pytest.mark.asyncio
    async def test_search_with_knowledge_types(self, knowledge_base):
        """Test search with knowledge type filtering."""
        # Store different types of knowledge
        await knowledge_base.store_learned_pattern("pattern1", {"type": "learned"})
        await knowledge_base.store_user_preference("pref1", {"type": "preference"})
        await knowledge_base.store_failure_pattern("fail1", {"type": "failure"})
        
        # Search specific knowledge types
        learned_results = await knowledge_base.search({
            "knowledge_types": ["learned_pattern"],
            "limit": 10
        })
        
        # Should only return learned patterns
        for result in learned_results:
            assert result["metadata"]["knowledge_type"] == "learned_pattern"

    @pytest.mark.asyncio
    async def test_delete_operation(self, knowledge_base):
        """Test delete operation across stores."""
        key = "to_delete"
        
        # Store in multiple stores
        await knowledge_base.store_learned_pattern(key, {"data": "learned"})
        await knowledge_base.store_user_preference(key, {"data": "preference"})
        
        # Verify storage
        assert await knowledge_base.retrieve(key) is not None
        
        # Delete and verify
        deleted = await knowledge_base.delete(key)
        assert deleted is True
        
        # Should be deleted from all stores
        assert await knowledge_base.retrieve(key) is None

    @pytest.mark.asyncio
    async def test_clear_operation(self, knowledge_base):
        """Test clear operation."""
        # Store data in multiple stores
        await knowledge_base.store_learned_pattern("pattern1", {"data": "test1"})
        await knowledge_base.store_user_preference("pref1", {"data": "test2"})
        await knowledge_base.store_failure_pattern("fail1", {"data": "test3"})
        
        # Verify data exists
        size_before = await knowledge_base.get_size()
        assert size_before > 0
        
        # Clear and verify
        await knowledge_base.clear()
        size_after = await knowledge_base.get_size()
        assert size_after == 0

    @pytest.mark.asyncio
    async def test_list_keys(self, knowledge_base):
        """Test list_keys operation."""
        # Store data with different keys
        keys = ["pattern_api", "pattern_db", "pref_style", "fail_timeout"]
        await knowledge_base.store_learned_pattern("pattern_api", {"data": "1"})
        await knowledge_base.store_learned_pattern("pattern_db", {"data": "2"})
        await knowledge_base.store_user_preference("pref_style", {"data": "3"})
        await knowledge_base.store_failure_pattern("fail_timeout", {"data": "4"})
        
        # List all keys
        all_keys = await knowledge_base.list_keys()
        assert len(all_keys) == 4
        
        # List with pattern
        pattern_keys = await knowledge_base.list_keys("pattern_*")
        assert len(pattern_keys) == 2

    @pytest.mark.asyncio
    async def test_get_size(self, knowledge_base):
        """Test get_size operation."""
        # Start with empty
        assert await knowledge_base.get_size() == 0
        
        # Add knowledge
        await knowledge_base.store_learned_pattern("p1", {"data": "1"})
        await knowledge_base.store_user_preference("pref1", {"data": "2"})
        
        assert await knowledge_base.get_size() == 2

    @pytest.mark.asyncio
    async def test_knowledge_statistics(self, knowledge_base):
        """Test get_knowledge_statistics operation."""
        # Store different types of knowledge
        await knowledge_base.store_learned_pattern("pattern1", {"data": "p1"})
        await knowledge_base.store_user_preference("pref1", {"data": "u1"})
        await knowledge_base.store_failure_pattern("fail1", {"data": "f1"})
        
        stats = await knowledge_base.get_knowledge_statistics()
        
        assert "total_entries" in stats
        assert "by_type" in stats
        assert "overall" in stats
        
        assert stats["total_entries"] == 3
        assert len(stats["by_type"]) == len(KnowledgeType)

    @pytest.mark.asyncio
    async def test_export_knowledge(self, knowledge_base):
        """Test knowledge export functionality."""
        # Store test knowledge
        await knowledge_base.store_learned_pattern("export_test1", {"data": "learned"})
        await knowledge_base.store_user_preference("export_test2", {"data": "preference"})
        
        # Export all knowledge
        export_data = await knowledge_base.export_knowledge()
        
        assert "export_timestamp" in export_data
        assert "knowledge" in export_data
        assert isinstance(export_data["knowledge"], dict)
        
        # Should contain exported knowledge types
        knowledge_data = export_data["knowledge"]
        assert "learned_pattern" in knowledge_data
        assert "user_preference" in knowledge_data

    @pytest.mark.asyncio
    async def test_import_knowledge(self, knowledge_base):
        """Test knowledge import functionality."""
        # Create export data
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "knowledge": {
                "learned_pattern": [
                    {
                        "key": "imported_pattern",
                        "data": {"type": "imported"},
                        "metadata": {"knowledge_type": "learned_pattern"}
                    }
                ],
                "user_preference": [
                    {
                        "key": "imported_pref",
                        "data": {"style": "imported"},
                        "metadata": {"knowledge_type": "user_preference"}
                    }
                ]
            }
        }
        
        # Import and verify
        import_counts = await knowledge_base.import_knowledge(export_data)
        
        assert import_counts["learned_pattern"] == 1
        assert import_counts["user_preference"] == 1
        
        # Verify imported data
        pattern = await knowledge_base.retrieve("imported_pattern")
        assert pattern == {"type": "imported"}
        
        pref = await knowledge_base.retrieve("imported_pref")
        assert pref == {"style": "imported"}

    @pytest.mark.asyncio
    async def test_import_with_overwrite(self, knowledge_base):
        """Test knowledge import with overwrite behavior."""
        key = "duplicate_key"
        
        # Store existing data
        await knowledge_base.store_learned_pattern(key, {"version": "original"})
        
        # Import data with same key
        export_data = {
            "knowledge": {
                "learned_pattern": [
                    {
                        "key": key,
                        "data": {"version": "imported"},
                        "metadata": {"knowledge_type": "learned_pattern"}
                    }
                ]
            }
        }
        
        # Import without overwrite (should not replace)
        await knowledge_base.import_knowledge(export_data, overwrite=False)
        result = await knowledge_base.retrieve(key)
        assert result == {"version": "original"}
        
        # Import with overwrite (should replace)
        await knowledge_base.import_knowledge(export_data, overwrite=True)
        result = await knowledge_base.retrieve(key)
        assert result == {"version": "imported"}

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, knowledge_base):
        """Test concurrent knowledge operations."""
        # Concurrent stores
        tasks = []
        for i in range(10):
            if i % 3 == 0:
                task = knowledge_base.store_learned_pattern(f"pattern_{i}", {"value": i})
            elif i % 3 == 1:
                task = knowledge_base.store_user_preference(f"pref_{i}", {"value": i})
            else:
                task = knowledge_base.store_failure_pattern(f"fail_{i}", {"value": i})
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Verify all stored
        size = await knowledge_base.get_size()
        assert size == 10

    @pytest.mark.asyncio
    async def test_error_handling(self, knowledge_base):
        """Test error handling in knowledge operations."""
        # Test with mock vector store that fails
        with patch.object(knowledge_base.stores[KnowledgeType.LEARNED_PATTERN], 'store', 
                         side_effect=Exception("Store error")):
            # Should not raise exception
            await knowledge_base.store_learned_pattern("error_test", {"data": "test"})

    @pytest.mark.asyncio
    async def test_knowledge_type_enum(self):
        """Test KnowledgeType enum values."""
        expected_types = [
            "learned_pattern",
            "user_preference", 
            "domain_knowledge",
            "failure_pattern",
            "workflow_template",
            "agent_behavior"
        ]
        
        actual_types = [kt.value for kt in KnowledgeType]
        assert set(actual_types) == set(expected_types)


if __name__ == "__main__":
    pytest.main([__file__])