#!/usr/bin/env python3
"""
Integration tests for Advanced Workflow Patterns - Phase 6

Tests integration between advanced workflows, prompt analysis,
workflow selection, and agent coordination.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.prompt_analyzer import PromptAnalyzer
from src.core.workflow_selector import WorkflowSelector
from src.core.models import WorkflowPattern, ExecutionStatus
from src.workflows.conditional_workflow import ConditionalWorkflow
from src.workflows.iterative_workflow import IterativeWorkflow
from src.workflows.hierarchical_workflow import HierarchicalWorkflow


class TestAdvancedWorkflowsIntegration:
    """Integration tests for advanced workflow patterns."""

    def setup_method(self):
        """Setup for each test method."""
        self.analyzer = PromptAnalyzer()
        self.selector = WorkflowSelector()

    @patch('src.agents.agent_factory.AgentFactory')
    def test_conditional_workflow_integration(self, mock_factory):
        """Test conditional workflow end-to-end integration."""
        # Setup mock agents
        mock_agent = Mock()
        mock_agent.name = "test_agent"
        mock_agent.role = "research"
        mock_agent.execute_task.return_value = {
            "status": "completed",
            "output": "High complexity analysis completed with security considerations"
        }
        mock_factory.return_value.create_agent.return_value = mock_agent

        # Test conditional request
        request = "If the data is sensitive, use encryption. Otherwise, use standard processing."
        
        # Analyze prompt
        analysis = self.analyzer.analyze_prompt(request)
        
        # Should detect conditional pattern
        assert analysis.decision_points is True
        assert analysis.recommended_pattern == WorkflowPattern.CONDITIONAL
        
        # Select workflow
        workflow = self.selector.select_workflow(analysis, request)
        assert isinstance(workflow, ConditionalWorkflow)
        
        # Add branches to workflow
        workflow.add_context_evaluator(mock_agent)
        workflow.add_branch(
            "secure_processing",
            lambda ctx: ctx.get("security_sensitive", False),
            ["technical"],
            ["Implement encryption and secure processing"]
        )
        workflow.add_default_branch(
            ["technical"],
            ["Implement standard processing"]
        )
        
        # Execute workflow
        result = workflow.execute()
        
        assert result.status == ExecutionStatus.COMPLETED
        assert "selected_branch" in result.output
        assert "context" in result.output

    @patch('src.agents.agent_factory.AgentFactory')
    def test_iterative_workflow_integration(self, mock_factory):
        """Test iterative workflow end-to-end integration."""
        # Setup mock agents with improving quality
        iteration_count = 0
        
        def mock_execute_task(task):
            nonlocal iteration_count
            iteration_count += 1
            
            if iteration_count <= 2:
                return {
                    "status": "completed", 
                    "output": f"Iteration {iteration_count}: Basic quality output"
                }
            else:
                return {
                    "status": "completed",
                    "output": f"Iteration {iteration_count}: High quality comprehensive output with excellent details"
                }
        
        mock_agent = Mock()
        mock_agent.name = "test_agent"
        mock_agent.role = "creative"
        mock_agent.execute_task.side_effect = mock_execute_task
        mock_factory.return_value.create_agent.return_value = mock_agent

        # Test iterative request
        request = "Refine and improve the design until it meets quality standards"
        
        # Analyze prompt
        analysis = self.analyzer.analyze_prompt(request)
        
        # Should detect iterative pattern
        assert analysis.iteration_needed is True
        assert analysis.recommended_pattern == WorkflowPattern.ITERATIVE
        
        # Select workflow
        workflow = self.selector.select_workflow(analysis, request)
        assert isinstance(workflow, IterativeWorkflow)
        
        # Configure workflow
        workflow.max_iterations = 3
        workflow.set_quality_threshold(0.7)
        
        # Execute workflow
        result = workflow.execute()
        
        assert result.status == ExecutionStatus.COMPLETED
        assert "converged" in result.output
        assert result.output["total_iterations"] >= 1

    @patch('src.agents.agent_factory.AgentFactory')
    def test_hierarchical_workflow_integration(self, mock_factory):
        """Test hierarchical workflow end-to-end integration."""
        # Setup mock agents
        mock_agent = Mock()
        mock_agent.name = "test_agent"
        mock_agent.role = "analytical"
        mock_agent.execute_task.return_value = {
            "status": "completed",
            "output": "Complex team coordination task completed successfully"
        }
        mock_factory.return_value.create_agent.return_value = mock_agent

        # Test hierarchical request
        request = "Coordinate multiple teams to research, design, and implement a comprehensive solution with specialists in each area"
        
        # Analyze prompt
        analysis = self.analyzer.analyze_prompt(request)
        
        # Should detect hierarchical pattern due to team coordination keywords
        assert analysis.recommended_pattern == WorkflowPattern.HIERARCHICAL
        assert analysis.team_size_needed > 2
        
        # Select workflow
        workflow = self.selector.select_workflow(analysis, request)
        assert isinstance(workflow, HierarchicalWorkflow)
        
        # Execute workflow
        result = workflow.execute()
        
        assert result.status == ExecutionStatus.COMPLETED
        assert "team_structure" in result.output
        assert "execution_phases" in result.output

    def test_prompt_analysis_pattern_detection(self):
        """Test that prompt analyzer correctly detects advanced patterns."""
        test_cases = [
            {
                "request": "If complexity is high, delegate to specialists. Otherwise, handle directly.",
                "expected_pattern": WorkflowPattern.CONDITIONAL,
                "expected_features": {"decision_points": True}
            },
            {
                "request": "Keep refining the solution until quality standards are met",
                "expected_pattern": WorkflowPattern.ITERATIVE,
                "expected_features": {"iteration_needed": True}
            },
            {
                "request": "Coordinate research team, technical team, and creative team to deliver comprehensive solution",
                "expected_pattern": WorkflowPattern.HIERARCHICAL,
                "expected_features": {"team_size_needed": lambda x: x >= 2}
            },
            {
                "request": "First analyze, then if complex coordinate teams, and iterate until perfect",
                "expected_pattern": WorkflowPattern.HYBRID,
                "expected_features": {
                    "dependencies": True,
                    "decision_points": True,
                    "iteration_needed": True
                }
            }
        ]
        
        for case in test_cases:
            analysis = self.analyzer.analyze_prompt(case["request"])
            
            assert analysis.recommended_pattern == case["expected_pattern"], \
                f"Failed for request: {case['request']}"
            
            for feature, expected_value in case["expected_features"].items():
                actual_value = getattr(analysis, feature)
                if callable(expected_value):
                    assert expected_value(actual_value), \
                        f"Feature {feature} failed check for: {case['request']}"
                else:
                    assert actual_value == expected_value, \
                        f"Feature {feature} mismatch for: {case['request']}"

    def test_workflow_selector_registry(self):
        """Test that workflow selector has all advanced patterns registered."""
        assert WorkflowPattern.CONDITIONAL in self.selector.workflow_registry
        assert WorkflowPattern.ITERATIVE in self.selector.workflow_registry
        assert WorkflowPattern.HIERARCHICAL in self.selector.workflow_registry
        
        assert self.selector.workflow_registry[WorkflowPattern.CONDITIONAL] == ConditionalWorkflow
        assert self.selector.workflow_registry[WorkflowPattern.ITERATIVE] == IterativeWorkflow
        assert self.selector.workflow_registry[WorkflowPattern.HIERARCHICAL] == HierarchicalWorkflow

    def test_workflow_configs(self):
        """Test workflow configuration parameters."""
        configs = {
            WorkflowPattern.CONDITIONAL: self.selector.get_workflow_config(WorkflowPattern.CONDITIONAL),
            WorkflowPattern.ITERATIVE: self.selector.get_workflow_config(WorkflowPattern.ITERATIVE),
            WorkflowPattern.HIERARCHICAL: self.selector.get_workflow_config(WorkflowPattern.HIERARCHICAL)
        }
        
        # Conditional config
        conditional_config = configs[WorkflowPattern.CONDITIONAL]
        assert "max_branches" in conditional_config
        assert "evaluation_timeout" in conditional_config
        assert "default_branch" in conditional_config
        
        # Iterative config
        iterative_config = configs[WorkflowPattern.ITERATIVE]
        assert "max_iterations" in iterative_config
        assert "convergence_threshold" in iterative_config
        assert "timeout_per_iteration" in iterative_config
        
        # Hierarchical config
        hierarchical_config = configs[WorkflowPattern.HIERARCHICAL]
        assert "max_depth" in hierarchical_config
        assert "delegation_strategy" in hierarchical_config
        assert "coordination_overhead" in hierarchical_config

    def test_execution_time_estimation(self):
        """Test execution time estimation for advanced patterns."""
        base_analysis = {
            "complexity_score": 0.7,
            "urgency_score": 0.5,
            "quality_requirements": 0.8,
            "task_types": ["research", "technical"],
            "dependencies": True,
            "parallel_potential": False,
            "decision_points": False,
            "iteration_needed": False,
            "team_size_needed": 3,
            "confidence": 0.8
        }
        
        patterns_to_test = [
            WorkflowPattern.CONDITIONAL,
            WorkflowPattern.ITERATIVE,
            WorkflowPattern.HIERARCHICAL
        ]
        
        for pattern in patterns_to_test:
            from src.core.models import PromptAnalysis
            analysis = PromptAnalysis(
                recommended_pattern=pattern,
                **base_analysis
            )
            
            estimated_time = self.selector.estimate_execution_time(analysis)
            
            assert estimated_time > 0
            assert isinstance(estimated_time, float)
            
            # Advanced patterns should generally take longer
            if pattern in [WorkflowPattern.ITERATIVE, WorkflowPattern.HIERARCHICAL]:
                assert estimated_time > 50  # Should be substantial for complex patterns

    @patch('src.agents.agent_factory.AgentFactory')
    def test_workflow_error_handling(self, mock_factory):
        """Test error handling across advanced workflows."""
        # Setup failing agent
        failing_agent = Mock()
        failing_agent.name = "failing_agent"
        failing_agent.role = "technical"
        failing_agent.execute_task.side_effect = Exception("Agent execution failed")
        mock_factory.return_value.create_agent.return_value = failing_agent

        patterns_to_test = [
            WorkflowPattern.CONDITIONAL,
            WorkflowPattern.ITERATIVE,
            WorkflowPattern.HIERARCHICAL
        ]
        
        for pattern in patterns_to_test:
            from src.core.models import PromptAnalysis
            analysis = PromptAnalysis(
                complexity_score=0.5,
                urgency_score=0.5,
                quality_requirements=0.7,
                task_types=["technical"],
                dependencies=False,
                parallel_potential=False,
                decision_points=(pattern == WorkflowPattern.CONDITIONAL),
                iteration_needed=(pattern == WorkflowPattern.ITERATIVE),
                team_size_needed=2,
                recommended_pattern=pattern,
                confidence=0.7
            )
            
            workflow = self.selector.select_workflow(analysis, f"Test {pattern.value} workflow")
            
            # Configure workflows appropriately
            if isinstance(workflow, ConditionalWorkflow):
                workflow.add_default_branch(["technical"], ["Default task"])
            elif isinstance(workflow, IterativeWorkflow):
                workflow.max_iterations = 2
            
            # Execute and check error handling
            result = workflow.execute()
            
            # Should handle errors gracefully
            assert result is not None
            assert hasattr(result, 'status')
            assert hasattr(result, 'errors')

    def test_complex_scenario_integration(self):
        """Test complex scenario with multiple patterns."""
        # Complex request that could trigger multiple patterns
        complex_request = """
        Coordinate research and development teams to analyze user requirements. 
        If the requirements are complex, iterate on the design until stakeholders approve.
        Then delegate implementation to specialized teams based on technology choices.
        """
        
        analysis = self.analyzer.analyze_prompt(complex_request)
        
        # Should detect multiple characteristics
        assert analysis.dependencies is True  # "Then delegate"
        assert analysis.decision_points is True  # "If the requirements"
        assert analysis.iteration_needed is True  # "iterate on the design until"
        
        # Complex scenario should suggest hierarchical or hybrid
        assert analysis.recommended_pattern in [WorkflowPattern.HIERARCHICAL, WorkflowPattern.HYBRID]
        
        # Should suggest larger team
        assert analysis.team_size_needed >= 3
        
        # High complexity score due to multiple requirements
        assert analysis.complexity_score > 0.6

    @patch('src.agents.agent_factory.AgentFactory')
    def test_workflow_result_consistency(self, mock_factory):
        """Test that all advanced workflows return consistent result format."""
        mock_agent = Mock()
        mock_agent.name = "test_agent"
        mock_agent.role = "analytical"
        mock_agent.execute_task.return_value = {
            "status": "completed",
            "output": "Test task completed"
        }
        mock_factory.return_value.create_agent.return_value = mock_agent

        workflows_to_test = [
            (WorkflowPattern.CONDITIONAL, ConditionalWorkflow),
            (WorkflowPattern.ITERATIVE, IterativeWorkflow),
            (WorkflowPattern.HIERARCHICAL, HierarchicalWorkflow)
        ]
        
        for pattern, workflow_class in workflows_to_test:
            from src.core.models import PromptAnalysis
            analysis = PromptAnalysis(
                complexity_score=0.5,
                urgency_score=0.5,
                quality_requirements=0.7,
                task_types=["analytical"],
                dependencies=False,
                parallel_potential=False,
                decision_points=(pattern == WorkflowPattern.CONDITIONAL),
                iteration_needed=(pattern == WorkflowPattern.ITERATIVE),
                team_size_needed=2,
                recommended_pattern=pattern,
                confidence=0.7
            )
            
            workflow = workflow_class(analysis, f"Test {pattern.value}")
            
            # Configure workflows
            if isinstance(workflow, ConditionalWorkflow):
                workflow.add_default_branch(["analytical"], ["Analysis task"])
            elif isinstance(workflow, IterativeWorkflow):
                workflow.max_iterations = 2
            
            result = workflow.execute()
            
            # Check consistent result format
            assert hasattr(result, 'workflow_id')
            assert hasattr(result, 'pattern')
            assert hasattr(result, 'status')
            assert hasattr(result, 'steps')
            assert hasattr(result, 'total_execution_time')
            assert hasattr(result, 'output')
            assert hasattr(result, 'errors')
            
            assert result.pattern == pattern
            assert isinstance(result.output, dict)
            assert isinstance(result.errors, list)


if __name__ == "__main__":
    pytest.main([__file__])