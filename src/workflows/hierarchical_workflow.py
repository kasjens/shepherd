import time
import asyncio
from typing import List, Dict, Any, Optional
from .base_workflow import BaseWorkflow
from ..core.models import ExecutionStep, ExecutionStatus, WorkflowResult, WorkflowPattern, TaskType
from ..agents.base_agent import BaseAgent
from ..agents.agent_factory import AgentFactory


class TeamStructure:
    """Represents a hierarchical team structure with manager and subordinates"""
    
    def __init__(self, manager: BaseAgent, team_name: str):
        self.manager = manager
        self.team_name = team_name
        self.specialists: List[BaseAgent] = []
        self.sub_teams: List['TeamStructure'] = []
        
    def add_specialist(self, agent: BaseAgent):
        """Add a specialist agent to this team"""
        self.specialists.append(agent)
        
    def add_sub_team(self, sub_team: 'TeamStructure'):
        """Add a sub-team under this team"""
        self.sub_teams.append(sub_team)
        
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all agents in this team hierarchy"""
        agents = [self.manager] + self.specialists
        for sub_team in self.sub_teams:
            agents.extend(sub_team.get_all_agents())
        return agents


class TaskDelegation:
    """Represents a task delegation from manager to subordinate"""
    
    def __init__(self, task_id: str, description: str, assigned_to: BaseAgent, 
                 priority: str = "medium", dependencies: List[str] = None):
        self.task_id = task_id
        self.description = description
        self.assigned_to = assigned_to
        self.priority = priority
        self.dependencies = dependencies or []
        self.status = ExecutionStatus.PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None


class HierarchicalWorkflow(BaseWorkflow):
    """
    Workflow that uses hierarchical delegation with manager agents coordinating
    specialized teams and individual agents.
    """
    
    def __init__(self, analysis, original_request: str = ""):
        super().__init__(analysis, original_request)
        self.agent_factory = AgentFactory()
        self.root_team: Optional[TeamStructure] = None
        self.delegations: List[TaskDelegation] = []
        self.coordination_results: Dict[str, Any] = {}
        
    def create_team_structure(self) -> TeamStructure:
        """Create hierarchical team structure based on task analysis"""
        # Create executive manager for overall coordination
        executive_manager = self.agent_factory.create_agent(
            task_type="analytical",
            name="Executive_Manager",
            complexity=self.analysis.complexity_score,
            request_text=f"Coordinate and manage: {self.original_request}"
        )
        
        root_team = TeamStructure(executive_manager, "Executive_Team")
        
        # Determine team structure based on task complexity and types
        task_types = self.analysis.task_types
        complexity = self.analysis.complexity_score
        
        if complexity > 0.7 and len(task_types) > 2:
            # High complexity: Create specialized teams with team leads
            self._create_specialized_teams(root_team, task_types)
        elif len(task_types) > 1:
            # Medium complexity: Create team leads with specialists
            self._create_team_leads(root_team, task_types)
        else:
            # Simple structure: Direct specialists under manager
            self._create_direct_specialists(root_team, task_types)
            
        return root_team
        
    def _create_specialized_teams(self, root_team: TeamStructure, task_types: List[str]):
        """Create specialized teams for complex workflows"""
        team_configs = {
            "research": ["research", "analytical"],
            "technical": ["technical"],
            "creative": ["creative", "communication"],
        }
        
        for team_name, team_task_types in team_configs.items():
            if any(task_type in task_types for task_type in team_task_types):
                # Create team lead
                team_lead = self.agent_factory.create_agent(
                    task_type=team_task_types[0],
                    name=f"{team_name.title()}_Team_Lead",
                    complexity=self.analysis.complexity_score,
                    request_text=f"Lead {team_name} team for: {self.original_request}"
                )
                
                team = TeamStructure(team_lead, f"{team_name.title()}_Team")
                
                # Add specialists to team
                for task_type in team_task_types:
                    if task_type in task_types:
                        specialist = self.agent_factory.create_agent(
                            task_type=task_type,
                            name=f"{team_name.title()}_Specialist_{task_type}",
                            complexity=self.analysis.complexity_score,
                            request_text=f"Specialize in {task_type} for: {self.original_request}"
                        )
                        team.add_specialist(specialist)
                        
                root_team.add_sub_team(team)
                
    def _create_team_leads(self, root_team: TeamStructure, task_types: List[str]):
        """Create team leads with specialists for medium complexity"""
        for i, task_type in enumerate(task_types):
            team_lead = self.agent_factory.create_agent(
                task_type=task_type,
                name=f"Team_Lead_{i}_{task_type}",
                complexity=self.analysis.complexity_score,
                request_text=f"Lead {task_type} work for: {self.original_request}"
            )
            
            team = TeamStructure(team_lead, f"Team_{i}_{task_type}")
            
            # Add 1-2 specialists per team
            num_specialists = 2 if self.analysis.complexity_score > 0.5 else 1
            for j in range(num_specialists):
                specialist = self.agent_factory.create_agent(
                    task_type=task_type,
                    name=f"Specialist_{i}_{j}_{task_type}",
                    complexity=self.analysis.complexity_score,
                    request_text=f"Execute {task_type} tasks for: {self.original_request}"
                )
                team.add_specialist(specialist)
                
            root_team.add_sub_team(team)
            
    def _create_direct_specialists(self, root_team: TeamStructure, task_types: List[str]):
        """Create specialists directly under manager for simple workflows"""
        for i, task_type in enumerate(task_types):
            specialist = self.agent_factory.create_agent(
                task_type=task_type,
                name=f"Specialist_{i}_{task_type}",
                complexity=self.analysis.complexity_score,
                request_text=f"Execute {task_type} tasks for: {self.original_request}"
            )
            root_team.add_specialist(specialist)
            
    def create_agents(self) -> List[BaseAgent]:
        """Create all agents in the hierarchical structure"""
        if not self.root_team:
            self.root_team = self.create_team_structure()
        return self.root_team.get_all_agents()
        
    def define_steps(self) -> List[ExecutionStep]:
        """Define hierarchical execution steps"""
        steps = []
        
        # Step 1: Executive planning
        planning_step = ExecutionStep(
            id="executive_planning",
            command="create_execution_plan",
            description="Executive manager creates detailed execution plan",
            risk_level="low",
            requires_confirmation=False,
            backup_command=None,
            rollback_command=None,
            status=ExecutionStatus.PENDING
        )
        steps.append(planning_step)
        
        # Step 2: Task delegation
        delegation_step = ExecutionStep(
            id="task_delegation",
            command="delegate_tasks",
            description="Delegate tasks to team leads and specialists",
            risk_level="medium",
            requires_confirmation=False,
            backup_command=None,
            rollback_command=None,
            status=ExecutionStatus.PENDING
        )
        steps.append(delegation_step)
        
        # Step 3: Parallel team execution
        execution_step = ExecutionStep(
            id="team_execution",
            command="execute_team_tasks",
            description="Teams execute delegated tasks in parallel",
            risk_level="medium",
            requires_confirmation=False,
            backup_command=None,
            rollback_command=None,
            status=ExecutionStatus.PENDING
        )
        steps.append(execution_step)
        
        # Step 4: Results coordination
        coordination_step = ExecutionStep(
            id="results_coordination",
            command="coordinate_results",
            description="Coordinate and integrate team results",
            risk_level="medium",
            requires_confirmation=False,
            backup_command=None,
            rollback_command=None,
            status=ExecutionStatus.PENDING
        )
        steps.append(coordination_step)
        
        # Step 5: Final synthesis
        synthesis_step = ExecutionStep(
            id="final_synthesis",
            command="synthesize_final_result",
            description="Executive manager synthesizes final result",
            risk_level="low",
            requires_confirmation=False,
            backup_command=None,
            rollback_command=None,
            status=ExecutionStatus.PENDING
        )
        steps.append(synthesis_step)
        
        return steps
        
    def _create_execution_plan(self) -> Dict[str, Any]:
        """Executive manager creates detailed execution plan"""
        self.log_progress("Creating executive execution plan")
        
        planning_task = f"""
        As the executive manager, create a detailed execution plan for this request:
        
        Original Request: {self.original_request}
        Available Teams: {[team.team_name for team in self.root_team.sub_teams] if self.root_team.sub_teams else ["Direct specialists"]}
        Task Types: {self.analysis.task_types}
        Complexity Score: {self.analysis.complexity_score}
        
        Create a plan that includes:
        1. Breakdown of the request into specific tasks
        2. Assignment of tasks to appropriate teams/specialists
        3. Dependencies between tasks
        4. Priority levels
        5. Success criteria for each task
        6. Coordination requirements
        
        Format your response as a structured plan.
        """
        
        try:
            result = self.root_team.manager.execute_task(planning_task)
            if result["status"] == "completed":
                return {"plan": result["output"], "status": "success"}
            else:
                return {"plan": None, "status": "failed", "error": result.get("error")}
        except Exception as e:
            return {"plan": None, "status": "failed", "error": str(e)}
            
    def _delegate_tasks(self, execution_plan: Dict[str, Any]) -> List[TaskDelegation]:
        """Delegate tasks based on execution plan"""
        self.log_progress("Delegating tasks to teams and specialists")
        
        delegations = []
        
        # Simple delegation strategy: assign tasks based on team capabilities
        if self.root_team.sub_teams:
            # Delegate to team leads
            for i, team in enumerate(self.root_team.sub_teams):
                task_id = f"team_task_{i}"
                description = f"""
                Team Assignment for {team.team_name}:
                Original Request: {self.original_request}
                Execution Plan Context: {execution_plan.get('plan', 'No detailed plan available')}
                
                Coordinate your team to execute the parts of this request that match your expertise.
                Work with your specialists and coordinate with other teams as needed.
                """
                
                delegation = TaskDelegation(
                    task_id=task_id,
                    description=description,
                    assigned_to=team.manager,
                    priority="high"
                )
                delegations.append(delegation)
                
                # Delegate to specialists within the team
                for j, specialist in enumerate(team.specialists):
                    specialist_task_id = f"specialist_task_{i}_{j}"
                    specialist_description = f"""
                    Specialist Assignment:
                    Original Request: {self.original_request}
                    Team Context: Working under {team.team_name}
                    Your Role: {specialist.role}
                    
                    Execute the specific parts of this request that require your {specialist.role} expertise.
                    Coordinate with your team lead and provide detailed results.
                    """
                    
                    specialist_delegation = TaskDelegation(
                        task_id=specialist_task_id,
                        description=specialist_description,
                        assigned_to=specialist,
                        priority="medium",
                        dependencies=[task_id]  # Depends on team lead coordination
                    )
                    delegations.append(specialist_delegation)
        else:
            # Direct delegation to specialists
            for i, specialist in enumerate(self.root_team.specialists):
                task_id = f"direct_task_{i}"
                description = f"""
                Direct Assignment:
                Original Request: {self.original_request}
                Your Role: {specialist.role}
                Execution Plan: {execution_plan.get('plan', 'Execute your part of the request')}
                
                Execute the parts of this request that require your {specialist.role} expertise.
                Provide detailed results for integration.
                """
                
                delegation = TaskDelegation(
                    task_id=task_id,
                    description=description,
                    assigned_to=specialist,
                    priority="high"
                )
                delegations.append(delegation)
                
        return delegations
        
    def _execute_delegated_tasks(self, delegations: List[TaskDelegation]) -> Dict[str, Any]:
        """Execute delegated tasks with dependency management"""
        self.log_progress("Executing delegated tasks")
        
        completed_tasks = set()
        results = {}
        
        # Execute tasks in dependency order
        max_rounds = len(delegations) + 1  # Prevent infinite loops
        
        for round_num in range(max_rounds):
            executed_this_round = False
            
            for delegation in delegations:
                if delegation.status != ExecutionStatus.PENDING:
                    continue
                    
                # Check if dependencies are satisfied
                dependencies_met = all(dep in completed_tasks for dep in delegation.dependencies)
                
                if dependencies_met:
                    self.log_progress(f"Executing task {delegation.task_id} assigned to {delegation.assigned_to.name}")
                    
                    delegation.status = ExecutionStatus.IN_PROGRESS
                    delegation.start_time = time.time()
                    
                    try:
                        # Add context from completed dependencies
                        context_info = ""
                        if delegation.dependencies:
                            related_results = {dep: results.get(dep) for dep in delegation.dependencies}
                            context_info = f"\nContext from dependencies: {related_results}"
                            
                        task_with_context = delegation.description + context_info
                        
                        result = delegation.assigned_to.execute_task(task_with_context)
                        
                        delegation.end_time = time.time()
                        
                        if result["status"] == "completed":
                            delegation.status = ExecutionStatus.COMPLETED
                            delegation.result = result["output"]
                            results[delegation.task_id] = result["output"]
                            completed_tasks.add(delegation.task_id)
                            executed_this_round = True
                        else:
                            delegation.status = ExecutionStatus.FAILED
                            delegation.result = {"error": result.get("error")}
                            results[delegation.task_id] = {"error": result.get("error")}
                            
                    except Exception as e:
                        delegation.status = ExecutionStatus.FAILED
                        delegation.result = {"error": str(e)}
                        results[delegation.task_id] = {"error": str(e)}
                        delegation.end_time = time.time()
                        
            # If no tasks were executed this round, break to avoid infinite loop
            if not executed_this_round:
                break
                
        return results
        
    def _coordinate_results(self, task_results: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate and integrate results from teams"""
        self.log_progress("Coordinating team results")
        
        coordination_task = f"""
        As the executive manager, coordinate and integrate the following results from your teams:
        
        Original Request: {self.original_request}
        Team Results: {task_results}
        
        Tasks:
        1. Review all team outputs
        2. Identify connections and dependencies between results
        3. Resolve any conflicts or inconsistencies
        4. Identify gaps that need additional work
        5. Create a coordinated integration plan
        
        Provide a comprehensive coordination report.
        """
        
        try:
            result = self.root_team.manager.execute_task(coordination_task)
            if result["status"] == "completed":
                return {"coordination": result["output"], "status": "success"}
            else:
                return {"coordination": None, "status": "failed", "error": result.get("error")}
        except Exception as e:
            return {"coordination": None, "status": "failed", "error": str(e)}
            
    def _synthesize_final_result(self, task_results: Dict[str, Any], 
                                coordination: Dict[str, Any]) -> Dict[str, Any]:
        """Executive manager synthesizes final result"""
        self.log_progress("Synthesizing final result")
        
        synthesis_task = f"""
        As the executive manager, create the final synthesized result:
        
        Original Request: {self.original_request}
        All Team Results: {task_results}
        Coordination Report: {coordination}
        
        Create a comprehensive final result that:
        1. Fully addresses the original request
        2. Integrates all team contributions
        3. Resolves any identified issues
        4. Provides clear value to the user
        5. Includes recommendations for next steps if applicable
        
        This should be the definitive final output for the user.
        """
        
        try:
            result = self.root_team.manager.execute_task(synthesis_task)
            if result["status"] == "completed":
                return {"final_result": result["output"], "status": "success"}
            else:
                return {"final_result": None, "status": "failed", "error": result.get("error")}
        except Exception as e:
            return {"final_result": None, "status": "failed", "error": str(e)}
            
    def execute(self) -> WorkflowResult:
        """Execute the hierarchical workflow"""
        self.start_time = time.time()
        self.initialize()
        
        output = {
            "workflow_type": "hierarchical",
            "team_structure": {},
            "execution_phases": {}
        }
        errors = []
        overall_status = ExecutionStatus.COMPLETED
        
        self.log_progress("Starting hierarchical workflow execution")
        
        try:
            # Phase 1: Executive Planning
            self.steps[0].status = ExecutionStatus.IN_PROGRESS
            execution_plan = self._create_execution_plan()
            self.steps[0].status = ExecutionStatus.COMPLETED if execution_plan["status"] == "success" else ExecutionStatus.FAILED
            output["execution_phases"]["planning"] = execution_plan
            
            if execution_plan["status"] != "success":
                errors.append(f"Planning failed: {execution_plan.get('error')}")
                
            # Phase 2: Task Delegation
            self.steps[1].status = ExecutionStatus.IN_PROGRESS
            self.delegations = self._delegate_tasks(execution_plan)
            self.steps[1].status = ExecutionStatus.COMPLETED
            output["execution_phases"]["delegation"] = {
                "delegations_count": len(self.delegations),
                "delegations": [{"task_id": d.task_id, "assigned_to": d.assigned_to.name} for d in self.delegations]
            }
            
            # Phase 3: Team Execution
            self.steps[2].status = ExecutionStatus.IN_PROGRESS
            task_results = self._execute_delegated_tasks(self.delegations)
            self.steps[2].status = ExecutionStatus.COMPLETED
            output["execution_phases"]["execution"] = task_results
            
            # Check for execution failures
            failed_tasks = [d for d in self.delegations if d.status == ExecutionStatus.FAILED]
            if failed_tasks:
                for task in failed_tasks:
                    errors.append(f"Task {task.task_id} failed: {task.result.get('error', 'Unknown error')}")
                    
            # Phase 4: Results Coordination
            self.steps[3].status = ExecutionStatus.IN_PROGRESS
            coordination = self._coordinate_results(task_results)
            self.steps[3].status = ExecutionStatus.COMPLETED if coordination["status"] == "success" else ExecutionStatus.FAILED
            output["execution_phases"]["coordination"] = coordination
            
            if coordination["status"] != "success":
                errors.append(f"Coordination failed: {coordination.get('error')}")
                
            # Phase 5: Final Synthesis
            self.steps[4].status = ExecutionStatus.IN_PROGRESS
            final_synthesis = self._synthesize_final_result(task_results, coordination)
            self.steps[4].status = ExecutionStatus.COMPLETED if final_synthesis["status"] == "success" else ExecutionStatus.FAILED
            output["execution_phases"]["synthesis"] = final_synthesis
            
            if final_synthesis["status"] == "success":
                output["final_output"] = final_synthesis["final_result"]
            else:
                errors.append(f"Synthesis failed: {final_synthesis.get('error')}")
                
            # Determine overall status
            if errors:
                overall_status = ExecutionStatus.FAILED
            elif all(step.status == ExecutionStatus.COMPLETED for step in self.steps):
                overall_status = ExecutionStatus.COMPLETED
            else:
                overall_status = ExecutionStatus.FAILED
                
        except Exception as e:
            errors.append(f"Hierarchical workflow execution failed: {str(e)}")
            overall_status = ExecutionStatus.FAILED
            
        self.end_time = time.time()
        
        # Add team structure to output
        if self.root_team:
            output["team_structure"] = {
                "root_manager": self.root_team.manager.name,
                "sub_teams": [{"name": team.team_name, "manager": team.manager.name, 
                              "specialists": [s.name for s in team.specialists]} 
                             for team in self.root_team.sub_teams],
                "direct_specialists": [s.name for s in self.root_team.specialists]
            }
        
        self.log_progress(f"Hierarchical workflow completed with status: {overall_status.value}")
        
        return self.create_result(overall_status, output, errors)