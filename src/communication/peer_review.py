"""
Peer review mechanism for agent collaboration and quality assurance.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from enum import Enum

from .manager import CommunicationManager
from .protocols import Message, MessageType, CommunicationProtocol

logger = logging.getLogger(__name__)


class ReviewCriteria(Enum):
    """Standard review criteria for peer reviews."""
    
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    BEST_PRACTICES = "best_practices"
    DOCUMENTATION = "documentation"


class ReviewResult:
    """
    Result of a peer review process.
    """
    
    def __init__(self, content_id: str, reviewer_count: int):
        """
        Initialize review result.
        
        Args:
            content_id: ID of content being reviewed
            reviewer_count: Number of reviewers
        """
        self.content_id = content_id
        self.reviewer_count = reviewer_count
        self.reviews: List[Dict[str, Any]] = []
        self.overall_score: Optional[float] = None
        self.consensus_reached: bool = False
        self.final_decision: Optional[str] = None
        self.improvements: List[Dict[str, Any]] = []
        self.timestamp = datetime.now()
    
    def add_review(self, review: Dict[str, Any]) -> None:
        """
        Add a review to the result.
        
        Args:
            review: Review data from a reviewer
        """
        self.reviews.append(review)
        
        # Recalculate overall metrics if we have all reviews
        if len(self.reviews) == self.reviewer_count:
            self._calculate_consensus()
    
    def _calculate_consensus(self) -> None:
        """Calculate consensus from all reviews."""
        if not self.reviews:
            return
        
        # Calculate average score
        scores = [r.get("score", 0.5) for r in self.reviews]
        self.overall_score = sum(scores) / len(scores)
        
        # Check for consensus (all reviews within 0.3 of each other)
        score_range = max(scores) - min(scores)
        self.consensus_reached = score_range <= 0.3
        
        # Determine final decision
        approved_count = sum(1 for r in self.reviews if r.get("approved", True))
        approval_rate = approved_count / len(self.reviews)
        
        if approval_rate >= 0.7:
            self.final_decision = "approved"
        elif approval_rate <= 0.3:
            self.final_decision = "rejected"
        else:
            self.final_decision = "needs_revision"
        
        # Collect improvement suggestions
        for review in self.reviews:
            suggestions = review.get("suggestions", [])
            for suggestion in suggestions:
                self.improvements.append({
                    "reviewer": review.get("reviewer"),
                    "suggestion": suggestion,
                    "priority": suggestion.get("priority", "medium")
                })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "content_id": self.content_id,
            "reviewer_count": self.reviewer_count,
            "reviews": self.reviews,
            "overall_score": self.overall_score,
            "consensus_reached": self.consensus_reached,
            "final_decision": self.final_decision,
            "improvements": self.improvements,
            "timestamp": self.timestamp.isoformat()
        }


class PeerReviewMechanism:
    """
    Peer review mechanism for agent collaboration.
    
    This class orchestrates peer review processes where multiple agents
    review outputs from other agents to ensure quality and accuracy.
    """
    
    def __init__(self, comm_manager: CommunicationManager):
        """
        Initialize peer review mechanism.
        
        Args:
            comm_manager: Communication manager for agent messaging
        """
        self.comm_manager = comm_manager
        
        # Active reviews
        self.active_reviews: Dict[str, ReviewResult] = {}
        self.review_timeouts: Dict[str, datetime] = {}
        
        # Agent capabilities for reviewer selection
        self.agent_capabilities: Dict[str, Set[str]] = {}
        
        # Review statistics
        self.stats = {
            "reviews_initiated": 0,
            "reviews_completed": 0,
            "reviews_timed_out": 0,
            "average_score": 0.0,
            "consensus_rate": 0.0
        }
    
    async def request_review(self, requester_id: str, content: Dict[str, Any],
                           review_criteria: List[str] = None,
                           reviewer_count: int = 2,
                           timeout_minutes: int = 10) -> str:
        """
        Request peer review from qualified agents.
        
        Args:
            requester_id: ID of agent requesting review
            content: Content to be reviewed
            review_criteria: List of review criteria
            reviewer_count: Number of reviewers needed
            timeout_minutes: Review timeout in minutes
            
        Returns:
            Review ID for tracking
        """
        import uuid
        
        review_id = str(uuid.uuid4())
        criteria = review_criteria or [ReviewCriteria.ACCURACY.value, 
                                     ReviewCriteria.COMPLETENESS.value]
        
        # Select qualified reviewers
        qualified_reviewers = await self._select_reviewers(
            requester_id, content, criteria, reviewer_count
        )
        
        if len(qualified_reviewers) < reviewer_count:
            logger.warning(f"Only found {len(qualified_reviewers)} reviewers, needed {reviewer_count}")
            reviewer_count = len(qualified_reviewers)
        
        if reviewer_count == 0:
            raise ValueError("No qualified reviewers available")
        
        # Create review result tracker
        review_result = ReviewResult(review_id, reviewer_count)
        self.active_reviews[review_id] = review_result
        
        # Set timeout
        timeout_time = datetime.now()
        timeout_time = timeout_time.replace(
            minute=timeout_time.minute + timeout_minutes
        )
        self.review_timeouts[review_id] = timeout_time
        
        # Send review requests
        review_tasks = []
        for reviewer_id in qualified_reviewers:
            review_content = {
                **content,
                "review_id": review_id,
                "requester": requester_id
            }
            
            message = CommunicationProtocol.create_review_request(
                requester_id, reviewer_id, review_content, criteria
            )
            
            # Add review tracking metadata
            message.metadata = {
                "review_id": review_id,
                "expected_reviewers": reviewer_count
            }
            
            review_tasks.append(
                self.comm_manager.send_message(message)
            )
        
        # Send all review requests concurrently
        await asyncio.gather(*review_tasks, return_exceptions=True)
        
        self.stats["reviews_initiated"] += 1
        logger.info(f"Review {review_id} initiated with {reviewer_count} reviewers")
        
        return review_id
    
    async def submit_review(self, review_id: str, reviewer_id: str,
                          review_data: Dict[str, Any]) -> bool:
        """
        Submit a review result.
        
        Args:
            review_id: ID of the review
            reviewer_id: ID of the reviewing agent
            review_data: Review result data
            
        Returns:
            True if review was accepted, False if review not found
        """
        if review_id not in self.active_reviews:
            logger.warning(f"Review {review_id} not found")
            return False
        
        review_result = self.active_reviews[review_id]
        
        # Add reviewer info to review data
        enhanced_review = {
            **review_data,
            "reviewer": reviewer_id,
            "submitted_at": datetime.now().isoformat()
        }
        
        review_result.add_review(enhanced_review)
        
        logger.info(f"Review submitted by {reviewer_id} for {review_id}")
        
        # Check if review is complete
        if len(review_result.reviews) == review_result.reviewer_count:
            await self._complete_review(review_id)
        
        return True
    
    async def get_review_status(self, review_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a review.
        
        Args:
            review_id: ID of the review
            
        Returns:
            Review status or None if not found
        """
        if review_id not in self.active_reviews:
            return None
        
        review_result = self.active_reviews[review_id]
        
        return {
            "review_id": review_id,
            "status": "completed" if len(review_result.reviews) == review_result.reviewer_count else "pending",
            "received_reviews": len(review_result.reviews),
            "expected_reviews": review_result.reviewer_count,
            "overall_score": review_result.overall_score,
            "consensus_reached": review_result.consensus_reached,
            "final_decision": review_result.final_decision
        }
    
    async def wait_for_review(self, review_id: str, timeout_seconds: int = 600) -> Optional[ReviewResult]:
        """
        Wait for a review to complete.
        
        Args:
            review_id: ID of the review
            timeout_seconds: Maximum time to wait
            
        Returns:
            Complete review result or None if timed out
        """
        if review_id not in self.active_reviews:
            return None
        
        start_time = datetime.now()
        timeout_delta = timedelta(seconds=timeout_seconds)
        
        while datetime.now() - start_time < timeout_delta:
            review_result = self.active_reviews[review_id]
            
            if len(review_result.reviews) == review_result.reviewer_count:
                return review_result
            
            await asyncio.sleep(1)  # Check every second
        
        logger.warning(f"Review {review_id} timed out")
        self.stats["reviews_timed_out"] += 1
        return None
    
    def register_agent_capabilities(self, agent_id: str, capabilities: Set[str]) -> None:
        """
        Register agent capabilities for reviewer selection.
        
        Args:
            agent_id: ID of the agent
            capabilities: Set of capability identifiers
        """
        self.agent_capabilities[agent_id] = capabilities
        logger.debug(f"Registered capabilities for {agent_id}: {capabilities}")
    
    async def _select_reviewers(self, requester_id: str, content: Dict[str, Any],
                              criteria: List[str], count: int) -> List[str]:
        """
        Select qualified reviewers for content.
        
        Args:
            requester_id: ID of requesting agent
            content: Content to review
            criteria: Review criteria
            count: Number of reviewers needed
            
        Returns:
            List of selected reviewer IDs
        """
        # Get available agents
        agents = await self.comm_manager.get_agent_list()
        
        # Filter out requester
        candidates = [
            agent for agent in agents 
            if agent["agent_id"] != requester_id
        ]
        
        # Score candidates based on capabilities
        scored_candidates = []
        for agent in candidates:
            agent_id = agent["agent_id"]
            capabilities = self.agent_capabilities.get(agent_id, set())
            
            # Calculate relevance score
            score = self._calculate_reviewer_score(capabilities, criteria, content)
            
            scored_candidates.append((score, agent_id))
        
        # Sort by score and select top candidates
        scored_candidates.sort(reverse=True, key=lambda x: x[0])
        selected = [agent_id for score, agent_id in scored_candidates[:count]]
        
        logger.debug(f"Selected reviewers for {criteria}: {selected}")
        return selected
    
    def _calculate_reviewer_score(self, capabilities: Set[str], 
                                criteria: List[str], content: Dict[str, Any]) -> float:
        """
        Calculate reviewer relevance score.
        
        Args:
            capabilities: Agent capabilities
            criteria: Review criteria
            content: Content being reviewed
            
        Returns:
            Relevance score (0-1)
        """
        if not capabilities:
            return 0.1  # Low score for agents with no capabilities
        
        # Score based on capability overlap with criteria
        criteria_set = set(criteria)
        overlap = len(capabilities & criteria_set)
        criteria_score = overlap / len(criteria_set) if criteria_set else 0.5
        
        # Bonus for general capabilities
        general_bonus = 0.2 if "general" in capabilities else 0.0
        
        # Bonus for specialized capabilities
        specialized_capabilities = {"security", "performance", "quality", "review"}
        specialized_bonus = 0.1 * len(capabilities & specialized_capabilities)
        
        total_score = min(1.0, criteria_score + general_bonus + specialized_bonus)
        return total_score
    
    async def _complete_review(self, review_id: str) -> None:
        """
        Complete a review process.
        
        Args:
            review_id: ID of the completed review
        """
        review_result = self.active_reviews[review_id]
        
        # Update statistics
        self.stats["reviews_completed"] += 1
        
        if review_result.overall_score is not None:
            # Update average score
            total_reviews = self.stats["reviews_completed"]
            current_avg = self.stats["average_score"]
            new_avg = ((current_avg * (total_reviews - 1)) + review_result.overall_score) / total_reviews
            self.stats["average_score"] = new_avg
        
        if review_result.consensus_reached:
            # Update consensus rate
            total_reviews = self.stats["reviews_completed"]
            current_rate = self.stats["consensus_rate"]
            new_rate = ((current_rate * (total_reviews - 1)) + 1.0) / total_reviews
            self.stats["consensus_rate"] = new_rate
        
        # Clean up
        if review_id in self.review_timeouts:
            del self.review_timeouts[review_id]
        
        logger.info(f"Review {review_id} completed: {review_result.final_decision} "
                   f"(score: {review_result.overall_score:.2f})")
    
    async def cleanup_expired_reviews(self) -> None:
        """Clean up expired reviews."""
        now = datetime.now()
        expired = [
            review_id for review_id, timeout_time in self.review_timeouts.items()
            if now > timeout_time
        ]
        
        for review_id in expired:
            if review_id in self.active_reviews:
                del self.active_reviews[review_id]
            del self.review_timeouts[review_id]
            self.stats["reviews_timed_out"] += 1
            
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired reviews")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get peer review statistics."""
        return {
            **self.stats,
            "active_reviews": len(self.active_reviews),
            "registered_agents": len(self.agent_capabilities)
        }