#!/usr/bin/env python3
"""
Conversation Management API - Phase 5

FastAPI endpoints for conversation compacting, token monitoring,
and real-time conversation management.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import logging

from src.memory.conversation_compactor import ConversationCompactor, CompactingStrategy, CompactingResult
from src.memory.context_preservation import ContextPreservationStrategy
from src.memory.shared_context import SharedContextPool
from src.memory.local_memory import AgentLocalMemory


logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic models for API requests/responses
class CompactRequest(BaseModel):
    """Request model for conversation compacting."""
    conversation_id: str = Field(..., description="ID of conversation to compact")
    strategy: CompactingStrategy = Field(CompactingStrategy.AUTO, description="Compacting strategy")
    preserve_last_hours: Optional[int] = Field(2, description="Hours of recent content to preserve")
    custom_preservation_rules: Optional[Dict[str, float]] = Field(None, description="Custom preservation rules")


class TokenUsageResponse(BaseModel):
    """Response model for token usage information."""
    conversation_id: str
    current_tokens: int
    threshold: int
    usage_percentage: float
    needs_compacting: bool
    workflow_count: int
    last_updated: str
    warning_level: str  # "none", "warning", "critical"


class CompactResponse(BaseModel):
    """Response model for compacting operations."""
    success: bool
    conversation_id: str
    strategy_used: str
    original_token_count: int
    compacted_token_count: int
    reduction_percentage: float
    segments_processed: int
    preserved_artifacts_count: int
    compacting_summary: str
    timestamp: str
    error: Optional[str] = None


class ConversationStatusResponse(BaseModel):
    """Response model for conversation status."""
    conversation_id: str
    active: bool
    total_workflows: int
    last_activity: str
    token_usage: TokenUsageResponse
    compacting_history: List[Dict[str, Any]]


class WebSocketMessage(BaseModel):
    """WebSocket message model."""
    type: str
    conversation_id: str
    data: Dict[str, Any]
    timestamp: str


class ConversationManager:
    """
    Main conversation management class handling compacting, monitoring,
    and real-time updates.
    """
    
    def __init__(self):
        """Initialize conversation manager with compacting system."""
        # Initialize memory components (would be injected in production)
        self.shared_context = SharedContextPool()
        self.local_memory = AgentLocalMemory("conversation_manager")
        
        # Initialize compacting system
        self.compactor = ConversationCompactor(
            self.shared_context,
            self.local_memory,
            token_threshold=50000,
            compression_ratio=0.3
        )
        
        self.preservation_strategy = ContextPreservationStrategy()
        
        # Track active conversations and WebSocket connections
        self.active_conversations: Dict[str, Dict[str, Any]] = {}
        self.websocket_connections: Dict[str, List[WebSocket]] = {}
        
        # Background monitoring
        self.monitoring_active = False
        
        logger.info("ConversationManager initialized")
    
    async def start_monitoring(self):
        """Start background monitoring for auto-compacting."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        logger.info("Started conversation monitoring")
        
        # Background task would run monitoring loop
        # In production, this would be a proper background service
    
    async def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring_active = False
        logger.info("Stopped conversation monitoring")


# Global conversation manager instance
conversation_manager = ConversationManager()


@router.on_event("startup")
async def startup_event():
    """Initialize conversation manager on startup."""
    await conversation_manager.start_monitoring()


@router.on_event("shutdown")
async def shutdown_event():
    """Cleanup conversation manager on shutdown."""
    await conversation_manager.stop_monitoring()


@router.post("/api/conversations/{conversation_id}/compact", response_model=CompactResponse)
async def compact_conversation(
    conversation_id: str,
    request: CompactRequest,
    background_tasks: BackgroundTasks
) -> CompactResponse:
    """
    Compact a conversation using specified strategy.
    
    Args:
        conversation_id: ID of conversation to compact
        request: Compacting request parameters
        background_tasks: FastAPI background tasks
        
    Returns:
        CompactResponse with compacting results
    """
    try:
        logger.info(f"Compacting conversation {conversation_id} with strategy {request.strategy}")
        
        # Update custom preservation rules if provided
        if request.custom_preservation_rules:
            conversation_manager.preservation_strategy.update_preservation_rules(
                request.custom_preservation_rules
            )
        
        # Perform compacting
        result = await conversation_manager.compactor.compact_conversation(
            conversation_id=request.conversation_id,
            strategy=request.strategy
        )
        
        # Create response
        response = CompactResponse(
            success=result.success,
            conversation_id=result.conversation_id,
            strategy_used=result.strategy_used.value,
            original_token_count=result.original_token_count,
            compacted_token_count=result.compacted_token_count,
            reduction_percentage=result.reduction_percentage,
            segments_processed=result.segments_processed,
            preserved_artifacts_count=len(result.preserved_artifacts),
            compacting_summary=result.compacting_summary,
            timestamp=result.timestamp.isoformat(),
            error=result.error
        )
        
        # Notify WebSocket clients
        background_tasks.add_task(
            notify_websocket_clients,
            conversation_id,
            "compacting_completed",
            response.dict()
        )
        
        logger.info(f"Compacting completed for {conversation_id}: {result.reduction_percentage:.1f}% reduction")
        return response
        
    except Exception as e:
        logger.error(f"Failed to compact conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Compacting failed: {str(e)}")


@router.get("/api/conversations/{conversation_id}/token-usage", response_model=TokenUsageResponse)
async def get_token_usage(conversation_id: str) -> TokenUsageResponse:
    """
    Get current token usage for a conversation.
    
    Args:
        conversation_id: ID of conversation to check
        
    Returns:
        TokenUsageResponse with current usage information
    """
    try:
        usage = await conversation_manager.compactor.get_token_usage(conversation_id)
        
        # Determine warning level
        usage_percent = usage["usage_percentage"]
        if usage_percent >= 90:
            warning_level = "critical"
        elif usage_percent >= 75:
            warning_level = "warning"
        else:
            warning_level = "none"
        
        return TokenUsageResponse(
            conversation_id=usage["conversation_id"],
            current_tokens=usage["current_tokens"],
            threshold=usage["threshold"],
            usage_percentage=usage["usage_percentage"],
            needs_compacting=usage["needs_compacting"],
            workflow_count=usage["workflow_count"],
            last_updated=datetime.now().isoformat(),
            warning_level=warning_level
        )
        
    except Exception as e:
        logger.error(f"Failed to get token usage for {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get token usage: {str(e)}")


@router.get("/api/conversations/{conversation_id}/status", response_model=ConversationStatusResponse)
async def get_conversation_status(conversation_id: str) -> ConversationStatusResponse:
    """
    Get comprehensive status of a conversation.
    
    Args:
        conversation_id: ID of conversation to check
        
    Returns:
        ConversationStatusResponse with full status information
    """
    try:
        # Get token usage
        token_usage = await get_token_usage(conversation_id)
        
        # Get compacting history
        history = await conversation_manager.compactor.get_compacting_history()
        conversation_history = [
            {
                "timestamp": h.timestamp.isoformat(),
                "strategy": h.strategy_used.value,
                "reduction": h.reduction_percentage,
                "success": h.success
            }
            for h in history if h.conversation_id == conversation_id
        ]
        
        # Get conversation metadata
        metadata_key = f"conversation_{conversation_id}_metadata"
        metadata = await conversation_manager.shared_context.retrieve(metadata_key) or {}
        
        return ConversationStatusResponse(
            conversation_id=conversation_id,
            active=conversation_id in conversation_manager.active_conversations,
            total_workflows=metadata.get("workflow_count", 0),
            last_activity=metadata.get("last_activity", datetime.now().isoformat()),
            token_usage=token_usage,
            compacting_history=conversation_history
        )
        
    except Exception as e:
        logger.error(f"Failed to get conversation status for {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.post("/api/conversations/{conversation_id}/auto-compact-check")
async def check_auto_compact(conversation_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Check if conversation should trigger auto-compacting.
    
    Args:
        conversation_id: ID of conversation to check
        background_tasks: FastAPI background tasks
        
    Returns:
        Dictionary with auto-compact recommendation
    """
    try:
        should_compact = await conversation_manager.compactor.should_trigger_auto_compact(conversation_id)
        
        if should_compact:
            # Schedule background compacting
            background_tasks.add_task(
                auto_compact_conversation,
                conversation_id
            )
            
            return {
                "should_compact": True,
                "action": "scheduled",
                "message": "Auto-compacting scheduled in background"
            }
        else:
            return {
                "should_compact": False,
                "action": "none",
                "message": "No compacting needed"
            }
            
    except Exception as e:
        logger.error(f"Failed auto-compact check for {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Auto-compact check failed: {str(e)}")


@router.get("/api/conversations", response_model=List[str])
async def list_conversations() -> List[str]:
    """
    List all active conversations.
    
    Returns:
        List of conversation IDs
    """
    try:
        # In production, this would query a proper database
        return list(conversation_manager.active_conversations.keys())
        
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list conversations: {str(e)}")


@router.websocket("/ws/conversation/{conversation_id}")
async def conversation_websocket(websocket: WebSocket, conversation_id: str):
    """
    WebSocket endpoint for real-time conversation monitoring.
    
    Provides real-time updates on token usage, compacting events,
    and conversation status changes.
    
    Args:
        websocket: WebSocket connection
        conversation_id: ID of conversation to monitor
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for conversation {conversation_id}")
    
    # Add to connections tracking
    if conversation_id not in conversation_manager.websocket_connections:
        conversation_manager.websocket_connections[conversation_id] = []
    conversation_manager.websocket_connections[conversation_id].append(websocket)
    
    try:
        # Send initial status
        initial_status = await get_conversation_status(conversation_id)
        await websocket.send_json({
            "type": "status_update",
            "conversation_id": conversation_id,
            "data": initial_status.dict(),
            "timestamp": datetime.now().isoformat()
        })
        
        # Monitor token usage and send periodic updates
        while True:
            try:
                # Check token usage
                token_usage = await conversation_manager.compactor.get_token_usage(conversation_id)
                
                # Send warning if approaching threshold
                if token_usage["usage_percentage"] > 80:
                    warning_message = {
                        "type": "context_warning",
                        "conversation_id": conversation_id,
                        "data": {
                            "message": "Approaching context limit",
                            "token_count": token_usage["current_tokens"],
                            "threshold": token_usage["threshold"],
                            "usage_percentage": token_usage["usage_percentage"],
                            "recommendation": "Consider compacting conversation"
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_json(warning_message)
                
                # Check if auto-compacting should trigger
                if await conversation_manager.compactor.should_trigger_auto_compact(conversation_id):
                    auto_compact_message = {
                        "type": "auto_compact_suggestion",
                        "conversation_id": conversation_id,
                        "data": {
                            "message": "Auto-compacting recommended",
                            "current_tokens": token_usage["current_tokens"],
                            "suggested_strategy": "auto"
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_json(auto_compact_message)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket monitoring: {e}")
                await asyncio.sleep(30)  # Continue monitoring despite errors
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for conversation {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error for conversation {conversation_id}: {e}")
    finally:
        # Remove from connections tracking
        if conversation_id in conversation_manager.websocket_connections:
            connections = conversation_manager.websocket_connections[conversation_id]
            if websocket in connections:
                connections.remove(websocket)
            if not connections:
                del conversation_manager.websocket_connections[conversation_id]


async def notify_websocket_clients(conversation_id: str, message_type: str, data: Dict[str, Any]):
    """
    Notify all WebSocket clients for a conversation.
    
    Args:
        conversation_id: ID of conversation
        message_type: Type of message to send
        data: Message data
    """
    if conversation_id not in conversation_manager.websocket_connections:
        return
    
    message = {
        "type": message_type,
        "conversation_id": conversation_id,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    # Send to all connected clients
    connections = conversation_manager.websocket_connections[conversation_id].copy()
    for websocket in connections:
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            # Remove failed connection
            conversation_manager.websocket_connections[conversation_id].remove(websocket)


async def auto_compact_conversation(conversation_id: str):
    """
    Background task to perform auto-compacting.
    
    Args:
        conversation_id: ID of conversation to compact
    """
    try:
        logger.info(f"Starting auto-compacting for {conversation_id}")
        
        result = await conversation_manager.compactor.compact_conversation(
            conversation_id=conversation_id,
            strategy=CompactingStrategy.AUTO
        )
        
        # Notify WebSocket clients
        await notify_websocket_clients(
            conversation_id,
            "auto_compact_completed",
            {
                "success": result.success,
                "reduction_percentage": result.reduction_percentage,
                "summary": result.compacting_summary
            }
        )
        
        logger.info(f"Auto-compacting completed for {conversation_id}")
        
    except Exception as e:
        logger.error(f"Auto-compacting failed for {conversation_id}: {e}")
        
        # Notify clients of failure
        await notify_websocket_clients(
            conversation_id,
            "auto_compact_failed",
            {"error": str(e)}
        )