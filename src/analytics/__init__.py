"""
Analytics package for Shepherd - Phase 10 Implementation

This package provides advanced analytics capabilities including:
- Agent collaboration pattern analysis
- Predictive insights based on historical data
- Performance metrics and trend analysis
- Custom dashboard data generation
- Export functionality for reports and visualizations

Components:
- collaboration_analyzer: Analyzes agent interaction patterns
- predictive_engine: Generates insights and predictions
- metrics_aggregator: Collects and aggregates performance data
- dashboard_engine: Powers custom dashboards
- export_manager: Handles data export in various formats
"""

from .collaboration_analyzer import CollaborationAnalyzer
from .predictive_engine import PredictiveEngine
from .metrics_aggregator import MetricsAggregator
from .dashboard_engine import DashboardEngine
from .export_manager import ExportManager

__all__ = [
    'CollaborationAnalyzer',
    'PredictiveEngine', 
    'MetricsAggregator',
    'DashboardEngine',
    'ExportManager'
]