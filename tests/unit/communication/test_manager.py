"""
Unit tests for CommunicationManager.
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from src.communication.manager import CommunicationManager
from src.communication.protocols import Message, MessageType, CommunicationProtocol


class TestCommunicationManager:
    """Test suite for CommunicationManager."""
    
    @pytest_asyncio.fixture
    async def comm_manager(self):
        """Create a communication manager for testing."""
        manager = CommunicationManager(max_queue_size=100, default_timeout=5)
        await manager.start()
        yield manager
        await manager.stop()
    
    @pytest.fixture
    def sample_agents(self):
        """Create sample agent handlers for testing."""
        messages_received = {"agent1": [], "agent2": [], "agent3": []}
        
        async def create_handler(agent_id):
            async def handler(message: Message):
                messages_received[agent_id].append(message)
            return handler
        
        return {
            "handlers": {
                "agent1": create_handler("agent1"),
                "agent2": create_handler("agent2"),
                "agent3": create_handler("agent3")
            },
            "received": messages_received
        }
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, comm_manager):
        """Test agent registration and unregistration."""
        handler = AsyncMock()
        metadata = {"role": "test", "capabilities": ["testing"]}
        
        # Register agent
        comm_manager.register_agent("test_agent", handler, metadata)
        
        assert "test_agent" in comm_manager.agents
        assert comm_manager.agent_metadata["test_agent"] == metadata
        
        # Unregister agent
        comm_manager.unregister_agent("test_agent")
        
        assert "test_agent" not in comm_manager.agents
        assert "test_agent" not in comm_manager.agent_metadata
    
    @pytest.mark.asyncio
    async def test_message_sending(self, comm_manager, sample_agents):
        """Test basic message sending between agents."""
        # Register agents
        for agent_id, handler_func in sample_agents["handlers"].items():
            handler = await handler_func
            comm_manager.register_agent(agent_id, handler)
        
        # Create test message
        message = Message(
            sender="agent1",
            recipient="agent2",
            message_type=MessageType.NOTIFICATION,
            content={"text": "Hello from agent1"},
            timestamp=datetime.now(),
            message_id="test_msg_001"
        )
        
        # Send message
        await comm_manager.send_message(message)
        
        # Wait a bit for processing
        await asyncio.sleep(0.1)
        
        # Verify message was delivered
        assert len(sample_agents["received"]["agent2"]) == 1
        received_msg = sample_agents["received"]["agent2"][0]
        assert received_msg.sender == "agent1"
        assert received_msg.content["text"] == "Hello from agent1"
    
    @pytest.mark.asyncio
    async def test_request_response(self, comm_manager):
        """Test request-response communication pattern."""
        # Create responding agent
        async def responder_handler(message: Message):
            if message.message_type == MessageType.REQUEST:
                # Send response
                response = CommunicationProtocol.create_response(
                    message, "responder", {"result": "success"}, True
                )
                await comm_manager.send_message(response)
        
        comm_manager.register_agent("responder", responder_handler)
        
        # Send request and wait for response
        response_data = await comm_manager.send_request(
            "requester", "responder", "test_request", {"data": "test"}, timeout=5
        )
        
        assert response_data["result"] == "success"
        assert comm_manager.stats["responses_received"] >= 1
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self, comm_manager, sample_agents):
        """Test broadcasting messages to all agents."""
        # Register agents
        for agent_id, handler_func in sample_agents["handlers"].items():
            handler = await handler_func
            comm_manager.register_agent(agent_id, handler)
        
        # Broadcast message
        sent_count = await comm_manager.broadcast_message(
            "agent1", MessageType.NOTIFICATION, {"broadcast": "test"}
        )
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        # Should send to all agents except sender
        assert sent_count == 2
        assert len(sample_agents["received"]["agent2"]) == 1
        assert len(sample_agents["received"]["agent3"]) == 1
        assert len(sample_agents["received"]["agent1"]) == 0  # Sender excluded
    
    @pytest.mark.asyncio
    async def test_message_timeout(self, comm_manager):
        """Test message timeout handling."""
        # Register agent that doesn't respond
        async def non_responder(message: Message):
            # Agent receives but doesn't respond
            pass
        
        comm_manager.register_agent("non_responder", non_responder)
        
        # Request with short timeout should fail
        with pytest.raises(TimeoutError):
            await comm_manager.send_request(
                "requester", "non_responder", "test", {}, timeout=1
            )
        
        assert comm_manager.stats["timeouts"] >= 1
    
    @pytest.mark.asyncio
    async def test_message_to_unregistered_agent(self, comm_manager):
        """Test sending message to unregistered agent."""
        message = Message(
            sender="test_sender",
            recipient="unknown_agent",
            message_type=MessageType.NOTIFICATION,
            content={"test": "data"},
            timestamp=datetime.now(),
            message_id="test_msg_002"
        )
        
        await comm_manager.send_message(message)
        await asyncio.sleep(0.1)
        
        # Should increment failed messages count
        assert comm_manager.stats["messages_failed"] >= 1
    
    @pytest.mark.asyncio
    async def test_agent_list_retrieval(self, comm_manager):
        """Test getting list of registered agents."""
        # Register test agents
        comm_manager.register_agent("agent1", AsyncMock(), {"role": "test1"})
        comm_manager.register_agent("agent2", AsyncMock(), {"role": "test2"})
        
        agent_list = await comm_manager.get_agent_list()
        
        assert len(agent_list) == 2
        agent_ids = [agent["agent_id"] for agent in agent_list]
        assert "agent1" in agent_ids
        assert "agent2" in agent_ids
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, comm_manager):
        """Test statistics tracking functionality."""
        # Register agent
        async def test_handler(message: Message):
            pass
        
        comm_manager.register_agent("test_agent", test_handler)
        
        # Send some messages
        for i in range(3):
            message = Message(
                sender="sender",
                recipient="test_agent",
                message_type=MessageType.NOTIFICATION,
                content={"index": i},
                timestamp=datetime.now(),
                message_id=f"msg_{i}"
            )
            await comm_manager.send_message(message)
        
        await asyncio.sleep(0.1)
        
        stats = comm_manager.get_statistics()
        assert stats["messages_sent"] >= 3
        assert stats["messages_delivered"] >= 3
        assert stats["registered_agents"] == 1
    
    @pytest.mark.asyncio
    async def test_conversation_tracking(self, comm_manager):
        """Test conversation history tracking."""
        async def test_handler(message: Message):
            pass
        
        comm_manager.register_agent("agent1", test_handler)
        comm_manager.register_agent("agent2", test_handler)
        
        conversation_id = "conv_001"
        
        # Send messages in conversation
        for i in range(3):
            message = Message(
                sender="agent1",
                recipient="agent2",
                message_type=MessageType.NOTIFICATION,
                content={"msg": f"Message {i}"},
                timestamp=datetime.now(),
                message_id=f"conv_msg_{i}",
                conversation_id=conversation_id
            )
            await comm_manager.send_message(message)
        
        await asyncio.sleep(0.1)
        
        # Check conversation history
        history = await comm_manager.get_conversation_history(conversation_id)
        assert len(history) >= 3
    
    @pytest.mark.asyncio
    async def test_message_serialization(self):
        """Test message serialization and deserialization."""
        original_message = Message(
            sender="agent1",
            recipient="agent2",
            message_type=MessageType.REQUEST,
            content={"request_type": "test", "data": {"key": "value"}},
            timestamp=datetime.now(),
            message_id="test_msg_003",
            requires_response=True,
            response_timeout=30,
            metadata={"priority": "high"}
        )
        
        # Serialize to dict
        message_dict = original_message.to_dict()
        
        # Verify dict contains expected fields
        assert message_dict["sender"] == "agent1"
        assert message_dict["recipient"] == "agent2"
        assert message_dict["message_type"] == "request"
        assert message_dict["requires_response"] is True
        
        # Deserialize back to message
        restored_message = Message.from_dict(message_dict)
        
        # Verify restored message matches original
        assert restored_message.sender == original_message.sender
        assert restored_message.recipient == original_message.recipient
        assert restored_message.message_type == original_message.message_type
        assert restored_message.content == original_message.content
        assert restored_message.requires_response == original_message.requires_response