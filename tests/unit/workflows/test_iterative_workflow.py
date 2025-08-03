#!/usr/bin/env python3
"""
Unit tests for IterativeWorkflow - Phase 6

Tests iterative workflow execution with convergence criteria
and quality assessment.
"""

import pytest
from unittest.mock import Mock, patch
from src.workflows.iterative_workflow import IterativeWorkflow, IterationResult, ConvergenceFunctions
from src.core.models import PromptAnalysis, WorkflowPattern, ExecutionStatus
from src.agents.base_agent import BaseAgent


@pytest.fixture
def sample_analysis():
    """Sample prompt analysis for iterative workflow."""
    return PromptAnalysis(
        complexity_score=0.6,
        urgency_score=0.5,
        quality_requirements=0.9,
        task_types=["creative", "technical"],
        dependencies=False,
        parallel_potential=False,
        decision_points=False,
        iteration_needed=True,
        team_size_needed=2,
        recommended_pattern=WorkflowPattern.ITERATIVE,
        confidence=0.8
    )


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = Mock(spec=BaseAgent)
    agent.configure_mock(name="test_agent", role="test_role")
    agent.execute_task.return_value = {
        "status": "completed",
        "output": "Iteration task completed"
    }
    return agent


@pytest.fixture
def iterative_workflow(sample_analysis):
    """Create an iterative workflow instance."""
    return IterativeWorkflow(sample_analysis, "Test iterative workflow request", max_iterations=3)


class TestIterativeWorkflow:
    """Test suite for IterativeWorkflow class."""

    def test_initialization(self, iterative_workflow):
        """Test iterative workflow initialization."""
        assert iterative_workflow.analysis is not None
        assert iterative_workflow.original_request == "Test iterative workflow request"
        assert iterative_workflow.max_iterations == 3
        assert iterative_workflow.quality_threshold == 0.8
        assert iterative_workflow.convergence_function is None
        assert iterative_workflow.quality_assessor is None
        assert iterative_workflow.iteration_results == []
        assert iterative_workflow.improvement_agents == []

    def test_set_quality_threshold(self, iterative_workflow):
        """Test setting quality threshold."""
        iterative_workflow.set_quality_threshold(0.95)
        assert iterative_workflow.quality_threshold == 0.95
        
        # Test bounds
        iterative_workflow.set_quality_threshold(1.5)  # Too high
        assert iterative_workflow.quality_threshold == 1.0
        
        iterative_workflow.set_quality_threshold(-0.1)  # Too low
        assert iterative_workflow.quality_threshold == 0.0

    def test_set_convergence_function(self, iterative_workflow):
        """Test setting custom convergence function."""
        def custom_convergence(results):
            return len(results) >= 2
        
        iterative_workflow.set_convergence_function(custom_convergence)
        assert iterative_workflow.convergence_function == custom_convergence

    def test_add_quality_assessor(self, iterative_workflow, mock_agent):
        """Test adding quality assessor agent."""
        iterative_workflow.add_quality_assessor(mock_agent)
        assert iterative_workflow.quality_assessor == mock_agent

    def test_add_improvement_agent(self, iterative_workflow, mock_agent):
        """Test adding improvement agent."""
        iterative_workflow.add_improvement_agent(mock_agent)
        assert len(iterative_workflow.improvement_agents) == 1
        assert iterative_workflow.improvement_agents[0] == mock_agent

    @patch('src.workflows.iterative_workflow.AgentFactory')
    def test_create_agents(self, mock_factory, iterative_workflow, mock_agent):
        """Test agent creation."""
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        # Add quality assessor and improvement agents
        quality_agent = Mock(spec=BaseAgent)
        improvement_agent = Mock(spec=BaseAgent)
        iterative_workflow.add_quality_assessor(quality_agent)
        iterative_workflow.add_improvement_agent(improvement_agent)
        
        agents = iterative_workflow.create_agents()
        
        assert quality_agent in agents
        assert improvement_agent in agents
        assert len(agents) >= 2  # At least quality and improvement agents

    def test_default_quality_assessment(self, iterative_workflow):
        """Test default quality assessment logic."""
        # Test empty output
        score = iterative_workflow._default_quality_assessment({})
        assert score == 0.1
        
        # Test successful output
        output = {
            "step_0": "Good result",
            "step_1": "Another good result with substantial content that shows detailed work"
        }
        score = iterative_workflow._default_quality_assessment(output)
        assert score > 0.5
        
        # Test output with errors
        error_output = {
            "step_0": "Failed with error",
            "step_1": "Another error occurred"
        }
        score = iterative_workflow._default_quality_assessment(error_output)
        assert score < 0.5

    def test_quality_assessment_with_agent(self, iterative_workflow, mock_agent):
        """Test quality assessment using quality assessor agent."""
        # Setup quality assessor
        mock_agent.execute_task.return_value = {
            "status": "completed",
            "output": "Quality Score: 0.85"
        }
        iterative_workflow.add_quality_assessor(mock_agent)
        
        output = {"step_0": "Test output"}
        score = iterative_workflow._assess_quality(output)
        
        assert score == 0.85
        assert mock_agent.execute_task.called

    def test_quality_assessment_text_analysis(self, iterative_workflow, mock_agent):
        """Test quality assessment through text analysis."""
        # Setup quality assessor with text-based output
        mock_agent.execute_task.return_value = {
            "status": "completed",
            "output": "This work is excellent and meets all requirements"
        }
        iterative_workflow.add_quality_assessor(mock_agent)
        
        output = {"step_0": "Test output"}
        score = iterative_workflow._assess_quality(output)
        
        assert score == 0.9  # Should detect "excellent"

    def test_check_convergence_quality_threshold(self, iterative_workflow):
        """Test convergence based on quality threshold."""
        # Add iteration result above threshold
        result = IterationResult(1, {"output": "good"}, 0.85, False)
        iterative_workflow.iteration_results = [result]
        iterative_workflow.quality_threshold = 0.8
        
        converged = iterative_workflow._check_convergence()
        assert converged is True

    def test_check_convergence_improvement_plateau(self, iterative_workflow):
        """Test convergence based on improvement plateau."""
        # Add iteration results with minimal improvement
        result1 = IterationResult(1, {"output": "ok"}, 0.70, False)
        result2 = IterationResult(2, {"output": "slightly better"}, 0.72, False)
        iterative_workflow.iteration_results = [result1, result2]
        iterative_workflow.quality_threshold = 0.9  # High threshold not met
        
        converged = iterative_workflow._check_convergence()
        assert converged is True  # Should converge due to minimal improvement

    def test_check_convergence_custom_function(self, iterative_workflow):
        """Test convergence with custom function."""
        def custom_convergence(results):
            return len(results) >= 2
        
        iterative_workflow.set_convergence_function(custom_convergence)
        
        # Add two results
        result1 = IterationResult(1, {"output": "first"}, 0.5, False)
        result2 = IterationResult(2, {"output": "second"}, 0.6, False)
        iterative_workflow.iteration_results = [result1, result2]
        
        converged = iterative_workflow._check_convergence()
        assert converged is True

    def test_get_improvement_feedback(self, iterative_workflow, mock_agent):
        """Test getting improvement feedback from agents."""
        # Setup improvement agent
        mock_agent.execute_task.return_value = {
            "status": "completed",
            "output": "Focus on improving accuracy and completeness"
        }
        iterative_workflow.add_improvement_agent(mock_agent)
        
        # Create iteration results
        result = IterationResult(1, {"output": "needs work"}, 0.5, False)
        feedback = iterative_workflow._get_improvement_feedback([result])
        
        assert "Focus on improving accuracy" in feedback
        assert mock_agent.execute_task.called

    @patch('src.workflows.iterative_workflow.AgentFactory')
    def test_execute_iteration(self, mock_factory, iterative_workflow, mock_agent):
        """Test execution of a single iteration."""
        # Setup mock factory and agents
        mock_factory.return_value.create_agent.return_value = mock_agent
        iterative_workflow.initialize()
        
        # Execute iteration
        result = iterative_workflow._execute_iteration(1)
        
        assert isinstance(result, IterationResult)
        assert result.iteration_number == 1
        assert result.quality_score >= 0.0
        # Check that the mock factory was called to create agents
        assert mock_factory.return_value.create_agent.called

    @patch('src.workflows.iterative_workflow.AgentFactory')
    def test_full_execution_convergence(self, mock_factory, iterative_workflow, mock_agent):
        """Test full iterative workflow execution with convergence."""
        # Setup high-quality agent
        mock_agent.execute_task.return_value = {
            "status": "completed",
            "output": "High quality output with substantial content and excellent results"
        }
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        # Set low quality threshold for quick convergence
        iterative_workflow.set_quality_threshold(0.7)
        
        # Execute workflow
        result = iterative_workflow.execute()
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.pattern == WorkflowPattern.ITERATIVE
        assert "workflow_type" in result.output
        assert result.output["workflow_type"] == "iterative"
        assert "converged" in result.output

    @patch('src.workflows.iterative_workflow.AgentFactory')
    def test_execution_max_iterations(self, mock_factory, iterative_workflow, mock_agent):
        """Test execution hitting maximum iterations."""
        # Setup low-quality agent that won't converge
        mock_agent.execute_task.return_value = {
            "status": "completed",
            "output": "Low quality output"
        }
        mock_factory.return_value.create_agent.return_value = mock_agent
        
        # Set high quality threshold
        iterative_workflow.set_quality_threshold(0.95)
        iterative_workflow.max_iterations = 2
        
        # Execute workflow
        result = iterative_workflow.execute()
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["converged"] is False
        assert result.output["total_iterations"] == 2

    @patch('src.workflows.iterative_workflow.AgentFactory')
    def test_execution_with_errors(self, mock_factory, iterative_workflow):
        """Test execution with agent errors."""
        # Setup failing agent
        failing_agent = Mock(spec=BaseAgent)
        failing_agent.configure_mock(name="failing_agent", role="test_role")
        failing_agent.execute_task.return_value = {
            "status": "failed",
            "error": "Task failed"
        }
        mock_factory.return_value.create_agent.return_value = failing_agent
        
        # Execute workflow
        result = iterative_workflow.execute()
        
        assert len(result.errors) > 0
        assert result.output["total_iterations"] >= 1

    def test_execution_with_quality_assessor(self, iterative_workflow, mock_agent):
        """Test execution with quality assessor agent."""
        # Setup quality assessor
        quality_agent = Mock(spec=BaseAgent)
        quality_agent.execute_task.return_value = {
            "status": "completed",
            "output": "Quality Score: 0.9"
        }
        iterative_workflow.add_quality_assessor(quality_agent)
        
        # Test quality assessment
        output = {"step_0": "test"}
        score = iterative_workflow._assess_quality(output)
        assert score == 0.9

    def test_convergence_functions(self):
        """Test built-in convergence functions."""
        # Test quality threshold function
        threshold_func = ConvergenceFunctions.quality_threshold(0.8)
        
        results = [
            IterationResult(1, {}, 0.7, False),
            IterationResult(2, {}, 0.85, False)
        ]
        assert threshold_func(results) is True
        
        # Test stable quality function
        stable_func = ConvergenceFunctions.stable_quality(2, 0.05)
        
        stable_results = [
            IterationResult(1, {}, 0.75, False),
            IterationResult(2, {}, 0.77, False)
        ]
        assert stable_func(stable_results) is True
        
        # Test diminishing returns function
        diminishing_func = ConvergenceFunctions.diminishing_returns(0.02)
        
        diminishing_results = [
            IterationResult(1, {}, 0.7, False),
            IterationResult(2, {}, 0.71, False)  # Small improvement
        ]
        assert diminishing_func(diminishing_results) is True


class TestIterationResult:
    """Test suite for IterationResult class."""

    def test_iteration_result_creation(self):
        """Test iteration result creation."""
        output = {"step_0": "test output"}
        errors = ["minor error"]
        
        result = IterationResult(1, output, 0.8, False, errors)
        
        assert result.iteration_number == 1
        assert result.output == output
        assert result.quality_score == 0.8
        assert result.converged is False
        assert result.errors == errors
        assert result.timestamp is not None


if __name__ == "__main__":
    pytest.main([__file__])