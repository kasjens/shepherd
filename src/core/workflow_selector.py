from typing import Dict, Any, List
from .models import PromptAnalysis, WorkflowPattern
from ..workflows.sequential_workflow import SequentialWorkflow
from ..workflows.parallel_workflow import ParallelWorkflow
from ..workflows.base_workflow import BaseWorkflow


class WorkflowSelector:
    def __init__(self):
        self.workflow_registry = {
            WorkflowPattern.SEQUENTIAL: SequentialWorkflow,
            WorkflowPattern.PARALLEL: ParallelWorkflow,
        }
    
    def select_workflow(self, analysis: PromptAnalysis) -> BaseWorkflow:
        pattern = analysis.recommended_pattern
        
        if pattern in self.workflow_registry:
            workflow_class = self.workflow_registry[pattern]
        else:
            workflow_class = self.workflow_registry[WorkflowPattern.SEQUENTIAL]
        
        return workflow_class(analysis)
    
    def get_workflow_config(self, pattern: WorkflowPattern) -> Dict[str, Any]:
        configs = {
            WorkflowPattern.SEQUENTIAL: {
                "max_steps": 10,
                "timeout_per_step": 60,
                "allow_rollback": True,
                "description": "Execute tasks one after another in order"
            },
            WorkflowPattern.PARALLEL: {
                "max_concurrent": 5,
                "timeout_total": 300,
                "coordination_strategy": "wait_all",
                "description": "Execute multiple tasks simultaneously"
            },
            WorkflowPattern.CONDITIONAL: {
                "max_branches": 5,
                "evaluation_timeout": 30,
                "default_branch": True,
                "description": "Execute different paths based on conditions"
            },
            WorkflowPattern.ITERATIVE: {
                "max_iterations": 10,
                "convergence_threshold": 0.95,
                "timeout_per_iteration": 120,
                "description": "Repeat tasks until quality criteria met"
            },
            WorkflowPattern.HIERARCHICAL: {
                "max_depth": 3,
                "delegation_strategy": "capability_based",
                "coordination_overhead": 0.2,
                "description": "Coordinate teams of specialized agents"
            }
        }
        
        return configs.get(pattern, configs[WorkflowPattern.SEQUENTIAL])
    
    def estimate_execution_time(self, analysis: PromptAnalysis) -> float:
        base_time = 10.0
        
        complexity_factor = analysis.complexity_score * 50
        team_factor = analysis.team_size_needed * 5
        
        pattern_multipliers = {
            WorkflowPattern.SEQUENTIAL: 1.0,
            WorkflowPattern.PARALLEL: 0.5,
            WorkflowPattern.CONDITIONAL: 1.2,
            WorkflowPattern.ITERATIVE: 2.0,
            WorkflowPattern.HIERARCHICAL: 1.5,
            WorkflowPattern.HYBRID: 2.5
        }
        
        pattern_multiplier = pattern_multipliers.get(
            analysis.recommended_pattern, 1.0
        )
        
        estimated_time = (base_time + complexity_factor + team_factor) * pattern_multiplier
        
        return round(estimated_time, 1)