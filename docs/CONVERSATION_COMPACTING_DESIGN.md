# Conversation Compacting Design for Shepherd

## Overview

This document outlines the design and implementation strategy for conversation compacting in the Shepherd intelligent workflow orchestrator. The approach leverages Shepherd's existing three-tier memory architecture and multi-agent system to provide efficient, context-aware conversation management.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Core Components](#core-components)
- [Compacting Strategies](#compacting-strategies)
- [Implementation Details](#implementation-details)
- [API Integration](#api-integration)
- [GUI Components](#gui-components)
- [Automatic Triggers](#automatic-triggers)
- [Benefits and Advantages](#benefits-and-advantages)
- [Implementation Phases](#implementation-phases)

## Architecture Overview

The conversation compacting system integrates seamlessly with Shepherd's existing architecture:

```
┌─────────────────────────────────────────────────────┐
│                GUI Layer (React/TypeScript)          │
│  - Token usage indicators                            │
│  - Compacting controls                               │
│  - Strategy selection                                │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              API Layer (FastAPI)                     │
│  - Compacting endpoints                              │
│  - WebSocket monitoring                              │
│  - Real-time notifications                           │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│         Conversation Compactor Engine                │
│  - Workflow segmentation                             │
│  - Agent-aware summarization                         │
│  - Context preservation                              │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│          Three-Tier Memory System                    │
│  - Local Agent Memory                                │
│  - Shared Context Pool                               │
│  - Persistent Knowledge Base                         │
└─────────────────────────────────────────────────────┘
```

## Core Components

### 1. ConversationSegment Data Model

```python
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
```

### 2. ConversationCompactor Class

The main orchestration class that manages the compacting process:

```python
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

### 3. Context Preservation Strategy

```python
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
```

## Compacting Strategies

### 1. Automatic Compacting
- Triggered when token count exceeds 80% of threshold
- Uses intelligent summarization to reduce context size
- Preserves critical information based on importance scores

### 2. Milestone-Based Compacting
- Occurs at natural workflow boundaries
- Segments conversation by completed workflows
- Creates hierarchical summaries of each workflow

### 3. Selective Compacting
- User-guided preservation of specific content
- Interactive selection of what to keep/summarize
- Fine-grained control over context management

## Implementation Details

### Workflow-Based Segmentation

```python
async def _segment_by_workflows(self, conversation_id: str) -> List[ConversationSegment]:
    """Segment conversation by completed workflows"""
    segments = []
    
    # Get workflow execution history
    history = await self.shared_context.retrieve(f"workflow_history_{conversation_id}")
    
    for workflow in history:
        segment = ConversationSegment(
            segment_id=f"{conversation_id}_{workflow.workflow_id}",
            timestamp=workflow.start_time,
            agent_interactions=workflow.agent_interactions,
            workflow_pattern=workflow.pattern.value,
            importance_score=self._calculate_importance(workflow),
            token_count=self._count_tokens(workflow)
        )
        segments.append(segment)
    
    return segments
```

### Agent-Aware Summarization

```python
async def _agent_aware_summarization(self, segment: ConversationSegment) -> str:
    """Create summaries that preserve agent-specific context"""
    summaries = {}
    
    # Group interactions by agent
    agent_groups = self._group_by_agent(segment.agent_interactions)
    
    for agent_id, interactions in agent_groups.items():
        # Preserve agent-specific discoveries and decisions
        agent_summary = {
            "agent": agent_id,
            "key_actions": self._extract_key_actions(interactions),
            "discoveries": self._extract_discoveries(interactions),
            "decisions": self._extract_decisions(interactions),
            "artifacts": self._extract_artifacts(interactions)
        }
        summaries[agent_id] = agent_summary
    
    # Combine into cohesive summary
    return self._combine_agent_summaries(summaries)
```

### Hierarchical Compression

The system applies different compression levels based on content importance:

1. **Level 1 - Full Preservation**: User objectives, critical decisions
2. **Level 2 - Detailed Summary**: Workflow outputs, agent discoveries
3. **Level 3 - Brief Summary**: Intermediate steps, context transitions
4. **Level 4 - Metadata Only**: Debug logs, repetitive confirmations

## API Integration

### RESTful Endpoints

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
```

### WebSocket Monitoring

```python
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
            
            # Offer compacting options
            await websocket.send_json({
                "type": "compact_suggestion",
                "options": ["auto", "milestone", "selective"]
            })
```

## GUI Components

### Token Usage Indicator

```typescript
// shepherd-gui/src/components/features/conversation/TokenUsageIndicator.tsx
export const TokenUsageIndicator: React.FC = () => {
    const { tokenCount, threshold } = useConversationStore();
    const percentage = (tokenCount / threshold) * 100;
    const isWarning = percentage > 80;
    
    return (
        <div className="token-usage-container">
            <div className="token-usage-bar">
                <div 
                    className={`usage-fill ${isWarning ? 'warning' : ''}`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
            <span className="token-count">
                {tokenCount.toLocaleString()} / {threshold.toLocaleString()} tokens
            </span>
        </div>
    );
};
```

### Conversation Compactor Component

```typescript
// shepherd-gui/src/components/features/conversation/ConversationCompactor.tsx
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
            <TokenUsageIndicator />
            
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

## Automatic Triggers

### Enhanced Orchestrator

```python
class AutoCompactingOrchestrator(Orchestrator):
    """Enhanced orchestrator with automatic conversation compacting"""
    
    async def execute_workflow(self, prompt: str, conversation_id: str):
        # Check if compacting needed before execution
        if await self._should_compact(conversation_id):
            await self._auto_compact(conversation_id)
        
        # Normal workflow execution
        result = await super().execute_workflow(prompt, conversation_id)
        
        # Post-workflow compacting check
        if result.pattern == WorkflowPattern.HIERARCHICAL:
            # Complex workflows benefit from milestone compacting
            await self._milestone_compact(conversation_id)
        
        return result
    
    async def _should_compact(self, conversation_id: str) -> bool:
        """Determine if conversation needs compacting"""
        metrics = await self._get_conversation_metrics(conversation_id)
        
        return any([
            metrics.token_count > self.token_threshold * 0.8,
            metrics.workflow_count > 5,
            metrics.elapsed_time > 3600,  # 1 hour
            metrics.performance_degradation > 0.2
        ])
```

### Compacting Triggers

1. **Token Threshold**: When conversation exceeds 80% of token limit
2. **Workflow Count**: After 5+ completed workflows
3. **Time-Based**: After 1 hour of continuous conversation
4. **Performance**: When response latency increases by 20%
5. **User-Initiated**: Manual trigger via GUI controls

## Benefits and Advantages

### 1. Leverages Existing Architecture
- Uses Shepherd's three-tier memory system
- Integrates with agent communication infrastructure
- Builds on workflow-based execution model

### 2. Agent-Aware Design
- Preserves agent-specific context and discoveries
- Maintains collaboration history
- Retains critical agent decisions

### 3. Workflow-Centric Approach
- Natural segmentation boundaries
- Preserves workflow outputs and artifacts
- Maintains execution history

### 4. Flexible Strategies
- Multiple compacting approaches
- User control when needed
- Automatic optimization

### 5. Real-time Monitoring
- WebSocket-based notifications
- Proactive warnings
- Visual indicators in GUI

### 6. Minimal User Disruption
- Seamless background operation
- Preserves conversation flow
- Maintains task continuity

## Implementation Phases

### Phase 1: Core Engine (2 weeks)
- [ ] Implement ConversationSegment data model
- [ ] Create ConversationCompactor class
- [ ] Develop workflow segmentation logic
- [ ] Build agent-aware summarization
- [ ] Implement context preservation strategy

### Phase 2: API Integration (1 week)
- [ ] Create RESTful endpoints
- [ ] Implement WebSocket monitoring
- [ ] Add conversation metrics tracking
- [ ] Build compacting response handlers

### Phase 3: GUI Components (1 week)
- [ ] Create TokenUsageIndicator component
- [ ] Build ConversationCompactor component
- [ ] Design CompactDialog interface
- [ ] Implement visual warnings and alerts

### Phase 4: Automatic Triggers (1 week)
- [ ] Enhance Orchestrator with auto-compacting
- [ ] Implement trigger conditions
- [ ] Add performance monitoring
- [ ] Create background compacting service

### Phase 5: Advanced Features (2 weeks)
- [ ] Selective preservation UI
- [ ] Learning-based importance scoring
- [ ] Multi-conversation management
- [ ] Export/import compacted conversations

## Testing Strategy

### Unit Tests
- Test each compacting strategy independently
- Verify context preservation rules
- Validate token counting accuracy

### Integration Tests
- Test API endpoints with mock data
- Verify WebSocket notifications
- Test GUI component interactions

### Performance Tests
- Measure compacting speed
- Monitor memory usage
- Track reduction effectiveness

### User Acceptance Tests
- Verify conversation continuity
- Test user controls
- Validate visual indicators

## Future Enhancements

1. **Machine Learning Integration**
   - Learn user preferences for preservation
   - Adaptive importance scoring
   - Predictive compacting triggers

2. **Advanced Summarization**
   - Multi-level hierarchical summaries
   - Cross-workflow pattern recognition
   - Semantic compression techniques

3. **Collaboration Features**
   - Team-based conversation management
   - Shared compacting preferences
   - Collaborative preservation decisions

4. **Analytics Dashboard**
   - Token usage trends
   - Compacting effectiveness metrics
   - Conversation efficiency scores

This design provides a comprehensive, scalable solution for conversation compacting that integrates seamlessly with Shepherd's architecture while maintaining the system's core capabilities and user experience.