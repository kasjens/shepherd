"""
Metrics Aggregator - Performance Data Collection and Analysis

This module aggregates performance metrics from various sources:
- Workflow execution metrics
- Agent performance data
- System resource utilization
- Error and failure rates
- Time-series analysis
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics collected"""
    WORKFLOW_DURATION = "workflow_duration"
    WORKFLOW_SUCCESS_RATE = "workflow_success_rate"
    AGENT_TASK_COUNT = "agent_task_count"
    AGENT_RESPONSE_TIME = "agent_response_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    QUEUE_LENGTH = "queue_length"
    COLLABORATION_SCORE = "collaboration_score"


class AggregationType(Enum):
    """Types of aggregations available"""
    AVERAGE = "average"
    SUM = "sum"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    PERCENTILE_50 = "p50"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    RATE = "rate"
    COUNT = "count"


@dataclass
class MetricPoint:
    """Single metric data point"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedMetric:
    """Aggregated metric result"""
    metric_type: MetricType
    aggregation_type: AggregationType
    value: float
    start_time: datetime
    end_time: datetime
    sample_count: int
    tags: Dict[str, str] = field(default_factory=dict)
    percentiles: Optional[Dict[str, float]] = None


@dataclass
class MetricTrend:
    """Trend analysis for a metric"""
    metric_type: MetricType
    direction: str  # increasing, decreasing, stable
    change_rate: float  # percentage change
    forecast_value: Optional[float] = None
    confidence: float = 0.0
    anomalies: List[datetime] = field(default_factory=list)


class MetricsAggregator:
    """
    Collects, aggregates, and analyzes performance metrics
    from across the Shepherd system.
    """
    
    def __init__(self, shared_context):
        self.shared_context = shared_context
        
        # Metric storage (in-memory for Phase 10)
        self.metrics_buffer: deque = deque(maxlen=100000)
        self.aggregation_cache: Dict[str, Any] = {}
        self.cache_ttl = 60  # seconds
        
        # Real-time metric streams
        self.metric_streams: Dict[str, List[MetricPoint]] = defaultdict(list)
        self.stream_subscribers: Dict[str, List[asyncio.Queue]] = defaultdict(list)
        
        # Anomaly detection
        self.baseline_stats: Dict[str, Dict[str, float]] = {}
        self.anomaly_threshold = 3.0  # standard deviations
    
    async def record_metric(self, metric: MetricPoint) -> None:
        """
        Record a new metric data point
        
        Args:
            metric: MetricPoint to record
        """
        # Add to buffer
        self.metrics_buffer.append(metric)
        
        # Add to stream
        stream_key = f"{metric.metric_type.value}:{self._serialize_tags(metric.tags)}"
        self.metric_streams[stream_key].append(metric)
        
        # Limit stream size
        if len(self.metric_streams[stream_key]) > 1000:
            self.metric_streams[stream_key] = self.metric_streams[stream_key][-1000:]
        
        # Notify subscribers
        await self._notify_subscribers(stream_key, metric)
        
        # Store in shared context for persistence
        await self.shared_context.store(
            f"metric_{metric.timestamp.isoformat()}_{metric.metric_type.value}",
            {
                'type': metric.metric_type.value,
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat(),
                'tags': metric.tags,
                'metadata': metric.metadata
            }
        )
        
        # Check for anomalies
        if await self._is_anomaly(metric):
            await self._handle_anomaly(metric)
    
    async def record_workflow_metrics(self, workflow_result: Dict[str, Any]) -> None:
        """
        Record metrics from a workflow execution
        
        Args:
            workflow_result: Workflow execution result
        """
        timestamp = datetime.now()
        
        # Duration metric
        if 'duration' in workflow_result:
            await self.record_metric(MetricPoint(
                metric_type=MetricType.WORKFLOW_DURATION,
                value=workflow_result['duration'],
                timestamp=timestamp,
                tags={
                    'workflow_id': workflow_result.get('workflow_id', 'unknown'),
                    'pattern': workflow_result.get('pattern', 'unknown')
                }
            ))
        
        # Success metric
        success = 1.0 if workflow_result.get('success', False) else 0.0
        await self.record_metric(MetricPoint(
            metric_type=MetricType.WORKFLOW_SUCCESS_RATE,
            value=success,
            timestamp=timestamp,
            tags={
                'workflow_id': workflow_result.get('workflow_id', 'unknown'),
                'pattern': workflow_result.get('pattern', 'unknown')
            }
        ))
        
        # Agent metrics
        for agent_result in workflow_result.get('agent_results', []):
            await self.record_metric(MetricPoint(
                metric_type=MetricType.AGENT_RESPONSE_TIME,
                value=agent_result.get('response_time', 0),
                timestamp=timestamp,
                tags={
                    'agent_id': agent_result.get('agent_id', 'unknown'),
                    'agent_type': agent_result.get('agent_type', 'unknown')
                }
            ))
    
    async def record_system_metrics(self, system_stats: Dict[str, float]) -> None:
        """
        Record system-level metrics
        
        Args:
            system_stats: Dictionary of system statistics
        """
        timestamp = datetime.now()
        
        # CPU usage
        if 'cpu_percent' in system_stats:
            await self.record_metric(MetricPoint(
                metric_type=MetricType.CPU_USAGE,
                value=system_stats['cpu_percent'],
                timestamp=timestamp,
                tags={'host': system_stats.get('host', 'localhost')}
            ))
        
        # Memory usage
        if 'memory_percent' in system_stats:
            await self.record_metric(MetricPoint(
                metric_type=MetricType.MEMORY_USAGE,
                value=system_stats['memory_percent'],
                timestamp=timestamp,
                tags={'host': system_stats.get('host', 'localhost')}
            ))
    
    async def aggregate_metrics(self,
                              metric_type: MetricType,
                              aggregation_type: AggregationType,
                              time_window: timedelta,
                              tags: Optional[Dict[str, str]] = None) -> AggregatedMetric:
        """
        Aggregate metrics over a time window
        
        Args:
            metric_type: Type of metric to aggregate
            aggregation_type: How to aggregate (avg, sum, etc.)
            time_window: Time window for aggregation
            tags: Optional tags to filter by
            
        Returns:
            AggregatedMetric with results
        """
        # Check cache
        cache_key = f"{metric_type.value}:{aggregation_type.value}:{time_window.total_seconds()}:{self._serialize_tags(tags or {})}"
        
        if cache_key in self.aggregation_cache:
            cache_time, cached_result = self.aggregation_cache[cache_key]
            if (datetime.now() - cache_time).seconds < self.cache_ttl:
                return cached_result
        
        # Filter metrics
        end_time = datetime.now()
        start_time = end_time - time_window
        
        filtered_metrics = []
        for metric in self.metrics_buffer:
            if (metric.metric_type == metric_type and 
                start_time <= metric.timestamp <= end_time):
                
                # Check tags if specified
                if tags:
                    if all(metric.tags.get(k) == v for k, v in tags.items()):
                        filtered_metrics.append(metric)
                else:
                    filtered_metrics.append(metric)
        
        if not filtered_metrics:
            return AggregatedMetric(
                metric_type=metric_type,
                aggregation_type=aggregation_type,
                value=0.0,
                start_time=start_time,
                end_time=end_time,
                sample_count=0,
                tags=tags or {}
            )
        
        # Calculate aggregation
        values = [m.value for m in filtered_metrics]
        aggregated_value = self._calculate_aggregation(values, aggregation_type)
        
        # Calculate percentiles if needed
        percentiles = None
        if aggregation_type in [AggregationType.PERCENTILE_50, AggregationType.PERCENTILE_95, AggregationType.PERCENTILE_99]:
            percentiles = {
                'p50': np.percentile(values, 50),
                'p95': np.percentile(values, 95),
                'p99': np.percentile(values, 99)
            }
        
        result = AggregatedMetric(
            metric_type=metric_type,
            aggregation_type=aggregation_type,
            value=aggregated_value,
            start_time=start_time,
            end_time=end_time,
            sample_count=len(filtered_metrics),
            tags=tags or {},
            percentiles=percentiles
        )
        
        # Cache result
        self.aggregation_cache[cache_key] = (datetime.now(), result)
        
        return result
    
    def _calculate_aggregation(self, values: List[float], aggregation_type: AggregationType) -> float:
        """Calculate aggregation value"""
        if not values:
            return 0.0
        
        if aggregation_type == AggregationType.AVERAGE:
            return np.mean(values)
        elif aggregation_type == AggregationType.SUM:
            return np.sum(values)
        elif aggregation_type == AggregationType.MINIMUM:
            return np.min(values)
        elif aggregation_type == AggregationType.MAXIMUM:
            return np.max(values)
        elif aggregation_type == AggregationType.PERCENTILE_50:
            return np.percentile(values, 50)
        elif aggregation_type == AggregationType.PERCENTILE_95:
            return np.percentile(values, 95)
        elif aggregation_type == AggregationType.PERCENTILE_99:
            return np.percentile(values, 99)
        elif aggregation_type == AggregationType.COUNT:
            return float(len(values))
        elif aggregation_type == AggregationType.RATE:
            # Rate per second
            return float(len(values)) / 60.0  # Assuming 1-minute window
        else:
            return np.mean(values)
    
    async def get_metric_trends(self,
                              metric_type: MetricType,
                              time_window: timedelta,
                              tags: Optional[Dict[str, str]] = None) -> MetricTrend:
        """
        Analyze trends for a metric
        
        Args:
            metric_type: Type of metric to analyze
            time_window: Time window for trend analysis
            tags: Optional tags to filter by
            
        Returns:
            MetricTrend with analysis results
        """
        # Get metrics for analysis
        end_time = datetime.now()
        start_time = end_time - time_window
        
        # Divide time window into buckets
        bucket_count = 10
        bucket_duration = time_window / bucket_count
        
        bucket_values = []
        anomalies = []
        
        for i in range(bucket_count):
            bucket_start = start_time + (i * bucket_duration)
            bucket_end = bucket_start + bucket_duration
            
            # Get average for this bucket
            bucket_metrics = []
            for metric in self.metrics_buffer:
                if (metric.metric_type == metric_type and
                    bucket_start <= metric.timestamp < bucket_end):
                    
                    if tags is None or all(metric.tags.get(k) == v for k, v in tags.items()):
                        bucket_metrics.append(metric.value)
            
            if bucket_metrics:
                bucket_avg = np.mean(bucket_metrics)
                bucket_values.append(bucket_avg)
                
                # Check for anomalies
                if self._is_anomaly_value(metric_type, bucket_avg, tags):
                    anomalies.append(bucket_start + bucket_duration / 2)
        
        if len(bucket_values) < 2:
            return MetricTrend(
                metric_type=metric_type,
                direction='stable',
                change_rate=0.0,
                anomalies=anomalies
            )
        
        # Calculate trend
        x = np.arange(len(bucket_values))
        slope, _ = np.polyfit(x, bucket_values, 1)
        
        # Determine direction
        avg_value = np.mean(bucket_values)
        change_rate = (slope * len(bucket_values)) / avg_value if avg_value > 0 else 0
        
        if abs(change_rate) < 0.05:  # Less than 5% change
            direction = 'stable'
        elif change_rate > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        # Simple forecast (linear extrapolation)
        forecast_value = bucket_values[-1] + slope if bucket_values else None
        
        # Confidence based on variance
        if bucket_values:
            variance = np.var(bucket_values)
            confidence = max(0.0, 1.0 - (variance / (avg_value ** 2 if avg_value > 0 else 1)))
        else:
            confidence = 0.0
        
        return MetricTrend(
            metric_type=metric_type,
            direction=direction,
            change_rate=abs(change_rate),
            forecast_value=forecast_value,
            confidence=confidence,
            anomalies=anomalies
        )
    
    async def get_correlation_analysis(self,
                                     metric_pairs: List[Tuple[MetricType, MetricType]],
                                     time_window: timedelta) -> Dict[str, float]:
        """
        Analyze correlations between metric pairs
        
        Args:
            metric_pairs: List of metric type pairs to analyze
            time_window: Time window for analysis
            
        Returns:
            Dictionary of correlation coefficients
        """
        correlations = {}
        end_time = datetime.now()
        start_time = end_time - time_window
        
        for metric1, metric2 in metric_pairs:
            # Get time-aligned values
            values1 = []
            values2 = []
            
            # Create time buckets
            bucket_duration = timedelta(minutes=1)
            current_time = start_time
            
            while current_time < end_time:
                bucket_end = current_time + bucket_duration
                
                # Get values for both metrics in this bucket
                bucket_values1 = []
                bucket_values2 = []
                
                for metric in self.metrics_buffer:
                    if current_time <= metric.timestamp < bucket_end:
                        if metric.metric_type == metric1:
                            bucket_values1.append(metric.value)
                        elif metric.metric_type == metric2:
                            bucket_values2.append(metric.value)
                
                # Only include if both metrics have values
                if bucket_values1 and bucket_values2:
                    values1.append(np.mean(bucket_values1))
                    values2.append(np.mean(bucket_values2))
                
                current_time = bucket_end
            
            # Calculate correlation
            if len(values1) >= 2 and len(values2) >= 2:
                correlation = np.corrcoef(values1, values2)[0, 1]
                correlations[f"{metric1.value}:{metric2.value}"] = correlation
            else:
                correlations[f"{metric1.value}:{metric2.value}"] = 0.0
        
        return correlations
    
    async def get_top_metrics(self,
                            metric_type: MetricType,
                            aggregation_type: AggregationType,
                            time_window: timedelta,
                            group_by: str,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top N metrics grouped by a tag
        
        Args:
            metric_type: Type of metric
            aggregation_type: How to aggregate
            time_window: Time window
            group_by: Tag to group by
            limit: Number of results
            
        Returns:
            List of top metrics with their tags
        """
        # Group metrics by tag value
        grouped_metrics = defaultdict(list)
        end_time = datetime.now()
        start_time = end_time - time_window
        
        for metric in self.metrics_buffer:
            if (metric.metric_type == metric_type and
                start_time <= metric.timestamp <= end_time and
                group_by in metric.tags):
                
                group_value = metric.tags[group_by]
                grouped_metrics[group_value].append(metric.value)
        
        # Calculate aggregations for each group
        group_aggregations = []
        
        for group_value, values in grouped_metrics.items():
            if values:
                aggregated_value = self._calculate_aggregation(values, aggregation_type)
                group_aggregations.append({
                    group_by: group_value,
                    'value': aggregated_value,
                    'sample_count': len(values),
                    'metric_type': metric_type.value,
                    'aggregation_type': aggregation_type.value
                })
        
        # Sort and limit
        group_aggregations.sort(key=lambda x: x['value'], reverse=True)
        return group_aggregations[:limit]
    
    async def subscribe_to_metric(self,
                                metric_type: MetricType,
                                tags: Optional[Dict[str, str]] = None) -> asyncio.Queue:
        """
        Subscribe to real-time metric updates
        
        Args:
            metric_type: Type of metric to subscribe to
            tags: Optional tags to filter by
            
        Returns:
            Queue that will receive metric updates
        """
        stream_key = f"{metric_type.value}:{self._serialize_tags(tags or {})}"
        
        queue = asyncio.Queue(maxsize=100)
        self.stream_subscribers[stream_key].append(queue)
        
        return queue
    
    async def _notify_subscribers(self, stream_key: str, metric: MetricPoint) -> None:
        """Notify subscribers of new metric"""
        subscribers = self.stream_subscribers.get(stream_key, [])
        
        # Remove closed queues
        active_subscribers = []
        for queue in subscribers:
            try:
                await queue.put_nowait(metric)
                active_subscribers.append(queue)
            except asyncio.QueueFull:
                # Skip if queue is full
                active_subscribers.append(queue)
            except:
                # Remove broken subscribers
                pass
        
        self.stream_subscribers[stream_key] = active_subscribers
    
    async def _is_anomaly(self, metric: MetricPoint) -> bool:
        """Check if metric is anomalous"""
        return self._is_anomaly_value(
            metric.metric_type,
            metric.value,
            metric.tags
        )
    
    def _is_anomaly_value(self,
                         metric_type: MetricType,
                         value: float,
                         tags: Optional[Dict[str, str]]) -> bool:
        """Check if a value is anomalous"""
        baseline_key = f"{metric_type.value}:{self._serialize_tags(tags or {})}"
        
        if baseline_key not in self.baseline_stats:
            # Not enough data for baseline
            return False
        
        baseline = self.baseline_stats[baseline_key]
        mean = baseline.get('mean', 0)
        std = baseline.get('std', 1)
        
        if std == 0:
            return False
        
        # Check if value is beyond threshold standard deviations
        z_score = abs(value - mean) / std
        return z_score > self.anomaly_threshold
    
    async def _handle_anomaly(self, metric: MetricPoint) -> None:
        """Handle detected anomaly"""
        logger.warning(
            f"Anomaly detected: {metric.metric_type.value} = {metric.value} "
            f"(tags: {metric.tags})"
        )
        
        # Store anomaly event
        await self.shared_context.store(
            f"anomaly_{metric.timestamp.isoformat()}",
            {
                'metric_type': metric.metric_type.value,
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat(),
                'tags': metric.tags,
                'baseline_stats': self.baseline_stats.get(
                    f"{metric.metric_type.value}:{self._serialize_tags(metric.tags)}", 
                    {}
                )
            }
        )
    
    async def update_baselines(self, time_window: timedelta = timedelta(hours=24)) -> None:
        """Update baseline statistics for anomaly detection"""
        end_time = datetime.now()
        start_time = end_time - time_window
        
        # Group metrics by type and tags
        metric_groups = defaultdict(list)
        
        for metric in self.metrics_buffer:
            if start_time <= metric.timestamp <= end_time:
                key = f"{metric.metric_type.value}:{self._serialize_tags(metric.tags)}"
                metric_groups[key].append(metric.value)
        
        # Calculate baselines
        for key, values in metric_groups.items():
            if len(values) >= 10:  # Minimum samples for baseline
                self.baseline_stats[key] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'sample_count': len(values),
                    'last_updated': datetime.now().isoformat()
                }
    
    def _serialize_tags(self, tags: Dict[str, str]) -> str:
        """Serialize tags to a consistent string format"""
        if not tags:
            return ""
        return json.dumps(sorted(tags.items()))
    
    async def get_health_score(self, time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """
        Calculate overall system health score
        
        Returns:
            Dictionary with health score and contributing factors
        """
        # Get key metrics
        success_rate = await self.aggregate_metrics(
            MetricType.WORKFLOW_SUCCESS_RATE,
            AggregationType.AVERAGE,
            time_window
        )
        
        error_rate = await self.aggregate_metrics(
            MetricType.ERROR_RATE,
            AggregationType.AVERAGE,
            time_window
        )
        
        response_time = await self.aggregate_metrics(
            MetricType.AGENT_RESPONSE_TIME,
            AggregationType.PERCENTILE_95,
            time_window
        )
        
        cpu_usage = await self.aggregate_metrics(
            MetricType.CPU_USAGE,
            AggregationType.AVERAGE,
            time_window
        )
        
        memory_usage = await self.aggregate_metrics(
            MetricType.MEMORY_USAGE,
            AggregationType.AVERAGE,
            time_window
        )
        
        # Calculate component scores
        performance_score = success_rate.value * (1 - error_rate.value)
        
        # Response time score (assuming 1000ms is baseline)
        response_score = max(0, 1 - (response_time.value / 1000))
        
        # Resource score (lower is better)
        resource_score = 1 - ((cpu_usage.value + memory_usage.value) / 200)
        
        # Overall health score (weighted average)
        health_score = (
            performance_score * 0.4 +
            response_score * 0.3 +
            resource_score * 0.3
        )
        
        # Determine health status
        if health_score >= 0.9:
            status = 'excellent'
        elif health_score >= 0.7:
            status = 'good'
        elif health_score >= 0.5:
            status = 'fair'
        else:
            status = 'poor'
        
        return {
            'score': health_score,
            'status': status,
            'components': {
                'performance': performance_score,
                'responsiveness': response_score,
                'resources': resource_score
            },
            'metrics': {
                'success_rate': success_rate.value,
                'error_rate': error_rate.value,
                'response_time_p95': response_time.value,
                'cpu_usage': cpu_usage.value,
                'memory_usage': memory_usage.value
            },
            'timestamp': datetime.now().isoformat()
        }