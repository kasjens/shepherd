"""
Dashboard Engine - Customizable Analytics Dashboard System

This module provides the backend for creating and managing custom dashboards:
- Widget-based dashboard layouts
- Real-time data streaming
- User-configurable metrics
- Dashboard templates
- Persistent dashboard configurations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)


class WidgetType(Enum):
    """Types of dashboard widgets available"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    GAUGE = "gauge"
    METRIC_CARD = "metric_card"
    TABLE = "table"
    HEATMAP = "heatmap"
    NETWORK_GRAPH = "network_graph"
    ALERT_LIST = "alert_list"
    LOG_VIEWER = "log_viewer"


class RefreshInterval(Enum):
    """Widget refresh intervals"""
    REAL_TIME = 1      # 1 second
    FAST = 5          # 5 seconds
    NORMAL = 30       # 30 seconds
    SLOW = 60         # 1 minute
    MANUAL = 0        # Manual refresh only


@dataclass
class WidgetConfig:
    """Configuration for a dashboard widget"""
    widget_id: str
    widget_type: WidgetType
    title: str
    position: Dict[str, int]  # x, y, width, height
    data_source: Dict[str, Any]
    refresh_interval: RefreshInterval
    options: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dashboard:
    """Dashboard configuration"""
    dashboard_id: str
    name: str
    description: str
    owner: str
    created_at: datetime
    updated_at: datetime
    widgets: List[WidgetConfig]
    layout_type: str = "grid"  # grid, freeform
    shared_with: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    theme: str = "light"


@dataclass
class DashboardTemplate:
    """Pre-built dashboard template"""
    template_id: str
    name: str
    description: str
    category: str
    widgets: List[Dict[str, Any]]
    preview_image: Optional[str] = None
    tags: List[str] = field(default_factory=list)


class DashboardEngine:
    """
    Manages custom dashboards with configurable widgets
    and real-time data updates.
    """
    
    def __init__(self, metrics_aggregator, collaboration_analyzer, predictive_engine, shared_context):
        self.metrics_aggregator = metrics_aggregator
        self.collaboration_analyzer = collaboration_analyzer
        self.predictive_engine = predictive_engine
        self.shared_context = shared_context
        
        # Dashboard storage
        self.dashboards: Dict[str, Dashboard] = {}
        self.templates: Dict[str, DashboardTemplate] = {}
        
        # Widget data cache
        self.widget_cache: Dict[str, Any] = {}
        self.cache_ttl = 60  # seconds
        
        # Real-time subscriptions
        self.widget_subscriptions: Dict[str, asyncio.Task] = {}
        self.dashboard_subscribers: Dict[str, List[asyncio.Queue]] = {}
        
        # Initialize default templates
        self._initialize_templates()
    
    def _initialize_templates(self) -> None:
        """Initialize default dashboard templates"""
        # System Overview Template
        self.templates['system_overview'] = DashboardTemplate(
            template_id='system_overview',
            name='System Overview',
            description='Overall system health and performance metrics',
            category='general',
            widgets=[
                {
                    'type': WidgetType.METRIC_CARD.value,
                    'title': 'System Health',
                    'position': {'x': 0, 'y': 0, 'width': 3, 'height': 2},
                    'data_source': {'type': 'health_score'}
                },
                {
                    'type': WidgetType.LINE_CHART.value,
                    'title': 'Workflow Success Rate',
                    'position': {'x': 3, 'y': 0, 'width': 6, 'height': 4},
                    'data_source': {
                        'metric_type': 'workflow_success_rate',
                        'aggregation': 'average',
                        'time_range': '1h'
                    }
                },
                {
                    'type': WidgetType.GAUGE.value,
                    'title': 'CPU Usage',
                    'position': {'x': 9, 'y': 0, 'width': 3, 'height': 2},
                    'data_source': {
                        'metric_type': 'cpu_usage',
                        'aggregation': 'average'
                    }
                }
            ],
            tags=['system', 'monitoring', 'overview']
        )
        
        # Agent Collaboration Template
        self.templates['agent_collaboration'] = DashboardTemplate(
            template_id='agent_collaboration',
            name='Agent Collaboration',
            description='Agent interaction patterns and collaboration metrics',
            category='agents',
            widgets=[
                {
                    'type': WidgetType.NETWORK_GRAPH.value,
                    'title': 'Agent Network',
                    'position': {'x': 0, 'y': 0, 'width': 6, 'height': 6},
                    'data_source': {'type': 'agent_network'}
                },
                {
                    'type': WidgetType.TABLE.value,
                    'title': 'Top Collaborating Agents',
                    'position': {'x': 6, 'y': 0, 'width': 6, 'height': 4},
                    'data_source': {'type': 'top_collaborators'}
                },
                {
                    'type': WidgetType.HEATMAP.value,
                    'title': 'Collaboration Patterns',
                    'position': {'x': 0, 'y': 6, 'width': 12, 'height': 4},
                    'data_source': {'type': 'collaboration_patterns'}
                }
            ],
            tags=['agents', 'collaboration', 'patterns']
        )
        
        # Predictive Analytics Template
        self.templates['predictive_analytics'] = DashboardTemplate(
            template_id='predictive_analytics',
            name='Predictive Analytics',
            description='Forecasts and predictive insights',
            category='analytics',
            widgets=[
                {
                    'type': WidgetType.LINE_CHART.value,
                    'title': 'Workload Forecast',
                    'position': {'x': 0, 'y': 0, 'width': 6, 'height': 4},
                    'data_source': {
                        'type': 'prediction',
                        'prediction_type': 'resource_usage'
                    }
                },
                {
                    'type': WidgetType.BAR_CHART.value,
                    'title': 'Failure Risk by Workflow',
                    'position': {'x': 6, 'y': 0, 'width': 6, 'height': 4},
                    'data_source': {
                        'type': 'prediction',
                        'prediction_type': 'failure_probability'
                    }
                },
                {
                    'type': WidgetType.ALERT_LIST.value,
                    'title': 'Predictive Alerts',
                    'position': {'x': 0, 'y': 4, 'width': 12, 'height': 3},
                    'data_source': {'type': 'predictive_alerts'}
                }
            ],
            tags=['analytics', 'prediction', 'insights']
        )
    
    async def create_dashboard(self,
                             name: str,
                             description: str,
                             owner: str,
                             template_id: Optional[str] = None) -> Dashboard:
        """
        Create a new dashboard
        
        Args:
            name: Dashboard name
            description: Dashboard description
            owner: Owner user ID
            template_id: Optional template to use
            
        Returns:
            Created Dashboard object
        """
        dashboard_id = str(uuid.uuid4())
        
        # Get widgets from template if specified
        widgets = []
        if template_id and template_id in self.templates:
            template = self.templates[template_id]
            
            # Create widget configs from template
            for widget_spec in template.widgets:
                widget_config = WidgetConfig(
                    widget_id=str(uuid.uuid4()),
                    widget_type=WidgetType(widget_spec['type']),
                    title=widget_spec['title'],
                    position=widget_spec['position'],
                    data_source=widget_spec['data_source'],
                    refresh_interval=RefreshInterval.NORMAL,
                    options=widget_spec.get('options', {}),
                    filters=widget_spec.get('filters', {})
                )
                widgets.append(widget_config)
        
        dashboard = Dashboard(
            dashboard_id=dashboard_id,
            name=name,
            description=description,
            owner=owner,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            widgets=widgets
        )
        
        # Store dashboard
        self.dashboards[dashboard_id] = dashboard
        
        # Persist to shared context
        await self._persist_dashboard(dashboard)
        
        return dashboard
    
    async def update_dashboard(self, dashboard_id: str, updates: Dict[str, Any]) -> Dashboard:
        """
        Update dashboard configuration
        
        Args:
            dashboard_id: Dashboard to update
            updates: Dictionary of updates
            
        Returns:
            Updated Dashboard object
        """
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        dashboard = self.dashboards[dashboard_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(dashboard, key):
                setattr(dashboard, key, value)
        
        dashboard.updated_at = datetime.now()
        
        # Persist changes
        await self._persist_dashboard(dashboard)
        
        # Notify subscribers
        await self._notify_dashboard_update(dashboard_id)
        
        return dashboard
    
    async def add_widget(self,
                        dashboard_id: str,
                        widget_type: WidgetType,
                        title: str,
                        position: Dict[str, int],
                        data_source: Dict[str, Any],
                        options: Optional[Dict[str, Any]] = None) -> WidgetConfig:
        """
        Add a widget to a dashboard
        
        Args:
            dashboard_id: Dashboard to add widget to
            widget_type: Type of widget
            title: Widget title
            position: Widget position and size
            data_source: Data source configuration
            options: Optional widget options
            
        Returns:
            Created WidgetConfig
        """
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        dashboard = self.dashboards[dashboard_id]
        
        widget = WidgetConfig(
            widget_id=str(uuid.uuid4()),
            widget_type=widget_type,
            title=title,
            position=position,
            data_source=data_source,
            refresh_interval=RefreshInterval.NORMAL,
            options=options or {},
            filters={}
        )
        
        dashboard.widgets.append(widget)
        dashboard.updated_at = datetime.now()
        
        # Persist changes
        await self._persist_dashboard(dashboard)
        
        # Start data subscription if needed
        if widget.refresh_interval != RefreshInterval.MANUAL:
            await self._start_widget_subscription(dashboard_id, widget)
        
        return widget
    
    async def remove_widget(self, dashboard_id: str, widget_id: str) -> None:
        """Remove a widget from a dashboard"""
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        dashboard = self.dashboards[dashboard_id]
        
        # Stop subscription
        subscription_key = f"{dashboard_id}:{widget_id}"
        if subscription_key in self.widget_subscriptions:
            self.widget_subscriptions[subscription_key].cancel()
            del self.widget_subscriptions[subscription_key]
        
        # Remove widget
        dashboard.widgets = [w for w in dashboard.widgets if w.widget_id != widget_id]
        dashboard.updated_at = datetime.now()
        
        # Persist changes
        await self._persist_dashboard(dashboard)
    
    async def get_widget_data(self,
                            dashboard_id: str,
                            widget_id: str,
                            force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get data for a widget
        
        Args:
            dashboard_id: Dashboard ID
            widget_id: Widget ID
            force_refresh: Force data refresh
            
        Returns:
            Widget data dictionary
        """
        # Find widget
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        widget = next((w for w in dashboard.widgets if w.widget_id == widget_id), None)
        if not widget:
            raise ValueError(f"Widget {widget_id} not found")
        
        # Check cache
        cache_key = f"{dashboard_id}:{widget_id}"
        
        if not force_refresh and cache_key in self.widget_cache:
            cache_time, cached_data = self.widget_cache[cache_key]
            if (datetime.now() - cache_time).seconds < self.cache_ttl:
                return cached_data
        
        # Fetch fresh data
        data = await self._fetch_widget_data(widget)
        
        # Cache result
        self.widget_cache[cache_key] = (datetime.now(), data)
        
        return data
    
    async def _fetch_widget_data(self, widget: WidgetConfig) -> Dict[str, Any]:
        """Fetch data for a widget based on its configuration"""
        data_source = widget.data_source
        source_type = data_source.get('type')
        
        if source_type == 'metric':
            # Fetch metric data
            metric_type = data_source.get('metric_type')
            aggregation = data_source.get('aggregation', 'average')
            time_range = data_source.get('time_range', '1h')
            
            # Parse time range
            time_window = self._parse_time_range(time_range)
            
            # Get aggregated metric
            from src.analytics.metrics_aggregator import MetricType, AggregationType
            
            metric_enum = MetricType[metric_type.upper()]
            agg_enum = AggregationType[aggregation.upper()]
            
            result = await self.metrics_aggregator.aggregate_metrics(
                metric_enum,
                agg_enum,
                time_window,
                widget.filters
            )
            
            return {
                'value': result.value,
                'timestamp': result.end_time.isoformat(),
                'sample_count': result.sample_count,
                'metadata': {
                    'aggregation': aggregation,
                    'time_range': time_range
                }
            }
        
        elif source_type == 'health_score':
            # Get system health score
            health = await self.metrics_aggregator.get_health_score()
            return health
        
        elif source_type == 'agent_network':
            # Get agent collaboration network
            network_analysis = await self.collaboration_analyzer.analyze_network_structure()
            
            # Convert to graph format for visualization
            nodes = []
            edges = []
            
            for agent, score in network_analysis.centrality_scores.items():
                nodes.append({
                    'id': agent,
                    'label': agent,
                    'size': score * 50,  # Scale for visualization
                    'centrality': score
                })
            
            # Build edges from interaction history
            interactions = self.collaboration_analyzer.interaction_history[-100:]  # Last 100
            edge_weights = {}
            
            for interaction in interactions:
                edge_key = f"{interaction.sender_id}-{interaction.receiver_id}"
                if edge_key not in edge_weights:
                    edge_weights[edge_key] = 0
                edge_weights[edge_key] += 1
            
            for edge_key, weight in edge_weights.items():
                source, target = edge_key.split('-')
                edges.append({
                    'source': source,
                    'target': target,
                    'weight': weight
                })
            
            return {
                'nodes': nodes,
                'edges': edges,
                'metadata': {
                    'clustering_coefficient': network_analysis.clustering_coefficient,
                    'network_diameter': network_analysis.network_diameter
                }
            }
        
        elif source_type == 'top_collaborators':
            # Get top collaborating agents
            metrics = await self.collaboration_analyzer.analyze_collaboration_patterns()
            
            return {
                'agents': [
                    {'agent': agent, 'interactions': count}
                    for agent, count in metrics.most_active_agents
                ],
                'total_interactions': metrics.total_interactions
            }
        
        elif source_type == 'collaboration_patterns':
            # Get collaboration pattern distribution
            metrics = await self.collaboration_analyzer.analyze_collaboration_patterns()
            
            # Convert to heatmap format
            patterns = []
            for pattern, frequency in metrics.pattern_distribution.items():
                patterns.append({
                    'pattern': pattern,
                    'frequency': frequency,
                    'color_value': frequency  # For heatmap coloring
                })
            
            return {
                'patterns': patterns,
                'efficiency_score': metrics.efficiency_score
            }
        
        elif source_type == 'prediction':
            # Get predictive data
            prediction_type = data_source.get('prediction_type')
            
            if prediction_type == 'resource_usage':
                # Get resource usage predictions for next 24 hours
                predictions = []
                for hour in range(24):
                    context = {
                        'current_resource_usage': 0.5,  # Would get from metrics
                        'agents': [],  # Would get active agents
                        'time_offset': hour
                    }
                    
                    from src.analytics.predictive_engine import PredictionType
                    pred = await self.predictive_engine.predict(
                        PredictionType.RESOURCE_USAGE,
                        context
                    )
                    
                    predictions.append({
                        'time': (datetime.now() + timedelta(hours=hour)).isoformat(),
                        'value': pred.predicted_value,
                        'confidence': pred.confidence
                    })
                
                return {
                    'predictions': predictions,
                    'current_value': 0.5  # Would get from metrics
                }
            
            elif prediction_type == 'failure_probability':
                # Get failure predictions by workflow type
                workflow_types = ['sequential', 'parallel', 'conditional', 'iterative', 'hierarchical']
                predictions = []
                
                for workflow_type in workflow_types:
                    context = {
                        'pattern_type': workflow_type,
                        'complexity': 0.5,
                        'recent_error_count': 0
                    }
                    
                    from src.analytics.predictive_engine import PredictionType
                    pred = await self.predictive_engine.predict(
                        PredictionType.FAILURE_PROBABILITY,
                        context
                    )
                    
                    predictions.append({
                        'workflow_type': workflow_type,
                        'failure_probability': pred.predicted_value,
                        'confidence': pred.confidence
                    })
                
                return {'predictions': predictions}
        
        elif source_type == 'predictive_alerts':
            # Get predictive insights as alerts
            insights = await self.predictive_engine.get_predictive_insights()
            
            alerts = []
            for insight in insights:
                if insight.impact in ['high', 'medium']:
                    alerts.append({
                        'id': str(uuid.uuid4()),
                        'title': insight.title,
                        'description': insight.description,
                        'severity': insight.impact,
                        'timestamp': datetime.now().isoformat(),
                        'recommendations': insight.recommendations
                    })
            
            return {'alerts': alerts}
        
        else:
            # Default empty data
            return {'error': f'Unknown data source type: {source_type}'}
    
    def _parse_time_range(self, time_range: str) -> timedelta:
        """Parse time range string to timedelta"""
        # Simple parser for common formats: 1h, 24h, 7d, etc.
        if time_range.endswith('m'):
            return timedelta(minutes=int(time_range[:-1]))
        elif time_range.endswith('h'):
            return timedelta(hours=int(time_range[:-1]))
        elif time_range.endswith('d'):
            return timedelta(days=int(time_range[:-1]))
        else:
            return timedelta(hours=1)  # Default to 1 hour
    
    async def _start_widget_subscription(self, dashboard_id: str, widget: WidgetConfig) -> None:
        """Start real-time data subscription for a widget"""
        subscription_key = f"{dashboard_id}:{widget.widget_id}"
        
        # Cancel existing subscription if any
        if subscription_key in self.widget_subscriptions:
            self.widget_subscriptions[subscription_key].cancel()
        
        # Create new subscription task
        task = asyncio.create_task(
            self._widget_update_loop(dashboard_id, widget)
        )
        
        self.widget_subscriptions[subscription_key] = task
    
    async def _widget_update_loop(self, dashboard_id: str, widget: WidgetConfig) -> None:
        """Update loop for widget data"""
        while True:
            try:
                # Fetch fresh data
                data = await self._fetch_widget_data(widget)
                
                # Update cache
                cache_key = f"{dashboard_id}:{widget.widget_id}"
                self.widget_cache[cache_key] = (datetime.now(), data)
                
                # Notify subscribers
                await self._notify_widget_update(dashboard_id, widget.widget_id, data)
                
                # Wait for refresh interval
                await asyncio.sleep(widget.refresh_interval.value)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error updating widget {widget.widget_id}: {e}")
                await asyncio.sleep(30)  # Wait before retry
    
    async def subscribe_to_dashboard(self, dashboard_id: str) -> asyncio.Queue:
        """
        Subscribe to dashboard updates
        
        Args:
            dashboard_id: Dashboard to subscribe to
            
        Returns:
            Queue that will receive updates
        """
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        queue = asyncio.Queue(maxsize=100)
        
        if dashboard_id not in self.dashboard_subscribers:
            self.dashboard_subscribers[dashboard_id] = []
        
        self.dashboard_subscribers[dashboard_id].append(queue)
        
        return queue
    
    async def _notify_widget_update(self,
                                  dashboard_id: str,
                                  widget_id: str,
                                  data: Dict[str, Any]) -> None:
        """Notify subscribers of widget data update"""
        subscribers = self.dashboard_subscribers.get(dashboard_id, [])
        
        update = {
            'type': 'widget_update',
            'dashboard_id': dashboard_id,
            'widget_id': widget_id,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to all subscribers
        for queue in subscribers[:]:  # Copy list to avoid modification during iteration
            try:
                await queue.put_nowait(update)
            except asyncio.QueueFull:
                # Skip if queue is full
                pass
            except:
                # Remove broken subscribers
                subscribers.remove(queue)
    
    async def _notify_dashboard_update(self, dashboard_id: str) -> None:
        """Notify subscribers of dashboard configuration update"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return
        
        subscribers = self.dashboard_subscribers.get(dashboard_id, [])
        
        update = {
            'type': 'dashboard_update',
            'dashboard_id': dashboard_id,
            'dashboard': self._serialize_dashboard(dashboard),
            'timestamp': datetime.now().isoformat()
        }
        
        for queue in subscribers[:]:
            try:
                await queue.put_nowait(update)
            except:
                pass
    
    async def _persist_dashboard(self, dashboard: Dashboard) -> None:
        """Persist dashboard to shared context"""
        await self.shared_context.store(
            f"dashboard_{dashboard.dashboard_id}",
            self._serialize_dashboard(dashboard)
        )
    
    def _serialize_dashboard(self, dashboard: Dashboard) -> Dict[str, Any]:
        """Serialize dashboard to dictionary"""
        return {
            'dashboard_id': dashboard.dashboard_id,
            'name': dashboard.name,
            'description': dashboard.description,
            'owner': dashboard.owner,
            'created_at': dashboard.created_at.isoformat(),
            'updated_at': dashboard.updated_at.isoformat(),
            'widgets': [self._serialize_widget(w) for w in dashboard.widgets],
            'layout_type': dashboard.layout_type,
            'shared_with': dashboard.shared_with,
            'tags': dashboard.tags,
            'theme': dashboard.theme
        }
    
    def _serialize_widget(self, widget: WidgetConfig) -> Dict[str, Any]:
        """Serialize widget to dictionary"""
        return {
            'widget_id': widget.widget_id,
            'widget_type': widget.widget_type.value,
            'title': widget.title,
            'position': widget.position,
            'data_source': widget.data_source,
            'refresh_interval': widget.refresh_interval.value,
            'options': widget.options,
            'filters': widget.filters
        }
    
    async def get_dashboard_list(self, owner: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of dashboards
        
        Args:
            owner: Optional filter by owner
            
        Returns:
            List of dashboard summaries
        """
        dashboards = []
        
        for dashboard in self.dashboards.values():
            if owner is None or dashboard.owner == owner or owner in dashboard.shared_with:
                dashboards.append({
                    'dashboard_id': dashboard.dashboard_id,
                    'name': dashboard.name,
                    'description': dashboard.description,
                    'owner': dashboard.owner,
                    'updated_at': dashboard.updated_at.isoformat(),
                    'widget_count': len(dashboard.widgets),
                    'tags': dashboard.tags
                })
        
        # Sort by updated time
        dashboards.sort(key=lambda x: x['updated_at'], reverse=True)
        
        return dashboards
    
    async def clone_dashboard(self,
                            dashboard_id: str,
                            new_name: str,
                            new_owner: str) -> Dashboard:
        """
        Clone an existing dashboard
        
        Args:
            dashboard_id: Dashboard to clone
            new_name: Name for the clone
            new_owner: Owner of the clone
            
        Returns:
            Cloned Dashboard object
        """
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        original = self.dashboards[dashboard_id]
        
        # Create new dashboard with same widgets
        clone = Dashboard(
            dashboard_id=str(uuid.uuid4()),
            name=new_name,
            description=f"Clone of {original.description}",
            owner=new_owner,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            widgets=[],
            layout_type=original.layout_type,
            theme=original.theme
        )
        
        # Clone widgets
        for widget in original.widgets:
            cloned_widget = WidgetConfig(
                widget_id=str(uuid.uuid4()),
                widget_type=widget.widget_type,
                title=widget.title,
                position=widget.position.copy(),
                data_source=widget.data_source.copy(),
                refresh_interval=widget.refresh_interval,
                options=widget.options.copy(),
                filters=widget.filters.copy()
            )
            clone.widgets.append(cloned_widget)
        
        # Store and persist
        self.dashboards[clone.dashboard_id] = clone
        await self._persist_dashboard(clone)
        
        return clone