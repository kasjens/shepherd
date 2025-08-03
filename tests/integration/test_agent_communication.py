"""
Integration tests for agent-to-agent communication.
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime

from src.communication.manager import CommunicationManager
from src.communication.protocols import MessageType
from src.communication.peer_review import PeerReviewMechanism
from src.memory.shared_context import SharedContextPool
from tests.fixtures.mock_agents import MockTaskAgent, MockResearchAgent


class TestAgentCommunication:
    """Test agent-to-agent communication integration."""
    
    @pytest_asyncio.fixture
    async def comm_system(self):
        """Create communication system with agents."""
        # Create communication manager
        comm_manager = CommunicationManager()
        await comm_manager.start()
        
        # Create shared context
        shared_context = SharedContextPool("test_workflow")
        
        # Create agents with communication
        task_agent = MockTaskAgent("task_agent")
        task_agent.comm_manager = comm_manager
        task_agent.shared_context = shared_context
        
        research_agent = MockResearchAgent("research_agent")
        research_agent.comm_manager = comm_manager
        research_agent.shared_context = shared_context
        
        # Register agents with communication manager
        comm_manager.register_agent(task_agent.id, task_agent.handle_message, {
            "name": task_agent.name,
            "role": task_agent.role,
            "capabilities": task_agent._get_capabilities()
        })
        
        comm_manager.register_agent(research_agent.id, research_agent.handle_message, {
            "name": research_agent.name,
            "role": research_agent.role,
            "capabilities": research_agent._get_capabilities()
        })
        
        yield {
            "comm_manager": comm_manager,
            "shared_context": shared_context,
            "task_agent": task_agent,
            "research_agent": research_agent
        }
        
        await comm_manager.stop()
    
    @pytest.mark.asyncio
    async def test_direct_agent_messaging(self, comm_system):
        """Test direct message exchange between agents."""
        task_agent = comm_system["task_agent"]
        research_agent = comm_system["research_agent"]
        
        # Task agent sends message to research agent
        response = await task_agent.send_message_to_agent(
            research_agent.id,
            MessageType.NOTIFICATION,
            {"message": "Hello from task agent"},
            requires_response=False
        )
        
        # Wait for message processing
        await asyncio.sleep(0.1)
        
        # Verify message was received and stored in research agent's memory
        stored_message = await research_agent.retrieve_memory(
            f"notification_{task_agent.id}_{int(datetime.now().timestamp())}"
        )
        
        # Note: Exact key might vary due to timestamp, so check if any notification was stored
        search_results = await research_agent.local_memory.search({
            "type": "notification"
        })
        
        assert len(search_results) >= 1
        assert any("Hello from task agent" in str(result["data"]) for result in search_results)
    
    @pytest.mark.asyncio
    async def test_request_response_pattern(self, comm_system):
        """Test request-response communication pattern."""
        task_agent = comm_system["task_agent"]
        research_agent = comm_system["research_agent"]
        
        # Task agent requests information from research agent
        response_data = await task_agent.send_request_to_agent(
            research_agent.id,
            "analyze_data",
            {"dataset": "test_data.csv", "analysis_type": "statistical"},
            timeout=10
        )
        
        # Verify response was received
        assert response_data is not None
        assert "message" in response_data
        assert "analyze_data" in response_data["message"]
    
    @pytest.mark.asyncio
    async def test_discovery_broadcasting(self, comm_system):
        """Test discovery sharing between agents."""
        task_agent = comm_system["task_agent"]
        research_agent = comm_system["research_agent"]
        shared_context = comm_system["shared_context"]
        
        # Task agent makes a discovery
        discovery_data = {
            "type": "performance_bottleneck",
            "location": "module.py:42",
            "impact": "high",
            "suggested_fix": "optimize_query()"
        }
        
        await task_agent.share_discovery("performance_issue", discovery_data, relevance=0.9)
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        # Verify discovery was shared in context
        discoveries = await shared_context.search({"context_type": "discovery"})
        assert len(discoveries) >= 1
        
        discovery_found = False
        for discovery in discoveries:
            if discovery["data"]["type"] == "performance_bottleneck":
                discovery_found = True
                assert discovery["metadata"]["relevance"] == 0.9
                break
        
        assert discovery_found, "Discovery not found in shared context"
        
        # Verify research agent can access the discovery
        shared_discoveries = await research_agent.get_shared_context(context_type="discovery")
        assert len(shared_discoveries) >= 1
    
    @pytest.mark.asyncio
    async def test_status_broadcasting(self, comm_system):
        """Test status update broadcasting."""
        task_agent = comm_system["task_agent"]
        research_agent = comm_system["research_agent"]
        
        # Task agent broadcasts status
        await task_agent.broadcast_status("working", {
            "current_task": "data_analysis",
            "progress": 0.75,
            "eta": "5 minutes"
        })
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        # Verify research agent received status update
        search_results = await research_agent.local_memory.search({
            "type": "status"
        })
        
        assert len(search_results) >= 1
        status_found = False
        for result in search_results:
            if result["data"]["status"] == "working":
                status_found = True
                assert result["data"]["details"]["current_task"] == "data_analysis"
                break
        
        assert status_found, "Status update not received"
    
    @pytest.mark.asyncio
    async def test_peer_review_integration(self, comm_system):
        """Test peer review mechanism with real agents."""
        comm_manager = comm_system["comm_manager"]
        task_agent = comm_system["task_agent"]
        research_agent = comm_system["research_agent"]
        
        # Create peer review mechanism
        peer_review = PeerReviewMechanism(comm_manager)
        
        # Register agent capabilities
        peer_review.register_agent_capabilities(task_agent.id, {"general", "task_execution"})
        peer_review.register_agent_capabilities(research_agent.id, {"research", "analysis", "review"})
        
        # Content to be reviewed
        content = {
            "type": "analysis_report",
            "findings": ["Finding 1", "Finding 2"],
            "methodology": "statistical_analysis",
            "confidence": 0.85
        }
        
        # Request peer review
        review_id = await peer_review.request_review(
            task_agent.id,
            content,
            ["accuracy", "completeness"],
            reviewer_count=1,
            timeout_minutes=5
        )
        
        # Wait a bit for review requests to be sent
        await asyncio.sleep(0.1)
        
        # Check review status
        status = await peer_review.get_review_status(review_id)
        assert status is not None
        assert status["status"] == "pending"
        assert status["expected_reviews"] == 1
        
        # Simulate review completion by research agent
        # In real scenario, this would happen automatically through message handling
        review_data = {
            "score": 0.8,
            "feedback": "Good analysis with minor suggestions",
            "approved": True,
            "suggestions": [
                {"text": "Add confidence intervals", "priority": "medium"}
            ]
        }
        
        await peer_review.submit_review(review_id, research_agent.id, review_data)
        
        # Verify review completion
        final_status = await peer_review.get_review_status(review_id)
        assert final_status["status"] == "completed"
        assert final_status["received_reviews"] == 1
    
    @pytest.mark.asyncio
    async def test_memory_and_communication_integration(self, comm_system):
        """Test integration between memory system and communication."""
        task_agent = comm_system["task_agent"]
        research_agent = comm_system["research_agent"]
        shared_context = comm_system["shared_context"]
        
        # Task agent stores information in local memory
        await task_agent.store_memory("current_analysis", {
            "dataset": "sales_data.csv",
            "status": "in_progress",
            "preliminary_results": {"trend": "upward", "confidence": 0.7}
        })
        
        # Task agent shares discovery via communication
        await task_agent.share_discovery("data_trend", {
            "trend": "upward",
            "significance": "high",
            "timeframe": "Q3-Q4"
        }, relevance=0.8)
        
        # Task agent sends request to research agent
        response = await task_agent.send_request_to_agent(
            research_agent.id,
            "validate_trend",
            {"trend_data": {"trend": "upward", "confidence": 0.7}},
            timeout=10
        )
        
        # Wait for all processing
        await asyncio.sleep(0.2)
        
        # Verify task agent's local memory
        stored_analysis = await task_agent.retrieve_memory("current_analysis")
        assert stored_analysis is not None
        assert stored_analysis["dataset"] == "sales_data.csv"
        
        # Verify shared context has discovery
        discoveries = await shared_context.search({"context_type": "discovery"})
        assert len(discoveries) >= 1
        
        # Verify research agent received and processed information
        search_results = await research_agent.local_memory.search({"type": "discovery"})
        assert len(search_results) >= 1
        
        # Verify response was received
        assert response is not None
        assert "validate_trend" in response["message"]
    
    @pytest.mark.asyncio
    async def test_multi_agent_collaboration_scenario(self, comm_system):
        """Test complex multi-agent collaboration scenario."""
        task_agent = comm_system["task_agent"]
        research_agent = comm_system["research_agent"]
        shared_context = comm_system["shared_context"]
        
        # Scenario: Task agent finds an issue, research agent investigates,
        # and they collaborate on a solution
        
        # Step 1: Task agent discovers an issue
        await task_agent.share_discovery("system_error", {
            "error_type": "database_timeout",
            "frequency": "increasing",
            "affected_queries": ["user_analytics", "report_generation"],
            "urgency": "high"
        }, relevance=0.9)
        
        # Step 2: Task agent requests investigation from research agent
        investigation_response = await task_agent.send_request_to_agent(
            research_agent.id,
            "investigate_error",
            {
                "error_type": "database_timeout",
                "context": "performance_degradation"
            },
            timeout=15
        )
        
        # Step 3: Research agent shares its findings
        await research_agent.share_discovery("root_cause", {
            "cause": "missing_database_index",
            "affected_tables": ["users", "analytics_events"],
            "solution": "CREATE INDEX idx_user_timestamp ON users(created_at)",
            "estimated_improvement": "80% query speed increase"
        }, relevance=0.95)
        
        # Wait for all processing
        await asyncio.sleep(0.2)
        
        # Verify collaboration artifacts
        
        # Check shared discoveries
        all_discoveries = await shared_context.search({"context_type": "discovery"})
        assert len(all_discoveries) >= 2
        
        discovery_types = [d["data"].get("error_type") or d["data"].get("cause") for d in all_discoveries]
        assert "database_timeout" in str(discovery_types)
        assert "missing_database_index" in str(discovery_types)
        
        # Check that both agents have relevant information
        task_agent_discoveries = await task_agent.local_memory.search({"type": "discovery"})
        research_agent_discoveries = await research_agent.local_memory.search({"type": "discovery"})
        
        assert len(task_agent_discoveries) >= 1  # Should have research agent's discovery
        assert len(research_agent_discoveries) >= 1  # Should have task agent's discovery
        
        # Verify investigation response
        assert investigation_response is not None
        assert "investigate_error" in investigation_response["message"]
    
    @pytest.mark.asyncio
    async def test_communication_error_handling(self, comm_system):
        """Test error handling in agent communication."""
        task_agent = comm_system["task_agent"]
        
        # Test sending message to non-existent agent
        response = await task_agent.send_request_to_agent(
            "non_existent_agent",
            "test_request",
            {"data": "test"},
            timeout=2
        )
        
        # Should return None for failed communication
        assert response is None
        
        # Test timeout scenario - simulate by requesting from agent without comm_manager
        isolated_agent = MockTaskAgent("isolated_agent")
        # Don't register with comm_manager
        
        response = await isolated_agent.send_request_to_agent(
            task_agent.id,
            "test_request",
            {"data": "test"},
            timeout=1
        )
        
        # Should return None due to no comm_manager
        assert response is None