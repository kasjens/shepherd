import time
from typing import List, Dict, Any, Callable, Optional, Union
from .base_workflow import BaseWorkflow
from ..core.models import ExecutionStep, ExecutionStatus, WorkflowResult, WorkflowPattern
from ..agents.base_agent import BaseAgent
from ..agents.agent_factory import AgentFactory
from ..tools.base_tool import ToolResult


class ConditionalBranch:
    """Represents a conditional branch with its steps and execution condition"""
    
    def __init__(self, name: str, condition: Callable[[Dict[str, Any]], bool], 
                 steps: List[ExecutionStep], agents: List[BaseAgent]):
        self.name = name
        self.condition = condition
        self.steps = steps
        self.agents = agents


class ConditionalWorkflow(BaseWorkflow):
    """
    Workflow that executes different branches based on conditions evaluated
    from context, tool results, or agent outputs.
    """
    
    def __init__(self, analysis, original_request: str = ""):
        super().__init__(analysis, original_request)
        self.agent_factory = AgentFactory()
        self.branches: List[ConditionalBranch] = []
        self.context: Dict[str, Any] = {}
        self.default_branch: Optional[ConditionalBranch] = None
        self.evaluation_agents: List[BaseAgent] = []
        
    def add_context_evaluator(self, agent: BaseAgent):
        """Add an agent that will evaluate context and populate decision variables"""
        self.evaluation_agents.append(agent)
        
    def set_context(self, context: Dict[str, Any]):
        """Set initial context for condition evaluation"""
        self.context.update(context)
        
    def add_branch(self, name: str, condition: Callable[[Dict[str, Any]], bool], 
                   task_types: List[str], descriptions: List[str]):
        """Add a conditional branch with its task types and descriptions"""
        # Create agents for this branch
        branch_agents = []
        for i, (task_type, description) in enumerate(zip(task_types, descriptions)):
            agent = self.agent_factory.create_agent(
                task_type=task_type,
                name=f"{name}_agent_{i}_{task_type}",
                complexity=self.analysis.complexity_score,
                request_text=f"{self.original_request} - {description}"
            )
            branch_agents.append(agent)
        
        # Create steps for this branch
        branch_steps = []
        for i, (agent, description) in enumerate(zip(branch_agents, descriptions)):
            step = ExecutionStep(
                id=f"{name}_step_{i}",
                command=f"execute_task_{agent.name}",
                description=description,
                risk_level="medium",
                requires_confirmation=False,
                backup_command=None,
                rollback_command=None,
                status=ExecutionStatus.PENDING
            )
            branch_steps.append(step)
        
        branch = ConditionalBranch(name, condition, branch_steps, branch_agents)
        self.branches.append(branch)
        
    def add_default_branch(self, task_types: List[str], descriptions: List[str]):
        """Add a default branch that executes if no conditions are met"""
        self.add_branch("default", lambda ctx: True, task_types, descriptions)
        self.default_branch = self.branches[-1]
        
    def create_agents(self) -> List[BaseAgent]:
        """Create all agents needed for evaluation and execution"""
        all_agents = []
        
        # Add evaluation agents
        all_agents.extend(self.evaluation_agents)
        
        # Add agents from all branches
        for branch in self.branches:
            all_agents.extend(branch.agents)
            
        return all_agents
        
    def define_steps(self) -> List[ExecutionStep]:
        """Define steps - will be determined dynamically during execution"""
        # Create evaluation steps
        eval_steps = []
        for i, agent in enumerate(self.evaluation_agents):
            step = ExecutionStep(
                id=f"eval_step_{i}",
                command=f"evaluate_context_{agent.name}",
                description=f"Evaluate context using {agent.role}",
                risk_level="low",
                requires_confirmation=False,
                backup_command=None,
                rollback_command=None,
                status=ExecutionStatus.PENDING
            )
            eval_steps.append(step)
            
        return eval_steps
        
    def _evaluate_context(self) -> Dict[str, Any]:
        """Run evaluation agents to populate context for condition checking"""
        evaluation_results = {}
        
        for i, agent in enumerate(self.evaluation_agents):
            self.log_progress(f"Running context evaluation with {agent.name}")
            
            try:
                # Create evaluation task
                eval_task = f"""
                Analyze the following request and provide evaluation data:
                Request: {self.original_request}
                Current Context: {self.context}
                
                Provide analysis including:
                - Complexity assessment (low/medium/high)
                - Task characteristics and requirements
                - Technical considerations
                - Resource requirements
                - Risk factors
                
                Format your response as structured data that can guide workflow decisions.
                """
                
                result = agent.execute_task(eval_task)
                if result["status"] == "completed":
                    evaluation_results[f"evaluation_{i}"] = result["output"]
                    
                    # Extract key metrics from agent output
                    output_text = str(result["output"]).lower()
                    
                    # Simple pattern matching for common decision factors
                    if "high complexity" in output_text or "complex" in output_text:
                        self.context["complexity_level"] = "high"
                    elif "low complexity" in output_text or "simple" in output_text:
                        self.context["complexity_level"] = "low"
                    else:
                        self.context["complexity_level"] = "medium"
                        
                    if "urgent" in output_text or "critical" in output_text:
                        self.context["urgency"] = "high"
                    elif "low priority" in output_text:
                        self.context["urgency"] = "low"
                    else:
                        self.context["urgency"] = "medium"
                        
                    if "security" in output_text or "risk" in output_text:
                        self.context["security_sensitive"] = True
                    
                    if "data" in output_text or "analysis" in output_text:
                        self.context["data_intensive"] = True
                        
                    if "creative" in output_text or "design" in output_text:
                        self.context["creative_task"] = True
                        
            except Exception as e:
                self.log_progress(f"Evaluation failed for {agent.name}: {str(e)}")
                evaluation_results[f"evaluation_{i}_error"] = str(e)
        
        # Update context with evaluation results
        self.context.update(evaluation_results)
        return self.context
        
    def _select_branch(self) -> Optional[ConditionalBranch]:
        """Evaluate conditions and select the appropriate branch"""
        self.log_progress("Evaluating branch conditions")
        
        for branch in self.branches:
            if branch == self.default_branch:
                continue  # Skip default branch in main evaluation
                
            try:
                if branch.condition(self.context):
                    self.log_progress(f"Selected branch: {branch.name}")
                    return branch
            except Exception as e:
                self.log_progress(f"Error evaluating condition for {branch.name}: {str(e)}")
                
        # If no conditions match, use default branch
        if self.default_branch:
            self.log_progress(f"No conditions matched, using default branch: {self.default_branch.name}")
            return self.default_branch
            
        self.log_progress("No branches available for execution")
        return None
        
    def execute(self) -> WorkflowResult:
        """Execute the conditional workflow"""
        self.start_time = time.time()
        self.initialize()
        
        output = {"workflow_type": "conditional", "context": {}}
        errors = []
        overall_status = ExecutionStatus.COMPLETED
        
        self.log_progress("Starting conditional workflow execution")
        
        try:
            # Step 1: Run context evaluation
            if self.evaluation_agents:
                self.log_progress("Running context evaluation phase")
                self.context = self._evaluate_context()
                output["context"] = self.context.copy()
            
            # Step 2: Select branch based on conditions
            selected_branch = self._select_branch()
            
            if not selected_branch:
                errors.append("No branch could be selected for execution")
                overall_status = ExecutionStatus.FAILED
            else:
                output["selected_branch"] = selected_branch.name
                
                # Step 3: Execute selected branch
                self.log_progress(f"Executing branch: {selected_branch.name}")
                branch_results = self._execute_branch(selected_branch)
                
                output.update(branch_results)
                
                # Check if branch execution was successful
                if any(step.status == ExecutionStatus.FAILED for step in selected_branch.steps):
                    overall_status = ExecutionStatus.FAILED
                    errors.extend([step.error for step in selected_branch.steps if step.error])
                
        except Exception as e:
            errors.append(f"Conditional workflow execution failed: {str(e)}")
            overall_status = ExecutionStatus.FAILED
            
        self.end_time = time.time()
        
        self.log_progress(f"Conditional workflow completed with status: {overall_status.value}")
        
        return self.create_result(overall_status, output, errors)
        
    def _execute_branch(self, branch: ConditionalBranch) -> Dict[str, Any]:
        """Execute a specific branch"""
        branch_output = {}
        
        for i, (step, agent) in enumerate(zip(branch.steps, branch.agents)):
            self.log_progress(f"Executing {branch.name} step {i+1}/{len(branch.steps)}: {step.description}")
            
            step.status = ExecutionStatus.IN_PROGRESS
            step_start = time.time()
            
            try:
                # Create task with context and branch-specific information
                task_with_context = f"""
                Branch: {branch.name}
                Context: {self.context}
                Original Request: {self.original_request}
                Step Description: {step.description}
                
                Execute this step considering the above context and branch selection.
                """
                
                result = agent.execute_task(task_with_context)
                
                if result["status"] == "completed":
                    step.status = ExecutionStatus.COMPLETED
                    step.output = result["output"]
                    branch_output[f"{branch.name}_step_{i}"] = result["output"]
                else:
                    step.status = ExecutionStatus.FAILED
                    step.error = result.get("error", "Unknown error")
                    
            except Exception as e:
                step.status = ExecutionStatus.FAILED
                step.error = str(e)
                
            finally:
                step.execution_time = time.time() - step_start
                
        return branch_output


# Common condition functions for reuse
class ConditionFunctions:
    """Common condition functions for conditional workflows"""
    
    @staticmethod
    def complexity_high(context: Dict[str, Any]) -> bool:
        """Check if task complexity is high"""
        return context.get("complexity_level") == "high"
        
    @staticmethod
    def complexity_low(context: Dict[str, Any]) -> bool:
        """Check if task complexity is low"""
        return context.get("complexity_level") == "low"
        
    @staticmethod
    def urgency_high(context: Dict[str, Any]) -> bool:
        """Check if task urgency is high"""
        return context.get("urgency") == "high"
        
    @staticmethod
    def security_sensitive(context: Dict[str, Any]) -> bool:
        """Check if task involves security considerations"""
        return context.get("security_sensitive", False)
        
    @staticmethod
    def data_intensive(context: Dict[str, Any]) -> bool:
        """Check if task is data-intensive"""
        return context.get("data_intensive", False)
        
    @staticmethod
    def creative_task(context: Dict[str, Any]) -> bool:
        """Check if task requires creative work"""
        return context.get("creative_task", False)
        
    @staticmethod
    def has_project_folder(context: Dict[str, Any]) -> bool:
        """Check if a project folder is available"""
        return "project_folder" in context and context["project_folder"] is not None