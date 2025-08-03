#!/usr/bin/env python3
"""
Unit tests for HierarchicalWorkflow - Phase 6

Tests hierarchical workflow execution with team delegation
and coordination.
"""

import pytest
from unittest.mock import Mock, patch
from src.workflows.hierarchical_workflow import HierarchicalWorkflow, TeamStructure, TaskDelegation
from src.core.models import PromptAnalysis, WorkflowPattern, ExecutionStatus
from src.agents.base_agent import BaseAgent


@pytest.fixture
def sample_analysis():
    """Sample prompt analysis for hierarchical workflow."""
    return PromptAnalysis(
        complexity_score=0.8,
        urgency_score=0.6,
        quality_requirements=0.8,
        task_types=["research", "technical", "creative"],
        dependencies=True,
        parallel_potential=True,
        decision_points=False,
        iteration_needed=False,
        team_size_needed=5,
        recommended_pattern=WorkflowPattern.HIERARCHICAL,
        confidence=0.9
    )


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = Mock(spec=BaseAgent)
    agent.name = "test_agent"
    agent.role = "test_role"
    agent.execute_task.return_value = {
        "status": "completed",
        "output": "Task completed successfully"
    }
    return agent


@pytest.fixture
def hierarchical_workflow(sample_analysis):
    """Create a hierarchical workflow instance."""
    return HierarchicalWorkflow(sample_analysis, "Test hierarchical workflow request")


class TestTeamStructure:
    """Test suite for TeamStructure class."""

    def test_team_creation(self, mock_agent):
        """Test team structure creation."""
        team = TeamStructure(mock_agent, "Test Team")
        
        assert team.manager == mock_agent
        assert team.team_name == "Test Team"
        assert team.specialists == []
        assert team.sub_teams == []

    def test_add_specialist(self, mock_agent):
        """Test adding specialist to team."""
        team = TeamStructure(mock_agent, "Test Team")
        specialist = Mock(spec=BaseAgent)
        
        team.add_specialist(specialist)
        
        assert len(team.specialists) == 1
        assert team.specialists[0] == specialist

    def test_add_sub_team(self, mock_agent):
        """Test adding sub-team."""
        parent_team = TeamStructure(mock_agent, "Parent Team")
        sub_manager = Mock(spec=BaseAgent)
        sub_team = TeamStructure(sub_manager, "Sub Team")
        
        parent_team.add_sub_team(sub_team)
        
        assert len(parent_team.sub_teams) == 1
        assert parent_team.sub_teams[0] == sub_team

    def test_get_all_agents(self, mock_agent):
        """Test getting all agents in hierarchy."""
        # Create team structure
        manager = Mock(spec=BaseAgent)
        team = TeamStructure(manager, "Test Team")
        
        specialist1 = Mock(spec=BaseAgent)
        specialist2 = Mock(spec=BaseAgent)
        team.add_specialist(specialist1)
        team.add_specialist(specialist2)
        
        # Add sub-team
        sub_manager = Mock(spec=BaseAgent)
        sub_team = TeamStructure(sub_manager, "Sub Team")
        sub_specialist = Mock(spec=BaseAgent)
        sub_team.add_specialist(sub_specialist)
        team.add_sub_team(sub_team)
        
        all_agents = team.get_all_agents()
        
        assert manager in all_agents
        assert specialist1 in all_agents
        assert specialist2 in all_agents
        assert sub_manager in all_agents
        assert sub_specialist in all_agents
        assert len(all_agents) == 5


class TestTaskDelegation:
    """Test suite for TaskDelegation class."""

    def test_delegation_creation(self, mock_agent):
        """Test task delegation creation."""
        delegation = TaskDelegation(
            "test_task",
            "Test task description",
            mock_agent,
            "high",
            ["dep1", "dep2"]
        )
        
        assert delegation.task_id == "test_task"
        assert delegation.description == "Test task description"
        assert delegation.assigned_to == mock_agent
        assert delegation.priority == "high"
        assert delegation.dependencies == ["dep1", "dep2"]
        assert delegation.status == ExecutionStatus.PENDING
        assert delegation.result is None


class TestHierarchicalWorkflow:
    """Test suite for HierarchicalWorkflow class."""

    def test_initialization(self, hierarchical_workflow):
        """Test hierarchical workflow initialization."""
        assert hierarchical_workflow.analysis is not None
        assert hierarchical_workflow.original_request == "Test hierarchical workflow request"
        assert hierarchical_workflow.root_team is None
        assert hierarchical_workflow.delegations == []
        assert hierarchical_workflow.coordination_results == {}

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_create_specialized_teams(self, mock_factory, hierarchical_workflow, mock_agent):
        """Test creation of specialized teams for complex workflows."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        # Create root team structure
        root_team = hierarchical_workflow.create_team_structure()
        
        # Check that teams were created
        assert root_team is not None
        assert len(root_team.sub_teams) > 0
        
        # Check for expected team types
        team_names = [team.team_name for team in root_team.sub_teams]
        expected_teams = ["Research_Team", "Technical_Team", "Creative_Team"]
        
        # At least some expected teams should be present
        assert any(expected in team_names for expected in expected_teams)

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_create_team_structure_high_complexity(self, mock_factory, hierarchical_workflow, mock_agent):
        """Test team structure creation for high complexity tasks."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        # Set high complexity
        hierarchical_workflow.analysis.complexity_score = 0.9
        hierarchical_workflow.analysis.task_types = ["research", "technical", "creative", "analytical"]
        
        root_team = hierarchical_workflow.create_team_structure()
        
        assert root_team is not None
        assert root_team.manager is not None
        assert len(root_team.sub_teams) > 0

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_create_team_structure_medium_complexity(self, mock_factory, hierarchical_workflow, mock_agent):
        """Test team structure creation for medium complexity tasks."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        # Set medium complexity
        hierarchical_workflow.analysis.complexity_score = 0.5
        hierarchical_workflow.analysis.task_types = ["research", "technical"]
        
        root_team = hierarchical_workflow.create_team_structure()
        
        assert root_team is not None
        assert len(root_team.sub_teams) > 0

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_create_team_structure_simple(self, mock_factory, hierarchical_workflow, mock_agent):
        """Test team structure creation for simple tasks."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        # Set simple structure
        hierarchical_workflow.analysis.complexity_score = 0.3
        hierarchical_workflow.analysis.task_types = ["research"]
        
        root_team = hierarchical_workflow.create_team_structure()
        
        assert root_team is not None
        # Simple structure should have direct specialists
        assert len(root_team.specialists) > 0 or len(root_team.sub_teams) > 0

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_create_agents(self, mock_factory, hierarchical_workflow, mock_agent):
        """Test agent creation in hierarchical workflow."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        agents = hierarchical_workflow.create_agents()
        
        assert len(agents) > 0
        assert hierarchical_workflow.root_team is not None

    def test_define_steps(self, hierarchical_workflow):
        """Test step definition for hierarchical workflow."""
        steps = hierarchical_workflow.define_steps()
        
        assert len(steps) == 5
        step_ids = [step.id for step in steps]
        expected_steps = [
            "executive_planning",
            "task_delegation", 
            "team_execution",
            "results_coordination",
            "final_synthesis"
        ]
        
        assert step_ids == expected_steps

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_create_execution_plan(self, mock_factory, hierarchical_workflow, mock_agent):
        """Test execution plan creation."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        # Initialize workflow
        hierarchical_workflow.initialize()
        
        # Create execution plan
        plan = hierarchical_workflow._create_execution_plan()
        
        assert "plan" in plan
        assert "status" in plan
        assert plan["status"] == "success"

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_delegate_tasks_with_teams(self, mock_factory, hierarchical_workflow, mock_agent):
        """Test task delegation with sub-teams."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        # Initialize workflow with team structure
        hierarchical_workflow.initialize()
        
        execution_plan = {"plan": "Test execution plan"}
        delegations = hierarchical_workflow._delegate_tasks(execution_plan)
        
        assert len(delegations) > 0
        assert all(isinstance(d, TaskDelegation) for d in delegations)

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_delegate_tasks_direct_specialists(self, mock_factory, hierarchical_workflow, mock_agent):
        """Test task delegation with direct specialists."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        # Set simple workflow to get direct specialists
        hierarchical_workflow.analysis.complexity_score = 0.3
        hierarchical_workflow.analysis.task_types = ["research"]
        
        hierarchical_workflow.initialize()
        
        execution_plan = {"plan": "Simple execution plan"}
        delegations = hierarchical_workflow._delegate_tasks(execution_plan)
        
        assert len(delegations) > 0

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_execute_delegated_tasks(self, mock_factory, hierarchical_workflow, mock_agent):
        """Test execution of delegated tasks."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        # Create delegations
        delegations = [
            TaskDelegation("task1", "First task", mock_agent, "high"),
            TaskDelegation("task2", "Second task", mock_agent, "medium", ["task1"])
        ]
        
        results = hierarchical_workflow._execute_delegated_tasks(delegations)
        
        assert "task1" in results
        assert "task2" in results
        assert delegations[0].status == ExecutionStatus.COMPLETED
        assert delegations[1].status == ExecutionStatus.COMPLETED

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_coordinate_results(self, mock_factory, hierarchical_workflow, mock_agent):
        """Test results coordination."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        hierarchical_workflow.initialize()
        
        task_results = {
            "task1": "Result 1",
            "task2": "Result 2"
        }
        
        coordination = hierarchical_workflow._coordinate_results(task_results)
        
        assert "coordination" in coordination
        assert "status" in coordination

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_synthesize_final_result(self, mock_factory, hierarchical_workflow, mock_agent):
        """Test final result synthesis."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        hierarchical_workflow.initialize()
        
        task_results = {"task1": "Result 1"}
        coordination = {"coordination": "Coordinated results"}
        
        synthesis = hierarchical_workflow._synthesize_final_result(task_results, coordination)
        
        assert "final_result" in synthesis
        assert "status" in synthesis

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_full_execution_success(self, mock_factory, hierarchical_workflow, mock_agent):
        """Test full hierarchical workflow execution."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        # Execute workflow
        result = hierarchical_workflow.execute()
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.pattern == WorkflowPattern.HIERARCHICAL
        assert "workflow_type" in result.output
        assert result.output["workflow_type"] == "hierarchical"
        assert "execution_phases" in result.output
        assert "team_structure" in result.output

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_execution_with_planning_failure(self, mock_factory, hierarchical_workflow):
        """Test execution when planning fails."""
        # Setup failing executive manager
        failing_manager = Mock(spec=BaseAgent)
        failing_manager.execute_task.return_value = {
            "status": "failed",
            "error": "Planning failed"
        }
        
        # Setup normal agents for other roles
        normal_agent = Mock(spec=BaseAgent)
        normal_agent.execute_task.return_value = {
            "status": "completed",
            "output": "Normal task completed"
        }
        
        # Mock factory to return failing manager first, then normal agents
        mock_factory.return_value.create_agent.side_effect = [failing_manager] + [normal_agent] * 10
        
        # Execute workflow
        result = hierarchical_workflow.execute()
        
        # Should continue execution even with planning failure
        assert len(result.errors) > 0
        assert "Planning failed" in str(result.errors)

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_execution_with_task_failures(self, mock_factory, hierarchical_workflow):
        """Test execution with task failures."""
        # Setup mixed success/failure agents
        success_agent = Mock(spec=BaseAgent)
        success_agent.name = "success_agent"
        success_agent.execute_task.return_value = {
            "status": "completed",
            "output": "Task completed"
        }
        
        failure_agent = Mock(spec=BaseAgent)
        failure_agent.name = "failure_agent"
        failure_agent.execute_task.return_value = {
            "status": "failed",
            "error": "Task failed"
        }
        
        # Alternate between success and failure
        mock_factory.return_value.create_agent.side_effect = [success_agent, failure_agent] * 5
        
        # Execute workflow
        result = hierarchical_workflow.execute()
        
        # Should have some errors but still complete
        assert len(result.errors) > 0

    @patch('src.workflows.hierarchical_workflow.AgentFactory')
    def test_execution_phase_tracking(self, mock_factory, hierarchical_workflow, mock_agent):
        """Test that all execution phases are tracked."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        result = hierarchical_workflow.execute()
        
        phases = result.output["execution_phases"]
        expected_phases = ["planning", "delegation", "execution", "coordination", "synthesis"]
        
        for phase in expected_phases:
            assert phase in phases

    def test_dependency_handling_in_task_execution(self, hierarchical_workflow, mock_agent):
        """Test that task dependencies are properly handled."""
        # Create tasks with dependencies
        task1 = TaskDelegation("task1", "First task", mock_agent, "high")
        task2 = TaskDelegation("task2", "Second task", mock_agent, "medium", ["task1"])
        task3 = TaskDelegation("task3", "Third task", mock_agent, "low", ["task1", "task2"])
        
        delegations = [task1, task2, task3]
        
        # Execute tasks
        results = hierarchical_workflow._execute_delegated_tasks(delegations)
        
        # All tasks should complete
        assert all(d.status == ExecutionStatus.COMPLETED for d in delegations)
        
        # Dependent tasks should execute after their dependencies
        assert task1.end_time <= task2.start_time
        assert task2.end_time <= task3.start_time


if __name__ == "__main__":
    pytest.main([__file__])