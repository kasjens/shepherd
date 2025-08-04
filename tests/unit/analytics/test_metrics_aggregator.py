"""
Unit tests for MetricsAggregator
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
import numpy as np

from src.analytics.metrics_aggregator import (
    MetricsAggregator,
    MetricPoint,
    MetricType,
    AggregationType,
    AggregatedMetric,
    MetricTrend
)


@pytest.fixture
def mock_shared_context():
    """Mock shared context"""
    context = AsyncMock()
    context.store = AsyncMock()
    return context


@pytest.fixture
def metrics_aggregator(mock_shared_context):
    """Create MetricsAggregator instance for testing"""
    return MetricsAggregator(mock_shared_context)


@pytest.fixture
def sample_metric_points():
    """Sample metric points for testing"""
    base_time = datetime.now()
    return [
        MetricPoint(
            metric_type=MetricType.WORKFLOW_DURATION,
            value=100.0,
            timestamp=base_time,
            tags={"workflow_id": "wf1", "pattern": "sequential"}
        ),
        MetricPoint(
            metric_type=MetricType.WORKFLOW_DURATION,
            value=150.0,
            timestamp=base_time + timedelta(seconds=30),
            tags={"workflow_id": "wf2", "pattern": "parallel"}
        ),
        MetricPoint(
            metric_type=MetricType.AGENT_RESPONSE_TIME,
            value=50.0,
            timestamp=base_time + timedelta(minutes=1),
            tags={"agent_id": "agent1", "agent_type": "research"}
        ),
        MetricPoint(
            metric_type=MetricType.CPU_USAGE,
            value=75.0,
            timestamp=base_time + timedelta(minutes=2),
            tags={"host": "localhost"}
        )
    ]


class TestMetricsAggregator:
    """Test cases for MetricsAggregator"""
    
    @pytest.mark.asyncio
    async def test_record_metric(self, metrics_aggregator, mock_shared_context):
        """Test recording a single metric"""
        metric = MetricPoint(
            metric_type=MetricType.WORKFLOW_DURATION,
            value=100.0,
            timestamp=datetime.now(),
            tags={"workflow_id": "test"}
        )
        
        await metrics_aggregator.record_metric(metric)
        
        assert len(metrics_aggregator.metrics_buffer) == 1
        assert metrics_aggregator.metrics_buffer[0] == metric
        mock_shared_context.store.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_record_workflow_metrics(self, metrics_aggregator):
        """Test recording workflow metrics"""
        workflow_result = {
            "workflow_id": "test_workflow",
            "pattern": "sequential",
            "duration": 120.0,
            "success": True,
            "agent_results": [
                {
                    "agent_id": "agent1",
                    "agent_type": "research",
                    "response_time": 50.0
                },
                {
                    "agent_id": "agent2",
                    "agent_type": "technical",
                    "response_time": 75.0
                }
            ]
        }
        
        await metrics_aggregator.record_workflow_metrics(workflow_result)
        
        # Should record duration, success, and agent response times
        assert len(metrics_aggregator.metrics_buffer) == 4  # 1 duration + 1 success + 2 response times
        
        # Check metric types
        metric_types = [m.metric_type for m in metrics_aggregator.metrics_buffer]
        assert MetricType.WORKFLOW_DURATION in metric_types
        assert MetricType.WORKFLOW_SUCCESS_RATE in metric_types
        assert MetricType.AGENT_RESPONSE_TIME in metric_types
    
    @pytest.mark.asyncio
    async def test_record_system_metrics(self, metrics_aggregator):
        """Test recording system metrics"""
        system_stats = {
            "cpu_percent": 80.0,
            "memory_percent": 65.0,
            "host": "test_host"
        }
        
        await metrics_aggregator.record_system_metrics(system_stats)
        
        assert len(metrics_aggregator.metrics_buffer) == 2  # CPU and memory
        
        metric_types = [m.metric_type for m in metrics_aggregator.metrics_buffer]
        assert MetricType.CPU_USAGE in metric_types
        assert MetricType.MEMORY_USAGE in metric_types
    
    @pytest.mark.asyncio
    async def test_aggregate_metrics_empty(self, metrics_aggregator):
        """Test aggregation with no metrics"""
        result = await metrics_aggregator.aggregate_metrics(
            MetricType.WORKFLOW_DURATION,
            AggregationType.AVERAGE,
            timedelta(hours=1)
        )
        
        assert result.value == 0.0
        assert result.sample_count == 0
    
    @pytest.mark.asyncio
    async def test_aggregate_metrics_with_data(self, metrics_aggregator, sample_metric_points):
        """Test aggregation with sample data"""
        # Add sample metrics
        for metric in sample_metric_points:
            await metrics_aggregator.record_metric(metric)
        
        # Test average aggregation
        result = await metrics_aggregator.aggregate_metrics(
            MetricType.WORKFLOW_DURATION,
            AggregationType.AVERAGE,
            timedelta(hours=1)
        )
        
        assert result.sample_count == 2  # Two workflow duration metrics
        assert result.value == (100.0 + 150.0) / 2  # Average of the two values
        assert result.aggregation_type == AggregationType.AVERAGE
    
    @pytest.mark.asyncio
    async def test_aggregate_metrics_with_tags(self, metrics_aggregator, sample_metric_points):
        """Test aggregation with tag filtering"""
        # Add sample metrics
        for metric in sample_metric_points:
            await metrics_aggregator.record_metric(metric)
        
        # Filter by pattern tag
        result = await metrics_aggregator.aggregate_metrics(
            MetricType.WORKFLOW_DURATION,
            AggregationType.AVERAGE,
            timedelta(hours=1),
            tags={"pattern": "sequential"}
        )
        
        assert result.sample_count == 1  # Only one sequential workflow
        assert result.value == 100.0
    
    def test_calculate_aggregation_average(self, metrics_aggregator):
        """Test average aggregation calculation"""
        values = [10.0, 20.0, 30.0]
        result = metrics_aggregator._calculate_aggregation(values, AggregationType.AVERAGE)
        assert result == 20.0
    
    def test_calculate_aggregation_sum(self, metrics_aggregator):
        """Test sum aggregation calculation"""
        values = [10.0, 20.0, 30.0]
        result = metrics_aggregator._calculate_aggregation(values, AggregationType.SUM)
        assert result == 60.0
    
    def test_calculate_aggregation_min_max(self, metrics_aggregator):
        """Test min/max aggregation calculation"""
        values = [10.0, 20.0, 30.0]
        
        min_result = metrics_aggregator._calculate_aggregation(values, AggregationType.MINIMUM)
        assert min_result == 10.0
        
        max_result = metrics_aggregator._calculate_aggregation(values, AggregationType.MAXIMUM)
        assert max_result == 30.0
    
    def test_calculate_aggregation_percentiles(self, metrics_aggregator):
        """Test percentile aggregation calculation"""
        values = list(range(100))  # 0 to 99
        
        p50 = metrics_aggregator._calculate_aggregation(values, AggregationType.PERCENTILE_50)
        p95 = metrics_aggregator._calculate_aggregation(values, AggregationType.PERCENTILE_95)
        p99 = metrics_aggregator._calculate_aggregation(values, AggregationType.PERCENTILE_99)
        
        assert abs(p50 - 49.5) < 1  # Median should be around 49.5
        assert p95 > p50  # 95th percentile should be higher than median
        assert p99 > p95  # 99th percentile should be highest
    
    @pytest.mark.asyncio
    async def test_get_metric_trends(self, metrics_aggregator):
        """Test metric trend analysis"""
        # Create trending data (increasing values over time)
        base_time = datetime.now() - timedelta(hours=1)
        
        for i in range(10):
            metric = MetricPoint(
                metric_type=MetricType.CPU_USAGE,
                value=50.0 + i * 5.0,  # Increasing trend
                timestamp=base_time + timedelta(minutes=i * 6),
                tags={"host": "test"}
            )
            await metrics_aggregator.record_metric(metric)
        
        # Analyze trend
        trend = await metrics_aggregator.get_metric_trends(
            MetricType.CPU_USAGE,
            timedelta(hours=1)
        )
        
        assert isinstance(trend, MetricTrend)
        assert trend.direction == "increasing"
        assert trend.change_rate > 0
        assert trend.confidence > 0
    
    @pytest.mark.asyncio
    async def test_get_correlation_analysis(self, metrics_aggregator):
        """Test correlation analysis between metrics"""
        base_time = datetime.now() - timedelta(hours=1)
        
        # Create correlated metrics (CPU and memory usage)
        for i in range(20):
            cpu_value = 50.0 + i * 2.0
            memory_value = 40.0 + i * 1.5  # Positively correlated
            
            timestamp = base_time + timedelta(minutes=i * 3)
            
            await metrics_aggregator.record_metric(MetricPoint(
                MetricType.CPU_USAGE, cpu_value, timestamp, {"host": "test"}
            ))
            await metrics_aggregator.record_metric(MetricPoint(
                MetricType.MEMORY_USAGE, memory_value, timestamp, {"host": "test"}
            ))
        
        # Analyze correlation
        correlations = await metrics_aggregator.get_correlation_analysis(
            [(MetricType.CPU_USAGE, MetricType.MEMORY_USAGE)],
            timedelta(hours=1)
        )
        
        correlation_key = f"{MetricType.CPU_USAGE.value}:{MetricType.MEMORY_USAGE.value}"
        assert correlation_key in correlations
        assert correlations[correlation_key] > 0.8  # Should be strongly correlated
    
    @pytest.mark.asyncio
    async def test_get_top_metrics(self, metrics_aggregator):
        """Test getting top metrics by group"""
        base_time = datetime.now()
        
        # Create metrics for different agents
        agents_data = [
            ("agent1", 100.0),
            ("agent2", 150.0),
            ("agent3", 75.0),
            ("agent1", 110.0),
            ("agent2", 160.0)
        ]
        
        for agent_id, response_time in agents_data:
            await metrics_aggregator.record_metric(MetricPoint(
                MetricType.AGENT_RESPONSE_TIME,
                response_time,
                base_time,
                {"agent_id": agent_id}
            ))
        
        # Get top agents by average response time
        top_metrics = await metrics_aggregator.get_top_metrics(
            MetricType.AGENT_RESPONSE_TIME,
            AggregationType.AVERAGE,
            timedelta(hours=1),
            group_by="agent_id",
            limit=3
        )
        
        assert len(top_metrics) == 3
        # Should be sorted by value (descending)
        assert top_metrics[0]["agent_id"] == "agent2"  # Highest average
        assert top_metrics[1]["agent_id"] == "agent1"
        assert top_metrics[2]["agent_id"] == "agent3"  # Lowest average
    
    @pytest.mark.asyncio
    async def test_subscribe_to_metric(self, metrics_aggregator):
        """Test subscribing to metric updates"""
        # Subscribe to CPU usage metrics
        queue = await metrics_aggregator.subscribe_to_metric(MetricType.CPU_USAGE)
        
        # Record a CPU metric
        metric = MetricPoint(
            MetricType.CPU_USAGE,
            75.0,
            datetime.now(),
            {"host": "test"}
        )
        
        await metrics_aggregator.record_metric(metric)
        
        # Check that subscriber received the metric
        try:
            received_metric = await asyncio.wait_for(queue.get(), timeout=1.0)
            assert received_metric == metric
        except asyncio.TimeoutError:
            pytest.fail("Subscriber did not receive metric within timeout")
    
    def test_is_anomaly_value(self, metrics_aggregator):
        """Test anomaly detection"""
        # Set up baseline stats
        metrics_aggregator.baseline_stats["cpu_usage:"] = {
            "mean": 50.0,
            "std": 10.0
        }
        
        # Normal value should not be anomaly
        assert not metrics_aggregator._is_anomaly_value(
            MetricType.CPU_USAGE, 55.0, {}
        )
        
        # Value far from mean should be anomaly
        assert metrics_aggregator._is_anomaly_value(
            MetricType.CPU_USAGE, 100.0, {}  # 5 standard deviations away
        )
    
    @pytest.mark.asyncio
    async def test_update_baselines(self, metrics_aggregator):
        """Test baseline statistics update"""
        base_time = datetime.now() - timedelta(hours=1)
        
        # Add metrics for baseline calculation
        values = [45.0, 50.0, 55.0, 48.0, 52.0] * 4  # 20 values
        for i, value in enumerate(values):
            await metrics_aggregator.record_metric(MetricPoint(
                MetricType.CPU_USAGE,
                value,
                base_time + timedelta(minutes=i * 3),
                {"host": "test"}
            ))
        
        # Update baselines
        await metrics_aggregator.update_baselines()
        
        # Check that baseline was created
        baseline_key = "cpu_usage:{\"host\":\"test\"}"
        assert baseline_key in metrics_aggregator.baseline_stats
        
        baseline = metrics_aggregator.baseline_stats[baseline_key]
        assert "mean" in baseline
        assert "std" in baseline
        assert baseline["sample_count"] == 20
    
    @pytest.mark.asyncio
    async def test_get_health_score(self, metrics_aggregator):
        """Test health score calculation"""
        base_time = datetime.now()
        
        # Add good metrics
        good_metrics = [
            (MetricType.WORKFLOW_SUCCESS_RATE, 0.95),
            (MetricType.ERROR_RATE, 0.02),
            (MetricType.AGENT_RESPONSE_TIME, 500.0),
            (MetricType.CPU_USAGE, 60.0),
            (MetricType.MEMORY_USAGE, 50.0)
        ]
        
        for metric_type, value in good_metrics:
            await metrics_aggregator.record_metric(MetricPoint(
                metric_type, value, base_time, {}
            ))
        
        # Calculate health score
        health = await metrics_aggregator.get_health_score()
        
        assert "score" in health
        assert "status" in health
        assert "components" in health
        assert "metrics" in health
        
        assert 0 <= health["score"] <= 1
        assert health["status"] in ["excellent", "good", "fair", "poor"]
    
    def test_serialize_tags(self, metrics_aggregator):
        """Test tag serialization"""
        tags = {"host": "server1", "env": "prod", "region": "us-east"}
        serialized = metrics_aggregator._serialize_tags(tags)
        
        # Should be consistent
        assert serialized == metrics_aggregator._serialize_tags(tags)
        
        # Empty tags should return empty string
        assert metrics_aggregator._serialize_tags({}) == ""
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, metrics_aggregator, sample_metric_points):
        """Test aggregation cache functionality"""
        # Add sample metrics
        for metric in sample_metric_points:
            await metrics_aggregator.record_metric(metric)
        
        # First call should compute and cache
        result1 = await metrics_aggregator.aggregate_metrics(
            MetricType.WORKFLOW_DURATION,
            AggregationType.AVERAGE,
            timedelta(hours=1)
        )
        
        # Second call should use cache
        result2 = await metrics_aggregator.aggregate_metrics(
            MetricType.WORKFLOW_DURATION,
            AggregationType.AVERAGE,
            timedelta(hours=1)
        )
        
        assert result1.value == result2.value
        assert result1.sample_count == result2.sample_count


@pytest.mark.asyncio
class TestAsyncMetricsAggregator:
    """Async test cases for MetricsAggregator"""
    
    async def test_concurrent_metric_recording(self, metrics_aggregator):
        """Test concurrent metric recording"""
        base_time = datetime.now()
        
        # Create metrics concurrently
        tasks = []
        for i in range(100):
            metric = MetricPoint(
                MetricType.CPU_USAGE,
                50.0 + i,
                base_time + timedelta(seconds=i),
                {"host": f"host{i % 5}"}
            )
            tasks.append(metrics_aggregator.record_metric(metric))
        
        await asyncio.gather(*tasks)
        
        assert len(metrics_aggregator.metrics_buffer) == 100
    
    async def test_performance_with_large_dataset(self, metrics_aggregator):
        """Test performance with large number of metrics"""
        base_time = datetime.now() - timedelta(hours=1)
        
        # Add large number of metrics
        metrics = []
        for i in range(10000):
            metric = MetricPoint(
                MetricType.CPU_USAGE,
                50.0 + (i % 50),  # Values from 50 to 99
                base_time + timedelta(seconds=i),
                {"host": f"host{i % 10}"}
            )
            metrics.append(metric)
        
        # Record all metrics
        for metric in metrics:
            await metrics_aggregator.record_metric(metric)
        
        # Test aggregation performance
        start_time = datetime.now()
        result = await metrics_aggregator.aggregate_metrics(
            MetricType.CPU_USAGE,
            AggregationType.AVERAGE,
            timedelta(hours=1)
        )
        aggregation_time = (datetime.now() - start_time).total_seconds()
        
        assert aggregation_time < 2.0  # Should complete within 2 seconds
        assert result.sample_count == 10000
    
    async def test_metric_stream_cleanup(self, metrics_aggregator):
        """Test that metric streams are properly cleaned up"""
        # Subscribe to metrics
        queue = await metrics_aggregator.subscribe_to_metric(MetricType.CPU_USAGE)
        
        # Record many metrics to test stream size limiting
        for i in range(1500):  # More than the 1000 limit
            await metrics_aggregator.record_metric(MetricPoint(
                MetricType.CPU_USAGE,
                50.0,
                datetime.now(),
                {}
            ))
        
        # Check that stream was limited
        stream_key = f"{MetricType.CPU_USAGE.value}:"
        stream = metrics_aggregator.metric_streams[stream_key]
        assert len(stream) == 1000  # Should be limited to 1000