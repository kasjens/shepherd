"""
Unit tests for PatternLearner - Phase 8

Tests the pattern learning system including:
- Workflow pattern extraction
- Success/failure analysis
- Pattern optimization
- Recommendation generation
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass

from src.learning.pattern_learner import PatternLearner, PatternMetrics
from src.memory.persistent_knowledge import PersistentKnowledgeBase
from src.core.models import WorkflowResult, ExecutionStep, ExecutionStatus, WorkflowPattern


@pytest.fixture
def mock_knowledge_base():
    """Create a mock knowledge base for testing"""
    kb = AsyncMock(spec=PersistentKnowledgeBase)
    kb.store_learned_pattern = AsyncMock()
    kb.store_failure_pattern = AsyncMock()
    kb.find_similar_patterns = AsyncMock(return_value=[])
    kb.get_knowledge_statistics = AsyncMock(return_value={
        'learned_pattern': {'count': 10},
        'failure_pattern': {'count': 2}
    })
    return kb


@pytest.fixture
def pattern_learner(mock_knowledge_base):
    """Create a pattern learner instance for testing"""
    return PatternLearner(mock_knowledge_base)


@pytest.fixture
def sample_workflow_result():
    """Create a sample successful workflow result"""
    steps = [
        ExecutionStep(
            agent_id="agent1",
            description="Initialize data",
            status=ExecutionStatus.COMPLETED,
            execution_time=10.0
        ),
        ExecutionStep(
            agent_id="agent2", 
            description="Process data",
            status=ExecutionStatus.COMPLETED,
            execution_time=20.0
        ),
        ExecutionStep(
            agent_id="agent1",
            description="Finalize results",
            status=ExecutionStatus.COMPLETED,
            execution_time=5.0
        )
    ]
    
    # Create mock workflow result
    workflow = MagicMock(spec=WorkflowResult)
    workflow.pattern = WorkflowPattern.SEQUENTIAL
    workflow.steps = steps
    workflow.success_rate = 0.9
    workflow.total_duration = 35.0
    workflow.id = "test_workflow_123"
    
    # Add resource usage
    workflow.resource_usage = {
        'cpu_usage': 0.6,
        'memory_usage': 0.4,
        'efficiency': 0.8
    }
    
    return workflow


@pytest.fixture
def sample_failed_workflow():
    """Create a sample failed workflow result"""
    steps = [
        ExecutionStep(
            agent_id="agent1",
            description="Initialize data",
            status=ExecutionStatus.COMPLETED,
            execution_time=10.0
        ),
        ExecutionStep(
            agent_id="agent2",
            description="Process data", 
            status=ExecutionStatus.FAILED,
            execution_time=15.0
        )
    ]
    
    workflow = MagicMock(spec=WorkflowResult)
    workflow.pattern = WorkflowPattern.SEQUENTIAL
    workflow.steps = steps
    workflow.success_rate = 0.3
    workflow.total_duration = 25.0
    workflow.id = "failed_workflow_456"
    
    return workflow


@pytest.mark.asyncio
class TestPatternLearner:
    """Test cases for PatternLearner"""
    
    async def test_initialization(self, mock_knowledge_base):
        """Test pattern learner initialization"""
        learner = PatternLearner(mock_knowledge_base)
        
        assert learner.knowledge_base == mock_knowledge_base
        assert learner.min_confidence == 0.7
        assert learner.pattern_cache == {}
        assert learner.learning_buffer == []
        assert learner.optimization_threshold == 0.8
    
    async def test_analyze_successful_workflow(self, pattern_learner, mock_knowledge_base, sample_workflow_result):
        """Test analyzing a successful workflow"""
        result = await pattern_learner.analyze_workflow_success(sample_workflow_result)
        
        assert result['action'] == 'created'
        assert 'pattern_id' in result
        assert result['confidence'] >= pattern_learner.min_confidence
        
        # Verify pattern was stored
        mock_knowledge_base.store_learned_pattern.assert_called_once()
        
        # Verify workflow was added to learning buffer
        assert len(pattern_learner.learning_buffer) == 1
    
    async def test_analyze_low_success_workflow(self, pattern_learner, sample_workflow_result):
        """Test analyzing workflow with low success rate"""
        sample_workflow_result.success_rate = 0.5  # Below threshold
        
        result = await pattern_learner.analyze_workflow_success(sample_workflow_result)
        
        assert result['learned'] is False
        assert result['reason'] == 'success_rate_too_low'
        assert result['success_rate'] == 0.5
    
    async def test_extract_comprehensive_pattern(self, pattern_learner, sample_workflow_result):
        """Test extracting comprehensive pattern from workflow"""
        pattern = await pattern_learner._extract_comprehensive_pattern(sample_workflow_result)
        
        # Check basic structure
        assert pattern['workflow_type'] == 'SEQUENTIAL'
        assert 'key_features' in pattern
        assert 'agent_sequence' in pattern
        assert 'performance_metrics' in pattern
        assert 'metadata' in pattern
        
        # Check key features
        features = pattern['key_features']
        assert features['workflow_pattern'] == 'SEQUENTIAL'
        assert features['agent_count'] == 2  # agent1 and agent2
        assert features['step_count'] == 3
        
        # Check performance metrics
        perf = pattern['performance_metrics']
        assert perf['duration'] == 35.0
        assert perf['success_rate'] == 0.9
    
    async def test_extract_agent_sequence(self, pattern_learner, sample_workflow_result):
        """Test extracting agent sequence from workflow"""
        sequence = pattern_learner._extract_agent_sequence(sample_workflow_result)
        
        assert len(sequence) == 3
        assert sequence[0]['agent_id'] == 'agent1'
        assert sequence[0]['order'] == 1
        assert sequence[1]['agent_id'] == 'agent2'
        assert sequence[1]['order'] == 2
        assert sequence[2]['agent_id'] == 'agent1'
        assert sequence[2]['order'] == 3
        
        # All should be successful
        assert all(action['success'] for action in sequence)
    
    async def test_calculate_resource_efficiency(self, pattern_learner, sample_workflow_result):
        """Test resource efficiency calculation"""
        efficiency = pattern_learner._calculate_resource_efficiency(sample_workflow_result)
        
        # Should be based on resource_usage in sample
        assert 0.0 <= efficiency <= 1.0
        assert efficiency > 0.5  # Should be reasonably efficient
    
    async def test_identify_success_factors(self, pattern_learner, sample_workflow_result):
        """Test identification of success factors"""
        factors = pattern_learner._identify_success_factors(sample_workflow_result)
        
        assert len(factors) >= 1
        
        # Should identify all critical steps succeeded
        critical_factor = next((f for f in factors if f['factor'] == 'all_critical_steps_succeeded'), None)
        assert critical_factor is not None
        assert critical_factor['impact'] == 'high'
    
    async def test_update_existing_pattern(self, pattern_learner, mock_knowledge_base, sample_workflow_result):
        """Test updating an existing similar pattern"""
        # Mock existing pattern
        existing_pattern = {
            'id': 'existing_123',
            'data': {
                'performance_metrics': {
                    'duration': 30.0,
                    'success_rate': 0.8,
                    'resource_efficiency': 0.7
                },
                'usage_count': 5,
                'confidence': 0.8,
                'success_factors': []
            }
        }
        
        mock_knowledge_base.find_similar_patterns.return_value = [
            {'distance': 0.05, **existing_pattern}  # Very similar
        ]
        
        result = await pattern_learner.analyze_workflow_success(sample_workflow_result)
        
        assert result['action'] == 'updated'
        assert result['usage_count'] == 6  # Incremented
        assert result['confidence'] > 0.8  # Should increase
        
        # Verify pattern was updated
        mock_knowledge_base.store_learned_pattern.assert_called_once()
    
    async def test_generate_pattern_key(self, pattern_learner):
        """Test pattern key generation"""
        pattern = {
            'workflow_type': 'SEQUENTIAL',
            'key_features': {
                'agent_count': 2,
                'step_count': 3,
                'parallel_execution': False,
                'has_conditions': True
            }
        }
        
        key = pattern_learner._generate_pattern_key(pattern)
        
        expected = 'SEQUENTIAL_2_3_False_True'
        assert key == expected
    
    async def test_batch_optimization_trigger(self, pattern_learner, mock_knowledge_base):
        """Test batch optimization is triggered when buffer is full"""
        # Fill the learning buffer
        for i in range(10):
            workflow = MagicMock()
            workflow.pattern = WorkflowPattern.SEQUENTIAL
            workflow.success_rate = 0.9
            workflow.total_duration = 30.0
            workflow.steps = []
            pattern_learner.learning_buffer.append(workflow)
        
        # Process one more workflow to trigger batch optimization
        sample_workflow = MagicMock()
        sample_workflow.pattern = WorkflowPattern.SEQUENTIAL
        sample_workflow.success_rate = 0.9
        sample_workflow.total_duration = 35.0
        sample_workflow.steps = [
            MagicMock(agent_id="agent1", status=ExecutionStatus.COMPLETED)
        ]
        sample_workflow.id = "trigger_workflow"
        
        with patch.object(pattern_learner, '_batch_pattern_optimization') as mock_batch:
            await pattern_learner.analyze_workflow_success(sample_workflow)
            mock_batch.assert_called_once()
        
        # Buffer should be cleared after optimization
        assert len(pattern_learner.learning_buffer) == 0
    
    async def test_pattern_recommendations(self, pattern_learner, mock_knowledge_base):
        """Test getting pattern recommendations"""
        # Mock similar patterns
        mock_patterns = [
            {
                'data': {
                    'pattern_id': 'pattern_1',
                    'workflow_type': 'SEQUENTIAL',
                    'confidence': 0.9,
                    'performance_metrics': {
                        'duration': 20.0,
                        'success_rate': 0.95
                    },
                    'key_features': {
                        'agent_count': 2,
                        'step_count': 3
                    },
                    'success_factors': [
                        {'factor': 'efficient_execution', 'impact': 'high'}
                    ]
                }
            }
        ]
        
        mock_knowledge_base.find_similar_patterns.return_value = mock_patterns
        
        context = {
            'workflow_type': 'SEQUENTIAL',
            'requirements': ['fast_execution'],
            'constraints': ['limited_resources']
        }
        
        recommendations = await pattern_learner.get_pattern_recommendations(context)
        
        assert len(recommendations) == 1
        rec = recommendations[0]
        assert rec['pattern_id'] == 'pattern_1'
        assert rec['workflow_type'] == 'SEQUENTIAL'
        assert rec['confidence'] == 0.9
        assert 'recommendation_score' in rec
        assert rec['recommendation_score'] > 0.5
    
    async def test_analyze_failure_patterns(self, pattern_learner, mock_knowledge_base, sample_failed_workflow):
        """Test analyzing failure patterns"""
        result = await pattern_learner.analyze_failure_patterns(sample_failed_workflow)
        
        assert result['analyzed'] is True
        assert result['failure_points'] >= 1
        assert len(result['suggestions']) >= 1
        
        # Verify failure pattern was stored
        mock_knowledge_base.store_failure_pattern.assert_called_once()
    
    async def test_successful_workflow_not_analyzed_for_failure(self, pattern_learner, sample_workflow_result):
        """Test that successful workflows are not analyzed for failure"""
        result = await pattern_learner.analyze_failure_patterns(sample_workflow_result)
        
        assert result['analyzed'] is False
        assert result['reason'] == 'workflow_successful'
    
    async def test_find_common_sequences(self, pattern_learner):
        """Test finding common sequences across workflows"""
        # Create workflows with common sequences
        workflows = []
        for i in range(3):
            workflow = MagicMock()
            workflow.steps = [
                MagicMock(agent_id="agent1", description="init", status=ExecutionStatus.COMPLETED),
                MagicMock(agent_id="agent2", description="process", status=ExecutionStatus.COMPLETED),
                MagicMock(agent_id="agent1", description="finalize", status=ExecutionStatus.COMPLETED)
            ]
            workflows.append(workflow)
        
        common_sequences = pattern_learner._find_common_sequences(workflows)
        
        # Should find common pairs that appear in all workflows
        assert len(common_sequences) >= 1
        
        # Check that sequences have high frequency
        for seq in common_sequences:
            assert seq['frequency'] >= 0.5  # Appears in >50% of workflows
            assert seq['confidence'] >= 0.5
    
    async def test_performance_metrics_calculation(self, pattern_learner, sample_workflow_result):
        """Test performance metrics calculation"""
        pattern = await pattern_learner._extract_comprehensive_pattern(sample_workflow_result)
        
        perf = pattern['performance_metrics']
        
        assert perf['duration'] == 35.0
        assert perf['success_rate'] == 0.9
        assert 'step_success_rates' in perf
        assert 'resource_efficiency' in perf
        
        # Step success rates should be calculated
        step_rates = perf['step_success_rates']
        assert len(step_rates) >= 1
    
    async def test_learning_summary(self, pattern_learner, mock_knowledge_base):
        """Test getting learning summary"""
        summary = await pattern_learner.get_learning_summary()
        
        assert 'total_patterns_learned' in summary
        assert 'failure_patterns_identified' in summary
        assert 'active_patterns_cached' in summary
        assert 'learning_buffer_size' in summary
        
        assert summary['total_patterns_learned'] == 10
        assert summary['failure_patterns_identified'] == 2


@pytest.mark.asyncio
class TestPatternMetrics:
    """Test PatternMetrics dataclass"""
    
    def test_pattern_metrics_creation(self):
        """Test creating PatternMetrics"""
        metrics = PatternMetrics(
            success_rate=0.9,
            average_duration=30.0,
            resource_efficiency=0.8,
            consistency_score=0.85,
            usage_count=5,
            last_used=datetime.utcnow()
        )
        
        assert metrics.success_rate == 0.9
        assert metrics.average_duration == 30.0
        assert metrics.resource_efficiency == 0.8
        assert metrics.consistency_score == 0.85
        assert metrics.usage_count == 5
    
    def test_overall_score_calculation(self):
        """Test overall score calculation"""
        metrics = PatternMetrics(
            success_rate=0.9,
            average_duration=120.0,  # 2 minutes
            resource_efficiency=0.8,
            consistency_score=0.85,
            usage_count=15,  # High usage
            last_used=datetime.utcnow()
        )
        
        score = metrics.overall_score
        
        # Should be a weighted combination
        assert 0.0 <= score <= 1.0
        
        # High usage should boost the score
        assert score > 0.8  # Should be high due to good metrics and high usage
    
    def test_overall_score_with_poor_metrics(self):
        """Test overall score with poor performance metrics"""
        metrics = PatternMetrics(
            success_rate=0.4,  # Poor success rate
            average_duration=600.0,  # Very long duration
            resource_efficiency=0.3,  # Poor efficiency
            consistency_score=0.4,  # Poor consistency
            usage_count=2,  # Low usage
            last_used=datetime.utcnow()
        )
        
        score = metrics.overall_score
        
        # Should be low due to poor metrics
        assert score < 0.5


@pytest.mark.asyncio
class TestPatternOptimization:
    """Test pattern optimization features"""
    
    async def test_optimization_threshold_check(self, pattern_learner):
        """Test optimization threshold checking"""
        # Create workflows with different success rates
        good_workflow = MagicMock()
        good_workflow.success_rate = 0.9
        good_workflow.pattern = WorkflowPattern.SEQUENTIAL
        good_workflow.total_duration = 30.0
        good_workflow.steps = []
        
        poor_workflow = MagicMock()
        poor_workflow.success_rate = 0.5
        poor_workflow.pattern = WorkflowPattern.SEQUENTIAL
        poor_workflow.total_duration = 60.0
        poor_workflow.steps = []
        
        workflows = [good_workflow, poor_workflow]
        
        # Only workflows above optimization threshold should be used
        await pattern_learner._optimize_pattern_type('SEQUENTIAL', workflows)
        
        # Should process the optimization (details depend on implementation)
        # This is more of a smoke test to ensure no errors
    
    async def test_recommendation_score_calculation(self, pattern_learner):
        """Test recommendation score calculation"""
        pattern = {
            'workflow_type': 'SEQUENTIAL',
            'performance_metrics': {
                'success_rate': 0.9,
                'duration': 30.0
            },
            'usage_count': 10,
            'confidence': 0.8
        }
        
        context = {
            'workflow_type': 'SEQUENTIAL',
            'requirements': ['efficiency']
        }
        
        score = pattern_learner._calculate_recommendation_score(pattern, context)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be good match
    
    async def test_recommendation_score_mismatch(self, pattern_learner):
        """Test recommendation score for mismatched pattern"""
        pattern = {
            'workflow_type': 'PARALLEL',  # Different type
            'performance_metrics': {
                'success_rate': 0.6,  # Lower success
                'duration': 120.0  # Longer duration
            },
            'usage_count': 1,  # Low usage
            'confidence': 0.5  # Lower confidence
        }
        
        context = {
            'workflow_type': 'SEQUENTIAL',
            'requirements': ['speed']
        }
        
        score = pattern_learner._calculate_recommendation_score(pattern, context)
        
        assert score < 0.5  # Should be poor match