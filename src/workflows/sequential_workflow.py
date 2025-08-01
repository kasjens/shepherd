import time
from typing import List, Dict, Any
from .base_workflow import BaseWorkflow
from ..core.models import ExecutionStep, ExecutionStatus, WorkflowResult
from ..agents.base_agent import BaseAgent
from ..agents.agent_factory import AgentFactory


class SequentialWorkflow(BaseWorkflow):
    def __init__(self, analysis, original_request: str = ""):
        super().__init__(analysis, original_request)
        self.agent_factory = AgentFactory()
    
    def create_agents(self) -> List[BaseAgent]:
        agents = []
        
        for i, task_type in enumerate(self.analysis.task_types):
            agent = self.agent_factory.create_agent(
                task_type=task_type,
                name=f"Agent_{i}_{task_type}",
                complexity=self.analysis.complexity_score,
                request_text=self.original_request
            )
            agents.append(agent)
        
        return agents
    
    def define_steps(self) -> List[ExecutionStep]:
        steps = []
        
        for i, agent in enumerate(self.agents):
            step = ExecutionStep(
                id=f"step_{i}",
                command=f"execute_task_{agent.name}",
                description=f"Execute {agent.role} task",
                risk_level="low",
                requires_confirmation=False,
                backup_command=None,
                rollback_command=None,
                status=ExecutionStatus.PENDING
            )
            steps.append(step)
        
        return steps
    
    def execute(self) -> WorkflowResult:
        self.start_time = time.time()
        self.initialize()
        
        output = {}
        errors = []
        overall_status = ExecutionStatus.COMPLETED
        
        self.log_progress("Starting sequential workflow execution")
        
        for i, (step, agent) in enumerate(zip(self.steps, self.agents)):
            self.log_progress(f"Executing step {i+1}/{len(self.steps)}: {step.description}")
            
            step.status = ExecutionStatus.IN_PROGRESS
            step_start = time.time()
            
            try:
                # Pass the original request for better context
                task_with_context = f"{self.original_request} - {step.description}" if self.original_request else step.description
                result = agent.execute_task(task_with_context)
                
                if result["status"] == "completed":
                    step.status = ExecutionStatus.COMPLETED
                    step.output = result["output"]
                    output[f"step_{i}"] = result["output"]
                else:
                    step.status = ExecutionStatus.FAILED
                    step.error = result["error"]
                    errors.append(f"Step {i} failed: {result['error']}")
                    overall_status = ExecutionStatus.FAILED
                    
                    if not self._should_continue_on_error():
                        break
                
            except Exception as e:
                step.status = ExecutionStatus.FAILED
                step.error = str(e)
                errors.append(f"Step {i} exception: {str(e)}")
                overall_status = ExecutionStatus.FAILED
                
                if not self._should_continue_on_error():
                    break
            
            finally:
                step.execution_time = time.time() - step_start
        
        self.end_time = time.time()
        
        self.log_progress(f"Workflow completed with status: {overall_status.value}")
        
        return self.create_result(overall_status, output, errors)
    
    def _should_continue_on_error(self) -> bool:
        return False