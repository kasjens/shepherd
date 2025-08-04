"""
Learning System for Shepherd - Phase 8 Implementation

This module implements advanced learning capabilities including:
- User feedback processing
- Pattern recognition and optimization
- Adaptive behavior system
- Continuous improvement mechanisms
"""

from .feedback_processor import UserFeedbackProcessor, FeedbackType
from .pattern_learner import PatternLearner
from .adaptive_system import AdaptiveBehaviorSystem

__all__ = [
    "UserFeedbackProcessor",
    "FeedbackType",
    "PatternLearner",
    "AdaptiveBehaviorSystem",
]