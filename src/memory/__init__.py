"""
Memory system for Shepherd agent collaboration.

This module provides a three-tier memory architecture:
1. Local Agent Memory - Short-term, task-specific storage
2. Shared Context Pool - Medium-term, workflow-wide collaboration
3. Persistent Knowledge Base - Long-term, cross-session learning
"""

from .base import BaseMemory
from .local_memory import AgentLocalMemory
from .shared_context import SharedContextPool

__all__ = [
    "BaseMemory",
    "AgentLocalMemory", 
    "SharedContextPool",
]