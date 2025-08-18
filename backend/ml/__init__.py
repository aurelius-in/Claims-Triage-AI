"""
ML/MLOps module for Claims Triage AI.

This module provides:
- Model training and evaluation pipelines
- Model registry and versioning
- Feature store implementation
- SHAP explainability integration
- A/B testing framework
"""

from .models import (
    RiskModel,
    ClassificationModel,
    ModelRegistry,
    ModelVersion
)
from .features import (
    FeatureStore,
    FeatureExtractor,
    FeaturePipeline
)
from .training import (
    train_risk_model,
    train_classification_model,
    evaluate_model,
    cross_validate_model
)
from .explainability import (
    SHAPExplainer,
    explain_prediction,
    generate_feature_importance
)
from .registry import (
    ModelRegistry,
    save_model,
    load_model,
    list_models,
    get_model_metadata
)

__all__ = [
    # Models
    "RiskModel",
    "ClassificationModel",
    "ModelRegistry",
    "ModelVersion",
    
    # Features
    "FeatureStore",
    "FeatureExtractor",
    "FeaturePipeline",
    
    # Training
    "train_risk_model",
    "train_classification_model",
    "evaluate_model",
    "cross_validate_model",
    
    # Explainability
    "SHAPExplainer",
    "explain_prediction",
    "generate_feature_importance",
    
    # Registry
    "ModelRegistry",
    "save_model",
    "load_model",
    "list_models",
    "get_model_metadata"
]
