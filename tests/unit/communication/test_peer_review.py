"""
Unit tests for peer review mechanism.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from src.communication.manager import CommunicationManager
from src.communication.peer_review import (
    PeerReviewMechanism, ReviewResult, ReviewCriteria
)
from src.communication.protocols import MessageType


class TestReviewResult:
    """Test suite for ReviewResult class."""
    
    def test_review_result_initialization(self):
        """Test ReviewResult initialization."""
        result = ReviewResult("content_123", 3)
        
        assert result.content_id == "content_123"
        assert result.reviewer_count == 3
        assert result.reviews == []
        assert result.overall_score is None
        assert result.consensus_reached is False
        assert result.final_decision is None
        assert isinstance(result.timestamp, datetime)
    
    def test_add_single_review(self):
        """Test adding a single review."""
        result = ReviewResult("content_123", 1)
        
        review = {
            "score": 0.8,
            "feedback": "Good work",
            "approved": True,
            "suggestions": []
        }
        
        result.add_review(review)
        
        assert len(result.reviews) == 1
        assert result.overall_score == 0.8
        assert result.consensus_reached is True  # Only one review
        assert result.final_decision == "approved"
    
    def test_multiple_reviews_consensus(self):
        """Test consensus calculation with multiple reviews."""
        result = ReviewResult("content_123", 3)
        
        # Add three similar reviews (consensus expected)
        reviews = [
            {"score": 0.8, "approved": True, "suggestions": []},
            {"score": 0.75, "approved": True, "suggestions": []},
            {"score": 0.85, "approved": True, "suggestions": []}
        ]
        
        for review in reviews:
            result.add_review(review)
        
        assert len(result.reviews) == 3
        assert abs(result.overall_score - 0.8) < 0.01  # Average
        assert result.consensus_reached is True  # Range within 0.3
        assert result.final_decision == "approved"  # All approved
    
    def test_multiple_reviews_no_consensus(self):
        """Test with reviews that don't reach consensus."""
        result = ReviewResult("content_123", 3)
        
        # Add divergent reviews
        reviews = [
            {"score": 0.9, "approved": True, "suggestions": []},
            {"score": 0.3, "approved": False, "suggestions": []},
            {"score": 0.6, "approved": True, "suggestions": []}
        ]
        
        for review in reviews:
            result.add_review(review)
        
        assert result.consensus_reached is False  # Range > 0.3
        assert result.final_decision == "needs_revision"  # Mixed approval
    
    def test_review_rejection(self):
        """Test when majority rejects content."""
        result = ReviewResult("content_123", 3)
        
        reviews = [
            {"score": 0.3, "approved": False, "suggestions": []},
            {"score": 0.2, "approved": False, "suggestions": []},
            {"score": 0.4, "approved": False, "suggestions": []}
        ]
        
        for review in reviews:
            result.add_review(review)
        
        assert result.final_decision == "rejected"
    
    def test_suggestions_collection(self):
        """Test collection of improvement suggestions."""
        result = ReviewResult("content_123", 2)
        
        reviews = [
            {
                "score": 0.7,
                "approved": True,
                "reviewer": "agent1",
                "suggestions": [
                    {"text": "Add more comments", "priority": "low"},
                    {"text": "Improve error handling", "priority": "high"}
                ]
            },
            {
                "score": 0.6,
                "approved": True,
                "reviewer": "agent2",
                "suggestions": [
                    {"text": "Optimize performance", "priority": "medium"}
                ]
            }
        ]
        
        for review in reviews:
            result.add_review(review)
        
        assert len(result.improvements) == 3
        assert any("comments" in imp["suggestion"]["text"] for imp in result.improvements)
        assert any("performance" in imp["suggestion"]["text"] for imp in result.improvements)


class TestPeerReviewMechanism:
    """Test suite for PeerReviewMechanism."""
    
    @pytest.fixture
    async def comm_manager(self):
        """Create communication manager for testing."""
        manager = CommunicationManager()
        await manager.start()
        yield manager
        await manager.stop()
    
    @pytest.fixture
    def peer_review(self, comm_manager):
        """Create peer review mechanism for testing."""
        return PeerReviewMechanism(comm_manager)
    
    @pytest.fixture
    def sample_agents(self, comm_manager):
        """Create sample agents with capabilities."""
        agents_data = {
            "security_agent": {"capabilities": {"security", "code_review"}},
            "quality_agent": {"capabilities": {"quality", "testing", "review"}},
            "general_agent": {"capabilities": {"general"}}
        }
        
        # Register agents
        for agent_id, data in agents_data.items():
            handler = AsyncMock()
            comm_manager.register_agent(agent_id, handler, data)
        
        return agents_data
    
    def test_agent_capabilities_registration(self, peer_review):
        """Test registering agent capabilities."""
        capabilities = {"security", "code_review", "quality"}
        
        peer_review.register_agent_capabilities("test_agent", capabilities)
        
        assert "test_agent" in peer_review.agent_capabilities
        assert peer_review.agent_capabilities["test_agent"] == capabilities
    
    def test_reviewer_score_calculation(self, peer_review):
        """Test reviewer relevance scoring."""
        # Test exact capability match
        capabilities = {"security", "quality"}
        criteria = ["security", "quality"]
        score = peer_review._calculate_reviewer_score(capabilities, criteria, {})
        assert score == 1.0  # Perfect match
        
        # Test partial match
        capabilities = {"security", "general"}
        criteria = ["security", "quality"]
        score = peer_review._calculate_reviewer_score(capabilities, criteria, {})
        assert 0.5 < score < 1.0  # Partial match with general bonus
        
        # Test no capabilities
        capabilities = set()
        criteria = ["security"]
        score = peer_review._calculate_reviewer_score(capabilities, criteria, {})
        assert score == 0.1  # Low score for no capabilities
    
    @pytest.mark.asyncio
    async def test_reviewer_selection(self, peer_review, sample_agents):
        """Test selecting qualified reviewers."""
        # Register capabilities
        peer_review.register_agent_capabilities("security_agent", {"security", "code_review"})
        peer_review.register_agent_capabilities("quality_agent", {"quality", "testing"})
        peer_review.register_agent_capabilities("general_agent", {"general"})
        
        # Select reviewers for security criteria
        reviewers = await peer_review._select_reviewers(
            "requester", {}, ["security"], 2
        )
        
        # Should prefer security_agent and include others if needed
        assert len(reviewers) <= 2
        assert "security_agent" in reviewers
    
    @pytest.mark.asyncio
    async def test_review_request_initiation(self, peer_review, sample_agents):
        """Test initiating a review request."""
        # Register capabilities
        for agent_id, data in sample_agents.items():
            peer_review.register_agent_capabilities(agent_id, data["capabilities"])
        
        content = {"code": "def test(): pass", "description": "Test function"}
        criteria = [ReviewCriteria.QUALITY.value, ReviewCriteria.ACCURACY.value]
        
        # Request review
        review_id = await peer_review.request_review(
            "requester_agent", content, criteria, reviewer_count=2
        )
        
        assert review_id in peer_review.active_reviews
        assert peer_review.stats["reviews_initiated"] == 1
        
        # Check review status
        status = await peer_review.get_review_status(review_id)
        assert status["status"] == "pending"
        assert status["expected_reviews"] == 2
        assert status["received_reviews"] == 0
    
    @pytest.mark.asyncio
    async def test_review_submission(self, peer_review):
        """Test submitting review results."""
        # Create active review
        review_id = "test_review_001"
        result = ReviewResult(review_id, 2)
        peer_review.active_reviews[review_id] = result
        
        # Submit first review
        review_data = {
            "score": 0.8,
            "feedback": "Good implementation",
            "approved": True,
            "suggestions": [{"text": "Add unit tests", "priority": "medium"}]
        }
        
        success = await peer_review.submit_review(review_id, "reviewer1", review_data)
        assert success is True
        assert len(result.reviews) == 1
        
        # Submit second review to complete
        review_data2 = {
            "score": 0.75,
            "feedback": "Minor improvements needed",
            "approved": True,
            "suggestions": []
        }
        
        await peer_review.submit_review(review_id, "reviewer2", review_data2)
        
        # Review should be completed
        assert len(result.reviews) == 2
        assert result.overall_score is not None
        assert peer_review.stats["reviews_completed"] == 1
    
    @pytest.mark.asyncio
    async def test_review_not_found(self, peer_review):
        """Test submitting review for non-existent review ID."""
        success = await peer_review.submit_review(
            "non_existent", "reviewer", {"score": 0.5}
        )
        assert success is False
    
    @pytest.mark.asyncio
    async def test_wait_for_review(self, peer_review):
        """Test waiting for review completion."""
        # Create and start review
        review_id = "test_review_002"
        result = ReviewResult(review_id, 1)
        peer_review.active_reviews[review_id] = result
        
        # Simulate review completion after delay
        async def complete_review():
            await asyncio.sleep(0.1)
            await peer_review.submit_review(review_id, "reviewer", {
                "score": 0.9,
                "approved": True
            })
        
        # Start completion task
        completion_task = asyncio.create_task(complete_review())
        
        # Wait for review
        completed_result = await peer_review.wait_for_review(review_id, timeout_seconds=5)
        
        await completion_task
        
        assert completed_result is not None
        assert len(completed_result.reviews) == 1
        assert completed_result.overall_score == 0.9
    
    @pytest.mark.asyncio
    async def test_wait_for_review_timeout(self, peer_review):
        """Test waiting for review that times out."""
        # Create review that won't be completed
        review_id = "test_review_timeout"
        result = ReviewResult(review_id, 1)
        peer_review.active_reviews[review_id] = result
        
        # Wait with very short timeout
        completed_result = await peer_review.wait_for_review(review_id, timeout_seconds=0.1)
        
        assert completed_result is None
        assert peer_review.stats["reviews_timed_out"] >= 1
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_reviews(self, peer_review):
        """Test cleanup of expired reviews."""
        # Create expired review
        review_id = "expired_review"
        result = ReviewResult(review_id, 1)
        peer_review.active_reviews[review_id] = result
        
        # Set timeout in the past
        peer_review.review_timeouts[review_id] = datetime.now() - timedelta(minutes=1)
        
        # Run cleanup
        await peer_review.cleanup_expired_reviews()
        
        # Review should be removed
        assert review_id not in peer_review.active_reviews
        assert review_id not in peer_review.review_timeouts
        assert peer_review.stats["reviews_timed_out"] >= 1
    
    def test_statistics_tracking(self, peer_review):
        """Test statistics collection."""
        # Register some capabilities
        peer_review.register_agent_capabilities("agent1", {"security"})
        peer_review.register_agent_capabilities("agent2", {"quality"})
        
        # Add some active reviews
        peer_review.active_reviews["review1"] = ReviewResult("content1", 2)
        peer_review.active_reviews["review2"] = ReviewResult("content2", 1)
        
        stats = peer_review.get_statistics()
        
        assert stats["registered_agents"] == 2
        assert stats["active_reviews"] == 2
        assert "reviews_initiated" in stats
        assert "reviews_completed" in stats
        assert "consensus_rate" in stats
    
    def test_review_criteria_enum(self):
        """Test ReviewCriteria enum values."""
        expected_criteria = [
            "ACCURACY", "COMPLETENESS", "QUALITY", "SECURITY", 
            "PERFORMANCE", "MAINTAINABILITY", "BEST_PRACTICES", "DOCUMENTATION"
        ]
        
        for criteria in expected_criteria:
            assert hasattr(ReviewCriteria, criteria)
        
        # Test specific values
        assert ReviewCriteria.ACCURACY.value == "accuracy"
        assert ReviewCriteria.SECURITY.value == "security"
        assert ReviewCriteria.QUALITY.value == "quality"