"""
Unit tests for DashboardEngine
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
import uuid

from src.analytics.dashboard_engine import (
    DashboardEngine,
    Dashboard,
    WidgetConfig,
    WidgetType,
    RefreshInterval,
    DashboardTemplate
)


class TestDashboardEngine:
    """Test cases for DashboardEngine"""
    
    @pytest.fixture
    def mock_metrics_aggregator(self):
        """Mock metrics aggregator"""
        ma = Mock()
        ma.aggregate_metrics = AsyncMock()
        ma.get_health_score = AsyncMock(return_value={
            'score': 0.85,
            'status': 'good',
            'components': {}
        })
        return ma
    
    @pytest.fixture
    def mock_collaboration_analyzer(self):
        """Mock collaboration analyzer"""
        ca = Mock()
        ca.analyze_network_structure = AsyncMock()
        ca.analyze_collaboration_patterns = AsyncMock()
        ca.interaction_history = []
        return ca
    
    @pytest.fixture
    def mock_predictive_engine(self):
        """Mock predictive engine"""
        pe = Mock()
        pe.predict = AsyncMock()
        pe.get_predictive_insights = AsyncMock(return_value=[])
        return pe
    
    @pytest.fixture
    def mock_shared_context(self):
        """Mock shared context"""
        context = AsyncMock()
        context.store = AsyncMock()
        return context
    
    @pytest.fixture
    def engine(self, mock_metrics_aggregator, mock_collaboration_analyzer, 
              mock_predictive_engine, mock_shared_context):
        """DashboardEngine instance"""
        return DashboardEngine(
            mock_metrics_aggregator,
            mock_collaboration_analyzer,
            mock_predictive_engine,
            mock_shared_context
        )
    
    def test_initialization(self, engine):
        """Test engine initialization"""
        assert len(engine.dashboards) == 0
        assert len(engine.templates) > 0
        
        # Check default templates
        assert 'system_overview' in engine.templates
        assert 'agent_collaboration' in engine.templates
        assert 'predictive_analytics' in engine.templates
    
    def test_initialize_templates(self, engine):
        """Test template initialization"""
        templates = engine.templates
        
        # System overview template
        system_template = templates['system_overview']
        assert system_template.name == 'System Overview'
        assert system_template.category == 'general'
        assert len(system_template.widgets) > 0
        
        # Agent collaboration template
        collab_template = templates['agent_collaboration']
        assert collab_template.name == 'Agent Collaboration'
        assert collab_template.category == 'agents'
        
        # Predictive analytics template
        pred_template = templates['predictive_analytics']
        assert pred_template.name == 'Predictive Analytics'
        assert pred_template.category == 'analytics'
    
    @pytest.mark.asyncio
    async def test_create_dashboard_empty(self, engine):
        """Test creating dashboard without template"""
        dashboard = await engine.create_dashboard(
            name="Test Dashboard",
            description="Test description",
            owner="test_user"
        )
        
        assert dashboard.name == "Test Dashboard"
        assert dashboard.description == "Test description"
        assert dashboard.owner == "test_user"
        assert len(dashboard.widgets) == 0
        assert dashboard.dashboard_id in engine.dashboards
    
    @pytest.mark.asyncio
    async def test_create_dashboard_with_template(self, engine):
        """Test creating dashboard from template"""
        dashboard = await engine.create_dashboard(
            name="System Dashboard",
            description="System monitoring",
            owner="admin",
            template_id="system_overview"
        )
        
        assert dashboard.name == "System Dashboard"
        assert len(dashboard.widgets) > 0
        
        # Check widgets were created from template
        widget_types = [w.widget_type for w in dashboard.widgets]
        assert WidgetType.METRIC_CARD in widget_types
        assert WidgetType.LINE_CHART in widget_types
        assert WidgetType.GAUGE in widget_types
    
    @pytest.mark.asyncio
    async def test_create_dashboard_invalid_template(self, engine):
        """Test creating dashboard with invalid template"""
        dashboard = await engine.create_dashboard(
            name="Test Dashboard",
            description="Test",
            owner="user",
            template_id="nonexistent_template"
        )
        
        # Should create empty dashboard
        assert len(dashboard.widgets) == 0
    
    @pytest.mark.asyncio
    async def test_update_dashboard(self, engine):
        """Test updating dashboard"""
        # Create dashboard first
        dashboard = await engine.create_dashboard(
            name="Original Name",
            description="Original desc",
            owner="user"
        )
        
        # Update it
        updates = {
            'name': 'Updated Name',
            'description': 'Updated description'
        }
        
        updated = await engine.update_dashboard(dashboard.dashboard_id, updates)
        
        assert updated.name == 'Updated Name'
        assert updated.description == 'Updated description'
        assert updated.updated_at > dashboard.created_at
    
    @pytest.mark.asyncio
    async def test_update_dashboard_not_found(self, engine):
        """Test updating non-existent dashboard"""
        with pytest.raises(ValueError, match="Dashboard .* not found"):
            await engine.update_dashboard("nonexistent", {"name": "test"})
    
    @pytest.mark.asyncio
    async def test_add_widget(self, engine):
        """Test adding widget to dashboard"""
        # Create dashboard
        dashboard = await engine.create_dashboard(
            name="Test Dashboard",
            description="Test",
            owner="user"
        )
        
        # Add widget
        widget = await engine.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.LINE_CHART,
            title="Test Chart",
            position={'x': 0, 'y': 0, 'width': 6, 'height': 4},
            data_source={'type': 'metric', 'metric_type': 'cpu_usage'}
        )
        
        assert widget.widget_type == WidgetType.LINE_CHART
        assert widget.title == "Test Chart"
        assert len(dashboard.widgets) == 1
        assert dashboard.widgets[0] == widget
    
    @pytest.mark.asyncio
    async def test_add_widget_dashboard_not_found(self, engine):
        """Test adding widget to non-existent dashboard"""
        with pytest.raises(ValueError, match="Dashboard .* not found"):
            await engine.add_widget(
                dashboard_id="nonexistent",
                widget_type=WidgetType.METRIC_CARD,
                title="Test",
                position={'x': 0, 'y': 0, 'width': 3, 'height': 2},
                data_source={'type': 'test'}
            )
    
    @pytest.mark.asyncio
    async def test_remove_widget(self, engine):
        """Test removing widget from dashboard"""
        # Create dashboard with widget
        dashboard = await engine.create_dashboard(
            name="Test Dashboard",
            description="Test",
            owner="user",
            template_id="system_overview"
        )
        
        original_count = len(dashboard.widgets)
        widget_to_remove = dashboard.widgets[0]
        
        # Remove widget
        await engine.remove_widget(dashboard.dashboard_id, widget_to_remove.widget_id)
        
        assert len(dashboard.widgets) == original_count - 1
        assert widget_to_remove not in dashboard.widgets
    
    @pytest.mark.asyncio
    async def test_remove_widget_dashboard_not_found(self, engine):
        """Test removing widget from non-existent dashboard"""
        with pytest.raises(ValueError, match="Dashboard .* not found"):
            await engine.remove_widget("nonexistent", "widget_id")
    
    @pytest.mark.asyncio
    async def test_get_widget_data_health_score(self, engine, mock_metrics_aggregator):
        """Test getting health score widget data"""
        # Create dashboard with health score widget
        dashboard = await engine.create_dashboard(
            name="Test Dashboard",
            description="Test",
            owner="user"
        )
        
        widget = await engine.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.METRIC_CARD,
            title="Health Score",
            position={'x': 0, 'y': 0, 'width': 3, 'height': 2},
            data_source={'type': 'health_score'}
        )
        
        # Get widget data
        data = await engine.get_widget_data(dashboard.dashboard_id, widget.widget_id)
        
        assert 'score' in data
        assert 'status' in data
        mock_metrics_aggregator.get_health_score.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_widget_data_metric(self, engine, mock_metrics_aggregator):
        """Test getting metric widget data"""
        from src.analytics.metrics_aggregator import AggregatedMetric, MetricType, AggregationType
        
        # Mock metric result
        mock_result = AggregatedMetric(
            metric_type=MetricType.CPU_USAGE,
            aggregation_type=AggregationType.AVERAGE,
            value=75.5,
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
            sample_count=60
        )
        mock_metrics_aggregator.aggregate_metrics.return_value = mock_result
        
        # Create dashboard with metric widget
        dashboard = await engine.create_dashboard(
            name="Test Dashboard",
            description="Test",
            owner="user"
        )
        
        widget = await engine.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.GAUGE,
            title="CPU Usage",
            position={'x': 0, 'y': 0, 'width': 3, 'height': 2},
            data_source={
                'type': 'metric',
                'metric_type': 'cpu_usage',
                'aggregation': 'average',
                'time_range': '1h'
            }
        )
        
        # Get widget data
        data = await engine.get_widget_data(dashboard.dashboard_id, widget.widget_id)
        
        assert data['value'] == 75.5
        assert data['sample_count'] == 60
        mock_metrics_aggregator.aggregate_metrics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_widget_data_widget_not_found(self, engine):
        """Test getting data for non-existent widget"""
        dashboard = await engine.create_dashboard(
            name="Test Dashboard",
            description="Test",
            owner="user"
        )
        
        with pytest.raises(ValueError, match="Widget .* not found"):
            await engine.get_widget_data(dashboard.dashboard_id, "nonexistent_widget")
    
    @pytest.mark.asyncio
    async def test_get_widget_data_dashboard_not_found(self, engine):
        """Test getting widget data from non-existent dashboard"""
        with pytest.raises(ValueError, match="Dashboard .* not found"):
            await engine.get_widget_data("nonexistent_dashboard", "widget_id")
    
    @pytest.mark.asyncio
    async def test_get_widget_data_cached(self, engine):
        """Test widget data caching"""
        # Create dashboard with widget
        dashboard = await engine.create_dashboard(
            name="Test Dashboard",
            description="Test",
            owner="user"
        )
        
        widget = await engine.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.METRIC_CARD,
            title="Health Score",
            position={'x': 0, 'y': 0, 'width': 3, 'height': 2},
            data_source={'type': 'health_score'}
        )
        
        # First call
        data1 = await engine.get_widget_data(dashboard.dashboard_id, widget.widget_id)
        
        # Second call (should use cache)
        data2 = await engine.get_widget_data(dashboard.dashboard_id, widget.widget_id)
        
        assert data1 == data2
    
    @pytest.mark.asyncio
    async def test_get_widget_data_force_refresh(self, engine, mock_metrics_aggregator):
        """Test forcing widget data refresh"""
        dashboard = await engine.create_dashboard(
            name="Test Dashboard",
            description="Test",
            owner="user"
        )
        
        widget = await engine.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.METRIC_CARD,
            title="Health Score",
            position={'x': 0, 'y': 0, 'width': 3, 'height': 2},
            data_source={'type': 'health_score'}
        )
        
        # First call
        await engine.get_widget_data(dashboard.dashboard_id, widget.widget_id)
        
        # Reset mock
        mock_metrics_aggregator.get_health_score.reset_mock()
        
        # Force refresh
        await engine.get_widget_data(
            dashboard.dashboard_id, 
            widget.widget_id, 
            force_refresh=True
        )
        
        # Should call the aggregator again
        mock_metrics_aggregator.get_health_score.assert_called_once()
    
    def test_parse_time_range(self, engine):
        """Test time range parsing"""
        # Test minutes
        assert engine._parse_time_range("30m") == timedelta(minutes=30)
        
        # Test hours
        assert engine._parse_time_range("2h") == timedelta(hours=2)
        
        # Test days
        assert engine._parse_time_range("7d") == timedelta(days=7)
        
        # Test default
        assert engine._parse_time_range("invalid") == timedelta(hours=1)
    
    @pytest.mark.asyncio
    async def test_subscribe_to_dashboard(self, engine):
        """Test subscribing to dashboard updates"""
        dashboard = await engine.create_dashboard(
            name="Test Dashboard",
            description="Test",
            owner="user"
        )
        
        queue = await engine.subscribe_to_dashboard(dashboard.dashboard_id)
        
        assert isinstance(queue, asyncio.Queue)
        assert dashboard.dashboard_id in engine.dashboard_subscribers
        assert queue in engine.dashboard_subscribers[dashboard.dashboard_id]
    
    @pytest.mark.asyncio
    async def test_subscribe_to_dashboard_not_found(self, engine):
        """Test subscribing to non-existent dashboard"""
        with pytest.raises(ValueError, match="Dashboard .* not found"):
            await engine.subscribe_to_dashboard("nonexistent")
    
    def test_serialize_dashboard(self, engine):
        """Test dashboard serialization"""
        widget = WidgetConfig(
            widget_id="test_widget",
            widget_type=WidgetType.LINE_CHART,
            title="Test Widget",
            position={'x': 0, 'y': 0, 'width': 6, 'height': 4},
            data_source={'type': 'test'},
            refresh_interval=RefreshInterval.NORMAL
        )
        
        dashboard = Dashboard(
            dashboard_id="test_dashboard",
            name="Test Dashboard",
            description="Test description",
            owner="test_user",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 2),
            widgets=[widget]
        )
        
        serialized = engine._serialize_dashboard(dashboard)
        
        assert serialized['dashboard_id'] == "test_dashboard"
        assert serialized['name'] == "Test Dashboard"
        assert serialized['owner'] == "test_user"
        assert len(serialized['widgets']) == 1
        
        # Check widget serialization
        widget_data = serialized['widgets'][0]
        assert widget_data['widget_id'] == "test_widget"
        assert widget_data['widget_type'] == WidgetType.LINE_CHART.value
        assert widget_data['title'] == "Test Widget"
    
    def test_serialize_widget(self, engine):
        """Test widget serialization"""
        widget = WidgetConfig(
            widget_id="test_widget",
            widget_type=WidgetType.BAR_CHART,
            title="Test Widget",
            position={'x': 3, 'y': 0, 'width': 6, 'height': 4},
            data_source={'type': 'metric', 'metric_type': 'memory_usage'},
            refresh_interval=RefreshInterval.FAST,
            options={'color': 'blue'},
            filters={'tag': 'production'}
        )
        
        serialized = engine._serialize_widget(widget)
        
        assert serialized['widget_id'] == "test_widget"
        assert serialized['widget_type'] == WidgetType.BAR_CHART.value
        assert serialized['title'] == "Test Widget"
        assert serialized['position'] == {'x': 3, 'y': 0, 'width': 6, 'height': 4}
        assert serialized['data_source'] == {'type': 'metric', 'metric_type': 'memory_usage'}
        assert serialized['refresh_interval'] == RefreshInterval.FAST.value
        assert serialized['options'] == {'color': 'blue'}
        assert serialized['filters'] == {'tag': 'production'}
    
    @pytest.mark.asyncio
    async def test_get_dashboard_list_empty(self, engine):
        """Test getting dashboard list when empty"""
        dashboards = await engine.get_dashboard_list()
        
        assert len(dashboards) == 0
    
    @pytest.mark.asyncio
    async def test_get_dashboard_list_with_dashboards(self, engine):
        """Test getting dashboard list with dashboards"""
        # Create a few dashboards
        dashboard1 = await engine.create_dashboard(
            name="Dashboard 1",
            description="First dashboard",
            owner="user1"
        )
        
        dashboard2 = await engine.create_dashboard(
            name="Dashboard 2",
            description="Second dashboard",
            owner="user2"
        )
        
        dashboards = await engine.get_dashboard_list()
        
        assert len(dashboards) == 2
        
        # Check structure
        for dash in dashboards:
            assert 'dashboard_id' in dash
            assert 'name' in dash
            assert 'description' in dash
            assert 'owner' in dash
            assert 'updated_at' in dash
            assert 'widget_count' in dash
            assert 'tags' in dash
    
    @pytest.mark.asyncio
    async def test_get_dashboard_list_filtered_by_owner(self, engine):
        """Test getting dashboard list filtered by owner"""
        # Create dashboards with different owners
        await engine.create_dashboard(
            name="Dashboard 1",
            description="First dashboard",
            owner="user1"
        )
        
        await engine.create_dashboard(
            name="Dashboard 2",
            description="Second dashboard",
            owner="user2"
        )
        
        # Filter by user1
        dashboards = await engine.get_dashboard_list(owner="user1")
        
        assert len(dashboards) == 1
        assert dashboards[0]['owner'] == "user1"
    
    @pytest.mark.asyncio
    async def test_clone_dashboard(self, engine):
        """Test cloning a dashboard"""
        # Create original dashboard with widgets
        original = await engine.create_dashboard(
            name="Original Dashboard",
            description="Original description",
            owner="user1",
            template_id="system_overview"
        )
        
        # Clone it
        clone = await engine.clone_dashboard(
            dashboard_id=original.dashboard_id,
            new_name="Cloned Dashboard",
            new_owner="user2"
        )
        
        assert clone.name == "Cloned Dashboard"
        assert clone.owner == "user2"
        assert len(clone.widgets) == len(original.widgets)
        assert clone.dashboard_id != original.dashboard_id
        
        # Check widgets were cloned
        for orig_widget, clone_widget in zip(original.widgets, clone.widgets):
            assert clone_widget.widget_id != orig_widget.widget_id
            assert clone_widget.title == orig_widget.title
            assert clone_widget.widget_type == orig_widget.widget_type
    
    @pytest.mark.asyncio
    async def test_clone_dashboard_not_found(self, engine):
        """Test cloning non-existent dashboard"""
        with pytest.raises(ValueError, match="Dashboard .* not found"):
            await engine.clone_dashboard(
                dashboard_id="nonexistent",
                new_name="Clone",
                new_owner="user"
            )