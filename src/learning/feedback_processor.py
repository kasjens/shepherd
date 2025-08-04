"""
User Feedback Processor - Phase 8 Implementation

Processes various types of user feedback to improve system behavior:
- Corrections: Fix mistakes and update knowledge
- Preferences: Store user-specific preferences
- Guidance: Learn from user instructions
- Ratings: Track performance feedback
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import logging
from collections import defaultdict

from ..memory.persistent_knowledge import PersistentKnowledgeBase
from ..core.models import WorkflowResult

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback that can be processed"""
    CORRECTION = "correction"
    PREFERENCE = "preference"
    GUIDANCE = "guidance"
    RATING = "rating"
    SUGGESTION = "suggestion"
    WARNING = "warning"


class FeedbackSeverity(Enum):
    """Severity levels for feedback impact"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserFeedbackProcessor:
    """Processes user feedback to improve system behavior and knowledge"""
    
    def __init__(self, knowledge_base: PersistentKnowledgeBase):
        """Initialize the feedback processor
        
        Args:
            knowledge_base: Persistent storage for learned patterns and preferences
        """
        self.knowledge_base = knowledge_base
        self.feedback_history: List[Dict[str, Any]] = []
        self.feedback_stats = defaultdict(int)
        self.learning_rate = 0.1  # How quickly to adapt based on feedback
        self.confidence_threshold = 0.7  # Minimum confidence for applying learnings
        
    async def process_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Process user feedback and update knowledge
        
        Args:
            feedback: Feedback data containing type, content, context, etc.
            
        Returns:
            Processing result with applied changes and recommendations
        """
        try:
            # Validate feedback structure
            feedback_type = FeedbackType(feedback.get('type'))
            severity = FeedbackSeverity(feedback.get('severity', 'medium'))
            
            # Add metadata
            feedback['timestamp'] = datetime.utcnow().isoformat()
            feedback['severity'] = severity.value
            
            # Process based on type
            result = None
            if feedback_type == FeedbackType.CORRECTION:
                result = await self._process_correction(feedback)
            elif feedback_type == FeedbackType.PREFERENCE:
                result = await self._process_preference(feedback)
            elif feedback_type == FeedbackType.GUIDANCE:
                result = await self._process_guidance(feedback)
            elif feedback_type == FeedbackType.RATING:
                result = await self._process_rating(feedback)
            elif feedback_type == FeedbackType.SUGGESTION:
                result = await self._process_suggestion(feedback)
            elif feedback_type == FeedbackType.WARNING:
                result = await self._process_warning(feedback)
                
            # Store feedback history
            self.feedback_history.append(feedback)
            self.feedback_stats[feedback_type.value] += 1
            
            # Analyze patterns in feedback
            if len(self.feedback_history) % 10 == 0:
                await self._analyze_feedback_patterns()
                
            logger.info(f"Processed {feedback_type.value} feedback with severity {severity.value}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            return {
                'success': False,
                'error': str(e),
                'feedback_type': feedback.get('type', 'unknown')
            }
    
    async def _process_correction(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Process correction feedback to fix mistakes
        
        Args:
            feedback: Correction details including what was wrong and correct approach
        """
        correction_data = {
            'original_action': feedback.get('original_action'),
            'correct_action': feedback.get('correct_action'),
            'context': feedback.get('context', {}),
            'explanation': feedback.get('explanation', ''),
            'impact': self._calculate_impact(feedback)
        }
        
        # Store as failure pattern to avoid
        await self.knowledge_base.store_failure_pattern(
            task_description=feedback.get('task_description', ''),
            failure_reason=feedback.get('explanation', 'User correction'),
            context=correction_data,
            recovery_strategy=feedback.get('correct_action', '')
        )
        
        # If high severity, also store as learned pattern
        if feedback.get('severity') in ['high', 'critical']:
            await self.knowledge_base.store_learned_pattern(
                pattern_data={
                    'type': 'correction',
                    'pattern': correction_data,
                    'confidence': 0.9
                }
            )
        
        return {
            'success': True,
            'type': 'correction',
            'impact': correction_data['impact'],
            'knowledge_updated': True
        }
    
    async def _process_preference(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Store user preferences for future reference
        
        Args:
            feedback: Preference details including context and preferred approaches
        """
        preference = {
            'context': feedback.get('context', {}),
            'preference': feedback.get('preference'),
            'examples': feedback.get('examples', []),
            'strength': feedback.get('strength', 0.5),
            'conditions': feedback.get('conditions', {}),
            'metadata': {
                'source': feedback.get('source', 'direct_feedback'),
                'confidence': feedback.get('confidence', 0.8)
            }
        }
        
        # Check for conflicting preferences
        similar_prefs = await self.knowledge_base.find_similar_patterns(
            query=str(preference['context']),
            knowledge_type='user_preference',
            limit=5
        )
        
        # Resolve conflicts or merge preferences
        if similar_prefs:
            preference = await self._merge_preferences(preference, similar_prefs)
        
        # Store the preference
        await self.knowledge_base.store_user_preference(
            preference_key=feedback.get('key', 'general'),
            preference_data=preference
        )
        
        return {
            'success': True,
            'type': 'preference',
            'stored': True,
            'conflicts_resolved': len(similar_prefs) > 0
        }
    
    async def _process_guidance(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Process user guidance to improve future behavior
        
        Args:
            feedback: Guidance including instructions and examples
        """
        guidance_pattern = {
            'instruction': feedback.get('instruction'),
            'context': feedback.get('context', {}),
            'examples': feedback.get('examples', []),
            'constraints': feedback.get('constraints', []),
            'expected_outcomes': feedback.get('expected_outcomes', []),
            'priority': feedback.get('priority', 'medium')
        }
        
        # Extract actionable patterns
        patterns = self._extract_guidance_patterns(guidance_pattern)
        
        # Store each pattern
        stored_patterns = []
        for pattern in patterns:
            await self.knowledge_base.store_learned_pattern(pattern)
            stored_patterns.append(pattern)
        
        # Create workflow template if comprehensive enough
        if len(patterns) >= 3 and feedback.get('create_template', False):
            template = await self._create_workflow_template(guidance_pattern)
            await self.knowledge_base.store_workflow_template(
                template_name=feedback.get('template_name', 'user_guided'),
                template_data=template
            )
        
        return {
            'success': True,
            'type': 'guidance',
            'patterns_extracted': len(patterns),
            'patterns_stored': len(stored_patterns),
            'template_created': feedback.get('create_template', False)
        }
    
    async def _process_rating(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Process performance ratings to track quality
        
        Args:
            feedback: Rating information including score and context
        """
        rating_data = {
            'score': feedback.get('score', 0),
            'max_score': feedback.get('max_score', 5),
            'normalized_score': feedback.get('score', 0) / feedback.get('max_score', 5),
            'context': feedback.get('context', {}),
            'workflow_id': feedback.get('workflow_id'),
            'agent_ids': feedback.get('agent_ids', []),
            'aspects': feedback.get('aspects', {})  # Detailed ratings by aspect
        }
        
        # Update performance metrics
        if rating_data['normalized_score'] < 0.4:
            # Low rating - store as failure pattern
            await self.knowledge_base.store_failure_pattern(
                task_description=feedback.get('task_description', ''),
                failure_reason=f"Low user rating: {rating_data['score']}/{rating_data['max_score']}",
                context=rating_data,
                recovery_strategy="Analyze user feedback and adjust approach"
            )
        elif rating_data['normalized_score'] > 0.8:
            # High rating - reinforce as successful pattern
            await self.knowledge_base.store_learned_pattern({
                'type': 'successful_approach',
                'rating': rating_data,
                'confidence': rating_data['normalized_score']
            })
        
        # Calculate performance trends
        trends = await self._calculate_performance_trends(rating_data)
        
        return {
            'success': True,
            'type': 'rating',
            'score': rating_data['normalized_score'],
            'trends': trends,
            'actions_taken': ['stored_failure' if rating_data['normalized_score'] < 0.4 else 'reinforced_success']
        }
    
    async def _process_suggestion(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Process user suggestions for improvements
        
        Args:
            feedback: Suggestion details and implementation hints
        """
        suggestion = {
            'idea': feedback.get('suggestion'),
            'category': feedback.get('category', 'general'),
            'feasibility': await self._assess_feasibility(feedback),
            'priority': feedback.get('priority', 'low'),
            'implementation_hints': feedback.get('hints', []),
            'benefits': feedback.get('benefits', [])
        }
        
        # Store as potential improvement
        await self.knowledge_base.store_domain_knowledge(
            domain='user_suggestions',
            knowledge={
                'type': 'improvement_suggestion',
                'data': suggestion,
                'status': 'pending_review'
            }
        )
        
        return {
            'success': True,
            'type': 'suggestion',
            'stored': True,
            'feasibility': suggestion['feasibility']
        }
    
    async def _process_warning(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Process warnings about potential issues
        
        Args:
            feedback: Warning details and risk information
        """
        warning = {
            'issue': feedback.get('issue'),
            'severity': feedback.get('severity', 'medium'),
            'context': feedback.get('context', {}),
            'potential_impact': feedback.get('impact', 'unknown'),
            'prevention': feedback.get('prevention', [])
        }
        
        # Store as failure pattern to avoid
        await self.knowledge_base.store_failure_pattern(
            task_description=f"Warning: {warning['issue']}",
            failure_reason=warning['issue'],
            context=warning,
            recovery_strategy=' '.join(warning['prevention'])
        )
        
        # If critical, create immediate safeguards
        if warning['severity'] == 'critical':
            await self._create_safeguards(warning)
        
        return {
            'success': True,
            'type': 'warning',
            'severity': warning['severity'],
            'safeguards_created': warning['severity'] == 'critical'
        }
    
    async def _analyze_feedback_patterns(self) -> None:
        """Analyze patterns in accumulated feedback"""
        if not self.feedback_history:
            return
            
        # Group feedback by type
        by_type = defaultdict(list)
        for fb in self.feedback_history[-50:]:  # Last 50 feedback items
            by_type[fb.get('type')].append(fb)
        
        # Look for recurring themes
        for feedback_type, items in by_type.items():
            if len(items) >= 3:  # Minimum for pattern
                contexts = [item.get('context', {}) for item in items]
                # Simple pattern detection - could be enhanced with ML
                common_keys = set.intersection(*[set(ctx.keys()) for ctx in contexts if ctx])
                
                if common_keys:
                    pattern = {
                        'feedback_type': feedback_type,
                        'common_context': list(common_keys),
                        'frequency': len(items),
                        'time_span': (
                            self.feedback_history[-1]['timestamp'],
                            self.feedback_history[-50]['timestamp']
                        )
                    }
                    
                    await self.knowledge_base.store_learned_pattern({
                        'type': 'feedback_pattern',
                        'pattern': pattern,
                        'confidence': min(0.9, len(items) / 10)
                    })
    
    def _calculate_impact(self, feedback: Dict[str, Any]) -> float:
        """Calculate the impact score of feedback"""
        severity_scores = {
            'low': 0.25,
            'medium': 0.5,
            'high': 0.75,
            'critical': 1.0
        }
        
        base_score = severity_scores.get(feedback.get('severity', 'medium'), 0.5)
        
        # Adjust based on frequency
        if feedback.get('frequency', 'once') == 'recurring':
            base_score *= 1.5
            
        # Adjust based on scope
        scope_multipliers = {
            'single_task': 0.8,
            'workflow': 1.0,
            'system_wide': 1.5
        }
        base_score *= scope_multipliers.get(feedback.get('scope', 'workflow'), 1.0)
        
        return min(1.0, base_score)
    
    async def _merge_preferences(self, new_pref: Dict[str, Any], 
                                existing: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge new preference with existing ones, resolving conflicts"""
        # Simple merge strategy - could be enhanced
        merged = new_pref.copy()
        
        for existing_pref in existing:
            # If contexts overlap significantly
            if self._context_similarity(new_pref['context'], 
                                       existing_pref.get('data', {}).get('context', {})) > 0.7:
                # Average the strengths
                merged['strength'] = (merged['strength'] + 
                                    existing_pref.get('data', {}).get('strength', 0.5)) / 2
                
                # Combine examples
                merged['examples'].extend(existing_pref.get('data', {}).get('examples', []))
                
                # Merge conditions
                merged['conditions'].update(existing_pref.get('data', {}).get('conditions', {}))
        
        return merged
    
    def _context_similarity(self, ctx1: Dict[str, Any], ctx2: Dict[str, Any]) -> float:
        """Calculate similarity between two contexts"""
        if not ctx1 or not ctx2:
            return 0.0
            
        # Simple Jaccard similarity on keys
        keys1 = set(ctx1.keys())
        keys2 = set(ctx2.keys())
        
        if not keys1 or not keys2:
            return 0.0
            
        intersection = keys1.intersection(keys2)
        union = keys1.union(keys2)
        
        return len(intersection) / len(union)
    
    def _extract_guidance_patterns(self, guidance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actionable patterns from guidance"""
        patterns = []
        
        # Extract from examples
        for example in guidance.get('examples', []):
            pattern = {
                'type': 'guided_example',
                'input': example.get('input', {}),
                'expected_output': example.get('output', {}),
                'constraints': guidance.get('constraints', []),
                'confidence': 0.8
            }
            patterns.append(pattern)
        
        # Extract from instructions
        if guidance.get('instruction'):
            pattern = {
                'type': 'guided_instruction',
                'instruction': guidance['instruction'],
                'context_requirements': guidance.get('context', {}),
                'priority': guidance.get('priority', 'medium'),
                'confidence': 0.7
            }
            patterns.append(pattern)
        
        return patterns
    
    async def _create_workflow_template(self, guidance: Dict[str, Any]) -> Dict[str, Any]:
        """Create a workflow template from comprehensive guidance"""
        template = {
            'name': guidance.get('template_name', 'user_guided_workflow'),
            'description': guidance.get('instruction', ''),
            'steps': [],
            'constraints': guidance.get('constraints', []),
            'expected_outcomes': guidance.get('expected_outcomes', []),
            'created_from': 'user_guidance',
            'confidence': 0.7
        }
        
        # Convert examples to workflow steps
        for i, example in enumerate(guidance.get('examples', [])):
            step = {
                'order': i + 1,
                'action': example.get('action', f'Step {i + 1}'),
                'input': example.get('input', {}),
                'expected_output': example.get('output', {}),
                'optional': example.get('optional', False)
            }
            template['steps'].append(step)
        
        return template
    
    async def _assess_feasibility(self, feedback: Dict[str, Any]) -> float:
        """Assess feasibility of a suggestion"""
        # Simple heuristic - could be enhanced with more sophisticated analysis
        feasibility = 0.5
        
        # Check if similar patterns exist
        similar = await self.knowledge_base.find_similar_patterns(
            query=feedback.get('suggestion', ''),
            knowledge_type='learned_pattern',
            limit=3
        )
        
        if similar:
            # More feasible if similar things have been done
            feasibility += 0.2
        
        # Adjust based on complexity hints
        if 'simple' in feedback.get('suggestion', '').lower():
            feasibility += 0.1
        elif 'complex' in feedback.get('suggestion', '').lower():
            feasibility -= 0.1
        
        return max(0.0, min(1.0, feasibility))
    
    async def _create_safeguards(self, warning: Dict[str, Any]) -> None:
        """Create immediate safeguards for critical warnings"""
        safeguard = {
            'type': 'critical_safeguard',
            'trigger': warning['issue'],
            'prevention_steps': warning.get('prevention', []),
            'check_conditions': {
                'context_match': warning.get('context', {}),
                'severity_threshold': 'high'
            },
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Store as high-priority failure pattern
        await self.knowledge_base.store_failure_pattern(
            task_description=f"SAFEGUARD: {warning['issue']}",
            failure_reason=f"Critical warning: {warning['issue']}",
            context=safeguard,
            recovery_strategy="Apply prevention steps immediately"
        )
    
    async def _calculate_performance_trends(self, rating: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance trends from ratings"""
        # Get recent ratings
        recent_ratings = [
            fb for fb in self.feedback_history[-20:]
            if fb.get('type') == 'rating'
        ]
        
        if len(recent_ratings) < 2:
            return {'trend': 'insufficient_data'}
        
        scores = [r.get('score', 0) / r.get('max_score', 5) for r in recent_ratings]
        
        # Simple trend calculation
        first_half = sum(scores[:len(scores)//2]) / (len(scores)//2)
        second_half = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
        
        trend_value = second_half - first_half
        
        return {
            'trend': 'improving' if trend_value > 0.1 else 'declining' if trend_value < -0.1 else 'stable',
            'trend_value': trend_value,
            'average_score': sum(scores) / len(scores),
            'sample_size': len(scores)
        }
    
    async def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of all processed feedback"""
        return {
            'total_feedback': len(self.feedback_history),
            'feedback_by_type': dict(self.feedback_stats),
            'recent_trends': await self._calculate_performance_trends({}),
            'last_processed': self.feedback_history[-1]['timestamp'] if self.feedback_history else None
        }