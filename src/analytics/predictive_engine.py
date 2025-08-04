"""
Predictive Engine - Machine Learning-based Insights and Predictions

This module provides predictive analytics capabilities including:
- Workflow success prediction
- Resource usage forecasting
- Agent performance prediction
- Anomaly detection
- Pattern-based recommendations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


class PredictionType(Enum):
    """Types of predictions available"""
    WORKFLOW_SUCCESS = "workflow_success"
    RESOURCE_USAGE = "resource_usage"
    AGENT_PERFORMANCE = "agent_performance"
    COMPLETION_TIME = "completion_time"
    BOTTLENECK_RISK = "bottleneck_risk"
    FAILURE_PROBABILITY = "failure_probability"


@dataclass
class Prediction:
    """Represents a single prediction"""
    prediction_type: PredictionType
    target_id: str  # workflow_id, agent_id, etc.
    predicted_value: Any
    confidence: float  # 0-1
    timestamp: datetime
    features_used: Dict[str, Any]
    explanation: str
    time_horizon: Optional[timedelta] = None


@dataclass
class HistoricalPattern:
    """Historical pattern for learning"""
    pattern_id: str
    pattern_type: str
    occurrences: int
    success_rate: float
    avg_duration: float
    context_features: Dict[str, Any]
    outcomes: List[Dict[str, Any]]


@dataclass
class PredictiveInsight:
    """High-level predictive insight"""
    insight_type: str
    title: str
    description: str
    confidence: float
    impact: str  # high, medium, low
    recommendations: List[str]
    supporting_data: Dict[str, Any]
    expires_at: datetime


class PredictiveEngine:
    """
    Machine learning-based predictive analytics engine that
    learns from historical data to make predictions about
    future agent and workflow performance.
    """
    
    def __init__(self, knowledge_base, pattern_learner, shared_context):
        self.knowledge_base = knowledge_base
        self.pattern_learner = pattern_learner
        self.shared_context = shared_context
        
        # Model storage
        self.models: Dict[PredictionType, Any] = {}
        self.feature_importance: Dict[PredictionType, Dict[str, float]] = {}
        self.prediction_history: deque = deque(maxlen=1000)
        
        # Performance tracking
        self.model_accuracy: Dict[PredictionType, float] = {}
        self.last_training: Dict[PredictionType, datetime] = {}
        
        # Initialize simple models
        self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize prediction models"""
        # For Phase 10, we'll use simple statistical models
        # In production, these would be replaced with proper ML models
        
        for prediction_type in PredictionType:
            self.models[prediction_type] = {
                'type': 'statistical',
                'parameters': {},
                'trained': False
            }
            self.model_accuracy[prediction_type] = 0.0
            self.feature_importance[prediction_type] = {}
    
    async def train_models(self, historical_data: Optional[List[Dict]] = None) -> Dict[str, float]:
        """
        Train or update prediction models with historical data
        
        Args:
            historical_data: Optional historical data to train on
            
        Returns:
            Dictionary of model accuracies
        """
        if historical_data is None:
            # Fetch from knowledge base
            historical_data = await self._fetch_historical_data()
        
        training_results = {}
        
        for prediction_type in PredictionType:
            logger.info(f"Training model for {prediction_type.value}")
            
            # Filter relevant data for this prediction type
            relevant_data = self._filter_data_for_prediction_type(
                historical_data, prediction_type
            )
            
            if len(relevant_data) < 10:  # Minimum data requirement
                logger.warning(f"Insufficient data for {prediction_type.value}: {len(relevant_data)} samples")
                training_results[prediction_type.value] = 0.0
                continue
            
            # Train model
            accuracy = await self._train_single_model(prediction_type, relevant_data)
            training_results[prediction_type.value] = accuracy
            
            self.model_accuracy[prediction_type] = accuracy
            self.last_training[prediction_type] = datetime.now()
            self.models[prediction_type]['trained'] = True
        
        return training_results
    
    async def _fetch_historical_data(self) -> List[Dict]:
        """Fetch historical data from knowledge base"""
        # Retrieve workflow results
        workflow_data = await self.knowledge_base.find_similar_patterns(
            "workflow_execution", "learned"
        )
        
        # Retrieve agent performance data
        agent_data = await self.knowledge_base.find_similar_patterns(
            "agent_performance", "learned"
        )
        
        # Retrieve failure patterns
        failure_data = await self.knowledge_base.find_similar_patterns(
            "failure_pattern", "failure"
        )
        
        # Combine all data
        all_data = []
        
        for data in workflow_data:
            all_data.append({
                'type': 'workflow',
                'data': data['content'],
                'metadata': data['metadata']
            })
        
        for data in agent_data:
            all_data.append({
                'type': 'agent',
                'data': data['content'],
                'metadata': data['metadata']
            })
        
        for data in failure_data:
            all_data.append({
                'type': 'failure',
                'data': data['content'],
                'metadata': data['metadata']
            })
        
        return all_data
    
    def _filter_data_for_prediction_type(self, 
                                       data: List[Dict], 
                                       prediction_type: PredictionType) -> List[Dict]:
        """Filter data relevant for specific prediction type"""
        filtered_data = []
        
        for item in data:
            if prediction_type == PredictionType.WORKFLOW_SUCCESS:
                if item['type'] == 'workflow':
                    filtered_data.append(item)
            
            elif prediction_type == PredictionType.AGENT_PERFORMANCE:
                if item['type'] == 'agent':
                    filtered_data.append(item)
            
            elif prediction_type == PredictionType.FAILURE_PROBABILITY:
                if item['type'] in ['workflow', 'failure']:
                    filtered_data.append(item)
            
            elif prediction_type == PredictionType.RESOURCE_USAGE:
                if 'resource_usage' in item.get('data', {}):
                    filtered_data.append(item)
            
            elif prediction_type == PredictionType.COMPLETION_TIME:
                if 'duration' in item.get('data', {}):
                    filtered_data.append(item)
            
            elif prediction_type == PredictionType.BOTTLENECK_RISK:
                if item['type'] in ['agent', 'workflow']:
                    filtered_data.append(item)
        
        return filtered_data
    
    async def _train_single_model(self, 
                                prediction_type: PredictionType, 
                                training_data: List[Dict]) -> float:
        """Train a single prediction model"""
        # Extract features and labels
        features, labels = self._prepare_training_data(prediction_type, training_data)
        
        if not features or not labels:
            return 0.0
        
        # For Phase 10, use simple statistical approach
        # Calculate feature statistics
        feature_stats = self._calculate_feature_statistics(features)
        label_stats = self._calculate_label_statistics(labels)
        
        # Store model parameters
        self.models[prediction_type]['parameters'] = {
            'feature_stats': feature_stats,
            'label_stats': label_stats,
            'correlation_matrix': self._calculate_correlations(features, labels)
        }
        
        # Calculate feature importance
        self.feature_importance[prediction_type] = self._calculate_feature_importance(
            features, labels
        )
        
        # Estimate accuracy using cross-validation
        accuracy = self._estimate_model_accuracy(features, labels, prediction_type)
        
        return accuracy
    
    def _prepare_training_data(self, 
                             prediction_type: PredictionType, 
                             raw_data: List[Dict]) -> Tuple[List[Dict], List[Any]]:
        """Prepare features and labels for training"""
        features = []
        labels = []
        
        for item in raw_data:
            data = item.get('data', {})
            
            # Extract features based on prediction type
            if prediction_type == PredictionType.WORKFLOW_SUCCESS:
                feature_dict = {
                    'complexity': data.get('complexity', 0.5),
                    'agent_count': data.get('agent_count', 1),
                    'pattern_type': data.get('pattern_type', 'unknown'),
                    'urgency': data.get('urgency', 0.5)
                }
                label = 1.0 if data.get('success', False) else 0.0
                
            elif prediction_type == PredictionType.COMPLETION_TIME:
                feature_dict = {
                    'task_count': data.get('task_count', 1),
                    'complexity': data.get('complexity', 0.5),
                    'agent_count': data.get('agent_count', 1),
                    'pattern_type': data.get('pattern_type', 'sequential')
                }
                label = data.get('duration', 0.0)
                
            elif prediction_type == PredictionType.AGENT_PERFORMANCE:
                feature_dict = {
                    'agent_type': data.get('agent_type', 'unknown'),
                    'task_complexity': data.get('task_complexity', 0.5),
                    'workload': data.get('workload', 0.5),
                    'collaboration_count': data.get('collaboration_count', 0)
                }
                label = data.get('performance_score', 0.5)
                
            else:
                continue
            
            features.append(feature_dict)
            labels.append(label)
        
        return features, labels
    
    def _calculate_feature_statistics(self, features: List[Dict]) -> Dict[str, Dict]:
        """Calculate statistics for each feature"""
        stats = defaultdict(lambda: {'mean': 0, 'std': 0, 'min': 0, 'max': 0})
        
        # Group values by feature name
        feature_values = defaultdict(list)
        for feature_dict in features:
            for key, value in feature_dict.items():
                if isinstance(value, (int, float)):
                    feature_values[key].append(value)
        
        # Calculate statistics
        for feature_name, values in feature_values.items():
            if values:
                stats[feature_name] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values)
                }
        
        return dict(stats)
    
    def _calculate_label_statistics(self, labels: List[Any]) -> Dict[str, float]:
        """Calculate statistics for labels"""
        numeric_labels = [l for l in labels if isinstance(l, (int, float))]
        
        if not numeric_labels:
            return {}
        
        return {
            'mean': np.mean(numeric_labels),
            'std': np.std(numeric_labels),
            'min': np.min(numeric_labels),
            'max': np.max(numeric_labels)
        }
    
    def _calculate_correlations(self, features: List[Dict], labels: List[Any]) -> Dict[str, float]:
        """Calculate feature-label correlations"""
        correlations = {}
        
        # Convert categorical features to numeric
        numeric_features = self._convert_to_numeric_features(features)
        numeric_labels = [float(l) if isinstance(l, (int, float)) else 0.0 for l in labels]
        
        for feature_name in numeric_features[0].keys():
            feature_values = [f[feature_name] for f in numeric_features]
            if len(set(feature_values)) > 1:  # Check if feature has variance
                correlation = np.corrcoef(feature_values, numeric_labels)[0, 1]
                correlations[feature_name] = float(correlation) if not np.isnan(correlation) else 0.0
        
        return correlations
    
    def _convert_to_numeric_features(self, features: List[Dict]) -> List[Dict]:
        """Convert categorical features to numeric"""
        numeric_features = []
        
        # Find all unique categorical values
        categorical_values = defaultdict(set)
        for feature_dict in features:
            for key, value in feature_dict.items():
                if isinstance(value, str):
                    categorical_values[key].add(value)
        
        # Create mappings
        category_mappings = {}
        for key, values in categorical_values.items():
            category_mappings[key] = {v: i for i, v in enumerate(sorted(values))}
        
        # Convert features
        for feature_dict in features:
            numeric_dict = {}
            for key, value in feature_dict.items():
                if isinstance(value, str) and key in category_mappings:
                    numeric_dict[key] = category_mappings[key][value]
                else:
                    numeric_dict[key] = float(value) if isinstance(value, (int, float)) else 0.0
            numeric_features.append(numeric_dict)
        
        return numeric_features
    
    def _calculate_feature_importance(self, features: List[Dict], labels: List[Any]) -> Dict[str, float]:
        """Calculate feature importance scores"""
        correlations = self._calculate_correlations(features, labels)
        
        # Normalize to 0-1 range
        if correlations:
            max_corr = max(abs(c) for c in correlations.values())
            if max_corr > 0:
                return {k: abs(v) / max_corr for k, v in correlations.items()}
        
        return {}
    
    def _estimate_model_accuracy(self, 
                               features: List[Dict], 
                               labels: List[Any], 
                               prediction_type: PredictionType) -> float:
        """Estimate model accuracy using simple validation"""
        if len(features) < 10:
            return 0.0
        
        # Simple train-test split
        split_idx = int(len(features) * 0.8)
        train_features = features[:split_idx]
        train_labels = labels[:split_idx]
        test_features = features[split_idx:]
        test_labels = labels[split_idx:]
        
        # Make predictions on test set
        correct_predictions = 0
        total_predictions = len(test_features)
        
        for i, test_feature in enumerate(test_features):
            prediction = self._make_simple_prediction(
                test_feature, train_features, train_labels, prediction_type
            )
            
            # Check prediction accuracy
            actual = test_labels[i]
            if prediction_type in [PredictionType.WORKFLOW_SUCCESS, PredictionType.FAILURE_PROBABILITY]:
                # Binary classification
                predicted_class = 1 if prediction > 0.5 else 0
                actual_class = 1 if actual > 0.5 else 0
                if predicted_class == actual_class:
                    correct_predictions += 1
            else:
                # Regression - check if within 20% of actual
                if actual > 0:
                    error_rate = abs(prediction - actual) / actual
                    if error_rate < 0.2:
                        correct_predictions += 1
        
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        return accuracy
    
    def _make_simple_prediction(self, 
                              feature: Dict, 
                              train_features: List[Dict], 
                              train_labels: List[Any],
                              prediction_type: PredictionType) -> float:
        """Make a simple prediction using nearest neighbor approach"""
        # Find most similar training example
        min_distance = float('inf')
        best_label = 0.0
        
        numeric_feature = self._convert_to_numeric_features([feature])[0]
        numeric_train_features = self._convert_to_numeric_features(train_features)
        
        for i, train_feature in enumerate(numeric_train_features):
            # Calculate distance
            distance = 0.0
            common_features = set(numeric_feature.keys()) & set(train_feature.keys())
            
            for key in common_features:
                distance += (numeric_feature[key] - train_feature[key]) ** 2
            
            distance = np.sqrt(distance)
            
            if distance < min_distance:
                min_distance = distance
                best_label = train_labels[i]
        
        return float(best_label)
    
    async def predict(self, 
                    prediction_type: PredictionType, 
                    context: Dict[str, Any]) -> Prediction:
        """
        Make a prediction based on current context
        
        Args:
            prediction_type: Type of prediction to make
            context: Current context for prediction
            
        Returns:
            Prediction object with results
        """
        # Check if model is trained
        if not self.models[prediction_type].get('trained', False):
            # Attempt to train with available data
            await self.train_models()
            
            if not self.models[prediction_type].get('trained', False):
                return Prediction(
                    prediction_type=prediction_type,
                    target_id=context.get('target_id', 'unknown'),
                    predicted_value=None,
                    confidence=0.0,
                    timestamp=datetime.now(),
                    features_used={},
                    explanation="Model not trained due to insufficient data"
                )
        
        # Extract features from context
        features = self._extract_features_from_context(context, prediction_type)
        
        # Make prediction
        predicted_value, confidence = await self._make_prediction(
            prediction_type, features
        )
        
        # Generate explanation
        explanation = self._generate_prediction_explanation(
            prediction_type, features, predicted_value, confidence
        )
        
        # Create prediction object
        prediction = Prediction(
            prediction_type=prediction_type,
            target_id=context.get('target_id', 'unknown'),
            predicted_value=predicted_value,
            confidence=confidence,
            timestamp=datetime.now(),
            features_used=features,
            explanation=explanation,
            time_horizon=context.get('time_horizon')
        )
        
        # Store prediction for tracking
        self.prediction_history.append({
            'prediction': prediction,
            'actual': None,  # To be updated later
            'timestamp': datetime.now()
        })
        
        return prediction
    
    def _extract_features_from_context(self, 
                                     context: Dict[str, Any], 
                                     prediction_type: PredictionType) -> Dict[str, Any]:
        """Extract relevant features from context"""
        features = {}
        
        if prediction_type == PredictionType.WORKFLOW_SUCCESS:
            features = {
                'complexity': context.get('complexity', 0.5),
                'agent_count': len(context.get('agents', [])),
                'pattern_type': context.get('pattern_type', 'unknown'),
                'urgency': context.get('urgency', 0.5)
            }
        
        elif prediction_type == PredictionType.COMPLETION_TIME:
            features = {
                'task_count': context.get('task_count', 1),
                'complexity': context.get('complexity', 0.5),
                'agent_count': len(context.get('agents', [])),
                'pattern_type': context.get('pattern_type', 'sequential')
            }
        
        elif prediction_type == PredictionType.AGENT_PERFORMANCE:
            features = {
                'agent_type': context.get('agent_type', 'unknown'),
                'task_complexity': context.get('task_complexity', 0.5),
                'workload': context.get('current_workload', 0.5),
                'collaboration_count': context.get('collaboration_count', 0)
            }
        
        elif prediction_type == PredictionType.RESOURCE_USAGE:
            features = {
                'current_usage': context.get('current_resource_usage', 0.5),
                'agent_count': len(context.get('agents', [])),
                'task_intensity': context.get('task_intensity', 0.5),
                'time_of_day': datetime.now().hour / 24.0
            }
        
        elif prediction_type == PredictionType.BOTTLENECK_RISK:
            features = {
                'agent_load': context.get('agent_load', 0.5),
                'queue_length': context.get('queue_length', 0),
                'avg_processing_time': context.get('avg_processing_time', 100),
                'connection_count': context.get('connection_count', 1)
            }
        
        elif prediction_type == PredictionType.FAILURE_PROBABILITY:
            features = {
                'complexity': context.get('complexity', 0.5),
                'error_history': context.get('recent_error_count', 0),
                'resource_availability': context.get('resource_availability', 1.0),
                'agent_health': context.get('agent_health', 1.0)
            }
        
        return features
    
    async def _make_prediction(self, 
                             prediction_type: PredictionType, 
                             features: Dict[str, Any]) -> Tuple[Any, float]:
        """Make prediction using trained model"""
        model_params = self.models[prediction_type]['parameters']
        
        if not model_params:
            return None, 0.0
        
        # Simple statistical prediction
        feature_stats = model_params.get('feature_stats', {})
        label_stats = model_params.get('label_stats', {})
        correlations = model_params.get('correlation_matrix', {})
        
        # Normalize features
        normalized_features = {}
        for key, value in features.items():
            if key in feature_stats and isinstance(value, (int, float)):
                stats = feature_stats[key]
                if stats['std'] > 0:
                    normalized_features[key] = (value - stats['mean']) / stats['std']
                else:
                    normalized_features[key] = 0.0
        
        # Make prediction based on correlations
        prediction = label_stats.get('mean', 0.0)
        total_weight = 0.0
        
        for feature_name, feature_value in normalized_features.items():
            if feature_name in correlations:
                weight = abs(correlations[feature_name])
                contribution = correlations[feature_name] * feature_value * label_stats.get('std', 1.0)
                prediction += contribution
                total_weight += weight
        
        # Calculate confidence based on feature coverage and correlation strength
        confidence = min(1.0, total_weight) * self.model_accuracy.get(prediction_type, 0.5)
        
        # Bound prediction to reasonable range
        if prediction_type in [PredictionType.WORKFLOW_SUCCESS, PredictionType.FAILURE_PROBABILITY]:
            prediction = max(0.0, min(1.0, prediction))
        elif prediction_type == PredictionType.COMPLETION_TIME:
            prediction = max(0.0, prediction)
        
        return prediction, confidence
    
    def _generate_prediction_explanation(self, 
                                       prediction_type: PredictionType,
                                       features: Dict[str, Any],
                                       predicted_value: Any,
                                       confidence: float) -> str:
        """Generate human-readable explanation for prediction"""
        explanation_parts = []
        
        # Add prediction summary
        if prediction_type == PredictionType.WORKFLOW_SUCCESS:
            success_prob = predicted_value * 100 if predicted_value else 0
            explanation_parts.append(f"Workflow has {success_prob:.1f}% chance of success")
        
        elif prediction_type == PredictionType.COMPLETION_TIME:
            time_str = f"{predicted_value:.1f} seconds" if predicted_value else "unknown time"
            explanation_parts.append(f"Estimated completion time: {time_str}")
        
        elif prediction_type == PredictionType.AGENT_PERFORMANCE:
            perf_score = predicted_value * 100 if predicted_value else 0
            explanation_parts.append(f"Expected agent performance: {perf_score:.1f}%")
        
        # Add confidence level
        confidence_level = "high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low"
        explanation_parts.append(f"Confidence: {confidence_level} ({confidence:.2f})")
        
        # Add key factors
        if self.feature_importance.get(prediction_type):
            top_features = sorted(
                self.feature_importance[prediction_type].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            if top_features:
                factors = []
                for feature_name, importance in top_features:
                    if feature_name in features:
                        factors.append(f"{feature_name} ({features[feature_name]})")
                
                if factors:
                    explanation_parts.append(f"Key factors: {', '.join(factors)}")
        
        return ". ".join(explanation_parts)
    
    async def get_predictive_insights(self, 
                                    context: Optional[Dict[str, Any]] = None,
                                    time_horizon: Optional[timedelta] = None) -> List[PredictiveInsight]:
        """
        Generate high-level predictive insights
        
        Args:
            context: Optional context to focus insights
            time_horizon: Time period for predictions
            
        Returns:
            List of predictive insights
        """
        if time_horizon is None:
            time_horizon = timedelta(hours=24)
        
        insights = []
        
        # Workflow success insights
        workflow_insight = await self._generate_workflow_insights(context, time_horizon)
        if workflow_insight:
            insights.append(workflow_insight)
        
        # Performance optimization insights
        performance_insight = await self._generate_performance_insights(context, time_horizon)
        if performance_insight:
            insights.append(performance_insight)
        
        # Resource planning insights
        resource_insight = await self._generate_resource_insights(context, time_horizon)
        if resource_insight:
            insights.append(resource_insight)
        
        # Risk management insights
        risk_insight = await self._generate_risk_insights(context, time_horizon)
        if risk_insight:
            insights.append(risk_insight)
        
        # Pattern-based insights
        pattern_insights = await self._generate_pattern_insights(context, time_horizon)
        insights.extend(pattern_insights)
        
        return insights
    
    async def _generate_workflow_insights(self, 
                                        context: Dict[str, Any],
                                        time_horizon: timedelta) -> Optional[PredictiveInsight]:
        """Generate insights about workflow success"""
        # Make predictions for different workflow types
        predictions = {}
        workflow_types = ['sequential', 'parallel', 'conditional', 'iterative', 'hierarchical']
        
        for workflow_type in workflow_types:
            pred_context = {
                'pattern_type': workflow_type,
                'complexity': context.get('avg_complexity', 0.5),
                'agent_count': context.get('avg_agent_count', 3)
            }
            
            prediction = await self.predict(PredictionType.WORKFLOW_SUCCESS, pred_context)
            if prediction.predicted_value is not None:
                predictions[workflow_type] = prediction
        
        if not predictions:
            return None
        
        # Find best performing workflow type
        best_type = max(predictions.items(), key=lambda x: x[1].predicted_value)[0]
        best_prediction = predictions[best_type]
        
        # Generate recommendations
        recommendations = []
        if best_prediction.predicted_value > 0.8:
            recommendations.append(f"Use {best_type} workflows for optimal success rate")
        
        if context.get('avg_complexity', 0.5) > 0.7:
            recommendations.append("Consider breaking down complex workflows into smaller tasks")
        
        supporting_data = {
            'workflow_predictions': {
                wf_type: pred.predicted_value 
                for wf_type, pred in predictions.items()
            },
            'confidence_levels': {
                wf_type: pred.confidence 
                for wf_type, pred in predictions.items()
            }
        }
        
        return PredictiveInsight(
            insight_type='workflow_optimization',
            title='Workflow Success Optimization',
            description=f"{best_type.capitalize()} workflows show highest success probability "
                       f"({best_prediction.predicted_value:.1%}) for next {time_horizon.days} days",
            confidence=best_prediction.confidence,
            impact='high',
            recommendations=recommendations,
            supporting_data=supporting_data,
            expires_at=datetime.now() + time_horizon
        )
    
    async def _generate_performance_insights(self, 
                                           context: Dict[str, Any],
                                           time_horizon: timedelta) -> Optional[PredictiveInsight]:
        """Generate insights about agent performance"""
        # Analyze performance trends
        agent_types = context.get('agent_types', ['task', 'research', 'technical'])
        performance_predictions = {}
        
        for agent_type in agent_types:
            pred_context = {
                'agent_type': agent_type,
                'task_complexity': context.get('avg_complexity', 0.5),
                'workload': context.get('current_workload', 0.5)
            }
            
            prediction = await self.predict(PredictionType.AGENT_PERFORMANCE, pred_context)
            if prediction.predicted_value is not None:
                performance_predictions[agent_type] = prediction
        
        if not performance_predictions:
            return None
        
        # Identify performance risks
        low_performers = [
            agent_type for agent_type, pred in performance_predictions.items()
            if pred.predicted_value < 0.6
        ]
        
        recommendations = []
        if low_performers:
            recommendations.append(f"Monitor {', '.join(low_performers)} agents for performance issues")
            recommendations.append("Consider load balancing or additional training")
        
        avg_performance = np.mean([p.predicted_value for p in performance_predictions.values()])
        
        return PredictiveInsight(
            insight_type='performance_optimization',
            title='Agent Performance Forecast',
            description=f"Average agent performance expected to be {avg_performance:.1%} "
                       f"over next {time_horizon.days} days",
            confidence=np.mean([p.confidence for p in performance_predictions.values()]),
            impact='medium' if avg_performance > 0.7 else 'high',
            recommendations=recommendations,
            supporting_data={
                'agent_performance': {
                    agent: pred.predicted_value 
                    for agent, pred in performance_predictions.items()
                }
            },
            expires_at=datetime.now() + time_horizon
        )
    
    async def _generate_resource_insights(self, 
                                        context: Dict[str, Any],
                                        time_horizon: timedelta) -> Optional[PredictiveInsight]:
        """Generate insights about resource usage"""
        # Predict resource usage
        resource_context = {
            'current_resource_usage': context.get('current_resource_usage', 0.5),
            'agents': context.get('active_agents', []),
            'task_intensity': context.get('task_intensity', 0.5)
        }
        
        prediction = await self.predict(PredictionType.RESOURCE_USAGE, resource_context)
        
        if prediction.predicted_value is None:
            return None
        
        # Determine if scaling is needed
        recommendations = []
        if prediction.predicted_value > 0.8:
            recommendations.append("Consider scaling up resources to handle predicted load")
            recommendations.append("Enable auto-scaling if available")
        elif prediction.predicted_value < 0.3:
            recommendations.append("Resources are underutilized - consider scaling down")
        
        impact = 'high' if prediction.predicted_value > 0.9 or prediction.predicted_value < 0.2 else 'medium'
        
        return PredictiveInsight(
            insight_type='resource_planning',
            title='Resource Usage Forecast',
            description=f"Resource utilization expected to reach {prediction.predicted_value:.1%} "
                       f"in next {time_horizon.hours} hours",
            confidence=prediction.confidence,
            impact=impact,
            recommendations=recommendations,
            supporting_data={
                'predicted_usage': prediction.predicted_value,
                'current_usage': resource_context['current_resource_usage'],
                'trend': 'increasing' if prediction.predicted_value > resource_context['current_resource_usage'] else 'decreasing'
            },
            expires_at=datetime.now() + time_horizon
        )
    
    async def _generate_risk_insights(self, 
                                    context: Dict[str, Any],
                                    time_horizon: timedelta) -> Optional[PredictiveInsight]:
        """Generate insights about potential risks"""
        # Predict failure probability
        risk_context = {
            'complexity': context.get('avg_complexity', 0.5),
            'recent_error_count': context.get('recent_errors', 0),
            'resource_availability': context.get('resource_availability', 1.0),
            'agent_health': context.get('avg_agent_health', 1.0)
        }
        
        failure_prediction = await self.predict(PredictionType.FAILURE_PROBABILITY, risk_context)
        
        # Predict bottleneck risk
        bottleneck_context = {
            'agent_load': context.get('max_agent_load', 0.5),
            'queue_length': context.get('avg_queue_length', 0),
            'avg_processing_time': context.get('avg_processing_time', 100)
        }
        
        bottleneck_prediction = await self.predict(PredictionType.BOTTLENECK_RISK, bottleneck_context)
        
        risks = []
        recommendations = []
        
        if failure_prediction.predicted_value and failure_prediction.predicted_value > 0.3:
            risks.append(f"Failure risk: {failure_prediction.predicted_value:.1%}")
            recommendations.append("Implement additional error handling and monitoring")
        
        if bottleneck_prediction.predicted_value and bottleneck_prediction.predicted_value > 0.5:
            risks.append(f"Bottleneck risk: {bottleneck_prediction.predicted_value:.1%}")
            recommendations.append("Review agent load distribution and optimize workflows")
        
        if not risks:
            return None
        
        return PredictiveInsight(
            insight_type='risk_management',
            title='Risk Assessment',
            description=f"Identified risks for next {time_horizon.days} days: {', '.join(risks)}",
            confidence=np.mean([failure_prediction.confidence, bottleneck_prediction.confidence]),
            impact='high',
            recommendations=recommendations,
            supporting_data={
                'failure_probability': failure_prediction.predicted_value,
                'bottleneck_risk': bottleneck_prediction.predicted_value,
                'risk_factors': risk_context
            },
            expires_at=datetime.now() + time_horizon
        )
    
    async def _generate_pattern_insights(self, 
                                       context: Dict[str, Any],
                                       time_horizon: timedelta) -> List[PredictiveInsight]:
        """Generate insights based on learned patterns"""
        insights = []
        
        # Get recent patterns from pattern learner
        recent_patterns = await self.pattern_learner.get_recent_patterns(time_window=timedelta(days=7))
        
        for pattern in recent_patterns[:3]:  # Top 3 patterns
            if pattern.success_rate > 0.8:
                insight = PredictiveInsight(
                    insight_type='pattern_recommendation',
                    title=f"High-Success Pattern: {pattern.pattern_type}",
                    description=f"Pattern '{pattern.pattern_id}' shows {pattern.success_rate:.1%} "
                               f"success rate with {pattern.occurrences} occurrences",
                    confidence=min(1.0, pattern.occurrences / 10),  # Confidence based on sample size
                    impact='medium',
                    recommendations=[
                        f"Apply this pattern for similar {pattern.pattern_type} tasks",
                        f"Expected duration: {pattern.avg_duration:.1f} seconds"
                    ],
                    supporting_data={
                        'pattern_details': pattern.context_features,
                        'success_rate': pattern.success_rate,
                        'sample_size': pattern.occurrences
                    },
                    expires_at=datetime.now() + time_horizon
                )
                insights.append(insight)
        
        return insights
    
    async def update_prediction_accuracy(self, 
                                       prediction_id: str, 
                                       actual_value: Any) -> None:
        """Update prediction accuracy with actual results"""
        # Find prediction in history
        for item in self.prediction_history:
            pred = item['prediction']
            if pred.target_id == prediction_id and item['actual'] is None:
                item['actual'] = actual_value
                
                # Update model accuracy tracking
                prediction_type = pred.prediction_type
                if prediction_type not in self.model_accuracy:
                    self.model_accuracy[prediction_type] = 0.0
                
                # Simple accuracy update (moving average)
                if pred.predicted_value is not None:
                    if prediction_type in [PredictionType.WORKFLOW_SUCCESS, PredictionType.FAILURE_PROBABILITY]:
                        # Binary accuracy
                        predicted_class = 1 if pred.predicted_value > 0.5 else 0
                        actual_class = 1 if actual_value > 0.5 else 0
                        accuracy = 1.0 if predicted_class == actual_class else 0.0
                    else:
                        # Regression accuracy (within 20% is considered accurate)
                        if actual_value > 0:
                            error_rate = abs(pred.predicted_value - actual_value) / actual_value
                            accuracy = 1.0 if error_rate < 0.2 else 0.0
                        else:
                            accuracy = 0.0
                    
                    # Update with exponential moving average
                    alpha = 0.1  # Learning rate
                    self.model_accuracy[prediction_type] = (
                        alpha * accuracy + (1 - alpha) * self.model_accuracy[prediction_type]
                    )
                
                break
    
    async def get_model_performance(self) -> Dict[str, Dict[str, float]]:
        """Get current model performance metrics"""
        performance = {}
        
        for prediction_type in PredictionType:
            performance[prediction_type.value] = {
                'accuracy': self.model_accuracy.get(prediction_type, 0.0),
                'trained': self.models[prediction_type].get('trained', False),
                'last_training': self.last_training.get(prediction_type, datetime.min).isoformat(),
                'prediction_count': len([
                    p for p in self.prediction_history 
                    if p['prediction'].prediction_type == prediction_type
                ])
            }
        
        return performance