from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from crewai import Agent
from ..utils.logger import get_logger, log_agent_action
import time
import uuid


class BaseAgent(ABC):
    def __init__(self, name: str, role: str, goal: str, backstory: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory or f"A specialized agent focused on {role}"
        self.crew_agent = None
        self.logger = get_logger(f'agent.{name}')
        self.logger.debug(f"Agent created: {name} ({role})")
    
    @abstractmethod
    def create_crew_agent(self) -> Agent:
        pass
    
    def initialize(self):
        self.crew_agent = self.create_crew_agent()
    
    def execute_task(self, task_description: str) -> Dict[str, Any]:
        start_time = time.time()
        self.logger.info(f"Starting task execution: {task_description}")
        
        if not self.crew_agent:
            self.initialize()
        
        try:
            # Simulated execution for MVP
            execution_time = time.time() - start_time
            result = {
                "agent_id": self.id,
                "agent_name": self.name,
                "task": task_description,
                "status": "completed",
                "output": f"Simulated execution of: {task_description}",
                "error": None
            }
            
            log_agent_action(self.id, self.name, task_description, "completed", execution_time)
            self.logger.info(f"Task completed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            result = {
                "agent_id": self.id,
                "agent_name": self.name,
                "task": task_description,
                "status": "failed",
                "output": None,
                "error": error_msg
            }
            
            log_agent_action(self.id, self.name, task_description, "failed", execution_time, e)
            self.logger.error(f"Task failed after {execution_time:.2f}s: {error_msg}")
            return result