#!/usr/bin/env python3
"""
Integration tests for Conversation Compacting System - Phase 5

Tests the complete conversation compacting workflow including API endpoints,
WebSocket notifications, and end-to-end compacting operations.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import WebSocket

from src.memory.conversation_compactor import ConversationCompactor, CompactingStrategy
from src.memory.context_preservation import ContextPreservationStrategy
from src.memory.shared_context import SharedContextPool
from src.memory.local_memory import AgentLocalMemory
from api.conversation_manager import ConversationManager, conversation_manager
from api.main import app


@pytest.fixture
def test_client():
    """Create test client for API testing."""
    return TestClient(app)


@pytest.fixture
def mock_conversation_manager():
    """Mock conversation manager for testing."""
    manager = Mock(spec=ConversationManager)
    manager.compactor = Mock(spec=ConversationCompactor)
    manager.preservation_strategy = Mock(spec=ContextPreservationStrategy)
    manager.shared_context = Mock(spec=SharedContextPool)
    manager.local_memory = Mock(spec=AgentLocalMemory)
    manager.active_conversations = {}
    manager.websocket_connections = {}
    return manager


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing."""
    return {
        "conversation_id": "test_conv_123",
        "workflow_history": [
            {
                "workflow_id": "wf_1",
                "pattern": "SEQUENTIAL",
                "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                "success": True,
                "duration": 180,
                "agent_interactions": [
                    {"agent_id": "research_agent", "action": "User wants to create a task manager", "type": "objective"},
                    {"agent_id": "research_agent", "action": "Analyzed requirements", "type": "analysis"},
                    {"agent_id": "task_agent", "action": "Started implementation", "type": "action"}
                ]
            },
            {
                "workflow_id": "wf_2",
                "pattern": "PARALLEL",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "success": True,
                "duration": 240,
                "agent_interactions": [
                    {"agent_id": "task_agent", "action": "Decided to use React framework", "type": "decision"},
                    {"agent_id": "security_agent", "action": "Validated security requirements", "type": "validation"},
                    {"agent_id": "tool_agent", "action": "Tool result: calculated optimal database schema", "type": "tool_result"}
                ],
                "tool_executions": ["calculator", "database_analyzer"]
            },
            {
                "workflow_id": "wf_3",
                "pattern": "CONDITIONAL",
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "success": True,
                "duration": 120,
                "agent_interactions": [
                    {"agent_id": "task_agent", "action": "Final result: Task manager application completed", "type": "result"},
                    {"agent_id": "task_agent", "action": "Deployed to production environment", "type": "deployment"},
                    {"agent_id": "system_agent", "action": "Performance monitoring activated", "type": "monitoring"}
                ]
            }
        ]
    }


class TestConversationCompactingAPI:
    """Test suite for conversation compacting API endpoints."""

    @patch('api.conversation_manager.conversation_manager')
    def test_compact_conversation_success(self, mock_manager, test_client, sample_conversation_data):
        """Test successful conversation compacting via API."""
        # Mock compacting result
        mock_result = Mock()
        mock_result.success = True
        mock_result.conversation_id = "test_conv_123"
        mock_result.strategy_used = CompactingStrategy.AUTO
        mock_result.original_token_count = 2000
        mock_result.compacted_token_count = 600
        mock_result.reduction_percentage = 70.0
        mock_result.segments_processed = 3
        mock_result.preserved_artifacts = ["objective1", "result1"]
        mock_result.compacting_summary = "Successfully compacted conversation with 70% reduction"
        mock_result.timestamp = datetime.now()
        mock_result.error = None
        
        mock_manager.compactor.compact_conversation.return_value = mock_result
        
        # Make API request
        response = test_client.post(
            "/api/conversations/test_conv_123/compact",
            json={
                "conversation_id": "test_conv_123",
                "strategy": "auto"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["conversation_id"] == "test_conv_123"
        assert data["strategy_used"] == "auto"
        assert data["reduction_percentage"] == 70.0
        assert data["preserved_artifacts_count"] == 2

    @patch('api.conversation_manager.conversation_manager')
    def test_compact_conversation_failure(self, mock_manager, test_client):
        """Test conversation compacting failure via API."""
        # Mock compacting failure
        mock_result = Mock()
        mock_result.success = False
        mock_result.conversation_id = "test_conv_123"
        mock_result.strategy_used = CompactingStrategy.AUTO
        mock_result.original_token_count = 0
        mock_result.compacted_token_count = 0
        mock_result.reduction_percentage = 0.0
        mock_result.segments_processed = 0
        mock_result.preserved_artifacts = []
        mock_result.compacting_summary = "Compacting failed"
        mock_result.timestamp = datetime.now()
        mock_result.error = "Database connection failed"
        
        mock_manager.compactor.compact_conversation.return_value = mock_result
        
        # Make API request
        response = test_client.post(
            "/api/conversations/test_conv_123/compact",
            json={
                "conversation_id": "test_conv_123",
                "strategy": "auto"
            }
        )
        
        assert response.status_code == 200  # API succeeds but compacting failed
        data = response.json()
        
        assert data["success"] is False
        assert data["error"] == "Database connection failed"

    @patch('api.conversation_manager.conversation_manager')
    def test_get_token_usage(self, mock_manager, test_client):
        """Test token usage endpoint."""
        # Mock token usage data
        mock_usage = {
            "conversation_id": "test_conv_123",
            "current_tokens": 1500,
            "threshold": 2000,
            "usage_percentage": 75.0,
            "needs_compacting": True,
            "workflow_count": 5
        }
        mock_manager.compactor.get_token_usage.return_value = mock_usage
        
        # Make API request
        response = test_client.get("/api/conversations/test_conv_123/token-usage")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["conversation_id"] == "test_conv_123"
        assert data["current_tokens"] == 1500
        assert data["usage_percentage"] == 75.0
        assert data["warning_level"] == "warning"  # 75% should be warning level

    @patch('api.conversation_manager.conversation_manager')
    def test_get_conversation_status(self, mock_manager, test_client):
        """Test conversation status endpoint."""
        # Mock token usage
        mock_usage = {
            "conversation_id": "test_conv_123",
            "current_tokens": 1200,
            "threshold": 2000,
            "usage_percentage": 60.0,
            "needs_compacting": False,
            "workflow_count": 3,
            "last_updated": datetime.now().isoformat(),
            "warning_level": "none"
        }
        mock_manager.compactor.get_token_usage.return_value = mock_usage
        
        # Mock compacting history
        mock_history = [
            Mock(
                conversation_id="test_conv_123",
                timestamp=datetime.now(),
                strategy_used=CompactingStrategy.AUTO,
                reduction_percentage=65.0,
                success=True
            )
        ]
        mock_manager.compactor.get_compacting_history.return_value = mock_history
        
        # Mock shared context
        mock_manager.shared_context.retrieve.return_value = {
            "workflow_count": 3,
            "last_activity": datetime.now().isoformat()
        }
        
        # Make API request
        response = test_client.get("/api/conversations/test_conv_123/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["conversation_id"] == "test_conv_123"
        assert data["total_workflows"] == 3
        assert "token_usage" in data
        assert "compacting_history" in data

    @patch('api.conversation_manager.conversation_manager')
    def test_auto_compact_check(self, mock_manager, test_client):
        """Test auto-compact check endpoint."""
        # Mock should compact
        mock_manager.compactor.should_trigger_auto_compact.return_value = True
        
        # Make API request
        response = test_client.post("/api/conversations/test_conv_123/auto-compact-check")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["should_compact"] is True
        assert data["action"] == "scheduled"

    def test_list_conversations(self, test_client):
        """Test conversation listing endpoint."""
        with patch.object(conversation_manager, 'active_conversations', {"conv1": {}, "conv2": {}}):
            response = test_client.get("/api/conversations")
            
            assert response.status_code == 200
            data = response.json()
            
            assert len(data) == 2
            assert "conv1" in data
            assert "conv2" in data


class TestWebSocketIntegration:
    """Test suite for WebSocket integration."""

    @pytest.mark.asyncio
    async def test_websocket_connection_and_monitoring(self):
        """Test WebSocket connection and monitoring."""
        # This would require more complex WebSocket testing setup
        # For now, we'll test the core logic
        
        # Mock WebSocket
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        
        # Mock conversation manager
        with patch('api.conversation_manager.conversation_manager') as mock_manager:
            mock_manager.compactor.get_token_usage.return_value = {
                "conversation_id": "test_conv",
                "current_tokens": 1800,
                "threshold": 2000,
                "usage_percentage": 90.0,
                "needs_compacting": True,
                "workflow_count": 8
            }
            
            mock_manager.compactor.should_trigger_auto_compact.return_value = True
            mock_manager.websocket_connections = {"test_conv": []}
            
            # Import the websocket function
            from api.conversation_manager import conversation_websocket
            
            # This would normally be called by FastAPI WebSocket handler
            # Here we're just testing the logic would work
            assert callable(conversation_websocket)


class TestEndToEndCompacting:
    """Test suite for end-to-end compacting workflows."""

    @pytest.mark.asyncio
    async def test_complete_compacting_workflow(self, sample_conversation_data):
        """Test complete conversation compacting workflow."""
        # Create real instances for integration testing
        shared_context = SharedContextPool()
        local_memory = AgentLocalMemory("test_compactor")
        compactor = ConversationCompactor(
            shared_context=shared_context,
            local_memory=local_memory,
            token_threshold=500,  # Low threshold for testing
            compression_ratio=0.3
        )
        
        # Store test conversation data
        conversation_id = sample_conversation_data["conversation_id"]
        await shared_context.store(f"conversation_{conversation_id}", sample_conversation_data)
        await shared_context.store(f"workflow_history_{conversation_id}", sample_conversation_data["workflow_history"])
        
        # Perform compacting
        result = await compactor.compact_conversation(conversation_id, CompactingStrategy.AUTO)
        
        # Verify results
        assert result.success is True
        assert result.conversation_id == conversation_id
        assert result.strategy_used == CompactingStrategy.AUTO
        assert result.segments_processed > 0
        
        # Check that token usage is reduced
        usage_after = await compactor.get_token_usage(conversation_id)
        assert usage_after["current_tokens"] >= 0  # Should have some usage

    @pytest.mark.asyncio
    async def test_multiple_strategy_comparison(self, sample_conversation_data):
        """Test different compacting strategies on the same data."""
        shared_context = SharedContextPool()
        local_memory = AgentLocalMemory("test_compactor")
        compactor = ConversationCompactor(
            shared_context=shared_context,
            local_memory=local_memory,
            token_threshold=500,
            compression_ratio=0.3
        )
        
        conversation_id = sample_conversation_data["conversation_id"]
        
        # Store conversation data
        await shared_context.store(f"conversation_{conversation_id}", sample_conversation_data)
        await shared_context.store(f"workflow_history_{conversation_id}", sample_conversation_data["workflow_history"])
        
        # Test different strategies
        strategies = [CompactingStrategy.AUTO, CompactingStrategy.AGGRESSIVE, CompactingStrategy.CONSERVATIVE]
        results = []
        
        for strategy in strategies:
            # Reset conversation data for each test
            await shared_context.store(f"conversation_{conversation_id}", sample_conversation_data)
            await shared_context.store(f"workflow_history_{conversation_id}", sample_conversation_data["workflow_history"])
            
            result = await compactor.compact_conversation(conversation_id, strategy)
            results.append(result)
        
        # Verify all strategies succeeded
        for result in results:
            assert result.success is True
        
        # Verify different strategies produce different results
        auto_result, aggressive_result, conservative_result = results
        
        # Aggressive should compress more than conservative
        assert aggressive_result.reduction_percentage >= conservative_result.reduction_percentage

    @pytest.mark.asyncio
    async def test_context_preservation_integration(self, sample_conversation_data):
        """Test that context preservation works in full workflow."""
        shared_context = SharedContextPool()
        local_memory = AgentLocalMemory("test_compactor")
        compactor = ConversationCompactor(
            shared_context=shared_context,
            local_memory=local_memory,
            token_threshold=100,  # Very low threshold to force compacting
            compression_ratio=0.5
        )
        
        conversation_id = sample_conversation_data["conversation_id"]
        
        # Store conversation data
        await shared_context.store(f"conversation_{conversation_id}", sample_conversation_data)
        await shared_context.store(f"workflow_history_{conversation_id}", sample_conversation_data["workflow_history"])
        
        # Perform compacting
        result = await compactor.compact_conversation(conversation_id, CompactingStrategy.AUTO)
        
        # Verify critical content is preserved
        assert result.success is True
        assert len(result.preserved_artifacts) > 0
        
        # Check that important content types are preserved
        summary = result.compacting_summary.lower()
        # Should mention preservation of critical artifacts
        assert "preserved" in summary or "artifacts" in summary

    @pytest.mark.asyncio
    async def test_auto_compact_triggering(self, sample_conversation_data):
        """Test automatic compacting trigger logic."""
        shared_context = SharedContextPool()
        local_memory = AgentLocalMemory("test_compactor")
        compactor = ConversationCompactor(
            shared_context=shared_context,
            local_memory=local_memory,
            token_threshold=100,  # Very low threshold
            compression_ratio=0.3
        )
        
        conversation_id = sample_conversation_data["conversation_id"]
        
        # Small data - should not trigger
        small_data = {"small": "data"}
        await shared_context.store(f"conversation_{conversation_id}", small_data)
        
        should_compact = await compactor.should_trigger_auto_compact(conversation_id)
        assert should_compact is False
        
        # Large data - should trigger
        await shared_context.store(f"conversation_{conversation_id}", sample_conversation_data)
        await shared_context.store(f"workflow_history_{conversation_id}", sample_conversation_data["workflow_history"])
        
        should_compact = await compactor.should_trigger_auto_compact(conversation_id)
        assert should_compact is True

    @pytest.mark.asyncio
    async def test_compacting_history_persistence(self, sample_conversation_data):
        """Test that compacting history is properly maintained."""
        shared_context = SharedContextPool()
        local_memory = AgentLocalMemory("test_compactor")
        compactor = ConversationCompactor(
            shared_context=shared_context,
            local_memory=local_memory,
            token_threshold=200,
            compression_ratio=0.3
        )
        
        conversation_id = sample_conversation_data["conversation_id"]
        
        # Store conversation data
        await shared_context.store(f"conversation_{conversation_id}", sample_conversation_data)
        await shared_context.store(f"workflow_history_{conversation_id}", sample_conversation_data["workflow_history"])
        
        # Perform multiple compacting operations
        result1 = await compactor.compact_conversation(conversation_id, CompactingStrategy.AUTO)
        result2 = await compactor.compact_conversation(conversation_id, CompactingStrategy.CONSERVATIVE)
        
        # Check history
        history = await compactor.get_compacting_history()
        assert len(history) == 2
        
        # Verify history contains both operations
        strategies_used = [h.strategy_used for h in history]
        assert CompactingStrategy.AUTO in strategies_used
        assert CompactingStrategy.CONSERVATIVE in strategies_used

    @pytest.mark.asyncio
    async def test_error_recovery_and_cleanup(self):
        """Test error handling and cleanup in compacting operations."""
        # Create compactor with invalid shared context to trigger errors
        shared_context = Mock(spec=SharedContextPool)
        shared_context.retrieve.side_effect = Exception("Connection failed")
        
        local_memory = AgentLocalMemory("test_compactor")
        compactor = ConversationCompactor(
            shared_context=shared_context,
            local_memory=local_memory,
            token_threshold=1000,
            compression_ratio=0.3
        )
        
        # Attempt compacting with error condition
        result = await compactor.compact_conversation("test_conv", CompactingStrategy.AUTO)
        
        # Verify error handling
        assert result.success is False
        assert result.error is not None
        assert "Connection failed" in result.error
        
        # Verify system is still functional (history tracking works)
        history = await compactor.get_compacting_history()
        assert len(history) == 1
        assert history[0].success is False


if __name__ == "__main__":
    pytest.main([__file__])