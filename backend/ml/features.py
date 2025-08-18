"""
Feature store and feature extraction for Claims Triage AI.

This module provides:
- Feature extraction from raw claim data
- Feature store for caching and serving features
- Feature pipeline for automated feature engineering
- Feature versioning and metadata tracking
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import redis

from ..core.config import settings


class FeatureExtractor:
    """Extracts features from raw claim data."""
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.vectorizers = {}
        self.feature_metadata = {}
    
    def extract_claim_features(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all features from a single claim."""
        features = {}
        
        # Basic numerical features
        features.update(self._extract_numerical_features(claim_data))
        
        # Categorical features
        features.update(self._extract_categorical_features(claim_data))
        
        # Text features
        features.update(self._extract_text_features(claim_data))
        
        # Temporal features
        features.update(self._extract_temporal_features(claim_data))
        
        # Derived features
        features.update(self._extract_derived_features(claim_data))
        
        return features
    
    def _extract_numerical_features(self, claim_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical features."""
        features = {}
        
        # Direct numerical features
        features['claim_amount'] = float(claim_data.get('claim_amount', 0))
        features['policy_duration'] = float(claim_data.get('policy_duration', 0))
        features['customer_age'] = float(claim_data.get('customer_age', 0))
        features['deductible'] = float(claim_data.get('deductible', 0))
        
        # Calculated features
        features['claim_to_policy_ratio'] = (
            features['claim_amount'] / max(features['policy_duration'], 1)
        )
        features['amount_to_deductible_ratio'] = (
            features['claim_amount'] / max(features['deductible'], 1)
        )
        
        return features
    
    def _extract_categorical_features(self, claim_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract categorical features."""
        features = {}
        
        features['claim_type'] = claim_data.get('claim_type', 'unknown')
        features['state'] = claim_data.get('state', 'unknown')
        features['customer_tier'] = claim_data.get('customer_tier', 'standard')
        features['policy_type'] = claim_data.get('policy_type', 'standard')
        
        return features
    
    def _extract_text_features(self, claim_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract text features."""
        features = {}
        
        # Combine all text fields
        text_fields = [
            claim_data.get('description', ''),
            claim_data.get('notes', ''),
            claim_data.get('customer_comments', '')
        ]
        
        features['combined_text'] = ' '.join(filter(None, text_fields))
        features['text_length'] = len(features['combined_text'])
        
        return features
    
    def _extract_temporal_features(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract temporal features."""
        features = {}
        
        claim_date = claim_data.get('claim_date')
        if claim_date:
            if isinstance(claim_date, str):
                claim_date = pd.to_datetime(claim_date)
            
            features['claim_day_of_week'] = claim_date.dayofweek
            features['claim_month'] = claim_date.month
            features['claim_quarter'] = claim_date.quarter
            features['claim_hour'] = claim_date.hour if hasattr(claim_date, 'hour') else 12
        else:
            features['claim_day_of_week'] = 0
            features['claim_month'] = 1
            features['claim_quarter'] = 1
            features['claim_hour'] = 12
        
        return features
    
    def _extract_derived_features(self, claim_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract derived/computed features."""
        features = {}
        
        # Risk indicators
        features['high_value_claim'] = float(claim_data.get('claim_amount', 0) > 10000)
        features['injury_claim'] = float(claim_data.get('injuries_involved', False))
        features['multi_vehicle'] = float(claim_data.get('multi_vehicle', False))
        features['hit_and_run'] = float(claim_data.get('hit_and_run', False))
        
        # Document completeness
        required_docs = ['police_report', 'medical_records', 'photos', 'estimates']
        docs_present = sum(1 for doc in required_docs if claim_data.get(doc))
        features['document_completeness'] = docs_present / len(required_docs)
        
        # Urgency indicators
        urgency_score = 0
        urgency_score += float(claim_data.get('time_sensitive', False))
        urgency_score += float(claim_data.get('customer_priority', False))
        urgency_score += float(claim_data.get('injuries_involved', False))
        features['urgency_score'] = urgency_score
        
        return features
    
    def fit_transform_batch(self, claims_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Fit feature extractors and transform batch of claims."""
        # Extract features for all claims
        features_list = [self.extract_claim_features(claim) for claim in claims_data]
        features_df = pd.DataFrame(features_list)
        
        # Fit and transform numerical features
        numerical_cols = features_df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            if col not in self.scalers:
                self.scalers[col] = StandardScaler()
                features_df[col] = self.scalers[col].fit_transform(features_df[[col]])
            else:
                features_df[col] = self.scalers[col].transform(features_df[[col]])
        
        # Fit and transform categorical features
        categorical_cols = features_df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
                features_df[col] = self.encoders[col].fit_transform(features_df[col])
            else:
                # Handle unseen categories
                features_df[col] = features_df[col].map(
                    lambda x: self.encoders[col].transform([x])[0] 
                    if x in self.encoders[col].classes_ 
                    else -1
                )
        
        # Fit and transform text features
        if 'combined_text' in features_df.columns:
            if 'text_vectorizer' not in self.vectorizers:
                self.vectorizers['text_vectorizer'] = TfidfVectorizer(
                    max_features=100,
                    stop_words='english'
                )
                text_features = self.vectorizers['text_vectorizer'].fit_transform(
                    features_df['combined_text']
                )
            else:
                text_features = self.vectorizers['text_vectorizer'].transform(
                    features_df['combined_text']
                )
            
            # Add text features to dataframe
            text_feature_names = [
                f'text_feature_{i}' for i in range(text_features.shape[1])
            ]
            text_df = pd.DataFrame(
                text_features.toarray(),
                columns=text_feature_names,
                index=features_df.index
            )
            features_df = pd.concat([features_df, text_df], axis=1)
        
        # Store feature metadata
        self.feature_metadata = {
            'feature_names': list(features_df.columns),
            'numerical_features': list(numerical_cols),
            'categorical_features': list(categorical_cols),
            'text_features': text_feature_names if 'combined_text' in features_df.columns else [],
            'created_at': datetime.now().isoformat()
        }
        
        return features_df
    
    def transform(self, claims_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transform batch of claims using fitted extractors."""
        # Extract features for all claims
        features_list = [self.extract_claim_features(claim) for claim in claims_data]
        features_df = pd.DataFrame(features_list)
        
        # Transform numerical features
        numerical_cols = features_df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            if col in self.scalers:
                features_df[col] = self.scalers[col].transform(features_df[[col]])
        
        # Transform categorical features
        categorical_cols = features_df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col in self.encoders:
                features_df[col] = features_df[col].map(
                    lambda x: self.encoders[col].transform([x])[0] 
                    if x in self.encoders[col].classes_ 
                    else -1
                )
        
        # Transform text features
        if 'combined_text' in features_df.columns and 'text_vectorizer' in self.vectorizers:
            text_features = self.vectorizers['text_vectorizer'].transform(
                features_df['combined_text']
            )
            
            text_feature_names = [
                f'text_feature_{i}' for i in range(text_features.shape[1])
            ]
            text_df = pd.DataFrame(
                text_features.toarray(),
                columns=text_feature_names,
                index=features_df.index
            )
            features_df = pd.concat([features_df, text_df], axis=1)
        
        return features_df
    
    def save(self, path: str) -> None:
        """Save feature extractor to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(f"{path}.pkl", "wb") as f:
            pickle.dump({
                'scalers': self.scalers,
                'encoders': self.encoders,
                'vectorizers': self.vectorizers,
                'feature_metadata': self.feature_metadata
            }, f)
    
    def load(self, path: str) -> None:
        """Load feature extractor from disk."""
        with open(f"{path}.pkl", "rb") as f:
            data = pickle.load(f)
            self.scalers = data['scalers']
            self.encoders = data['encoders']
            self.vectorizers = data['vectorizers']
            self.feature_metadata = data['feature_metadata']


class FeatureStore:
    """Simple feature store for caching and serving features."""
    
    def __init__(self, redis_url: str = None, cache_ttl: int = 3600):
        self.redis_url = redis_url or settings.redis_url
        self.cache_ttl = cache_ttl
        self.redis_client = None
        self._connect_redis()
    
    def _connect_redis(self) -> None:
        """Connect to Redis."""
        try:
            import redis
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.redis_client = None
    
    def _get_feature_key(self, claim_id: str, feature_set: str = "default") -> str:
        """Generate Redis key for features."""
        return f"features:{feature_set}:{claim_id}"
    
    def store_features(self, claim_id: str, features: Dict[str, Any], 
                      feature_set: str = "default") -> bool:
        """Store features for a claim."""
        if not self.redis_client:
            return False
        
        try:
            key = self._get_feature_key(claim_id, feature_set)
            # Store as JSON for easy retrieval
            self.redis_client.setex(
                key,
                self.cache_ttl,
                json.dumps(features, default=str)
            )
            return True
        except Exception as e:
            print(f"Failed to store features: {e}")
            return False
    
    def get_features(self, claim_id: str, feature_set: str = "default") -> Optional[Dict[str, Any]]:
        """Get features for a claim."""
        if not self.redis_client:
            return None
        
        try:
            key = self._get_feature_key(claim_id, feature_set)
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Failed to get features: {e}")
            return None
    
    def store_batch_features(self, features_dict: Dict[str, Dict[str, Any]], 
                           feature_set: str = "default") -> int:
        """Store features for multiple claims."""
        if not self.redis_client:
            return 0
        
        try:
            pipeline = self.redis_client.pipeline()
            for claim_id, features in features_dict.items():
                key = self._get_feature_key(claim_id, feature_set)
                pipeline.setex(
                    key,
                    self.cache_ttl,
                    json.dumps(features, default=str)
                )
            pipeline.execute()
            return len(features_dict)
        except Exception as e:
            print(f"Failed to store batch features: {e}")
            return 0
    
    def get_batch_features(self, claim_ids: List[str], 
                          feature_set: str = "default") -> Dict[str, Dict[str, Any]]:
        """Get features for multiple claims."""
        if not self.redis_client:
            return {}
        
        try:
            keys = [self._get_feature_key(claim_id, feature_set) for claim_id in claim_ids]
            pipeline = self.redis_client.pipeline()
            for key in keys:
                pipeline.get(key)
            results = pipeline.execute()
            
            features_dict = {}
            for claim_id, result in zip(claim_ids, results):
                if result:
                    features_dict[claim_id] = json.loads(result)
            
            return features_dict
        except Exception as e:
            print(f"Failed to get batch features: {e}")
            return {}
    
    def delete_features(self, claim_id: str, feature_set: str = "default") -> bool:
        """Delete features for a claim."""
        if not self.redis_client:
            return False
        
        try:
            key = self._get_feature_key(claim_id, feature_set)
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Failed to delete features: {e}")
            return False
    
    def clear_feature_set(self, feature_set: str = "default") -> int:
        """Clear all features for a feature set."""
        if not self.redis_client:
            return 0
        
        try:
            pattern = f"features:{feature_set}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Failed to clear feature set: {e}")
            return 0
    
    def get_feature_stats(self) -> Dict[str, Any]:
        """Get feature store statistics."""
        if not self.redis_client:
            return {"error": "Redis not connected"}
        
        try:
            stats = {
                "total_keys": self.redis_client.dbsize(),
                "feature_sets": {}
            }
            
            # Count keys by feature set
            for key in self.redis_client.scan_iter(match="features:*"):
                parts = key.decode().split(":")
                if len(parts) >= 3:
                    feature_set = parts[1]
                    if feature_set not in stats["feature_sets"]:
                        stats["feature_sets"][feature_set] = 0
                    stats["feature_sets"][feature_set] += 1
            
            return stats
        except Exception as e:
            return {"error": str(e)}


class FeaturePipeline:
    """Orchestrates feature extraction and storage."""
    
    def __init__(self, feature_store: FeatureStore = None):
        self.feature_extractor = FeatureExtractor()
        self.feature_store = feature_store or FeatureStore()
        self.pipeline_metadata = {}
    
    def process_claims(self, claims_data: List[Dict[str, Any]], 
                      fit_extractor: bool = True) -> pd.DataFrame:
        """Process claims through the feature pipeline."""
        # Extract claim IDs
        claim_ids = [claim.get('claim_id', f'claim_{i}') for i, claim in enumerate(claims_data)]
        
        # Extract features
        if fit_extractor:
            features_df = self.feature_extractor.fit_transform_batch(claims_data)
        else:
            features_df = self.feature_extractor.transform(claims_data)
        
        # Store features in feature store
        features_dict = features_df.to_dict('index')
        for i, claim_id in enumerate(claim_ids):
            self.feature_store.store_features(claim_id, features_dict[i])
        
        # Update pipeline metadata
        self.pipeline_metadata.update({
            'last_processed_count': len(claims_data),
            'last_processed_at': datetime.now().isoformat(),
            'feature_count': len(features_df.columns),
            'extractor_fitted': fit_extractor
        })
        
        return features_df
    
    def get_features_for_claims(self, claim_ids: List[str]) -> pd.DataFrame:
        """Get features for specific claims."""
        # Try to get from feature store first
        cached_features = self.feature_store.get_batch_features(claim_ids)
        
        # For missing features, we would need to re-extract
        # This is a simplified version - in production you'd want to handle this
        missing_ids = [cid for cid in claim_ids if cid not in cached_features]
        
        if missing_ids:
            print(f"Warning: Missing features for {len(missing_ids)} claims")
        
        # Convert to DataFrame
        features_list = []
        for claim_id in claim_ids:
            if claim_id in cached_features:
                features_list.append(cached_features[claim_id])
            else:
                # Add empty features for missing claims
                features_list.append({})
        
        return pd.DataFrame(features_list)
    
    def save_pipeline(self, path: str) -> None:
        """Save the entire feature pipeline."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save feature extractor
        self.feature_extractor.save(f"{path}_extractor")
        
        # Save pipeline metadata
        with open(f"{path}_metadata.json", "w") as f:
            json.dump(self.pipeline_metadata, f, indent=2)
    
    def load_pipeline(self, path: str) -> None:
        """Load the entire feature pipeline."""
        # Load feature extractor
        self.feature_extractor.load(f"{path}_extractor")
        
        # Load pipeline metadata
        with open(f"{path}_metadata.json", "r") as f:
            self.pipeline_metadata = json.load(f)
