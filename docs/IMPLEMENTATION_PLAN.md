# Shepherd Agent Collaboration Implementation Plan

This document provides a sequenced, testable implementation plan for adding agent collaboration, memory sharing, and learning capabilities to Shepherd.

## Overview

The implementation is divided into 14 phases, each with specific deliverables and test plans. Each phase builds on the previous one and can be tested independently.

## Current Implementation Status

### ✅ Completed Phases (1-4)
- **Phase 1: Test Infrastructure** - Complete test framework with comprehensive testing
- **Phase 2: Memory System** - Three-tier memory architecture fully operational
- **Phase 3: Communication System** - Agent-to-agent messaging with peer review mechanisms
- **Phase 4: Tool Use Foundation** - Complete tool system with registry, execution engine, and built-in tools

### 🚧 Next Phase (5)
- **Phase 5: Conversation Compacting System** - Manage context window limitations and workflow segmentation

### 📊 Key Metrics
- **Total Tests**: 134+ (109 previous + 25 tool system tests)
- **Backend Test Success**: 100% (All tool tests passing)
- **Frontend Test Success**: 100% (7/7 passing)
- **Architecture Status**: Memory + Communication + Tool systems operational
- **Agent Integration**: BaseAgent class fully integrated with memory, communication, and tool systems

---

## Phase 1: Test Infrastructure Setup (Week 1) ✅ COMPLETED

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

**Verification:** ✅ COMPLETED
- Run `pytest tests/` - 109/114 backend tests passing (96% success rate)
- Frontend tests: 7/7 passing (100% success rate)  
- Test infrastructure fully operational with mock agents and fixtures
- Comprehensive test framework supporting TDD with async capabilities
- Total test coverage: 116 working tests (109 backend + 7 frontend)

---

## Phase 2: Memory System Foundation (Week 2) ✅ COMPLETED

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

## Phase 3: Agent Communication System (Week 3) ✅ COMPLETED

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

**Verification:** ✅ COMPLETED
- Direct agent-to-agent messaging with CommunicationManager and structured protocols functional
- Event-based communication with Message dataclass and 13 MessageType enums implemented
- Peer review mechanisms with consensus building and quality assurance operational
- BaseAgent communication integration with send_message, request_response, and broadcast methods working
- Communication testing infrastructure with 25 additional tests (17 unit + 8 integration) passing
- Request-response patterns with timeout handling and error recovery functional
- Message routing and queuing with conversation tracking and statistics implemented
- Total working tests: 109 tests (94 stable backend tests + 7 frontend tests + additional communication tests)

---

## Phase 4: Tool Use Foundation (Week 4) ✅ COMPLETED

### Objectives
- Implement core tool registry and execution infrastructure
- Add tool-aware agent capabilities
- Create basic tool types (computation, information retrieval, file operations)
- Integrate tool use into existing workflow patterns

### Implementation Steps

#### 4.1 Core Tool Infrastructure

```python
# src/tools/__init__.py
# Package initialization with tool exports

# src/tools/registry.py
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import asyncio
import logging

class ToolRegistry:
    """Central registry for all available tools"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.categories: Dict[str, List[str]] = {}
        self.permissions: Dict[str, List[str]] = {}
        
    def register_tool(self, tool: 'BaseTool') -> None:
        """Register a tool in the registry"""
        self.tools[tool.name] = tool
        
        # Add to category
        category = tool.category
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(tool.name)
        
        # Set default permissions
        self.permissions[tool.name] = tool.default_permissions
        
    def get_tool(self, name: str) -> Optional['BaseTool']:
        """Get tool by name"""
        return self.tools.get(name)
        
    def get_tools_by_category(self, category: str) -> List['BaseTool']:
        """Get all tools in a category"""
        tool_names = self.categories.get(category, [])
        return [self.tools[name] for name in tool_names]
        
    def search_tools(self, query: str, agent_permissions: List[str] = None) -> List['BaseTool']:
        """Search for tools matching query and permissions"""
        results = []
        for tool in self.tools.values():
            # Check description match
            if query.lower() in tool.description.lower():
                # Check permissions if provided
                if agent_permissions is None or any(
                    perm in agent_permissions for perm in self.permissions[tool.name]
                ):
                    results.append(tool)
        return results
```

#### 4.2 Base Tool Interface

```python
# src/tools/base_tool.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class ToolCategory(Enum):
    COMPUTATION = "computation"
    INFORMATION = "information"
    FILE_SYSTEM = "file_system"
    COMMUNICATION = "communication"
    SYSTEM = "system"
    CREATIVE = "creative"

@dataclass
class ToolParameter:
    """Tool parameter definition"""
    name: str
    param_type: type
    description: str
    required: bool = True
    default: Any = None
    validation_regex: str = None

@dataclass
class ToolResult:
    """Tool execution result"""
    success: bool
    data: Any = None
    error: str = None
    metadata: Dict[str, Any] = None
    execution_time: float = 0.0

class BaseTool(ABC):
    """Abstract base class for all tools"""
    
    def __init__(self, name: str, description: str, category: ToolCategory):
        self.name = name
        self.description = description
        self.category = category.value
        self.default_permissions = ["basic_tools"]
        
    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """Define tool parameters"""
        pass
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate parameters against tool schema"""
        for param in self.parameters:
            if param.required and param.name not in parameters:
                return False
            if param.name in parameters:
                if not isinstance(parameters[param.name], param.param_type):
                    return False
        return True
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for documentation"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.param_type.__name__,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default
                }
                for p in self.parameters
            ]
        }
```

#### 4.3 Core Tool Implementations

```python
# src/tools/core/computation_tools.py
import math
import ast
import operator
from src.tools.base_tool import BaseTool, ToolParameter, ToolResult, ToolCategory

class CalculatorTool(BaseTool):
    """Basic mathematical calculator tool"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations with support for basic operations",
            category=ToolCategory.COMPUTATION
        )
        
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="expression",
                param_type=str,
                description="Mathematical expression to evaluate (e.g., '2 + 3 * 4')"
            )
        ]
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute mathematical calculation"""
        try:
            expression = parameters["expression"]
            
            # Safe evaluation using ast
            result = self._safe_eval(expression)
            
            return ToolResult(
                success=True,
                data={"result": result, "expression": expression},
                metadata={"tool": "calculator", "operation": "evaluate"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Calculation error: {str(e)}"
            )
    
    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate mathematical expressions"""
        # Define allowed operations
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }
        
        # Define allowed functions
        functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'log': math.log,
            'abs': abs,
        }
        
        def _eval(node):
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Name):
                if node.id in functions:
                    return functions[node.id]
                else:
                    raise ValueError(f"Unknown variable: {node.id}")
            elif isinstance(node, ast.BinOp):
                return operators[type(node.op)](_eval(node.left), _eval(node.right))
            elif isinstance(node, ast.UnaryOp):
                return operators[type(node.op)](_eval(node.operand))
            elif isinstance(node, ast.Call):
                func = _eval(node.func)
                args = [_eval(arg) for arg in node.args]
                return func(*args)
            else:
                raise ValueError(f"Unsupported operation: {type(node)}")
        
        tree = ast.parse(expression, mode='eval')
        return _eval(tree.body)

class CodeExecutorTool(BaseTool):
    """Execute Python code in a sandboxed environment"""
    
    def __init__(self):
        super().__init__(
            name="code_executor",
            description="Execute Python code with safety restrictions",
            category=ToolCategory.COMPUTATION
        )
        self.default_permissions = ["code_execution"]
        
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="code",
                param_type=str,
                description="Python code to execute"
            ),
            ToolParameter(
                name="timeout",
                param_type=int,
                description="Execution timeout in seconds",
                required=False,
                default=10
            )
        ]
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute Python code safely"""
        try:
            code = parameters["code"]
            timeout = parameters.get("timeout", 10)
            
            # Create restricted execution environment
            restricted_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'list': list,
                    'dict': dict,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                }
            }
            
            # Capture output
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            try:
                # Execute with timeout
                import asyncio
                exec(code, restricted_globals)
                output = captured_output.getvalue()
                
                return ToolResult(
                    success=True,
                    data={"output": output, "code": code},
                    metadata={"tool": "code_executor", "timeout": timeout}
                )
                
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Code execution error: {str(e)}"
            )
```

```python
# src/tools/core/information_tools.py
import aiohttp
import json
from src.tools.base_tool import BaseTool, ToolParameter, ToolResult, ToolCategory

class WebSearchTool(BaseTool):
    """Web search tool using search APIs"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for current information",
            category=ToolCategory.INFORMATION
        )
        self.default_permissions = ["web_access"]
        
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                param_type=str,
                description="Search query"
            ),
            ToolParameter(
                name="max_results",
                param_type=int,
                description="Maximum number of results to return",
                required=False,
                default=5
            )
        ]
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Perform web search"""
        try:
            query = parameters["query"]
            max_results = parameters.get("max_results", 5)
            
            # For demonstration - in production would use real search API
            # This is a mock implementation
            mock_results = [
                {
                    "title": f"Search result {i+1} for '{query}'",
                    "url": f"https://example.com/result{i+1}",
                    "snippet": f"This is a mock search result snippet for query '{query}'. Result number {i+1}."
                }
                for i in range(min(max_results, 3))
            ]
            
            return ToolResult(
                success=True,
                data={"results": mock_results, "query": query, "count": len(mock_results)},
                metadata={"tool": "web_search", "api": "mock"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Web search error: {str(e)}"
            )

class FileReaderTool(BaseTool):
    """Read files from the file system"""
    
    def __init__(self):
        super().__init__(
            name="file_reader",
            description="Read text files from the file system",
            category=ToolCategory.FILE_SYSTEM
        )
        self.default_permissions = ["file_read"]
        
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                param_type=str,
                description="Path to the file to read"
            ),
            ToolParameter(
                name="encoding",
                param_type=str,
                description="File encoding",
                required=False,
                default="utf-8"
            )
        ]
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Read file contents"""
        try:
            file_path = parameters["file_path"]
            encoding = parameters.get("encoding", "utf-8")
            
            # Basic security check - prevent path traversal
            import os
            if ".." in file_path or file_path.startswith("/"):
                return ToolResult(
                    success=False,
                    error="Access denied: Invalid file path"
                )
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return ToolResult(
                success=True,
                data={"content": content, "file_path": file_path, "size": len(content)},
                metadata={"tool": "file_reader", "encoding": encoding}
            )
            
        except FileNotFoundError:
            return ToolResult(
                success=False,
                error=f"File not found: {file_path}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"File read error: {str(e)}"
            )
```

#### 4.4 Tool Execution Engine

```python
# src/tools/execution_engine.py
from typing import Dict, Any, Optional
import asyncio
import time
import logging
from src.tools.registry import ToolRegistry
from src.tools.base_tool import ToolResult

logger = logging.getLogger(__name__)

class ToolExecutionEngine:
    """Engine for executing tools with monitoring and error handling"""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.active_executions: Dict[str, Dict] = {}
        self.execution_history: List[Dict] = []
        
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], 
                          agent_id: str, timeout: float = 30.0) -> ToolResult:
        """Execute a tool with monitoring and timeout"""
        execution_id = f"{agent_id}_{tool_name}_{int(time.time())}"
        
        # Get tool from registry
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found in registry"
            )
        
        # Validate parameters
        if not tool.validate_parameters(parameters):
            return ToolResult(
                success=False,
                error=f"Invalid parameters for tool '{tool_name}'"
            )
        
        # Record execution start
        start_time = time.time()
        execution_info = {
            "id": execution_id,
            "tool_name": tool_name,
            "agent_id": agent_id,
            "parameters": parameters,
            "start_time": start_time,
            "status": "running"
        }
        self.active_executions[execution_id] = execution_info
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                tool.execute(parameters),
                timeout=timeout
            )
            
            # Record execution time
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            
            # Update execution info
            execution_info.update({
                "status": "completed",
                "duration": execution_time,
                "success": result.success,
                "end_time": time.time()
            })
            
            logger.info(f"Tool execution completed: {tool_name} by {agent_id} in {execution_time:.2f}s")
            
            return result
            
        except asyncio.TimeoutError:
            execution_info.update({
                "status": "timeout",
                "duration": timeout,
                "end_time": time.time()
            })
            
            logger.warning(f"Tool execution timeout: {tool_name} by {agent_id}")
            
            return ToolResult(
                success=False,
                error=f"Tool execution timeout after {timeout}s"
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            execution_info.update({
                "status": "error",
                "duration": execution_time,
                "error": str(e),
                "end_time": time.time()
            })
            
            logger.error(f"Tool execution error: {tool_name} by {agent_id}: {str(e)}")
            
            return ToolResult(
                success=False,
                error=f"Tool execution error: {str(e)}"
            )
            
        finally:
            # Move to history and cleanup
            if execution_id in self.active_executions:
                self.execution_history.append(self.active_executions[execution_id])
                del self.active_executions[execution_id]
                
                # Keep only last 1000 executions in history
                if len(self.execution_history) > 1000:
                    self.execution_history = self.execution_history[-1000:]
    
    def get_active_executions(self) -> List[Dict]:
        """Get currently running tool executions"""
        return list(self.active_executions.values())
    
    def get_execution_history(self, agent_id: str = None, limit: int = 100) -> List[Dict]:
        """Get execution history, optionally filtered by agent"""
        history = self.execution_history
        if agent_id:
            history = [ex for ex in history if ex.get("agent_id") == agent_id]
        return history[-limit:]
```

#### 4.5 BaseAgent Tool Integration

```python
# src/agents/base_agent.py (additions to existing class)
from src.tools.registry import ToolRegistry
from src.tools.execution_engine import ToolExecutionEngine
from src.tools.base_tool import ToolResult

class BaseAgent(ABC):
    def __init__(self, name: str, ...):
        # ... existing initialization ...
        
        # NEW: Tool system integration
        self.tool_registry: Optional[ToolRegistry] = None
        self.tool_engine: Optional[ToolExecutionEngine] = None
        self.allowed_tools: List[str] = []
        self.tool_permissions: List[str] = ["basic_tools"]
        
    def set_tool_system(self, registry: ToolRegistry, engine: ToolExecutionEngine):
        """Initialize tool system for this agent"""
        self.tool_registry = registry
        self.tool_engine = engine
        
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool with given parameters"""
        if not self.tool_engine:
            return ToolResult(
                success=False,
                error="Tool system not initialized for this agent"
            )
        
        # Check tool permissions
        if not await self.validate_tool_access(tool_name):
            return ToolResult(
                success=False,
                error=f"Agent '{self.name}' does not have permission to use tool '{tool_name}'"
            )
        
        # Execute tool
        result = await self.tool_engine.execute_tool(
            tool_name, parameters, self.name
        )
        
        # Store result in memory
        if result.success:
            await self.store_memory(
                f"tool_result_{tool_name}_{int(time.time())}",
                {
                    "tool": tool_name,
                    "parameters": parameters,
                    "result": result.data,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        return result
    
    async def validate_tool_access(self, tool_name: str) -> bool:
        """Check if agent has permission to use tool"""
        if not self.tool_registry:
            return False
            
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return False
        
        # Check if tool is in allowed list (if specified)
        if self.allowed_tools and tool_name not in self.allowed_tools:
            return False
        
        # Check permissions
        tool_permissions = self.tool_registry.permissions.get(tool_name, [])
        return any(perm in self.tool_permissions for perm in tool_permissions)
    
    async def select_tools_for_task(self, task_description: str) -> List[str]:
        """Select appropriate tools for a given task"""
        if not self.tool_registry:
            return []
        
        # Basic keyword-based tool selection
        selected_tools = []
        
        # Search for relevant tools
        tools = self.tool_registry.search_tools(task_description, self.tool_permissions)
        
        for tool in tools:
            if await self.validate_tool_access(tool.name):
                selected_tools.append(tool.name)
        
        return selected_tools
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of tools available to this agent"""
        if not self.tool_registry:
            return []
        
        available_tools = []
        for tool in self.tool_registry.tools.values():
            if await self.validate_tool_access(tool.name):
                available_tools.append(tool.get_schema())
        
        return available_tools
```

### Testing Plan

```python
# tests/unit/tools/test_tool_registry.py
import pytest
from src.tools.registry import ToolRegistry
from src.tools.core.computation_tools import CalculatorTool

def test_tool_registration():
    """Test tool registration and discovery"""
    registry = ToolRegistry()
    calculator = CalculatorTool()
    
    registry.register_tool(calculator)
    
    assert "calculator" in registry.tools
    assert registry.get_tool("calculator") == calculator
    assert "computation" in registry.categories
    assert "calculator" in registry.categories["computation"]

def test_tool_search():
    """Test tool search functionality"""
    registry = ToolRegistry()
    calculator = CalculatorTool()
    registry.register_tool(calculator)
    
    results = registry.search_tools("mathematical")
    assert len(results) == 1
    assert results[0].name == "calculator"

# tests/unit/tools/test_computation_tools.py
@pytest.mark.asyncio
async def test_calculator_tool():
    """Test calculator tool execution"""
    calculator = CalculatorTool()
    
    # Test simple calculation
    result = await calculator.execute({"expression": "2 + 3 * 4"})
    
    assert result.success == True
    assert result.data["result"] == 14
    assert result.data["expression"] == "2 + 3 * 4"

@pytest.mark.asyncio
async def test_calculator_error_handling():
    """Test calculator error handling"""
    calculator = CalculatorTool()
    
    # Test invalid expression
    result = await calculator.execute({"expression": "invalid_expression"})
    
    assert result.success == False
    assert "error" in result.error.lower()

# tests/integration/test_agent_tool_integration.py
@pytest.mark.asyncio
async def test_agent_tool_execution():
    """Test agent tool execution integration"""
    from src.tools.registry import ToolRegistry
    from src.tools.execution_engine import ToolExecutionEngine
    from src.tools.core.computation_tools import CalculatorTool
    from src.agents.task_agent import TaskAgent
    
    # Setup tool system
    registry = ToolRegistry()
    calculator = CalculatorTool()
    registry.register_tool(calculator)
    
    engine = ToolExecutionEngine(registry)
    
    # Create agent with tool access
    agent = TaskAgent("test_agent")
    agent.set_tool_system(registry, engine)
    agent.tool_permissions = ["basic_tools"]
    
    # Execute tool through agent
    result = await agent.execute_tool("calculator", {"expression": "10 + 5"})
    
    assert result.success == True
    assert result.data["result"] == 15

@pytest.mark.asyncio
async def test_tool_permission_validation():
    """Test tool permission system"""
    registry = ToolRegistry()
    calculator = CalculatorTool()
    registry.register_tool(calculator)
    
    engine = ToolExecutionEngine(registry)
    
    # Create agent without permissions
    agent = TaskAgent("test_agent")
    agent.set_tool_system(registry, engine)
    agent.tool_permissions = []  # No permissions
    
    # Should fail due to lack of permissions
    result = await agent.execute_tool("calculator", {"expression": "1 + 1"})
    
    assert result.success == False
    assert "permission" in result.error.lower()
```

**Verification:**
- Tool registry manages tool discovery and permissions
- Core tools (calculator, web search, file reader) work correctly
- Tool execution engine provides monitoring and timeout handling
- BaseAgent integration enables tool use with permission validation
- Comprehensive testing covers functionality and security

---

## Phase 5: Conversation Compacting System (Week 5)

### Objectives
- Implement conversation compacting to manage context window limitations
- Create token usage monitoring and warnings
- Add GUI components for conversation management
- Enable automatic and manual compacting strategies

### Implementation Steps

#### 5.1 Core Compacting Engine
```python
# src/memory/conversation_compactor.py
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class ConversationSegment:
    segment_id: str
    timestamp: datetime
    agent_interactions: List[Dict[str, Any]]
    workflow_pattern: str
    importance_score: float
    token_count: int
    summary: Optional[str] = None
    preserved_artifacts: List[str] = []

class ConversationCompactor:
    def __init__(self, shared_context: SharedContextPool, 
                 local_memory: AgentLocalMemory):
        self.shared_context = shared_context
        self.local_memory = local_memory
        self.token_threshold = 50000  # Configurable based on model
        self.compression_ratio = 0.3  # Target 70% reduction
        
    async def compact_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Main compacting orchestration method"""
        # 1. Analyze current conversation state
        analysis = await self._analyze_conversation_state(conversation_id)
        
        # 2. Segment conversation by workflows
        segments = await self._segment_by_workflows(conversation_id)
        
        # 3. Apply hierarchical compression
        compacted = await self._hierarchical_compression(segments)
        
        # 4. Preserve critical context
        preserved = await self._preserve_critical_context(compacted)
        
        return preserved
```

#### 5.2 Context Preservation Strategy
```python
# src/memory/context_preservation.py
class ContextPreservationStrategy:
    def __init__(self):
        self.preservation_rules = {
            "user_objectives": 1.0,      # Always preserve
            "critical_decisions": 0.9,    # High priority
            "workflow_outputs": 0.8,      # Important results
            "agent_discoveries": 0.7,     # Collaborative findings
            "intermediate_steps": 0.3,    # Low priority
            "debug_logs": 0.1            # Rarely preserve
        }
    
    async def preserve_critical_context(self, segments: List[ConversationSegment]) -> Dict:
        """Intelligently preserve important context across segments"""
        preserved = {
            "objectives": [],
            "decisions": [],
            "artifacts": [],
            "discoveries": [],
            "active_context": {}
        }
        
        for segment in segments:
            # Extract and score content
            content_items = await self._extract_content_items(segment)
            
            for item in content_items:
                score = self._calculate_preservation_score(item)
                if score > 0.5:  # Preservation threshold
                    category = self._categorize_content(item)
                    preserved[category].append(item)
        
        return preserved
```

#### 5.3 API Integration
```python
# api/conversation_manager.py
from fastapi import APIRouter, WebSocket
from typing import Optional

router = APIRouter()

class ConversationManager:
    def __init__(self):
        self.compactor = ConversationCompactor()
        self.active_conversations = {}
        
    @router.post("/api/conversations/{conversation_id}/compact")
    async def compact_conversation(self, conversation_id: str, 
                                 strategy: Optional[str] = "auto"):
        """Compact a conversation using specified strategy"""
        if strategy == "auto":
            # Automatic compacting based on token count
            result = await self.compactor.auto_compact(conversation_id)
        elif strategy == "milestone":
            # Compact at workflow milestones
            result = await self.compactor.milestone_compact(conversation_id)
        elif strategy == "selective":
            # User-guided selective preservation
            result = await self.compactor.selective_compact(conversation_id)
        
        return {"status": "success", "reduction": result.reduction_percentage}
    
    @router.websocket("/ws/conversation/{conversation_id}")
    async def conversation_websocket(self, websocket: WebSocket, 
                                   conversation_id: str):
        """Real-time conversation monitoring with auto-compacting"""
        await websocket.accept()
        
        while True:
            # Monitor token usage
            token_count = await self._get_token_count(conversation_id)
            
            if token_count > self.compactor.token_threshold * 0.8:
                # Send warning to client
                await websocket.send_json({
                    "type": "context_warning",
                    "message": "Approaching context limit",
                    "token_count": token_count,
                    "threshold": self.compactor.token_threshold
                })
```

#### 5.4 GUI Components
```typescript
// shepherd-gui/src/components/features/conversation/ConversationCompactor.tsx
import React, { useState, useEffect } from 'react';
import { useConversationStore } from '@/stores/conversation-store';

export const ConversationCompactor: React.FC = () => {
    const { currentConversation, tokenCount, threshold } = useConversationStore();
    const [showCompactDialog, setShowCompactDialog] = useState(false);
    const [compactStrategy, setCompactStrategy] = useState<'auto' | 'milestone' | 'selective'>('auto');
    
    useEffect(() => {
        // Monitor token usage
        if (tokenCount > threshold * 0.8) {
            setShowCompactDialog(true);
        }
    }, [tokenCount, threshold]);
    
    const handleCompact = async () => {
        const response = await fetch(`/api/conversations/${currentConversation.id}/compact`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ strategy: compactStrategy })
        });
        
        if (response.ok) {
            const result = await response.json();
            // Update UI with compacted conversation
            useConversationStore.getState().updateConversation(result);
        }
    };
    
    return (
        <>
            {/* Token usage indicator */}
            <div className="token-usage-bar">
                <div 
                    className="usage-fill"
                    style={{ width: `${(tokenCount / threshold) * 100}%` }}
                />
                <span>{tokenCount} / {threshold} tokens</span>
            </div>
            
            {/* Compact dialog */}
            {showCompactDialog && (
                <CompactDialog
                    onCompact={handleCompact}
                    onStrategyChange={setCompactStrategy}
                    currentStrategy={compactStrategy}
                />
            )}
        </>
    );
};
```

### Test Plan
```python
# tests/unit/memory/test_conversation_compactor.py
import pytest
from src.memory.conversation_compactor import ConversationCompactor

class TestConversationCompactor:
    @pytest.mark.asyncio
    async def test_workflow_segmentation(self, mock_shared_context):
        """Test conversation segmentation by workflows"""
        compactor = ConversationCompactor(mock_shared_context, None)
        
        # Create test conversation with multiple workflows
        conversation_id = "test_conv_1"
        await mock_shared_context.store(
            f"workflow_history_{conversation_id}",
            [mock_workflow(i) for i in range(3)]
        )
        
        segments = await compactor._segment_by_workflows(conversation_id)
        
        assert len(segments) == 3
        assert all(s.workflow_pattern for s in segments)
    
    @pytest.mark.asyncio
    async def test_agent_aware_summarization(self):
        """Test that summarization preserves agent-specific context"""
        # Test implementation
        pass
    
    @pytest.mark.asyncio
    async def test_context_preservation_rules(self):
        """Test that critical context is preserved"""
        # Test implementation
        pass

# tests/integration/test_conversation_compacting.py
@pytest.mark.asyncio
async def test_auto_compacting_trigger(test_app, mock_orchestrator):
    """Test automatic compacting triggers"""
    # Create conversation approaching token limit
    conversation_id = "test_conv"
    
    # Simulate conversation growth
    for i in range(10):
        response = await test_app.post(
            f"/api/workflow/execute",
            json={"prompt": f"Task {i}", "conversation_id": conversation_id}
        )
    
    # Check that compacting was triggered
    compacting_events = mock_orchestrator.get_compacting_events()
    assert len(compacting_events) > 0
```

### Deliverables
- [ ] ConversationCompactor implementation with workflow segmentation
- [ ] Context preservation strategy with importance scoring
- [ ] API endpoints for compacting operations
- [ ] WebSocket monitoring for real-time warnings
- [ ] GUI components for token usage and compacting controls
- [ ] Comprehensive test suite
- [ ] Documentation in CONVERSATION_COMPACTING_DESIGN.md

**Verification:**
- Token usage is accurately tracked and displayed
- Compacting preserves critical context while reducing size
- Multiple compacting strategies work correctly
- GUI provides clear warnings and controls
- System maintains conversation continuity after compacting

---

## Phase 6: Advanced Workflow Patterns (Week 6)

### Objectives
- Implement Conditional workflows
- Add Iterative workflows  
- Create Hierarchical workflows
- Integrate tool use into workflow patterns

### Implementation Steps

#### 5.1 Conditional Workflow
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

#### 5.2 Iterative Workflow
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

#### 5.3 Hierarchical Workflow
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

## Phase 7: Vector Memory Implementation (Week 7)

### Objectives
- Add vector database for similarity search
- Implement embedding generation
- Enable semantic memory retrieval
- Integrate tool execution results into vector memory for semantic search

### Implementation Steps

#### 6.1 Add Vector Store
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

#### 6.2 Integrate with Persistent Knowledge Base
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

## Phase 8: Learning System Implementation (Week 8)

### Objectives
- Implement user feedback processing
- Add pattern recognition
- Create adaptive behavior system

### Implementation Steps

#### 7.1 User Feedback Processor
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

#### 7.2 Pattern Recognition System
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

## Phase 9: Frontend Collaboration UI (Week 9)

### Objectives
- Add agent status visualization
- Implement memory sharing display
- Create learning progress indicators

### Implementation Steps

#### 8.1 Agent Status Component
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

#### 8.2 Memory Sharing Visualizer
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

#### 8.3 Learning Progress Tracker
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

## Phase 10: Integration Testing (Week 10)

### Objectives
- Test complete agent collaboration flow
- Verify memory persistence
- Validate learning improvements

### Implementation Steps

#### 9.1 End-to-End Collaboration Test
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

#### 9.2 Memory Persistence Test
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

## Phase 11: Advanced Learning Features (Week 11)

### Objectives
- Implement reinforcement learning
- Add meta-learning capabilities
- Create predictive adaptations

### Implementation Steps

#### 10.1 Reinforcement Learning System
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

#### 10.2 Meta-Learning System
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

## Phase 12: Production Readiness (Week 12)

### Objectives
- Add monitoring and observability
- Implement safety mechanisms
- Create deployment pipeline

### Implementation Steps

#### 11.1 Monitoring System
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

#### 11.2 Safety Mechanisms
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

#### 11.3 Deployment Configuration
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

## Phase 13: Performance Optimization (Week 13)

### Objectives
- Optimize memory retrieval speed
- Implement caching strategies
- Add batch processing

### Implementation Steps

#### 12.1 Memory Caching Layer
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

#### 12.2 Batch Processing System
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

## Phase 14: Documentation and Finalization (Week 14)

### Objectives
- Complete API documentation
- Create user guides
- Final integration testing

### Implementation Steps

#### 13.1 API Documentation
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

#### 13.2 User Guide Creation
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

1. **Foundation** (Weeks 1-3): Test infrastructure, memory system, and communication
2. **Tool Integration** (Week 4): Tool use foundation with registry, execution engine, and agent integration
3. **Advanced Features** (Weeks 5-7): Advanced workflows, vector memory, learning
4. **UI Integration** (Week 8): Frontend collaboration features
5. **Testing & Optimization** (Weeks 9-12): Integration, performance, safety
6. **Finalization** (Week 13): Documentation and deployment

Each phase builds on the previous one with clear deliverables and comprehensive testing. The modular approach allows for iterative development and continuous validation of functionality. Tool use is strategically introduced in Phase 4 to build on the memory and communication foundations while enabling more sophisticated workflow patterns in subsequent phases.