"""
Analytics API Routes - Phase 10 Implementation

FastAPI routes for the analytics system including:
- Collaboration analysis
- Predictive insights
- Dashboard management
- Export functionality
"""

from fastapi import APIRouter, HTTPException, Response, Depends, WebSocket
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
import io
import logging

from api.analytics_manager import (
    AnalyticsManager,
    CollaborationAnalysisRequest,
    CollaborationAnalysisResponse,
    PredictionRequest,
    PredictionResponse,
    PredictiveInsightsRequest,
    PredictiveInsightsResponse,
    DashboardCreateRequest,
    DashboardUpdateRequest,
    WidgetCreateRequest,
    WidgetUpdateRequest,
    ExportRequest,
    ExportResponse,
    MetricsRequest,
    MetricsResponse
)

# Initialize router
router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize analytics manager (placeholder - will be properly initialized in main.py)
analytics_manager: Optional[AnalyticsManager] = None


def get_analytics_manager() -> AnalyticsManager:
    """Dependency to get analytics manager"""
    if analytics_manager is None:
        raise HTTPException(status_code=503, detail="Analytics system not initialized")
    return analytics_manager


def get_current_user() -> str:
    """Get current user ID (placeholder for real auth)"""
    # In production, this would extract user from JWT token or session
    return "default_user"


# Collaboration Analysis Routes

@router.post("/collaboration/analysis", response_model=CollaborationAnalysisResponse)
async def get_collaboration_analysis(
    request: CollaborationAnalysisRequest,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """
    Get agent collaboration analysis
    
    Analyzes agent interaction patterns, network structure,
    and collaboration efficiency over a specified time window.
    """
    return await manager.get_collaboration_analysis(request, user_id)


# Predictive Analytics Routes

@router.post("/predictions", response_model=PredictionResponse)
async def make_prediction(
    request: PredictionRequest,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """
    Make a prediction using the predictive engine
    
    Supports predictions for:
    - workflow_success: Likelihood of workflow success
    - completion_time: Estimated completion time
    - agent_performance: Expected agent performance
    - resource_usage: Predicted resource consumption
    - bottleneck_risk: Risk of bottlenecks
    - failure_probability: Probability of failure
    """
    return await manager.make_prediction(request, user_id)


@router.post("/insights", response_model=PredictiveInsightsResponse)
async def get_predictive_insights(
    request: PredictiveInsightsRequest,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """
    Get predictive insights and recommendations
    
    Returns AI-generated insights about:
    - Workflow optimization opportunities
    - Performance improvement suggestions
    - Resource planning recommendations
    - Risk mitigation strategies
    """
    return await manager.get_predictive_insights(request, user_id)


# Dashboard Management Routes

@router.post("/dashboards")
async def create_dashboard(
    request: DashboardCreateRequest,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """
    Create a new analytics dashboard
    
    Supports creating dashboards from templates:
    - system_overview: System health and performance
    - agent_collaboration: Agent interaction analytics
    - predictive_analytics: Forecasts and predictions
    """
    return await manager.create_dashboard(request, user_id)


@router.get("/dashboards")
async def list_dashboards(
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """List all dashboards accessible to the user"""
    return await manager.list_dashboards(user_id)


@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(
    dashboard_id: str,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """Get dashboard configuration and widgets"""
    return await manager.get_dashboard(dashboard_id, user_id)


@router.patch("/dashboards/{dashboard_id}")
async def update_dashboard(
    dashboard_id: str,
    request: DashboardUpdateRequest,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """Update dashboard configuration"""
    return await manager.update_dashboard(dashboard_id, request, user_id)


@router.delete("/dashboards/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: str,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """Delete a dashboard"""
    return await manager.delete_dashboard(dashboard_id, user_id)


@router.post("/dashboards/{dashboard_id}/clone")
async def clone_dashboard(
    dashboard_id: str,
    new_name: str,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """Clone an existing dashboard"""
    return await manager.clone_dashboard(dashboard_id, new_name, user_id)


# Widget Management Routes

@router.post("/dashboards/{dashboard_id}/widgets")
async def add_widget(
    dashboard_id: str,
    request: WidgetCreateRequest,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """
    Add a widget to a dashboard
    
    Supported widget types:
    - line_chart: Time series line chart
    - bar_chart: Bar chart for categorical data
    - pie_chart: Pie chart for proportional data
    - gauge: Gauge for single metrics
    - metric_card: Single metric display
    - table: Tabular data display
    - heatmap: Heat map visualization
    - network_graph: Network topology visualization
    - alert_list: List of alerts/notifications
    """
    return await manager.add_widget(dashboard_id, request, user_id)


@router.delete("/dashboards/{dashboard_id}/widgets/{widget_id}")
async def remove_widget(
    dashboard_id: str,
    widget_id: str,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """Remove a widget from a dashboard"""
    return await manager.remove_widget(dashboard_id, widget_id, user_id)


@router.get("/dashboards/{dashboard_id}/widgets/{widget_id}/data")
async def get_widget_data(
    dashboard_id: str,
    widget_id: str,
    force_refresh: bool = False,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """Get data for a specific widget"""
    return await manager.get_widget_data(dashboard_id, widget_id, user_id, force_refresh)


# Metrics Routes

@router.post("/metrics", response_model=MetricsResponse)
async def get_metrics(
    request: MetricsRequest,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """
    Get aggregated metrics data
    
    Supported metric types:
    - workflow_duration: Workflow execution times
    - workflow_success_rate: Success rate of workflows
    - agent_task_count: Number of tasks per agent
    - agent_response_time: Agent response times
    - memory_usage: System memory usage
    - cpu_usage: System CPU usage
    - error_rate: Error occurrence rate
    - throughput: Task processing throughput
    - queue_length: Task queue lengths
    - collaboration_score: Agent collaboration metrics
    """
    return await manager.get_metrics(request, user_id)


# Export Routes

@router.post("/exports", response_model=ExportResponse)
async def create_export(
    request: ExportRequest,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """
    Create a data export
    
    Supported formats:
    - pdf: PDF report with charts and analysis
    - csv: Comma-separated values data
    - json: JSON data dump
    - excel: Excel workbook (uses CSV in Phase 10)
    - html: HTML report
    - markdown: Markdown document
    """
    return await manager.create_export(request, user_id)


@router.get("/exports/{export_id}", response_model=ExportResponse)
async def get_export_status(
    export_id: str,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """Get the status of an export job"""
    return await manager.get_export_status(export_id, user_id)


@router.get("/exports/{export_id}/download")
async def download_export(
    export_id: str,
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """Download an export file"""
    try:
        file_content = await manager.download_export(export_id, user_id)
        
        # Get export details for proper headers
        export_result = await manager.get_export_status(export_id, user_id)
        
        # Determine content type and filename
        content_type_map = {
            'pdf': 'application/pdf',
            'csv': 'text/csv',
            'json': 'application/json',
            'excel': 'application/vnd.ms-excel',
            'html': 'text/html',
            'markdown': 'text/markdown'
        }
        
        content_type = content_type_map.get(export_result.format, 'application/octet-stream')
        filename = f"shepherd_export_{export_id}.{export_result.format}"
        
        return Response(
            content=file_content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(file_content))
            }
        )
        
    except Exception as e:
        logger.error(f"Error in download_export: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System Health and Status Routes

@router.get("/health")
async def get_system_health(
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """
    Get overall system health score
    
    Returns a composite health score based on:
    - Workflow success rates
    - System performance metrics
    - Error rates
    - Resource utilization
    """
    return await manager.get_system_health(user_id)


@router.get("/status")
async def get_analytics_status(
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """
    Get analytics system status
    
    Returns status of all analytics components:
    - Collaboration analyzer
    - Predictive engine
    - Metrics aggregator
    - Dashboard engine
    - Export manager
    """
    return await manager.get_analytics_status(user_id)


# WebSocket Routes for Real-time Updates

@router.websocket("/ws/dashboards/{dashboard_id}")
async def dashboard_websocket(websocket: WebSocket, dashboard_id: str):
    """
    WebSocket endpoint for real-time dashboard updates
    
    Streams:
    - Widget data updates
    - Dashboard configuration changes
    - System alerts and notifications
    """
    await websocket.accept()
    
    try:
        if analytics_manager is None:
            await websocket.close(code=1011, reason="Service unavailable")
            return
        
        # Subscribe to dashboard updates
        queue = await analytics_manager.dashboard_engine.subscribe_to_dashboard(dashboard_id)
        
        # Send initial dashboard state
        try:
            dashboard = await analytics_manager.dashboard_engine.get_dashboard(dashboard_id)
            await websocket.send_json({
                "type": "dashboard_initial",
                "data": dashboard
            })
        except:
            await websocket.close(code=1008, reason="Dashboard not found")
            return
        
        # Stream updates
        while True:
            try:
                # Wait for updates from the dashboard engine
                update = await queue.get()
                await websocket.send_json(update)
                
            except Exception as e:
                logger.error(f"Error in dashboard WebSocket: {e}")
                break
                
    except Exception as e:
        logger.error(f"Dashboard WebSocket error: {e}")
    finally:
        # Clean up connection
        try:
            await websocket.close()
        except:
            pass


@router.websocket("/ws/metrics")
async def metrics_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time metrics streaming
    
    Streams live metrics data for dashboard widgets
    and monitoring applications.
    """
    await websocket.accept()
    
    try:
        if analytics_manager is None:
            await websocket.close(code=1011, reason="Service unavailable")
            return
        
        # Stream system metrics
        while True:
            try:
                # Get current health score
                health = await analytics_manager.get_system_health("websocket_user")
                
                await websocket.send_json({
                    "type": "health_update",
                    "data": health,
                    "timestamp": health.get("timestamp")
                })
                
                # Wait 5 seconds before next update
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in metrics WebSocket: {e}")
                break
                
    except Exception as e:
        logger.error(f"Metrics WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass


# Dashboard Templates Route

@router.get("/templates")
async def get_dashboard_templates(
    manager: AnalyticsManager = Depends(get_analytics_manager),
    user_id: str = Depends(get_current_user)
):
    """
    Get available dashboard templates
    
    Returns a list of pre-built dashboard templates
    that can be used to create new dashboards.
    """
    try:
        templates = []
        for template_id, template in manager.dashboard_engine.templates.items():
            templates.append({
                "template_id": template_id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "widget_count": len(template.widgets),
                "tags": template.tags,
                "preview_image": template.preview_image
            })
        
        return {"templates": templates}
        
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Initialize analytics manager function (to be called from main.py)
def initialize_analytics_manager(manager: AnalyticsManager):
    """Initialize the analytics manager instance"""
    global analytics_manager
    analytics_manager = manager