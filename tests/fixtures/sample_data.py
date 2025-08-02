"""
Sample data sets for testing Shepherd components.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from src.core.models import TaskType, WorkflowPattern, ExecutionStep, ExecutionStatus


# Sample prompts for different complexity levels
SAMPLE_PROMPTS = {
    "simple": [
        "Create a hello world function",
        "List all files in the current directory",
        "Check system status",
        "Generate a simple README file"
    ],
    
    "medium": [
        "Analyze code quality and suggest improvements",
        "Create a REST API for user management",
        "Set up a CI/CD pipeline",
        "Implement authentication and authorization"
    ],
    
    "complex": [
        "Analyze the entire codebase for security vulnerabilities and performance issues",
        "Design and implement a microservices architecture with proper monitoring",
        "Create a comprehensive testing strategy including unit, integration, and e2e tests",
        "Migrate legacy system to modern tech stack with zero downtime"
    ],
    
    "collaborative": [
        "Research best practices, implement solution, test thoroughly, and document everything",
        "Analyze security, optimize performance, refactor code, and deploy to production",
        "Gather requirements, design architecture, implement features, and create user documentation",
        "Audit codebase, fix issues, improve performance, and establish monitoring"
    ]
}


# Sample contexts for different project types
SAMPLE_CONTEXTS = {
    "python_web": {
        "project_folder": "/project/python-web-app",
        "language": "python",
        "framework": "fastapi",
        "complexity": 0.7,
        "files": ["main.py", "models.py", "requirements.txt"],
        "tech_stack": ["FastAPI", "SQLAlchemy", "PostgreSQL"]
    },
    
    "react_frontend": {
        "project_folder": "/project/react-app",
        "language": "typescript",
        "framework": "react",
        "complexity": 0.6,
        "files": ["App.tsx", "package.json", "tsconfig.json"],
        "tech_stack": ["React", "TypeScript", "Next.js"]
    },
    
    "microservices": {
        "project_folder": "/project/microservices",
        "language": "multiple",
        "framework": "kubernetes",
        "complexity": 0.9,
        "files": ["docker-compose.yml", "k8s/", "services/"],
        "tech_stack": ["Docker", "Kubernetes", "gRPC", "Redis"]
    },
    
    "data_science": {
        "project_folder": "/project/ml-pipeline",
        "language": "python",
        "framework": "sklearn",
        "complexity": 0.8,
        "files": ["notebook.ipynb", "pipeline.py", "requirements.txt"],
        "tech_stack": ["Pandas", "Scikit-learn", "Jupyter", "MLflow"]
    }
}


# Sample execution steps for different workflow patterns
SAMPLE_EXECUTION_STEPS = {
    "sequential": [
        ExecutionStep(
            id="step_1",
            command="research_requirements",
            description="Research project requirements and constraints",
            risk_level="low",
            requires_confirmation=False,
            backup_command=None,
            rollback_command=None,
            status=ExecutionStatus.PENDING
        ),
        ExecutionStep(
            id="step_2", 
            command="design_architecture",
            description="Design system architecture",
            risk_level="medium",
            requires_confirmation=True,
            backup_command="save_current_design",
            rollback_command="restore_previous_design",
            status=ExecutionStatus.PENDING
        ),
        ExecutionStep(
            id="step_3",
            command="implement_core",
            description="Implement core functionality", 
            risk_level="high",
            requires_confirmation=True,
            backup_command="create_backup",
            rollback_command="restore_backup",
            status=ExecutionStatus.PENDING
        )
    ],
    
    "parallel": [
        ExecutionStep(
            id="parallel_1",
            command="security_research",
            description="Research security best practices",
            risk_level="low",
            requires_confirmation=False,
            backup_command=None,
            rollback_command=None,
            status=ExecutionStatus.PENDING
        ),
        ExecutionStep(
            id="parallel_2",
            command="performance_research", 
            description="Research performance optimization techniques",
            risk_level="low",
            requires_confirmation=False,
            backup_command=None,
            rollback_command=None,
            status=ExecutionStatus.PENDING
        ),
        ExecutionStep(
            id="parallel_3",
            command="code_analysis",
            description="Analyze current codebase structure",
            risk_level="medium",
            requires_confirmation=False,
            backup_command=None,
            rollback_command=None,
            status=ExecutionStatus.PENDING
        )
    ]
}


# Sample workflow results for testing
SAMPLE_WORKFLOW_RESULTS = [
    {
        "workflow_id": "test_sequential_001",
        "pattern": WorkflowPattern.SEQUENTIAL,
        "success": True,
        "total_duration": 45.2,
        "results": [
            {"agent": "research_agent", "output": "Requirements gathered successfully", "duration": 15.1},
            {"agent": "technical_agent", "output": "Architecture designed", "duration": 20.3},
            {"agent": "task_agent", "output": "Implementation completed", "duration": 9.8}
        ],
        "metadata": {
            "agents_used": 3,
            "steps_completed": 3,
            "success_rate": 1.0
        }
    },
    
    {
        "workflow_id": "test_parallel_001", 
        "pattern": WorkflowPattern.PARALLEL,
        "success": True,
        "total_duration": 28.7,
        "results": [
            {"agent": "research_agent_1", "output": "Security analysis complete", "duration": 25.1},
            {"agent": "research_agent_2", "output": "Performance analysis complete", "duration": 28.7},
            {"agent": "technical_agent", "output": "Code structure analyzed", "duration": 18.3}
        ],
        "metadata": {
            "agents_used": 3,
            "steps_completed": 3,
            "parallel_efficiency": 0.89
        }
    }
]


# Sample user feedback for learning systems
SAMPLE_USER_FEEDBACK = [
    {
        "type": "preference",
        "context": "code_documentation",
        "preference": "detailed_explanations",
        "examples": [
            "Added comprehensive docstrings with examples",
            "Included type hints and parameter descriptions"
        ],
        "strength": 0.9,
        "timestamp": datetime.now() - timedelta(days=1)
    },
    
    {
        "type": "correction",
        "context": "security_analysis",
        "original_output": "No vulnerabilities found",
        "corrected_output": "Found SQL injection vulnerability in login endpoint",
        "explanation": "The tool missed a critical SQL injection point",
        "timestamp": datetime.now() - timedelta(hours=6)
    },
    
    {
        "type": "guidance",
        "context": "code_style",
        "guidance": "Always use async/await for database operations",
        "examples": [
            "async def get_user(db: Session, user_id: int):",
            "user = await db.execute(select(User).where(User.id == user_id))"
        ],
        "timestamp": datetime.now() - timedelta(hours=2)
    },
    
    {
        "type": "rating",
        "context": "implementation_quality",
        "rating": 4,
        "max_rating": 5,
        "feedback": "Good implementation but could use better error handling",
        "timestamp": datetime.now() - timedelta(minutes=30)
    }
]


# Sample memory patterns for testing
SAMPLE_MEMORY_PATTERNS = [
    {
        "pattern_id": "auth_implementation",
        "pattern_type": "learned",
        "context": "authentication system",
        "successful_sequence": ["research", "design", "implement", "test"],
        "key_decisions": {
            "auth_method": "oauth2",
            "token_storage": "httponly_cookies",
            "session_management": "jwt_with_refresh"
        },
        "success_rate": 0.92,
        "usage_count": 15
    },
    
    {
        "pattern_id": "api_error_handling",
        "pattern_type": "user_preference",
        "context": "API development",
        "preference": "structured_error_responses",
        "implementation": {
            "use_custom_exceptions": True,
            "include_error_codes": True,
            "provide_user_friendly_messages": True
        },
        "strength": 0.85
    }
]


# Sample agent collaboration scenarios
COLLABORATION_SCENARIOS = [
    {
        "name": "Security Audit and Fix",
        "description": "Multiple agents collaborate to audit security and implement fixes",
        "agents_involved": ["research", "security", "technical", "system"],
        "expected_interactions": [
            {"from": "research", "to": "security", "type": "context_share"},
            {"from": "security", "to": "technical", "type": "requirements"},
            {"from": "technical", "to": "system", "type": "deployment_plan"}
        ],
        "success_criteria": {
            "min_agents": 3,
            "min_interactions": 2,
            "completion_time": 60.0
        }
    },
    
    {
        "name": "Full Stack Development",
        "description": "Complete application development with multiple specialists",
        "agents_involved": ["research", "frontend", "backend", "database", "devops"],
        "expected_interactions": [
            {"from": "research", "to": "all", "type": "requirements_broadcast"},
            {"from": "backend", "to": "frontend", "type": "api_specification"},
            {"from": "database", "to": "backend", "type": "schema_design"},
            {"from": "devops", "to": "all", "type": "deployment_requirements"}
        ],
        "success_criteria": {
            "min_agents": 4,
            "min_interactions": 5,
            "completion_time": 120.0
        }
    }
]


# Performance benchmarks for testing
PERFORMANCE_BENCHMARKS = {
    "agent_execution": {
        "simple_task": {"max_duration": 2.0, "target_duration": 1.0},
        "medium_task": {"max_duration": 10.0, "target_duration": 5.0},
        "complex_task": {"max_duration": 30.0, "target_duration": 15.0}
    },
    
    "workflow_execution": {
        "sequential_3_agents": {"max_duration": 20.0, "target_duration": 10.0},
        "parallel_3_agents": {"max_duration": 15.0, "target_duration": 8.0},
        "conditional_branch": {"max_duration": 25.0, "target_duration": 12.0}
    },
    
    "memory_operations": {
        "store_simple": {"max_duration": 0.1, "target_duration": 0.05},
        "retrieve_simple": {"max_duration": 0.1, "target_duration": 0.02},
        "search_similar": {"max_duration": 1.0, "target_duration": 0.5}
    }
}


def get_sample_data(category: str, subcategory: str = None) -> Any:
    """Get sample data by category and optional subcategory."""
    data_map = {
        "prompts": SAMPLE_PROMPTS,
        "contexts": SAMPLE_CONTEXTS,
        "steps": SAMPLE_EXECUTION_STEPS,
        "results": SAMPLE_WORKFLOW_RESULTS,
        "feedback": SAMPLE_USER_FEEDBACK,
        "patterns": SAMPLE_MEMORY_PATTERNS,
        "scenarios": COLLABORATION_SCENARIOS,
        "benchmarks": PERFORMANCE_BENCHMARKS
    }
    
    if category not in data_map:
        raise ValueError(f"Unknown category: {category}")
    
    data = data_map[category]
    
    if subcategory:
        if isinstance(data, dict) and subcategory in data:
            return data[subcategory]
        else:
            raise ValueError(f"Unknown subcategory: {subcategory} in {category}")
    
    return data