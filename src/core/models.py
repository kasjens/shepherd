from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class WorkflowPattern(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    ITERATIVE = "iterative"
    HIERARCHICAL = "hierarchical"
    EVENT_DRIVEN = "event_driven"
    HYBRID = "hybrid"


class TaskType(Enum):
    RESEARCH = "research"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    TECHNICAL = "technical"
    COMMUNICATION = "communication"


class ExecutionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PromptAnalysis:
    complexity_score: float
    urgency_score: float
    quality_requirements: float
    task_types: List[str]
    dependencies: bool
    parallel_potential: bool
    decision_points: bool
    iteration_needed: bool
    team_size_needed: int
    recommended_pattern: WorkflowPattern
    confidence: float


@dataclass
class ExecutionStep:
    id: str
    command: str
    description: str
    risk_level: str
    requires_confirmation: bool
    backup_command: Optional[str]
    rollback_command: Optional[str]
    status: ExecutionStatus
    output: str = ""
    error: str = ""
    execution_time: float = 0.0


@dataclass
class WorkflowResult:
    workflow_id: str
    pattern: WorkflowPattern
    status: ExecutionStatus
    steps: List[ExecutionStep]
    total_execution_time: float
    output: Dict[str, Any]
    errors: List[str]