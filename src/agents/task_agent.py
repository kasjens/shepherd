from .base_agent import BaseAgent
from crewai import Agent
from typing import Optional


class TaskAgent(BaseAgent):
    def __init__(self, name: str, task_type: str, complexity: float):
        self.task_type = task_type
        self.complexity = complexity
        
        role_mapping = {
            "research": "Research Specialist",
            "creative": "Creative Designer",
            "analytical": "Data Analyst",
            "technical": "Software Engineer",
            "communication": "Communication Expert"
        }
        
        role = role_mapping.get(task_type, "General Task Executor")
        goal = f"Execute {task_type} tasks with {complexity:.1%} complexity level"
        
        backstory_mapping = {
            "research": "An expert researcher skilled in finding and analyzing information from various sources",
            "creative": "A creative professional with expertise in design and content creation",
            "analytical": "A data analyst specialized in extracting insights from complex datasets",
            "technical": "A software engineer proficient in coding and system implementation",
            "communication": "A communication specialist focused on clear and effective messaging"
        }
        
        backstory = backstory_mapping.get(task_type, f"A specialist in {task_type} tasks")
        
        super().__init__(name=name, role=role, goal=goal, backstory=backstory)
    
    def create_crew_agent(self) -> Agent:
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            verbose=True,
            allow_delegation=False
        )