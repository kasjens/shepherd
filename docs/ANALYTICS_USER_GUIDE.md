# Analytics User Guide - Shepherd Project

**Shepherd Advanced Analytics and Reporting System**  
*Phase 10 Implementation - Complete Analytics Suite*

## Overview

Shepherd's Advanced Analytics system provides comprehensive insights into agent collaboration patterns, workflow performance, and system optimization. This guide covers all analytics features, dashboards, predictive insights, and export capabilities.

## 🚀 Quick Start

### Accessing Analytics

1. **GUI Access**: Navigate to the Analytics panel in the main Shepherd GUI
2. **API Access**: Use REST endpoints at `http://localhost:8000/api/analytics/`
3. **WebSocket Streaming**: Connect to `ws://localhost:8000/ws/analytics` for real-time data

### Basic Analytics Workflow

1. **Start Shepherd**: `./scripts/start.sh --gui`
2. **Run some workflows** to generate data
3. **Open Analytics Dashboard** in the GUI
4. **Configure widgets** and view insights
5. **Export reports** in your preferred format

## 📊 Analytics Components

### 1. CollaborationAnalyzer

**Purpose**: Analyze agent interaction patterns and collaboration effectiveness

**Key Features**:
- **Network Topology Analysis**: Visualize agent communication networks
- **Collaboration Metrics**: Measure collaboration efficiency and patterns
- **Interaction Patterns**: Identify successful collaboration strategies
- **Team Performance**: Track multi-agent team effectiveness

**Usage Example**:
```python
# Via API
GET /api/analytics/collaboration/network-topology
GET /api/analytics/collaboration/patterns?timeframe=7d
GET /api/analytics/collaboration/metrics?agent_id=research_agent
```

### 2. PredictiveEngine

**Purpose**: Machine learning predictions for workflow optimization

**Prediction Types**:
1. **Workflow Success**: Predict likely success rate before execution
2. **Performance Metrics**: Estimate execution time and resource usage
3. **Resource Usage**: Predict CPU, memory, and network requirements
4. **Optimal Patterns**: Suggest best workflow patterns for tasks
5. **Agent Selection**: Recommend optimal agent combinations
6. **Quality Scores**: Predict output quality metrics

**Usage Example**:
```python
# Get workflow success prediction
POST /api/analytics/predictions/workflow-success
{
  "prompt": "Analyze security vulnerabilities in codebase",
  "context": {"complexity": 0.8, "project_size": "large"},
  "preferred_pattern": "hierarchical"
}

# Response
{
  "success_probability": 0.87,
  "confidence": 0.92,
  "estimated_duration": 1800,
  "recommended_agents": ["security_specialist", "code_analyst", "report_writer"]
}
```

### 3. MetricsAggregator

**Purpose**: Real-time metrics collection and trend analysis

**Metrics Categories**:
- **Performance Metrics**: Execution times, success rates, resource usage
- **Agent Metrics**: Individual agent performance and efficiency
- **Workflow Metrics**: Pattern effectiveness and optimization opportunities
- **System Metrics**: Overall system health and capacity
- **Learning Metrics**: Learning system performance and improvement rates

**Key Features**:
- **Trend Analysis**: Historical performance trends
- **Anomaly Detection**: Automatic detection of performance issues
- **Real-time Monitoring**: Live system health monitoring
- **Threshold Alerts**: Configurable performance alerts

### 4. DashboardEngine

**Purpose**: Customizable analytics dashboards with real-time streaming

**Widget Types**:
1. **Line Charts**: Performance trends over time
2. **Bar Charts**: Comparative metrics across agents/workflows
3. **Pie Charts**: Distribution analysis (agent usage, pattern distribution)
4. **Gauge Charts**: Current performance levels and thresholds
5. **Table Widgets**: Detailed tabular data with sorting/filtering
6. **Network Graphs**: Agent collaboration network visualization
7. **Heatmaps**: Activity patterns and performance matrices
8. **Progress Bars**: Goal tracking and completion rates
9. **Status Indicators**: System health and alert status

**Dashboard Configuration**:
```json
{
  "dashboard_id": "main_analytics",
  "title": "Shepherd Analytics Overview",
  "layout": "grid",
  "widgets": [
    {
      "id": "performance_trend",
      "type": "line_chart",
      "title": "Workflow Performance Trend",
      "data_source": "workflow_metrics",
      "timeframe": "7d",
      "refresh_interval": 30
    },
    {
      "id": "agent_distribution",
      "type": "pie_chart",
      "title": "Agent Usage Distribution",
      "data_source": "agent_metrics",
      "refresh_interval": 60
    }
  ]
}
```

### 5. ExportManager

**Purpose**: Multi-format data export and reporting

**Supported Formats**:
- **PDF**: Professional reports with charts and analysis
- **CSV**: Tabular data for spreadsheet analysis
- **JSON**: Structured data for programmatic use
- **Excel**: Advanced spreadsheet with multiple sheets
- **HTML**: Web-viewable reports with interactive elements
- **Markdown**: Documentation-friendly format

**Export Features**:
- **Scheduled Exports**: Automatic report generation
- **Custom Templates**: Branded report templates
- **Data Filtering**: Export specific time ranges or metrics
- **Batch Exports**: Multiple format generation
- **Email Integration**: Automatic report distribution

## 🎛️ Dashboard Usage

### Creating Custom Dashboards

1. **Access Dashboard Manager**:
   - GUI: Analytics → Dashboard Manager
   - API: `POST /api/analytics/dashboards`

2. **Configure Layout**:
   ```json
   {
     "name": "My Custom Dashboard",
     "layout": "grid",
     "columns": 3,
     "refresh_interval": 30
   }
   ```

3. **Add Widgets**:
   - Drag and drop from widget library
   - Configure data sources and parameters
   - Set refresh intervals and filters

4. **Save and Share**:
   - Save dashboard configuration
   - Share with team members
   - Export dashboard as template

### Real-time Streaming

**WebSocket Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/analytics/dashboard/main_analytics');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  if (update.type === 'widget_update') {
    updateWidget(update.widget_id, update.data);
  }
};
```

**Streaming Data Types**:
- Performance metrics updates
- Agent status changes
- Workflow completion events
- System alerts and warnings
- Learning progress updates

## 🔮 Predictive Analytics

### Workflow Success Prediction

**Use Case**: Predict workflow success before execution

**Process**:
1. Submit workflow description and context
2. System analyzes similar historical workflows
3. ML model predicts success probability
4. Recommendations provided for optimization

**Example Usage**:
```bash
curl -X POST http://localhost:8000/api/analytics/predictions/workflow-success \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create comprehensive test suite for authentication module",
    "context": {"codebase_size": "medium", "complexity": 0.7},
    "agent_preferences": ["technical", "quality_assurance"]
  }'
```

### Performance Optimization

**Predictive Insights**:
- **Bottleneck Prediction**: Identify potential performance bottlenecks
- **Resource Planning**: Predict resource requirements
- **Agent Optimization**: Suggest optimal agent configurations
- **Pattern Recommendations**: Recommend workflow patterns

### Learning Enhancement

**ML-Driven Improvements**:
- **Pattern Recognition**: Identify successful patterns automatically
- **Anomaly Detection**: Detect unusual patterns or failures
- **Adaptation Suggestions**: Recommend system adaptations
- **Performance Forecasting**: Predict future performance trends

## 📈 Performance Monitoring

### Real-time Metrics

**System Health Dashboard**:
- CPU, Memory, Network usage
- Active workflow count
- Agent performance metrics
- Error rates and response times

**Alert Configuration**:
```json
{
  "alert_rules": [
    {
      "name": "High CPU Usage",
      "metric": "system.cpu_usage",
      "threshold": 80,
      "condition": "greater_than",
      "duration": "5m",
      "severity": "warning"
    },
    {
      "name": "Workflow Failure Rate",
      "metric": "workflow.failure_rate",
      "threshold": 10,
      "condition": "greater_than",
      "duration": "10m",
      "severity": "critical"
    }
  ]
}
```

### Historical Analysis

**Trend Analysis**:
- Performance trends over time
- Seasonal patterns in usage
- Improvement tracking
- Capacity planning insights

**Comparative Analysis**:
- Agent performance comparison
- Workflow pattern effectiveness
- Before/after optimization results
- A/B testing results

## 📤 Export and Reporting

### Report Generation

**Standard Reports**:
1. **Weekly Performance Report**: Overall system performance summary
2. **Agent Efficiency Report**: Individual agent performance analysis
3. **Collaboration Analysis**: Team collaboration effectiveness
4. **Learning Progress Report**: System learning and improvement tracking
5. **Resource Usage Report**: System resource utilization analysis

**Custom Report Creation**:
```python
# Via API
POST /api/analytics/reports/generate
{
  "template": "custom",
  "title": "Monthly Analytics Summary",
  "sections": [
    "performance_overview",
    "agent_analysis",
    "learning_progress",
    "predictions"
  ],
  "timeframe": "30d",
  "format": "pdf",
  "include_charts": true
}
```

### Automated Reporting

**Scheduled Reports**:
- Daily system health reports
- Weekly performance summaries
- Monthly analytical insights
- Quarterly trend analysis

**Distribution Options**:
- Email delivery
- File system export
- Cloud storage upload
- Integration with external systems

## 🔧 Configuration and Setup

### Analytics Configuration

**Environment Variables**:
```bash
# Analytics settings
ANALYTICS_ENABLED=true
ANALYTICS_RETENTION_DAYS=90
ANALYTICS_SAMPLING_RATE=1.0
DASHBOARD_REFRESH_INTERVAL=30

# Export settings
EXPORT_MAX_FILE_SIZE=100MB
EXPORT_TEMP_DIR=/tmp/shepherd-exports
EXPORT_COMPRESSION=true

# Prediction settings
PREDICTION_MODEL_PATH=/data/models/
PREDICTION_CONFIDENCE_THRESHOLD=0.7
PREDICTION_CACHE_TTL=3600
```

### Database Setup

**Analytics Tables**:
- `analytics_metrics`: Time-series performance data
- `analytics_predictions`: ML prediction results
- `analytics_dashboards`: Dashboard configurations
- `analytics_exports`: Export job tracking

### Performance Optimization

**Recommendations**:
- Enable data compression for large datasets
- Configure appropriate retention policies
- Use indexed queries for fast retrieval
- Implement data aggregation for historical analysis

## 🎯 Best Practices

### Dashboard Design

1. **Keep It Simple**: Focus on key metrics
2. **Use Appropriate Visualizations**: Match chart types to data
3. **Configure Refresh Rates**: Balance freshness with performance
4. **Group Related Metrics**: Logical widget organization
5. **Set Meaningful Alerts**: Avoid alert fatigue

### Analytics Usage

1. **Regular Monitoring**: Check analytics regularly for insights
2. **Historical Analysis**: Use trends for improvement planning
3. **Predictive Planning**: Leverage predictions for resource planning
4. **Collaborative Review**: Share insights with team members
5. **Continuous Improvement**: Act on analytics insights

### Export and Reporting

1. **Choose Appropriate Formats**: Match format to use case
2. **Schedule Regular Reports**: Automate routine reporting
3. **Customize Templates**: Brand reports appropriately
4. **Filter Relevant Data**: Focus on actionable insights
5. **Archive Historical Data**: Maintain analytics history

## 🐛 Troubleshooting

### Common Issues

**Analytics Not Loading**:
- Check if analytics service is running
- Verify database connectivity
- Review configuration settings
- Check log files for errors

**Dashboard Performance Issues**:
- Reduce refresh intervals
- Limit widget count per dashboard
- Optimize data queries
- Enable data caching

**Export Failures**:
- Check disk space availability
- Verify export permissions
- Review file size limits
- Monitor export queue status

### Performance Optimization

**Slow Queries**:
- Add database indexes
- Implement data aggregation
- Use time-based partitioning
- Enable query caching

**Memory Issues**:
- Adjust retention policies
- Implement data compression
- Optimize widget queries
- Monitor memory usage

## 📚 API Reference Summary

### Core Endpoints

**Analytics Data**:
- `GET /api/analytics/metrics` - Retrieve system metrics
- `GET /api/analytics/trends` - Get performance trends
- `POST /api/analytics/query` - Custom analytics queries

**Predictions**:
- `POST /api/analytics/predictions/workflow-success` - Workflow success prediction
- `POST /api/analytics/predictions/performance` - Performance prediction
- `GET /api/analytics/predictions/history` - Prediction accuracy tracking

**Dashboards**:
- `GET /api/analytics/dashboards` - List all dashboards
- `POST /api/analytics/dashboards` - Create new dashboard
- `PUT /api/analytics/dashboards/{id}` - Update dashboard
- `DELETE /api/analytics/dashboards/{id}` - Delete dashboard

**Exports**:
- `POST /api/analytics/exports` - Generate export
- `GET /api/analytics/exports/{id}` - Check export status
- `GET /api/analytics/exports/{id}/download` - Download export file

### WebSocket Endpoints

**Real-time Streaming**:
- `ws://localhost:8000/ws/analytics` - General analytics stream
- `ws://localhost:8000/ws/analytics/dashboard/{id}` - Dashboard-specific stream
- `ws://localhost:8000/ws/analytics/alerts` - Alert notifications stream

## 🎉 Conclusion

Shepherd's Advanced Analytics system provides comprehensive insights into your workflow orchestration performance. Use this guide to:

- Set up custom dashboards for your specific needs
- Leverage predictive analytics for optimization
- Generate professional reports for stakeholders
- Monitor system performance in real-time
- Make data-driven decisions for improvements

For additional support or advanced configuration, refer to the API documentation or contact the development team.

---

**Next Steps**:
1. Explore the analytics dashboard in the GUI
2. Create your first custom dashboard
3. Set up automated reporting
4. Experiment with predictive analytics
5. Share insights with your team

**Remember**: Analytics data becomes more valuable over time as the system learns patterns and builds historical baselines. Start collecting data early and review insights regularly for continuous improvement.