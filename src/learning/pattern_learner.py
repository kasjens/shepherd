"""
Pattern Learning System - Phase 8 Implementation

Analyzes workflow executions to extract and optimize patterns for improved performance.
Features:
- Success pattern extraction
- Performance optimization
- Context flow analysis
- Decision point learning
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
from collections import defaultdict, Counter
import json
from dataclasses import dataclass

from ..memory.persistent_knowledge import PersistentKnowledgeBase
from ..core.models import WorkflowResult, ExecutionStep, ExecutionStatus

logger = logging.getLogger(__name__)


@dataclass
class PatternMetrics:
    """Metrics for evaluating pattern effectiveness"""
    success_rate: float
    average_duration: float
    resource_efficiency: float
    consistency_score: float
    usage_count: int
    last_used: datetime
    
    @property
    def overall_score(self) -> float:
        """Calculate overall pattern effectiveness score"""
        # Weighted combination of metrics
        score = (
            self.success_rate * 0.4 +
            (1.0 - min(self.average_duration / 300, 1.0)) * 0.2 +  # Normalize duration
            self.resource_efficiency * 0.2 +
            self.consistency_score * 0.2
        )
        # Boost for frequently used patterns
        if self.usage_count > 10:
            score *= 1.1
        return min(score, 1.0)


class PatternLearner:
    """Learns and optimizes patterns from workflow executions"""
    
    def __init__(self, knowledge_base: PersistentKnowledgeBase):
        """Initialize the pattern learner
        
        Args:
            knowledge_base: Persistent storage for learned patterns
        """
        self.knowledge_base = knowledge_base
        self.min_confidence = 0.7
        self.pattern_cache: Dict[str, PatternMetrics] = {}
        self.learning_buffer: List[WorkflowResult] = []
        self.optimization_threshold = 0.8
        self.pattern_version = "1.0"
        
    async def analyze_workflow_success(self, workflow: WorkflowResult) -> Dict[str, Any]:
        """Extract patterns from successful workflows
        
        Args:
            workflow: Completed workflow result to analyze
            
        Returns:
            Analysis results including extracted patterns and recommendations
        """
        # Add to learning buffer
        self.learning_buffer.append(workflow)
        
        # Only learn from sufficiently successful workflows
        if workflow.success_rate < self.min_confidence:
            logger.info(f"Workflow success rate {workflow.success_rate} below threshold {self.min_confidence}")
            return {
                'learned': False,
                'reason': 'success_rate_too_low',
                'success_rate': workflow.success_rate
            }
        
        # Extract comprehensive pattern
        pattern = await self._extract_comprehensive_pattern(workflow)
        
        # Check for similar existing patterns
        similar_patterns = await self.knowledge_base.find_similar_patterns(
            query=json.dumps(pattern['key_features']),
            knowledge_type='learned_pattern',
            limit=5
        )
        
        # Process the pattern
        if similar_patterns and similar_patterns[0]['distance'] < 0.1:
            # Very similar pattern exists - update it
            result = await self._update_existing_pattern(similar_patterns[0], pattern, workflow)
        else:
            # New pattern - store it
            result = await self._store_new_pattern(pattern, workflow)
        
        # Perform batch learning if buffer is full
        if len(self.learning_buffer) >= 10:
            await self._batch_pattern_optimization()
        
        return result
    
    async def _extract_comprehensive_pattern(self, workflow: WorkflowResult) -> Dict[str, Any]:
        """Extract a comprehensive pattern from workflow execution"""
        pattern = {
            'workflow_type': workflow.pattern.value,
            'key_features': {
                'workflow_pattern': workflow.pattern.value,
                'agent_count': len(set(step.agent_id for step in workflow.steps if step.agent_id)),
                'step_count': len(workflow.steps),
                'parallel_execution': any(step.parallel for step in workflow.steps),
                'has_conditions': any(hasattr(step, 'condition') for step in workflow.steps)
            },
            'agent_sequence': self._extract_agent_sequence(workflow),
            'context_transitions': self._extract_context_flow(workflow),
            'decision_points': self._extract_decisions(workflow),
            'resource_patterns': self._extract_resource_patterns(workflow),
            'timing_patterns': self._extract_timing_patterns(workflow),
            'success_factors': self._identify_success_factors(workflow),
            'performance_metrics': {
                'duration': workflow.total_duration,
                'success_rate': workflow.success_rate,
                'step_success_rates': self._calculate_step_success_rates(workflow),
                'resource_efficiency': self._calculate_resource_efficiency(workflow)
            },
            'metadata': {
                'pattern_version': self.pattern_version,
                'extraction_time': datetime.utcnow().isoformat(),
                'workflow_id': getattr(workflow, 'id', 'unknown')
            }
        }
        
        return pattern
    
    def _extract_agent_sequence(self, workflow: WorkflowResult) -> List[Dict[str, Any]]:
        """Extract the sequence of agent actions"""
        sequence = []
        
        for i, step in enumerate(workflow.steps):
            agent_action = {
                'order': i + 1,
                'agent_id': step.agent_id,
                'agent_type': getattr(step, 'agent_type', 'unknown'),
                'action': step.description,
                'duration': step.execution_time,
                'success': step.status == ExecutionStatus.COMPLETED,
                'dependencies': getattr(step, 'dependencies', []),
                'parallel': getattr(step, 'parallel', False)
            }
            
            # Add context if available
            if hasattr(step, 'context'):
                agent_action['context_used'] = list(step.context.keys())
            
            sequence.append(agent_action)
        
        return sequence
    
    def _extract_context_flow(self, workflow: WorkflowResult) -> List[Dict[str, Any]]:
        """Extract how context flows between steps"""
        context_flow = []
        
        for i in range(len(workflow.steps) - 1):
            current_step = workflow.steps[i]
            next_step = workflow.steps[i + 1]
            
            flow = {
                'from_step': i + 1,
                'to_step': i + 2,
                'context_passed': [],
                'transformations': []
            }
            
            # Analyze what context was passed
            if hasattr(current_step, 'output_context') and hasattr(next_step, 'input_context'):
                flow['context_passed'] = list(
                    set(current_step.output_context.keys()) & 
                    set(next_step.input_context.keys())
                )
                
                # Identify transformations
                for key in flow['context_passed']:
                    if current_step.output_context[key] != next_step.input_context[key]:
                        flow['transformations'].append({
                            'key': key,
                            'type': 'modified'
                        })
            
            if flow['context_passed'] or flow['transformations']:
                context_flow.append(flow)
        
        return context_flow
    
    def _extract_decisions(self, workflow: WorkflowResult) -> List[Dict[str, Any]]:
        """Extract decision points and their outcomes"""
        decisions = []
        
        for i, step in enumerate(workflow.steps):
            if hasattr(step, 'decision') or hasattr(step, 'condition'):
                decision = {
                    'step': i + 1,
                    'type': getattr(step, 'decision_type', 'conditional'),
                    'condition': getattr(step, 'condition', None),
                    'outcome': getattr(step, 'outcome', None),
                    'alternatives': getattr(step, 'alternatives', []),
                    'confidence': getattr(step, 'confidence', 1.0)
                }
                
                # Extract factors that influenced the decision
                if hasattr(step, 'decision_factors'):
                    decision['factors'] = step.decision_factors
                
                decisions.append(decision)
        
        return decisions
    
    def _extract_resource_patterns(self, workflow: WorkflowResult) -> Dict[str, Any]:
        """Extract patterns in resource usage"""
        resource_patterns = {
            'total_agents': len(set(step.agent_id for step in workflow.steps if step.agent_id)),
            'parallel_steps': sum(1 for step in workflow.steps if getattr(step, 'parallel', False)),
            'sequential_steps': sum(1 for step in workflow.steps if not getattr(step, 'parallel', False)),
            'tool_usage': defaultdict(int),
            'memory_access_patterns': {
                'local_reads': 0,
                'local_writes': 0,
                'shared_reads': 0,
                'shared_writes': 0,
                'vector_searches': 0
            }
        }
        
        # Count tool usage
        for step in workflow.steps:
            if hasattr(step, 'tools_used'):
                for tool in step.tools_used:
                    resource_patterns['tool_usage'][tool] += 1
        
        # Analyze memory access patterns
        for step in workflow.steps:
            if hasattr(step, 'memory_operations'):
                for op in step.memory_operations:
                    if op['type'] in resource_patterns['memory_access_patterns']:
                        resource_patterns['memory_access_patterns'][op['type']] += 1
        
        resource_patterns['tool_usage'] = dict(resource_patterns['tool_usage'])
        return resource_patterns
    
    def _extract_timing_patterns(self, workflow: WorkflowResult) -> Dict[str, Any]:
        """Extract timing patterns and bottlenecks"""
        steps_by_duration = sorted(workflow.steps, key=lambda s: s.execution_time, reverse=True)
        
        timing_patterns = {
            'total_duration': workflow.total_duration,
            'average_step_duration': workflow.total_duration / len(workflow.steps) if workflow.steps else 0,
            'longest_steps': [
                {
                    'step': workflow.steps.index(step) + 1,
                    'duration': step.execution_time,
                    'description': step.description,
                    'percentage': (step.execution_time / workflow.total_duration * 100) if workflow.total_duration > 0 else 0
                }
                for step in steps_by_duration[:3]  # Top 3 longest steps
            ],
            'parallel_efficiency': self._calculate_parallel_efficiency(workflow),
            'wait_times': self._extract_wait_times(workflow)
        }
        
        return timing_patterns
    
    def _identify_success_factors(self, workflow: WorkflowResult) -> List[Dict[str, Any]]:
        """Identify key factors that contributed to success"""
        success_factors = []
        
        # Factor 1: All critical steps succeeded
        critical_steps = [s for s in workflow.steps if getattr(s, 'critical', True)]
        if all(s.status == ExecutionStatus.COMPLETED for s in critical_steps):
            success_factors.append({
                'factor': 'all_critical_steps_succeeded',
                'impact': 'high',
                'details': f"{len(critical_steps)} critical steps completed successfully"
            })
        
        # Factor 2: Efficient parallel execution
        if self._calculate_parallel_efficiency(workflow) > 0.7:
            success_factors.append({
                'factor': 'efficient_parallel_execution',
                'impact': 'medium',
                'details': 'Parallel steps executed efficiently'
            })
        
        # Factor 3: Quick error recovery
        failed_steps = [s for s in workflow.steps if s.status == ExecutionStatus.FAILED]
        if failed_steps and workflow.success_rate > 0.8:
            success_factors.append({
                'factor': 'effective_error_recovery',
                'impact': 'high',
                'details': f"Recovered from {len(failed_steps)} failures"
            })
        
        # Factor 4: Resource optimization
        if hasattr(workflow, 'resource_usage') and workflow.resource_usage.get('efficiency', 0) > 0.8:
            success_factors.append({
                'factor': 'optimized_resource_usage',
                'impact': 'medium',
                'details': 'Resources used efficiently'
            })
        
        return success_factors
    
    def _calculate_step_success_rates(self, workflow: WorkflowResult) -> Dict[str, float]:
        """Calculate success rates for different types of steps"""
        step_types = defaultdict(lambda: {'total': 0, 'successful': 0})
        
        for step in workflow.steps:
            step_type = getattr(step, 'type', 'general')
            step_types[step_type]['total'] += 1
            if step.status == ExecutionStatus.COMPLETED:
                step_types[step_type]['successful'] += 1
        
        success_rates = {}
        for step_type, counts in step_types.items():
            if counts['total'] > 0:
                success_rates[step_type] = counts['successful'] / counts['total']
        
        return success_rates
    
    def _calculate_resource_efficiency(self, workflow: WorkflowResult) -> float:
        """Calculate overall resource efficiency"""
        if not hasattr(workflow, 'resource_usage'):
            return 0.5  # Default middle value
        
        efficiency_factors = []
        
        # CPU efficiency
        if 'cpu_usage' in workflow.resource_usage:
            cpu_eff = 1.0 - workflow.resource_usage['cpu_usage']
            efficiency_factors.append(cpu_eff)
        
        # Memory efficiency
        if 'memory_usage' in workflow.resource_usage:
            mem_eff = 1.0 - workflow.resource_usage['memory_usage']
            efficiency_factors.append(mem_eff)
        
        # Time efficiency (compared to estimated time)
        if hasattr(workflow, 'estimated_duration'):
            time_eff = min(workflow.estimated_duration / workflow.total_duration, 1.0)
            efficiency_factors.append(time_eff)
        
        return sum(efficiency_factors) / len(efficiency_factors) if efficiency_factors else 0.5
    
    def _calculate_parallel_efficiency(self, workflow: WorkflowResult) -> float:
        """Calculate how efficiently parallel steps were executed"""
        parallel_groups = self._identify_parallel_groups(workflow)
        
        if not parallel_groups:
            return 1.0  # No parallel execution, so "perfectly efficient"
        
        total_efficiency = 0.0
        for group in parallel_groups:
            # Ideal time is the longest step in the group
            ideal_time = max(step.execution_time for step in group)
            # Actual time is from start of first to end of last
            actual_time = max(step.execution_time + getattr(step, 'start_offset', 0) for step in group)
            
            efficiency = ideal_time / actual_time if actual_time > 0 else 0
            total_efficiency += efficiency
        
        return total_efficiency / len(parallel_groups)
    
    def _identify_parallel_groups(self, workflow: WorkflowResult) -> List[List[ExecutionStep]]:
        """Identify groups of steps that executed in parallel"""
        parallel_groups = []
        current_group = []
        
        for step in workflow.steps:
            if getattr(step, 'parallel', False):
                current_group.append(step)
            else:
                if current_group:
                    parallel_groups.append(current_group)
                    current_group = []
        
        if current_group:
            parallel_groups.append(current_group)
        
        return parallel_groups
    
    def _extract_wait_times(self, workflow: WorkflowResult) -> List[Dict[str, Any]]:
        """Extract wait times between steps"""
        wait_times = []
        
        for i in range(len(workflow.steps) - 1):
            current_end = getattr(workflow.steps[i], 'end_time', None)
            next_start = getattr(workflow.steps[i + 1], 'start_time', None)
            
            if current_end and next_start:
                wait_time = (next_start - current_end).total_seconds()
                if wait_time > 0.1:  # Significant wait
                    wait_times.append({
                        'after_step': i + 1,
                        'before_step': i + 2,
                        'duration': wait_time,
                        'reason': getattr(workflow.steps[i + 1], 'wait_reason', 'unknown')
                    })
        
        return wait_times
    
    async def _update_existing_pattern(self, existing: Dict[str, Any], 
                                     new_pattern: Dict[str, Any], 
                                     workflow: WorkflowResult) -> Dict[str, Any]:
        """Update an existing pattern with new information"""
        logger.info(f"Updating existing pattern {existing.get('id', 'unknown')}")
        
        # Merge performance metrics
        existing_data = existing.get('data', {})
        existing_metrics = existing_data.get('performance_metrics', {})
        new_metrics = new_pattern['performance_metrics']
        
        # Update metrics with weighted average
        usage_count = existing_data.get('usage_count', 1)
        updated_metrics = {
            'duration': (existing_metrics.get('duration', 0) * usage_count + new_metrics['duration']) / (usage_count + 1),
            'success_rate': (existing_metrics.get('success_rate', 0) * usage_count + new_metrics['success_rate']) / (usage_count + 1),
            'resource_efficiency': (existing_metrics.get('resource_efficiency', 0) * usage_count + new_metrics['resource_efficiency']) / (usage_count + 1)
        }
        
        # Merge success factors
        existing_factors = set(f['factor'] for f in existing_data.get('success_factors', []))
        new_factors = [f for f in new_pattern['success_factors'] if f['factor'] not in existing_factors]
        
        # Create updated pattern
        updated_pattern = {
            **existing_data,
            'performance_metrics': updated_metrics,
            'success_factors': existing_data.get('success_factors', []) + new_factors,
            'usage_count': usage_count + 1,
            'last_updated': datetime.utcnow().isoformat(),
            'confidence': min(0.95, existing_data.get('confidence', 0.7) + 0.05)  # Increase confidence
        }
        
        # Store updated pattern
        await self.knowledge_base.store_learned_pattern(updated_pattern)
        
        # Update cache
        pattern_key = self._generate_pattern_key(new_pattern)
        self.pattern_cache[pattern_key] = PatternMetrics(
            success_rate=updated_metrics['success_rate'],
            average_duration=updated_metrics['duration'],
            resource_efficiency=updated_metrics['resource_efficiency'],
            consistency_score=0.9,  # High consistency since pattern repeated
            usage_count=usage_count + 1,
            last_used=datetime.utcnow()
        )
        
        return {
            'action': 'updated',
            'pattern_id': existing.get('id'),
            'usage_count': usage_count + 1,
            'confidence': updated_pattern['confidence']
        }
    
    async def _store_new_pattern(self, pattern: Dict[str, Any], 
                               workflow: WorkflowResult) -> Dict[str, Any]:
        """Store a new pattern"""
        logger.info("Storing new workflow pattern")
        
        # Add metadata
        pattern['usage_count'] = 1
        pattern['created_at'] = datetime.utcnow().isoformat()
        pattern['confidence'] = self.min_confidence
        pattern['pattern_id'] = self._generate_pattern_key(pattern)
        
        # Store the pattern
        stored = await self.knowledge_base.store_learned_pattern(pattern)
        
        # Cache pattern metrics
        self.pattern_cache[pattern['pattern_id']] = PatternMetrics(
            success_rate=pattern['performance_metrics']['success_rate'],
            average_duration=pattern['performance_metrics']['duration'],
            resource_efficiency=pattern['performance_metrics']['resource_efficiency'],
            consistency_score=0.7,  # Initial score
            usage_count=1,
            last_used=datetime.utcnow()
        )
        
        return {
            'action': 'created',
            'pattern_id': pattern['pattern_id'],
            'confidence': pattern['confidence']
        }
    
    def _generate_pattern_key(self, pattern: Dict[str, Any]) -> str:
        """Generate a unique key for a pattern"""
        key_components = [
            pattern['workflow_type'],
            str(pattern['key_features']['agent_count']),
            str(pattern['key_features']['step_count']),
            str(pattern['key_features']['parallel_execution']),
            str(pattern['key_features']['has_conditions'])
        ]
        return '_'.join(key_components)
    
    async def _batch_pattern_optimization(self) -> None:
        """Perform batch optimization on accumulated patterns"""
        logger.info(f"Running batch optimization on {len(self.learning_buffer)} workflows")
        
        # Group workflows by pattern type
        pattern_groups = defaultdict(list)
        for workflow in self.learning_buffer:
            pattern_groups[workflow.pattern.value].append(workflow)
        
        # Optimize each pattern type
        for pattern_type, workflows in pattern_groups.items():
            await self._optimize_pattern_type(pattern_type, workflows)
        
        # Clear the buffer
        self.learning_buffer.clear()
    
    async def _optimize_pattern_type(self, pattern_type: str, 
                                   workflows: List[WorkflowResult]) -> None:
        """Optimize a specific pattern type based on multiple executions"""
        # Find common successful paths
        successful_workflows = [w for w in workflows if w.success_rate >= self.optimization_threshold]
        
        if len(successful_workflows) < 2:
            return
        
        # Extract common patterns
        common_sequences = self._find_common_sequences(successful_workflows)
        optimal_resource_patterns = self._find_optimal_resource_patterns(successful_workflows)
        
        # Create optimized pattern
        optimized_pattern = {
            'type': 'optimized',
            'pattern_type': pattern_type,
            'common_sequences': common_sequences,
            'optimal_resources': optimal_resource_patterns,
            'based_on_count': len(successful_workflows),
            'average_performance': {
                'duration': sum(w.total_duration for w in successful_workflows) / len(successful_workflows),
                'success_rate': sum(w.success_rate for w in successful_workflows) / len(successful_workflows)
            },
            'optimization_date': datetime.utcnow().isoformat()
        }
        
        # Store as high-confidence pattern
        optimized_pattern['confidence'] = 0.9
        await self.knowledge_base.store_learned_pattern(optimized_pattern)
    
    def _find_common_sequences(self, workflows: List[WorkflowResult]) -> List[Dict[str, Any]]:
        """Find common action sequences across workflows"""
        # Extract sequences
        sequences = []
        for workflow in workflows:
            sequence = [
                (step.agent_id, step.description)
                for step in workflow.steps
                if step.status == ExecutionStatus.COMPLETED
            ]
            sequences.append(sequence)
        
        # Find common subsequences (simplified algorithm)
        common = []
        if sequences:
            # Find pairs that appear in most sequences
            pair_counts = Counter()
            for seq in sequences:
                for i in range(len(seq) - 1):
                    pair = (seq[i], seq[i + 1])
                    pair_counts[pair] += 1
            
            # Extract common pairs (appearing in >50% of workflows)
            threshold = len(sequences) * 0.5
            for pair, count in pair_counts.items():
                if count >= threshold:
                    common.append({
                        'sequence': [pair[0], pair[1]],
                        'frequency': count / len(sequences),
                        'confidence': count / len(sequences)
                    })
        
        return common
    
    def _find_optimal_resource_patterns(self, workflows: List[WorkflowResult]) -> Dict[str, Any]:
        """Find optimal resource usage patterns"""
        # Collect resource patterns from most efficient workflows
        workflows_by_efficiency = sorted(
            workflows,
            key=lambda w: self._calculate_resource_efficiency(w),
            reverse=True
        )
        
        top_efficient = workflows_by_efficiency[:max(3, len(workflows) // 3)]
        
        # Average the resource patterns
        avg_patterns = {
            'optimal_agent_count': sum(
                len(set(s.agent_id for s in w.steps if s.agent_id))
                for w in top_efficient
            ) / len(top_efficient),
            'optimal_parallel_ratio': sum(
                sum(1 for s in w.steps if getattr(s, 'parallel', False)) / len(w.steps)
                for w in top_efficient
            ) / len(top_efficient),
            'recommended_tools': self._extract_recommended_tools(top_efficient)
        }
        
        return avg_patterns
    
    def _extract_recommended_tools(self, workflows: List[WorkflowResult]) -> List[str]:
        """Extract commonly used tools from efficient workflows"""
        tool_counts = Counter()
        
        for workflow in workflows:
            for step in workflow.steps:
                if hasattr(step, 'tools_used'):
                    for tool in step.tools_used:
                        tool_counts[tool] += 1
        
        # Return tools used in >50% of workflows
        threshold = len(workflows) * 0.5
        return [tool for tool, count in tool_counts.items() if count >= threshold]
    
    async def get_pattern_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get pattern recommendations for a given context"""
        # Find similar successful patterns
        context_str = json.dumps({
            'workflow_type': context.get('workflow_type'),
            'requirements': context.get('requirements', []),
            'constraints': context.get('constraints', [])
        })
        
        similar_patterns = await self.knowledge_base.find_similar_patterns(
            query=context_str,
            knowledge_type='learned_pattern',
            limit=10
        )
        
        recommendations = []
        for pattern in similar_patterns:
            pattern_data = pattern.get('data', {})
            
            # Calculate recommendation score
            score = self._calculate_recommendation_score(pattern_data, context)
            
            if score > 0.5:
                recommendations.append({
                    'pattern_id': pattern_data.get('pattern_id'),
                    'workflow_type': pattern_data.get('workflow_type'),
                    'confidence': pattern_data.get('confidence', 0.5),
                    'performance': pattern_data.get('performance_metrics', {}),
                    'recommendation_score': score,
                    'key_features': pattern_data.get('key_features', {}),
                    'success_factors': pattern_data.get('success_factors', [])[:3]  # Top 3
                })
        
        # Sort by recommendation score
        recommendations.sort(key=lambda r: r['recommendation_score'], reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _calculate_recommendation_score(self, pattern: Dict[str, Any], 
                                      context: Dict[str, Any]) -> float:
        """Calculate how well a pattern matches the given context"""
        score = 0.0
        
        # Workflow type match
        if pattern.get('workflow_type') == context.get('workflow_type'):
            score += 0.3
        
        # Performance score
        if 'performance_metrics' in pattern:
            perf = pattern['performance_metrics']
            perf_score = perf.get('success_rate', 0) * 0.5 + (1.0 - min(perf.get('duration', 300) / 300, 1.0)) * 0.5
            score += perf_score * 0.3
        
        # Usage and confidence
        usage_count = pattern.get('usage_count', 0)
        if usage_count > 5:
            score += 0.2
        
        confidence = pattern.get('confidence', 0.5)
        score += confidence * 0.2
        
        return min(score, 1.0)
    
    async def analyze_failure_patterns(self, workflow: WorkflowResult) -> Dict[str, Any]:
        """Analyze failed workflows to identify patterns to avoid"""
        if workflow.success_rate >= self.min_confidence:
            return {'analyzed': False, 'reason': 'workflow_successful'}
        
        failure_pattern = {
            'workflow_type': workflow.pattern.value,
            'failure_points': [],
            'common_issues': [],
            'recovery_suggestions': []
        }
        
        # Identify failure points
        for i, step in enumerate(workflow.steps):
            if step.status == ExecutionStatus.FAILED:
                failure_point = {
                    'step': i + 1,
                    'agent': step.agent_id,
                    'action': step.description,
                    'error': getattr(step, 'error', 'Unknown error'),
                    'context': getattr(step, 'context', {})
                }
                failure_pattern['failure_points'].append(failure_point)
        
        # Look for common issues
        if len(failure_pattern['failure_points']) > 1:
            # Multiple failures might indicate systemic issues
            failure_pattern['common_issues'].append({
                'issue': 'multiple_failures',
                'severity': 'high',
                'description': f"{len(failure_pattern['failure_points'])} steps failed"
            })
        
        # Generate recovery suggestions
        failure_pattern['recovery_suggestions'] = await self._generate_recovery_suggestions(workflow, failure_pattern)
        
        # Store as failure pattern
        await self.knowledge_base.store_failure_pattern(
            task_description=f"Workflow {workflow.pattern.value}",
            failure_reason=json.dumps(failure_pattern['failure_points']),
            context=failure_pattern,
            recovery_strategy='; '.join(failure_pattern['recovery_suggestions'])
        )
        
        return {
            'analyzed': True,
            'failure_points': len(failure_pattern['failure_points']),
            'suggestions': failure_pattern['recovery_suggestions']
        }
    
    async def _generate_recovery_suggestions(self, workflow: WorkflowResult, 
                                           failure_pattern: Dict[str, Any]) -> List[str]:
        """Generate suggestions for recovering from failures"""
        suggestions = []
        
        # Check if similar successful patterns exist
        similar_successful = await self.knowledge_base.find_similar_patterns(
            query=workflow.pattern.value,
            knowledge_type='learned_pattern',
            limit=3
        )
        
        if similar_successful:
            suggestions.append("Consider using proven patterns from similar successful workflows")
        
        # Analyze specific failure types
        for failure in failure_pattern['failure_points']:
            error = failure.get('error', '').lower()
            
            if 'timeout' in error:
                suggestions.append(f"Increase timeout for step {failure['step']} or optimize performance")
            elif 'resource' in error:
                suggestions.append(f"Check resource availability before step {failure['step']}")
            elif 'permission' in error:
                suggestions.append(f"Verify permissions for agent {failure['agent']}")
        
        # General suggestions
        if len(failure_pattern['failure_points']) > len(workflow.steps) * 0.3:
            suggestions.append("Consider breaking down the workflow into smaller, more manageable parts")
        
        return suggestions
    
    async def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learned patterns and insights"""
        # Get pattern statistics
        all_patterns = await self.knowledge_base.get_knowledge_statistics()
        
        learned_patterns = all_patterns.get('learned_pattern', {}).get('count', 0)
        failure_patterns = all_patterns.get('failure_pattern', {}).get('count', 0)
        
        # Calculate cache statistics
        active_patterns = len(self.pattern_cache)
        avg_score = sum(m.overall_score for m in self.pattern_cache.values()) / active_patterns if active_patterns > 0 else 0
        
        return {
            'total_patterns_learned': learned_patterns,
            'failure_patterns_identified': failure_patterns,
            'active_patterns_cached': active_patterns,
            'average_pattern_score': avg_score,
            'learning_buffer_size': len(self.learning_buffer),
            'optimization_performed': learned_patterns > 10,
            'last_optimization': getattr(self, 'last_optimization', None)
        }