# Shepherd Agent Collaboration Implementation Plan

This document provides a sequenced, testable implementation plan for adding agent collaboration, memory sharing, and learning capabilities to Shepherd.

## Overview

The implementation is divided into 12 phases, each with specific deliverables and test plans. Each phase builds on the previous one and can be tested independently.

---

## Phase 1: Test Infrastructure Setup (Week 1)

### Objectives
- Establish comprehensive test infrastructure
- Create test utilities and fixtures
- Set up CI/CD pipeline basics

### Implementation Steps

#### 1.1 Backend Test Framework
```bash
# Create test structure
tests/
├── unit/
│   ├── agents/
│   ├── core/
│   ├── workflows/
│   └── api/
├── integration/
├── fixtures/
└── conftest.py
```

**Files to create:**
- `tests/conftest.py` - pytest configuration and shared fixtures
- `tests/fixtures/mock_agents.py` - Mock agent implementations
- `tests/fixtures/sample_data.py` - Test data sets

#### 1.2 Frontend Test Setup
```bash
# In shepherd-gui/
__tests__/
├── components/
├── stores/
├── lib/
└── setup.ts
```

**Commands:**
```bash
cd shepherd-gui
npm install --save-dev @testing-library/react @testing-library/jest-dom jest-environment-jsdom
```

### Testing Plan
```python
# tests/test_infrastructure.py
def test_mock_agent_creation():
    """Verify mock agents can be created"""
    agent = MockTaskAgent("test_agent")
    assert agent.name == "test_agent"
    assert agent.execute("test") is not None

def test_fixtures_available():
    """Verify all fixtures load correctly"""
    from fixtures.sample_data import SAMPLE_PROMPTS
    assert len(SAMPLE_PROMPTS) > 0
```

**Verification:** Run `pytest tests/` - all infrastructure tests should pass

---

## Phase 2: Memory System Foundation (Week 2)

### Objectives
- Implement three-tier memory architecture
- Add in-memory storage initially (vector DB later)
- Create memory interfaces

### Implementation Steps

#### 2.1 Create Memory Base Classes
```python
# src/memory/__init__.py
# src/memory/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime

class BaseMemory(ABC):
    @abstractmethod
    async def store(self, key: str, data: Any) -> None:
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Any:
        pass
    
    @abstractmethod
    async def search(self, query: Dict) -> List[Any]:
        pass
```

#### 2.2 Implement Local Agent Memory
```python
# src/memory/local_memory.py
class AgentLocalMemory(BaseMemory):
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.working_memory = {}
        self.recent_actions = []
        self.temporary_findings = {}
        
    async def store(self, key: str, data: Any) -> None:
        self.working_memory[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        
    async def clear(self) -> None:
        """Clear memory after task completion"""
        self.working_memory.clear()
        self.recent_actions.clear()
```

#### 2.3 Implement Shared Context Pool
```python
# src/memory/shared_context.py
from typing import Dict, List
import asyncio

class SharedContextPool(BaseMemory):
    def __init__(self):
        self.conversation_context = {}
        self.workflow_artifacts = {}
        self.agent_discoveries = {}
        self.execution_history = []
        self._subscribers = []
        
    async def subscribe(self, callback):
        """Subscribe to context updates"""
        self._subscribers.append(callback)
        
    async def broadcast_update(self, update_type: str, data: Dict):
        """Notify all subscribers of context changes"""
        tasks = [sub(update_type, data) for sub in self._subscribers]
        await asyncio.gather(*tasks)
```

#### 2.4 Update Agent Base Class
```python
# src/agents/base_agent.py (update existing)
from src.memory.local_memory import AgentLocalMemory
from src.memory.shared_context import SharedContextPool

class BaseAgent(ABC):
    def __init__(self, name: str, shared_context: SharedContextPool = None):
        self.name = name
        self.local_memory = AgentLocalMemory(name)
        self.shared_context = shared_context or SharedContextPool()
        
    async def store_memory(self, key: str, data: Any):
        """Store in local memory"""
        await self.local_memory.store(key, data)
        
    async def share_discovery(self, discovery_type: str, data: Dict):
        """Share discovery with other agents"""
        if self.shared_context:
            await self.shared_context.store(
                f"discovery_{self.name}_{discovery_type}",
                data
            )
            await self.shared_context.broadcast_update('discovery', {
                'agent': self.name,
                'type': discovery_type,
                'data': data
            })
```

### Testing Plan

```python
# tests/unit/memory/test_local_memory.py
import pytest
from src.memory.local_memory import AgentLocalMemory

@pytest.mark.asyncio
async def test_local_memory_storage():
    memory = AgentLocalMemory("test_agent")
    await memory.store("key1", {"value": "test"})
    
    result = await memory.retrieve("key1")
    assert result['data']['value'] == "test"
    assert 'timestamp' in result

@pytest.mark.asyncio
async def test_memory_clear():
    memory = AgentLocalMemory("test_agent")
    await memory.store("key1", "data")
    await memory.clear()
    
    result = await memory.retrieve("key1")
    assert result is None
```

```python
# tests/unit/memory/test_shared_context.py
@pytest.mark.asyncio
async def test_context_broadcasting():
    context = SharedContextPool()
    updates_received = []
    
    async def subscriber(update_type, data):
        updates_received.append((update_type, data))
    
    await context.subscribe(subscriber)
    await context.broadcast_update('test', {'message': 'hello'})
    
    assert len(updates_received) == 1
    assert updates_received[0][0] == 'test'
```

**Verification:** ✅ COMPLETED
- Run `pytest tests/unit/memory/ tests/integration/test_memory_integration.py` - All 37 memory tests pass
- Memory system fully integrated with BaseAgent class
- Agent collaboration via shared context pool functional
- Local memory with LRU eviction and action tracking operational
- Pub/sub system for real-time context updates working

---

## Phase 3: Agent Communication System (Week 3)

### Objectives
- Implement agent-to-agent messaging
- Create communication protocols
- Add event-based notifications

### Implementation Steps

#### 3.1 Create Communication Manager
```python
# src/communication/manager.py
from typing import Dict, List, Callable
import asyncio
from dataclasses import dataclass

@dataclass
class Message:
    sender: str
    recipient: str
    message_type: str
    content: Dict
    timestamp: datetime

class CommunicationManager:
    def __init__(self):
        self.agents = {}
        self.message_queue = asyncio.Queue()
        self.message_handlers = {}
        
    def register_agent(self, agent_id: str, handler: Callable):
        """Register an agent with its message handler"""
        self.agents[agent_id] = handler
        
    async def send_message(self, message: Message):
        """Send message to specific agent"""
        await self.message_queue.put(message)
        
    async def broadcast(self, sender: str, message_type: str, content: Dict):
        """Broadcast to all agents except sender"""
        for agent_id in self.agents:
            if agent_id != sender:
                msg = Message(sender, agent_id, message_type, content, datetime.now())
                await self.send_message(msg)
```

#### 3.2 Add Communication to Agents
```python
# src/agents/base_agent.py (update)
class BaseAgent(ABC):
    def __init__(self, name: str, comm_manager: CommunicationManager = None):
        # ... existing init ...
        self.comm_manager = comm_manager
        if comm_manager:
            comm_manager.register_agent(name, self.handle_message)
            
    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        if message.message_type == 'request':
            response = await self.process_request(message.content)
            await self.send_response(message.sender, response)
        elif message.message_type == 'notification':
            await self.process_notification(message.content)
            
    async def request_from_agent(self, agent_id: str, request: Dict):
        """Request information from another agent"""
        message = Message(
            sender=self.name,
            recipient=agent_id,
            message_type='request',
            content=request,
            timestamp=datetime.now()
        )
        await self.comm_manager.send_message(message)
```

#### 3.3 Implement Peer Review Mechanism
```python
# src/collaboration/peer_review.py
class PeerReviewMechanism:
    def __init__(self, comm_manager: CommunicationManager):
        self.comm_manager = comm_manager
        
    async def request_review(self, output: Dict, reviewer_agents: List[str]):
        """Request peer review from specific agents"""
        review_requests = []
        for agent in reviewer_agents:
            request = {
                'action': 'review',
                'output': output,
                'criteria': ['accuracy', 'completeness', 'quality']
            }
            review_requests.append(
                self.comm_manager.send_message(
                    Message('orchestrator', agent, 'review_request', request, datetime.now())
                )
            )
        
        reviews = await asyncio.gather(*review_requests)
        return self.synthesize_reviews(reviews)
```

### Testing Plan

```python
# tests/unit/communication/test_manager.py
@pytest.mark.asyncio
async def test_agent_registration():
    manager = CommunicationManager()
    
    async def handler(message):
        return f"Handled: {message.content}"
    
    manager.register_agent("agent1", handler)
    assert "agent1" in manager.agents

@pytest.mark.asyncio
async def test_message_sending():
    manager = CommunicationManager()
    messages_received = []
    
    async def handler(message):
        messages_received.append(message)
    
    manager.register_agent("agent1", handler)
    
    msg = Message("sender", "agent1", "test", {"data": "hello"}, datetime.now())
    await manager.send_message(msg)
    
    # Process message queue
    await manager.process_messages()
    
    assert len(messages_received) == 1
    assert messages_received[0].content["data"] == "hello"
```

**Integration Test:**
```python
# tests/integration/test_agent_communication.py
@pytest.mark.asyncio
async def test_agent_to_agent_communication():
    manager = CommunicationManager()
    context = SharedContextPool()
    
    agent1 = TaskAgent("agent1", shared_context=context, comm_manager=manager)
    agent2 = TaskAgent("agent2", shared_context=context, comm_manager=manager)
    
    # Agent1 requests information from Agent2
    await agent1.request_from_agent("agent2", {"query": "status"})
    
    # Verify Agent2 received and responded
    # Check shared context for response
```

**Verification:**
- Two agents can exchange messages
- Broadcast reaches all agents except sender
- Message queue processes correctly

---

## Phase 4: Advanced Workflow Patterns (Week 4)

### Objectives
- Implement Conditional workflows
- Add Iterative workflows
- Create Hierarchical workflows

### Implementation Steps

#### 4.1 Conditional Workflow
```python
# src/workflows/conditional_workflow.py
from typing import Dict, Callable
from src.workflows.base_workflow import BaseWorkflow

class ConditionalWorkflow(BaseWorkflow):
    def __init__(self, name: str):
        super().__init__(name)
        self.conditions = {}
        self.branches = {}
        
    def add_condition(self, name: str, condition: Callable[[Dict], str]):
        """Add a condition that returns branch name"""
        self.conditions[name] = condition
        
    def add_branch(self, branch_name: str, steps: List[ExecutionStep]):
        """Add a branch with its steps"""
        self.branches[branch_name] = steps
        
    async def execute(self) -> WorkflowResult:
        """Execute workflow with conditional branching"""
        start_time = datetime.now()
        results = []
        
        # Evaluate conditions based on context
        context = await self.shared_context.retrieve("workflow_context")
        
        for condition_name, condition_func in self.conditions.items():
            branch_name = condition_func(context)
            if branch_name in self.branches:
                # Execute the selected branch
                branch_results = await self._execute_branch(branch_name)
                results.extend(branch_results)
                
        return WorkflowResult(
            workflow_id=self.name,
            pattern=WorkflowPattern.CONDITIONAL,
            results=results,
            total_duration=(datetime.now() - start_time).seconds
        )
```

#### 4.2 Iterative Workflow
```python
# src/workflows/iterative_workflow.py
class IterativeWorkflow(BaseWorkflow):
    def __init__(self, name: str, max_iterations: int = 5):
        super().__init__(name)
        self.max_iterations = max_iterations
        self.convergence_criteria = None
        
    def set_convergence_criteria(self, criteria: Callable[[Dict], bool]):
        """Set function to check if iteration should stop"""
        self.convergence_criteria = criteria
        
    async def execute(self) -> WorkflowResult:
        """Execute workflow with iterations until convergence"""
        results = []
        iteration = 0
        converged = False
        
        while iteration < self.max_iterations and not converged:
            iteration_results = await self._execute_iteration(iteration)
            results.extend(iteration_results)
            
            # Check convergence
            if self.convergence_criteria:
                context = await self.shared_context.retrieve("iteration_results")
                converged = self.convergence_criteria(context)
                
            # Share iteration results
            await self.shared_context.store(
                f"iteration_{iteration}_results",
                iteration_results
            )
            
            iteration += 1
            
        return WorkflowResult(
            workflow_id=self.name,
            pattern=WorkflowPattern.ITERATIVE,
            results=results,
            metadata={"iterations": iteration, "converged": converged}
        )
```

#### 4.3 Hierarchical Workflow
```python
# src/workflows/hierarchical_workflow.py
class HierarchicalWorkflow(BaseWorkflow):
    def __init__(self, name: str):
        super().__init__(name)
        self.manager_agent = None
        self.team_leads = []
        self.specialists = {}
        
    def set_hierarchy(self, manager: BaseAgent, leads: List[BaseAgent], 
                     specialists: Dict[str, List[BaseAgent]]):
        """Define the agent hierarchy"""
        self.manager_agent = manager
        self.team_leads = leads
        self.specialists = specialists
        
    async def execute(self) -> WorkflowResult:
        """Execute with hierarchical delegation"""
        # Manager analyzes and creates plan
        plan = await self.manager_agent.create_execution_plan(self.prompt)
        
        # Delegate to team leads
        lead_tasks = []
        for lead, tasks in zip(self.team_leads, plan.task_groups):
            lead_tasks.append(
                self._delegate_to_lead(lead, tasks)
            )
        
        lead_results = await asyncio.gather(*lead_tasks)
        
        # Manager reviews and synthesizes
        final_result = await self.manager_agent.synthesize_results(lead_results)
        
        return WorkflowResult(
            workflow_id=self.name,
            pattern=WorkflowPattern.HIERARCHICAL,
            results=[final_result],
            metadata={"hierarchy_depth": 3}
        )
```

### Testing Plan

```python
# tests/unit/workflows/test_conditional_workflow.py
@pytest.mark.asyncio
async def test_conditional_branching():
    workflow = ConditionalWorkflow("test_conditional")
    
    # Define condition
    def check_complexity(context):
        return "complex" if context.get("complexity", 0) > 0.7 else "simple"
    
    workflow.add_condition("complexity_check", check_complexity)
    
    # Add branches
    workflow.add_branch("simple", [
        ExecutionStep(agent_type="task", task="simple_analysis")
    ])
    workflow.add_branch("complex", [
        ExecutionStep(agent_type="research", task="deep_analysis"),
        ExecutionStep(agent_type="technical", task="implementation")
    ])
    
    # Set context
    workflow.shared_context.store("workflow_context", {"complexity": 0.8})
    
    # Execute
    result = await workflow.execute()
    
    # Verify complex branch was taken
    assert len(result.results) == 2
    assert any("deep_analysis" in str(r) for r in result.results)
```

```python
# tests/unit/workflows/test_iterative_workflow.py
@pytest.mark.asyncio
async def test_iteration_convergence():
    workflow = IterativeWorkflow("test_iterative", max_iterations=3)
    
    # Convergence after 2 iterations
    iteration_count = 0
    def check_convergence(context):
        nonlocal iteration_count
        iteration_count += 1
        return iteration_count >= 2
    
    workflow.set_convergence_criteria(check_convergence)
    
    result = await workflow.execute()
    
    assert result.metadata["iterations"] == 2
    assert result.metadata["converged"] == True
```

**Verification:**
- Conditional workflow selects correct branch
- Iterative workflow stops at convergence
- Hierarchical workflow properly delegates tasks

---

## Phase 5: Vector Memory Implementation (Week 5)

### Objectives
- Add vector database for similarity search
- Implement embedding generation
- Enable semantic memory retrieval

### Implementation Steps

#### 5.1 Add Vector Store
```python
# src/memory/vector_store.py
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb

class VectorMemoryStore:
    def __init__(self, collection_name: str = "agent_memories"):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(collection_name)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    async def store_memory(self, memory_id: str, content: str, metadata: Dict):
        """Store memory with vector embedding"""
        embedding = self.encoder.encode(content)
        
        self.collection.add(
            embeddings=[embedding.tolist()],
            documents=[content],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
    async def retrieve_similar(self, query: str, limit: int = 5) -> List[Dict]:
        """Retrieve memories similar to query"""
        query_embedding = self.encoder.encode(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=limit
        )
        
        return [
            {
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            }
            for i in range(len(results['ids'][0]))
        ]
```

#### 5.2 Integrate with Persistent Knowledge Base
```python
# src/memory/persistent_knowledge.py
from src.memory.vector_store import VectorMemoryStore

class PersistentKnowledgeBase(BaseMemory):
    def __init__(self):
        self.learned_patterns = VectorMemoryStore("learned_patterns")
        self.user_preferences = VectorMemoryStore("user_preferences")
        self.domain_knowledge = VectorMemoryStore("domain_knowledge")
        self.failure_patterns = VectorMemoryStore("failure_patterns")
        
    async def store_pattern(self, pattern: Dict, pattern_type: str):
        """Store a learned pattern"""
        content = self._serialize_pattern(pattern)
        metadata = {
            'type': pattern_type,
            'timestamp': datetime.now().isoformat(),
            'success_rate': pattern.get('success_rate', 0.0)
        }
        
        store = getattr(self, f"{pattern_type}_patterns")
        await store.store_memory(
            f"{pattern_type}_{datetime.now().timestamp()}",
            content,
            metadata
        )
        
    async def find_similar_patterns(self, context: str, pattern_type: str) -> List[Dict]:
        """Find patterns similar to current context"""
        store = getattr(self, f"{pattern_type}_patterns")
        return await store.retrieve_similar(context, limit=3)
```

### Testing Plan

```python
# tests/unit/memory/test_vector_store.py
@pytest.mark.asyncio
async def test_vector_similarity_search():
    store = VectorMemoryStore("test_memories")
    
    # Store related memories
    await store.store_memory("mem1", "Python code for data analysis", {"type": "code"})
    await store.store_memory("mem2", "JavaScript web development", {"type": "code"})
    await store.store_memory("mem3", "Python machine learning tutorial", {"type": "tutorial"})
    
    # Search for Python-related memories
    results = await store.retrieve_similar("Python programming", limit=2)
    
    # Should return Python-related memories first
    assert len(results) == 2
    assert "Python" in results[0]['content']
    assert results[0]['distance'] < results[1]['distance']  # Closer match
```

**Verification:**
- Vector store returns semantically similar memories
- Distance metrics are meaningful
- Metadata is preserved

---

## Phase 6: Learning System Implementation (Week 6)

### Objectives
- Implement user feedback processing
- Add pattern recognition
- Create adaptive behavior system

### Implementation Steps

#### 6.1 User Feedback Processor
```python
# src/learning/feedback_processor.py
from enum import Enum
from typing import Dict, List

class FeedbackType(Enum):
    CORRECTION = "correction"
    PREFERENCE = "preference"
    GUIDANCE = "guidance"
    RATING = "rating"

class UserFeedbackProcessor:
    def __init__(self, knowledge_base: PersistentKnowledgeBase):
        self.knowledge_base = knowledge_base
        
    async def process_feedback(self, feedback: Dict):
        """Process user feedback and update knowledge"""
        feedback_type = FeedbackType(feedback['type'])
        
        if feedback_type == FeedbackType.CORRECTION:
            await self._process_correction(feedback)
        elif feedback_type == FeedbackType.PREFERENCE:
            await self._process_preference(feedback)
        elif feedback_type == FeedbackType.GUIDANCE:
            await self._process_guidance(feedback)
        elif feedback_type == FeedbackType.RATING:
            await self._process_rating(feedback)
            
    async def _process_preference(self, feedback: Dict):
        """Store user preferences"""
        preference = {
            'context': feedback['context'],
            'preference': feedback['preference'],
            'examples': feedback.get('examples', []),
            'strength': feedback.get('strength', 0.5)
        }
        
        await self.knowledge_base.store_pattern(
            preference,
            'user_preferences'
        )
```

#### 6.2 Pattern Recognition System
```python
# src/learning/pattern_learner.py
class PatternLearner:
    def __init__(self, knowledge_base: PersistentKnowledgeBase):
        self.knowledge_base = knowledge_base
        self.min_confidence = 0.7
        
    async def analyze_workflow_success(self, workflow: WorkflowResult):
        """Extract patterns from successful workflows"""
        if workflow.success_rate < self.min_confidence:
            return
            
        pattern = {
            'workflow_type': workflow.pattern.value,
            'agent_sequence': self._extract_agent_sequence(workflow),
            'context_transitions': self._extract_context_flow(workflow),
            'decision_points': self._extract_decisions(workflow),
            'performance_metrics': {
                'duration': workflow.total_duration,
                'success_rate': workflow.success_rate,
                'resource_usage': workflow.resource_usage
            }
        }
        
        # Check if similar pattern exists
        similar = await self.knowledge_base.find_similar_patterns(
            str(pattern),
            'learned'
        )
        
        if similar and similar[0]['distance'] < 0.1:
            # Update existing pattern
            await self._update_pattern(similar[0], pattern)
        else:
            # Store new pattern
            await self.knowledge_base.store_pattern(pattern, 'learned')
```

#### 6.3 Adaptive Behavior System
```python
# src/learning/adaptive_system.py
class AdaptiveBehaviorSystem:
    def __init__(self, knowledge_base: PersistentKnowledgeBase):
        self.knowledge_base = knowledge_base
        self.adaptation_threshold = 0.6
        
    async def get_adaptations(self, context: Dict) -> Dict:
        """Get behavioral adaptations based on context"""
        adaptations = {}
        
        # Check user preferences
        preferences = await self.knowledge_base.find_similar_patterns(
            str(context),
            'user_preferences'
        )
        
        if preferences:
            adaptations['preferences'] = [
                p for p in preferences 
                if p['distance'] < self.adaptation_threshold
            ]
            
        # Check learned patterns
        patterns = await self.knowledge_base.find_similar_patterns(
            str(context),
            'learned'
        )
        
        if patterns:
            adaptations['patterns'] = [
                p for p in patterns
                if p['metadata']['success_rate'] > 0.8
            ]
            
        return adaptations
```

### Testing Plan

```python
# tests/unit/learning/test_feedback_processor.py
@pytest.mark.asyncio
async def test_preference_processing():
    knowledge_base = PersistentKnowledgeBase()
    processor = UserFeedbackProcessor(knowledge_base)
    
    feedback = {
        'type': 'preference',
        'context': 'code_documentation',
        'preference': 'detailed_explanations',
        'examples': ['Added docstrings', 'Included usage examples'],
        'strength': 0.9
    }
    
    await processor.process_feedback(feedback)
    
    # Verify preference was stored
    similar = await knowledge_base.find_similar_patterns(
        'code_documentation',
        'user_preferences'
    )
    
    assert len(similar) > 0
    assert similar[0]['metadata']['type'] == 'user_preferences'
```

**Verification:**
- Feedback is properly categorized and stored
- Pattern recognition identifies repeated successes
- Adaptive system retrieves relevant adaptations

---

## Phase 7: Frontend Collaboration UI (Week 7)

### Objectives
- Add agent status visualization
- Implement memory sharing display
- Create learning progress indicators

### Implementation Steps

#### 7.1 Agent Status Component
```typescript
// shepherd-gui/src/components/features/agents/agent-status.tsx
import React from 'react'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'

interface AgentStatus {
  id: string
  name: string
  type: string
  status: 'idle' | 'working' | 'communicating' | 'learning'
  currentTask?: string
  progress?: number
}

export function AgentStatusPanel({ agents }: { agents: AgentStatus[] }) {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium">Active Agents</h3>
      {agents.map(agent => (
        <div key={agent.id} className="p-2 border rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">{agent.name}</span>
            <Badge variant={getStatusVariant(agent.status)}>
              {agent.status}
            </Badge>
          </div>
          {agent.currentTask && (
            <p className="text-xs text-muted-gray mt-1">{agent.currentTask}</p>
          )}
          {agent.progress !== undefined && (
            <Progress value={agent.progress} className="mt-2 h-2" />
          )}
        </div>
      ))}
    </div>
  )
}
```

#### 7.2 Memory Sharing Visualizer
```typescript
// shepherd-gui/src/components/features/memory/memory-flow.tsx
import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface MemoryTransfer {
  id: string
  from: string
  to: string
  type: 'discovery' | 'context' | 'learning'
  content: string
}

export function MemoryFlowVisualizer() {
  const [transfers, setTransfers] = useState<MemoryTransfer[]>([])
  
  useEffect(() => {
    // Subscribe to memory transfer events via WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws')
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'memory_transfer') {
        setTransfers(prev => [...prev, data.transfer].slice(-5))
      }
    }
    
    return () => ws.close()
  }, [])
  
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium">Memory Sharing</h3>
      <AnimatePresence>
        {transfers.map(transfer => (
          <motion.div
            key={transfer.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="p-2 bg-accent/20 rounded border border-border-gray"
          >
            <div className="flex items-center gap-2 text-xs">
              <span className="font-medium">{transfer.from}</span>
              <span>→</span>
              <span className="font-medium">{transfer.to}</span>
              <Badge variant="outline" className="ml-auto">
                {transfer.type}
              </Badge>
            </div>
            <p className="text-xs text-muted-gray mt-1">{transfer.content}</p>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
```

#### 7.3 Learning Progress Tracker
```typescript
// shepherd-gui/src/components/features/learning/learning-progress.tsx
interface LearningMetric {
  category: string
  current: number
  target: number
  unit: string
}

export function LearningProgressTracker({ metrics }: { metrics: LearningMetric[] }) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium">Learning Progress</h3>
      {metrics.map(metric => (
        <div key={metric.category} className="space-y-1">
          <div className="flex justify-between text-xs">
            <span>{metric.category}</span>
            <span>{metric.current}/{metric.target} {metric.unit}</span>
          </div>
          <Progress 
            value={(metric.current / metric.target) * 100} 
            className="h-2"
          />
        </div>
      ))}
    </div>
  )
}
```

### Testing Plan

```typescript
// shepherd-gui/__tests__/components/agents/agent-status.test.tsx
import { render, screen } from '@testing-library/react'
import { AgentStatusPanel } from '@/components/features/agents/agent-status'

describe('AgentStatusPanel', () => {
  test('displays agent statuses correctly', () => {
    const agents = [
      { id: '1', name: 'Research Agent', type: 'research', status: 'working', currentTask: 'Analyzing data', progress: 75 }
    ]
    
    render(<AgentStatusPanel agents={agents} />)
    
    expect(screen.getByText('Research Agent')).toBeInTheDocument()
    expect(screen.getByText('working')).toBeInTheDocument()
    expect(screen.getByText('Analyzing data')).toBeInTheDocument()
  })
})
```

**Verification:**
- Agent status updates in real-time
- Memory transfers are visualized
- Learning progress is tracked

---

## Phase 8: Integration Testing (Week 8)

### Objectives
- Test complete agent collaboration flow
- Verify memory persistence
- Validate learning improvements

### Implementation Steps

#### 8.1 End-to-End Collaboration Test
```python
# tests/integration/test_full_collaboration.py
@pytest.mark.asyncio
async def test_full_agent_collaboration():
    """Test complete collaboration scenario"""
    # Setup
    orchestrator = IntelligentOrchestrator()
    
    # Complex prompt requiring collaboration
    prompt = """
    Analyze the codebase for security vulnerabilities,
    create a report, and suggest fixes with implementation examples.
    """
    
    # Execute
    result = await orchestrator.execute(prompt, {"project_folder": "/test/project"})
    
    # Verify collaboration occurred
    assert len(result.agents_involved) >= 3  # Research, Security, Technical
    assert result.memory_shares > 0
    assert result.peer_reviews > 0
    
    # Verify learning
    patterns = await orchestrator.knowledge_base.find_similar_patterns(
        "security_analysis",
        "learned"
    )
    assert len(patterns) > 0
```

#### 8.2 Memory Persistence Test
```python
@pytest.mark.asyncio
async def test_memory_persistence():
    """Test that memories persist across sessions"""
    # First session
    orchestrator1 = IntelligentOrchestrator()
    await orchestrator1.execute("Learn this: always use type hints in Python")
    
    # New session
    orchestrator2 = IntelligentOrchestrator()
    preferences = await orchestrator2.knowledge_base.find_similar_patterns(
        "Python coding",
        "user_preferences"
    )
    
    assert any("type hints" in p['content'] for p in preferences)
```

### Testing Plan

**System Integration Tests:**
1. Multi-agent workflow with memory sharing
2. Learning from user feedback
3. Pattern recognition and reuse
4. WebSocket real-time updates
5. Frontend-backend synchronization

**Performance Tests:**
```python
# tests/performance/test_scalability.py
@pytest.mark.performance
async def test_agent_scalability():
    """Test system with many agents"""
    orchestrator = IntelligentOrchestrator()
    
    # Create workflow with 10 parallel agents
    start_time = time.time()
    result = await orchestrator.execute(
        "Analyze 10 different aspects of the system simultaneously"
    )
    duration = time.time() - start_time
    
    assert len(result.agents_involved) >= 10
    assert duration < 30  # Should complete within 30 seconds
    assert result.memory_shares > 20  # Agents should share discoveries
```

**Verification:**
- Full collaboration scenarios work end-to-end
- Performance meets requirements
- Memory persists correctly

---

## Phase 9: Advanced Learning Features (Week 9)

### Objectives
- Implement reinforcement learning
- Add meta-learning capabilities
- Create predictive adaptations

### Implementation Steps

#### 9.1 Reinforcement Learning System
```python
# src/learning/reinforcement.py
import numpy as np
from typing import Dict, List, Tuple

class RLAgentOptimizer:
    def __init__(self, learning_rate: float = 0.1, epsilon: float = 0.1):
        self.q_table = {}
        self.learning_rate = learning_rate
        self.epsilon = epsilon
        self.discount_factor = 0.9
        
    def get_state_key(self, context: Dict) -> str:
        """Convert context to state representation"""
        return f"{context['task_type']}_{context['complexity']}_{context.get('user_preference', 'none')}"
        
    def select_action(self, state: str, available_actions: List[str]) -> str:
        """Select action using epsilon-greedy strategy"""
        if np.random.random() < self.epsilon:
            return np.random.choice(available_actions)
        
        q_values = [self.q_table.get((state, action), 0.0) for action in available_actions]
        max_q = max(q_values)
        
        # Handle ties
        best_actions = [a for a, q in zip(available_actions, q_values) if q == max_q]
        return np.random.choice(best_actions)
        
    def update_q_value(self, state: str, action: str, reward: float, next_state: str, done: bool):
        """Update Q-value based on experience"""
        current_q = self.q_table.get((state, action), 0.0)
        
        if done:
            target = reward
        else:
            next_actions = self.get_available_actions(next_state)
            next_q_values = [self.q_table.get((next_state, a), 0.0) for a in next_actions]
            target = reward + self.discount_factor * max(next_q_values, default=0.0)
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (target - current_q)
        self.q_table[(state, action)] = new_q
```

#### 9.2 Meta-Learning System
```python
# src/learning/meta_learning.py
class MetaLearningSystem:
    def __init__(self):
        self.task_embeddings = {}
        self.adaptation_strategies = {}
        self.few_shot_examples = {}
        
    async def learn_task_representation(self, task: Dict, outcome: Dict):
        """Learn abstract representation of tasks"""
        task_type = task['type']
        
        if task_type not in self.task_embeddings:
            self.task_embeddings[task_type] = {
                'successful_features': [],
                'failure_features': [],
                'avg_performance': 0.0
            }
        
        features = self._extract_task_features(task)
        
        if outcome['success']:
            self.task_embeddings[task_type]['successful_features'].append(features)
        else:
            self.task_embeddings[task_type]['failure_features'].append(features)
            
    async def get_adaptation_strategy(self, new_task: Dict) -> Dict:
        """Get rapid adaptation strategy for new task"""
        # Find similar tasks
        similar_tasks = self._find_similar_tasks(new_task)
        
        if not similar_tasks:
            return {'strategy': 'explore', 'confidence': 0.2}
        
        # Extract successful strategies
        successful_strategies = []
        for task in similar_tasks:
            if task['outcome']['success']:
                successful_strategies.append(task['strategy'])
        
        if successful_strategies:
            # Use most common successful strategy
            strategy = max(set(successful_strategies), key=successful_strategies.count)
            confidence = len(successful_strategies) / len(similar_tasks)
            
            return {
                'strategy': strategy,
                'confidence': confidence,
                'examples': self._get_few_shot_examples(strategy)
            }
        
        return {'strategy': 'cautious_explore', 'confidence': 0.4}
```

### Testing Plan

```python
# tests/unit/learning/test_reinforcement.py
def test_q_learning_convergence():
    """Test that Q-learning converges to optimal policy"""
    rl_optimizer = RLAgentOptimizer(learning_rate=0.1)
    
    # Simple environment: choosing between 'fast' and 'accurate'
    states = ['simple_task', 'complex_task']
    actions = ['fast_approach', 'accurate_approach']
    
    # Optimal policy: fast for simple, accurate for complex
    optimal_rewards = {
        ('simple_task', 'fast_approach'): 1.0,
        ('simple_task', 'accurate_approach'): 0.5,
        ('complex_task', 'fast_approach'): -0.5,
        ('complex_task', 'accurate_approach'): 1.0
    }
    
    # Train for 1000 episodes
    for _ in range(1000):
        state = np.random.choice(states)
        action = rl_optimizer.select_action(state, actions)
        reward = optimal_rewards[(state, action)]
        
        # Terminal state
        rl_optimizer.update_q_value(state, action, reward, state, done=True)
    
    # Verify learned optimal policy
    assert rl_optimizer.select_action('simple_task', actions) == 'fast_approach'
    assert rl_optimizer.select_action('complex_task', actions) == 'accurate_approach'
```

**Verification:**
- RL system learns optimal policies
- Meta-learning accelerates adaptation
- Few-shot learning works for new tasks

---

## Phase 10: Production Readiness (Week 10)

### Objectives
- Add monitoring and observability
- Implement safety mechanisms
- Create deployment pipeline

### Implementation Steps

#### 10.1 Monitoring System
```python
# src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import structlog

# Metrics
agent_tasks_total = Counter('agent_tasks_total', 'Total tasks by agent', ['agent_type'])
workflow_duration = Histogram('workflow_duration_seconds', 'Workflow execution time')
memory_usage = Gauge('memory_usage_bytes', 'Memory usage by component', ['component'])
learning_accuracy = Gauge('learning_accuracy', 'Learning system accuracy')

logger = structlog.get_logger()

class MonitoringSystem:
    def __init__(self):
        self.metrics = {
            'agent_performance': {},
            'memory_efficiency': {},
            'learning_progress': {}
        }
        
    async def record_agent_task(self, agent_type: str, duration: float, success: bool):
        """Record agent task metrics"""
        agent_tasks_total.labels(agent_type=agent_type).inc()
        
        if agent_type not in self.metrics['agent_performance']:
            self.metrics['agent_performance'][agent_type] = {
                'total_tasks': 0,
                'successful_tasks': 0,
                'avg_duration': 0.0
            }
        
        metrics = self.metrics['agent_performance'][agent_type]
        metrics['total_tasks'] += 1
        if success:
            metrics['successful_tasks'] += 1
            
        logger.info(
            "agent_task_completed",
            agent_type=agent_type,
            duration=duration,
            success=success
        )
```

#### 10.2 Safety Mechanisms
```python
# src/safety/guardrails.py
class SafetyGuardrails:
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.content_filter = ContentFilter()
        self.resource_monitor = ResourceMonitor()
        
    async def validate_agent_action(self, agent: str, action: Dict) -> Tuple[bool, str]:
        """Validate agent action against safety rules"""
        # Check rate limits
        if not self.rate_limiter.check_limit(agent):
            return False, "Rate limit exceeded"
        
        # Check content safety
        if not self.content_filter.is_safe(action):
            return False, "Content policy violation"
        
        # Check resource usage
        if not self.resource_monitor.has_capacity(action):
            return False, "Insufficient resources"
        
        return True, "OK"
        
    async def validate_memory_share(self, content: Dict) -> bool:
        """Validate memory content before sharing"""
        # Check for sensitive information
        if self._contains_sensitive_data(content):
            logger.warning("Blocked sensitive data sharing", content_type=type(content))
            return False
            
        # Check size limits
        if self._exceeds_size_limit(content):
            return False
            
        return True
```

#### 10.3 Deployment Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  shepherd-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - DATABASE_URL=postgresql://postgres:password@db:5432/shepherd
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
      - ollama
      
  shepherd-gui:
    build: ./shepherd-gui
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://shepherd-backend:8000
      
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=shepherd
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    
  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
      
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      
volumes:
  postgres_data:
  ollama_data:
```

### Testing Plan

```python
# tests/integration/test_production_safety.py
@pytest.mark.asyncio
async def test_rate_limiting():
    """Test that rate limiting prevents abuse"""
    guardrails = SafetyGuardrails()
    agent = "test_agent"
    
    # Should allow initial requests
    for _ in range(10):
        valid, msg = await guardrails.validate_agent_action(agent, {"action": "test"})
        assert valid
    
    # Should block after limit
    valid, msg = await guardrails.validate_agent_action(agent, {"action": "test"})
    assert not valid
    assert "Rate limit" in msg
```

**Verification:**
- Monitoring captures all key metrics
- Safety mechanisms prevent abuse
- System deploys successfully with docker-compose

---

## Phase 11: Performance Optimization (Week 11)

### Objectives
- Optimize memory retrieval speed
- Implement caching strategies
- Add batch processing

### Implementation Steps

#### 11.1 Memory Caching Layer
```python
# src/memory/cache.py
from functools import lru_cache
import asyncio
from typing import Dict, List, Optional

class MemoryCache:
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.access_times = {}
        
    async def get(self, key: str) -> Optional[Dict]:
        """Get from cache with LRU eviction"""
        if key in self.cache:
            self.access_times[key] = asyncio.get_event_loop().time()
            return self.cache[key]
        return None
        
    async def set(self, key: str, value: Dict):
        """Set in cache with size limit"""
        if len(self.cache) >= self.max_size:
            # Evict least recently used
            lru_key = min(self.access_times, key=self.access_times.get)
            del self.cache[lru_key]
            del self.access_times[lru_key]
            
        self.cache[key] = value
        self.access_times[key] = asyncio.get_event_loop().time()
        
    @lru_cache(maxsize=128)
    def compute_embedding_similarity(self, embedding1: tuple, embedding2: tuple) -> float:
        """Cached similarity computation"""
        # Convert back from tuple (for caching) to array
        arr1 = np.array(embedding1)
        arr2 = np.array(embedding2)
        return np.dot(arr1, arr2) / (np.linalg.norm(arr1) * np.linalg.norm(arr2))
```

#### 11.2 Batch Processing System
```python
# src/optimization/batch_processor.py
class BatchProcessor:
    def __init__(self, batch_size: int = 10, timeout_seconds: float = 0.1):
        self.batch_size = batch_size
        self.timeout_seconds = timeout_seconds
        self.pending_items = []
        self.process_lock = asyncio.Lock()
        
    async def add_item(self, item: Dict) -> asyncio.Future:
        """Add item to batch and return future for result"""
        future = asyncio.Future()
        
        async with self.process_lock:
            self.pending_items.append((item, future))
            
            if len(self.pending_items) >= self.batch_size:
                await self._process_batch()
            else:
                # Schedule timeout processing
                asyncio.create_task(self._timeout_processor())
                
        return future
        
    async def _process_batch(self):
        """Process accumulated batch"""
        if not self.pending_items:
            return
            
        items, futures = zip(*self.pending_items)
        self.pending_items = []
        
        # Batch process all items
        results = await self._batch_operation(list(items))
        
        # Resolve futures
        for future, result in zip(futures, results):
            future.set_result(result)
```

### Testing Plan

```python
# tests/performance/test_optimization.py
@pytest.mark.asyncio
async def test_cache_performance():
    """Test that caching improves performance"""
    cache = MemoryCache()
    
    # First access - cache miss
    start = time.time()
    result = await cache.get("test_key")
    assert result is None
    
    # Store in cache
    await cache.set("test_key", {"data": "test"})
    
    # Second access - cache hit (should be much faster)
    start = time.time()
    result = await cache.get("test_key")
    cache_time = time.time() - start
    
    assert result["data"] == "test"
    assert cache_time < 0.001  # Sub-millisecond
```

**Verification:**
- Cache reduces memory retrieval time by >90%
- Batch processing improves throughput
- System handles 100+ concurrent agents

---

## Phase 12: Documentation and Finalization (Week 12)

### Objectives
- Complete API documentation
- Create user guides
- Final integration testing

### Implementation Steps

#### 12.1 API Documentation
```python
# src/api/docs.py
from fastapi import FastAPI
from pydantic import BaseModel, Field

class WorkflowExecuteRequest(BaseModel):
    """Request model for workflow execution"""
    prompt: str = Field(..., description="Natural language task description")
    context: Dict = Field(default={}, description="Additional context (project folder, etc)")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Analyze security vulnerabilities in the codebase",
                "context": {"project_folder": "/home/user/project"}
            }
        }

# In api/main.py
app = FastAPI(
    title="Shepherd Orchestrator API",
    description="Intelligent multi-agent workflow orchestration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

#### 12.2 User Guide Creation
```markdown
# docs/USER_GUIDE.md

# Shepherd User Guide

## Getting Started with Agent Collaboration

### Basic Usage
1. Start the application: `./scripts/start.sh --gui`
2. Create a new chat
3. Describe your task in natural language
4. Watch agents collaborate in real-time

### Understanding Agent Collaboration
- **Memory Sharing**: Agents share discoveries via the memory panel
- **Learning Progress**: Track how the system improves over time
- **Agent Status**: Monitor what each agent is working on

### Advanced Features
- **Teaching Preferences**: Use "I prefer..." statements
- **Correcting Mistakes**: Right-click any output to provide feedback
- **Viewing Patterns**: Check Settings > Learned Patterns
```

### Final Testing Plan

**Complete System Test:**
```python
# tests/system/test_complete_flow.py
@pytest.mark.system
async def test_complete_user_journey():
    """Test complete user journey from start to finish"""
    # 1. User starts application
    # 2. Creates new conversation
    # 3. Submits complex request
    # 4. Agents collaborate
    # 5. User provides feedback
    # 6. System learns and adapts
    # 7. Second similar request is faster/better
```

**Verification Checklist:**
- [ ] All unit tests pass (>90% coverage)
- [ ] Integration tests pass
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] Security review passed
- [ ] Deployment successful

---

## Summary

This implementation plan provides a structured approach to building the agent collaboration system:

1. **Foundation** (Weeks 1-2): Test infrastructure and memory system
2. **Core Features** (Weeks 3-6): Communication, workflows, vector memory, learning
3. **UI Integration** (Week 7): Frontend collaboration features
4. **Testing & Optimization** (Weeks 8-11): Integration, performance, safety
5. **Finalization** (Week 12): Documentation and deployment

Each phase builds on the previous one with clear deliverables and comprehensive testing. The modular approach allows for iterative development and continuous validation of functionality.