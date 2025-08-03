"""
Communication protocols and message types for agent communication.
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


class MessageType(Enum):
    """Types of messages that can be sent between agents."""
    
    # Request-response patterns
    REQUEST = "request"
    RESPONSE = "response"
    
    # Information sharing
    NOTIFICATION = "notification"
    DISCOVERY = "discovery"
    UPDATE = "update"
    
    # Collaboration patterns
    REVIEW_REQUEST = "review_request"
    REVIEW_RESPONSE = "review_response"
    PEER_FEEDBACK = "peer_feedback"
    
    # Workflow coordination
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETION = "task_completion"
    STATUS_UPDATE = "status_update"
    
    # Error handling
    ERROR = "error"
    RETRY_REQUEST = "retry_request"


@dataclass
class Message:
    """
    Message structure for agent-to-agent communication.
    
    This dataclass defines the standard message format used for all
    inter-agent communication within the Shepherd system.
    """
    
    sender: str                      # Agent ID of sender
    recipient: str                   # Agent ID of recipient (or "all" for broadcast)
    message_type: MessageType        # Type of message
    content: Dict[str, Any]         # Message payload
    timestamp: datetime             # When message was created
    message_id: str                 # Unique message identifier
    conversation_id: Optional[str] = None    # Optional conversation thread ID
    priority: int = 5               # Priority level (1=highest, 10=lowest)
    requires_response: bool = False  # Whether sender expects a response
    response_timeout: Optional[int] = None   # Timeout in seconds for response
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "priority": self.priority,
            "requires_response": self.requires_response,
            "response_timeout": self.response_timeout,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        return cls(
            sender=data["sender"],
            recipient=data["recipient"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            message_id=data["message_id"],
            conversation_id=data.get("conversation_id"),
            priority=data.get("priority", 5),
            requires_response=data.get("requires_response", False),
            response_timeout=data.get("response_timeout"),
            metadata=data.get("metadata", {})
        )


class CommunicationProtocol:
    """
    Protocol definitions for different types of agent communication.
    
    This class provides standardized methods for creating common
    message types and handling communication patterns.
    """
    
    @staticmethod
    def create_request(sender: str, recipient: str, request_type: str, 
                      data: Dict[str, Any], timeout: int = 30) -> Message:
        """
        Create a request message.
        
        Args:
            sender: ID of requesting agent
            recipient: ID of target agent
            request_type: Type of request (e.g., "analyze", "review", "execute")
            data: Request data
            timeout: Response timeout in seconds
            
        Returns:
            Formatted request message
        """
        import uuid
        
        return Message(
            sender=sender,
            recipient=recipient,
            message_type=MessageType.REQUEST,
            content={
                "request_type": request_type,
                "data": data
            },
            timestamp=datetime.now(),
            message_id=str(uuid.uuid4()),
            requires_response=True,
            response_timeout=timeout,
            priority=3
        )
    
    @staticmethod
    def create_response(original_message: Message, sender: str, 
                       response_data: Dict[str, Any], success: bool = True) -> Message:
        """
        Create a response message to an original request.
        
        Args:
            original_message: The message being responded to
            sender: ID of responding agent
            response_data: Response data
            success: Whether the request was successful
            
        Returns:
            Formatted response message
        """
        import uuid
        
        return Message(
            sender=sender,
            recipient=original_message.sender,
            message_type=MessageType.RESPONSE,
            content={
                "original_message_id": original_message.message_id,
                "success": success,
                "data": response_data
            },
            timestamp=datetime.now(),
            message_id=str(uuid.uuid4()),
            conversation_id=original_message.conversation_id,
            priority=original_message.priority
        )
    
    @staticmethod
    def create_discovery_share(sender: str, discovery_type: str, 
                             discovery_data: Dict[str, Any], 
                             relevance: float = 0.5) -> Message:
        """
        Create a discovery sharing message.
        
        Args:
            sender: ID of agent making discovery
            discovery_type: Type of discovery
            discovery_data: Discovery content
            relevance: Relevance score (0-1)
            
        Returns:
            Formatted discovery message
        """
        import uuid
        
        return Message(
            sender=sender,
            recipient="all",  # Broadcast to all agents
            message_type=MessageType.DISCOVERY,
            content={
                "discovery_type": discovery_type,
                "data": discovery_data,
                "relevance": relevance
            },
            timestamp=datetime.now(),
            message_id=str(uuid.uuid4()),
            priority=4
        )
    
    @staticmethod
    def create_review_request(sender: str, recipient: str, 
                            review_content: Dict[str, Any],
                            review_criteria: list = None) -> Message:
        """
        Create a peer review request.
        
        Args:
            sender: ID of agent requesting review
            recipient: ID of reviewing agent
            review_content: Content to be reviewed
            review_criteria: List of review criteria
            
        Returns:
            Formatted review request message
        """
        import uuid
        
        return Message(
            sender=sender,
            recipient=recipient,
            message_type=MessageType.REVIEW_REQUEST,
            content={
                "content": review_content,
                "criteria": review_criteria or ["accuracy", "completeness", "quality"]
            },
            timestamp=datetime.now(),
            message_id=str(uuid.uuid4()),
            requires_response=True,
            response_timeout=120,  # 2 minutes for review
            priority=2
        )
    
    @staticmethod
    def create_status_update(sender: str, status: str, 
                           details: Dict[str, Any] = None) -> Message:
        """
        Create a status update message.
        
        Args:
            sender: ID of agent sending update
            status: Current status (e.g., "working", "completed", "error")
            details: Additional status details
            
        Returns:
            Formatted status update message
        """
        import uuid
        
        return Message(
            sender=sender,
            recipient="all",  # Broadcast status updates
            message_type=MessageType.STATUS_UPDATE,
            content={
                "status": status,
                "details": details or {}
            },
            timestamp=datetime.now(),
            message_id=str(uuid.uuid4()),
            priority=6
        )