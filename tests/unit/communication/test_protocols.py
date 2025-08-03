"""
Unit tests for communication protocols.
"""

import pytest
from datetime import datetime

from src.communication.protocols import Message, MessageType, CommunicationProtocol


class TestMessage:
    """Test suite for Message class."""
    
    def test_message_creation(self):
        """Test basic message creation."""
        message = Message(
            sender="agent1",
            recipient="agent2",
            message_type=MessageType.NOTIFICATION,
            content={"text": "test message"},
            timestamp=datetime.now(),
            message_id="msg_001"
        )
        
        assert message.sender == "agent1"
        assert message.recipient == "agent2"
        assert message.message_type == MessageType.NOTIFICATION
        assert message.content["text"] == "test message"
        assert message.priority == 5  # Default priority
        assert message.requires_response is False  # Default
    
    def test_message_serialization(self):
        """Test message to/from dict conversion."""
        original = Message(
            sender="agent1",
            recipient="agent2",
            message_type=MessageType.REQUEST,
            content={"request": "data"},
            timestamp=datetime.now(),
            message_id="msg_002",
            priority=1,
            requires_response=True,
            response_timeout=60,
            metadata={"urgent": True}
        )
        
        # Convert to dict
        message_dict = original.to_dict()
        
        # Verify dict structure
        assert isinstance(message_dict, dict)
        assert message_dict["sender"] == "agent1"
        assert message_dict["message_type"] == "request"
        assert message_dict["priority"] == 1
        assert message_dict["metadata"]["urgent"] is True
        
        # Convert back to message
        restored = Message.from_dict(message_dict)
        
        # Verify all fields match
        assert restored.sender == original.sender
        assert restored.recipient == original.recipient
        assert restored.message_type == original.message_type
        assert restored.content == original.content
        assert restored.priority == original.priority
        assert restored.requires_response == original.requires_response
        assert restored.response_timeout == original.response_timeout
        assert restored.metadata == original.metadata


class TestCommunicationProtocol:
    """Test suite for CommunicationProtocol class."""
    
    def test_create_request(self):
        """Test request message creation."""
        message = CommunicationProtocol.create_request(
            sender="agent1",
            recipient="agent2",
            request_type="analyze",
            data={"content": "test data"},
            timeout=45
        )
        
        assert message.message_type == MessageType.REQUEST
        assert message.sender == "agent1"
        assert message.recipient == "agent2"
        assert message.requires_response is True
        assert message.response_timeout == 45
        assert message.content["request_type"] == "analyze"
        assert message.content["data"]["content"] == "test data"
        assert message.priority == 3  # Request priority
    
    def test_create_response(self):
        """Test response message creation."""
        # Create original request
        original = Message(
            sender="agent1",
            recipient="agent2",
            message_type=MessageType.REQUEST,
            content={"request_type": "test"},
            timestamp=datetime.now(),
            message_id="original_001",
            conversation_id="conv_001"
        )
        
        # Create response
        response = CommunicationProtocol.create_response(
            original_message=original,
            sender="agent2",
            response_data={"result": "completed"},
            success=True
        )
        
        assert response.message_type == MessageType.RESPONSE
        assert response.sender == "agent2"
        assert response.recipient == "agent1"  # Reversed
        assert response.conversation_id == "conv_001"
        assert response.content["original_message_id"] == "original_001"
        assert response.content["success"] is True
        assert response.content["data"]["result"] == "completed"
    
    def test_create_discovery_share(self):
        """Test discovery sharing message creation."""
        message = CommunicationProtocol.create_discovery_share(
            sender="agent1",
            discovery_type="performance_issue",
            discovery_data={"issue": "memory leak", "location": "module.py:42"},
            relevance=0.8
        )
        
        assert message.message_type == MessageType.DISCOVERY
        assert message.sender == "agent1"
        assert message.recipient == "all"  # Broadcast
        assert message.content["discovery_type"] == "performance_issue"
        assert message.content["relevance"] == 0.8
        assert message.content["data"]["issue"] == "memory leak"
        assert message.priority == 4  # Discovery priority
    
    def test_create_review_request(self):
        """Test review request message creation."""
        content = {"code": "def test(): pass", "description": "Test function"}
        criteria = ["accuracy", "style", "documentation"]
        
        message = CommunicationProtocol.create_review_request(
            sender="agent1",
            recipient="agent2",
            review_content=content,
            review_criteria=criteria
        )
        
        assert message.message_type == MessageType.REVIEW_REQUEST
        assert message.sender == "agent1"
        assert message.recipient == "agent2"
        assert message.requires_response is True
        assert message.response_timeout == 120  # 2 minutes
        assert message.content["content"] == content
        assert message.content["criteria"] == criteria
        assert message.priority == 2  # High priority for reviews
    
    def test_create_status_update(self):
        """Test status update message creation."""
        details = {"progress": 75, "current_task": "analysis"}
        
        message = CommunicationProtocol.create_status_update(
            sender="agent1",
            status="working",
            details=details
        )
        
        assert message.message_type == MessageType.STATUS_UPDATE
        assert message.sender == "agent1"
        assert message.recipient == "all"  # Broadcast
        assert message.content["status"] == "working"
        assert message.content["details"] == details
        assert message.priority == 6  # Lower priority for status
    
    def test_message_types_enum(self):
        """Test MessageType enum values."""
        # Test that all expected message types exist
        expected_types = [
            "REQUEST", "RESPONSE", "NOTIFICATION", "DISCOVERY", 
            "UPDATE", "REVIEW_REQUEST", "REVIEW_RESPONSE", 
            "PEER_FEEDBACK", "TASK_ASSIGNMENT", "TASK_COMPLETION", 
            "STATUS_UPDATE", "ERROR", "RETRY_REQUEST"
        ]
        
        for type_name in expected_types:
            assert hasattr(MessageType, type_name)
            
        # Test enum values
        assert MessageType.REQUEST.value == "request"
        assert MessageType.RESPONSE.value == "response"
        assert MessageType.DISCOVERY.value == "discovery"
        assert MessageType.REVIEW_REQUEST.value == "review_request"
    
    def test_default_values(self):
        """Test protocol methods use appropriate defaults."""
        # Request with minimal parameters
        request = CommunicationProtocol.create_request(
            "agent1", "agent2", "test", {}
        )
        assert request.response_timeout == 30  # Default timeout
        
        # Discovery with minimal parameters
        discovery = CommunicationProtocol.create_discovery_share(
            "agent1", "finding", {"data": "test"}
        )
        assert discovery.content["relevance"] == 0.5  # Default relevance
        
        # Review request with default criteria
        review = CommunicationProtocol.create_review_request(
            "agent1", "agent2", {"content": "test"}
        )
        expected_criteria = ["accuracy", "completeness", "quality"]
        assert review.content["criteria"] == expected_criteria
        
        # Status update with no details
        status = CommunicationProtocol.create_status_update(
            "agent1", "idle"
        )
        assert status.content["details"] == {}
    
    def test_message_priorities(self):
        """Test that different message types have appropriate priorities."""
        # Review requests should be high priority
        review = CommunicationProtocol.create_review_request(
            "agent1", "agent2", {"test": "content"}
        )
        assert review.priority == 2
        
        # Requests should be medium-high priority
        request = CommunicationProtocol.create_request(
            "agent1", "agent2", "test", {}
        )
        assert request.priority == 3
        
        # Discoveries should be medium priority
        discovery = CommunicationProtocol.create_discovery_share(
            "agent1", "finding", {}
        )
        assert discovery.priority == 4
        
        # Status updates should be lower priority
        status = CommunicationProtocol.create_status_update(
            "agent1", "working"
        )
        assert status.priority == 6