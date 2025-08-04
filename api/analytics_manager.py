"""
Analytics API Manager - Phase 10 Analytics Endpoints

This module provides REST API endpoints for all Phase 10 analytics functionality:
- Collaboration analysis endpoints
- Predictive insights endpoints  
- Custom dashboard management
- Metrics aggregation and export
- Real-time analytics streaming
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import asyncio
import json
import uuid
import io

from src.analytics.collaboration_analyzer import CollaborationAnalyzer
from src.analytics.predictive_engine import PredictiveEngine, PredictionType
from src.analytics.metrics_aggregator import MetricsAggregator, MetricType, AggregationType
from src.analytics.dashboard_engine import DashboardEngine, WidgetType, RefreshInterval
from src.analytics.export_manager import ExportManager, ExportFormat


# Pydantic models for API requests/responses
class CollaborationAnalysisRequest(BaseModel):
    time_window_hours: int = Field(default=24, ge=1, le=168)  # 1 hour to 1 week
    include_network_analysis: bool = True


class CollaborationMetricsResponse(BaseModel):
    total_interactions: int
    unique_agent_pairs: int
    avg_response_time: float
    success_rate: float
    communication_density: float
    efficiency_score: float
    most_active_agents: List[Dict[str, Any]]
    pattern_distribution: Dict[str, float]


class NetworkAnalysisResponse(BaseModel):
    centrality_scores: Dict[str, float]
    clustering_coefficient: float
    network_diameter: int
    connected_components: int
    bottleneck_agents: List[str]
    bridge_agents: List[str]


class PredictionRequest(BaseModel):
    prediction_type: str
    context: Dict[str, Any]
    target_id: Optional[str] = None
    time_horizon_hours: Optional[int] = None


class PredictionResponse(BaseModel):
    prediction_type: str
    target_id: str
    predicted_value: Any
    confidence: float
    explanation: str
    timestamp: str
    time_horizon: Optional[str] = None


class PredictiveInsightsRequest(BaseModel):
    context: Optional[Dict[str, Any]] = None
    time_horizon_hours: int = Field(default=24, ge=1, le=168)
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class MetricsAggregationRequest(BaseModel):
    metric_type: str
    aggregation_type: str
    time_window_hours: int = Field(default=1, ge=1, le=168)
    tags: Optional[Dict[str, str]] = None


class DashboardCreateRequest(BaseModel):
    name: str
    description: str
    template_id: Optional[str] = None


class DashboardUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    theme: Optional[str] = None
    shared_with: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class WidgetCreateRequest(BaseModel):
    widget_type: str
    title: str
    position: Dict[str, int]
    data_source: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[str] = "normal"


class ExportRequest(BaseModel):
    format: str
    title: str
    description: str
    data_sources: List[Dict[str, Any]]
    time_range_hours: int = Field(default=24, ge=1, le=168)
    filters: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None
    include_charts: bool = True
    include_raw_data: bool = False


class AnalyticsManager:
    """
    Manages all Phase 10 analytics API endpoints and WebSocket connections.
    """
    
    def __init__(self, 
                 collaboration_analyzer: CollaborationAnalyzer,
                 predictive_engine: PredictiveEngine,
                 metrics_aggregator: MetricsAggregator,
                 dashboard_engine: DashboardEngine,
                 export_manager: ExportManager):
        
        self.collaboration_analyzer = collaboration_analyzer
        self.predictive_engine = predictive_engine
        self.metrics_aggregator = metrics_aggregator
        self.dashboard_engine = dashboard_engine
        self.export_manager = export_manager
        
        # WebSocket connections
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Create router
        self.router = APIRouter(prefix="/api/analytics", tags=["analytics"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        # Collaboration Analysis Routes
        @self.router.post("/collaboration/analyze", response_model=CollaborationMetricsResponse)
        async def analyze_collaboration(request: CollaborationAnalysisRequest):
            """Analyze agent collaboration patterns"""
            try:
                time_window = timedelta(hours=request.time_window_hours)
                metrics = await self.collaboration_analyzer.analyze_collaboration_patterns(time_window)
                
                return CollaborationMetricsResponse(
                    total_interactions=metrics.total_interactions,
                    unique_agent_pairs=metrics.unique_agent_pairs,
                    avg_response_time=metrics.avg_response_time,
                    success_rate=metrics.success_rate,
                    communication_density=metrics.communication_density,
                    efficiency_score=metrics.efficiency_score,
                    most_active_agents=[
                        {"agent": agent, "interactions": count}
                        for agent, count in metrics.most_active_agents
                    ],
                    pattern_distribution=metrics.pattern_distribution
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        
        @self.router.post("/collaboration/network", response_model=NetworkAnalysisResponse)
        async def analyze_network(request: CollaborationAnalysisRequest):
            """Analyze agent network structure"""
            try:
                time_window = timedelta(hours=request.time_window_hours)
                network = await self.collaboration_analyzer.analyze_network_structure(time_window)
                
                return NetworkAnalysisResponse(
                    centrality_scores=network.centrality_scores,
                    clustering_coefficient=network.clustering_coefficient,
                    network_diameter=network.network_diameter,
                    connected_components=network.connected_components,
                    bottleneck_agents=network.bottleneck_agents,
                    bridge_agents=network.bridge_agents
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Network analysis failed: {str(e)}")
        
        @self.router.get("/collaboration/insights")
        async def get_collaboration_insights(time_window_hours: int = 24):
            """Get high-level collaboration insights"""
            try:
                time_window = timedelta(hours=time_window_hours)
                insights = await self.collaboration_analyzer.get_collaboration_insights(time_window)
                return insights
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Insights failed: {str(e)}")
        
        # Predictive Analytics Routes
        @self.router.post("/predictions/predict", response_model=PredictionResponse)
        async def make_prediction(request: PredictionRequest):
            """Make a prediction based on context"""
            try:
                # Parse prediction type
                try:
                    prediction_type = PredictionType[request.prediction_type.upper()]
                except KeyError:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid prediction type: {request.prediction_type}"
                    )
                
                # Add time horizon to context if provided
                context = request.context.copy()
                if request.time_horizon_hours:
                    context['time_horizon'] = timedelta(hours=request.time_horizon_hours)
                if request.target_id:
                    context['target_id'] = request.target_id
                
                # Make prediction
                prediction = await self.predictive_engine.predict(prediction_type, context)
                
                return PredictionResponse(
                    prediction_type=prediction.prediction_type.value,
                    target_id=prediction.target_id,
                    predicted_value=prediction.predicted_value,
                    confidence=prediction.confidence,
                    explanation=prediction.explanation,
                    timestamp=prediction.timestamp.isoformat(),
                    time_horizon=prediction.time_horizon.total_seconds() if prediction.time_horizon else None
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
        
        @self.router.post("/predictions/insights")
        async def get_predictive_insights(request: PredictiveInsightsRequest):
            """Get predictive insights and recommendations"""
            try:
                time_horizon = timedelta(hours=request.time_horizon_hours)
                insights = await self.predictive_engine.get_predictive_insights(
                    context=request.context,
                    time_horizon=time_horizon
                )
                
                # Filter by confidence
                filtered_insights = [
                    {
                        'insight_type': insight.insight_type,
                        'title': insight.title,
                        'description': insight.description,
                        'confidence': insight.confidence,
                        'impact': insight.impact,
                        'recommendations': insight.recommendations,
                        'supporting_data': insight.supporting_data,
                        'expires_at': insight.expires_at.isoformat()
                    }
                    for insight in insights
                    if insight.confidence >= request.min_confidence
                ]
                
                return {
                    'insights': filtered_insights,
                    'total_insights': len(insights),
                    'filtered_insights': len(filtered_insights),
                    'generated_at': datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Insights failed: {str(e)}")
        
        @self.router.get("/predictions/models/performance")
        async def get_model_performance():
            """Get performance metrics for all prediction models"""
            try:
                performance = await self.predictive_engine.get_model_performance()
                return performance
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Model performance failed: {str(e)}")
        
        @self.router.post("/predictions/models/train")
        async def train_models(background_tasks: BackgroundTasks, 
                             historical_data: Optional[List[Dict]] = None):
            """Train or retrain prediction models"""
            try:
                # Run training in background
                background_tasks.add_task(
                    self.predictive_engine.train_models,
                    historical_data
                )
                
                return {
                    'status': 'training_started',
                    'message': 'Model training started in background',
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")
        
        # Metrics Aggregation Routes
        @self.router.post("/metrics/aggregate")
        async def aggregate_metrics(request: MetricsAggregationRequest):
            """Aggregate metrics over time window"""
            try:
                # Parse enums
                try:
                    metric_type = MetricType[request.metric_type.upper()]
                    aggregation_type = AggregationType[request.aggregation_type.upper()]
                except KeyError as e:
                    raise HTTPException(status_code=400, detail=f"Invalid enum value: {str(e)}")
                
                time_window = timedelta(hours=request.time_window_hours)
                
                result = await self.metrics_aggregator.aggregate_metrics(
                    metric_type, aggregation_type, time_window, request.tags
                )
                
                return {
                    'metric_type': result.metric_type.value,
                    'aggregation_type': result.aggregation_type.value,
                    'value': result.value,
                    'sample_count': result.sample_count,
                    'start_time': result.start_time.isoformat(),
                    'end_time': result.end_time.isoformat(),
                    'tags': result.tags,
                    'percentiles': result.percentiles
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Aggregation failed: {str(e)}")
        
        @self.router.get("/metrics/trends/{metric_type}")
        async def get_metric_trends(metric_type: str, 
                                  time_window_hours: int = 24,
                                  tags: Optional[str] = None):
            """Get trend analysis for a metric"""
            try:
                # Parse metric type
                try:
                    metric_enum = MetricType[metric_type.upper()]
                except KeyError:
                    raise HTTPException(status_code=400, detail=f"Invalid metric type: {metric_type}")
                
                # Parse tags
                tag_dict = None
                if tags:
                    try:
                        tag_dict = json.loads(tags)
                    except json.JSONDecodeError:
                        raise HTTPException(status_code=400, detail="Invalid tags JSON")
                
                time_window = timedelta(hours=time_window_hours)
                trend = await self.metrics_aggregator.get_metric_trends(
                    metric_enum, time_window, tag_dict
                )
                
                return {
                    'metric_type': trend.metric_type.value,
                    'direction': trend.direction,
                    'change_rate': trend.change_rate,
                    'forecast_value': trend.forecast_value,
                    'confidence': trend.confidence,
                    'anomalies': [t.isoformat() for t in trend.anomalies]
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")
        
        @self.router.get("/metrics/health")
        async def get_health_score(time_window_hours: int = 1):
            """Get system health score"""
            try:
                time_window = timedelta(hours=time_window_hours)
                health = await self.metrics_aggregator.get_health_score(time_window)
                return health
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
        
        @self.router.get("/metrics/top/{metric_type}")
        async def get_top_metrics(metric_type: str,
                                aggregation_type: str = "average",
                                group_by: str = "agent_id",
                                time_window_hours: int = 24,
                                limit: int = 10):
            """Get top N metrics grouped by tag"""
            try:
                # Parse enums
                try:
                    metric_enum = MetricType[metric_type.upper()]
                    agg_enum = AggregationType[aggregation_type.upper()]
                except KeyError as e:
                    raise HTTPException(status_code=400, detail=f"Invalid enum: {str(e)}")
                
                time_window = timedelta(hours=time_window_hours)
                
                top_metrics = await self.metrics_aggregator.get_top_metrics(
                    metric_enum, agg_enum, time_window, group_by, limit
                )
                
                return {
                    'top_metrics': top_metrics,
                    'metric_type': metric_type,
                    'aggregation_type': aggregation_type,
                    'group_by': group_by,
                    'time_window_hours': time_window_hours,
                    'generated_at': datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Top metrics failed: {str(e)}")
        
        # Dashboard Management Routes
        @self.router.post("/dashboards")
        async def create_dashboard(request: DashboardCreateRequest, owner: str = "default"):
            """Create a new dashboard"""
            try:
                dashboard = await self.dashboard_engine.create_dashboard(
                    name=request.name,
                    description=request.description,
                    owner=owner,
                    template_id=request.template_id
                )
                
                return {
                    'dashboard_id': dashboard.dashboard_id,
                    'name': dashboard.name,
                    'description': dashboard.description,
                    'owner': dashboard.owner,
                    'created_at': dashboard.created_at.isoformat(),
                    'widget_count': len(dashboard.widgets)
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Dashboard creation failed: {str(e)}")
        
        @self.router.get("/dashboards")
        async def list_dashboards(owner: Optional[str] = None):
            """List all dashboards"""
            try:
                dashboards = await self.dashboard_engine.get_dashboard_list(owner)
                return {
                    'dashboards': dashboards,
                    'count': len(dashboards),
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Dashboard listing failed: {str(e)}")
        
        @self.router.get("/dashboards/{dashboard_id}")
        async def get_dashboard(dashboard_id: str):
            """Get dashboard configuration"""
            try:
                if dashboard_id not in self.dashboard_engine.dashboards:
                    raise HTTPException(status_code=404, detail="Dashboard not found")
                
                dashboard = self.dashboard_engine.dashboards[dashboard_id]
                return self.dashboard_engine._serialize_dashboard(dashboard)
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Dashboard retrieval failed: {str(e)}")
        
        @self.router.put("/dashboards/{dashboard_id}")
        async def update_dashboard(dashboard_id: str, request: DashboardUpdateRequest):
            """Update dashboard configuration"""
            try:
                updates = {k: v for k, v in request.dict().items() if v is not None}
                dashboard = await self.dashboard_engine.update_dashboard(dashboard_id, updates)
                
                return {
                    'dashboard_id': dashboard.dashboard_id,
                    'updated_at': dashboard.updated_at.isoformat(),
                    'changes': list(updates.keys())
                }
                
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Dashboard update failed: {str(e)}")
        
        @self.router.delete("/dashboards/{dashboard_id}")
        async def delete_dashboard(dashboard_id: str):
            """Delete a dashboard"""
            try:
                if dashboard_id not in self.dashboard_engine.dashboards:
                    raise HTTPException(status_code=404, detail="Dashboard not found")
                
                del self.dashboard_engine.dashboards[dashboard_id]
                
                return {
                    'dashboard_id': dashboard_id,
                    'deleted_at': datetime.now().isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Dashboard deletion failed: {str(e)}")
        
        @self.router.post("/dashboards/{dashboard_id}/widgets")
        async def add_widget(dashboard_id: str, request: WidgetCreateRequest):
            """Add widget to dashboard"""
            try:
                # Parse widget type and refresh interval
                try:
                    widget_type = WidgetType[request.widget_type.upper()]
                    refresh_interval = RefreshInterval[request.refresh_interval.upper()]
                except KeyError as e:
                    raise HTTPException(status_code=400, detail=f"Invalid enum: {str(e)}")
                
                widget = await self.dashboard_engine.add_widget(
                    dashboard_id=dashboard_id,
                    widget_type=widget_type,
                    title=request.title,
                    position=request.position,
                    data_source=request.data_source,
                    options=request.options
                )
                
                return {
                    'widget_id': widget.widget_id,
                    'widget_type': widget.widget_type.value,
                    'title': widget.title,
                    'position': widget.position
                }
                
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Widget creation failed: {str(e)}")
        
        @self.router.delete("/dashboards/{dashboard_id}/widgets/{widget_id}")
        async def remove_widget(dashboard_id: str, widget_id: str):
            """Remove widget from dashboard"""
            try:
                await self.dashboard_engine.remove_widget(dashboard_id, widget_id)
                
                return {
                    'dashboard_id': dashboard_id,
                    'widget_id': widget_id,
                    'removed_at': datetime.now().isoformat()
                }
                
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Widget removal failed: {str(e)}")
        
        @self.router.get("/dashboards/{dashboard_id}/widgets/{widget_id}/data")
        async def get_widget_data(dashboard_id: str, widget_id: str, force_refresh: bool = False):
            """Get data for a specific widget"""
            try:
                data = await self.dashboard_engine.get_widget_data(
                    dashboard_id, widget_id, force_refresh
                )
                
                return {
                    'widget_id': widget_id,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }
                
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Widget data failed: {str(e)}")
        
        @self.router.post("/dashboards/{dashboard_id}/clone")
        async def clone_dashboard(dashboard_id: str, new_name: str, new_owner: str = "default"):
            """Clone an existing dashboard"""
            try:
                clone = await self.dashboard_engine.clone_dashboard(
                    dashboard_id, new_name, new_owner
                )
                
                return {
                    'original_dashboard_id': dashboard_id,
                    'cloned_dashboard_id': clone.dashboard_id,
                    'name': clone.name,
                    'owner': clone.owner,
                    'created_at': clone.created_at.isoformat()
                }
                
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Dashboard cloning failed: {str(e)}")
        
        # Export Routes
        @self.router.post("/export")
        async def create_export(request: ExportRequest, background_tasks: BackgroundTasks):
            """Create an export job"""
            try:
                # Parse export format
                try:
                    export_format = ExportFormat[request.format.upper()]
                except KeyError:
                    raise HTTPException(status_code=400, detail=f"Invalid format: {request.format}")
                
                # Create export config
                from src.analytics.export_manager import ExportConfig
                
                export_config = ExportConfig(
                    export_id=str(uuid.uuid4()),
                    format=export_format,
                    title=request.title,
                    description=request.description,
                    data_sources=request.data_sources,
                    time_range=timedelta(hours=request.time_range_hours),
                    filters=request.filters or {},
                    options=request.options or {},
                    include_charts=request.include_charts,
                    include_raw_data=request.include_raw_data
                )
                
                # Start export
                result = await self.export_manager.export_data(export_config)
                
                return {
                    'export_id': result.export_id,
                    'format': result.format.value,
                    'status': result.status,
                    'created_at': result.created_at.isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Export creation failed: {str(e)}")
        
        @self.router.get("/export/{export_id}/status")
        async def get_export_status(export_id: str):
            """Get export job status"""
            try:
                result = await self.export_manager.get_export_status(export_id)
                
                if not result:
                    raise HTTPException(status_code=404, detail="Export not found")
                
                return {
                    'export_id': result.export_id,
                    'format': result.format.value,
                    'status': result.status,
                    'file_size': result.file_size,
                    'errors': result.errors,
                    'created_at': result.created_at.isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Export status failed: {str(e)}")
        
        @self.router.get("/export/{export_id}/download")
        async def download_export(export_id: str):
            """Download exported file"""
            try:
                result = await self.export_manager.get_export_status(export_id)
                
                if not result:
                    raise HTTPException(status_code=404, detail="Export not found")
                
                if result.status != 'success':
                    raise HTTPException(status_code=400, detail=f"Export not ready: {result.status}")
                
                file_content = await self.export_manager.get_export_file(export_id)
                
                if not file_content:
                    raise HTTPException(status_code=404, detail="Export file not found")
                
                # Determine content type
                content_type = result.metadata.get('mime_type', 'application/octet-stream')
                
                # Generate filename
                extension_map = {
                    'csv': 'csv',
                    'json': 'json',
                    'pdf': 'pdf',
                    'excel': 'xlsx',
                    'html': 'html',
                    'markdown': 'md'
                }
                extension = extension_map.get(result.format.value, 'txt')
                filename = f"export_{export_id}.{extension}"
                
                return StreamingResponse(
                    io.BytesIO(file_content),
                    media_type=content_type,
                    headers={"Content-Disposition": f"attachment; filename={filename}"}
                )
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Export download failed: {str(e)}")
        
        # WebSocket Routes for Real-time Updates
        @self.router.websocket("/ws/dashboard/{dashboard_id}")
        async def dashboard_websocket(websocket: WebSocket, dashboard_id: str):
            """WebSocket for real-time dashboard updates"""
            await websocket.accept()
            connection_id = str(uuid.uuid4())
            self.active_connections[connection_id] = websocket
            
            try:
                # Subscribe to dashboard updates
                queue = await self.dashboard_engine.subscribe_to_dashboard(dashboard_id)
                
                while True:
                    try:
                        # Wait for updates
                        update = await asyncio.wait_for(queue.get(), timeout=30.0)
                        await websocket.send_json(update)
                        
                    except asyncio.TimeoutError:
                        # Send heartbeat
                        await websocket.send_json({
                            'type': 'heartbeat',
                            'timestamp': datetime.now().isoformat()
                        })
                        
            except WebSocketDisconnect:
                pass
            except Exception as e:
                await websocket.send_json({
                    'type': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            finally:
                if connection_id in self.active_connections:
                    del self.active_connections[connection_id]
        
        @self.router.websocket("/ws/metrics/{metric_type}")
        async def metrics_websocket(websocket: WebSocket, metric_type: str, tags: Optional[str] = None):
            """WebSocket for real-time metric updates"""
            await websocket.accept()
            connection_id = str(uuid.uuid4())
            self.active_connections[connection_id] = websocket
            
            try:
                # Parse metric type
                try:
                    metric_enum = MetricType[metric_type.upper()]
                except KeyError:
                    await websocket.send_json({
                        'type': 'error',
                        'message': f'Invalid metric type: {metric_type}'
                    })
                    return
                
                # Parse tags
                tag_dict = None
                if tags:
                    try:
                        tag_dict = json.loads(tags)
                    except json.JSONDecodeError:
                        await websocket.send_json({
                            'type': 'error', 
                            'message': 'Invalid tags JSON'
                        })
                        return
                
                # Subscribe to metric updates
                queue = await self.metrics_aggregator.subscribe_to_metric(metric_enum, tag_dict)
                
                while True:
                    try:
                        # Wait for metric updates
                        metric = await asyncio.wait_for(queue.get(), timeout=30.0)
                        
                        await websocket.send_json({
                            'type': 'metric_update',
                            'metric_type': metric.metric_type.value,
                            'value': metric.value,
                            'timestamp': metric.timestamp.isoformat(),
                            'tags': metric.tags,
                            'metadata': metric.metadata
                        })
                        
                    except asyncio.TimeoutError:
                        # Send heartbeat
                        await websocket.send_json({
                            'type': 'heartbeat',
                            'timestamp': datetime.now().isoformat()
                        })
                        
            except WebSocketDisconnect:
                pass
            except Exception as e:
                await websocket.send_json({
                    'type': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            finally:
                if connection_id in self.active_connections:
                    del self.active_connections[connection_id]
    
    async def shutdown(self):
        """Cleanup on shutdown"""
        # Close all WebSocket connections
        for connection in self.active_connections.values():
            await connection.close()
        self.active_connections.clear()