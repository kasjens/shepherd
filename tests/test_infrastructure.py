"""
Infrastructure validation tests for Shepherd test framework.

These tests verify that the test infrastructure itself is working correctly.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from tests.fixtures.mock_agents import (
    MockTaskAgent, 
    MockSystemAgent, 
    MockResearchAgent, 
    MockCreativeAgent,
    MockCommunicationManager,
    create_mock_agent_team,
    create_collaborative_scenario
)
from tests.fixtures.sample_data import (
    get_sample_data,
    SAMPLE_PROMPTS,
    SAMPLE_CONTEXTS
)


class TestFixtureAvailability:
    """Test that all fixtures are available and working."""
    
    def test_sample_prompts_available(self):
        """Verify sample prompts are loaded correctly."""
        prompts = get_sample_data("prompts")
        assert isinstance(prompts, dict)
        assert "simple" in prompts
        assert "complex" in prompts
        assert len(prompts["simple"]) > 0
        assert len(prompts["complex"]) > 0
    
    def test_sample_contexts_available(self):
        """Verify sample contexts are loaded correctly."""
        contexts = get_sample_data("contexts")
        assert isinstance(contexts, dict)
        assert "python_web" in contexts
        assert "react_frontend" in contexts
        
        python_context = contexts["python_web"]
        assert "project_folder" in python_context
        assert "language" in python_context
        assert python_context["language"] == "python"
    
    def test_sample_data_getter_function(self):
        """Test the get_sample_data utility function."""
        # Test valid category
        steps = get_sample_data("steps", "sequential")
        assert isinstance(steps, list)
        assert len(steps) > 0
        
        # Test invalid category
        with pytest.raises(ValueError, match="Unknown category"):
            get_sample_data("invalid_category")
        
        # Test invalid subcategory
        with pytest.raises(ValueError, match="Unknown subcategory"):
            get_sample_data("prompts", "invalid_subcategory")


class TestMockAgents:
    """Test mock agent implementations."""
    
    @pytest.mark.asyncio
    async def test_mock_task_agent_creation(self):
        """Verify MockTaskAgent can be created and has correct attributes."""
        agent = MockTaskAgent("test_agent")
        assert agent.name == "test_agent"
        assert agent.execution_count == 0
        assert agent.execution_history == []
        assert not agent.should_fail
    
    @pytest.mark.asyncio
    async def test_mock_task_agent_execution(self):
        """Verify MockTaskAgent execution works correctly."""
        agent = MockTaskAgent("test_agent")
        
        result = await agent.execute("Create a hello world function")
        
        assert result["success"] is True
        assert "output" in result
        assert "metadata" in result
        assert result["metadata"]["agent"] == "test_agent"
        assert agent.execution_count == 1
        assert len(agent.execution_history) == 1
    
    @pytest.mark.asyncio
    async def test_mock_task_agent_failure_mode(self):
        """Test MockTaskAgent failure mode."""
        agent = MockTaskAgent("test_agent")
        agent.set_failure_mode(True)
        
        result = await agent.execute("test task")
        
        assert result["success"] is False
        assert "error" in result
        assert "Mock agent configured to fail" in result["error"]
    
    @pytest.mark.asyncio
    async def test_mock_task_agent_execution_delay(self):
        """Test MockTaskAgent execution delay configuration."""
        import time
        
        agent = MockTaskAgent("test_agent")
        agent.set_execution_delay(0.2)
        
        start_time = time.time()
        await agent.execute("test task")
        execution_time = time.time() - start_time
        
        assert execution_time >= 0.2
        assert execution_time < 0.3  # Allow some tolerance
    
    @pytest.mark.asyncio
    async def test_mock_system_agent(self):
        """Test MockSystemAgent functionality."""
        agent = MockSystemAgent("system_agent")
        
        result = await agent.execute("monitor system status")
        
        assert result["success"] is True
        assert "output" in result
        assert isinstance(result["output"], dict)
        assert "cpu_usage" in result["output"]
        assert len(agent.system_calls) == 1
    
    @pytest.mark.asyncio
    async def test_mock_research_agent(self):
        """Test MockResearchAgent functionality."""
        agent = MockResearchAgent("research_agent")
        
        result = await agent.execute("research python best practices")
        
        assert result["success"] is True
        assert "output" in result
        assert "research_findings" in result["output"]
        assert "sources" in result["output"]
        assert "confidence" in result["output"]
    
    @pytest.mark.asyncio
    async def test_mock_creative_agent(self):
        """Test MockCreativeAgent functionality."""
        agent = MockCreativeAgent("creative_agent")
        
        result = await agent.execute("create documentation for the API")
        
        assert result["success"] is True
        assert "output" in result
        assert result["metadata"]["output_type"] == "documentation"
    
    def test_mock_agent_team_creation(self):
        """Test creating a team of mock agents."""
        team = create_mock_agent_team()
        
        assert len(team) == 4
        assert any(agent.name == "task_agent_1" for agent in team)
        assert any(agent.name == "system_agent_1" for agent in team)
        assert any(agent.name == "research_agent_1" for agent in team)
        assert any(agent.name == "creative_agent_1" for agent in team)


class TestMockCommunication:
    """Test mock communication system."""
    
    @pytest.mark.asyncio
    async def test_communication_manager_creation(self):
        """Test MockCommunicationManager creation."""
        comm = MockCommunicationManager()
        assert len(comm.agents) == 0
        assert len(comm.message_history) == 0
        assert len(comm.broadcasts) == 0
    
    def test_agent_registration(self):
        """Test agent registration with communication manager."""
        comm = MockCommunicationManager()
        
        def mock_handler(message):
            return f"Handled: {message}"
        
        comm.register_agent("agent1", mock_handler)
        assert "agent1" in comm.agents
        assert comm.agents["agent1"] == mock_handler
    
    @pytest.mark.asyncio
    async def test_message_sending(self):
        """Test message sending between agents."""
        comm = MockCommunicationManager()
        received_messages = []
        
        async def handler(message):
            received_messages.append(message)
        
        comm.register_agent("agent1", handler)
        
        await comm.send_message("sender", "agent1", "test", {"data": "hello"})
        
        assert len(comm.message_history) == 1
        assert comm.message_history[0]["sender"] == "sender"
        assert comm.message_history[0]["recipient"] == "agent1"
        assert len(received_messages) == 1
    
    @pytest.mark.asyncio
    async def test_broadcasting(self):
        """Test message broadcasting."""
        comm = MockCommunicationManager()
        agent1_messages = []
        agent2_messages = []
        
        async def handler1(message):
            agent1_messages.append(message)
        
        async def handler2(message):
            agent2_messages.append(message)
        
        comm.register_agent("agent1", handler1)
        comm.register_agent("agent2", handler2)
        
        await comm.broadcast("sender", "announcement", {"message": "hello all"})
        
        assert len(comm.broadcasts) == 1
        assert len(agent1_messages) == 1
        assert len(agent2_messages) == 1
    
    def test_collaborative_scenario_creation(self):
        """Test collaborative scenario setup."""
        scenario = create_collaborative_scenario()
        
        assert "agents" in scenario
        assert "communication_manager" in scenario
        assert "scenario" in scenario
        
        assert len(scenario["agents"]) == 4
        assert isinstance(scenario["communication_manager"], MockCommunicationManager)
        assert "expected_collaboration" in scenario["scenario"]


class TestPytestFixtures:
    """Test that pytest fixtures are working correctly."""
    
    def test_sample_project_context(self, sample_project_context):
        """Test sample_project_context fixture."""
        assert isinstance(sample_project_context, dict)
        assert "project_folder" in sample_project_context
        assert "language" in sample_project_context
        assert sample_project_context["language"] == "python"
    
    def test_sample_prompts(self, sample_prompt, simple_prompt, complex_prompt):
        """Test prompt fixtures."""
        assert isinstance(sample_prompt, str)
        assert len(sample_prompt) > 0
        
        assert isinstance(simple_prompt, str)
        assert "hello world" in simple_prompt.lower()
        
        assert isinstance(complex_prompt, str)
        assert len(complex_prompt) > len(simple_prompt)
    
    def test_mock_agent_fixture(self, mock_agent):
        """Test mock_agent fixture."""
        assert mock_agent.name == "test_agent"
        assert mock_agent.agent_type == "task"
        assert hasattr(mock_agent, "execute")
    
    @pytest.mark.asyncio
    async def test_mock_agent_fixture_execution(self, mock_agent):
        """Test mock_agent fixture execution."""
        result = await mock_agent.execute("test task")
        
        assert result["success"] is True
        assert "output" in result
        assert result["output"] == "Mock agent execution result"
    
    def test_temp_project_dir(self, temp_project_dir):
        """Test temporary project directory fixture."""
        import os
        assert os.path.exists(temp_project_dir)
        assert os.path.isdir(temp_project_dir)
        
        # Check that sample files were created
        main_py = os.path.join(temp_project_dir, "main.py")
        assert os.path.exists(main_py)
        
        src_dir = os.path.join(temp_project_dir, "src")
        assert os.path.exists(src_dir)
        assert os.path.isdir(src_dir)
    
    def test_mock_shared_context(self, mock_shared_context):
        """Test mock_shared_context fixture."""
        assert hasattr(mock_shared_context, "store")
        assert hasattr(mock_shared_context, "retrieve")
        assert hasattr(mock_shared_context, "broadcast_update")
    
    def test_sample_execution_steps(self, sample_execution_steps):
        """Test sample_execution_steps fixture."""
        assert isinstance(sample_execution_steps, list)
        assert len(sample_execution_steps) > 0
        
        step = sample_execution_steps[0]
        assert hasattr(step, "id")
        assert hasattr(step, "command")
        assert hasattr(step, "description")
        assert hasattr(step, "status")
    
    def test_performance_tracker(self, performance_tracker):
        """Test performance_tracker fixture."""
        assert hasattr(performance_tracker, "start")
        assert hasattr(performance_tracker, "stop")
        
        performance_tracker.start()
        import time
        time.sleep(0.01)  # Small delay
        metrics = performance_tracker.stop()
        
        assert "duration" in metrics
        assert "memory_delta" in metrics
        assert metrics["duration"] > 0


class TestAsyncInfrastructure:
    """Test async testing infrastructure."""
    
    @pytest.mark.asyncio
    async def test_async_test_execution(self):
        """Test that async tests run correctly."""
        await asyncio.sleep(0.01)  # Small async operation
        assert True  # If we get here, async is working
    
    @pytest.mark.asyncio
    async def test_async_mock_usage(self):
        """Test using AsyncMock in tests."""
        mock_func = AsyncMock(return_value="async result")
        result = await mock_func("test input")
        
        assert result == "async result"
        mock_func.assert_called_once_with("test input")
    
    @pytest.mark.asyncio
    async def test_multiple_async_operations(self):
        """Test concurrent async operations."""
        async def mock_operation(value):
            await asyncio.sleep(0.01)
            return value * 2
        
        tasks = [mock_operation(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        assert results == [0, 2, 4]


class TestErrorHandling:
    """Test error handling in test infrastructure."""
    
    @pytest.mark.asyncio
    async def test_mock_agent_error_handling(self):
        """Test that mock agents handle errors gracefully."""
        agent = MockTaskAgent("error_agent")
        agent.set_failure_mode(True)
        
        result = await agent.execute("failing task")
        
        assert result["success"] is False
        assert "error" in result
        # Should not raise an exception
    
    def test_invalid_sample_data_access(self):
        """Test error handling for invalid sample data access."""
        with pytest.raises(ValueError):
            get_sample_data("nonexistent_category")
    
    @pytest.mark.asyncio
    async def test_communication_with_unregistered_agent(self):
        """Test sending message to unregistered agent."""
        comm = MockCommunicationManager()
        
        # Should not raise an error, just not deliver
        await comm.send_message("sender", "nonexistent", "test", {})
        
        assert len(comm.message_history) == 1  # Message recorded but not delivered


# Integration test to verify everything works together
class TestFullInfrastructureIntegration:
    """Integration tests for the complete test infrastructure."""
    
    @pytest.mark.asyncio
    async def test_complete_mock_scenario(self):
        """Test a complete scenario using all mock components."""
        # Create collaborative scenario
        scenario = create_collaborative_scenario()
        agents = scenario["agents"]
        comm = scenario["communication_manager"]
        
        # Execute tasks with multiple agents
        task = "Analyze project and create implementation plan"
        results = []
        
        for agent in agents:
            result = await agent.execute(task)
            results.append(result)
        
        # Verify all agents executed successfully
        assert len(results) == 4
        assert all(result["success"] for result in results)
        
        # Test communication between agents
        await comm.broadcast("orchestrator", "task_complete", {
            "task": task,
            "results": len(results)
        })
        
        assert comm.get_broadcast_count() == 1
    
    def test_data_flow_through_fixtures(self, sample_prompt, sample_project_context, mock_agent):
        """Test that data flows correctly through fixtures."""
        # Verify we can use multiple fixtures together
        assert isinstance(sample_prompt, str)
        assert isinstance(sample_project_context, dict)
        assert mock_agent.name == "test_agent"
        
        # Simulate using them together
        context_with_prompt = {
            **sample_project_context,
            "prompt": sample_prompt
        }
        
        assert "prompt" in context_with_prompt
        assert "project_folder" in context_with_prompt