import re
from typing import List, Dict, Any
from dataclasses import dataclass
from .models import PromptAnalysis, WorkflowPattern, TaskType


class PromptAnalyzer:
    def __init__(self):
        self.complexity_keywords = {
            "simple": 0.2,
            "basic": 0.2,
            "complex": 0.8,
            "complicated": 0.8,
            "multi-step": 0.7,
            "comprehensive": 0.9,
            "detailed": 0.7,
            "analyze": 0.6,
            "implement": 0.8,
            "create": 0.6,
            "fix": 0.5,
            "debug": 0.7,
            "optimize": 0.8,
            "refactor": 0.7
        }
        
        self.urgency_keywords = {
            "urgent": 0.9,
            "asap": 0.9,
            "immediately": 0.9,
            "critical": 1.0,
            "emergency": 1.0,
            "when possible": 0.3,
            "eventually": 0.2,
            "normal": 0.5
        }
        
        self.quality_keywords = {
            "high quality": 0.9,
            "production ready": 0.9,
            "robust": 0.8,
            "reliable": 0.8,
            "quick": 0.4,
            "draft": 0.3,
            "prototype": 0.5,
            "mvp": 0.6,
            "perfect": 1.0,
            "best": 0.9
        }
        
        self.task_type_keywords = {
            TaskType.RESEARCH: ["research", "find", "search", "investigate", "explore", "analyze data"],
            TaskType.CREATIVE: ["create", "design", "write", "generate", "compose", "build"],
            TaskType.ANALYTICAL: ["analyze", "evaluate", "assess", "review", "audit", "diagnose"],
            TaskType.TECHNICAL: ["implement", "code", "program", "develop", "fix", "debug", "deploy"],
            TaskType.COMMUNICATION: ["document", "explain", "present", "report", "summarize", "communicate"]
        }
        
        self.pattern_indicators = {
            WorkflowPattern.SEQUENTIAL: ["then", "after", "next", "followed by", "step by step"],
            WorkflowPattern.PARALLEL: ["simultaneously", "at the same time", "concurrently", "in parallel"],
            WorkflowPattern.CONDITIONAL: ["if", "when", "depending on", "based on", "choose"],
            WorkflowPattern.ITERATIVE: ["until", "repeat", "iterate", "refine", "improve"],
            WorkflowPattern.HIERARCHICAL: ["coordinate", "manage", "oversee", "delegate", "team"]
        }
    
    def analyze_prompt(self, user_request: str) -> PromptAnalysis:
        request_lower = user_request.lower()
        
        complexity_score = self._calculate_complexity(request_lower)
        urgency_score = self._calculate_urgency(request_lower)
        quality_requirements = self._calculate_quality_requirements(request_lower)
        task_types = self._identify_task_types(request_lower)
        
        dependencies = self._has_dependencies(request_lower)
        parallel_potential = self._has_parallel_potential(request_lower)
        decision_points = self._has_decision_points(request_lower)
        iteration_needed = self._needs_iteration(request_lower)
        
        team_size_needed = self._estimate_team_size(complexity_score, len(task_types))
        recommended_pattern = self._recommend_pattern(
            request_lower, dependencies, parallel_potential, 
            decision_points, iteration_needed
        )
        
        confidence = self._calculate_confidence(
            complexity_score, len(task_types), recommended_pattern
        )
        
        return PromptAnalysis(
            complexity_score=complexity_score,
            urgency_score=urgency_score,
            quality_requirements=quality_requirements,
            task_types=[t.value for t in task_types],
            dependencies=dependencies,
            parallel_potential=parallel_potential,
            decision_points=decision_points,
            iteration_needed=iteration_needed,
            team_size_needed=team_size_needed,
            recommended_pattern=recommended_pattern,
            confidence=confidence
        )
    
    def _calculate_complexity(self, text: str) -> float:
        scores = []
        for keyword, score in self.complexity_keywords.items():
            if keyword in text:
                scores.append(score)
        
        word_count = len(text.split())
        length_factor = min(word_count / 100, 1.0) * 0.3
        
        if scores:
            return min(max(scores) + length_factor, 1.0)
        return 0.5 + length_factor
    
    def _calculate_urgency(self, text: str) -> float:
        for keyword, score in self.urgency_keywords.items():
            if keyword in text:
                return score
        return 0.5
    
    def _calculate_quality_requirements(self, text: str) -> float:
        scores = []
        for keyword, score in self.quality_keywords.items():
            if keyword in text:
                scores.append(score)
        
        if scores:
            return max(scores)
        return 0.7
    
    def _identify_task_types(self, text: str) -> List[TaskType]:
        identified_types = []
        for task_type, keywords in self.task_type_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    identified_types.append(task_type)
                    break
        
        if not identified_types:
            identified_types.append(TaskType.ANALYTICAL)
        
        return list(set(identified_types))
    
    def _has_dependencies(self, text: str) -> bool:
        dependency_keywords = ["then", "after", "before", "first", "next", "finally"]
        return any(keyword in text for keyword in dependency_keywords)
    
    def _has_parallel_potential(self, text: str) -> bool:
        parallel_keywords = ["and", "also", "simultaneously", "concurrently", "multiple"]
        return any(keyword in text for keyword in parallel_keywords)
    
    def _has_decision_points(self, text: str) -> bool:
        decision_keywords = ["if", "when", "depending", "choose", "select", "decide"]
        return any(keyword in text for keyword in decision_keywords)
    
    def _needs_iteration(self, text: str) -> bool:
        iteration_keywords = ["until", "repeat", "iterate", "refine", "improve", "optimize"]
        return any(keyword in text for keyword in iteration_keywords)
    
    def _estimate_team_size(self, complexity: float, task_type_count: int) -> int:
        base_size = 1
        if complexity > 0.7:
            base_size += 1
        if task_type_count > 2:
            base_size += 1
        if complexity > 0.9 and task_type_count > 3:
            base_size += 1
        return base_size
    
    def _recommend_pattern(self, text: str, dependencies: bool, 
                          parallel: bool, conditional: bool, 
                          iterative: bool) -> WorkflowPattern:
        pattern_scores = {}
        
        # Calculate base scores from text indicators
        for pattern, indicators in self.pattern_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text)
            pattern_scores[pattern] = score
        
        # Enhanced logic for advanced patterns
        
        # Hierarchical pattern detection
        hierarchical_indicators = [
            "team", "teams", "manager", "lead", "coordinate", "oversee",
            "delegate", "manage", "supervise", "organize", "multiple teams",
            "different groups", "specialists", "experts", "roles"
        ]
        hierarchical_score = sum(1 for indicator in hierarchical_indicators if indicator in text)
        if hierarchical_score > 0:
            pattern_scores[WorkflowPattern.HIERARCHICAL] += hierarchical_score
            
        # Additional complexity-based hierarchical detection
        word_count = len(text.split())
        if word_count > 50:  # Complex requests may benefit from hierarchical approach
            pattern_scores[WorkflowPattern.HIERARCHICAL] += 1
            
        # Conditional pattern enhancement
        conditional_indicators = [
            "if", "when", "depending on", "based on", "choose", "select",
            "decide", "either", "or", "case", "scenario", "situation",
            "condition", "whether", "options", "alternatives"
        ]
        conditional_score = sum(1 for indicator in conditional_indicators if indicator in text)
        if conditional_score > 1:  # Multiple conditional indicators
            pattern_scores[WorkflowPattern.CONDITIONAL] += conditional_score
            
        # Iterative pattern enhancement
        iterative_indicators = [
            "until", "repeat", "iterate", "refine", "improve", "optimize",
            "enhance", "perfect", "quality", "better", "version", "revision",
            "feedback", "adjust", "modify", "polish"
        ]
        iterative_score = sum(1 for indicator in iterative_indicators if indicator in text)
        if iterative_score > 1:
            pattern_scores[WorkflowPattern.ITERATIVE] += iterative_score
        
        # Apply boolean-based scoring
        if dependencies and not parallel and not conditional:
            pattern_scores[WorkflowPattern.SEQUENTIAL] += 2
        if parallel and not dependencies and not conditional:
            pattern_scores[WorkflowPattern.PARALLEL] += 2
        if conditional:
            pattern_scores[WorkflowPattern.CONDITIONAL] += 2
        if iterative:
            pattern_scores[WorkflowPattern.ITERATIVE] += 2
            
        # Complex multi-pattern scenarios
        active_patterns = sum([dependencies, parallel, conditional, iterative])
        if active_patterns >= 3:
            return WorkflowPattern.HYBRID
            
        # High complexity with multiple task types suggests hierarchical
        complexity_score = self._calculate_complexity(text)
        task_types = self._identify_task_types(text)
        if complexity_score > 0.7 and len(task_types) > 2:
            pattern_scores[WorkflowPattern.HIERARCHICAL] += 2
            
        # Select highest scoring pattern
        if pattern_scores:
            max_score = max(pattern_scores.values())
            if max_score > 0:
                return max(pattern_scores.items(), key=lambda x: x[1])[0]
        
        return WorkflowPattern.SEQUENTIAL
    
    def _calculate_confidence(self, complexity: float, 
                            task_count: int, 
                            pattern: WorkflowPattern) -> float:
        base_confidence = 0.7
        
        if 0.3 <= complexity <= 0.8:
            base_confidence += 0.1
        
        if 1 <= task_count <= 3:
            base_confidence += 0.1
        
        if pattern != WorkflowPattern.HYBRID:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)