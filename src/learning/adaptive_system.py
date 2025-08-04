"""
Adaptive Behavior System - Phase 8 Implementation

Provides dynamic behavior adaptation based on learned patterns, user preferences,
and contextual information. Enables agents to improve their performance over time.
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
import json
from enum import Enum

from ..memory.persistent_knowledge import PersistentKnowledgeBase
from ..memory.vector_store import VectorMemoryStore
from ..core.models import TaskType, WorkflowPattern

logger = logging.getLogger(__name__)


class AdaptationType(Enum):
    """Types of behavioral adaptations"""
    PREFERENCE_BASED = "preference_based"
    PERFORMANCE_BASED = "performance_based"
    CONTEXT_BASED = "context_based"
    LEARNING_BASED = "learning_based"
    FAILURE_AVOIDANCE = "failure_avoidance"
    RESOURCE_OPTIMIZATION = "resource_optimization"


@dataclass
class Adaptation:
    """Represents a behavioral adaptation"""
    type: AdaptationType
    name: str
    description: str
    confidence: float
    impact: str  # 'low', 'medium', 'high'
    parameters: Dict[str, Any]
    source: str  # Where this adaptation came from
    constraints: List[str]
    
    def apply_to_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply this adaptation to a context"""
        adapted_context = context.copy()
        
        # Apply parameters
        for key, value in self.parameters.items():
            if key.startswith('add_'):
                # Add new context
                adapted_context[key[4:]] = value
            elif key.startswith('modify_'):
                # Modify existing context
                target_key = key[7:]
                if target_key in adapted_context:
                    adapted_context[target_key] = value
            elif key.startswith('remove_'):
                # Remove from context
                target_key = key[7:]
                adapted_context.pop(target_key, None)
            else:
                # Direct assignment
                adapted_context[key] = value
        
        # Add adaptation metadata
        adapted_context['_adaptations_applied'] = adapted_context.get('_adaptations_applied', [])
        adapted_context['_adaptations_applied'].append({
            'name': self.name,
            'type': self.type.value,
            'confidence': self.confidence
        })
        
        return adapted_context


class AdaptiveBehaviorSystem:
    """System for dynamic behavioral adaptation based on learning and context"""
    
    def __init__(self, knowledge_base: PersistentKnowledgeBase, 
                 vector_store: Optional[VectorMemoryStore] = None):
        """Initialize the adaptive behavior system
        
        Args:
            knowledge_base: Persistent storage for patterns and preferences
            vector_store: Optional vector store for semantic matching
        """
        self.knowledge_base = knowledge_base
        self.vector_store = vector_store
        self.adaptation_threshold = 0.6
        self.max_adaptations = 5
        self.adaptation_cache: Dict[str, List[Adaptation]] = {}
        self.performance_history: Dict[str, List[float]] = defaultdict(list)
        self.enabled_types = set(AdaptationType)  # All types enabled by default
        
    async def get_adaptations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get behavioral adaptations based on context
        
        Args:
            context: Current execution context
            
        Returns:
            Dict containing adaptations and their metadata
        """
        adaptations = {
            'adaptations': [],
            'preferences': [],
            'warnings': [],
            'optimizations': [],
            'metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'context_analyzed': True
            }
        }
        
        # Check cache first
        cache_key = self._generate_cache_key(context)
        if cache_key in self.adaptation_cache:
            cached = self.adaptation_cache[cache_key]
            adaptations['adaptations'] = [self._adaptation_to_dict(a) for a in cached]
            adaptations['metadata']['from_cache'] = True
            return adaptations
        
        # Collect adaptations from different sources
        all_adaptations: List[Adaptation] = []
        
        # 1. User preference based adaptations
        if AdaptationType.PREFERENCE_BASED in self.enabled_types:
            pref_adaptations = await self._get_preference_adaptations(context)
            all_adaptations.extend(pref_adaptations)
            adaptations['preferences'] = [self._adaptation_to_dict(a) for a in pref_adaptations]
        
        # 2. Performance based adaptations  
        if AdaptationType.PERFORMANCE_BASED in self.enabled_types:
            perf_adaptations = await self._get_performance_adaptations(context)
            all_adaptations.extend(perf_adaptations)
        
        # 3. Context based adaptations
        if AdaptationType.CONTEXT_BASED in self.enabled_types:
            ctx_adaptations = await self._get_context_adaptations(context)
            all_adaptations.extend(ctx_adaptations)
        
        # 4. Learning based adaptations
        if AdaptationType.LEARNING_BASED in self.enabled_types:
            learn_adaptations = await self._get_learning_adaptations(context)
            all_adaptations.extend(learn_adaptations)
        
        # 5. Failure avoidance adaptations
        if AdaptationType.FAILURE_AVOIDANCE in self.enabled_types:
            avoid_adaptations = await self._get_avoidance_adaptations(context)
            all_adaptations.extend(avoid_adaptations)
            adaptations['warnings'] = [self._adaptation_to_dict(a) for a in avoid_adaptations]
        
        # 6. Resource optimization adaptations
        if AdaptationType.RESOURCE_OPTIMIZATION in self.enabled_types:
            opt_adaptations = await self._get_optimization_adaptations(context)
            all_adaptations.extend(opt_adaptations)
            adaptations['optimizations'] = [self._adaptation_to_dict(a) for a in opt_adaptations]
        
        # Filter and rank adaptations
        filtered_adaptations = self._filter_adaptations(all_adaptations, context)
        ranked_adaptations = self._rank_adaptations(filtered_adaptations)
        
        # Select top adaptations
        selected = ranked_adaptations[:self.max_adaptations]
        
        # Cache the results
        self.adaptation_cache[cache_key] = selected
        
        # Prepare response
        adaptations['adaptations'] = [self._adaptation_to_dict(a) for a in selected]
        adaptations['metadata']['total_found'] = len(all_adaptations)
        adaptations['metadata']['filtered'] = len(filtered_adaptations)
        adaptations['metadata']['selected'] = len(selected)
        
        return adaptations
    
    async def _get_preference_adaptations(self, context: Dict[str, Any]) -> List[Adaptation]:
        """Get adaptations based on user preferences"""
        adaptations = []
        
        # Find relevant preferences
        preferences = await self.knowledge_base.find_similar_patterns(
            query=str(context),
            knowledge_type='user_preference',
            limit=10
        )
        
        for pref in preferences:
            if pref['distance'] < self.adaptation_threshold:
                pref_data = pref.get('data', {})
                
                adaptation = Adaptation(
                    type=AdaptationType.PREFERENCE_BASED,
                    name=f"user_preference_{pref.get('id', 'unknown')}",
                    description=f"Apply user preference: {pref_data.get('preference', 'unknown')}",
                    confidence=1.0 - pref['distance'],
                    impact=self._determine_impact(pref_data.get('strength', 0.5)),
                    parameters=self._extract_preference_parameters(pref_data),
                    source='user_preferences',
                    constraints=pref_data.get('conditions', {}).get('constraints', [])
                )
                
                adaptations.append(adaptation)
        
        return adaptations
    
    async def _get_performance_adaptations(self, context: Dict[str, Any]) -> List[Adaptation]:
        """Get adaptations based on performance patterns"""
        adaptations = []
        
        # Find high-performing patterns similar to current context
        patterns = await self.knowledge_base.find_similar_patterns(
            query=str(context),
            knowledge_type='learned_pattern',
            limit=10
        )
        
        for pattern in patterns:
            pattern_data = pattern.get('data', {})
            perf_metrics = pattern_data.get('performance_metrics', {})
            
            # Only use high-performing patterns
            if perf_metrics.get('success_rate', 0) > 0.8:
                adaptation = Adaptation(
                    type=AdaptationType.PERFORMANCE_BASED,
                    name=f"high_performance_pattern_{pattern.get('id', 'unknown')}",
                    description="Apply successful pattern from previous executions",
                    confidence=perf_metrics.get('success_rate', 0.8),
                    impact='high',
                    parameters=self._extract_pattern_parameters(pattern_data),
                    source='learned_patterns',
                    constraints=[]
                )
                
                adaptations.append(adaptation)
        
        return adaptations
    
    async def _get_context_adaptations(self, context: Dict[str, Any]) -> List[Adaptation]:
        """Get adaptations based on contextual analysis"""
        adaptations = []
        
        # Analyze context characteristics
        characteristics = self._analyze_context_characteristics(context)
        
        # Time-based adaptations
        if characteristics.get('is_peak_hours'):
            adaptations.append(Adaptation(
                type=AdaptationType.CONTEXT_BASED,
                name='peak_hours_optimization',
                description='Optimize for peak hours operation',
                confidence=0.8,
                impact='medium',
                parameters={
                    'add_priority': 'high',
                    'modify_timeout': 60,  # Shorter timeout
                    'add_resource_efficient': True
                },
                source='context_analysis',
                constraints=['time_sensitive']
            ))
        
        # Complexity-based adaptations
        if characteristics.get('high_complexity'):
            adaptations.append(Adaptation(
                type=AdaptationType.CONTEXT_BASED,
                name='complex_task_handling',
                description='Adapt for complex task execution',
                confidence=0.7,
                impact='high',
                parameters={
                    'add_detailed_logging': True,
                    'modify_agent_count': characteristics.get('suggested_agents', 3),
                    'add_checkpoint_frequency': 5  # More frequent checkpoints
                },
                source='complexity_analysis',
                constraints=[]
            ))
        
        # Resource-based adaptations
        if characteristics.get('resource_constrained'):
            adaptations.append(Adaptation(
                type=AdaptationType.CONTEXT_BASED,
                name='resource_conservation',
                description='Conserve system resources',
                confidence=0.9,
                impact='high',
                parameters={
                    'add_batch_processing': True,
                    'modify_parallel_limit': 2,
                    'add_memory_efficient': True
                },
                source='resource_monitoring',
                constraints=['resource_limited']
            ))
        
        return adaptations
    
    async def _get_learning_adaptations(self, context: Dict[str, Any]) -> List[Adaptation]:
        """Get adaptations based on continuous learning"""
        adaptations = []
        
        # Check for recent learnings relevant to context
        if self.vector_store:
            # Use semantic search for relevant learnings
            similar_contexts = await self.vector_store.search(
                query=str(context),
                limit=5,
                metadata_filter={'type': 'learning'}
            )
            
            for learning in similar_contexts:
                if learning['score'] > self.adaptation_threshold:
                    learning_data = learning.get('metadata', {})
                    
                    adaptation = Adaptation(
                        type=AdaptationType.LEARNING_BASED,
                        name=f"learned_optimization_{learning.get('id', 'unknown')}",
                        description=learning_data.get('description', 'Apply learned optimization'),
                        confidence=learning['score'],
                        impact=learning_data.get('impact', 'medium'),
                        parameters=learning_data.get('parameters', {}),
                        source='continuous_learning',
                        constraints=learning_data.get('constraints', [])
                    )
                    
                    adaptations.append(adaptation)
        
        # Check performance trends
        task_type = context.get('task_type')
        if task_type and task_type in self.performance_history:
            recent_performance = self.performance_history[task_type][-10:]
            if len(recent_performance) >= 5:
                trend = self._calculate_trend(recent_performance)
                
                if trend == 'improving':
                    adaptations.append(Adaptation(
                        type=AdaptationType.LEARNING_BASED,
                        name='continue_improvement_trend',
                        description='Continue with recent successful approaches',
                        confidence=0.7,
                        impact='medium',
                        parameters={'add_continue_current_approach': True},
                        source='performance_trending',
                        constraints=[]
                    ))
                elif trend == 'declining':
                    adaptations.append(Adaptation(
                        type=AdaptationType.LEARNING_BASED,
                        name='reverse_declining_trend',
                        description='Adjust approach to reverse declining performance',
                        confidence=0.8,
                        impact='high',
                        parameters={
                            'add_try_alternative_approach': True,
                            'modify_risk_tolerance': 0.3  # Lower risk tolerance
                        },
                        source='performance_trending',
                        constraints=[]
                    ))
        
        return adaptations
    
    async def _get_avoidance_adaptations(self, context: Dict[str, Any]) -> List[Adaptation]:
        """Get adaptations to avoid known failures"""
        adaptations = []
        
        # Check for similar failure patterns
        failures = await self.knowledge_base.find_similar_patterns(
            query=str(context),
            knowledge_type='failure_pattern',
            limit=10
        )
        
        for failure in failures:
            if failure['distance'] < self.adaptation_threshold:
                failure_data = failure.get('data', {})
                
                adaptation = Adaptation(
                    type=AdaptationType.FAILURE_AVOIDANCE,
                    name=f"avoid_failure_{failure.get('id', 'unknown')}",
                    description=f"Avoid known failure: {failure_data.get('failure_reason', 'unknown')}",
                    confidence=1.0 - failure['distance'],
                    impact='high',
                    parameters=self._create_avoidance_parameters(failure_data),
                    source='failure_patterns',
                    constraints=['safety_critical']
                )
                
                adaptations.append(adaptation)
        
        return adaptations
    
    async def _get_optimization_adaptations(self, context: Dict[str, Any]) -> List[Adaptation]:
        """Get resource optimization adaptations"""
        adaptations = []
        
        # Check current resource usage
        resource_state = await self._get_resource_state()
        
        # CPU optimization
        if resource_state.get('cpu_usage', 0) > 0.8:
            adaptations.append(Adaptation(
                type=AdaptationType.RESOURCE_OPTIMIZATION,
                name='cpu_optimization',
                description='Reduce CPU usage through optimizations',
                confidence=0.9,
                impact='high',
                parameters={
                    'modify_parallel_limit': max(1, resource_state.get('available_cores', 4) // 2),
                    'add_cpu_throttling': True,
                    'modify_batch_size': 10  # Smaller batches
                },
                source='resource_monitoring',
                constraints=['cpu_constrained']
            ))
        
        # Memory optimization
        if resource_state.get('memory_usage', 0) > 0.8:
            adaptations.append(Adaptation(
                type=AdaptationType.RESOURCE_OPTIMIZATION,
                name='memory_optimization',
                description='Optimize memory usage',
                confidence=0.9,
                impact='high',
                parameters={
                    'add_streaming_mode': True,
                    'modify_cache_size': 100,  # Smaller cache
                    'add_aggressive_gc': True
                },
                source='memory_monitoring',
                constraints=['memory_constrained']
            ))
        
        # Time optimization based on patterns
        if context.get('time_sensitive'):
            time_patterns = await self._find_time_optimized_patterns(context)
            for pattern in time_patterns[:2]:  # Top 2 time-optimized patterns
                adaptations.append(Adaptation(
                    type=AdaptationType.RESOURCE_OPTIMIZATION,
                    name=f"time_optimization_{pattern.get('id', 'unknown')}",
                    description='Apply time-optimized execution pattern',
                    confidence=pattern.get('confidence', 0.7),
                    impact='high',
                    parameters=pattern.get('parameters', {}),
                    source='time_optimization_patterns',
                    constraints=['time_critical']
                ))
        
        return adaptations
    
    def _generate_cache_key(self, context: Dict[str, Any]) -> str:
        """Generate a cache key for the context"""
        # Use key aspects of context for caching
        key_parts = [
            context.get('task_type', 'unknown'),
            context.get('workflow_type', 'unknown'),
            str(context.get('complexity', 0)),
            str(context.get('urgency', 'normal'))
        ]
        return '_'.join(key_parts)
    
    def _adaptation_to_dict(self, adaptation: Adaptation) -> Dict[str, Any]:
        """Convert adaptation to dictionary format"""
        return {
            'name': adaptation.name,
            'type': adaptation.type.value,
            'description': adaptation.description,
            'confidence': adaptation.confidence,
            'impact': adaptation.impact,
            'parameters': adaptation.parameters,
            'source': adaptation.source,
            'constraints': adaptation.constraints
        }
    
    def _determine_impact(self, strength: float) -> str:
        """Determine impact level from strength value"""
        if strength >= 0.8:
            return 'high'
        elif strength >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _extract_preference_parameters(self, preference: Dict[str, Any]) -> Dict[str, Any]:
        """Extract actionable parameters from preference data"""
        parameters = {}
        
        # Extract direct preferences
        if 'preference' in preference:
            pref_value = preference['preference']
            if isinstance(pref_value, dict):
                for key, value in pref_value.items():
                    parameters[f'modify_{key}'] = value
            else:
                parameters['add_preference'] = pref_value
        
        # Extract from examples
        if 'examples' in preference:
            examples = preference['examples']
            if examples and isinstance(examples[0], dict):
                # Use first example as template
                for key, value in examples[0].items():
                    if key not in parameters:
                        parameters[f'add_{key}'] = value
        
        return parameters
    
    def _extract_pattern_parameters(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Extract actionable parameters from learned pattern"""
        parameters = {}
        
        # Resource patterns
        if 'resource_patterns' in pattern:
            resources = pattern['resource_patterns']
            if resources.get('parallel_steps', 0) > resources.get('sequential_steps', 0):
                parameters['add_prefer_parallel'] = True
            parameters['modify_optimal_agents'] = resources.get('total_agents', 2)
        
        # Timing patterns
        if 'timing_patterns' in pattern:
            timing = pattern['timing_patterns']
            if timing.get('parallel_efficiency', 0) > 0.8:
                parameters['add_maximize_parallelism'] = True
        
        # Success factors
        if 'success_factors' in pattern:
            for factor in pattern['success_factors']:
                if factor['factor'] == 'efficient_parallel_execution':
                    parameters['add_parallel_execution'] = True
                elif factor['factor'] == 'optimized_resource_usage':
                    parameters['add_optimize_resources'] = True
        
        return parameters
    
    def _analyze_context_characteristics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze context to determine its characteristics"""
        characteristics = {}
        
        # Time analysis
        current_hour = datetime.utcnow().hour
        characteristics['is_peak_hours'] = 9 <= current_hour <= 17
        characteristics['is_off_hours'] = current_hour < 6 or current_hour > 22
        
        # Complexity analysis
        complexity = context.get('complexity', 0)
        characteristics['high_complexity'] = complexity > 0.7
        characteristics['low_complexity'] = complexity < 0.3
        
        if characteristics['high_complexity']:
            # Suggest more agents for complex tasks
            characteristics['suggested_agents'] = min(5, int(complexity * 6) + 1)
        
        # Resource analysis (simplified - could be enhanced)
        characteristics['resource_constrained'] = context.get('resource_limited', False)
        
        # Urgency analysis
        characteristics['urgent'] = context.get('urgency', 'normal') in ['high', 'critical']
        
        return characteristics
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from a series of values"""
        if len(values) < 3:
            return 'insufficient_data'
        
        # Simple linear trend
        first_half_avg = sum(values[:len(values)//2]) / (len(values)//2)
        second_half_avg = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        difference = second_half_avg - first_half_avg
        
        if difference > 0.1:
            return 'improving'
        elif difference < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _create_avoidance_parameters(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create parameters to avoid a specific failure"""
        parameters = {}
        
        # Extract recovery strategy
        recovery = failure_data.get('recovery_strategy', '')
        if recovery:
            parameters['add_recovery_strategy'] = recovery
        
        # Add safety checks
        parameters['add_pre_validation'] = True
        parameters['modify_risk_tolerance'] = 0.2  # Very conservative
        
        # Avoid specific conditions that led to failure
        if 'context' in failure_data:
            failure_context = failure_data['context']
            for key, value in failure_context.items():
                if isinstance(value, (str, int, float, bool)):
                    parameters[f'avoid_{key}'] = value
        
        return parameters
    
    async def _get_resource_state(self) -> Dict[str, Any]:
        """Get current resource state (simplified)"""
        # In a real implementation, this would query actual system resources
        import random
        
        return {
            'cpu_usage': random.uniform(0.2, 0.9),
            'memory_usage': random.uniform(0.3, 0.85),
            'available_cores': 4,
            'total_memory_gb': 16
        }
    
    async def _find_time_optimized_patterns(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find patterns optimized for execution time"""
        patterns = await self.knowledge_base.find_similar_patterns(
            query=str(context),
            knowledge_type='learned_pattern',
            limit=20
        )
        
        # Filter and sort by execution time
        time_optimized = []
        for pattern in patterns:
            pattern_data = pattern.get('data', {})
            perf = pattern_data.get('performance_metrics', {})
            
            if perf.get('duration', float('inf')) < 60:  # Under 1 minute
                time_optimized.append({
                    'id': pattern.get('id'),
                    'duration': perf['duration'],
                    'confidence': pattern_data.get('confidence', 0.5),
                    'parameters': {
                        'add_fast_execution': True,
                        'modify_timeout': int(perf['duration'] * 1.5),
                        'add_skip_optional': True
                    }
                })
        
        # Sort by duration
        time_optimized.sort(key=lambda x: x['duration'])
        
        return time_optimized
    
    def _filter_adaptations(self, adaptations: List[Adaptation], 
                          context: Dict[str, Any]) -> List[Adaptation]:
        """Filter adaptations based on constraints and context"""
        filtered = []
        
        for adaptation in adaptations:
            # Check confidence threshold
            if adaptation.confidence < self.adaptation_threshold:
                continue
            
            # Check constraints
            if adaptation.constraints:
                constraint_met = True
                for constraint in adaptation.constraints:
                    if constraint == 'time_sensitive' and not context.get('time_sensitive'):
                        constraint_met = False
                        break
                    elif constraint == 'resource_limited' and not context.get('resource_limited'):
                        constraint_met = False
                        break
                
                if not constraint_met:
                    continue
            
            # Check for conflicts with existing adaptations
            conflicts = False
            for existing in filtered:
                if self._adaptations_conflict(adaptation, existing):
                    # Keep the one with higher confidence
                    if adaptation.confidence <= existing.confidence:
                        conflicts = True
                        break
                    else:
                        # Remove the existing one
                        filtered.remove(existing)
            
            if not conflicts:
                filtered.append(adaptation)
        
        return filtered
    
    def _adaptations_conflict(self, adapt1: Adaptation, adapt2: Adaptation) -> bool:
        """Check if two adaptations conflict"""
        # Check for parameter conflicts
        params1 = set(adapt1.parameters.keys())
        params2 = set(adapt2.parameters.keys())
        
        # Direct conflicts
        for param in params1.intersection(params2):
            if adapt1.parameters[param] != adapt2.parameters[param]:
                return True
        
        # Semantic conflicts
        if (adapt1.type == AdaptationType.RESOURCE_OPTIMIZATION and 
            adapt2.type == AdaptationType.PERFORMANCE_BASED):
            # Resource optimization might conflict with performance
            if ('add_batch_processing' in adapt1.parameters and 
                'add_real_time_processing' in adapt2.parameters):
                return True
        
        return False
    
    def _rank_adaptations(self, adaptations: List[Adaptation]) -> List[Adaptation]:
        """Rank adaptations by priority"""
        # Sort by: impact (high to low), confidence (high to low), type priority
        type_priority = {
            AdaptationType.FAILURE_AVOIDANCE: 1,
            AdaptationType.PREFERENCE_BASED: 2,
            AdaptationType.PERFORMANCE_BASED: 3,
            AdaptationType.LEARNING_BASED: 4,
            AdaptationType.RESOURCE_OPTIMIZATION: 5,
            AdaptationType.CONTEXT_BASED: 6
        }
        
        impact_scores = {'high': 3, 'medium': 2, 'low': 1}
        
        def adaptation_score(adapt: Adaptation) -> Tuple[int, float, int]:
            return (
                -impact_scores.get(adapt.impact, 2),  # Negative for descending sort
                -adapt.confidence,  # Negative for descending sort
                type_priority.get(adapt.type, 99)
            )
        
        return sorted(adaptations, key=adaptation_score)
    
    async def apply_adaptations(self, context: Dict[str, Any], 
                               adaptations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply selected adaptations to context
        
        Args:
            context: Original context
            adaptations: List of adaptations to apply
            
        Returns:
            Adapted context with all modifications applied
        """
        adapted_context = context.copy()
        
        for adapt_dict in adaptations:
            # Recreate Adaptation object
            adaptation = Adaptation(
                type=AdaptationType(adapt_dict['type']),
                name=adapt_dict['name'],
                description=adapt_dict['description'],
                confidence=adapt_dict['confidence'],
                impact=adapt_dict['impact'],
                parameters=adapt_dict['parameters'],
                source=adapt_dict['source'],
                constraints=adapt_dict['constraints']
            )
            
            # Apply the adaptation
            adapted_context = adaptation.apply_to_context(adapted_context)
            
            logger.info(f"Applied adaptation: {adaptation.name} (confidence: {adaptation.confidence})")
        
        return adapted_context
    
    async def record_adaptation_outcome(self, adaptation_name: str, 
                                      success: bool, 
                                      performance_score: float) -> None:
        """Record the outcome of applying an adaptation
        
        Args:
            adaptation_name: Name of the adaptation that was applied
            success: Whether the execution was successful
            performance_score: Performance score (0-1)
        """
        # Update performance history
        self.performance_history[adaptation_name].append(performance_score)
        
        # Store feedback for learning
        if self.vector_store:
            feedback_data = {
                'adaptation': adaptation_name,
                'success': success,
                'performance': performance_score,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.vector_store.store(
                key=f"adaptation_feedback_{adaptation_name}_{datetime.utcnow().timestamp()}",
                content=json.dumps(feedback_data),
                metadata={
                    'type': 'adaptation_feedback',
                    'adaptation_name': adaptation_name,
                    'success': success
                }
            )
        
        # Clear cache if performance is poor
        if performance_score < 0.5:
            # Remove from cache to force re-evaluation
            for key in list(self.adaptation_cache.keys()):
                cached = self.adaptation_cache[key]
                if any(a.name == adaptation_name for a in cached):
                    del self.adaptation_cache[key]
    
    def enable_adaptation_type(self, adaptation_type: AdaptationType) -> None:
        """Enable a specific adaptation type"""
        self.enabled_types.add(adaptation_type)
    
    def disable_adaptation_type(self, adaptation_type: AdaptationType) -> None:
        """Disable a specific adaptation type"""
        self.enabled_types.discard(adaptation_type)
    
    async def get_adaptation_statistics(self) -> Dict[str, Any]:
        """Get statistics about adaptation usage and effectiveness"""
        stats = {
            'enabled_types': [t.value for t in self.enabled_types],
            'cache_size': len(self.adaptation_cache),
            'performance_tracking': {}
        }
        
        # Calculate average performance by adaptation
        for adaptation_name, scores in self.performance_history.items():
            if scores:
                stats['performance_tracking'][adaptation_name] = {
                    'average_score': sum(scores) / len(scores),
                    'usage_count': len(scores),
                    'trend': self._calculate_trend(scores[-10:]) if len(scores) >= 3 else 'insufficient_data'
                }
        
        # Get knowledge base stats
        kb_stats = await self.knowledge_base.get_knowledge_statistics()
        stats['knowledge_base'] = {
            'preferences': kb_stats.get('user_preference', {}).get('count', 0),
            'learned_patterns': kb_stats.get('learned_pattern', {}).get('count', 0),
            'failure_patterns': kb_stats.get('failure_pattern', {}).get('count', 0)
        }
        
        return stats