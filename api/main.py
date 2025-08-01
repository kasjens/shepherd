"""
FastAPI backend for Shepherd - Intelligent Workflow Orchestrator
Provides REST API and WebSocket endpoints for the TypeScript GUI
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
import logging
from datetime import datetime

# Import Shepherd core components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.orchestrator import IntelligentOrchestrator
from src.core.models import ExecutionStatus
from src.utils.logger import get_logger

# Initialize FastAPI app
app = FastAPI(
    title="Shepherd API",
    description="Intelligent Workflow Orchestrator API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
logger = get_logger('api')
orchestrator = IntelligentOrchestrator()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Pydantic models
class WorkflowRequest(BaseModel):
    request: str
    show_analysis: bool = True

class WorkflowResponse(BaseModel):
    success: bool
    workflow_id: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    execution_summary: Optional[Dict[str, Any]] = None
    steps: Optional[List[Dict[str, Any]]] = None
    output: Optional[Any] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# API Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.post("/api/workflow/execute", response_model=WorkflowResponse)
async def execute_workflow(request: WorkflowRequest):
    """Execute a workflow based on natural language request"""
    try:
        logger.info(f"Executing workflow request: {request.request[:50]}...")
        
        # Broadcast start message
        await manager.broadcast(json.dumps({
            "type": "workflow_started",
            "request": request.request,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Analyze the prompt
        analysis = orchestrator.analyze_prompt(request.request)
        
        # Broadcast analysis
        if request.show_analysis:
            await manager.broadcast(json.dumps({
                "type": "analysis_complete",
                "analysis": {
                    "complexity_score": analysis.complexity_score,
                    "urgency_score": analysis.urgency_score,
                    "quality_requirements": analysis.quality_requirements,
                    "task_types": analysis.task_types,
                    "recommended_pattern": analysis.recommended_pattern.value,
                    "team_size_needed": analysis.team_size_needed,
                    "confidence": analysis.confidence,
                    "dependencies": analysis.dependencies,
                    "parallel_potential": analysis.parallel_potential,
                    "decision_points": analysis.decision_points,
                    "iteration_needed": analysis.iteration_needed
                },
                "timestamp": datetime.now().isoformat()
            }))
        
        # Execute the workflow
        result = orchestrator.execute_request(request.request)
        
        # Broadcast completion
        await manager.broadcast(json.dumps({
            "type": "workflow_complete",
            "workflow_id": result.workflow_id,
            "status": result.status.value,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Prepare response
        response_data = WorkflowResponse(
            success=result.status == ExecutionStatus.COMPLETED,
            workflow_id=result.workflow_id,
            analysis={
                "complexity_score": analysis.complexity_score,
                "urgency_score": analysis.urgency_score,
                "quality_requirements": analysis.quality_requirements,
                "task_types": analysis.task_types,
                "recommended_pattern": analysis.recommended_pattern.value,
                "team_size_needed": analysis.team_size_needed,
                "confidence": analysis.confidence,
                "dependencies": analysis.dependencies,
                "parallel_potential": analysis.parallel_potential,
                "decision_points": analysis.decision_points,
                "iteration_needed": analysis.iteration_needed
            } if request.show_analysis else None,
            execution_summary={
                "workflow_id": result.workflow_id,
                "pattern": result.pattern.value,
                "status": result.status.value,
                "total_execution_time": result.total_execution_time,
                "steps_executed": len(result.steps)
            },
            steps=[{
                "description": step.description,
                "status": step.status.value,
                "execution_time": step.execution_time,
                "output": step.output,
                "error": step.error
            } for step in result.steps],
            output=result.output
        )
        
        logger.info("Workflow execution completed successfully")
        return response_data
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Workflow execution failed: {error_msg}", exc_info=True)
        
        # Broadcast error
        await manager.broadcast(json.dumps({
            "type": "workflow_error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }))
        
        return WorkflowResponse(
            success=False,
            error=error_msg
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/api/status")
async def get_status():
    """Get system status"""
    return {
        "status": "running",
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)