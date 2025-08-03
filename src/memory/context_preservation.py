#!/usr/bin/env python3
"""
Context Preservation Strategy - Phase 5

Intelligent context preservation for conversation compacting that maintains
critical information while reducing overall memory footprint.
"""

import re
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from enum import Enum
import logging

from src.memory.conversation_compactor import ConversationSegment, ContentImportance


logger = logging.getLogger(__name__)


class PreservationCategory(Enum):
    """Categories for preserved content organization."""
    OBJECTIVES = "objectives"          # User goals and requirements
    DECISIONS = "decisions"            # Critical decisions made
    ARTIFACTS = "artifacts"            # Important outputs and results
    DISCOVERIES = "discoveries"        # Agent findings and insights
    ERRORS = "errors"                  # Error patterns and resolutions
    ACTIVE_CONTEXT = "active_context"  # Current working context
    TOOLS = "tools"                    # Tool execution results
    PATTERNS = "patterns"              # Workflow and behavioral patterns


@dataclass
class ContentItem:
    """Represents a piece of content for preservation analysis."""
    content_id: str
    content: Union[str, Dict[str, Any]]
    category: PreservationCategory
    importance_score: float
    timestamp: datetime
    source_agent: Optional[str] = None
    workflow_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PreservationReport:
    """Report of preservation analysis and actions."""
    total_items_analyzed: int
    items_preserved: int
    items_summarized: int
    items_discarded: int
    preservation_ratio: float
    categories_preserved: Dict[PreservationCategory, int]
    timestamp: datetime


class ContextPreservationStrategy:
    """
    Intelligent context preservation strategy for conversation compacting.
    
    Analyzes conversation content and determines what should be preserved,
    summarized, or discarded based on importance scores and preservation rules.
    """
    
    def __init__(self):
        """Initialize preservation strategy with default rules."""
        self.preservation_rules = self._initialize_preservation_rules()
        self.category_priorities = self._initialize_category_priorities()
        self.content_patterns = self._initialize_content_patterns()
        
        logger.info("ContextPreservationStrategy initialized")
    
    def _initialize_preservation_rules(self) -> Dict[str, float]:
        """Initialize content preservation rules with importance thresholds."""
        return {
            # Content type -> minimum importance score for preservation
            "user_objectives": ContentImportance.CRITICAL.value,
            "final_results": ContentImportance.CRITICAL.value,
            "critical_decisions": ContentImportance.HIGH.value,
            "error_resolutions": ContentImportance.HIGH.value,
            "workflow_outputs": ContentImportance.HIGH.value,
            "agent_discoveries": ContentImportance.MEDIUM.value,
            "tool_results": ContentImportance.MEDIUM.value,
            "collaboration_insights": ContentImportance.MEDIUM.value,
            "intermediate_steps": ContentImportance.LOW.value,
            "status_updates": ContentImportance.MINIMAL.value,
            "debug_information": ContentImportance.MINIMAL.value
        }
    
    def _initialize_category_priorities(self) -> Dict[PreservationCategory, float]:
        """Initialize category-based preservation priorities."""
        return {
            PreservationCategory.OBJECTIVES: 1.0,      # Always preserve
            PreservationCategory.DECISIONS: 0.9,       # High priority
            PreservationCategory.ARTIFACTS: 0.8,       # Important outputs
            PreservationCategory.DISCOVERIES: 0.7,     # Valuable insights
            PreservationCategory.ERRORS: 0.6,          # Learning opportunities
            PreservationCategory.TOOLS: 0.5,           # Execution results
            PreservationCategory.PATTERNS: 0.4,        # Behavioral data
            PreservationCategory.ACTIVE_CONTEXT: 0.3   # Current state
        }
    
    def _initialize_content_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize regex patterns for content classification."""
        return {
            "objectives": {
                "patterns": [
                    r"user wants?.*to",
                    r"goal is to",
                    r"objective.*:",
                    r"requirement.*:",
                    r"need to accomplish",
                    r"trying to achieve"
                ],
                "category": PreservationCategory.OBJECTIVES,
                "base_importance": ContentImportance.CRITICAL.value
            },
            "decisions": {
                "patterns": [
                    r"decided to",
                    r"chosen approach",
                    r"selected.*strategy",
                    r"opted for",
                    r"final decision",
                    r"concluded that"
                ],
                "category": PreservationCategory.DECISIONS,
                "base_importance": ContentImportance.HIGH.value
            },
            "artifacts": {
                "patterns": [
                    r"final result",
                    r"output:",
                    r"generated.*:",
                    r"created.*file",
                    r"produced.*:",
                    r"delivered.*:"
                ],
                "category": PreservationCategory.ARTIFACTS,
                "base_importance": ContentImportance.HIGH.value
            },
            "discoveries": {
                "patterns": [
                    r"discovered that",
                    r"found out",
                    r"insight:",
                    r"learned that",
                    r"observed that",
                    r"key finding"
                ],
                "category": PreservationCategory.DISCOVERIES,
                "base_importance": ContentImportance.MEDIUM.value
            },
            "errors": {
                "patterns": [
                    r"error.*resolved",
                    r"fixed.*issue",
                    r"problem.*solved",
                    r"workaround.*:",
                    r"correction.*:",
                    r"debug.*success"
                ],
                "category": PreservationCategory.ERRORS,
                "base_importance": ContentImportance.MEDIUM.value
            },
            "tools": {
                "patterns": [
                    r"tool.*result",
                    r"executed.*tool",
                    r"calculation.*result",
                    r"search.*results",
                    r"file.*operation",
                    r"api.*response"
                ],
                "category": PreservationCategory.TOOLS,
                "base_importance": ContentImportance.MEDIUM.value
            }
        }
    
    async def preserve_critical_context(self, segments: List[ConversationSegment]) -> Dict[str, Any]:
        """
        Main preservation method that analyzes segments and preserves critical context.
        
        Args:
            segments: List of conversation segments to analyze
            
        Returns:
            Dictionary with preserved content organized by category
        """
        logger.info(f"Starting context preservation for {len(segments)} segments")
        
        # Initialize preservation containers
        preserved = {
            PreservationCategory.OBJECTIVES: [],
            PreservationCategory.DECISIONS: [],
            PreservationCategory.ARTIFACTS: [],
            PreservationCategory.DISCOVERIES: [],
            PreservationCategory.ERRORS: [],
            PreservationCategory.ACTIVE_CONTEXT: [],
            PreservationCategory.TOOLS: [],
            PreservationCategory.PATTERNS: []
        }
        
        total_items = 0
        preserved_items = 0
        summarized_items = 0
        discarded_items = 0
        
        # Process each segment
        for segment in segments:
            segment_items = await self._extract_content_items(segment)
            total_items += len(segment_items)
            
            for item in segment_items:
                # Calculate preservation score
                preservation_score = self._calculate_preservation_score(item)
                
                if preservation_score >= 0.7:  # High preservation threshold
                    preserved[item.category].append(item)
                    preserved_items += 1
                elif preservation_score >= 0.3:  # Medium threshold - summarize
                    summary_item = await self._summarize_content_item(item)
                    preserved[item.category].append(summary_item)
                    summarized_items += 1
                else:  # Low threshold - discard
                    discarded_items += 1
        
        # Add active context from most recent segment
        if segments:
            active_context = await self._extract_active_context(segments[-1])
            preserved[PreservationCategory.ACTIVE_CONTEXT] = active_context
        
        # Create preservation report
        report = PreservationReport(
            total_items_analyzed=total_items,
            items_preserved=preserved_items,
            items_summarized=summarized_items,
            items_discarded=discarded_items,
            preservation_ratio=preserved_items / max(total_items, 1),
            categories_preserved={cat: len(items) for cat, items in preserved.items()},
            timestamp=datetime.now()
        )
        
        logger.info(f"Preservation complete: {preserved_items}/{total_items} items preserved")
        
        return {
            "preserved_content": preserved,
            "preservation_report": report,
            "summary": self._create_preservation_summary(preserved, report)
        }
    
    async def _extract_content_items(self, segment: ConversationSegment) -> List[ContentItem]:
        """Extract content items from a conversation segment."""
        items = []
        
        # Process agent interactions
        for i, interaction in enumerate(segment.agent_interactions):
            content_str = str(interaction)
            
            # Classify content using patterns
            category, base_importance = self._classify_content(content_str)
            
            # Adjust importance based on segment context
            importance = self._adjust_importance_for_context(
                base_importance, segment, interaction
            )
            
            item = ContentItem(
                content_id=f"{segment.segment_id}_item_{i}",
                content=interaction,
                category=category,
                importance_score=importance,
                timestamp=segment.timestamp,
                source_agent=interaction.get("agent_id") if isinstance(interaction, dict) else None,
                workflow_id=segment.metadata.get("workflow_id"),
                metadata={
                    "segment_id": segment.segment_id,
                    "workflow_pattern": segment.workflow_pattern.value,
                    "original_importance": base_importance
                }
            )
            
            items.append(item)
        
        return items
    
    def _classify_content(self, content: str) -> Tuple[PreservationCategory, float]:
        """Classify content and assign base importance score."""
        content_lower = content.lower()
        
        # Check against known patterns
        for pattern_type, pattern_data in self.content_patterns.items():
            for pattern in pattern_data["patterns"]:
                if re.search(pattern, content_lower):
                    return pattern_data["category"], pattern_data["base_importance"]
        
        # Default classification for unmatched content
        if len(content) > 200:  # Longer content might be more important
            return PreservationCategory.ACTIVE_CONTEXT, ContentImportance.MEDIUM.value
        else:
            return PreservationCategory.ACTIVE_CONTEXT, ContentImportance.LOW.value
    
    def _adjust_importance_for_context(self, 
                                     base_importance: float,
                                     segment: ConversationSegment,
                                     interaction: Dict[str, Any]) -> float:
        """Adjust importance score based on segment and interaction context."""
        adjusted_importance = base_importance
        
        # Boost importance for successful workflows
        if segment.metadata.get("success", False):
            adjusted_importance += 0.1
        
        # Boost importance for complex workflow patterns
        if segment.workflow_pattern.value in ["PARALLEL", "HIERARCHICAL", "CONDITIONAL"]:
            adjusted_importance += 0.1
        
        # Boost importance for recent interactions
        if segment.timestamp > datetime.now() - timedelta(hours=1):
            adjusted_importance += 0.05
        
        # Boost importance for tool-related interactions
        if isinstance(interaction, dict) and "tool_execution" in str(interaction):
            adjusted_importance += 0.1
        
        # Boost importance for error-related interactions
        if "error" in str(interaction).lower() or "failed" in str(interaction).lower():
            adjusted_importance += 0.1
        
        return min(adjusted_importance, 1.0)  # Cap at 1.0
    
    def _calculate_preservation_score(self, item: ContentItem) -> float:
        """Calculate final preservation score for a content item."""
        # Start with item's importance score
        score = item.importance_score
        
        # Apply category priority
        category_priority = self.category_priorities.get(item.category, 0.5)
        score *= category_priority
        
        # Apply recency boost
        age_hours = (datetime.now() - item.timestamp).total_seconds() / 3600
        if age_hours < 1:  # Last hour
            score *= 1.2
        elif age_hours < 6:  # Last 6 hours
            score *= 1.1
        elif age_hours > 24:  # Older than 24 hours
            score *= 0.9
        
        # Apply source agent boost (some agents might be more important)
        if item.source_agent:
            # TODO: Could implement agent-specific importance multipliers
            pass
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _summarize_content_item(self, item: ContentItem) -> ContentItem:
        """Create a summarized version of a content item."""
        try:
            original_content = item.content
            
            if isinstance(original_content, dict):
                # Summarize dictionary content
                summary = {
                    "type": original_content.get("type", "interaction"),
                    "agent": original_content.get("agent_id", "unknown"),
                    "timestamp": original_content.get("timestamp", item.timestamp.isoformat()),
                    "summary": f"Agent interaction in {item.metadata.get('workflow_pattern', 'unknown')} workflow"
                }
            else:
                # Summarize string content
                content_str = str(original_content)
                if len(content_str) > 100:
                    summary = content_str[:100] + "... [summarized]"
                else:
                    summary = content_str
            
            # Create summarized item
            summarized_item = ContentItem(
                content_id=f"{item.content_id}_summary",
                content=summary,
                category=item.category,
                importance_score=item.importance_score * 0.8,  # Reduce importance for summaries
                timestamp=item.timestamp,
                source_agent=item.source_agent,
                workflow_id=item.workflow_id,
                metadata={**item.metadata, "summarized": True}
            )
            
            return summarized_item
            
        except Exception as e:
            logger.error(f"Failed to summarize content item: {e}")
            return item  # Return original item if summarization fails
    
    async def _extract_active_context(self, latest_segment: ConversationSegment) -> List[Dict[str, Any]]:
        """Extract active context from the most recent segment."""
        active_context = []
        
        try:
            # Get the last few interactions as active context
            recent_interactions = latest_segment.agent_interactions[-3:]  # Last 3 interactions
            
            for interaction in recent_interactions:
                context_item = {
                    "content": interaction,
                    "timestamp": latest_segment.timestamp.isoformat(),
                    "workflow_pattern": latest_segment.workflow_pattern.value,
                    "active": True
                }
                active_context.append(context_item)
            
            return active_context
            
        except Exception as e:
            logger.error(f"Failed to extract active context: {e}")
            return []
    
    def _create_preservation_summary(self, 
                                   preserved: Dict[PreservationCategory, List],
                                   report: PreservationReport) -> str:
        """Create a human-readable summary of preservation actions."""
        total_preserved = sum(len(items) for items in preserved.values())
        
        summary_parts = [
            f"Preserved {total_preserved} critical items from {report.total_items_analyzed} analyzed",
            f"Preservation ratio: {report.preservation_ratio:.1%}"
        ]
        
        # Add category breakdown
        category_summary = []
        for category, items in preserved.items():
            if items:
                category_summary.append(f"{len(items)} {category.value}")
        
        if category_summary:
            summary_parts.append(f"Categories: {', '.join(category_summary)}")
        
        # Add efficiency note
        if report.items_summarized > 0:
            summary_parts.append(f"Summarized {report.items_summarized} additional items")
        
        return ". ".join(summary_parts) + "."
    
    def update_preservation_rules(self, new_rules: Dict[str, float]):
        """Update preservation rules (for customization)."""
        self.preservation_rules.update(new_rules)
        logger.info(f"Updated preservation rules: {new_rules}")
    
    def get_preservation_statistics(self) -> Dict[str, Any]:
        """Get current preservation strategy statistics."""
        return {
            "rules_count": len(self.preservation_rules),
            "category_priorities": self.category_priorities,
            "pattern_types": list(self.content_patterns.keys()),
            "preservation_thresholds": {
                "preserve": 0.7,
                "summarize": 0.3,
                "discard": 0.0
            }
        }