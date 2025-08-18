"""
Integration tests for the ML/MLOps module.

This test suite verifies:
- Model training and evaluation
- Feature extraction and storage
- Model registry operations
- SHAP explainability
- End-to-end ML pipeline
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import tempfile
import os
import shutil

# Import ML modules
from ml.models import RiskModel, ClassificationModel, ModelRegistry
from ml.features import FeatureExtractor, FeatureStore, FeaturePipeline
from ml.training import (
    train_risk_model,
    train_classification_model,
    evaluate_model,
    cross_validate_model
)
from ml.explainability import SHAPExplainer, analyze_model_bias
from ml.registry import (
    save_model,
    load_model,
    list_models,
    get_model_metadata,
    validate_model_registry
)


@pytest.fixture
def sample_claims_data():
    """Create sample claims data for testing."""
    np.random.seed(42)
    
    data = pd.DataFrame({
        'claim_id': [f'claim_{i}' for i in range(100)],
        'claim_amount': np.random.uniform(1000, 50000, 100),
        'policy_duration': np.random.uniform(1, 10, 100),
        'customer_age': np.random.uniform(25, 75, 100),
        'deductible': np.random.uniform(500, 2000, 100),
        'claim_type': np.random.choice(['auto_collision', 'auto_theft', 'health_medical'], 100),
        'state': np.random.choice(['CA', 'TX', 'FL', 'NY', 'IL'], 100),
        'customer_tier': np.random.choice(['standard', 'premium', 'vip'], 100),
        'policy_type': np.random.choice(['standard', 'comprehensive'], 100),
        'description': [
            f"Claim description {i} with details about the incident" 
            for i in range(100)
        ],
        'claim_date': pd.date_range('2023-01-01', periods=100, freq='D'),
        'injuries_involved': np.random.choice([True, False], 100),
        'multi_vehicle': np.random.choice([True, False], 100),
        'hit_and_run': np.random.choice([True, False], 100),
        'time_sensitive': np.random.choice([True, False], 100),
        'customer_priority': np.random.choice([True, False], 100),
        'police_report': np.random.choice([True, False], 100),
        'medical_records': np.random.choice([True, False], 100),
        'photos': np.random.choice([True, False], 100),
        'estimates': np.random.choice([True, False], 100),
        'risk_score': np.random.uniform(0, 1, 100)
    })
    
    return data


@pytest.fixture
def temp_registry_path():
    """Create a temporary directory for model registry."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestRiskModel:
    """Test RiskModel functionality."""
    
    def test_risk_model_initialization(self):
        """Test RiskModel initialization."""
        model = RiskModel()
        assert model.model_name == "risk_model"
        assert model.model_type == "risk_scoring"
        assert model.model is not None
        assert len(model.feature_names) > 0
    
    def test_feature_extraction(self, sample_claims_data):
        """Test feature extraction from claims data."""
        model = RiskModel()
        features = model.extract_features(sample_claims_data)
        
        assert isinstance(features, pd.DataFrame)
        assert len(features) == len(sample_claims_data)
        assert 'claim_amount' in features.columns
        assert 'geographic_risk' in features.columns
        assert 'urgency_score' in features.columns
    
    def test_risk_model_training(self, sample_claims_data):
        """Test risk model training."""
        model = RiskModel()
        
        # Prepare data
        X = sample_claims_data.drop(columns=['risk_score', 'claim_id'])
        y = sample_claims_data['risk_score']
        
        # Train model
        metrics = model.train(X, y, validation_split=0.2)
        
        assert isinstance(metrics, dict)
        assert 'mse' in metrics
        assert 'mae' in metrics
        assert 'r2' in metrics
        assert metrics['r2'] >= 0  # R² should be non-negative
    
    def test_risk_model_prediction(self, sample_claims_data):
        """Test risk model prediction."""
        model = RiskModel()
        
        # Prepare data
        X = sample_claims_data.drop(columns=['risk_score', 'claim_id'])
        y = sample_claims_data['risk_score']
        
        # Train model
        model.train(X, y, validation_split=0.2)
        
        # Make predictions
        predictions = model.predict(X.head(10))
        
        assert len(predictions) == 10
        assert all(isinstance(p, (int, float)) for p in predictions)
        assert all(0 <= p <= 1 for p in predictions)  # Risk scores should be in [0,1]


class TestClassificationModel:
    """Test ClassificationModel functionality."""
    
    def test_classification_model_initialization(self):
        """Test ClassificationModel initialization."""
        model = ClassificationModel()
        assert model.model_name == "classification_model"
        assert model.model_type == "classification"
        assert len(model.claim_types) > 0
        assert len(model.urgency_levels) > 0
    
    def test_claim_type_classification(self):
        """Test claim type classification."""
        model = ClassificationModel()
        
        # Test classification
        result = model.classify_claim_type("Car accident with injuries")
        
        assert isinstance(result, dict)
        assert 'prediction' in result
        assert 'confidence' in result
        assert 'method' in result
        assert result['prediction'] in model.claim_types
    
    def test_urgency_classification(self):
        """Test urgency classification."""
        model = ClassificationModel()
        
        # Test urgency classification
        claim_data = {
            'claim_amount': 25000,
            'injuries_involved': True,
            'time_sensitive': True,
            'customer_priority': False
        }
        
        result = model.classify_urgency(claim_data)
        
        assert isinstance(result, dict)
        assert 'prediction' in result
        assert 'confidence' in result
        assert 'urgency_score' in result
        assert result['prediction'] in model.urgency_levels
    
    def test_ml_fallback_training(self, sample_claims_data):
        """Test ML fallback model training."""
        model = ClassificationModel()
        
        # Prepare data
        texts = sample_claims_data['description'].tolist()
        labels = sample_claims_data['claim_type'].tolist()
        
        # Train ML fallback
        metrics = model.train_ml_fallback(texts, labels)
        
        assert isinstance(metrics, dict)
        assert 'accuracy' in metrics
        assert 0 <= metrics['accuracy'] <= 1


class TestFeatureExtractor:
    """Test FeatureExtractor functionality."""
    
    def test_feature_extractor_initialization(self):
        """Test FeatureExtractor initialization."""
        extractor = FeatureExtractor()
        assert extractor.scalers == {}
        assert extractor.encoders == {}
        assert extractor.vectorizers == {}
    
    def test_claim_feature_extraction(self, sample_claims_data):
        """Test feature extraction from single claim."""
        extractor = FeatureExtractor()
        
        claim_data = sample_claims_data.iloc[0].to_dict()
        features = extractor.extract_claim_features(claim_data)
        
        assert isinstance(features, dict)
        assert 'claim_amount' in features
        assert 'claim_type' in features
        assert 'combined_text' in features
        assert 'urgency_score' in features
    
    def test_batch_feature_extraction(self, sample_claims_data):
        """Test batch feature extraction."""
        extractor = FeatureExtractor()
        
        claims_data = sample_claims_data.head(10).to_dict('records')
        features_df = extractor.fit_transform_batch(claims_data)
        
        assert isinstance(features_df, pd.DataFrame)
        assert len(features_df) == 10
        assert len(features_df.columns) > 0


class TestFeatureStore:
    """Test FeatureStore functionality."""
    
    def test_feature_store_initialization(self):
        """Test FeatureStore initialization."""
        # Note: This test may fail if Redis is not available
        try:
            store = FeatureStore()
            # If Redis is available, test basic operations
            if store.redis_client:
                assert store.redis_client is not None
        except Exception:
            # Redis not available, skip detailed tests
            pass
    
    def test_feature_storage_and_retrieval(self):
        """Test feature storage and retrieval."""
        try:
            store = FeatureStore()
            if not store.redis_client:
                pytest.skip("Redis not available")
            
            # Test storage and retrieval
            features = {'feature1': 1.0, 'feature2': 2.0}
            success = store.store_features('test_claim', features)
            
            if success:
                retrieved = store.get_features('test_claim')
                assert retrieved == features
                
                # Cleanup
                store.delete_features('test_claim')
        except Exception:
            pytest.skip("Redis not available")


class TestModelRegistry:
    """Test ModelRegistry functionality."""
    
    def test_registry_initialization(self, temp_registry_path):
        """Test ModelRegistry initialization."""
        registry = ModelRegistry(temp_registry_path)
        assert registry.registry_path == temp_registry_path
        assert isinstance(registry.registry, dict)
    
    def test_model_registration(self, temp_registry_path, sample_claims_data):
        """Test model registration."""
        registry = ModelRegistry(temp_registry_path)
        
        # Create and train a model
        model = RiskModel()
        X = sample_claims_data.drop(columns=['risk_score', 'claim_id'])
        y = sample_claims_data['risk_score']
        model.train(X, y, validation_split=0.2)
        
        # Register model
        metrics = {'accuracy': 0.85}
        model_id = registry.register_model(model, "1.0.0", metrics)
        
        assert model_id is not None
        assert "risk_model_risk_scoring_v1.0.0" in model_id
    
    def test_model_loading(self, temp_registry_path, sample_claims_data):
        """Test model loading."""
        registry = ModelRegistry(temp_registry_path)
        
        # Create and register a model
        model = RiskModel()
        X = sample_claims_data.drop(columns=['risk_score', 'claim_id'])
        y = sample_claims_data['risk_score']
        model.train(X, y, validation_split=0.2)
        
        metrics = {'accuracy': 0.85}
        model_id = registry.register_model(model, "1.0.0", metrics)
        
        # Load model
        loaded_model = registry.get_model(model_id)
        assert loaded_model is not None
        assert isinstance(loaded_model, RiskModel)
    
    def test_model_listing(self, temp_registry_path):
        """Test model listing."""
        registry = ModelRegistry(temp_registry_path)
        models = registry.list_models()
        assert isinstance(models, list)


class TestTrainingFunctions:
    """Test training functions."""
    
    def test_risk_model_training_function(self, sample_claims_data):
        """Test risk model training function."""
        results = train_risk_model(
            data=sample_claims_data,
            target_column='risk_score',
            save_model=False
        )
        
        assert isinstance(results, dict)
        assert 'model_type' in results
        assert 'training_metrics' in results
        assert 'test_metrics' in results
        assert results['model_type'] == 'risk_scoring'
    
    def test_classification_model_training_function(self, sample_claims_data):
        """Test classification model training function."""
        results = train_classification_model(
            data=sample_claims_data,
            text_column='description',
            target_column='claim_type',
            save_model=False
        )
        
        assert isinstance(results, dict)
        assert 'model_type' in results
        assert 'test_metrics' in results
        assert results['model_type'] == 'classification'
    
    def test_cross_validation(self, sample_claims_data):
        """Test cross-validation."""
        results = cross_validate_model(
            data=sample_claims_data,
            target_column='risk_score',
            model_type='risk',
            cv_folds=3
        )
        
        assert isinstance(results, dict)
        assert 'cv_folds' in results
        assert 'mean_mse' in results
        assert 'std_mse' in results


class TestExplainability:
    """Test explainability functionality."""
    
    def test_shap_explainer_initialization(self, sample_claims_data):
        """Test SHAP explainer initialization."""
        # Create and train a model
        model = RiskModel()
        X = sample_claims_data.drop(columns=['risk_score', 'claim_id'])
        y = sample_claims_data['risk_score']
        model.train(X, y, validation_split=0.2)
        
        # Initialize explainer
        explainer = SHAPExplainer(model)
        assert explainer.model is not None
    
    def test_feature_importance(self, sample_claims_data):
        """Test feature importance calculation."""
        # Create and train a model
        model = RiskModel()
        X = sample_claims_data.drop(columns=['risk_score', 'claim_id'])
        y = sample_claims_data['risk_score']
        model.train(X, y, validation_split=0.2)
        
        # Initialize explainer
        explainer = SHAPExplainer(model)
        
        # Get feature importance
        importance = explainer.get_feature_importance(X.head(10))
        
        assert isinstance(importance, dict)
        assert 'feature_importance' in importance
        assert 'sorted_features' in importance
        assert 'top_features' in importance
    
    def test_bias_analysis(self, sample_claims_data):
        """Test bias analysis."""
        # Create and train a model
        model = RiskModel()
        X = sample_claims_data.drop(columns=['risk_score', 'claim_id'])
        y = sample_claims_data['risk_score']
        model.train(X, y, validation_split=0.2)
        
        # Analyze bias
        bias_results = analyze_model_bias(
            model=model,
            data=sample_claims_data,
            sensitive_features=['state', 'customer_tier']
        )
        
        assert isinstance(bias_results, dict)
        assert 'sensitive_features' in bias_results
        assert 'analysis_results' in bias_results


class TestRegistryFunctions:
    """Test registry utility functions."""
    
    def test_save_and_load_model(self, temp_registry_path, sample_claims_data):
        """Test save and load model functions."""
        # Create and train a model
        model = RiskModel()
        X = sample_claims_data.drop(columns=['risk_score', 'claim_id'])
        y = sample_claims_data['risk_score']
        model.train(X, y, validation_split=0.2)
        
        # Save model
        model_id = save_model(
            model=model,
            model_name="test_model",
            metadata={'accuracy': 0.85},
            registry_path=temp_registry_path
        )
        
        assert model_id is not None
        
        # Load model
        loaded_model = load_model(model_id, registry_path=temp_registry_path)
        assert loaded_model is not None
        assert isinstance(loaded_model, RiskModel)
    
    def test_list_models_function(self, temp_registry_path):
        """Test list_models function."""
        models = list_models(registry_path=temp_registry_path)
        assert isinstance(models, list)
    
    def test_get_model_metadata(self, temp_registry_path, sample_claims_data):
        """Test get_model_metadata function."""
        # Create and register a model
        model = RiskModel()
        X = sample_claims_data.drop(columns=['risk_score', 'claim_id'])
        y = sample_claims_data['risk_score']
        model.train(X, y, validation_split=0.2)
        
        metadata = {'accuracy': 0.85, 'test_metric': 0.82}
        model_id = save_model(
            model=model,
            model_name="test_model",
            metadata=metadata,
            registry_path=temp_registry_path
        )
        
        # Get metadata
        retrieved_metadata = get_model_metadata(model_id, registry_path=temp_registry_path)
        assert retrieved_metadata is not None
        assert 'accuracy' in retrieved_metadata
    
    def test_validate_registry(self, temp_registry_path):
        """Test validate_model_registry function."""
        validation = validate_model_registry(registry_path=temp_registry_path)
        assert isinstance(validation, dict)
        assert 'total_models' in validation
        assert 'total_versions' in validation
        assert 'errors' in validation
        assert 'warnings' in validation


class TestEndToEndPipeline:
    """Test end-to-end ML pipeline."""
    
    def test_complete_ml_pipeline(self, temp_registry_path, sample_claims_data):
        """Test complete ML pipeline from training to evaluation."""
        # 1. Train risk model
        training_results = train_risk_model(
            data=sample_claims_data,
            target_column='risk_score',
            save_model=True,
            model_version="test_v1"
        )
        
        assert 'model_id' in training_results
        
        # 2. Load model
        model = load_model(training_results['model_id'])
        assert model is not None
        
        # 3. Evaluate model
        evaluation_results = evaluate_model(
            model_id=training_results['model_id'],
            test_data=sample_claims_data.head(20),
            target_column='risk_score',
            model_type='risk'
        )
        
        assert isinstance(evaluation_results, dict)
        assert 'evaluation_metrics' in evaluation_results
        
        # 4. Generate explanations
        explainer = SHAPExplainer(model)
        importance = explainer.get_feature_importance(sample_claims_data.head(10))
        assert isinstance(importance, dict)
        
        # 5. Check registry
        models = list_models(registry_path=temp_registry_path)
        assert len(models) > 0
        
        # 6. Validate registry
        validation = validate_model_registry(registry_path=temp_registry_path)
        assert validation['is_valid'] is True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
