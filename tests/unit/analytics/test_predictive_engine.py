"""
Unit tests for PredictiveEngine
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
import numpy as np

from src.analytics.predictive_engine import (
    PredictiveEngine,
    PredictionType,
    Prediction,
    PredictiveInsight,
    HistoricalPattern
)


@pytest.fixture
def mock_knowledge_base():
    """Mock knowledge base"""
    kb = AsyncMock()
    kb.find_similar_patterns = AsyncMock(return_value=[])
    return kb


@pytest.fixture
def mock_pattern_learner():
    """Mock pattern learner"""
    learner = AsyncMock()
    learner.get_recent_patterns = AsyncMock(return_value=[])
    return learner


@pytest.fixture
def mock_shared_context():
    """Mock shared context"""
    context = AsyncMock()
    context.store = AsyncMock()
    return context


@pytest.fixture
def predictive_engine(mock_knowledge_base, mock_pattern_learner, mock_shared_context):
    """Create PredictiveEngine instance for testing"""
    return PredictiveEngine(mock_knowledge_base, mock_pattern_learner, mock_shared_context)


@pytest.fixture
def sample_historical_data():
    """Sample historical data for training"""
    return [
        {
            'type': 'workflow',
            'data': {
                'complexity': 0.7,
                'agent_count': 3,
                'pattern_type': 'sequential',
                'success': True,
                'duration': 120.0
            },
            'metadata': {'timestamp': datetime.now().isoformat()}
        },
        {
            'type': 'workflow',
            'data': {
                'complexity': 0.3,
                'agent_count': 2,
                'pattern_type': 'parallel',
                'success': True,
                'duration': 80.0
            },
            'metadata': {'timestamp': datetime.now().isoformat()}
        },
        {
            'type': 'agent',
            'data': {
                'agent_type': 'research',
                'task_complexity': 0.5,
                'workload': 0.4,
                'performance_score': 0.8
            },
            'metadata': {'timestamp': datetime.now().isoformat()}
        }
    ]


class TestPredictiveEngine:
    """Test cases for PredictiveEngine"""
    
    def test_initialization(self, predictive_engine):
        """Test PredictiveEngine initialization"""
        assert len(predictive_engine.models) == len(PredictionType)
        assert len(predictive_engine.model_accuracy) == len(PredictionType)
        
        # All models should be initialized but not trained
        for prediction_type in PredictionType:
            assert prediction_type in predictive_engine.models
            assert not predictive_engine.models[prediction_type]['trained']
    
    @pytest.mark.asyncio
    async def test_train_models_insufficient_data(self, predictive_engine):
        """Test training with insufficient data"""
        # Provide very little data
        minimal_data = [
            {
                'type': 'workflow',
                'data': {'complexity': 0.5, 'success': True},
                'metadata': {}
            }
        ]
        
        results = await predictive_engine.train_models(minimal_data)
        
        # Should return 0 accuracy for all models due to insufficient data
        for prediction_type in PredictionType:
            assert results[prediction_type.value] == 0.0
    
    @pytest.mark.asyncio
    async def test_train_models_with_data(self, predictive_engine, sample_historical_data):
        """Test training with sufficient data"""
        # Expand sample data to meet minimum requirements
        expanded_data = sample_historical_data * 5  # 15 total samples
        
        results = await predictive_engine.train_models(expanded_data)
        
        # Should have some accuracy for models with sufficient data
        assert isinstance(results, dict)
        for prediction_type, accuracy in results.items():
            assert 0 <= accuracy <= 1
    
    def test_filter_data_for_prediction_type(self, predictive_engine, sample_historical_data):
        """Test data filtering for specific prediction types"""
        # Test workflow success filtering
        workflow_data = predictive_engine._filter_data_for_prediction_type(
            sample_historical_data, PredictionType.WORKFLOW_SUCCESS
        )
        
        assert len(workflow_data) == 2  # Two workflow items
        
        # Test agent performance filtering
        agent_data = predictive_engine._filter_data_for_prediction_type(
            sample_historical_data, PredictionType.AGENT_PERFORMANCE
        )
        
        assert len(agent_data) == 1  # One agent item
    
    def test_prepare_training_data_workflow_success(self, predictive_engine):
        """Test training data preparation for workflow success"""
        raw_data = [
            {
                'data': {
                    'complexity': 0.7,
                    'agent_count': 3,
                    'pattern_type': 'sequential',
                    'success': True
                }
            },
            {
                'data': {
                    'complexity': 0.3,
                    'agent_count': 2,
                    'pattern_type': 'parallel',
                    'success': False
                }
            }
        ]
        
        features, labels = predictive_engine._prepare_training_data(
            PredictionType.WORKFLOW_SUCCESS, raw_data
        )
        
        assert len(features) == 2
        assert len(labels) == 2
        assert labels[0] == 1.0  # Success
        assert labels[1] == 0.0  # Failure
        
        # Check feature extraction
        assert features[0]['complexity'] == 0.7
        assert features[0]['agent_count'] == 3
    
    def test_prepare_training_data_completion_time(self, predictive_engine):
        """Test training data preparation for completion time"""
        raw_data = [
            {
                'data': {
                    'task_count': 5,
                    'complexity': 0.6,
                    'agent_count': 3,
                    'duration': 150.0
                }
            }
        ]
        
        features, labels = predictive_engine._prepare_training_data(
            PredictionType.COMPLETION_TIME, raw_data
        )
        
        assert len(features) == 1
        assert len(labels) == 1
        assert labels[0] == 150.0
        assert features[0]['task_count'] == 5
    
    def test_convert_to_numeric_features(self, predictive_engine):
        """Test conversion of categorical features to numeric"""
        features = [
            {'numeric_feature': 1.5, 'categorical_feature': 'type_a'},
            {'numeric_feature': 2.0, 'categorical_feature': 'type_b'},
            {'numeric_feature': 1.0, 'categorical_feature': 'type_a'}
        ]
        
        numeric_features = predictive_engine._convert_to_numeric_features(features)
        
        assert len(numeric_features) == 3
        
        # Categorical values should be mapped to numbers
        assert all(isinstance(f['categorical_feature'], float) for f in numeric_features)
        
        # Same categorical values should have same numeric mapping
        assert numeric_features[0]['categorical_feature'] == numeric_features[2]['categorical_feature']
        assert numeric_features[0]['categorical_feature'] != numeric_features[1]['categorical_feature']
    
    def test_calculate_feature_statistics(self, predictive_engine):
        """Test feature statistics calculation"""
        features = [
            {'feature1': 10.0, 'feature2': 5.0},
            {'feature1': 20.0, 'feature2': 15.0},
            {'feature1': 30.0, 'feature2': 25.0}
        ]
        
        stats = predictive_engine._calculate_feature_statistics(features)
        
        assert 'feature1' in stats
        assert 'feature2' in stats
        
        # Check statistics for feature1
        assert stats['feature1']['mean'] == 20.0
        assert stats['feature1']['min'] == 10.0
        assert stats['feature1']['max'] == 30.0
    
    def test_calculate_correlations(self, predictive_engine):
        """Test correlation calculation between features and labels"""
        features = [
            {'feature1': 1.0, 'feature2': 10.0},
            {'feature1': 2.0, 'feature2': 20.0},
            {'feature1': 3.0, 'feature2': 30.0}
        ]
        labels = [10.0, 20.0, 30.0]  # Perfectly correlated with feature2
        
        correlations = predictive_engine._calculate_correlations(features, labels)
        
        assert 'feature1' in correlations
        assert 'feature2' in correlations
        
        # feature2 should have higher correlation than feature1
        assert abs(correlations['feature2']) > abs(correlations['feature1'])
    
    @pytest.mark.asyncio
    async def test_predict_untrained_model(self, predictive_engine):
        """Test prediction with untrained model"""
        context = {
            'complexity': 0.5,
            'agent_count': 2,
            'pattern_type': 'sequential'
        }
        
        prediction = await predictive_engine.predict(
            PredictionType.WORKFLOW_SUCCESS, context
        )
        
        assert prediction.predicted_value is None
        assert prediction.confidence == 0.0
        assert "not trained" in prediction.explanation.lower()
    
    @pytest.mark.asyncio
    async def test_predict_with_trained_model(self, predictive_engine, sample_historical_data):
        """Test prediction with trained model"""
        # Train the model first
        expanded_data = sample_historical_data * 10
        await predictive_engine.train_models(expanded_data)
        
        # Mark a model as trained for testing
        predictive_engine.models[PredictionType.WORKFLOW_SUCCESS]['trained'] = True
        predictive_engine.models[PredictionType.WORKFLOW_SUCCESS]['parameters'] = {
            'feature_stats': {'complexity': {'mean': 0.5, 'std': 0.2}},
            'label_stats': {'mean': 0.8, 'std': 0.1},
            'correlation_matrix': {'complexity': 0.5}
        }
        
        context = {
            'complexity': 0.7,
            'agents': ['agent1', 'agent2'],
            'pattern_type': 'sequential'
        }
        
        prediction = await predictive_engine.predict(
            PredictionType.WORKFLOW_SUCCESS, context
        )
        
        assert prediction.predicted_value is not None
        assert 0 <= prediction.predicted_value <= 1  # Should be probability
        assert prediction.confidence > 0
        assert len(prediction.explanation) > 0
    
    def test_extract_features_from_context_workflow_success(self, predictive_engine):
        """Test feature extraction for workflow success prediction"""
        context = {
            'complexity': 0.8,
            'agents': ['agent1', 'agent2', 'agent3'],
            'pattern_type': 'hierarchical',
            'urgency': 0.9
        }
        
        features = predictive_engine._extract_features_from_context(
            context, PredictionType.WORKFLOW_SUCCESS
        )
        
        assert features['complexity'] == 0.8
        assert features['agent_count'] == 3
        assert features['pattern_type'] == 'hierarchical'
        assert features['urgency'] == 0.9
    
    def test_extract_features_from_context_agent_performance(self, predictive_engine):
        """Test feature extraction for agent performance prediction"""
        context = {
            'agent_type': 'research',
            'task_complexity': 0.6,
            'current_workload': 0.4,
            'collaboration_count': 2
        }
        
        features = predictive_engine._extract_features_from_context(
            context, PredictionType.AGENT_PERFORMANCE
        )
        
        assert features['agent_type'] == 'research'
        assert features['task_complexity'] == 0.6
        assert features['workload'] == 0.4
        assert features['collaboration_count'] == 2
    
    def test_generate_prediction_explanation(self, predictive_engine):
        """Test prediction explanation generation"""
        features = {'complexity': 0.7, 'agent_count': 3}
        predicted_value = 0.85
        confidence = 0.9
        
        explanation = predictive_engine._generate_prediction_explanation(
            PredictionType.WORKFLOW_SUCCESS, features, predicted_value, confidence
        )
        
        assert "85.0%" in explanation  # Success percentage
        assert "high" in explanation.lower()  # High confidence
        assert len(explanation) > 50  # Should be reasonably detailed
    
    @pytest.mark.asyncio
    async def test_update_prediction_accuracy(self, predictive_engine):
        """Test updating prediction accuracy with actual results"""
        # Create a prediction entry
        prediction = Prediction(
            prediction_type=PredictionType.WORKFLOW_SUCCESS,
            target_id="test_workflow",
            predicted_value=0.8,
            confidence=0.9,
            timestamp=datetime.now(),
            features_used={},
            explanation="Test prediction"
        )
        
        # Add to history
        predictive_engine.prediction_history.append({
            'prediction': prediction,
            'actual': None,
            'timestamp': datetime.now()
        })
        
        # Update with actual result
        await predictive_engine.update_prediction_accuracy("test_workflow", 1.0)
        
        # Check that accuracy was updated
        assert PredictionType.WORKFLOW_SUCCESS in predictive_engine.model_accuracy
        
        # Verify the prediction was marked with actual value
        history_item = predictive_engine.prediction_history[0]
        assert history_item['actual'] == 1.0
    
    @pytest.mark.asyncio
    async def test_get_model_performance(self, predictive_engine):
        """Test getting model performance metrics"""
        # Set some test accuracy values
        predictive_engine.model_accuracy[PredictionType.WORKFLOW_SUCCESS] = 0.85
        predictive_engine.models[PredictionType.WORKFLOW_SUCCESS]['trained'] = True
        
        performance = await predictive_engine.get_model_performance()
        
        assert PredictionType.WORKFLOW_SUCCESS.value in performance
        
        workflow_perf = performance[PredictionType.WORKFLOW_SUCCESS.value]
        assert workflow_perf['accuracy'] == 0.85
        assert workflow_perf['trained'] == True
        assert 'last_training' in workflow_perf
        assert 'prediction_count' in workflow_perf
    
    @pytest.mark.asyncio
    async def test_get_predictive_insights_empty(self, predictive_engine):
        """Test getting insights with no data"""
        insights = await predictive_engine.get_predictive_insights()
        
        # Should return list even if empty
        assert isinstance(insights, list)
    
    @pytest.mark.asyncio
    async def test_get_predictive_insights_with_patterns(self, predictive_engine, mock_pattern_learner):
        """Test getting insights with pattern data"""
        # Mock pattern learner to return sample patterns
        mock_patterns = [
            HistoricalPattern(
                pattern_id="pattern1",
                pattern_type="sequential_research",
                occurrences=15,
                success_rate=0.9,
                avg_duration=120.0,
                context_features={'complexity': 0.5},
                outcomes=[]
            )
        ]
        mock_pattern_learner.get_recent_patterns.return_value = mock_patterns
        
        insights = await predictive_engine.get_predictive_insights()
        
        assert len(insights) > 0
        
        # Check that pattern insight was generated
        pattern_insights = [i for i in insights if i.insight_type == 'pattern_recommendation']
        assert len(pattern_insights) > 0
        
        insight = pattern_insights[0]
        assert insight.title.startswith("High-Success Pattern")
        assert "90.0%" in insight.description
    
    def test_make_simple_prediction(self, predictive_engine):
        """Test simple prediction using nearest neighbor approach"""
        feature = {'complexity': 0.5, 'agent_count': 2}
        train_features = [
            {'complexity': 0.4, 'agent_count': 2},  # Similar
            {'complexity': 0.8, 'agent_count': 5},  # Different
            {'complexity': 0.6, 'agent_count': 3}   # Moderately similar
        ]
        train_labels = [0.8, 0.3, 0.7]
        
        prediction = predictive_engine._make_simple_prediction(
            feature, train_features, train_labels, PredictionType.WORKFLOW_SUCCESS
        )
        
        # Should return the label of the most similar training example
        # The first training example is most similar
        assert prediction == 0.8
    
    def test_estimate_model_accuracy(self, predictive_engine):
        """Test model accuracy estimation"""
        features = [
            {'feature1': 1.0}, {'feature1': 2.0}, {'feature1': 3.0},
            {'feature1': 4.0}, {'feature1': 5.0}, {'feature1': 6.0},
            {'feature1': 7.0}, {'feature1': 8.0}, {'feature1': 9.0},
            {'feature1': 10.0}
        ]
        # Labels perfectly correlated with feature1
        labels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        
        accuracy = predictive_engine._estimate_model_accuracy(
            features, labels, PredictionType.WORKFLOW_SUCCESS
        )
        
        # Should have reasonable accuracy for perfectly correlated data
        assert 0 <= accuracy <= 1
    
    @pytest.mark.asyncio
    async def test_large_dataset_performance(self, predictive_engine):
        """Test performance with large dataset"""
        # Generate large dataset
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                'type': 'workflow',
                'data': {
                    'complexity': np.random.random(),
                    'agent_count': np.random.randint(1, 10),
                    'pattern_type': np.random.choice(['sequential', 'parallel', 'hierarchical']),
                    'success': np.random.random() > 0.3,
                    'duration': np.random.uniform(50, 300)
                },
                'metadata': {'timestamp': datetime.now().isoformat()}
            })
        
        # Train models (should complete in reasonable time)
        start_time = datetime.now()
        results = await predictive_engine.train_models(large_dataset)
        training_time = (datetime.now() - start_time).total_seconds()
        
        assert training_time < 10.0  # Should complete within 10 seconds
        assert len(results) == len(PredictionType)


@pytest.mark.asyncio
class TestAsyncPredictiveEngine:
    """Async test cases for PredictiveEngine"""
    
    async def test_concurrent_predictions(self, predictive_engine, sample_historical_data):
        """Test concurrent prediction requests"""
        # Train model first
        expanded_data = sample_historical_data * 10
        await predictive_engine.train_models(expanded_data)
        
        # Mark model as trained
        predictive_engine.models[PredictionType.WORKFLOW_SUCCESS]['trained'] = True
        predictive_engine.models[PredictionType.WORKFLOW_SUCCESS]['parameters'] = {
            'feature_stats': {'complexity': {'mean': 0.5, 'std': 0.2}},
            'label_stats': {'mean': 0.8, 'std': 0.1},
            'correlation_matrix': {'complexity': 0.5}
        }
        
        # Make concurrent predictions
        contexts = [
            {'complexity': 0.1 * i, 'agents': [f'agent{j}' for j in range(i+1)]}
            for i in range(10)
        ]
        
        tasks = [
            predictive_engine.predict(PredictionType.WORKFLOW_SUCCESS, context)
            for context in contexts
        ]
        
        predictions = await asyncio.gather(*tasks)
        
        assert len(predictions) == 10
        assert all(p.predicted_value is not None for p in predictions)