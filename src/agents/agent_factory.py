from typing import List, Dict, Any
from .base_agent import BaseAgent
from .task_agent import TaskAgent
from .system_agent import SystemAgent
from ..core.models import TaskType


class AgentFactory:
    def __init__(self):
        self.agent_registry = {
            TaskType.RESEARCH: self._create_research_agent,
            TaskType.CREATIVE: self._create_creative_agent,
            TaskType.ANALYTICAL: self._create_analytical_agent,
            TaskType.TECHNICAL: self._create_technical_agent,
            TaskType.COMMUNICATION: self._create_communication_agent
        }
    
    def create_agent(self, task_type: str, name: str = None, 
                    complexity: float = 0.5, **kwargs) -> BaseAgent:
        # Check for specific system administration keywords
        if isinstance(task_type, str):
            task_lower = task_type.lower()
            # Check if this should be a system agent based on keywords
            system_keywords = ['server', 'performance', 'system', 'service', 'memory', 'disk', 'cpu', 'optimize']
            request_text = kwargs.get('request_text', '').lower()
            
            if (any(keyword in task_lower for keyword in system_keywords) or
                any(keyword in request_text for keyword in system_keywords)):
                return SystemAgent(name=name or "SystemAgent", complexity=complexity)
        
        # Use enum-based creation for standard task types
        try:
            task_type_enum = TaskType[task_type.upper()] if isinstance(task_type, str) else task_type
            
            if task_type_enum in self.agent_registry:
                creator = self.agent_registry[task_type_enum]
                return creator(name, complexity)
        except (KeyError, AttributeError):
            pass
        
        return self._create_default_agent(name or f"Agent_{task_type}", 
                                        task_type, complexity)
    
    def create_agents_for_tasks(self, task_types: List[str], 
                               complexity: float = 0.5) -> List[BaseAgent]:
        agents = []
        for i, task_type in enumerate(task_types):
            agent = self.create_agent(
                task_type=task_type,
                name=f"Agent_{i}_{task_type}",
                complexity=complexity
            )
            agents.append(agent)
        return agents
    
    def _create_research_agent(self, name: str = None, complexity: float = 0.5) -> BaseAgent:
        return TaskAgent(
            name=name or "ResearchAgent",
            task_type="research",
            complexity=complexity
        )
    
    def _create_creative_agent(self, name: str = None, complexity: float = 0.5) -> BaseAgent:
        return TaskAgent(
            name=name or "CreativeAgent",
            task_type="creative",
            complexity=complexity
        )
    
    def _create_analytical_agent(self, name: str = None, complexity: float = 0.5) -> BaseAgent:
        return TaskAgent(
            name=name or "AnalyticalAgent",
            task_type="analytical",
            complexity=complexity
        )
    
    def _create_technical_agent(self, name: str = None, complexity: float = 0.5) -> BaseAgent:
        return TaskAgent(
            name=name or "TechnicalAgent",
            task_type="technical",
            complexity=complexity
        )
    
    def _create_communication_agent(self, name: str = None, complexity: float = 0.5) -> BaseAgent:
        return TaskAgent(
            name=name or "CommunicationAgent",
            task_type="communication",
            complexity=complexity
        )
    
    def _create_default_agent(self, name: str, task_type: str, 
                            complexity: float) -> BaseAgent:
        return TaskAgent(
            name=name,
            task_type=task_type.lower(),
            complexity=complexity
        )