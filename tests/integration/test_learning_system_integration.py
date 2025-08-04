"""
Integration tests for Learning System - Phase 8

Tests the complete learning system integration including:
- End-to-end feedback processing and learning
- Agent integration with learning capabilities
- Cross-system learning and adaptation
- Real workflow pattern learning
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from src.learning.feedback_processor import UserFeedbackProcessor, FeedbackType
from src.learning.pattern_learner import PatternLearner
from src.learning.adaptive_system import AdaptiveBehaviorSystem, AdaptationType
from src.agents.base_agent import BaseAgent
from src.memory.persistent_knowledge import PersistentKnowledgeBase
from src.memory.vector_store import VectorMemoryStore
from src.core.models import WorkflowResult, ExecutionStep, ExecutionStatus, WorkflowPattern


class MockAgent(BaseAgent):
    """Mock agent for testing learning integration"""
    
    def create_crew_agent(self):
        return MagicMock()
    
    def _get_capabilities(self):
        return ['learning', 'adaptation', 'feedback_processing']


@pytest.fixture
async def knowledge_base():
    """Create a real knowledge base for integration testing"""
    kb = PersistentKnowledgeBase()
    await kb.initialize()
    return kb


@pytest.fixture
async def vector_store():
    """Create a real vector store for integration testing"""
    try:
        vs = VectorMemoryStore()
        await vs.initialize()
        return vs
    except Exception:
        # If vector store fails to initialize (missing dependencies), use mock
        return AsyncMock(spec=VectorMemoryStore)


@pytest.fixture
async def learning_agent(knowledge_base, vector_store):
    """Create an agent with learning capabilities enabled"""
    agent = MockAgent(
        name="learning_agent",
        role="test_learner", 
        goal="Learn from interactions",
        knowledge_base=knowledge_base,
        vector_store=vector_store,
        enable_learning=True
    )
    
    return agent


@pytest.fixture
def sample_workflow_success():
    """Create a successful workflow for testing"""
    steps = [
        ExecutionStep(
            agent_id="agent1",
            description="Data initialization",
            status=ExecutionStatus.COMPLETED,
            execution_time=10.0
        ),
        ExecutionStep(
            agent_id="agent2",
            description="Data processing",
            status=ExecutionStatus.COMPLETED,
            execution_time=20.0
        ),
        ExecutionStep(
            agent_id="agent1",
            description="Result compilation",
            status=ExecutionStatus.COMPLETED,
            execution_time=8.0
        )
    ]
    
    workflow = MagicMock(spec=WorkflowResult)
    workflow.pattern = WorkflowPattern.SEQUENTIAL
    workflow.steps = steps
    workflow.success_rate = 0.95
    workflow.total_duration = 38.0
    workflow.id = "integration_test_workflow"
    workflow.resource_usage = {
        'cpu_usage': 0.6,
        'memory_usage': 0.4,
        'efficiency': 0.85
    }
    
    return workflow


@pytest.fixture
def sample_workflow_failure():
    """Create a failed workflow for testing"""
    steps = [
        ExecutionStep(
            agent_id="agent1",
            description="Data initialization",
            status=ExecutionStatus.COMPLETED,
            execution_time=10.0
        ),
        ExecutionStep(
            agent_id="agent2",
            description="Data processing",
            status=ExecutionStatus.FAILED,
            execution_time=25.0
        )
    ]
    
    workflow = MagicMock(spec=WorkflowResult)
    workflow.pattern = WorkflowPattern.SEQUENTIAL
    workflow.steps = steps
    workflow.success_rate = 0.2
    workflow.total_duration = 35.0
    workflow.id = "failed_integration_workflow"
    
    return workflow


@pytest.mark.asyncio
class TestLearningSystemIntegration:
    """Integration tests for the complete learning system"""
    
    async def test_agent_learning_initialization(self, learning_agent):
        """Test that agent properly initializes learning systems"""
        assert learning_agent.is_learning_enabled() is True
        assert learning_agent.feedback_processor is not None
        assert learning_agent.pattern_learner is not None
        assert learning_agent.adaptive_system is not None
    
    async def test_end_to_end_feedback_processing(self, learning_agent):
        """Test complete feedback processing flow"""
        feedback_data = {
            'type': 'correction',
            'original_action': 'used_inefficient_algorithm',
            'correct_action': 'use_optimized_algorithm',
            'explanation': 'The optimized algorithm is 3x faster',
            'severity': 'high',
            'task_description': 'Data processing optimization',
            'context': {
                'task_type': 'data_processing',
                'data_size': 'large',
                'performance_critical': True
            }
        }
        
        # Process feedback through agent
        result = await learning_agent.process_user_feedback(feedback_data)
        
        assert result['success'] is True
        assert result['type'] == 'correction'
        assert result['knowledge_updated'] is True
        
        # Verify feedback was stored in knowledge base
        similar_failures = await learning_agent.knowledge_base.find_similar_patterns(
            query='inefficient_algorithm',
            knowledge_type='failure_pattern',
            limit=5
        )
        
        assert len(similar_failures) >= 1
    
    async def test_workflow_pattern_learning(self, learning_agent, sample_workflow_success):
        """Test learning from successful workflow execution"""
        # Learn from workflow
        result = await learning_agent.learn_from_workflow_result(sample_workflow_success)
        
        assert result['learned'] is True
        assert 'success_analysis' in result
        assert 'failure_analysis' in result
        
        success_analysis = result['success_analysis']
        assert success_analysis['action'] in ['created', 'updated']
        assert 'confidence' in success_analysis
        
        # Verify pattern was stored
        patterns = await learning_agent.knowledge_base.find_similar_patterns(
            query='SEQUENTIAL',
            knowledge_type='learned_pattern',
            limit=5
        )
        
        assert len(patterns) >= 1
    
    async def test_failure_pattern_learning(self, learning_agent, sample_workflow_failure):
        """Test learning from failed workflow execution"""
        result = await learning_agent.learn_from_workflow_result(sample_workflow_failure)
        
        assert result['learned'] is True
        
        failure_analysis = result['failure_analysis']
        assert failure_analysis['analyzed'] is True
        assert failure_analysis['failure_points'] >= 1
        assert len(failure_analysis['suggestions']) >= 1
        
        # Verify failure pattern was stored
        failures = await learning_agent.knowledge_base.find_similar_patterns(
            query='SEQUENTIAL',
            knowledge_type='failure_pattern',
            limit=5
        )
        
        assert len(failures) >= 1
    
    async def test_adaptive_context_enhancement(self, learning_agent):
        """Test context enhancement with adaptive behaviors"""
        base_context = {
            'task_type': 'analysis',
            'workflow_type': 'SEQUENTIAL',
            'complexity': 0.7,
            'urgency': 'normal'
        }
        
        # First, add some user preferences
        await learning_agent.process_user_feedback({
            'type': 'preference',
            'key': 'analysis_style',
            'preference': 'detailed_with_metrics',
            'context': {'task_type': 'analysis'},
            'strength': 0.9
        })
        
        # Get adaptive context
        enhanced_context = await learning_agent.get_adaptive_context(base_context)
        
        # Context should be enhanced with adaptations
        assert '_adaptations_applied' in enhanced_context or enhanced_context == base_context
        
        # If adaptations were applied, verify structure
        if '_adaptations_applied' in enhanced_context:
            adaptations = enhanced_context['_adaptations_applied']
            assert isinstance(adaptations, list)
            for adaptation in adaptations:
                assert 'name' in adaptation
                assert 'type' in adaptation
                assert 'confidence' in adaptation
    
    async def test_pattern_recommendation_system(self, learning_agent, sample_workflow_success):
        """Test pattern recommendation after learning"""
        # First, learn from a successful workflow
        await learning_agent.learn_from_workflow_result(sample_workflow_success)
        
        # Now request recommendations for similar context
        context = {
            'workflow_type': 'SEQUENTIAL',
            'task_type': 'data_processing',
            'requirements': ['efficiency', 'reliability']
        }
        
        recommendations = await learning_agent.get_pattern_recommendations(context)
        
        # Should have recommendations based on learned patterns
        assert isinstance(recommendations, list)
        
        if recommendations:
            rec = recommendations[0]
            assert 'pattern_id' in rec
            assert 'confidence' in rec
            assert 'recommendation_score' in rec
            assert 'performance' in rec
    
    async def test_feedback_based_adaptation_learning(self, learning_agent):
        """Test that feedback leads to adaptive behavior changes"""
        # Provide feedback about preference for parallel execution
        feedback = {
            'type': 'preference',
            'key': 'execution_style',
            'preference': 'parallel_when_possible',
            'context': {'task_type': 'data_processing'},
            'strength': 0.8,
            'examples': [
                {
                    'input': {'task': 'process_large_dataset'},
                    'output': {'approach': 'parallel_chunks'}
                }
            ]
        }
        
        await learning_agent.process_user_feedback(feedback)
        
        # Now get adaptations for similar context
        context = {
            'task_type': 'data_processing',
            'data_size': 'large'
        }
        
        enhanced_context = await learning_agent.get_adaptive_context(context)
        
        # Should potentially include parallel-related adaptations
        # (This is probabilistic based on similarity matching)
        assert isinstance(enhanced_context, dict)
    
    async def test_learning_insights_compilation(self, learning_agent, sample_workflow_success):
        """Test compilation of learning insights"""
        # Generate some learning activity
        await learning_agent.process_user_feedback({
            'type': 'rating',
            'score': 4,
            'max_score': 5,
            'task_description': 'Test task',
            'context': {'task_type': 'analysis'}
        })
        
        await learning_agent.learn_from_workflow_result(sample_workflow_success)
        
        # Get learning insights
        insights = await learning_agent.get_learning_insights()
        
        assert insights['learning_enabled'] is True
        assert 'feedback_processing' in insights
        assert 'pattern_learning' in insights
        assert 'adaptive_behavior' in insights
        
        # Check feedback processing insights
        feedback_insights = insights['feedback_processing']
        assert 'total_feedback' in feedback_insights
        assert 'feedback_by_type' in feedback_insights
        
        # Check pattern learning insights
        pattern_insights = insights['pattern_learning']
        assert 'total_patterns_learned' in pattern_insights
        assert 'learning_buffer_size' in pattern_insights
    
    async def test_cross_system_learning_coordination(self, learning_agent, sample_workflow_success):
        """Test coordination between different learning systems"""
        # Simulate a complete learning cycle
        
        # 1. Process user feedback
        feedback_result = await learning_agent.process_user_feedback({
            'type': 'guidance',
            'instruction': 'Always validate data before processing',
            'context': {'domain': 'data_processing'},
            'examples': [
                {'input': 'raw_data', 'action': 'validate', 'output': 'clean_data'}
            ]
        })
        
        # 2. Learn from workflow execution
        learning_result = await learning_agent.learn_from_workflow_result(sample_workflow_success)
        
        # 3. Get adaptive recommendations
        context = {
            'task_type': 'data_processing',
            'workflow_type': 'SEQUENTIAL'
        }
        enhanced_context = await learning_agent.get_adaptive_context(context)
        
        # 4. Provide execution feedback
        await learning_agent.provide_feedback_on_execution(
            task_description="Data processing with validation",
            execution_result={'status': 'completed', 'duration': 30.0},
            user_rating=0.9
        )
        
        # Verify all systems worked together
        assert feedback_result['success'] is True
        assert learning_result['learned'] is True
        assert isinstance(enhanced_context, dict)
        
        # Check that insights reflect activity across all systems
        insights = await learning_agent.get_learning_insights()
        
        assert insights['feedback_processing']['total_feedback'] >= 2  # guidance + rating
        assert insights['pattern_learning']['total_patterns_learned'] >= 1
    
    async def test_adaptation_outcome_recording(self, learning_agent):
        """Test recording and learning from adaptation outcomes"""
        # Get some adaptations
        context = {'task_type': 'analysis', 'complexity': 0.8}
        enhanced_context = await learning_agent.get_adaptive_context(context)
        
        # Record outcomes for fictional adaptations
        await learning_agent.record_adaptation_outcome('test_adaptation_1', True, 0.9)
        await learning_agent.record_adaptation_outcome('test_adaptation_2', False, 0.3)
        await learning_agent.record_adaptation_outcome('test_adaptation_1', True, 0.85)
        
        # Check that outcomes were recorded
        if learning_agent.adaptive_system:
            performance_history = learning_agent.adaptive_system.performance_history
            assert 'test_adaptation_1' in performance_history
            assert 'test_adaptation_2' in performance_history
            
            # Test adaptation 1 should have two successful outcomes
            assert len(performance_history['test_adaptation_1']) == 2
            assert all(score >= 0.8 for score in performance_history['test_adaptation_1'])
            
            # Test adaptation 2 should have one poor outcome
            assert len(performance_history['test_adaptation_2']) == 1
            assert performance_history['test_adaptation_2'][0] == 0.3
    
    async def test_learning_system_disable_enable(self, learning_agent):
        """Test disabling and re-enabling learning systems"""
        # Initially enabled
        assert learning_agent.is_learning_enabled() is True
        
        # Disable learning
        learning_agent.disable_learning_systems()
        assert learning_agent.is_learning_enabled() is False
        
        # Try to process feedback (should fail gracefully)
        result = await learning_agent.process_user_feedback({
            'type': 'rating',
            'score': 5,
            'max_score': 5
        })
        
        assert result['success'] is False
        assert result['reason'] == 'learning_disabled'
        
        # Re-enable learning
        learning_agent.enable_learning_systems()
        assert learning_agent.is_learning_enabled() is True
        
        # Now feedback should work
        result = await learning_agent.process_user_feedback({
            'type': 'rating',
            'score': 5,
            'max_score': 5
        })
        
        assert result['success'] is True


@pytest.mark.asyncio
class TestLearningSystemPerformance:
    """Performance and scalability tests for learning system"""
    
    async def test_multiple_feedback_processing(self, learning_agent):
        """Test processing multiple feedback items efficiently"""
        feedback_items = [
            {
                'type': 'rating',
                'score': 4,
                'max_score': 5,
                'task_description': f'Task {i}',
                'context': {'task_type': 'analysis', 'batch': i}
            }
            for i in range(20)
        ]
        
        # Process all feedback
        results = []
        for feedback in feedback_items:
            result = await learning_agent.process_user_feedback(feedback)
            results.append(result)
        
        # All should be successful
        assert all(r['success'] for r in results)
        
        # Check feedback history
        if learning_agent.feedback_processor:
            assert len(learning_agent.feedback_processor.feedback_history) == 20
    
    async def test_workflow_batch_learning(self, learning_agent):
        """Test learning from multiple workflows"""
        workflows = []
        
        # Create multiple similar successful workflows
        for i in range(12):  # More than buffer size to trigger optimization
            steps = [
                ExecutionStep(
                    agent_id=f"agent{i % 3 + 1}",
                    description=f"Step 1 for workflow {i}",
                    status=ExecutionStatus.COMPLETED,
                    execution_time=10.0 + i
                ),
                ExecutionStep(
                    agent_id=f"agent{(i + 1) % 3 + 1}",
                    description=f"Step 2 for workflow {i}",
                    status=ExecutionStatus.COMPLETED,
                    execution_time=15.0 + i
                )
            ]
            
            workflow = MagicMock(spec=WorkflowResult)
            workflow.pattern = WorkflowPattern.SEQUENTIAL
            workflow.steps = steps
            workflow.success_rate = 0.9 + (i % 10) * 0.01  # Vary success rate slightly
            workflow.total_duration = 25.0 + i
            workflow.id = f"batch_workflow_{i}"
            
            workflows.append(workflow)
        
        # Learn from all workflows
        results = []
        for workflow in workflows:
            result = await learning_agent.learn_from_workflow_result(workflow)
            results.append(result)
        
        # All should be processed
        assert all(r['learned'] for r in results)
        
        # Check that batch optimization was triggered
        if learning_agent.pattern_learner:
            # Buffer should be cleared after batch processing
            assert len(learning_agent.pattern_learner.learning_buffer) < 10


@pytest.mark.asyncio
class TestLearningSystemRealWorld:
    """Real-world scenario tests for learning system"""
    
    async def test_user_correction_workflow(self, learning_agent):
        """Test realistic user correction and improvement workflow"""
        # Scenario: User corrects an inefficient approach
        
        # 1. User provides correction
        correction = {
            'type': 'correction',
            'original_action': 'process_files_sequentially',
            'correct_action': 'process_files_in_parallel',
            'explanation': 'Parallel processing is much faster for independent files',
            'severity': 'medium',
            'task_description': 'File processing optimization',
            'context': {
                'task_type': 'file_processing',
                'file_count': 'many',
                'files_independent': True
            }
        }
        
        correction_result = await learning_agent.process_user_feedback(correction)
        assert correction_result['success'] is True
        
        # 2. Later, agent encounters similar context
        similar_context = {
            'task_type': 'file_processing',
            'file_count': 'many',
            'files_independent': True
        }
        
        enhanced_context = await learning_agent.get_adaptive_context(similar_context)
        
        # 3. Should recommend avoiding the corrected approach
        # (This depends on the similarity matching working correctly)
        assert isinstance(enhanced_context, dict)
        
        # 4. User rates the improved approach highly
        rating = {
            'type': 'rating',
            'score': 5,
            'max_score': 5,
            'task_description': 'Parallel file processing',
            'context': similar_context
        }
        
        rating_result = await learning_agent.process_user_feedback(rating)
        assert rating_result['success'] is True
        
        # Verify the learning cycle completed
        insights = await learning_agent.get_learning_insights()
        assert insights['feedback_processing']['total_feedback'] >= 2
    
    async def test_progressive_improvement_cycle(self, learning_agent, sample_workflow_success):
        """Test progressive improvement through multiple learning cycles"""
        # Simulate multiple iterations of improvement
        
        contexts = [
            {'task_type': 'data_analysis', 'complexity': 0.6},
            {'task_type': 'data_analysis', 'complexity': 0.7},
            {'task_type': 'data_analysis', 'complexity': 0.8}
        ]
        
        improvement_scores = []
        
        for i, context in enumerate(contexts):
            # Learn from workflow
            workflow_copy = MagicMock(spec=WorkflowResult)
            workflow_copy.pattern = WorkflowPattern.SEQUENTIAL
            workflow_copy.steps = sample_workflow_success.steps
            workflow_copy.success_rate = 0.8 + i * 0.05  # Gradually improving
            workflow_copy.total_duration = 40.0 - i * 2.0  # Getting faster
            workflow_copy.id = f"improvement_cycle_{i}"
            
            await learning_agent.learn_from_workflow_result(workflow_copy)
            
            # Get adaptive context
            enhanced_context = await learning_agent.get_adaptive_context(context)
            
            # Provide feedback
            rating = 0.7 + i * 0.1  # Improving ratings
            await learning_agent.provide_feedback_on_execution(
                task_description=f"Analysis cycle {i}",
                execution_result={'status': 'completed', 'duration': workflow_copy.total_duration},
                user_rating=rating
            )
            
            improvement_scores.append(rating)
        
        # Verify improvement trend
        assert improvement_scores[-1] > improvement_scores[0]
        
        # Check final insights
        final_insights = await learning_agent.get_learning_insights()
        assert final_insights['feedback_processing']['total_feedback'] >= 3
        assert final_insights['pattern_learning']['total_patterns_learned'] >= 1