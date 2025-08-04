"""
Unit tests for AdaptiveBehaviorSystem - Phase 8

Tests the adaptive behavior system including:
- Behavioral adaptations
- Context analysis  
- Performance optimization
- Preference application
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from collections import defaultdict

from src.learning.adaptive_system import (
    AdaptiveBehaviorSystem, 
    AdaptationType, 
    Adaptation,
    AdaptationType
)
from src.memory.persistent_knowledge import PersistentKnowledgeBase
from src.memory.vector_store import VectorMemoryStore


@pytest.fixture
def mock_knowledge_base():
    """Create a mock knowledge base for testing"""
    kb = AsyncMock(spec=PersistentKnowledgeBase)
    kb.find_similar_patterns = AsyncMock(return_value=[])
    kb.get_knowledge_statistics = AsyncMock(return_value={
        'user_preference': {'count': 5},
        'learned_pattern': {'count': 10},
        'failure_pattern': {'count': 2}
    })
    return kb


@pytest.fixture
def mock_vector_store():
    """Create a mock vector store for testing"""
    vs = AsyncMock(spec=VectorMemoryStore)
    vs.search = AsyncMock(return_value=[])
    vs.store = AsyncMock()
    return vs


@pytest.fixture
def adaptive_system(mock_knowledge_base, mock_vector_store):
    """Create an adaptive system instance for testing"""
    return AdaptiveBehaviorSystem(mock_knowledge_base, mock_vector_store)


@pytest.fixture
def sample_context():
    """Create a sample context for testing"""
    return {
        'task_type': 'analysis',
        'workflow_type': 'SEQUENTIAL',
        'complexity': 0.6,
        'urgency': 'normal',
        'resource_limited': False,
        'time_sensitive': False
    }


@pytest.mark.asyncio
class TestAdaptiveBehaviorSystem:
    """Test cases for AdaptiveBehaviorSystem"""
    
    async def test_initialization(self, mock_knowledge_base, mock_vector_store):
        """Test adaptive system initialization"""
        system = AdaptiveBehaviorSystem(mock_knowledge_base, mock_vector_store)
        
        assert system.knowledge_base == mock_knowledge_base
        assert system.vector_store == mock_vector_store
        assert system.adaptation_threshold == 0.6
        assert system.max_adaptations == 5
        assert system.adaptation_cache == {}
        assert len(system.enabled_types) == len(AdaptationType)
    
    async def test_get_adaptations_empty(self, adaptive_system, sample_context):
        """Test getting adaptations when none are available"""
        result = await adaptive_system.get_adaptations(sample_context)
        
        assert 'adaptations' in result
        assert 'preferences' in result
        assert 'warnings' in result
        assert 'optimizations' in result
        assert 'metadata' in result
        
        assert result['metadata']['context_analyzed'] is True
        assert 'total_found' in result['metadata']
    
    async def test_preference_based_adaptations(self, adaptive_system, mock_knowledge_base, sample_context):
        """Test preference-based adaptations"""
        # Mock preference patterns
        mock_preferences = [
            {
                'distance': 0.3,
                'id': 'pref_1',
                'data': {
                    'preference': 'detailed_logging',
                    'strength': 0.8,
                    'conditions': {
                        'constraints': ['debug_mode']
                    }
                }
            }
        ]
        
        mock_knowledge_base.find_similar_patterns.return_value = mock_preferences
        
        # Enable only preference adaptations for this test
        adaptive_system.enabled_types = {AdaptationType.PREFERENCE_BASED}
        
        result = await adaptive_system.get_adaptations(sample_context)
        
        assert len(result['preferences']) >= 1
        pref = result['preferences'][0]
        assert pref['type'] == 'preference_based'
        assert pref['confidence'] > 0.5  # 1.0 - 0.3 distance
    
    async def test_performance_based_adaptations(self, adaptive_system, mock_knowledge_base, sample_context):
        """Test performance-based adaptations"""
        # Mock high-performing patterns
        mock_patterns = [
            {
                'distance': 0.2,
                'id': 'pattern_1',
                'data': {
                    'performance_metrics': {
                        'success_rate': 0.9,
                        'duration': 30.0,
                        'resource_efficiency': 0.8
                    },
                    'key_features': {
                        'parallel_execution': True
                    }
                }
            }
        ]
        
        mock_knowledge_base.find_similar_patterns.return_value = mock_patterns
        
        # Enable only performance adaptations
        adaptive_system.enabled_types = {AdaptationType.PERFORMANCE_BASED}
        
        result = await adaptive_system.get_adaptations(sample_context)
        
        assert len(result['adaptations']) >= 1
        adaptation = result['adaptations'][0]
        assert adaptation['type'] == 'performance_based'
        assert adaptation['confidence'] == 0.9  # From success rate
    
    async def test_context_based_adaptations_complexity(self, adaptive_system, sample_context):
        """Test context-based adaptations for high complexity"""
        sample_context['complexity'] = 0.8  # High complexity
        
        # Enable only context adaptations
        adaptive_system.enabled_types = {AdaptationType.CONTEXT_BASED}
        
        result = await adaptive_system.get_adaptations(sample_context)
        
        # Should suggest complex task handling
        assert len(result['adaptations']) >= 1
        
        # Look for complexity-related adaptation
        complex_adaptation = next(
            (a for a in result['adaptations'] if 'complex' in a['name']), 
            None
        )
        assert complex_adaptation is not None
        assert complex_adaptation['impact'] == 'high'
    
    async def test_context_based_adaptations_resources(self, adaptive_system, sample_context):
        """Test context-based adaptations for resource constraints"""
        sample_context['resource_constrained'] = True
        
        # Enable only context adaptations
        adaptive_system.enabled_types = {AdaptationType.CONTEXT_BASED}
        
        result = await adaptive_system.get_adaptations(sample_context)
        
        # Should suggest resource conservation
        resource_adaptation = next(
            (a for a in result['adaptations'] if 'resource' in a['name']),
            None
        )
        assert resource_adaptation is not None
        assert resource_adaptation['impact'] == 'high'
        assert 'resource_limited' in resource_adaptation['constraints']
    
    async def test_learning_based_adaptations(self, adaptive_system, mock_vector_store, sample_context):
        """Test learning-based adaptations"""
        # Mock vector search results
        mock_learnings = [
            {
                'id': 'learning_1',
                'score': 0.8,
                'metadata': {
                    'type': 'learning',
                    'description': 'Optimize batch size',
                    'impact': 'medium',
                    'parameters': {'modify_batch_size': 50},
                    'constraints': []
                }
            }
        ]
        
        mock_vector_store.search.return_value = mock_learnings
        
        # Enable only learning adaptations
        adaptive_system.enabled_types = {AdaptationType.LEARNING_BASED}
        
        result = await adaptive_system.get_adaptations(sample_context)
        
        assert len(result['adaptations']) >= 1
        learning_adaptation = result['adaptations'][0]
        assert learning_adaptation['type'] == 'learning_based'
        assert learning_adaptation['confidence'] == 0.8
    
    async def test_failure_avoidance_adaptations(self, adaptive_system, mock_knowledge_base, sample_context):
        """Test failure avoidance adaptations"""
        # Mock failure patterns
        mock_failures = [
            {
                'distance': 0.4,
                'id': 'failure_1',
                'data': {
                    'failure_reason': 'Timeout due to inefficient processing',
                    'context': {'processing_type': 'batch'},
                    'recovery_strategy': 'Use streaming processing'
                }
            }
        ]
        
        mock_knowledge_base.find_similar_patterns.return_value = mock_failures
        
        # Enable only failure avoidance
        adaptive_system.enabled_types = {AdaptationType.FAILURE_AVOIDANCE}
        
        result = await adaptive_system.get_adaptations(sample_context)
        
        assert len(result['warnings']) >= 1
        warning = result['warnings'][0]
        assert warning['type'] == 'failure_avoidance'
        assert warning['impact'] == 'high'
        assert 'safety_critical' in warning['constraints']
    
    async def test_resource_optimization_adaptations(self, adaptive_system, sample_context):
        """Test resource optimization adaptations"""
        # Mock high resource usage
        with patch.object(adaptive_system, '_get_resource_state') as mock_resources:
            mock_resources.return_value = {
                'cpu_usage': 0.9,  # High CPU usage
                'memory_usage': 0.85,  # High memory usage
                'available_cores': 4,
                'total_memory_gb': 16
            }
            
            # Enable only resource optimization
            adaptive_system.enabled_types = {AdaptationType.RESOURCE_OPTIMIZATION}
            
            result = await adaptive_system.get_adaptations(sample_context)
            
            assert len(result['optimizations']) >= 2  # CPU and memory optimizations
            
            # Check for CPU optimization
            cpu_opt = next(
                (a for a in result['optimizations'] if 'cpu' in a['name']),
                None
            )
            assert cpu_opt is not None
            assert cpu_opt['impact'] == 'high'
            
            # Check for memory optimization  
            mem_opt = next(
                (a for a in result['optimizations'] if 'memory' in a['name']),
                None
            )
            assert mem_opt is not None
            assert mem_opt['impact'] == 'high'
    
    async def test_adaptation_caching(self, adaptive_system, sample_context):
        """Test adaptation result caching"""
        # First call
        result1 = await adaptive_system.get_adaptations(sample_context)
        
        # Second call with same context
        result2 = await adaptive_system.get_adaptations(sample_context)
        
        # Second result should be from cache
        assert result2['metadata'].get('from_cache') is True
        
        # Results should be the same
        assert result1['adaptations'] == result2['adaptations']
    
    async def test_apply_adaptations(self, adaptive_system, sample_context):
        """Test applying adaptations to context"""
        adaptations = [
            {
                'name': 'test_adaptation',
                'type': 'preference_based',
                'description': 'Test adaptation',
                'confidence': 0.8,
                'impact': 'medium',
                'parameters': {
                    'add_verbose': True,
                    'modify_timeout': 60,
                    'remove_debug': None
                },
                'source': 'test',
                'constraints': []
            }
        ]
        
        adapted_context = await adaptive_system.apply_adaptations(sample_context, adaptations)
        
        # Check modifications were applied
        assert adapted_context['verbose'] is True
        assert adapted_context['timeout'] == 60
        assert 'debug' not in adapted_context
        
        # Check adaptation metadata was added
        assert '_adaptations_applied' in adapted_context
        applied = adapted_context['_adaptations_applied']
        assert len(applied) == 1
        assert applied[0]['name'] == 'test_adaptation'
    
    async def test_adaptation_filtering(self, adaptive_system, sample_context):
        """Test adaptation filtering based on constraints and confidence"""
        # Create adaptations with different confidence levels
        low_confidence = Adaptation(
            type=AdaptationType.PREFERENCE_BASED,
            name='low_conf',
            description='Low confidence adaptation',
            confidence=0.3,  # Below threshold
            impact='medium',
            parameters={'test': True},
            source='test',
            constraints=[]
        )
        
        high_confidence = Adaptation(
            type=AdaptationType.PREFERENCE_BASED,
            name='high_conf',
            description='High confidence adaptation', 
            confidence=0.8,  # Above threshold
            impact='medium',
            parameters={'test': True},
            source='test',
            constraints=[]
        )
        
        constrained = Adaptation(
            type=AdaptationType.CONTEXT_BASED,
            name='constrained',
            description='Constrained adaptation',
            confidence=0.9,
            impact='high',
            parameters={'test': True},
            source='test',
            constraints=['time_sensitive']  # Context doesn't meet this
        )
        
        adaptations = [low_confidence, high_confidence, constrained]
        filtered = adaptive_system._filter_adaptations(adaptations, sample_context)
        
        # Only high confidence should pass
        assert len(filtered) == 1
        assert filtered[0].name == 'high_conf'
    
    async def test_adaptation_ranking(self, adaptive_system):
        """Test adaptation ranking by priority"""
        adaptations = [
            Adaptation(
                type=AdaptationType.CONTEXT_BASED,
                name='medium_impact',
                description='Medium impact',
                confidence=0.7,
                impact='medium',
                parameters={},
                source='test',
                constraints=[]
            ),
            Adaptation(
                type=AdaptationType.FAILURE_AVOIDANCE,
                name='high_impact_failure',
                description='High impact failure avoidance',
                confidence=0.8,
                impact='high',
                parameters={},
                source='test',
                constraints=[]
            ),
            Adaptation(
                type=AdaptationType.PREFERENCE_BASED,
                name='high_impact_pref',
                description='High impact preference',
                confidence=0.9,
                impact='high',
                parameters={},
                source='test',
                constraints=[]
            )
        ]
        
        ranked = adaptive_system._rank_adaptations(adaptations)
        
        # Should be ranked by: impact (high first), confidence (high first), type priority
        assert ranked[0].name == 'high_impact_failure'  # Failure avoidance has highest type priority
        assert ranked[1].name == 'high_impact_pref'     # Preference has next priority
        assert ranked[2].name == 'medium_impact'        # Medium impact comes last
    
    async def test_record_adaptation_outcome_success(self, adaptive_system, mock_vector_store):
        """Test recording successful adaptation outcome"""
        await adaptive_system.record_adaptation_outcome('test_adaptation', True, 0.9)
        
        # Should update performance history
        assert 'test_adaptation' in adaptive_system.performance_history
        assert adaptive_system.performance_history['test_adaptation'] == [0.9]
        
        # Should store feedback in vector store
        mock_vector_store.store.assert_called_once()
    
    async def test_record_adaptation_outcome_failure(self, adaptive_system):
        """Test recording failed adaptation outcome"""
        # Add to cache first
        cache_key = 'test_key'
        adaptation = Adaptation(
            type=AdaptationType.PREFERENCE_BASED,
            name='failing_adaptation',
            description='Test',
            confidence=0.8,
            impact='medium',
            parameters={},
            source='test',
            constraints=[]
        )
        adaptive_system.adaptation_cache[cache_key] = [adaptation]
        
        await adaptive_system.record_adaptation_outcome('failing_adaptation', False, 0.3)
        
        # Should clear from cache due to poor performance
        assert cache_key not in adaptive_system.adaptation_cache
    
    async def test_enable_disable_adaptation_types(self, adaptive_system):
        """Test enabling and disabling adaptation types"""
        # Disable preference-based adaptations
        adaptive_system.disable_adaptation_type(AdaptationType.PREFERENCE_BASED)
        assert AdaptationType.PREFERENCE_BASED not in adaptive_system.enabled_types
        
        # Re-enable preference-based adaptations
        adaptive_system.enable_adaptation_type(AdaptationType.PREFERENCE_BASED)
        assert AdaptationType.PREFERENCE_BASED in adaptive_system.enabled_types
    
    async def test_adaptation_statistics(self, adaptive_system, mock_knowledge_base):
        """Test getting adaptation statistics"""
        # Add some performance history
        adaptive_system.performance_history['test_adaptation'] = [0.8, 0.9, 0.7, 0.85]
        
        stats = await adaptive_system.get_adaptation_statistics()
        
        assert 'enabled_types' in stats
        assert 'cache_size' in stats
        assert 'performance_tracking' in stats
        assert 'knowledge_base' in stats
        
        # Check performance tracking
        assert 'test_adaptation' in stats['performance_tracking']
        adaptation_stats = stats['performance_tracking']['test_adaptation']
        assert adaptation_stats['usage_count'] == 4
        assert 0.7 <= adaptation_stats['average_score'] <= 0.9
        assert adaptation_stats['trend'] in ['improving', 'declining', 'stable']
    
    async def test_context_characteristics_analysis(self, adaptive_system):
        """Test context characteristics analysis"""
        context = {
            'complexity': 0.8,
            'resource_limited': True,
            'urgency': 'high'
        }
        
        characteristics = adaptive_system._analyze_context_characteristics(context)
        
        assert characteristics['high_complexity'] is True
        assert characteristics['resource_constrained'] is True
        assert characteristics['urgent'] is True
        assert 'suggested_agents' in characteristics  # Should suggest more agents for complex tasks


@pytest.mark.asyncio 
class TestAdaptation:
    """Test the Adaptation dataclass"""
    
    def test_adaptation_creation(self):
        """Test creating an Adaptation"""
        adaptation = Adaptation(
            type=AdaptationType.PREFERENCE_BASED,
            name='test_adaptation',
            description='Test adaptation',
            confidence=0.8,
            impact='medium',
            parameters={'test_param': 'value'},
            source='test_source',
            constraints=['test_constraint']
        )
        
        assert adaptation.type == AdaptationType.PREFERENCE_BASED
        assert adaptation.name == 'test_adaptation'
        assert adaptation.confidence == 0.8
        assert adaptation.impact == 'medium'
        assert adaptation.parameters == {'test_param': 'value'}
    
    def test_apply_to_context(self):
        """Test applying adaptation to context"""
        adaptation = Adaptation(
            type=AdaptationType.PREFERENCE_BASED,
            name='test_adaptation',
            description='Test adaptation',
            confidence=0.8,
            impact='medium',
            parameters={
                'add_verbose': True,
                'modify_timeout': 60,
                'remove_debug': None,
                'direct_assignment': 'value'
            },
            source='test',
            constraints=[]
        )
        
        original_context = {
            'existing_param': 'original',
            'timeout': 30,
            'debug': True
        }
        
        adapted_context = adaptation.apply_to_context(original_context)
        
        # Check additions
        assert adapted_context['verbose'] is True
        
        # Check modifications
        assert adapted_context['timeout'] == 60
        
        # Check removals
        assert 'debug' not in adapted_context
        
        # Check direct assignments
        assert adapted_context['direct_assignment'] == 'value'
        
        # Check original param preserved
        assert adapted_context['existing_param'] == 'original'
        
        # Check adaptation metadata
        assert '_adaptations_applied' in adapted_context
        applied = adapted_context['_adaptations_applied']
        assert len(applied) == 1
        assert applied[0]['name'] == 'test_adaptation'


@pytest.mark.asyncio
class TestAdaptationTypes:
    """Test adaptation type enumeration"""
    
    def test_adaptation_types(self):
        """Test all adaptation types are defined"""
        expected_types = [
            'preference_based', 'performance_based', 'context_based',
            'learning_based', 'failure_avoidance', 'resource_optimization'
        ]
        
        for type_name in expected_types:
            assert hasattr(AdaptationType, type_name.upper())
            assert AdaptationType(type_name).value == type_name