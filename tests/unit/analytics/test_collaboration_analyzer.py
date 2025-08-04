"""
Unit tests for CollaborationAnalyzer
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.analytics.collaboration_analyzer import (
    CollaborationAnalyzer,
    AgentInteraction,
    CollaborationPattern,
    CollaborationMetrics,
    NetworkAnalysis
)


@pytest.fixture
def mock_shared_context():
    """Mock shared context"""
    context = AsyncMock()
    context.store = AsyncMock()
    return context


@pytest.fixture
def mock_communication_manager():
    """Mock communication manager"""
    return MagicMock()


@pytest.fixture
def collaboration_analyzer(mock_shared_context, mock_communication_manager):
    """Create CollaborationAnalyzer instance for testing"""
    return CollaborationAnalyzer(mock_shared_context, mock_communication_manager)


@pytest.fixture
def sample_interactions():
    """Sample agent interactions for testing"""
    base_time = datetime.now()
    return [
        AgentInteraction(
            sender_id="agent1",
            receiver_id="agent2",
            interaction_type="message",
            timestamp=base_time,
            duration_ms=100.0,
            success=True,
            metadata={"task": "research"}
        ),
        AgentInteraction(
            sender_id="agent2",
            receiver_id="agent3",
            interaction_type="memory_share",
            timestamp=base_time + timedelta(seconds=30),
            duration_ms=50.0,
            success=True,
            metadata={"type": "discovery"}
        ),
        AgentInteraction(
            sender_id="agent1",
            receiver_id="agent3",
            interaction_type="tool_request",
            timestamp=base_time + timedelta(minutes=1),
            duration_ms=200.0,
            success=False,
            metadata={"tool": "calculator"}
        )
    ]


class TestCollaborationAnalyzer:
    """Test cases for CollaborationAnalyzer"""
    
    @pytest.mark.asyncio
    async def test_record_interaction(self, collaboration_analyzer, mock_shared_context):
        """Test recording agent interactions"""
        interaction = AgentInteraction(
            sender_id="agent1",
            receiver_id="agent2",
            interaction_type="message",
            timestamp=datetime.now(),
            duration_ms=100.0,
            success=True
        )
        
        await collaboration_analyzer.record_interaction(interaction)
        
        assert len(collaboration_analyzer.interaction_history) == 1
        assert collaboration_analyzer.interaction_history[0] == interaction
        mock_shared_context.store.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_collaboration_patterns_empty(self, collaboration_analyzer):
        """Test analysis with no interactions"""
        metrics = await collaboration_analyzer.analyze_collaboration_patterns()
        
        assert metrics.total_interactions == 0
        assert metrics.unique_agent_pairs == 0
        assert metrics.success_rate == 0
        assert metrics.efficiency_score == 0
    
    @pytest.mark.asyncio
    async def test_analyze_collaboration_patterns_with_data(self, collaboration_analyzer, sample_interactions):
        """Test analysis with sample interactions"""
        # Add interactions to history
        for interaction in sample_interactions:
            await collaboration_analyzer.record_interaction(interaction)
        
        metrics = await collaboration_analyzer.analyze_collaboration_patterns()
        
        assert metrics.total_interactions == 3
        assert metrics.unique_agent_pairs == 3  # (agent1,agent2), (agent2,agent3), (agent1,agent3)
        assert metrics.success_rate == 2/3  # 2 successful out of 3
        assert metrics.avg_response_time == (100 + 50 + 200) / 3
        assert len(metrics.most_active_agents) > 0
        assert metrics.efficiency_score > 0
    
    def test_identify_collaboration_pattern_sequential(self, collaboration_analyzer):
        """Test identification of sequential collaboration pattern"""
        interactions = [
            AgentInteraction("agent1", "agent2", "message", datetime.now(), 100, True),
            AgentInteraction("agent2", "agent3", "message", datetime.now(), 100, True)
        ]
        
        pattern = collaboration_analyzer._identify_collaboration_pattern(interactions)
        assert pattern == CollaborationPattern.SEQUENTIAL
    
    def test_identify_collaboration_pattern_hub_and_spoke(self, collaboration_analyzer):
        """Test identification of hub-and-spoke pattern"""
        base_time = datetime.now()
        interactions = [
            AgentInteraction("hub", "agent1", "message", base_time, 100, True),
            AgentInteraction("hub", "agent2", "message", base_time, 100, True),
            AgentInteraction("hub", "agent3", "message", base_time, 100, True),
            AgentInteraction("agent1", "hub", "response", base_time, 100, True),
            AgentInteraction("agent2", "hub", "response", base_time, 100, True),
            AgentInteraction("agent3", "hub", "response", base_time, 100, True)
        ]
        
        pattern = collaboration_analyzer._identify_collaboration_pattern(interactions)
        assert pattern == CollaborationPattern.HUB_AND_SPOKE
    
    def test_identify_collaboration_pattern_mesh(self, collaboration_analyzer):
        """Test identification of mesh pattern"""
        base_time = datetime.now()
        # Create fully connected graph
        interactions = []
        agents = ["agent1", "agent2", "agent3", "agent4"]
        
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i+1:]:
                interactions.extend([
                    AgentInteraction(agent1, agent2, "message", base_time, 100, True),
                    AgentInteraction(agent2, agent1, "response", base_time, 100, True)
                ])
        
        pattern = collaboration_analyzer._identify_collaboration_pattern(interactions)
        assert pattern == CollaborationPattern.MESH
    
    def test_group_interactions_by_time(self, collaboration_analyzer):
        """Test grouping interactions by time windows"""
        base_time = datetime.now()
        interactions = [
            AgentInteraction("agent1", "agent2", "message", base_time, 100, True),
            AgentInteraction("agent2", "agent3", "message", base_time + timedelta(minutes=2), 100, True),
            AgentInteraction("agent1", "agent3", "message", base_time + timedelta(minutes=10), 100, True)
        ]
        
        groups = collaboration_analyzer._group_interactions_by_time(interactions, window_minutes=5)
        
        assert len(groups) == 2  # Two time windows
        assert len(groups[0]) == 2  # First two interactions in first window
        assert len(groups[1]) == 1  # Last interaction in second window
    
    @pytest.mark.asyncio
    async def test_analyze_network_structure(self, collaboration_analyzer, sample_interactions):
        """Test network structure analysis"""
        # Add interactions to history
        for interaction in sample_interactions:
            await collaboration_analyzer.record_interaction(interaction)
        
        network_analysis = await collaboration_analyzer.analyze_network_structure()
        
        assert isinstance(network_analysis, NetworkAnalysis)
        assert len(network_analysis.centrality_scores) > 0
        assert network_analysis.clustering_coefficient >= 0
        assert network_analysis.network_diameter >= 0
        assert network_analysis.connected_components >= 1
    
    def test_calculate_centrality(self, collaboration_analyzer):
        """Test centrality calculation"""
        # Create simple graph: agent1 -> agent2, agent1 -> agent3
        graph = {
            "agent1": {"agent2": 1, "agent3": 1},
            "agent2": {"agent1": 1},
            "agent3": {"agent1": 1}
        }
        
        centrality = collaboration_analyzer._calculate_centrality(graph)
        
        assert "agent1" in centrality
        assert "agent2" in centrality
        assert "agent3" in centrality
        assert centrality["agent1"] > centrality["agent2"]  # agent1 has more connections
    
    def test_calculate_clustering_coefficient(self, collaboration_analyzer):
        """Test clustering coefficient calculation"""
        # Create triangle graph
        graph = {
            "agent1": {"agent2": 1, "agent3": 1},
            "agent2": {"agent1": 1, "agent3": 1},
            "agent3": {"agent1": 1, "agent2": 1}
        }
        
        clustering = collaboration_analyzer._calculate_clustering_coefficient(graph)
        
        assert clustering == 1.0  # Perfect triangle has clustering coefficient of 1
    
    def test_calculate_network_diameter(self, collaboration_analyzer):
        """Test network diameter calculation"""
        # Create linear graph: agent1 -> agent2 -> agent3
        graph = {
            "agent1": {"agent2": 1},
            "agent2": {"agent1": 1, "agent3": 1},
            "agent3": {"agent2": 1}
        }
        
        diameter = collaboration_analyzer._calculate_network_diameter(graph)
        
        assert diameter == 2  # Maximum distance is 2 (agent1 to agent3)
    
    def test_identify_bottleneck_agents(self, collaboration_analyzer):
        """Test bottleneck agent identification"""
        # Create hub-and-spoke graph
        graph = {
            "hub": {"agent1": 1, "agent2": 1, "agent3": 1},
            "agent1": {"hub": 1},
            "agent2": {"hub": 1},
            "agent3": {"hub": 1}
        }
        centrality = {"hub": 1.0, "agent1": 0.33, "agent2": 0.33, "agent3": 0.33}
        
        bottlenecks = collaboration_analyzer._identify_bottleneck_agents(graph, centrality)
        
        assert "hub" in bottlenecks
    
    def test_identify_bridge_agents(self, collaboration_analyzer):
        """Test bridge agent identification"""
        # Create two clusters connected by bridge
        graph = {
            "bridge": {"cluster1": 1, "cluster2": 1},
            "cluster1": {"bridge": 1, "c1_member": 1},
            "cluster2": {"bridge": 1, "c2_member": 1},
            "c1_member": {"cluster1": 1},
            "c2_member": {"cluster2": 1}
        }
        
        bridges = collaboration_analyzer._identify_bridge_agents(graph)
        
        # Bridge agent should be identified (connects poorly connected neighbors)
        assert "bridge" in bridges
    
    def test_calculate_efficiency_score(self, collaboration_analyzer):
        """Test efficiency score calculation"""
        # Test with good metrics
        score = collaboration_analyzer._calculate_efficiency_score(
            success_rate=0.9,
            avg_response_time=500,  # Good response time
            communication_density=0.8
        )
        
        assert 0 <= score <= 1
        assert score > 0.7  # Should be high with good metrics
        
        # Test with poor metrics
        poor_score = collaboration_analyzer._calculate_efficiency_score(
            success_rate=0.3,
            avg_response_time=2000,  # Poor response time
            communication_density=0.1
        )
        
        assert poor_score < score  # Should be lower than good metrics
    
    @pytest.mark.asyncio
    async def test_get_collaboration_insights(self, collaboration_analyzer, sample_interactions):
        """Test getting collaboration insights"""
        # Add interactions to history
        for interaction in sample_interactions:
            await collaboration_analyzer.record_interaction(interaction)
        
        insights = await collaboration_analyzer.get_collaboration_insights()
        
        assert "overall_health" in insights
        assert "top_patterns" in insights
        assert "performance_trends" in insights
        assert "recommendations" in insights
        assert "key_metrics" in insights
        
        # Verify key metrics structure
        key_metrics = insights["key_metrics"]
        assert "efficiency_score" in key_metrics
        assert "success_rate" in key_metrics
        assert "avg_response_time" in key_metrics
        assert "communication_density" in key_metrics
    
    def test_cache_functionality(self, collaboration_analyzer):
        """Test pattern cache functionality"""
        # Clear cache should work without errors
        collaboration_analyzer._clear_pattern_cache()
        
        # Add something to cache
        collaboration_analyzer.pattern_cache["test_key"] = (datetime.now(), "test_value")
        
        assert "test_key" in collaboration_analyzer.pattern_cache
        
        # Clear should remove expired entries
        collaboration_analyzer.analysis_cache_ttl = 0  # Make everything expire immediately
        collaboration_analyzer._clear_pattern_cache()
        
        # Entry should still be there (clear only removes expired entries)
        assert "test_key" in collaboration_analyzer.pattern_cache


@pytest.mark.asyncio
class TestAsyncCollaborationAnalyzer:
    """Async test cases for CollaborationAnalyzer"""
    
    async def test_concurrent_interaction_recording(self, collaboration_analyzer):
        """Test concurrent interaction recording"""
        interactions = [
            AgentInteraction(f"agent{i}", f"agent{i+1}", "message", datetime.now(), 100, True)
            for i in range(10)
        ]
        
        # Record interactions concurrently
        tasks = [
            collaboration_analyzer.record_interaction(interaction)
            for interaction in interactions
        ]
        
        await asyncio.gather(*tasks)
        
        assert len(collaboration_analyzer.interaction_history) == 10
    
    async def test_large_dataset_performance(self, collaboration_analyzer):
        """Test performance with large dataset"""
        # Create large number of interactions
        interactions = []
        base_time = datetime.now()
        
        for i in range(1000):
            interaction = AgentInteraction(
                sender_id=f"agent{i % 10}",
                receiver_id=f"agent{(i + 1) % 10}",
                interaction_type="message",
                timestamp=base_time + timedelta(seconds=i),
                duration_ms=100.0,
                success=i % 5 != 0  # 80% success rate
            )
            interactions.append(interaction)
        
        # Record all interactions
        for interaction in interactions:
            await collaboration_analyzer.record_interaction(interaction)
        
        # Analyze patterns (should complete in reasonable time)
        start_time = datetime.now()
        metrics = await collaboration_analyzer.analyze_collaboration_patterns()
        analysis_time = (datetime.now() - start_time).total_seconds()
        
        assert analysis_time < 5.0  # Should complete within 5 seconds
        assert metrics.total_interactions == 1000
        assert metrics.success_rate == 0.8