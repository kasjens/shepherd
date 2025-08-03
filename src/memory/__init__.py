"""
Memory system for Shepherd agent collaboration.

This module provides a three-tier memory architecture:
1. Local Agent Memory - Short-term, task-specific storage
2. Shared Context Pool - Medium-term, workflow-wide collaboration
3. Persistent Knowledge Base - Long-term, cross-session learning

Phase 7 adds vector-based semantic memory capabilities:
- VectorMemoryStore - Vector embeddings with similarity search
- PersistentKnowledgeBase - Long-term knowledge storage with semantic retrieval
"""

from .base import BaseMemory
from .local_memory import AgentLocalMemory
from .shared_context import SharedContextPool
from .vector_store import VectorMemoryStore
from .persistent_knowledge import PersistentKnowledgeBase, KnowledgeType

__all__ = [
    "BaseMemory",
    "AgentLocalMemory", 
    "SharedContextPool",
    "VectorMemoryStore",
    "PersistentKnowledgeBase",
    "KnowledgeType",
]