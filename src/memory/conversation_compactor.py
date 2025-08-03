#!/usr/bin/env python3
"""
Conversation Compacting System - Phase 5

Manages context window limitations through intelligent conversation compacting
and workflow segmentation while preserving critical context.
"""

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum
import logging

from src.memory.base import BaseMemory
from src.memory.local_memory import AgentLocalMemory
from src.memory.shared_context import SharedContextPool
from src.core.models import WorkflowPattern


logger = logging.getLogger(__name__)


class CompactingStrategy(Enum):
    """Available compacting strategies."""
    AUTO = "auto"              # Automatic based on token count
    MILESTONE = "milestone"    # Compact at workflow milestones
    SELECTIVE = "selective"    # User-guided selective preservation
    AGGRESSIVE = "aggressive"  # Maximum compression
    CONSERVATIVE = "conservative"  # Minimal compression


class ContentImportance(Enum):
    """Content importance levels for preservation."""
    CRITICAL = 1.0      # Must always preserve
    HIGH = 0.9          # High priority preservation
    MEDIUM = 0.7        # Medium priority
    LOW = 0.3           # Low priority
    MINIMAL = 0.1       # Rarely preserve


@dataclass
class ConversationSegment:
    """Represents a segment of conversation for compacting analysis."""
    segment_id: str
    timestamp: datetime
    agent_interactions: List[Dict[str, Any]]
    workflow_pattern: WorkflowPattern
    importance_score: float
    token_count: int
    summary: Optional[str] = None
    preserved_artifacts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompactingResult:
    """Result of conversation compacting operation."""
    conversation_id: str
    strategy_used: CompactingStrategy
    original_token_count: int
    compacted_token_count: int
    reduction_percentage: float
    segments_processed: int
    preserved_artifacts: List[str]
    compacting_summary: str
    timestamp: datetime
    success: bool
    error: Optional[str] = None


class ConversationCompactor:
    """
    Main conversation compacting engine.
    
    Provides intelligent conversation compacting with multiple strategies,
    context preservation, and workflow-aware segmentation.
    """
    
    def __init__(self, 
                 shared_context: SharedContextPool,
                 local_memory: AgentLocalMemory,
                 token_threshold: int = 50000,
                 compression_ratio: float = 0.3):
        """
        Initialize conversation compactor.
        
        Args:
            shared_context: Shared context pool for collaboration
            local_memory: Local memory for temporary storage
            token_threshold: Token count threshold for auto-compacting
            compression_ratio: Target compression ratio (0.3 = 70% reduction)
        """
        self.shared_context = shared_context
        self.local_memory = local_memory
        self.token_threshold = token_threshold
        self.compression_ratio = compression_ratio
        
        # Compacting statistics
        self.compacting_history: List[CompactingResult] = []
        self.preservation_rules = self._initialize_preservation_rules()
        
        logger.info(f"ConversationCompactor initialized with threshold={token_threshold}, ratio={compression_ratio}")
    
    def _initialize_preservation_rules(self) -> Dict[str, float]:
        """Initialize content preservation rules with importance scores."""
        return {
            "user_objectives": ContentImportance.CRITICAL.value,
            "critical_decisions": ContentImportance.HIGH.value,
            "workflow_outputs": ContentImportance.HIGH.value,
            "agent_discoveries": ContentImportance.MEDIUM.value,
            "tool_results": ContentImportance.MEDIUM.value,
            "error_messages": ContentImportance.MEDIUM.value,
            "intermediate_steps": ContentImportance.LOW.value,
            "debug_logs": ContentImportance.MINIMAL.value,
            "status_updates": ContentImportance.MINIMAL.value
        }
    
    async def compact_conversation(self, 
                                 conversation_id: str,
                                 strategy: CompactingStrategy = CompactingStrategy.AUTO) -> CompactingResult:
        """
        Main compacting orchestration method.
        
        Args:
            conversation_id: ID of conversation to compact
            strategy: Compacting strategy to use
            
        Returns:
            CompactingResult with compacting details and statistics
        """
        start_time = datetime.now()
        logger.info(f"Starting conversation compacting for {conversation_id} with strategy {strategy}")
        
        try:
            # 1. Analyze current conversation state
            analysis = await self._analyze_conversation_state(conversation_id)
            if not analysis["needs_compacting"]:
                result = CompactingResult(
                    conversation_id=conversation_id,
                    strategy_used=strategy,
                    original_token_count=analysis["token_count"],
                    compacted_token_count=analysis["token_count"],
                    reduction_percentage=0.0,
                    segments_processed=0,
                    preserved_artifacts=[],
                    compacting_summary="No compacting needed",
                    timestamp=start_time,
                    success=True
                )
                # Store result in history even when no compacting is needed
                self.compacting_history.append(result)
                return result
            
            # 2. Segment conversation by workflows
            segments = await self._segment_by_workflows(conversation_id)
            logger.info(f"Segmented conversation into {len(segments)} workflow segments")
            
            # 3. Apply strategy-specific compression
            if strategy == CompactingStrategy.AUTO:
                compacted = await self._auto_compacting(segments)
            elif strategy == CompactingStrategy.MILESTONE:
                compacted = await self._milestone_compacting(segments)
            elif strategy == CompactingStrategy.SELECTIVE:
                compacted = await self._selective_compacting(segments)
            elif strategy == CompactingStrategy.AGGRESSIVE:
                compacted = await self._aggressive_compacting(segments)
            elif strategy == CompactingStrategy.CONSERVATIVE:
                compacted = await self._conservative_compacting(segments)
            else:
                raise ValueError(f"Unknown compacting strategy: {strategy}")
            
            # 4. Preserve critical context
            preserved = await self._preserve_critical_context(compacted)
            
            # 5. Update conversation state
            await self._update_conversation_state(conversation_id, preserved)
            
            # 6. Create result
            result = CompactingResult(
                conversation_id=conversation_id,
                strategy_used=strategy,
                original_token_count=analysis["token_count"],
                compacted_token_count=preserved["token_count"],
                reduction_percentage=((analysis["token_count"] - preserved["token_count"]) / analysis["token_count"]) * 100,
                segments_processed=len(segments),
                preserved_artifacts=preserved["artifacts"],
                compacting_summary=preserved["summary"],
                timestamp=start_time,
                success=True
            )
            
            # Store result in history
            self.compacting_history.append(result)
            
            logger.info(f"Compacting completed: {result.reduction_percentage:.1f}% reduction")
            return result
            
        except Exception as e:
            logger.error(f"Compacting failed for {conversation_id}: {e}")
            return CompactingResult(
                conversation_id=conversation_id,
                strategy_used=strategy,
                original_token_count=0,
                compacted_token_count=0,
                reduction_percentage=0.0,
                segments_processed=0,
                preserved_artifacts=[],
                compacting_summary="Compacting failed",
                timestamp=start_time,
                success=False,
                error=str(e)
            )
    
    async def _analyze_conversation_state(self, conversation_id: str) -> Dict[str, Any]:
        """Analyze current conversation state to determine if compacting is needed."""
        try:
            # Get conversation context
            context_key = f"conversation_{conversation_id}"
            conversation_data = await self.shared_context.retrieve(context_key)
            
            if not conversation_data:
                return {
                    "needs_compacting": False,
                    "token_count": 0,
                    "workflow_count": 0,
                    "analysis": "No conversation data found"
                }
            
            # Estimate token count (rough approximation: 1 token ≈ 4 characters)
            content_str = str(conversation_data)
            estimated_tokens = len(content_str) // 4
            
            # Count workflows
            workflow_count = len(conversation_data.get("workflow_history", []))
            
            # Determine if compacting is needed
            needs_compacting = (
                estimated_tokens > self.token_threshold * 0.8 or  # Approaching threshold
                workflow_count > 10  # Many workflows accumulated
            )
            
            return {
                "needs_compacting": needs_compacting,
                "token_count": estimated_tokens,
                "workflow_count": workflow_count,
                "analysis": f"Estimated {estimated_tokens} tokens, {workflow_count} workflows"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze conversation state: {e}")
            return {
                "needs_compacting": False,
                "token_count": 0,
                "workflow_count": 0,
                "analysis": f"Analysis failed: {e}"
            }
    
    async def _segment_by_workflows(self, conversation_id: str) -> List[ConversationSegment]:
        """Segment conversation by workflow boundaries."""
        segments = []
        
        try:
            # Get workflow history
            workflow_key = f"workflow_history_{conversation_id}"
            workflow_history = await self.shared_context.retrieve(workflow_key) or []
            
            for i, workflow_data in enumerate(workflow_history):
                # Calculate importance score based on workflow success and complexity
                importance = self._calculate_workflow_importance(workflow_data)
                
                # Estimate token count for this workflow
                workflow_str = str(workflow_data)
                token_count = len(workflow_str) // 4
                
                segment = ConversationSegment(
                    segment_id=f"{conversation_id}_workflow_{i}",
                    timestamp=datetime.fromisoformat(workflow_data.get("timestamp", datetime.now().isoformat())),
                    agent_interactions=workflow_data.get("agent_interactions", []),
                    workflow_pattern=WorkflowPattern(workflow_data.get("pattern", "SEQUENTIAL")),
                    importance_score=importance,
                    token_count=token_count,
                    metadata={
                        "workflow_id": workflow_data.get("workflow_id"),
                        "success": workflow_data.get("success", False),
                        "duration": workflow_data.get("duration", 0)
                    }
                )
                
                segments.append(segment)
                
            logger.info(f"Created {len(segments)} workflow segments")
            return segments
            
        except Exception as e:
            logger.error(f"Failed to segment conversation: {e}")
            return []
    
    def _calculate_workflow_importance(self, workflow_data: Dict[str, Any]) -> float:
        """Calculate importance score for a workflow."""
        base_importance = 0.5
        
        # Increase importance for successful workflows
        if workflow_data.get("success", False):
            base_importance += 0.2
        
        # Increase importance for complex patterns
        pattern = workflow_data.get("pattern", "SEQUENTIAL")
        if pattern in ["PARALLEL", "CONDITIONAL", "HIERARCHICAL"]:
            base_importance += 0.1
        
        # Increase importance for longer workflows
        duration = workflow_data.get("duration", 0)
        if duration > 300:  # More than 5 minutes
            base_importance += 0.1
        
        # Increase importance for workflows with tool usage
        if "tool_executions" in workflow_data:
            base_importance += 0.1
        
        return min(base_importance, 1.0)
    
    async def _auto_compacting(self, segments: List[ConversationSegment]) -> Dict[str, Any]:
        """Apply automatic compacting strategy."""
        preserved_segments = []
        total_tokens = sum(s.token_count for s in segments)
        target_tokens = int(total_tokens * self.compression_ratio)
        current_tokens = 0
        
        # Sort segments by importance (descending)
        sorted_segments = sorted(segments, key=lambda s: s.importance_score, reverse=True)
        
        for segment in sorted_segments:
            if current_tokens + segment.token_count <= target_tokens:
                preserved_segments.append(segment)
                current_tokens += segment.token_count
            else:
                # Summarize this segment instead of preserving fully
                summary = await self._summarize_segment(segment)
                segment.summary = summary
                segment.token_count = len(summary) // 4  # Rough token estimate
                if current_tokens + segment.token_count <= target_tokens:
                    preserved_segments.append(segment)
                    current_tokens += segment.token_count
        
        return {
            "segments": preserved_segments,
            "token_count": current_tokens,
            "strategy": "auto"
        }
    
    async def _milestone_compacting(self, segments: List[ConversationSegment]) -> Dict[str, Any]:
        """Apply milestone-based compacting strategy."""
        # Keep only high-importance segments and recent segments
        cutoff_time = datetime.now() - timedelta(hours=2)  # Keep last 2 hours
        
        preserved_segments = []
        for segment in segments:
            if (segment.importance_score > 0.7 or  # High importance
                segment.timestamp > cutoff_time):  # Recent
                preserved_segments.append(segment)
            else:
                # Summarize older, less important segments
                segment.summary = await self._summarize_segment(segment)
                segment.token_count = len(segment.summary) // 4
                preserved_segments.append(segment)
        
        total_tokens = sum(s.token_count for s in preserved_segments)
        
        return {
            "segments": preserved_segments,
            "token_count": total_tokens,
            "strategy": "milestone"
        }
    
    async def _selective_compacting(self, segments: List[ConversationSegment]) -> Dict[str, Any]:
        """Apply selective compacting strategy (placeholder for user interaction)."""
        # For now, implement as conservative compacting
        return await self._conservative_compacting(segments)
    
    async def _aggressive_compacting(self, segments: List[ConversationSegment]) -> Dict[str, Any]:
        """Apply aggressive compacting strategy."""
        # Keep only the most critical segments
        preserved_segments = []
        
        for segment in segments:
            if segment.importance_score >= 0.8:  # Only critical content
                preserved_segments.append(segment)
            else:
                # Create very brief summary
                brief_summary = f"Workflow {segment.workflow_pattern.value} completed at {segment.timestamp}"
                segment.summary = brief_summary
                segment.token_count = len(brief_summary) // 4
                preserved_segments.append(segment)
        
        total_tokens = sum(s.token_count for s in preserved_segments)
        
        return {
            "segments": preserved_segments,
            "token_count": total_tokens,
            "strategy": "aggressive"
        }
    
    async def _conservative_compacting(self, segments: List[ConversationSegment]) -> Dict[str, Any]:
        """Apply conservative compacting strategy."""
        # Minimal compacting - only remove debug info and status updates
        preserved_segments = []
        
        for segment in segments:
            # Keep all segments but clean up low-value content
            cleaned_interactions = []
            for interaction in segment.agent_interactions:
                if not self._is_low_value_content(interaction):
                    cleaned_interactions.append(interaction)
            
            segment.agent_interactions = cleaned_interactions
            segment.token_count = sum(len(str(i)) for i in cleaned_interactions) // 4
            preserved_segments.append(segment)
        
        total_tokens = sum(s.token_count for s in preserved_segments)
        
        return {
            "segments": preserved_segments,
            "token_count": total_tokens,
            "strategy": "conservative"
        }
    
    def _is_low_value_content(self, interaction: Dict[str, Any]) -> bool:
        """Determine if interaction content is low-value and can be removed."""
        content = str(interaction).lower()
        
        # Low-value patterns
        low_value_patterns = [
            r'debug:', r'trace:', r'verbose:',
            r'status update', r'progress:', r'loading',
            r'connecting to', r'initializing',
            r'temporary', r'intermediate'
        ]
        
        for pattern in low_value_patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    async def _summarize_segment(self, segment: ConversationSegment) -> str:
        """Create a summary of a conversation segment."""
        try:
            # Extract key information
            timestamp = segment.timestamp.strftime("%Y-%m-%d %H:%M")
            pattern = segment.workflow_pattern.value
            success = segment.metadata.get("success", False)
            duration = segment.metadata.get("duration", 0)
            
            # Count agent interactions
            interaction_count = len(segment.agent_interactions)
            
            # Extract any tool usage
            tool_usage = []
            for interaction in segment.agent_interactions:
                if "tool_execution" in str(interaction):
                    tool_usage.append("tools")
            
            tool_info = f" with {', '.join(set(tool_usage))}" if tool_usage else ""
            
            summary = (
                f"[{timestamp}] {pattern} workflow with {interaction_count} interactions"
                f"{tool_info} - {'SUCCESS' if success else 'FAILED'} ({duration}s)"
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to summarize segment: {e}")
            return f"Workflow segment at {segment.timestamp}"
    
    async def _preserve_critical_context(self, compacted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preserve critical context items that must not be lost."""
        preserved_artifacts = []
        
        for segment in compacted_data["segments"]:
            # Extract critical artifacts
            for interaction in segment.agent_interactions:
                if self._is_critical_artifact(interaction):
                    preserved_artifacts.append(interaction)
        
        # Create overall summary
        total_segments = len(compacted_data["segments"])
        strategy = compacted_data["strategy"]
        
        summary = (
            f"Conversation compacted using {strategy} strategy. "
            f"Processed {total_segments} workflow segments. "
            f"Preserved {len(preserved_artifacts)} critical artifacts."
        )
        
        return {
            "segments": compacted_data["segments"],
            "token_count": compacted_data["token_count"],
            "artifacts": preserved_artifacts,
            "summary": summary
        }
    
    def _is_critical_artifact(self, interaction: Dict[str, Any]) -> bool:
        """Determine if an interaction contains critical artifacts."""
        content = str(interaction).lower()
        
        critical_patterns = [
            r'user objective', r'final result', r'critical decision',
            r'error resolution', r'important finding', r'key insight',
            r'tool result', r'calculation result'
        ]
        
        for pattern in critical_patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    async def _update_conversation_state(self, conversation_id: str, preserved_data: Dict[str, Any]):
        """Update conversation state with compacted data."""
        try:
            # Store compacted conversation
            compacted_key = f"conversation_{conversation_id}_compacted"
            await self.shared_context.store(compacted_key, preserved_data)
            
            # Update metadata
            metadata_key = f"conversation_{conversation_id}_metadata"
            metadata = {
                "last_compacted": datetime.now().isoformat(),
                "compacted_token_count": preserved_data["token_count"],
                "segments_count": len(preserved_data["segments"])
            }
            await self.shared_context.store(metadata_key, metadata)
            
            logger.info(f"Updated conversation state for {conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to update conversation state: {e}")
    
    async def get_token_usage(self, conversation_id: str) -> Dict[str, Any]:
        """Get current token usage for a conversation."""
        try:
            analysis = await self._analyze_conversation_state(conversation_id)
            
            return {
                "conversation_id": conversation_id,
                "current_tokens": analysis["token_count"],
                "threshold": self.token_threshold,
                "usage_percentage": (analysis["token_count"] / self.token_threshold) * 100,
                "needs_compacting": analysis["needs_compacting"],
                "workflow_count": analysis["workflow_count"]
            }
            
        except Exception as e:
            logger.error(f"Failed to get token usage: {e}")
            return {
                "conversation_id": conversation_id,
                "current_tokens": 0,
                "threshold": self.token_threshold,
                "usage_percentage": 0.0,
                "needs_compacting": False,
                "workflow_count": 0,
                "error": str(e)
            }
    
    async def get_compacting_history(self) -> List[CompactingResult]:
        """Get history of compacting operations."""
        return self.compacting_history.copy()
    
    async def should_trigger_auto_compact(self, conversation_id: str) -> bool:
        """Check if auto-compacting should be triggered."""
        usage = await self.get_token_usage(conversation_id)
        return usage["needs_compacting"]