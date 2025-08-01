from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..core.models import PromptAnalysis, WorkflowResult, ExecutionStep, ExecutionStatus
from ..agents.base_agent import BaseAgent
from ..utils.logger import get_logger
import time
import uuid


class BaseWorkflow(ABC):
    def __init__(self, analysis: PromptAnalysis, original_request: str = ""):
        self.analysis = analysis
        self.original_request = original_request
        self.workflow_id = str(uuid.uuid4())
        self.agents: List[BaseAgent] = []
        self.steps: List[ExecutionStep] = []
        self.start_time = None
        self.end_time = None
        self.project_folder: Optional[str] = None
        self.logger = get_logger(f'workflow.{self.__class__.__name__}')
        self.logger.debug(f"Workflow initialized: {self.workflow_id}")
    
    def set_project_folder(self, project_folder: str):
        """Set the project folder context for this workflow"""
        self.project_folder = project_folder
        self.logger.info(f"Project folder set: {project_folder}")
        
        # Pass project folder to all agents
        for agent in self.agents:
            if hasattr(agent, 'set_project_folder'):
                agent.set_project_folder(project_folder)
    
    @abstractmethod
    def create_agents(self) -> List[BaseAgent]:
        pass
    
    @abstractmethod
    def define_steps(self) -> List[ExecutionStep]:
        pass
    
    @abstractmethod
    def execute(self) -> WorkflowResult:
        pass
    
    def initialize(self):
        self.agents = self.create_agents()
        self.steps = self.define_steps()
    
    def get_execution_time(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def create_result(self, status: ExecutionStatus, 
                     output: Dict[str, Any], 
                     errors: List[str]) -> WorkflowResult:
        return WorkflowResult(
            workflow_id=self.workflow_id,
            pattern=self.analysis.recommended_pattern,
            status=status,
            steps=self.steps,
            total_execution_time=self.get_execution_time(),
            output=output,
            errors=errors
        )
    
    def log_progress(self, message: str):
        self.logger.info(f"[{self.workflow_id[:8]}] {message}")
        print(f"[{self.workflow_id[:8]}] {message}")