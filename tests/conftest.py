"""
Pytest configuration and shared fixtures for Shepherd tests.
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock
import tempfile
import os
from pathlib import Path

# Import test subjects
from src.core.orchestrator import IntelligentOrchestrator
from src.core.prompt_analyzer import PromptAnalyzer
from src.core.workflow_selector import WorkflowSelector
from src.agents.agent_factory import AgentFactory
from src.workflows.sequential_workflow import SequentialWorkflow
from src.workflows.parallel_workflow import ParallelWorkflow


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_project_context():
    """Sample project context for testing."""
    return {
        "project_folder": "/test/project",
        "language": "python",
        "framework": "fastapi",
        "complexity": 0.7
    }


@pytest.fixture
def sample_prompt():
    """Sample prompt for testing."""
    return "Analyze the codebase for security vulnerabilities and create a detailed report."


@pytest.fixture
def simple_prompt():
    """Simple prompt for basic testing."""
    return "Create a hello world function in Python."


@pytest.fixture
def complex_prompt():
    """Complex prompt requiring multiple agents."""
    return """
    Analyze the entire codebase for security vulnerabilities, performance issues, 
    and code quality problems. Create a comprehensive report with specific 
    recommendations and implementation examples for each issue found.
    """


@pytest.fixture
def mock_ollama_response():
    """Mock Ollama LLM response."""
    return {
        "content": "This is a mock response from the LLM.",
        "model": "llama3.1:8b",
        "done": True
    }


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = AsyncMock()
    agent.name = "test_agent"
    agent.agent_type = "task"
    agent.execute = AsyncMock(return_value={
        "success": True,
        "output": "Mock agent execution result",
        "metadata": {"duration": 1.5}
    })
    return agent


@pytest.fixture
def mock_orchestrator():
    """Create a mock orchestrator for testing."""
    orchestrator = AsyncMock(spec=IntelligentOrchestrator)
    orchestrator.analyze_prompt = AsyncMock()
    orchestrator.execute = AsyncMock()
    return orchestrator


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some sample files
        project_path = Path(temp_dir)
        
        # Python files
        (project_path / "main.py").write_text("""
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
""")
        
        (project_path / "requirements.txt").write_text("""
fastapi>=0.100.0
uvicorn>=0.23.0
pytest>=7.0.0
""")
        
        # Create subdirectories
        (project_path / "src").mkdir()
        (project_path / "src" / "__init__.py").write_text("")
        (project_path / "src" / "models.py").write_text("""
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
""")
        
        (project_path / "tests").mkdir()
        (project_path / "tests" / "__init__.py").write_text("")
        
        yield str(project_path)


@pytest.fixture
async def prompt_analyzer():
    """Create a PromptAnalyzer instance."""
    return PromptAnalyzer()


@pytest.fixture
async def workflow_selector():
    """Create a WorkflowSelector instance."""
    return WorkflowSelector()


@pytest.fixture
async def agent_factory():
    """Create an AgentFactory instance."""
    return AgentFactory()


@pytest.fixture
def mock_shared_context():
    """Mock shared context for testing."""
    context = MagicMock()
    context.store = AsyncMock()
    context.retrieve = AsyncMock()
    context.broadcast_update = AsyncMock()
    return context


@pytest.fixture
def mock_communication_manager():
    """Mock communication manager for testing."""
    comm = MagicMock()
    comm.register_agent = MagicMock()
    comm.send_message = AsyncMock()
    comm.broadcast = AsyncMock()
    return comm


@pytest.fixture
def sample_execution_steps():
    """Sample execution steps for workflow testing."""
    from src.core.models import ExecutionStep, ExecutionStatus
    return [
        ExecutionStep(
            id="step_1",
            command="analyze_project_structure",
            description="Analyze project structure",
            risk_level="low",
            requires_confirmation=False,
            backup_command=None,
            rollback_command=None,
            status=ExecutionStatus.PENDING
        ),
        ExecutionStep(
            id="step_2",
            command="generate_implementation_plan",
            description="Generate implementation plan",
            risk_level="medium",
            requires_confirmation=True,
            backup_command=None,
            rollback_command=None,
            status=ExecutionStatus.PENDING
        )
    ]


@pytest.fixture
def sample_workflow_result():
    """Sample workflow result for testing."""
    from src.core.models import WorkflowResult, WorkflowPattern
    from datetime import datetime
    
    return WorkflowResult(
        workflow_id="test_workflow_001",
        pattern=WorkflowPattern.SEQUENTIAL,
        results=[
            {"agent": "research", "output": "Analysis complete"},
            {"agent": "technical", "output": "Implementation plan ready"}
        ],
        total_duration=45.2,
        start_time=datetime.now(),
        end_time=datetime.now(),
        success=True,
        metadata={"agents_used": 2, "steps_completed": 2}
    )


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.debug = MagicMock()
    return logger


# Async test utilities
@pytest.fixture
def async_test_timeout():
    """Default timeout for async tests."""
    return 10.0  # seconds


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("SANDBOX_MODE", "true")


# Database fixtures (for future use)
@pytest.fixture
def mock_database():
    """Mock database connection for testing."""
    db = MagicMock()
    db.connect = AsyncMock()
    db.disconnect = AsyncMock()
    db.execute = AsyncMock()
    db.fetch_all = AsyncMock()
    db.fetch_one = AsyncMock()
    return db


# API testing fixtures
@pytest.fixture
def test_client():
    """Create a test client for FastAPI testing."""
    from fastapi.testclient import TestClient
    from api.main import app
    
    return TestClient(app)


# Performance testing utilities
@pytest.fixture
def performance_tracker():
    """Track performance metrics during tests."""
    import time
    import psutil
    
    class PerformanceTracker:
        def __init__(self):
            self.start_time = None
            self.start_memory = None
            
        def start(self):
            self.start_time = time.time()
            self.start_memory = psutil.Process().memory_info().rss
            
        def stop(self):
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            
            return {
                "duration": end_time - self.start_time,
                "memory_delta": end_memory - self.start_memory,
                "memory_mb": (end_memory - self.start_memory) / 1024 / 1024
            }
    
    return PerformanceTracker()


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test."""
    yield
    # Any cleanup code goes here
    pass