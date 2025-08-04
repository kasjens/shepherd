"""
Unit tests for UserFeedbackProcessor - Phase 8

Tests the feedback processing system including:
- Different feedback types processing
- Pattern analysis and learning
- User preference storage
- Performance tracking
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.learning.feedback_processor import UserFeedbackProcessor, FeedbackType, FeedbackSeverity
from src.memory.persistent_knowledge import PersistentKnowledgeBase


@pytest.fixture
def mock_knowledge_base():
    """Create a mock knowledge base for testing"""
    kb = AsyncMock(spec=PersistentKnowledgeBase)
    kb.store_failure_pattern = AsyncMock()
    kb.store_learned_pattern = AsyncMock()
    kb.store_user_preference = AsyncMock()
    kb.store_domain_knowledge = AsyncMock()
    kb.store_workflow_template = AsyncMock()
    kb.find_similar_patterns = AsyncMock(return_value=[])
    return kb


@pytest.fixture
def feedback_processor(mock_knowledge_base):
    """Create a feedback processor instance for testing"""
    return UserFeedbackProcessor(mock_knowledge_base)


@pytest.mark.asyncio
class TestFeedbackProcessor:
    """Test cases for UserFeedbackProcessor"""
    
    async def test_initialization(self, mock_knowledge_base):
        """Test processor initialization"""
        processor = UserFeedbackProcessor(mock_knowledge_base)
        
        assert processor.knowledge_base == mock_knowledge_base
        assert processor.feedback_history == []
        assert processor.learning_rate == 0.1
        assert processor.confidence_threshold == 0.7
    
    async def test_process_correction_feedback(self, feedback_processor, mock_knowledge_base):
        """Test processing correction feedback"""
        feedback = {
            'type': 'correction',
            'original_action': 'wrong_approach',
            'correct_action': 'right_approach',
            'explanation': 'Should use right approach instead',
            'severity': 'high',
            'task_description': 'Test task'
        }
        
        result = await feedback_processor.process_feedback(feedback)
        
        assert result['success'] is True
        assert result['type'] == 'correction'
        assert result['knowledge_updated'] is True
        
        # Verify failure pattern was stored
        mock_knowledge_base.store_failure_pattern.assert_called_once()
        
        # Verify learned pattern was stored (high severity)
        mock_knowledge_base.store_learned_pattern.assert_called_once()
    
    async def test_process_preference_feedback(self, feedback_processor, mock_knowledge_base):
        """Test processing preference feedback"""
        feedback = {
            'type': 'preference',
            'key': 'communication_style',
            'preference': 'detailed_explanations',
            'context': {'task_type': 'analysis'},
            'strength': 0.8,
            'examples': [{'input': 'analyze data', 'output': 'detailed analysis'}]
        }
        
        result = await feedback_processor.process_feedback(feedback)
        
        assert result['success'] is True
        assert result['type'] == 'preference'
        assert result['stored'] is True
        
        # Verify preference was stored
        mock_knowledge_base.store_user_preference.assert_called_once()
    
    async def test_process_guidance_feedback(self, feedback_processor, mock_knowledge_base):
        """Test processing guidance feedback"""
        feedback = {
            'type': 'guidance',
            'instruction': 'Always validate inputs first',
            'context': {'domain': 'data_processing'},
            'examples': [
                {'input': 'data', 'action': 'validate', 'output': 'validated_data'}
            ],
            'constraints': ['safety_first'],
            'create_template': True,
            'template_name': 'data_validation'
        }
        
        result = await feedback_processor.process_feedback(feedback)
        
        assert result['success'] is True
        assert result['type'] == 'guidance'
        assert result['patterns_extracted'] >= 1
        assert result['template_created'] is True
        
        # Verify pattern and template storage
        mock_knowledge_base.store_learned_pattern.assert_called()
        mock_knowledge_base.store_workflow_template.assert_called_once()
    
    async def test_process_rating_feedback_low(self, feedback_processor, mock_knowledge_base):
        """Test processing low rating feedback"""
        feedback = {
            'type': 'rating',
            'score': 2,
            'max_score': 5,
            'context': {'task_type': 'analysis'},
            'task_description': 'Poor analysis task'
        }
        
        result = await feedback_processor.process_feedback(feedback)
        
        assert result['success'] is True
        assert result['type'] == 'rating'
        assert result['score'] == 0.4  # 2/5
        
        # Low rating should store as failure pattern
        mock_knowledge_base.store_failure_pattern.assert_called_once()
    
    async def test_process_rating_feedback_high(self, feedback_processor, mock_knowledge_base):
        """Test processing high rating feedback"""
        feedback = {
            'type': 'rating',
            'score': 4.5,
            'max_score': 5,
            'context': {'task_type': 'analysis'},
            'task_description': 'Great analysis task'
        }
        
        result = await feedback_processor.process_feedback(feedback)
        
        assert result['success'] is True
        assert result['type'] == 'rating'
        assert result['score'] == 0.9  # 4.5/5
        
        # High rating should store as successful pattern
        mock_knowledge_base.store_learned_pattern.assert_called_once()
    
    async def test_process_suggestion_feedback(self, feedback_processor, mock_knowledge_base):
        """Test processing suggestion feedback"""
        feedback = {
            'type': 'suggestion',
            'suggestion': 'Add retry mechanism for failed operations',
            'category': 'reliability',
            'priority': 'high',
            'benefits': ['improved reliability', 'better user experience']
        }
        
        result = await feedback_processor.process_feedback(feedback)
        
        assert result['success'] is True
        assert result['type'] == 'suggestion'
        assert result['stored'] is True
        assert 'feasibility' in result
        
        # Verify suggestion was stored
        mock_knowledge_base.store_domain_knowledge.assert_called_once()
    
    async def test_process_warning_feedback(self, feedback_processor, mock_knowledge_base):
        """Test processing warning feedback"""
        feedback = {
            'type': 'warning',
            'issue': 'Memory leak in data processing',
            'severity': 'critical',
            'context': {'module': 'data_processor'},
            'prevention': ['monitor memory usage', 'cleanup after processing']
        }
        
        result = await feedback_processor.process_feedback(feedback)
        
        assert result['success'] is True
        assert result['type'] == 'warning'
        assert result['severity'] == 'critical'
        assert result['safeguards_created'] is True
        
        # Critical warning should create failure pattern
        mock_knowledge_base.store_failure_pattern.assert_called()
    
    async def test_feedback_pattern_analysis(self, feedback_processor, mock_knowledge_base):
        """Test feedback pattern analysis after multiple feedbacks"""
        # Add multiple feedbacks of the same type
        for i in range(10):
            feedback = {
                'type': 'correction',
                'original_action': f'action_{i}',
                'correct_action': f'better_action_{i}',
                'context': {'common_key': 'common_value'},
                'severity': 'medium'
            }
            await feedback_processor.process_feedback(feedback)
        
        # Pattern analysis should have been triggered
        assert len(feedback_processor.feedback_history) == 10
        
        # Should have stored pattern
        mock_knowledge_base.store_learned_pattern.assert_called()
    
    async def test_merge_conflicting_preferences(self, feedback_processor, mock_knowledge_base):
        """Test merging conflicting preferences"""
        # Mock existing similar preferences
        mock_knowledge_base.find_similar_patterns.return_value = [
            {
                'distance': 0.2,
                'data': {
                    'context': {'task_type': 'analysis'},
                    'preference': 'brief_summaries',
                    'strength': 0.6,
                    'examples': [],
                    'conditions': {}
                }
            }
        ]
        
        feedback = {
            'type': 'preference',
            'key': 'communication_style',
            'preference': 'detailed_explanations',
            'context': {'task_type': 'analysis'},
            'strength': 0.8
        }
        
        result = await feedback_processor.process_feedback(feedback)
        
        assert result['success'] is True
        assert result['conflicts_resolved'] is True
        
        # Should have merged preferences
        mock_knowledge_base.store_user_preference.assert_called_once()
    
    async def test_calculate_impact(self, feedback_processor):
        """Test impact calculation"""
        # High severity, recurring, system-wide
        feedback = {
            'severity': 'high',
            'frequency': 'recurring',
            'scope': 'system_wide'
        }
        impact = feedback_processor._calculate_impact(feedback)
        assert impact > 0.8
        
        # Low severity, single occurrence, single task
        feedback = {
            'severity': 'low',
            'frequency': 'once',
            'scope': 'single_task'
        }
        impact = feedback_processor._calculate_impact(feedback)
        assert impact < 0.4
    
    async def test_context_similarity(self, feedback_processor):
        """Test context similarity calculation"""
        ctx1 = {'task_type': 'analysis', 'domain': 'data', 'complexity': 'high'}
        ctx2 = {'task_type': 'analysis', 'domain': 'data', 'urgency': 'low'}
        
        similarity = feedback_processor._context_similarity(ctx1, ctx2)
        
        # Should have some similarity (common keys)
        assert 0.0 < similarity < 1.0
        
        # Test identical contexts
        similarity = feedback_processor._context_similarity(ctx1, ctx1)
        assert similarity == 1.0
        
        # Test empty contexts
        similarity = feedback_processor._context_similarity({}, {})
        assert similarity == 0.0
    
    async def test_extract_guidance_patterns(self, feedback_processor):
        """Test extraction of patterns from guidance"""
        guidance = {
            'instruction': 'Always validate inputs',
            'examples': [
                {'input': {'data': 'raw'}, 'output': {'data': 'validated'}},
                {'input': {'file': 'test.txt'}, 'output': {'file': 'validated.txt'}}
            ],
            'constraints': ['safety_first'],
            'priority': 'high'
        }
        
        patterns = feedback_processor._extract_guidance_patterns(guidance)
        
        assert len(patterns) >= 2  # One for instruction, one+ for examples
        assert any(p['type'] == 'guided_instruction' for p in patterns)
        assert any(p['type'] == 'guided_example' for p in patterns)
    
    async def test_feedback_summary(self, feedback_processor, mock_knowledge_base):
        """Test getting feedback summary"""
        # Add some feedback
        await feedback_processor.process_feedback({
            'type': 'correction',
            'original_action': 'test',
            'correct_action': 'better_test'
        })
        
        await feedback_processor.process_feedback({
            'type': 'preference',
            'key': 'style',
            'preference': 'detailed'
        })
        
        summary = await feedback_processor.get_feedback_summary()
        
        assert summary['total_feedback'] == 2
        assert 'correction' in summary['feedback_by_type']
        assert 'preference' in summary['feedback_by_type']
        assert summary['feedback_by_type']['correction'] == 1
        assert summary['feedback_by_type']['preference'] == 1
    
    async def test_invalid_feedback_type(self, feedback_processor):
        """Test handling of invalid feedback type"""
        feedback = {
            'type': 'invalid_type',
            'content': 'test'
        }
        
        result = await feedback_processor.process_feedback(feedback)
        
        assert result['success'] is False
        assert 'error' in result
    
    async def test_error_handling(self, feedback_processor, mock_knowledge_base):
        """Test error handling in feedback processing"""
        # Make knowledge base throw an error
        mock_knowledge_base.store_failure_pattern.side_effect = Exception("Storage error")
        
        feedback = {
            'type': 'correction',
            'original_action': 'test',
            'correct_action': 'better_test'
        }
        
        result = await feedback_processor.process_feedback(feedback)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Storage error' in result['error']


@pytest.mark.asyncio
class TestFeedbackTypes:
    """Test feedback type enumeration"""
    
    def test_feedback_types(self):
        """Test all feedback types are defined"""
        expected_types = [
            'correction', 'preference', 'guidance', 
            'rating', 'suggestion', 'warning'
        ]
        
        for type_name in expected_types:
            assert hasattr(FeedbackType, type_name.upper())
            assert FeedbackType(type_name).value == type_name
    
    def test_feedback_severity(self):
        """Test feedback severity levels"""
        expected_severities = ['low', 'medium', 'high', 'critical']
        
        for severity in expected_severities:
            assert hasattr(FeedbackSeverity, severity.upper())
            assert FeedbackSeverity(severity).value == severity


@pytest.mark.asyncio 
class TestFeedbackIntegration:
    """Integration tests for feedback processing"""
    
    async def test_end_to_end_correction(self, feedback_processor, mock_knowledge_base):
        """Test end-to-end correction processing"""
        feedback = {
            'type': 'correction',
            'original_action': 'inefficient_sort',
            'correct_action': 'use_built_in_sort',
            'explanation': 'Built-in sort is optimized',
            'severity': 'medium',
            'task_description': 'Sort data efficiently',
            'context': {'data_size': 'large', 'performance_critical': True}
        }
        
        result = await feedback_processor.process_feedback(feedback)
        
        # Verify all aspects were processed
        assert result['success'] is True
        assert result['knowledge_updated'] is True
        assert result['impact'] > 0.3  # Should have some impact
        
        # Verify storage calls
        mock_knowledge_base.store_failure_pattern.assert_called_once()
        
        # Verify feedback was added to history
        assert len(feedback_processor.feedback_history) == 1
        stored_feedback = feedback_processor.feedback_history[0]
        assert stored_feedback['type'] == 'correction'
        assert 'timestamp' in stored_feedback