"""
Core ML models for Claims Triage AI.

This module provides:
- RiskModel: XGBoost-based risk scoring model
- ClassificationModel: Zero-shot LLM + fallback ML classifier
- Model base classes and interfaces
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime
from pathlib import Path

import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    roc_auc_score,
    precision_recall_curve,
    average_precision_score
)
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import shap

# For zero-shot classification
try:
    from transformers import pipeline
    ZERO_SHOT_AVAILABLE = True
except ImportError:
    ZERO_SHOT_AVAILABLE = False

from ..core.config import settings


class BaseModel:
    """Base class for all ML models."""
    
    def __init__(self, model_name: str, model_type: str):
        self.model_name = model_name
        self.model_type = model_type
        self.model = None
        self.feature_names = []
        self.metadata = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def save(self, path: str) -> None:
        """Save model to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model
        joblib.dump(self.model, f"{path}.pkl")
        
        # Save metadata
        metadata = {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "feature_names": self.feature_names,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        with open(f"{path}_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
    
    def load(self, path: str) -> None:
        """Load model from disk."""
        # Load model
        self.model = joblib.load(f"{path}.pkl")
        
        # Load metadata
        with open(f"{path}_metadata.json", "r") as f:
            metadata = json.load(f)
            self.model_name = metadata["model_name"]
            self.model_type = metadata["model_type"]
            self.feature_names = metadata["feature_names"]
            self.metadata = metadata["metadata"]
            self.created_at = datetime.fromisoformat(metadata["created_at"])
            self.updated_at = datetime.fromisoformat(metadata["updated_at"])


class RiskModel(BaseModel):
    """
    XGBoost-based risk scoring model for claims.
    
    Features:
    - Claim amount
    - Claim type
    - Policy duration
    - Customer history
    - Geographic risk factors
    - Temporal features
    """
    
    def __init__(self, model_name: str = "risk_model"):
        super().__init__(model_name, "risk_scoring")
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            objective='reg:squarederror'
        )
        self.scaler = StandardScaler()
        self.feature_names = [
            'claim_amount', 'policy_duration', 'customer_age',
            'claim_frequency', 'geographic_risk', 'temporal_risk',
            'document_completeness', 'urgency_score'
        ]
    
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract features from raw claim data."""
        features = pd.DataFrame()
        
        # Basic features
        features['claim_amount'] = data['claim_amount'].fillna(0)
        features['policy_duration'] = data['policy_duration'].fillna(0)
        features['customer_age'] = data['customer_age'].fillna(0)
        
        # Derived features
        features['claim_frequency'] = data.groupby('customer_id')['claim_id'].transform('count')
        features['geographic_risk'] = data['state'].map(self._get_geographic_risk())
        features['temporal_risk'] = data['claim_date'].dt.dayofweek
        
        # Document completeness
        features['document_completeness'] = (
            data[['police_report', 'medical_records', 'photos', 'estimates']]
            .notna().sum(axis=1) / 4
        )
        
        # Urgency score (simple heuristic)
        features['urgency_score'] = (
            (features['claim_amount'] > 10000).astype(int) +
            (features['claim_frequency'] > 2).astype(int) +
            (features['geographic_risk'] > 0.7).astype(int)
        )
        
        return features
    
    def _get_geographic_risk(self) -> Dict[str, float]:
        """Get geographic risk scores by state."""
        # This would typically come from external data or be learned
        high_risk_states = ['CA', 'TX', 'FL', 'NY', 'IL']
        medium_risk_states = ['PA', 'OH', 'GA', 'NC', 'MI']
        
        risk_scores = {}
        for state in high_risk_states:
            risk_scores[state] = 0.8
        for state in medium_risk_states:
            risk_scores[state] = 0.5
        # Default risk for other states
        risk_scores['default'] = 0.3
        
        return risk_scores
    
    def train(self, X: pd.DataFrame, y: pd.Series, validation_split: float = 0.2) -> Dict[str, float]:
        """Train the risk model."""
        # Extract features
        X_features = self.extract_features(X)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X_features, y, test_size=validation_split, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Train model
        self.model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_val_scaled, y_val)],
            early_stopping_rounds=10,
            verbose=False
        )
        
        # Evaluate
        y_pred = self.model.predict(X_val_scaled)
        metrics = {
            'mse': np.mean((y_val - y_pred) ** 2),
            'mae': np.mean(np.abs(y_val - y_pred)),
            'r2': self.model.score(X_val_scaled, y_val)
        }
        
        self.updated_at = datetime.now()
        self.metadata['last_training_metrics'] = metrics
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict risk scores."""
        X_features = self.extract_features(X)
        X_scaled = self.scaler.transform(X_features)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict risk probabilities (for binary risk classification)."""
        # Convert regression predictions to probabilities
        predictions = self.predict(X)
        # Normalize to [0, 1] range
        predictions = (predictions - predictions.min()) / (predictions.max() - predictions.min())
        return np.column_stack([1 - predictions, predictions])


class ClassificationModel(BaseModel):
    """
    Hybrid classification model using zero-shot LLM + fallback ML.
    
    Supports:
    - Claim type classification
    - Urgency classification
    - Fraud detection
    """
    
    def __init__(self, model_name: str = "classification_model"):
        super().__init__(model_name, "classification")
        
        # Zero-shot classifier
        if ZERO_SHOT_AVAILABLE:
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
        else:
            self.zero_shot_classifier = None
        
        # Fallback ML model
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.ml_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoder = LabelEncoder()
        
        # Classification categories
        self.claim_types = [
            "auto_collision", "auto_theft", "auto_comprehensive",
            "health_medical", "health_dental", "health_vision",
            "property_damage", "property_theft", "property_liability",
            "life_insurance", "disability", "fraud"
        ]
        
        self.urgency_levels = ["low", "medium", "high", "critical"]
    
    def classify_claim_type(self, claim_text: str, confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """Classify claim type using zero-shot LLM with fallback."""
        try:
            if self.zero_shot_classifier and confidence_threshold > 0.5:
                # Use zero-shot classification
                result = self.zero_shot_classifier(
                    claim_text,
                    candidate_labels=self.claim_types,
                    hypothesis_template="This is a {} claim."
                )
                
                if result['scores'][0] >= confidence_threshold:
                    return {
                        'prediction': result['labels'][0],
                        'confidence': result['scores'][0],
                        'method': 'zero_shot',
                        'all_scores': dict(zip(result['labels'], result['scores']))
                    }
        except Exception as e:
            print(f"Zero-shot classification failed: {e}")
        
        # Fallback to ML model
        if hasattr(self, 'ml_model_trained') and self.ml_model_trained:
            features = self.vectorizer.transform([claim_text])
            prediction = self.ml_classifier.predict(features)[0]
            confidence = np.max(self.ml_classifier.predict_proba(features))
            
            return {
                'prediction': self.label_encoder.inverse_transform([prediction])[0],
                'confidence': confidence,
                'method': 'ml_fallback',
                'all_scores': {}
            }
        
        # Default fallback
        return {
            'prediction': 'auto_collision',  # Most common type
            'confidence': 0.5,
            'method': 'default',
            'all_scores': {}
        }
    
    def classify_urgency(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify urgency level based on claim characteristics."""
        urgency_score = 0
        
        # Claim amount factor
        claim_amount = claim_data.get('claim_amount', 0)
        if claim_amount > 50000:
            urgency_score += 3
        elif claim_amount > 20000:
            urgency_score += 2
        elif claim_amount > 5000:
            urgency_score += 1
        
        # Injury factor
        if claim_data.get('injuries_involved', False):
            urgency_score += 2
        
        # Time sensitivity
        if claim_data.get('time_sensitive', False):
            urgency_score += 1
        
        # Customer priority
        if claim_data.get('customer_priority', False):
            urgency_score += 1
        
        # Map score to urgency level
        if urgency_score >= 4:
            urgency_level = "critical"
            confidence = 0.9
        elif urgency_score >= 2:
            urgency_level = "high"
            confidence = 0.8
        elif urgency_score >= 1:
            urgency_level = "medium"
            confidence = 0.7
        else:
            urgency_level = "low"
            confidence = 0.6
        
        return {
            'prediction': urgency_level,
            'confidence': confidence,
            'urgency_score': urgency_score,
            'method': 'rule_based'
        }
    
    def train_ml_fallback(self, texts: List[str], labels: List[str]) -> Dict[str, float]:
        """Train the ML fallback model."""
        # Encode labels
        encoded_labels = self.label_encoder.fit_transform(labels)
        
        # Vectorize texts
        X = self.vectorizer.fit_transform(texts)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, encoded_labels, test_size=0.2, random_state=42
        )
        
        # Train model
        self.ml_classifier.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.ml_classifier.predict(X_val)
        accuracy = self.ml_classifier.score(X_val, y_val)
        
        metrics = {
            'accuracy': accuracy,
            'classification_report': classification_report(y_val, y_pred)
        }
        
        self.ml_model_trained = True
        self.updated_at = datetime.now()
        self.metadata['ml_fallback_metrics'] = metrics
        
        return metrics


class ModelVersion:
    """Represents a versioned model."""
    
    def __init__(self, model_id: str, version: str, model_path: str, metadata: Dict[str, Any]):
        self.model_id = model_id
        self.version = version
        self.model_path = model_path
        self.metadata = metadata
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_id': self.model_id,
            'version': self.version,
            'model_path': self.model_path,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }


class ModelRegistry:
    """Simple file-based model registry."""
    
    def __init__(self, registry_path: str = "ml/models"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.registry_path / "registry.json"
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load registry from file."""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {"models": {}, "versions": {}}
    
    def _save_registry(self) -> None:
        """Save registry to file."""
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_model(self, model: BaseModel, version: str, metrics: Dict[str, float]) -> str:
        """Register a new model version."""
        model_id = f"{model.model_name}_{model.model_type}"
        
        # Save model
        model_path = self.registry_path / f"{model_id}_v{version}"
        model.save(str(model_path))
        
        # Create version record
        version_record = ModelVersion(
            model_id=model_id,
            version=version,
            model_path=str(model_path),
            metadata={
                'metrics': metrics,
                'feature_names': model.feature_names,
                'model_metadata': model.metadata
            }
        )
        
        # Update registry
        if model_id not in self.registry["models"]:
            self.registry["models"][model_id] = {
                'name': model.model_name,
                'type': model.model_type,
                'versions': []
            }
        
        self.registry["models"][model_id]["versions"].append(version_record.to_dict())
        self.registry["versions"][f"{model_id}_v{version}"] = version_record.to_dict()
        
        self._save_registry()
        return f"{model_id}_v{version}"
    
    def get_model(self, model_id: str, version: str = None) -> Optional[BaseModel]:
        """Get a model by ID and version."""
        if version is None:
            # Get latest version
            model_info = self.registry["models"].get(model_id)
            if not model_info or not model_info["versions"]:
                return None
            version = model_info["versions"][-1]["version"]
        
        version_id = f"{model_id}_v{version}"
        version_info = self.registry["versions"].get(version_id)
        
        if not version_info:
            return None
        
        # Load model based on type
        if "risk" in model_id:
            model = RiskModel()
        elif "classification" in model_id:
            model = ClassificationModel()
        else:
            return None
        
        model.load(version_info["model_path"])
        return model
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all registered models."""
        return list(self.registry["models"].values())
    
    def list_versions(self, model_id: str) -> List[Dict[str, Any]]:
        """List all versions of a model."""
        model_info = self.registry["models"].get(model_id)
        if not model_info:
            return []
        return model_info["versions"]
