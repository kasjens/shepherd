"""
Communication system for agent-to-agent messaging and collaboration.
"""

from .manager import CommunicationManager
from .protocols import Message, MessageType, CommunicationProtocol
from .peer_review import PeerReviewMechanism, ReviewCriteria, ReviewResult

__all__ = [
    "CommunicationManager",
    "Message", 
    "MessageType",
    "CommunicationProtocol",
    "PeerReviewMechanism",
    "ReviewCriteria",
    "ReviewResult"
]