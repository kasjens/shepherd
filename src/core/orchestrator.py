from typing import Dict, Any, Optional
from .prompt_analyzer import PromptAnalyzer
from .workflow_selector import WorkflowSelector
from .models import PromptAnalysis, WorkflowResult, ExecutionStatus
from ..agents.agent_factory import AgentFactory
from ..utils.logger import get_logger, log_prompt_analysis, log_workflow_start, log_workflow_end


class IntelligentOrchestrator:
    def __init__(self):
        self.logger = get_logger('orchestrator')
        self.prompt_analyzer = PromptAnalyzer()
        self.workflow_selector = WorkflowSelector()
        self.agent_factory = AgentFactory()
        self.logger.info("IntelligentOrchestrator initialized")
    
    def analyze_prompt(self, user_request: str) -> PromptAnalysis:
        self.logger.info(f"Analyzing prompt: {user_request[:100]}...")
        analysis = self.prompt_analyzer.analyze_prompt(user_request)
        log_prompt_analysis(user_request, analysis)
        return analysis
    
    def create_workflow(self, analysis: PromptAnalysis, original_request: str = ""):
        self.logger.info(f"Creating workflow with pattern: {analysis.recommended_pattern.value}")
        workflow = self.workflow_selector.select_workflow(analysis, original_request)
        self.logger.debug(f"Workflow created: {type(workflow).__name__}")
        return workflow
    
    def execute_request(self, user_request: str) -> WorkflowResult:
        self.logger.info(f"Starting request execution: {user_request[:50]}...")
        
        try:
            analysis = self.analyze_prompt(user_request)
            
            print(f"\n=== Prompt Analysis ===")
            print(f"Complexity: {analysis.complexity_score:.2f}")
            print(f"Urgency: {analysis.urgency_score:.2f}")
            print(f"Quality Requirements: {analysis.quality_requirements:.2f}")
            print(f"Task Types: {', '.join(analysis.task_types)}")
            print(f"Recommended Pattern: {analysis.recommended_pattern.value}")
            print(f"Team Size Needed: {analysis.team_size_needed}")
            print(f"Confidence: {analysis.confidence:.2f}")
            
            workflow = self.create_workflow(analysis, user_request)
            log_workflow_start(workflow.workflow_id, analysis.recommended_pattern, analysis)
            
            print(f"\n=== Executing {analysis.recommended_pattern.value} Workflow ===")
            
            result = workflow.execute()
            log_workflow_end(workflow.workflow_id, result.status, result.total_execution_time, result.errors)
            
            self.logger.info(f"Request execution completed with status: {result.status.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"Request execution failed: {str(e)}", exc_info=True)
            raise
    
    def execute_interactive(self, user_request: str, 
                          confirm_steps: bool = True) -> WorkflowResult:
        analysis = self.analyze_prompt(user_request)
        workflow = self.create_workflow(analysis, user_request)
        
        if confirm_steps:
            workflow.initialize()
            print(f"\n=== Workflow Plan ===")
            print(f"Pattern: {analysis.recommended_pattern.value}")
            print(f"Steps to execute: {len(workflow.steps)}")
            
            for i, step in enumerate(workflow.steps):
                print(f"{i+1}. {step.description}")
            
            response = input("\nProceed with execution? (y/n): ")
            if response.lower() != 'y':
                print("Execution cancelled by user")
                return workflow.create_result(
                    ExecutionStatus.CANCELLED,
                    {},
                    ["User cancelled execution"]
                )
        
        return workflow.execute()