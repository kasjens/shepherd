import time
import concurrent.futures
from typing import List, Dict, Any, Tuple
from .base_workflow import BaseWorkflow
from ..core.models import ExecutionStep, ExecutionStatus, WorkflowResult
from ..agents.base_agent import BaseAgent
from ..agents.task_agent import TaskAgent


class ParallelWorkflow(BaseWorkflow):
    def __init__(self, analysis):
        super().__init__(analysis)
        self.max_workers = min(len(analysis.task_types), 5)
    
    def create_agents(self) -> List[BaseAgent]:
        agents = []
        
        for i, task_type in enumerate(self.analysis.task_types):
            agent = TaskAgent(
                name=f"ParallelAgent_{i}_{task_type}",
                task_type=task_type,
                complexity=self.analysis.complexity_score
            )
            agents.append(agent)
        
        return agents
    
    def define_steps(self) -> List[ExecutionStep]:
        steps = []
        
        for i, agent in enumerate(self.agents):
            step = ExecutionStep(
                id=f"parallel_step_{i}",
                command=f"execute_parallel_task_{agent.name}",
                description=f"Execute {agent.role} task in parallel",
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
        
        self.log_progress(f"Starting parallel workflow execution with {len(self.agents)} agents")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_step = {}
            
            for step, agent in zip(self.steps, self.agents):
                step.status = ExecutionStatus.IN_PROGRESS
                future = executor.submit(self._execute_step, step, agent)
                future_to_step[future] = (step, agent)
            
            for future in concurrent.futures.as_completed(future_to_step):
                step, agent = future_to_step[future]
                
                try:
                    result, execution_time = future.result()
                    
                    if result["status"] == "completed":
                        step.status = ExecutionStatus.COMPLETED
                        step.output = result["output"]
                        output[step.id] = result["output"]
                        self.log_progress(f"Step {step.id} completed successfully")
                    else:
                        step.status = ExecutionStatus.FAILED
                        step.error = result["error"]
                        errors.append(f"Step {step.id} failed: {result['error']}")
                        overall_status = ExecutionStatus.FAILED
                        self.log_progress(f"Step {step.id} failed: {result['error']}")
                    
                    step.execution_time = execution_time
                    
                except Exception as e:
                    step.status = ExecutionStatus.FAILED
                    step.error = str(e)
                    errors.append(f"Step {step.id} exception: {str(e)}")
                    overall_status = ExecutionStatus.FAILED
                    self.log_progress(f"Step {step.id} exception: {str(e)}")
        
        self.end_time = time.time()
        
        self.log_progress(f"Parallel workflow completed with status: {overall_status.value}")
        
        return self.create_result(overall_status, output, errors)
    
    def _execute_step(self, step: ExecutionStep, agent: BaseAgent) -> Tuple[Dict[str, Any], float]:
        start_time = time.time()
        self.log_progress(f"Starting execution of {step.id}")
        
        result = agent.execute_task(step.description)
        
        execution_time = time.time() - start_time
        return result, execution_time