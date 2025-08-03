import time
from typing import List, Dict, Any, Callable, Optional
from .base_workflow import BaseWorkflow
from ..core.models import ExecutionStep, ExecutionStatus, WorkflowResult, WorkflowPattern
from ..agents.base_agent import BaseAgent
from ..agents.agent_factory import AgentFactory


class IterationResult:
    """Result of a single iteration"""
    
    def __init__(self, iteration_number: int, output: Dict[str, Any], 
                 quality_score: float, converged: bool, errors: List[str] = None):
        self.iteration_number = iteration_number
        self.output = output
        self.quality_score = quality_score
        self.converged = converged
        self.errors = errors or []
        self.timestamp = time.time()


class IterativeWorkflow(BaseWorkflow):
    """
    Workflow that repeats execution until convergence criteria are met
    or maximum iterations reached. Includes quality assessment and improvement.
    """
    
    def __init__(self, analysis, original_request: str = "", max_iterations: int = 5):
        super().__init__(analysis, original_request)
        self.agent_factory = AgentFactory()
        self.max_iterations = max_iterations
        self.quality_threshold = 0.8  # Quality score threshold for convergence
        self.convergence_function: Optional[Callable[[List[IterationResult]], bool]] = None
        self.quality_assessor: Optional[BaseAgent] = None
        self.iteration_results: List[IterationResult] = []
        self.improvement_agents: List[BaseAgent] = []
        
    def set_convergence_function(self, func: Callable[[List[IterationResult]], bool]):
        """Set custom convergence function"""
        self.convergence_function = func
        
    def set_quality_threshold(self, threshold: float):
        """Set quality threshold for convergence (0.0 to 1.0)"""
        self.quality_threshold = max(0.0, min(1.0, threshold))
        
    def add_quality_assessor(self, agent: BaseAgent):
        """Add agent that will assess quality of iteration results"""
        self.quality_assessor = agent
        
    def add_improvement_agent(self, agent: BaseAgent):
        """Add agent that will improve results based on previous iterations"""
        self.improvement_agents.append(agent)
        
    def create_agents(self) -> List[BaseAgent]:
        """Create agents for iterative execution"""
        agents = []
        
        # Create main execution agents
        for i, task_type in enumerate(self.analysis.task_types):
            agent = self.agent_factory.create_agent(
                task_type=task_type,
                name=f"Iteration_Agent_{i}_{task_type}",
                complexity=self.analysis.complexity_score,
                request_text=self.original_request
            )
            agents.append(agent)
            
        # Add quality assessor if provided
        if self.quality_assessor:
            agents.append(self.quality_assessor)
            
        # Add improvement agents
        agents.extend(self.improvement_agents)
        
        return agents
        
    def define_steps(self) -> List[ExecutionStep]:
        """Define steps for one iteration - will be repeated"""
        steps = []
        
        # Main execution steps
        main_agents = [a for a in self.agents if a != self.quality_assessor and a not in self.improvement_agents]
        
        for i, agent in enumerate(main_agents):
            step = ExecutionStep(
                id=f"iteration_step_{i}",
                command=f"execute_iteration_task_{agent.name}",
                description=f"Execute {agent.role} iteration task",
                risk_level="medium",
                requires_confirmation=False,
                backup_command=None,
                rollback_command=None,
                status=ExecutionStatus.PENDING
            )
            steps.append(step)
            
        # Quality assessment step
        if self.quality_assessor:
            quality_step = ExecutionStep(
                id="quality_assessment",
                command=f"assess_quality_{self.quality_assessor.name}",
                description="Assess quality of iteration results",
                risk_level="low",
                requires_confirmation=False,
                backup_command=None,
                rollback_command=None,
                status=ExecutionStatus.PENDING
            )
            steps.append(quality_step)
            
        return steps
        
    def _assess_quality(self, iteration_output: Dict[str, Any]) -> float:
        """Assess quality of iteration output"""
        if not self.quality_assessor:
            # Default quality assessment based on output completeness
            return self._default_quality_assessment(iteration_output)
            
        try:
            assessment_task = f"""
            Assess the quality of the following iteration output on a scale from 0.0 to 1.0:
            
            Original Request: {self.original_request}
            Iteration Output: {iteration_output}
            
            Consider factors such as:
            - Completeness of the solution
            - Accuracy and correctness
            - Clarity and usability
            - Adherence to requirements
            - Overall effectiveness
            
            Provide a single quality score between 0.0 and 1.0, where:
            - 0.0-0.3: Poor quality, major issues
            - 0.4-0.6: Acceptable quality, some improvements needed
            - 0.7-0.8: Good quality, minor improvements possible
            - 0.9-1.0: Excellent quality, minimal improvements needed
            
            Format: "Quality Score: X.X"
            """
            
            result = self.quality_assessor.execute_task(assessment_task)
            
            if result["status"] == "completed":
                output_text = str(result["output"]).lower()
                
                # Extract quality score from output
                import re
                score_match = re.search(r"quality score:?\s*([0-9]*\.?[0-9]+)", output_text)
                if score_match:
                    score = float(score_match.group(1))
                    return max(0.0, min(1.0, score))  # Clamp to valid range
                    
                # Fallback: analyze text for quality indicators
                if "excellent" in output_text or "outstanding" in output_text:
                    return 0.9
                elif "good" in output_text or "satisfactory" in output_text:
                    return 0.7
                elif "acceptable" in output_text or "adequate" in output_text:
                    return 0.6
                elif "poor" in output_text or "inadequate" in output_text:
                    return 0.3
                else:
                    return 0.5  # Neutral score
                    
        except Exception as e:
            self.log_progress(f"Quality assessment failed: {str(e)}")
            
        return self._default_quality_assessment(iteration_output)
        
    def _default_quality_assessment(self, iteration_output: Dict[str, Any]) -> float:
        """Default quality assessment based on output characteristics"""
        if not iteration_output:
            return 0.1
            
        # Simple heuristic based on output richness
        score = 0.5  # Base score
        
        # Check for multiple successful steps
        successful_steps = sum(1 for key, value in iteration_output.items() 
                             if key.startswith("step_") and value)
        if successful_steps > 1:
            score += 0.2
            
        # Check for detailed output
        total_output_length = sum(len(str(value)) for value in iteration_output.values())
        if total_output_length > 500:  # Substantial output
            score += 0.2
            
        # Check for error indicators
        output_text = str(iteration_output).lower()
        if "error" in output_text or "failed" in output_text:
            score -= 0.3
            
        return max(0.0, min(1.0, score))
        
    def _check_convergence(self) -> bool:
        """Check if convergence criteria are met"""
        if not self.iteration_results:
            return False
            
        # Use custom convergence function if provided
        if self.convergence_function:
            try:
                return self.convergence_function(self.iteration_results)
            except Exception as e:
                self.log_progress(f"Custom convergence function failed: {str(e)}")
                
        # Default convergence logic
        latest_result = self.iteration_results[-1]
        
        # Check if quality threshold is met
        if latest_result.quality_score >= self.quality_threshold:
            self.log_progress(f"Quality threshold met: {latest_result.quality_score:.2f} >= {self.quality_threshold}")
            return True
            
        # Check for quality improvement plateau (last 2 iterations show minimal improvement)
        if len(self.iteration_results) >= 2:
            prev_quality = self.iteration_results[-2].quality_score
            current_quality = latest_result.quality_score
            improvement = current_quality - prev_quality
            
            if improvement < 0.05:  # Less than 5% improvement
                self.log_progress(f"Quality improvement plateau detected: {improvement:.3f}")
                return True
                
        return False
        
    def _get_improvement_feedback(self, iteration_results: List[IterationResult]) -> str:
        """Get feedback for improvement from improvement agents"""
        if not self.improvement_agents or not iteration_results:
            return "Continue with similar approach but focus on improving quality."
            
        feedback_parts = []
        
        for agent in self.improvement_agents:
            try:
                # Prepare iteration history for analysis
                history_summary = []
                for i, result in enumerate(iteration_results[-3:]):  # Last 3 iterations
                    history_summary.append(f"Iteration {result.iteration_number}: Quality {result.quality_score:.2f}")
                    
                feedback_task = f"""
                Analyze the iteration history and provide specific improvement recommendations:
                
                Original Request: {self.original_request}
                Iteration History: {history_summary}
                Latest Output: {iteration_results[-1].output}
                Current Quality Score: {iteration_results[-1].quality_score:.2f}
                Target Quality: {self.quality_threshold}
                
                Provide specific, actionable recommendations for improving the next iteration.
                Focus on what could be done differently or better.
                """
                
                result = agent.execute_task(feedback_task)
                if result["status"] == "completed":
                    feedback_parts.append(f"{agent.role} feedback: {result['output']}")
                    
            except Exception as e:
                self.log_progress(f"Failed to get feedback from {agent.name}: {str(e)}")
                
        if feedback_parts:
            return "\n".join(feedback_parts)
        else:
            return "Focus on addressing any quality issues and improving completeness."
            
    def _execute_iteration(self, iteration_number: int) -> IterationResult:
        """Execute a single iteration"""
        self.log_progress(f"Starting iteration {iteration_number}")
        
        iteration_output = {}
        iteration_errors = []
        
        # Get improvement feedback from previous iterations
        improvement_feedback = ""
        if self.iteration_results:
            improvement_feedback = self._get_improvement_feedback(self.iteration_results)
            
        # Execute main steps
        main_agents = [a for a in self.agents if a != self.quality_assessor and a not in self.improvement_agents]
        
        for i, (step, agent) in enumerate(zip(self.steps[:-1] if self.quality_assessor else self.steps, main_agents)):
            step.status = ExecutionStatus.IN_PROGRESS
            step_start = time.time()
            
            try:
                # Create iteration-specific task
                task_context = f"""
                Iteration {iteration_number}/{self.max_iterations}
                Original Request: {self.original_request}
                
                Previous iterations summary: {len(self.iteration_results)} completed
                """
                
                if improvement_feedback:
                    task_context += f"\nImprovement feedback: {improvement_feedback}"
                    
                if self.iteration_results:
                    task_context += f"\nPrevious quality score: {self.iteration_results[-1].quality_score:.2f}"
                    task_context += f"\nTarget quality: {self.quality_threshold}"
                    
                result = agent.execute_task(task_context)
                
                if result["status"] == "completed":
                    step.status = ExecutionStatus.COMPLETED
                    step.output = result["output"]
                    iteration_output[f"step_{i}"] = result["output"]
                else:
                    step.status = ExecutionStatus.FAILED
                    step.error = result.get("error", "Unknown error")
                    iteration_errors.append(step.error)
                    
            except Exception as e:
                step.status = ExecutionStatus.FAILED
                step.error = str(e)
                iteration_errors.append(str(e))
                
            finally:
                step.execution_time = time.time() - step_start
                
        # Assess quality
        quality_score = self._assess_quality(iteration_output)
        
        # Check for convergence
        converged = False
        if iteration_number > 1:  # Can't converge on first iteration
            # Temporarily add this result to check convergence
            temp_result = IterationResult(iteration_number, iteration_output, quality_score, False, iteration_errors)
            self.iteration_results.append(temp_result)
            converged = self._check_convergence()
            self.iteration_results.pop()  # Remove temporary result
            
        return IterationResult(iteration_number, iteration_output, quality_score, converged, iteration_errors)
        
    def execute(self) -> WorkflowResult:
        """Execute the iterative workflow"""
        self.start_time = time.time()
        self.initialize()
        
        output = {
            "workflow_type": "iterative",
            "max_iterations": self.max_iterations,
            "quality_threshold": self.quality_threshold,
            "iterations": []
        }
        errors = []
        overall_status = ExecutionStatus.COMPLETED
        
        self.log_progress(f"Starting iterative workflow (max {self.max_iterations} iterations)")
        
        try:
            for iteration_num in range(1, self.max_iterations + 1):
                # Reset step statuses for new iteration
                for step in self.steps:
                    step.status = ExecutionStatus.PENDING
                    
                # Execute iteration
                iteration_result = self._execute_iteration(iteration_num)
                self.iteration_results.append(iteration_result)
                
                # Add to output
                iteration_summary = {
                    "iteration": iteration_num,
                    "quality_score": iteration_result.quality_score,
                    "converged": iteration_result.converged,
                    "output": iteration_result.output,
                    "errors": iteration_result.errors
                }
                output["iterations"].append(iteration_summary)
                
                # Collect errors
                errors.extend(iteration_result.errors)
                
                self.log_progress(f"Iteration {iteration_num} completed. Quality: {iteration_result.quality_score:.2f}")
                
                # Check for convergence
                if iteration_result.converged:
                    self.log_progress(f"Convergence achieved after {iteration_num} iterations")
                    output["converged"] = True
                    output["convergence_iteration"] = iteration_num
                    break
                    
            else:
                # Max iterations reached without convergence
                self.log_progress(f"Max iterations ({self.max_iterations}) reached without convergence")
                output["converged"] = False
                
            # Set final results
            if self.iteration_results:
                output["final_quality_score"] = self.iteration_results[-1].quality_score
                output["final_output"] = self.iteration_results[-1].output
                output["total_iterations"] = len(self.iteration_results)
                
                # Determine overall status
                if self.iteration_results[-1].quality_score >= self.quality_threshold:
                    overall_status = ExecutionStatus.COMPLETED
                elif errors:
                    overall_status = ExecutionStatus.FAILED
                else:
                    overall_status = ExecutionStatus.COMPLETED  # Completed but may not meet quality threshold
            else:
                overall_status = ExecutionStatus.FAILED
                errors.append("No iterations completed successfully")
                
        except Exception as e:
            errors.append(f"Iterative workflow execution failed: {str(e)}")
            overall_status = ExecutionStatus.FAILED
            
        self.end_time = time.time()
        
        self.log_progress(f"Iterative workflow completed with status: {overall_status.value}")
        
        return self.create_result(overall_status, output, errors)


# Common convergence functions
class ConvergenceFunctions:
    """Common convergence functions for iterative workflows"""
    
    @staticmethod
    def quality_threshold(threshold: float) -> Callable[[List[IterationResult]], bool]:
        """Converge when quality threshold is reached"""
        def check(results: List[IterationResult]) -> bool:
            return bool(results and results[-1].quality_score >= threshold)
        return check
        
    @staticmethod
    def stable_quality(min_iterations: int = 2, stability_threshold: float = 0.05) -> Callable[[List[IterationResult]], bool]:
        """Converge when quality is stable across iterations"""
        def check(results: List[IterationResult]) -> bool:
            if len(results) < min_iterations:
                return False
            recent_scores = [r.quality_score for r in results[-min_iterations:]]
            return max(recent_scores) - min(recent_scores) <= stability_threshold
        return check
        
    @staticmethod
    def diminishing_returns(min_improvement: float = 0.02) -> Callable[[List[IterationResult]], bool]:
        """Converge when improvement between iterations is minimal"""
        def check(results: List[IterationResult]) -> bool:
            if len(results) < 2:
                return False
            improvement = results[-1].quality_score - results[-2].quality_score
            return improvement <= min_improvement
        return check