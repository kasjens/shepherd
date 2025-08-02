"""
Mock agent implementations for testing.
"""

import asyncio
from typing import Dict, Any, List
from unittest.mock import AsyncMock
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.core.models import TaskType


class MockTaskAgent(BaseAgent):
    """Mock implementation of TaskAgent for testing."""
    
    def __init__(self, name: str = "mock_task_agent", **kwargs):
        # Provide required parameters for BaseAgent
        role = kwargs.get('role', 'Mock Task Agent')
        goal = kwargs.get('goal', 'Execute test tasks for validation')
        backstory = kwargs.get('backstory', 'A mock agent designed for testing purposes')
        
        super().__init__(name, role, goal, backstory)
        self.agent_type = TaskType.TECHNICAL
        self.execution_count = 0
        self.execution_history = []
        self.should_fail = False
        self.execution_delay = 0.1  # Default delay in seconds
    
    def create_crew_agent(self):
        """Mock implementation of create_crew_agent."""
        # Return a mock object instead of a real CrewAI agent
        from unittest.mock import MagicMock
        mock_agent = MagicMock()
        mock_agent.role = self.role
        mock_agent.goal = self.goal
        return mock_agent
        
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Mock execute method with configurable behavior."""
        self.execution_count += 1
        
        # Simulate processing time
        await asyncio.sleep(self.execution_delay)
        
        execution_record = {
            "task": task,
            "context": context or {},
            "timestamp": datetime.now(),
            "execution_number": self.execution_count
        }
        self.execution_history.append(execution_record)
        
        if self.should_fail:
            return {
                "success": False,
                "error": "Mock agent configured to fail",
                "output": None,
                "metadata": {
                    "agent": self.name,
                    "duration": self.execution_delay,
                    "execution_count": self.execution_count
                }
            }
        
        # Generate mock output based on task
        mock_output = self._generate_mock_output(task, context)
        
        return {
            "success": True,
            "output": mock_output,
            "metadata": {
                "agent": self.name,
                "duration": self.execution_delay,
                "execution_count": self.execution_count,
                "task_type": self._classify_task(task)
            }
        }
    
    def _generate_mock_output(self, task: str, context: Dict[str, Any]) -> str:
        """Generate realistic mock output based on task."""
        task_lower = task.lower()
        
        if "security" in task_lower or "vulnerability" in task_lower:
            return """
Security Analysis Report:
1. No SQL injection vulnerabilities found
2. Input validation properly implemented
3. Authentication mechanisms secure
4. Recommended: Update dependency versions
            """.strip()
        
        elif "code" in task_lower and "analysis" in task_lower:
            return """
Code Analysis Results:
- Total files analyzed: 15
- Code quality score: 8.5/10
- Test coverage: 85%
- Suggestions: Add type hints, improve documentation
            """.strip()
        
        elif "implement" in task_lower or "create" in task_lower:
            return """
Implementation Plan:
1. Define data models
2. Create API endpoints
3. Implement business logic
4. Add comprehensive tests
5. Deploy and monitor
            """.strip()
        
        else:
            return f"Mock execution result for task: {task}"
    
    def _classify_task(self, task: str) -> str:
        """Classify task type for metadata."""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["analyze", "analysis", "review"]):
            return "analysis"
        elif any(word in task_lower for word in ["implement", "create", "build"]):
            return "implementation"
        elif any(word in task_lower for word in ["security", "vulnerability"]):
            return "security"
        elif any(word in task_lower for word in ["test", "testing"]):
            return "testing"
        else:
            return "general"
    
    def set_failure_mode(self, should_fail: bool = True):
        """Configure agent to fail on next execution."""
        self.should_fail = should_fail
    
    def set_execution_delay(self, delay: float):
        """Set execution delay for simulating processing time."""
        self.execution_delay = delay
    
    def reset_state(self):
        """Reset agent state for fresh testing."""
        self.execution_count = 0
        self.execution_history = []
        self.should_fail = False


class MockSystemAgent(BaseAgent):
    """Mock implementation of SystemAgent for testing."""
    
    def __init__(self, name: str = "mock_system_agent", **kwargs):
        role = kwargs.get('role', 'Mock System Agent')
        goal = kwargs.get('goal', 'Monitor and manage system resources')
        backstory = kwargs.get('backstory', 'A mock agent for system operations testing')
        
        super().__init__(name, role, goal, backstory)
        self.agent_type = TaskType.TECHNICAL
        self.system_calls = []
        self.mock_system_state = {
            "cpu_usage": 25.5,
            "memory_usage": 68.2,
            "disk_usage": 45.0,
            "running_processes": 156
        }
    
    def create_crew_agent(self):
        """Mock implementation of create_crew_agent."""
        from unittest.mock import MagicMock
        mock_agent = MagicMock()
        mock_agent.role = self.role
        mock_agent.goal = self.goal
        return mock_agent
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Mock system operation execution."""
        await asyncio.sleep(0.05)  # Quick system call simulation
        
        self.system_calls.append({
            "task": task,
            "timestamp": datetime.now(),
            "context": context or {}
        })
        
        if "monitor" in task.lower() or "status" in task.lower():
            return {
                "success": True,
                "output": self.mock_system_state,
                "metadata": {
                    "agent": self.name,
                    "operation_type": "monitoring"
                }
            }
        
        elif "process" in task.lower():
            return {
                "success": True,
                "output": {
                    "processes": [
                        {"pid": 1234, "name": "python", "cpu": 15.2},
                        {"pid": 5678, "name": "node", "cpu": 8.1}
                    ]
                },
                "metadata": {
                    "agent": self.name,
                    "operation_type": "process_management"
                }
            }
        
        else:
            return {
                "success": True,
                "output": f"System operation completed: {task}",
                "metadata": {
                    "agent": self.name,
                    "operation_type": "general"
                }
            }
    
    def update_system_state(self, new_state: Dict[str, Any]):
        """Update mock system state for testing."""
        self.mock_system_state.update(new_state)


class MockResearchAgent(BaseAgent):
    """Mock research agent specialized for information gathering."""
    
    def __init__(self, name: str = "mock_research_agent", **kwargs):
        role = kwargs.get('role', 'Mock Research Agent')
        goal = kwargs.get('goal', 'Gather and analyze information for decision making')
        backstory = kwargs.get('backstory', 'A mock agent specialized in research and analysis')
        
        super().__init__(name, role, goal, backstory)
        self.agent_type = TaskType.RESEARCH
        self.research_database = {
            "python": "Python is a high-level programming language...",
            "fastapi": "FastAPI is a modern web framework for Python...",
            "security": "Common security vulnerabilities include...",
            "testing": "Software testing best practices include..."
        }
    
    def create_crew_agent(self):
        """Mock implementation of create_crew_agent."""
        from unittest.mock import MagicMock
        mock_agent = MagicMock()
        mock_agent.role = self.role
        mock_agent.goal = self.goal
        return mock_agent
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Mock research execution."""
        await asyncio.sleep(0.2)  # Research takes a bit longer
        
        # Find relevant information
        relevant_info = []
        task_lower = task.lower()
        
        for topic, info in self.research_database.items():
            if topic in task_lower:
                relevant_info.append(f"{topic.upper()}: {info}")
        
        if not relevant_info:
            relevant_info = ["General research information for: " + task]
        
        return {
            "success": True,
            "output": {
                "research_findings": relevant_info,
                "sources": ["Mock Source 1", "Mock Source 2"],
                "confidence": 0.85
            },
            "metadata": {
                "agent": self.name,
                "topics_covered": list(self.research_database.keys()),
                "research_depth": "comprehensive"
            }
        }


class MockCreativeAgent(BaseAgent):
    """Mock creative agent for content generation."""
    
    def __init__(self, name: str = "mock_creative_agent", **kwargs):
        role = kwargs.get('role', 'Mock Creative Agent')
        goal = kwargs.get('goal', 'Generate creative and engaging content')
        backstory = kwargs.get('backstory', 'A mock agent focused on creative content generation')
        
        super().__init__(name, role, goal, backstory)
        self.agent_type = TaskType.CREATIVE
        self.creativity_level = 0.8
    
    def create_crew_agent(self):
        """Mock implementation of create_crew_agent."""
        from unittest.mock import MagicMock
        mock_agent = MagicMock()
        mock_agent.role = self.role
        mock_agent.goal = self.goal
        return mock_agent
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Mock creative execution."""
        await asyncio.sleep(0.15)
        
        creative_outputs = {
            "documentation": "# Comprehensive Documentation\n\nThis is a well-structured document...",
            "naming": ["ClearVariableName", "DescriptiveFunction", "IntuitiveClass"],
            "examples": "```python\ndef example_function():\n    return 'Creative example'\n```",
            "suggestions": [
                "Consider using a more descriptive name",
                "Add visual elements to improve clarity",
                "Structure content with clear hierarchy"
            ]
        }
        
        task_lower = task.lower()
        output_type = "general"
        
        if any(word in task_lower for word in ["document", "write", "content"]):
            output_type = "documentation"
        elif any(word in task_lower for word in ["name", "naming"]):
            output_type = "naming"
        elif any(word in task_lower for word in ["example", "demo"]):
            output_type = "examples"
        else:
            output_type = "suggestions"
        
        return {
            "success": True,
            "output": creative_outputs.get(output_type, "Creative output generated"),
            "metadata": {
                "agent": self.name,
                "creativity_level": self.creativity_level,
                "output_type": output_type
            }
        }


class MockCommunicationManager:
    """Mock communication manager for testing agent interactions."""
    
    def __init__(self):
        self.agents = {}
        self.message_history = []
        self.broadcasts = []
    
    def register_agent(self, agent_id: str, handler):
        """Register agent with message handler."""
        self.agents[agent_id] = handler
    
    async def send_message(self, sender: str, recipient: str, message_type: str, content: Dict):
        """Mock message sending."""
        message = {
            "sender": sender,
            "recipient": recipient,
            "type": message_type,
            "content": content,
            "timestamp": datetime.now()
        }
        self.message_history.append(message)
        
        # If recipient is registered, deliver message
        if recipient in self.agents:
            await self.agents[recipient](message)
    
    async def broadcast(self, sender: str, message_type: str, content: Dict):
        """Mock broadcast to all agents."""
        broadcast = {
            "sender": sender,
            "type": message_type,
            "content": content,
            "timestamp": datetime.now(),
            "recipients": list(self.agents.keys())
        }
        self.broadcasts.append(broadcast)
        
        # Deliver to all registered agents except sender
        for agent_id, handler in self.agents.items():
            if agent_id != sender:
                await handler(broadcast)
    
    def get_message_count(self) -> int:
        """Get total number of messages sent."""
        return len(self.message_history)
    
    def get_broadcast_count(self) -> int:
        """Get total number of broadcasts sent."""
        return len(self.broadcasts)
    
    def clear_history(self):
        """Clear message history for fresh testing."""
        self.message_history = []
        self.broadcasts = []


def create_mock_agent_team() -> List[BaseAgent]:
    """Create a team of different mock agents for testing."""
    return [
        MockTaskAgent("task_agent_1"),
        MockSystemAgent("system_agent_1"),
        MockResearchAgent("research_agent_1"),
        MockCreativeAgent("creative_agent_1")
    ]


def create_collaborative_scenario():
    """Create a mock scenario for testing agent collaboration."""
    agents = create_mock_agent_team()
    comm_manager = MockCommunicationManager()
    
    # Register all agents
    for agent in agents:
        async def dummy_handler(message):
            pass
        comm_manager.register_agent(agent.name, dummy_handler)
    
    return {
        "agents": agents,
        "communication_manager": comm_manager,
        "scenario": {
            "task": "Analyze project and create implementation plan",
            "expected_collaboration": True,
            "expected_messages": 3,
            "expected_agents": 4
        }
    }