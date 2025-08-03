"""
Communication manager for handling agent-to-agent messaging.
"""

import asyncio
import logging
from typing import Dict, List, Callable, Optional, Set, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta

from .protocols import Message, MessageType, CommunicationProtocol

logger = logging.getLogger(__name__)


class CommunicationManager:
    """
    Central manager for agent-to-agent communication.
    
    This class handles message routing, delivery, and conversation management
    between agents in the Shepherd system. It provides:
    - Direct agent-to-agent messaging
    - Broadcast messaging
    - Message queuing and delivery
    - Conversation threading
    - Response tracking and timeouts
    """
    
    def __init__(self, max_queue_size: int = 1000, 
                 default_timeout: int = 30):
        """
        Initialize communication manager.
        
        Args:
            max_queue_size: Maximum messages to queue per agent
            default_timeout: Default response timeout in seconds
        """
        self.max_queue_size = max_queue_size
        self.default_timeout = default_timeout
        
        # Agent registration
        self.agents: Dict[str, Callable] = {}
        self.agent_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Message routing
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.agent_queues: Dict[str, asyncio.Queue] = defaultdict(
            lambda: asyncio.Queue(maxsize=max_queue_size)
        )
        
        # Response tracking
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self.response_timeouts: Dict[str, datetime] = {}
        
        # Conversation management
        self.conversations: Dict[str, List[str]] = defaultdict(list)
        self.conversation_participants: Dict[str, Set[str]] = defaultdict(set)
        
        # Message history for debugging/analysis
        self.message_history: deque = deque(maxlen=1000)
        
        # Processing control
        self._processing = False
        self._processor_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "messages_failed": 0,
            "responses_received": 0,
            "timeouts": 0,
            "broadcasts": 0
        }
    
    async def start(self):
        """Start the message processing system."""
        if not self._processing:
            self._processing = True
            self._processor_task = asyncio.create_task(self._process_messages())
            logger.info("Communication manager started")
    
    async def stop(self):
        """Stop the message processing system."""
        self._processing = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        logger.info("Communication manager stopped")
    
    def register_agent(self, agent_id: str, message_handler: Callable,
                      metadata: Optional[Dict[str, Any]] = None):
        """
        Register an agent with the communication system.
        
        Args:
            agent_id: Unique identifier for the agent
            message_handler: Async function to handle incoming messages
            metadata: Optional agent metadata (capabilities, etc.)
        """
        self.agents[agent_id] = message_handler
        self.agent_metadata[agent_id] = metadata or {}
        
        logger.info(f"Agent registered: {agent_id}")
    
    def unregister_agent(self, agent_id: str):
        """
        Unregister an agent from the communication system.
        
        Args:
            agent_id: ID of agent to unregister
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self.agent_metadata[agent_id]
            
            # Clear agent's message queue
            if agent_id in self.agent_queues:
                del self.agent_queues[agent_id]
            
            logger.info(f"Agent unregistered: {agent_id}")
    
    async def send_message(self, message: Message) -> Optional[asyncio.Future]:
        """
        Send a message to another agent.
        
        Args:
            message: Message to send
            
        Returns:
            Future for response if message requires response, None otherwise
        """
        self.stats["messages_sent"] += 1
        
        # Add to message history
        self.message_history.append({
            "timestamp": datetime.now(),
            "action": "sent",
            "message": message.to_dict()
        })
        
        # Handle response tracking
        response_future = None
        if message.requires_response:
            response_future = asyncio.Future()
            self.pending_responses[message.message_id] = response_future
            
            # Set timeout
            timeout = message.response_timeout or self.default_timeout
            self.response_timeouts[message.message_id] = (
                datetime.now() + timedelta(seconds=timeout)
            )
        
        # Queue message for processing
        await self.message_queue.put(message)
        
        logger.debug(f"Message queued: {message.message_id} from {message.sender} to {message.recipient}")
        
        return response_future
    
    async def send_request(self, sender: str, recipient: str, 
                          request_type: str, data: Dict[str, Any],
                          timeout: int = None) -> Dict[str, Any]:
        """
        Send a request and wait for response.
        
        Args:
            sender: ID of requesting agent
            recipient: ID of target agent
            request_type: Type of request
            data: Request data
            timeout: Response timeout in seconds
            
        Returns:
            Response data
            
        Raises:
            TimeoutError: If response not received within timeout
            RuntimeError: If request fails
        """
        message = CommunicationProtocol.create_request(
            sender, recipient, request_type, data, 
            timeout or self.default_timeout
        )
        
        response_future = await self.send_message(message)
        
        try:
            response = await response_future
            return response.content["data"]
        except asyncio.TimeoutError:
            self.stats["timeouts"] += 1
            raise TimeoutError(f"Request timeout: {request_type} to {recipient}")
    
    async def broadcast_message(self, sender: str, message_type: MessageType, 
                              content: Dict[str, Any],
                              exclude: Optional[Set[str]] = None) -> int:
        """
        Broadcast a message to all registered agents.
        
        Args:
            sender: ID of broadcasting agent
            message_type: Type of message to broadcast
            content: Message content
            exclude: Optional set of agent IDs to exclude
            
        Returns:
            Number of agents the message was sent to
        """
        exclude = exclude or set()
        exclude.add(sender)  # Don't send to self
        
        target_agents = [
            agent_id for agent_id in self.agents.keys()
            if agent_id not in exclude
        ]
        
        if not target_agents:
            return 0
        
        # Create broadcast messages
        import uuid
        for agent_id in target_agents:
            message = Message(
                sender=sender,
                recipient=agent_id,
                message_type=message_type,
                content=content,
                timestamp=datetime.now(),
                message_id=str(uuid.uuid4()),
                priority=5
            )
            await self.send_message(message)
        
        self.stats["broadcasts"] += 1
        logger.info(f"Broadcast sent from {sender} to {len(target_agents)} agents")
        
        return len(target_agents)
    
    async def get_agent_list(self) -> List[Dict[str, Any]]:
        """
        Get list of registered agents with their metadata.
        
        Returns:
            List of agent information
        """
        return [
            {
                "agent_id": agent_id,
                "metadata": self.agent_metadata.get(agent_id, {}),
                "queue_size": self.agent_queues[agent_id].qsize() if agent_id in self.agent_queues else 0
            }
            for agent_id in self.agents.keys()
        ]
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get message history for a conversation.
        
        Args:
            conversation_id: ID of conversation
            
        Returns:
            List of messages in conversation
        """
        message_ids = self.conversations.get(conversation_id, [])
        
        # Find messages in history
        messages = []
        for entry in self.message_history:
            if entry["message"]["message_id"] in message_ids:
                messages.append(entry)
        
        return sorted(messages, key=lambda x: x["timestamp"])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get communication statistics."""
        return {
            **self.stats,
            "registered_agents": len(self.agents),
            "pending_responses": len(self.pending_responses),
            "active_conversations": len(self.conversations),
            "queue_size": self.message_queue.qsize(),
            "history_size": len(self.message_history)
        }
    
    async def _process_messages(self):
        """Main message processing loop."""
        logger.info("Message processor started")
        
        while self._processing:
            try:
                # Process pending timeouts
                await self._check_timeouts()
                
                # Process queued messages
                try:
                    # Wait for message with timeout to allow timeout checking
                    message = await asyncio.wait_for(
                        self.message_queue.get(), timeout=1.0
                    )
                    await self._deliver_message(message)
                except asyncio.TimeoutError:
                    # No message available, continue to check timeouts
                    continue
                    
            except Exception as e:
                logger.error(f"Error in message processor: {e}")
                await asyncio.sleep(0.1)  # Brief pause before retrying
    
    async def _deliver_message(self, message: Message):
        """
        Deliver a message to its recipient(s).
        
        Args:
            message: Message to deliver
        """
        try:
            # Handle broadcast messages
            if message.recipient == "all":
                exclude = {message.sender}
                await self.broadcast_message(
                    message.sender, message.message_type, 
                    message.content, exclude
                )
                return
            
            # Check if recipient is registered
            if message.recipient not in self.agents:
                logger.warning(f"Recipient not found: {message.recipient}")
                self.stats["messages_failed"] += 1
                return
            
            # Add to conversation if specified
            if message.conversation_id:
                self.conversations[message.conversation_id].append(message.message_id)
                self.conversation_participants[message.conversation_id].add(message.sender)
                self.conversation_participants[message.conversation_id].add(message.recipient)
            
            # Deliver to agent
            handler = self.agents[message.recipient]
            
            # Add to message history
            self.message_history.append({
                "timestamp": datetime.now(),
                "action": "delivered",
                "message": message.to_dict()
            })
            
            # Handle response messages
            if message.message_type == MessageType.RESPONSE:
                await self._handle_response(message)
            
            # Call agent's message handler
            try:
                await handler(message)
                self.stats["messages_delivered"] += 1
                logger.debug(f"Message delivered: {message.message_id} to {message.recipient}")
                
            except Exception as e:
                logger.error(f"Error delivering message to {message.recipient}: {e}")
                self.stats["messages_failed"] += 1
                
        except Exception as e:
            logger.error(f"Error in message delivery: {e}")
            self.stats["messages_failed"] += 1
    
    async def _check_timeouts(self):
        """Check for and handle response timeouts."""
        now = datetime.now()
        timed_out = []
        
        for message_id, timeout_time in self.response_timeouts.items():
            if now > timeout_time:
                timed_out.append(message_id)
        
        for message_id in timed_out:
            if message_id in self.pending_responses:
                future = self.pending_responses[message_id]
                if not future.done():
                    future.set_exception(asyncio.TimeoutError(f"Response timeout for message {message_id}"))
                
                del self.pending_responses[message_id]
                del self.response_timeouts[message_id]
                self.stats["timeouts"] += 1
    
    async def _handle_response(self, message: Message):
        """
        Handle response messages.
        
        Args:
            message: Response message
        """
        original_message_id = message.content.get("original_message_id")
        
        if original_message_id and original_message_id in self.pending_responses:
            future = self.pending_responses[original_message_id]
            
            if not future.done():
                future.set_result(message)
                self.stats["responses_received"] += 1
            
            # Clean up tracking
            del self.pending_responses[original_message_id]
            if original_message_id in self.response_timeouts:
                del self.response_timeouts[original_message_id]