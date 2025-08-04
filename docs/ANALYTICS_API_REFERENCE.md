# Analytics API Reference - Shepherd Project

**Shepherd Advanced Analytics and Reporting API**  
*Phase 10 Implementation - Complete API Documentation*

## Overview

The Shepherd Analytics API provides programmatic access to all analytics features including metrics collection, predictive insights, dashboard management, and export capabilities. This reference documents all 25+ REST endpoints and WebSocket connections.

**Base URL**: `http://localhost:8000/api/analytics/`  
**WebSocket Base**: `ws://localhost:8000/ws/analytics/`

## Authentication

All API endpoints require authentication. Include the authorization header in all requests:

```http
Authorization: Bearer <your-api-token>
Content-Type: application/json
```

## Core Analytics Endpoints

### System Metrics

#### Get System Metrics
```http
GET /api/analytics/metrics
```

**Query Parameters**:
- `timeframe` (string): Time range (1h, 6h, 24h, 7d, 30d)
- `metric_types` (array): Filter by metric types
- `agents` (array): Filter by specific agents
- `include_predictions` (boolean): Include predictive data

**Response**:
```json
{
  "success": true,
  "data": {
    "system_metrics": {
      "cpu_usage": 45.2,
      "memory_usage": 67.8,
      "disk_usage": 23.1,
      "network_io": 125.4
    },
    "workflow_metrics": {
      "total_workflows": 156,
      "success_rate": 94.2,
      "avg_duration": 234.5,
      "active_workflows": 3
    },
    "agent_metrics": {
      "total_agents": 12,
      "active_agents": 8,
      "avg_efficiency": 87.3,
      "communication_events": 45
    }
  },
  "metadata": {
    "timestamp": "2025-01-15T10:30:00Z",
    "timeframe": "1h",
    "data_points": 60
  }
}
```

#### Get Performance Trends
```http
GET /api/analytics/trends
```

**Query Parameters**:
- `metric` (string, required): Metric name to analyze
- `period` (string): Aggregation period (minute, hour, day)
- `start_date` (string): ISO 8601 start date
- `end_date` (string): ISO 8601 end date

**Response**:
```json
{
  "success": true,
  "data": {
    "trend_data": [
      {
        "timestamp": "2025-01-15T09:00:00Z",
        "value": 82.3,
        "change_percent": 2.1
      },
      {
        "timestamp": "2025-01-15T10:00:00Z",
        "value": 84.1,
        "change_percent": 2.2
      }
    ],
    "summary": {
      "trend_direction": "upward",
      "average_change": 2.15,
      "volatility": "low",
      "correlation_score": 0.87
    }
  }
}
```

#### Custom Metrics Query
```http
POST /api/analytics/query
```

**Request Body**:
```json
{
  "query": {
    "select": ["workflow_success_rate", "agent_efficiency", "response_time"],
    "filters": {
      "agent_type": "technical",
      "date_range": {
        "start": "2025-01-01T00:00:00Z",
        "end": "2025-01-15T23:59:59Z"
      }
    },
    "group_by": ["agent_id", "workflow_pattern"],
    "order_by": "success_rate DESC",
    "limit": 100
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "agent_id": "tech_agent_1",
        "workflow_pattern": "hierarchical",
        "workflow_success_rate": 96.8,
        "agent_efficiency": 89.2,
        "response_time": 145.3
      }
    ],
    "total_rows": 45,
    "execution_time": 0.234
  }
}
```

## Collaboration Analytics

### Agent Collaboration Analysis

#### Get Collaboration Network
```http
GET /api/analytics/collaboration/network-topology
```

**Query Parameters**:
- `timeframe` (string): Analysis period
- `min_interactions` (integer): Minimum interaction threshold
- `include_metrics` (boolean): Include detailed metrics

**Response**:
```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": "research_agent",
        "type": "research",
        "metrics": {
          "total_interactions": 234,
          "success_rate": 92.1,
          "avg_response_time": 145.2
        }
      }
    ],
    "edges": [
      {
        "source": "research_agent",
        "target": "technical_agent",
        "weight": 45,
        "interaction_types": ["request", "response", "collaboration"],
        "success_rate": 94.7
      }
    ],
    "network_metrics": {
      "density": 0.67,
      "centralization": 0.34,
      "clustering_coefficient": 0.82
    }
  }
}
```

#### Get Collaboration Patterns
```http
GET /api/analytics/collaboration/patterns
```

**Query Parameters**:
- `pattern_type` (string): Type of pattern analysis
- `min_confidence` (float): Minimum confidence threshold
- `agents` (array): Specific agents to analyze

**Response**:
```json
{
  "success": true,
  "data": {
    "patterns": [
      {
        "pattern_id": "collab_pattern_1",
        "type": "sequential_collaboration",
        "participants": ["research_agent", "analysis_agent", "report_agent"],
        "confidence": 0.89,
        "frequency": 34,
        "success_rate": 96.2,
        "avg_duration": 342.1
      }
    ],
    "pattern_summary": {
      "total_patterns": 12,
      "avg_confidence": 0.76,
      "most_effective_pattern": "hierarchical_delegation"
    }
  }
}
```

#### Get Team Metrics
```http
GET /api/analytics/collaboration/team-metrics
```

**Response**:
```json
{
  "success": true,
  "data": {
    "team_performance": {
      "collaboration_efficiency": 87.3,
      "communication_latency": 234.5,
      "knowledge_sharing_rate": 76.2,
      "peer_review_effectiveness": 91.8
    },
    "agent_contributions": [
      {
        "agent_id": "research_agent",
        "contribution_score": 92.1,
        "collaboration_frequency": 45,
        "knowledge_shared": 23,
        "reviews_conducted": 12
      }
    ]
  }
}
```

## Predictive Analytics

### Workflow Success Prediction

#### Predict Workflow Success
```http
POST /api/analytics/predictions/workflow-success
```

**Request Body**:
```json
{
  "prompt": "Analyze security vulnerabilities in authentication module",
  "context": {
    "codebase_size": "medium",
    "complexity": 0.7,
    "domain": "security",
    "urgency": "high"
  },
  "preferred_pattern": "hierarchical",
  "agent_preferences": ["security_specialist", "code_analyst"],
  "historical_context": true
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "prediction": {
      "success_probability": 0.87,
      "confidence_interval": [0.82, 0.92],
      "confidence_score": 0.94
    },
    "performance_estimates": {
      "estimated_duration": 1847,
      "estimated_duration_range": [1234, 2456],
      "resource_requirements": {
        "cpu_usage": 0.65,
        "memory_usage": 0.23,
        "network_io": 0.15
      }
    },
    "recommendations": {
      "optimal_pattern": "hierarchical",
      "recommended_agents": [
        {
          "agent_type": "security_specialist",
          "confidence": 0.91,
          "reasoning": "High expertise in security analysis"
        },
        {
          "agent_type": "code_analyst",
          "confidence": 0.87,
          "reasoning": "Strong pattern matching for code review"
        }
      ],
      "risk_factors": [
        {
          "factor": "high_complexity",
          "impact": 0.15,
          "mitigation": "Add additional review cycles"
        }
      ]
    },
    "similar_workflows": [
      {
        "workflow_id": "wf_123",
        "similarity": 0.89,
        "outcome": "success",
        "duration": 1923
      }
    ]
  }
}
```

### Performance Prediction

#### Get Performance Forecast
```http
POST /api/analytics/predictions/performance
```

**Request Body**:
```json
{
  "prediction_type": "system_performance",
  "forecast_horizon": "7d",
  "metrics": ["cpu_usage", "workflow_success_rate", "response_time"],
  "context": {
    "expected_workload": "high",
    "seasonal_factors": true,
    "historical_data_points": 1000
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "forecasts": [
      {
        "metric": "cpu_usage",
        "predictions": [
          {
            "timestamp": "2025-01-16T12:00:00Z",
            "predicted_value": 67.2,
            "confidence_interval": [62.1, 72.3],
            "confidence": 0.86
          }
        ],
        "trend": "increasing",
        "seasonal_pattern": "detected"
      }
    ],
    "recommendations": [
      {
        "type": "capacity_planning",
        "message": "Consider scaling resources due to predicted 15% increase in CPU usage",
        "urgency": "medium",
        "impact": "high"
      }
    ]
  }
}
```

### Resource Usage Prediction

#### Predict Resource Requirements
```http
POST /api/analytics/predictions/resource-usage
```

**Request Body**:
```json
{
  "workflow_description": "Large-scale data analysis with machine learning",
  "expected_agents": 8,
  "data_size": "10GB",
  "time_constraints": "2h"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "resource_predictions": {
      "cpu_requirements": {
        "peak_usage": 0.85,
        "average_usage": 0.67,
        "duration": 7200
      },
      "memory_requirements": {
        "peak_memory": "12.5GB",
        "sustained_memory": "8.2GB",
        "memory_profile": "high_sustained"
      },
      "storage_requirements": {
        "temporary_storage": "15GB",
        "output_storage": "2.3GB",
        "cache_requirements": "5.1GB"
      },
      "network_requirements": {
        "bandwidth": "100Mbps",
        "data_transfer": "25GB",
        "api_calls": 2340
      }
    },
    "capacity_recommendations": {
      "current_capacity": "sufficient",
      "bottlenecks": ["memory_intensive_operations"],
      "scaling_recommendations": [
        {
          "resource": "memory",
          "recommendation": "increase_by_20_percent",
          "reasoning": "High memory usage predicted for ML operations"
        }
      ]
    }
  }
}
```

## Dashboard Management

### Dashboard Operations

#### List Dashboards
```http
GET /api/analytics/dashboards
```

**Query Parameters**:
- `user_id` (string): Filter by user
- `shared` (boolean): Include shared dashboards
- `template` (boolean): Include template dashboards

**Response**:
```json
{
  "success": true,
  "data": {
    "dashboards": [
      {
        "id": "dashboard_123",
        "name": "System Overview",
        "description": "Main system performance dashboard",
        "owner": "user_456",
        "created_at": "2025-01-10T14:30:00Z",
        "modified_at": "2025-01-15T09:15:00Z",
        "is_shared": true,
        "is_template": false,
        "widget_count": 8,
        "layout": "grid"
      }
    ],
    "total_count": 15,
    "user_dashboards": 8,
    "shared_dashboards": 5,
    "template_dashboards": 2
  }
}
```

#### Create Dashboard
```http
POST /api/analytics/dashboards
```

**Request Body**:
```json
{
  "name": "Custom Analytics Dashboard",
  "description": "Tailored dashboard for team performance",
  "layout": "grid",
  "columns": 3,
  "refresh_interval": 30,
  "is_shared": false,
  "widgets": [
    {
      "id": "widget_1",
      "type": "line_chart",
      "title": "Workflow Success Rate",
      "position": {"x": 0, "y": 0, "width": 1, "height": 1},
      "data_source": "workflow_metrics",
      "configuration": {
        "metric": "success_rate",
        "timeframe": "24h",
        "refresh_interval": 60
      }
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "dashboard_id": "dashboard_789",
    "message": "Dashboard created successfully",
    "url": "/analytics/dashboards/dashboard_789"
  }
}
```

#### Update Dashboard
```http
PUT /api/analytics/dashboards/{dashboard_id}
```

#### Delete Dashboard
```http
DELETE /api/analytics/dashboards/{dashboard_id}
```

#### Get Dashboard Configuration
```http
GET /api/analytics/dashboards/{dashboard_id}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "dashboard": {
      "id": "dashboard_123",
      "name": "System Overview",
      "layout": "grid",
      "widgets": [
        {
          "id": "widget_1",
          "type": "gauge_chart",
          "title": "CPU Usage",
          "data_source": "system_metrics",
          "configuration": {
            "metric": "cpu_usage",
            "threshold_warning": 70,
            "threshold_critical": 85
          }
        }
      ]
    }
  }
}
```

### Widget Management

#### Get Available Widget Types
```http
GET /api/analytics/widgets/types
```

**Response**:
```json
{
  "success": true,
  "data": {
    "widget_types": [
      {
        "type": "line_chart",
        "name": "Line Chart",
        "description": "Time-series data visualization",
        "supported_data_types": ["time_series", "metrics"],
        "configuration_options": [
          "timeframe", "metric", "aggregation", "color_scheme"
        ]
      },
      {
        "type": "network_graph",
        "name": "Network Graph",
        "description": "Relationship visualization",
        "supported_data_types": ["network", "collaboration"],
        "configuration_options": [
          "layout_algorithm", "node_size", "edge_weight", "interaction_threshold"
        ]
      }
    ]
  }
}
```

#### Update Widget Configuration
```http
PUT /api/analytics/dashboards/{dashboard_id}/widgets/{widget_id}
```

**Request Body**:
```json
{
  "configuration": {
    "timeframe": "7d",
    "refresh_interval": 120,
    "color_scheme": "professional",
    "show_legend": true
  }
}
```

## Export and Reporting

### Export Operations

#### Generate Export
```http
POST /api/analytics/exports
```

**Request Body**:
```json
{
  "export_type": "analytics_report",
  "format": "pdf",
  "template": "professional_report",
  "data_sources": [
    {
      "type": "metrics",
      "timeframe": "30d",
      "filters": {
        "agent_types": ["research", "technical"],
        "workflow_patterns": ["hierarchical", "parallel"]
      }
    },
    {
      "type": "predictions",
      "prediction_types": ["workflow_success", "performance_forecast"]
    }
  ],
  "configuration": {
    "include_charts": true,
    "include_raw_data": false,
    "compress_output": true,
    "custom_title": "Monthly Analytics Report - January 2025"
  },
  "delivery": {
    "method": "download",
    "email_recipients": ["team@company.com"],
    "schedule": null
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "export_id": "export_456",
    "status": "processing",
    "estimated_completion": "2025-01-15T10:45:00Z",
    "progress_url": "/api/analytics/exports/export_456/status"
  }
}
```

#### Check Export Status
```http
GET /api/analytics/exports/{export_id}/status
```

**Response**:
```json
{
  "success": true,
  "data": {
    "export_id": "export_456",
    "status": "completed",
    "progress": 100,
    "created_at": "2025-01-15T10:30:00Z",
    "completed_at": "2025-01-15T10:42:00Z",
    "file_info": {
      "filename": "analytics_report_2025_01.pdf",
      "size": "2.3MB",
      "format": "pdf"
    },
    "download_url": "/api/analytics/exports/export_456/download",
    "expires_at": "2025-01-22T10:42:00Z"
  }
}
```

#### Download Export
```http
GET /api/analytics/exports/{export_id}/download
```

**Response**: Binary file download with appropriate headers

#### List Exports
```http
GET /api/analytics/exports
```

**Query Parameters**:
- `status` (string): Filter by status
- `format` (string): Filter by format
- `limit` (integer): Number of results
- `offset` (integer): Pagination offset

### Scheduled Exports

#### Create Scheduled Export
```http
POST /api/analytics/exports/scheduled
```

**Request Body**:
```json
{
  "name": "Weekly Performance Report",
  "schedule": {
    "frequency": "weekly",
    "day_of_week": "monday",
    "time": "09:00:00",
    "timezone": "UTC"
  },
  "export_configuration": {
    "format": "pdf",
    "template": "weekly_summary",
    "data_sources": ["performance_metrics", "collaboration_analysis"]
  },
  "delivery": {
    "method": "email",
    "recipients": ["managers@company.com"],
    "subject": "Weekly Shepherd Analytics Report"
  }
}
```

#### List Scheduled Exports
```http
GET /api/analytics/exports/scheduled
```

#### Update Scheduled Export
```http
PUT /api/analytics/exports/scheduled/{schedule_id}
```

#### Delete Scheduled Export
```http
DELETE /api/analytics/exports/scheduled/{schedule_id}
```

## WebSocket Streaming

### Real-time Analytics Data

#### Dashboard Streaming
```
ws://localhost:8000/ws/analytics/dashboard/{dashboard_id}
```

**Connection Parameters**:
- `dashboard_id`: Target dashboard ID
- `refresh_rate`: Update frequency in seconds

**Message Types**:
```json
{
  "type": "widget_update",
  "widget_id": "widget_123",
  "data": {
    "timestamp": "2025-01-15T10:30:00Z",
    "values": [
      {"metric": "cpu_usage", "value": 67.2},
      {"metric": "memory_usage", "value": 45.8}
    ]
  }
}

{
  "type": "alert",
  "severity": "warning",
  "message": "CPU usage approaching threshold",
  "metric": "cpu_usage",
  "current_value": 82.5,
  "threshold": 85.0
}

{
  "type": "prediction_update",
  "prediction_id": "pred_789",
  "data": {
    "success_probability": 0.89,
    "confidence": 0.92,
    "updated_at": "2025-01-15T10:30:15Z"
  }
}
```

#### General Analytics Stream
```
ws://localhost:8000/ws/analytics/stream
```

**Subscription Management**:
```json
{
  "action": "subscribe",
  "streams": ["system_metrics", "collaboration_events", "predictions"],
  "filters": {
    "agent_types": ["research", "technical"],
    "metric_threshold": 0.8
  }
}

{
  "action": "unsubscribe",
  "streams": ["predictions"]
}
```

#### Collaboration Events Stream
```
ws://localhost:8000/ws/analytics/collaboration
```

**Event Types**:
```json
{
  "type": "agent_communication",
  "timestamp": "2025-01-15T10:30:00Z",
  "source_agent": "research_agent",
  "target_agent": "analysis_agent",
  "message_type": "request",
  "success": true,
  "response_time": 145
}

{
  "type": "collaboration_pattern",
  "pattern_id": "pattern_123",
  "agents": ["agent_1", "agent_2", "agent_3"],
  "pattern_type": "sequential",
  "confidence": 0.87,
  "detected_at": "2025-01-15T10:30:00Z"
}
```

## Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMETERS",
    "message": "The specified timeframe is invalid",
    "details": {
      "parameter": "timeframe",
      "provided_value": "invalid_range",
      "valid_values": ["1h", "6h", "24h", "7d", "30d"]
    }
  },
  "request_id": "req_123456789"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_PARAMETERS` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `PROCESSING_ERROR` | 500 | Internal processing error |
| `SERVICE_UNAVAILABLE` | 503 | Analytics service unavailable |

## Rate Limiting

**Rate Limits**:
- Standard endpoints: 100 requests/minute
- Export endpoints: 10 requests/minute
- WebSocket connections: 5 concurrent connections per user
- Bulk query endpoints: 20 requests/minute

**Rate Limit Headers**:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1642251600
```

## SDK and Client Libraries

### Python Client Example
```python
from shepherd_analytics import AnalyticsClient

client = AnalyticsClient(
    base_url="http://localhost:8000",
    api_token="your_api_token"
)

# Get system metrics
metrics = client.get_metrics(timeframe="24h")

# Create prediction
prediction = client.predict_workflow_success(
    prompt="Analyze code quality",
    context={"complexity": 0.7}
)

# Create dashboard
dashboard = client.create_dashboard(
    name="My Dashboard",
    widgets=[
        {"type": "line_chart", "metric": "success_rate"}
    ]
)

# Stream real-time data
for update in client.stream_metrics():
    print(f"Metric update: {update}")
```

### JavaScript Client Example
```javascript
import { AnalyticsClient } from '@shepherd/analytics-client';

const client = new AnalyticsClient({
  baseUrl: 'http://localhost:8000',
  apiToken: 'your_api_token'
});

// Get metrics
const metrics = await client.getMetrics({ timeframe: '24h' });

// WebSocket streaming
const ws = client.streamDashboard('dashboard_123');
ws.on('widget_update', (data) => {
  console.log('Widget updated:', data);
});
```

## Conclusion

This API reference provides comprehensive access to Shepherd's advanced analytics capabilities. The API supports:

- **25+ REST endpoints** for complete analytics functionality
- **Real-time WebSocket streaming** for live data updates
- **Predictive analytics** with ML-powered insights
- **Custom dashboards** with 9 widget types
- **Multi-format exports** with professional templates
- **Comprehensive collaboration analysis** with network topology
- **Performance monitoring** with trend analysis and alerts

For additional support, examples, or advanced use cases, refer to the Analytics User Guide or contact the development team.

---

**API Version**: 1.0.0  
**Last Updated**: January 15, 2025  
**Compatibility**: Shepherd Phase 10+