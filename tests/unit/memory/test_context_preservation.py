#!/usr/bin/env python3
"""
Unit tests for ContextPreservationStrategy - Phase 5

Tests context preservation logic including content classification,
importance scoring, and preservation strategies.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from src.memory.context_preservation import (
    ContextPreservationStrategy,
    ContentItem,
    PreservationCategory,
    PreservationReport
)
from src.memory.conversation_compactor import ConversationSegment, ContentImportance
from src.core.models import WorkflowPattern


@pytest.fixture
def preservation_strategy():
    """Create context preservation strategy instance."""
    return ContextPreservationStrategy()


@pytest.fixture
def sample_content_items():
    """Sample content items for testing."""
    now = datetime.now()
    return [
        ContentItem(
            content_id="item_1",
            content="User wants to create a todo application",
            category=PreservationCategory.OBJECTIVES,
            importance_score=0.95,
            timestamp=now,
            source_agent="user_interface",
            metadata={"type": "user_objective"}
        ),
        ContentItem(
            content_id="item_2", 
            content="debug: entering main function",
            category=PreservationCategory.ACTIVE_CONTEXT,
            importance_score=0.1,
            timestamp=now - timedelta(hours=1),
            source_agent="debug_agent",
            metadata={"type": "debug_info"}
        ),
        ContentItem(
            content_id="item_3",
            content="Final result: Todo application successfully created",
            category=PreservationCategory.ARTIFACTS,
            importance_score=0.9,
            timestamp=now,
            source_agent="task_agent",
            metadata={"type": "final_result"}
        ),
        ContentItem(
            content_id="item_4",
            content="Tool execution result: calculated optimal layout",
            category=PreservationCategory.TOOLS,
            importance_score=0.6,
            timestamp=now - timedelta(minutes=30),
            source_agent="tool_agent",
            metadata={"type": "tool_result"}
        )
    ]


@pytest.fixture
def sample_conversation_segments():
    """Sample conversation segments for testing."""
    now = datetime.now()
    return [
        ConversationSegment(
            segment_id="seg_1",
            timestamp=now - timedelta(hours=2),
            agent_interactions=[
                {"agent_id": "research_agent", "message": "User wants to build a calculator", "type": "objective"},
                {"agent_id": "research_agent", "message": "debug: analyzing requirements", "type": "debug"},
                {"agent_id": "research_agent", "message": "Found similar patterns in database", "type": "discovery"}
            ],
            workflow_pattern=WorkflowPattern.SEQUENTIAL,
            importance_score=0.8,
            token_count=150,
            metadata={"workflow_id": "wf_1", "success": True}
        ),
        ConversationSegment(
            segment_id="seg_2",
            timestamp=now - timedelta(hours=1),
            agent_interactions=[
                {"agent_id": "task_agent", "message": "Decided to use React framework", "type": "decision"},
                {"agent_id": "task_agent", "message": "status: 50% complete", "type": "status"},
                {"agent_id": "security_agent", "message": "Security validation passed", "type": "validation"}
            ],
            workflow_pattern=WorkflowPattern.PARALLEL,
            importance_score=0.7,
            token_count=120,
            metadata={"workflow_id": "wf_2", "success": True}
        ),
        ConversationSegment(
            segment_id="seg_3",
            timestamp=now,
            agent_interactions=[
                {"agent_id": "task_agent", "message": "Final result: Calculator application deployed", "type": "result"},
                {"agent_id": "tool_agent", "message": "Tool result: performance score = 95", "type": "tool_result"},
                {"agent_id": "system_agent", "message": "trace: cleanup completed", "type": "trace"}
            ],
            workflow_pattern=WorkflowPattern.CONDITIONAL,
            importance_score=0.9,
            token_count=100,
            metadata={"workflow_id": "wf_3", "success": True}
        )
    ]


class TestContextPreservationStrategy:
    """Test suite for ContextPreservationStrategy."""

    def test_initialization(self, preservation_strategy):
        """Test preservation strategy initialization."""
        assert len(preservation_strategy.preservation_rules) > 0
        assert len(preservation_strategy.category_priorities) > 0
        assert len(preservation_strategy.content_patterns) > 0
        
        # Check that all preservation categories have priorities
        for category in PreservationCategory:
            assert category in preservation_strategy.category_priorities

    def test_classify_content_objectives(self, preservation_strategy):
        """Test content classification for objectives."""
        test_cases = [
            "User wants to create a web application",
            "Goal is to optimize performance",
            "Requirement: must handle 1000 users",
            "Need to accomplish data migration"
        ]
        
        for content in test_cases:
            category, importance = preservation_strategy._classify_content(content)
            assert category == PreservationCategory.OBJECTIVES
            assert importance == ContentImportance.CRITICAL.value

    def test_classify_content_decisions(self, preservation_strategy):
        """Test content classification for decisions."""
        test_cases = [
            "decided to use PostgreSQL database",
            "final decision to implement caching layer"
        ]
        
        for content in test_cases:
            category, importance = preservation_strategy._classify_content(content)
            assert category == PreservationCategory.DECISIONS
            assert importance == ContentImportance.HIGH.value

    def test_classify_content_artifacts(self, preservation_strategy):
        """Test content classification for artifacts."""
        test_cases = [
            "Final result: application deployed successfully",
            "Output: Generated 15 test files",
            "Created configuration file: app.yaml",
            "Delivered: Performance report with metrics"
        ]
        
        for content in test_cases:
            category, importance = preservation_strategy._classify_content(content)
            assert category == PreservationCategory.ARTIFACTS
            assert importance == ContentImportance.HIGH.value

    def test_classify_content_discoveries(self, preservation_strategy):
        """Test content classification for discoveries."""
        test_cases = [
            "Discovered that API rate limiting is needed",
            "Found out users prefer dark mode",
            "Insight: caching improves performance by 40%",
            "Key finding: memory usage spikes during peak hours"
        ]
        
        for content in test_cases:
            category, importance = preservation_strategy._classify_content(content)
            assert category == PreservationCategory.DISCOVERIES
            assert importance == ContentImportance.MEDIUM.value

    def test_classify_content_tools(self, preservation_strategy):
        """Test content classification for tool results."""
        test_cases = [
            "Tool result: calculation completed successfully",
            "Executed search tool, found 15 relevant items",
            "API response: status 200, data retrieved",
            "File operation: successfully saved 3 files"
        ]
        
        for content in test_cases:
            category, importance = preservation_strategy._classify_content(content)
            assert category == PreservationCategory.TOOLS
            assert importance == ContentImportance.MEDIUM.value

    def test_classify_content_default(self, preservation_strategy):
        """Test content classification for unmatched content."""
        # Short unmatched content
        category, importance = preservation_strategy._classify_content("short text")
        assert category == PreservationCategory.ACTIVE_CONTEXT
        assert importance == ContentImportance.LOW.value
        
        # Long unmatched content (make sure it's >200 chars)
        long_content = "This is a longer piece of content that doesn't match any specific patterns but might be important due to its length and complexity. " * 3  # Repeat to make it longer
        category, importance = preservation_strategy._classify_content(long_content)
        assert category == PreservationCategory.ACTIVE_CONTEXT
        assert importance == ContentImportance.MEDIUM.value

    def test_adjust_importance_for_context(self, preservation_strategy):
        """Test importance adjustment based on context."""
        base_importance = 0.5
        
        # Successful workflow should boost importance
        successful_segment = ConversationSegment(
            segment_id="test",
            timestamp=datetime.now(),
            agent_interactions=[],
            workflow_pattern=WorkflowPattern.SEQUENTIAL,
            importance_score=0.7,
            token_count=100,
            metadata={"success": True}
        )
        
        interaction = {"message": "test interaction"}
        adjusted = preservation_strategy._adjust_importance_for_context(
            base_importance, successful_segment, interaction
        )
        assert adjusted > base_importance
        
        # Complex workflow pattern should boost importance
        complex_segment = ConversationSegment(
            segment_id="test",
            timestamp=datetime.now(),
            agent_interactions=[],
            workflow_pattern=WorkflowPattern.HIERARCHICAL,
            importance_score=0.7,
            token_count=100,
            metadata={}
        )
        
        adjusted = preservation_strategy._adjust_importance_for_context(
            base_importance, complex_segment, interaction
        )
        assert adjusted > base_importance

    def test_calculate_preservation_score(self, preservation_strategy, sample_content_items):
        """Test preservation score calculation."""
        # High importance objective - should get high score
        objective_item = sample_content_items[0]  # User objective
        score = preservation_strategy._calculate_preservation_score(objective_item)
        assert score > 0.8
        
        # Low importance debug info - should get low score
        debug_item = sample_content_items[1]  # Debug info
        score = preservation_strategy._calculate_preservation_score(debug_item)
        assert score < 0.3
        
        # Recent high importance item should score higher than old one
        recent_item = ContentItem(
            content_id="recent",
            content="Important recent finding",
            category=PreservationCategory.DISCOVERIES,
            importance_score=0.7,
            timestamp=datetime.now(),
            metadata={}
        )
        
        old_item = ContentItem(
            content_id="old",
            content="Important old finding",
            category=PreservationCategory.DISCOVERIES,
            importance_score=0.7,
            timestamp=datetime.now() - timedelta(days=2),
            metadata={}
        )
        
        recent_score = preservation_strategy._calculate_preservation_score(recent_item)
        old_score = preservation_strategy._calculate_preservation_score(old_item)
        assert recent_score > old_score

    @pytest.mark.asyncio
    async def test_extract_content_items(self, preservation_strategy, sample_conversation_segments):
        """Test content item extraction from segments."""
        segment = sample_conversation_segments[0]  # First segment
        
        items = await preservation_strategy._extract_content_items(segment)
        
        assert len(items) == 3  # Should extract 3 interactions
        
        # Check that items have proper structure
        for item in items:
            assert hasattr(item, 'content_id')
            assert hasattr(item, 'content')
            assert hasattr(item, 'category')
            assert hasattr(item, 'importance_score')
            assert hasattr(item, 'timestamp')
            assert item.timestamp == segment.timestamp

    @pytest.mark.asyncio
    async def test_summarize_content_item(self, preservation_strategy, sample_content_items):
        """Test content item summarization."""
        original_item = sample_content_items[0]  # User objective
        
        summarized = await preservation_strategy._summarize_content_item(original_item)
        
        assert summarized.content_id != original_item.content_id
        assert summarized.content_id.endswith("_summary")
        assert summarized.importance_score < original_item.importance_score
        assert summarized.metadata.get("summarized") is True

    @pytest.mark.asyncio
    async def test_extract_active_context(self, preservation_strategy, sample_conversation_segments):
        """Test active context extraction."""
        latest_segment = sample_conversation_segments[-1]  # Most recent segment
        
        active_context = await preservation_strategy._extract_active_context(latest_segment)
        
        assert len(active_context) > 0
        assert len(active_context) <= 3  # Should limit to last 3 interactions
        
        for context_item in active_context:
            assert "content" in context_item
            assert "timestamp" in context_item
            assert "workflow_pattern" in context_item
            assert context_item["active"] is True

    @pytest.mark.asyncio
    async def test_preserve_critical_context_full_workflow(self, preservation_strategy, sample_conversation_segments):
        """Test full context preservation workflow."""
        result = await preservation_strategy.preserve_critical_context(sample_conversation_segments)
        
        # Check result structure
        assert "preserved_content" in result
        assert "preservation_report" in result
        assert "summary" in result
        
        preserved_content = result["preserved_content"]
        preservation_report = result["preservation_report"]
        
        # Check that all categories are present
        for category in PreservationCategory:
            assert category in preserved_content
            assert isinstance(preserved_content[category], list)
        
        # Check preservation report
        assert isinstance(preservation_report, PreservationReport)
        assert preservation_report.total_items_analyzed > 0
        assert preservation_report.items_preserved >= 0
        assert preservation_report.items_summarized >= 0
        assert preservation_report.items_discarded >= 0
        assert (preservation_report.items_preserved + 
                preservation_report.items_summarized + 
                preservation_report.items_discarded) == preservation_report.total_items_analyzed

    @pytest.mark.asyncio
    async def test_preservation_thresholds(self, preservation_strategy):
        """Test that preservation thresholds work correctly."""
        # Create items with different importance scores
        high_importance = ContentItem(
            content_id="high",
            content="Critical user objective",
            category=PreservationCategory.OBJECTIVES,
            importance_score=0.9,
            timestamp=datetime.now(),
            metadata={}
        )
        
        medium_importance = ContentItem(
            content_id="medium",
            content="Intermediate finding",
            category=PreservationCategory.DISCOVERIES,
            importance_score=0.5,
            timestamp=datetime.now(),
            metadata={}
        )
        
        low_importance = ContentItem(
            content_id="low",
            content="Debug trace information",
            category=PreservationCategory.ACTIVE_CONTEXT,
            importance_score=0.2,
            timestamp=datetime.now(),
            metadata={}
        )
        
        # Create segment with these items
        segment = ConversationSegment(
            segment_id="test",
            timestamp=datetime.now(),
            agent_interactions=[
                high_importance.content,
                medium_importance.content,
                low_importance.content
            ],
            workflow_pattern=WorkflowPattern.SEQUENTIAL,
            importance_score=0.7,
            token_count=100,
            metadata={}
        )
        
        result = await preservation_strategy.preserve_critical_context([segment])
        report = result["preservation_report"]
        
        # Check that analysis was performed
        assert report.total_items_analyzed == 3
        
        # Some items should be preserved, summarized, or discarded
        assert (report.items_preserved + report.items_summarized + report.items_discarded) == 3

    def test_create_preservation_summary(self, preservation_strategy):
        """Test preservation summary creation."""
        preserved_content = {
            PreservationCategory.OBJECTIVES: [Mock(), Mock()],
            PreservationCategory.DECISIONS: [Mock()],
            PreservationCategory.ARTIFACTS: [],
            PreservationCategory.DISCOVERIES: [Mock()],
            PreservationCategory.ERRORS: [],
            PreservationCategory.ACTIVE_CONTEXT: [],
            PreservationCategory.TOOLS: [],
            PreservationCategory.PATTERNS: []
        }
        
        report = PreservationReport(
            total_items_analyzed=10,
            items_preserved=4,
            items_summarized=3,
            items_discarded=3,
            preservation_ratio=0.4,
            categories_preserved={},
            timestamp=datetime.now()
        )
        
        summary = preservation_strategy._create_preservation_summary(preserved_content, report)
        
        assert isinstance(summary, str)
        assert "Preserved 4 critical items" in summary
        assert "from 10 analyzed" in summary
        assert "40.0%" in summary
        assert "objectives" in summary.lower()
        assert "decisions" in summary.lower()

    def test_update_preservation_rules(self, preservation_strategy):
        """Test preservation rules update."""
        new_rules = {
            "custom_pattern": 0.8,
            "special_case": 0.95
        }
        
        original_count = len(preservation_strategy.preservation_rules)
        preservation_strategy.update_preservation_rules(new_rules)
        
        assert len(preservation_strategy.preservation_rules) == original_count + 2
        assert preservation_strategy.preservation_rules["custom_pattern"] == 0.8
        assert preservation_strategy.preservation_rules["special_case"] == 0.95

    def test_get_preservation_statistics(self, preservation_strategy):
        """Test preservation statistics retrieval."""
        stats = preservation_strategy.get_preservation_statistics()
        
        assert "rules_count" in stats
        assert "category_priorities" in stats
        assert "pattern_types" in stats
        assert "preservation_thresholds" in stats
        
        assert stats["rules_count"] > 0
        assert len(stats["category_priorities"]) == len(PreservationCategory)
        assert stats["preservation_thresholds"]["preserve"] == 0.7
        assert stats["preservation_thresholds"]["summarize"] == 0.3
        assert stats["preservation_thresholds"]["discard"] == 0.0


class TestContentItem:
    """Test suite for ContentItem data class."""

    def test_content_item_creation(self):
        """Test content item creation."""
        timestamp = datetime.now()
        item = ContentItem(
            content_id="test_item",
            content="Test content",
            category=PreservationCategory.OBJECTIVES,
            importance_score=0.8,
            timestamp=timestamp,
            source_agent="test_agent",
            workflow_id="wf_123",
            metadata={"type": "test"}
        )
        
        assert item.content_id == "test_item"
        assert item.content == "Test content"
        assert item.category == PreservationCategory.OBJECTIVES
        assert item.importance_score == 0.8
        assert item.timestamp == timestamp
        assert item.source_agent == "test_agent"
        assert item.workflow_id == "wf_123"
        assert item.metadata["type"] == "test"


class TestPreservationReport:
    """Test suite for PreservationReport data class."""

    def test_preservation_report_creation(self):
        """Test preservation report creation."""
        timestamp = datetime.now()
        categories = {
            PreservationCategory.OBJECTIVES: 2,
            PreservationCategory.DECISIONS: 1
        }
        
        report = PreservationReport(
            total_items_analyzed=10,
            items_preserved=5,
            items_summarized=3,
            items_discarded=2,
            preservation_ratio=0.5,
            categories_preserved=categories,
            timestamp=timestamp
        )
        
        assert report.total_items_analyzed == 10
        assert report.items_preserved == 5
        assert report.items_summarized == 3
        assert report.items_discarded == 2
        assert report.preservation_ratio == 0.5
        assert len(report.categories_preserved) == 2
        assert report.timestamp == timestamp


if __name__ == "__main__":
    pytest.main([__file__])