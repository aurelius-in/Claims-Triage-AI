"""
Risk Scorer Agent for calculating case risk scores and providing explanations.
"""

import time
import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
import pandas as pd
import joblib
import os
import json

from ..core.config import settings
from ..data.schemas import RiskLevel, AgentResult

logger = logging.getLogger(__name__)


@dataclass
class RiskScoreResult:
    """Result of risk scoring."""
    risk_score: float  # 0-1 scale
    risk_level: RiskLevel
    confidence: float
    rationale: str
    top_features: List[Dict[str, Any]]  # SHAP feature importance
    risk_factors: List[str]
    processing_time_ms: int


class RiskScorerAgent:
    """
    Agent responsible for calculating risk scores and providing explanations.
    
    Features:
    - ML-based risk scoring using XGBoost
    - SHAP explanations for interpretability
    - Rule-based risk factor identification
    - Confidence scoring
    """
    
    def __init__(self):
        self.model_path = os.path.join(settings.model_registry_path, "risk_scorer")
        self.risk_threshold_high = settings.risk_threshold_high
        self.risk_threshold_medium = settings.risk_threshold_medium
        
        # Load ML model and feature processor
        self._load_ml_model()
        
        # Risk factor patterns
        self.risk_patterns = {
            "fraud_indicators": [
                "suspicious", "unusual", "unexpected", "anomaly", "irregular",
                "duplicate", "multiple claims", "recent policy", "high amount"
            ],
            "urgency_indicators": [
                "emergency", "urgent", "immediate", "critical", "time-sensitive",
                "deadline", "escalation", "complaint"
            ],
            "complexity_indicators": [
                "complex", "complicated", "multiple parties", "legal", "litigation",
                "dispute", "appeal", "review", "investigation"
            ],
            "financial_indicators": [
                "high value", "large amount", "expensive", "costly", "premium",
                "deductible", "coverage", "policy limit"
            ]
        }
    
    def _load_ml_model(self):
        """Load pre-trained risk scoring model."""
        try:
            # Load XGBoost model
            self.risk_model = joblib.load(
                os.path.join(self.model_path, "risk_scorer_xgb.pkl")
            )
            
            # Load feature processor
            self.feature_processor = joblib.load(
                os.path.join(self.model_path, "feature_processor.pkl")
            )
            
            # Load SHAP explainer
            self.shap_explainer = joblib.load(
                os.path.join(self.model_path, "shap_explainer.pkl")
            )
            
            # Load feature names
            with open(os.path.join(self.model_path, "feature_names.json"), "r") as f:
                self.feature_names = json.load(f)
            
            logger.info("Risk scoring model loaded successfully")
            
        except FileNotFoundError:
            logger.warning("Risk scoring model not found, using rule-based scoring only")
            self.risk_model = None
            self.feature_processor = None
            self.shap_explainer = None
            self.feature_names = None
    
    async def score_risk(self, case_data: Dict[str, Any], 
                        classification_result: Dict[str, Any]) -> RiskScoreResult:
        """
        Calculate risk score for a case.
        
        Args:
            case_data: Dictionary containing case information
            classification_result: Results from ClassifierAgent
        
        Returns:
            RiskScoreResult with risk score and explanations
        """
        start_time = time.time()
        
        try:
            # Extract features
            features = self._extract_features(case_data, classification_result)
            
            # Calculate risk score using ML model
            if self.risk_model is not None:
                ml_result = self._score_with_ml(features)
            else:
                ml_result = None
            
            # Calculate risk score using rules
            rule_result = self._score_with_rules(case_data, classification_result)
            
            # Combine results
            final_result = self._combine_risk_scores(ml_result, rule_result, features)
            
            processing_time = int((time.time() - start_time) * 1000)
            return RiskScoreResult(
                risk_score=final_result.risk_score,
                risk_level=final_result.risk_level,
                confidence=final_result.confidence,
                rationale=final_result.rationale,
                top_features=final_result.top_features,
                risk_factors=final_result.risk_factors,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Risk scoring failed: {str(e)}")
            # Return safe defaults
            processing_time = int((time.time() - start_time) * 1000)
            return RiskScoreResult(
                risk_score=0.5,
                risk_level=RiskLevel.MEDIUM,
                confidence=0.5,
                rationale=f"Risk scoring failed: {str(e)}",
                top_features=[],
                risk_factors=["scoring_error"],
                processing_time_ms=processing_time
            )
    
    def _extract_features(self, case_data: Dict[str, Any], 
                         classification_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features for risk scoring."""
        features = {}
        
        # Text-based features
        text = self._extract_text(case_data)
        features["text_length"] = len(text)
        features["word_count"] = len(text.split())
        
        # Case type features
        case_type = classification_result.get("case_type", "insurance_claim")
        features["case_type_insurance"] = 1 if case_type == "insurance_claim" else 0
        features["case_type_healthcare"] = 1 if case_type == "healthcare_prior_auth" else 0
        features["case_type_bank"] = 1 if case_type == "bank_dispute" else 0
        features["case_type_legal"] = 1 if case_type == "legal_intake" else 0
        features["case_type_fraud"] = 1 if case_type == "fraud_review" else 0
        
        # Urgency features
        urgency = classification_result.get("urgency", "medium")
        features["urgency_critical"] = 1 if urgency == "critical" else 0
        features["urgency_high"] = 1 if urgency == "high" else 0
        features["urgency_medium"] = 1 if urgency == "medium" else 0
        features["urgency_low"] = 1 if urgency == "low" else 0
        
        # Financial features
        amount = case_data.get("amount", 0)
        features["amount"] = float(amount) if amount else 0
        features["amount_log"] = np.log1p(features["amount"])
        features["has_amount"] = 1 if amount else 0
        
        # Customer features
        customer_id = case_data.get("customer_id")
        features["has_customer_id"] = 1 if customer_id else 0
        features["customer_id_length"] = len(str(customer_id)) if customer_id else 0
        
        # Metadata features
        metadata = case_data.get("metadata", {})
        features["metadata_count"] = len(metadata)
        features["has_attachments"] = 1 if case_data.get("attachments") else 0
        
        # Risk pattern features
        risk_factors = self._identify_risk_patterns(text)
        features["fraud_indicators"] = len(risk_factors.get("fraud_indicators", []))
        features["urgency_indicators"] = len(risk_factors.get("urgency_indicators", []))
        features["complexity_indicators"] = len(risk_factors.get("complexity_indicators", []))
        features["financial_indicators"] = len(risk_factors.get("financial_indicators", []))
        
        # Missing fields features
        missing_fields = classification_result.get("missing_fields", [])
        features["missing_fields_count"] = len(missing_fields)
        features["has_missing_fields"] = 1 if missing_fields else 0
        
        return features
    
    def _extract_text(self, case_data: Dict[str, Any]) -> str:
        """Extract and combine text from case data."""
        text_parts = []
        
        if case_data.get("title"):
            text_parts.append(case_data["title"])
        
        if case_data.get("description"):
            text_parts.append(case_data["description"])
        
        # Add metadata text if available
        metadata = case_data.get("metadata", {})
        for key, value in metadata.items():
            if isinstance(value, str):
                text_parts.append(f"{key}: {value}")
        
        return " ".join(text_parts).lower()
    
    def _identify_risk_patterns(self, text: str) -> Dict[str, List[str]]:
        """Identify risk patterns in text."""
        risk_factors = {}
        
        for pattern_type, keywords in self.risk_patterns.items():
            found_keywords = []
            for keyword in keywords:
                if keyword in text:
                    found_keywords.append(keyword)
            risk_factors[pattern_type] = found_keywords
        
        return risk_factors
    
    def _score_with_ml(self, features: Dict[str, Any]) -> RiskScoreResult:
        """Calculate risk score using ML model."""
        try:
            # Convert features to DataFrame
            feature_df = pd.DataFrame([features])
            
            # Process features
            if self.feature_processor:
                processed_features = self.feature_processor.transform(feature_df)
            else:
                processed_features = feature_df.values
            
            # Predict risk score
            risk_score = self.risk_model.predict_proba(processed_features)[0][1]
            
            # Get SHAP explanations
            if self.shap_explainer:
                shap_values = self.shap_explainer.shap_values(processed_features)
                feature_importance = self._extract_shap_importance(
                    shap_values[0], self.feature_names
                )
            else:
                feature_importance = []
            
            # Determine risk level
            risk_level = self._score_to_risk_level(risk_score)
            
            # Identify risk factors
            risk_factors = self._extract_risk_factors(features)
            
            return RiskScoreResult(
                risk_score=risk_score,
                risk_level=risk_level,
                confidence=0.9,  # High confidence for ML model
                rationale=f"ML-based risk scoring (XGBoost model)",
                top_features=feature_importance,
                risk_factors=risk_factors,
                processing_time_ms=0
            )
            
        except Exception as e:
            logger.warning(f"ML risk scoring failed: {str(e)}")
            return None
    
    def _score_with_rules(self, case_data: Dict[str, Any], 
                         classification_result: Dict[str, Any]) -> RiskScoreResult:
        """Calculate risk score using rule-based approach."""
        risk_score = 0.0
        risk_factors = []
        
        # Base risk from case type
        case_type = classification_result.get("case_type", "insurance_claim")
        if case_type == "fraud_review":
            risk_score += 0.4
            risk_factors.append("fraud_review_case")
        elif case_type == "legal_intake":
            risk_score += 0.3
            risk_factors.append("legal_case")
        elif case_type == "bank_dispute":
            risk_score += 0.25
            risk_factors.append("bank_dispute")
        
        # Risk from urgency
        urgency = classification_result.get("urgency", "medium")
        if urgency == "critical":
            risk_score += 0.3
            risk_factors.append("critical_urgency")
        elif urgency == "high":
            risk_score += 0.2
            risk_factors.append("high_urgency")
        
        # Risk from amount
        amount = case_data.get("amount", 0)
        if amount:
            if amount > 10000:
                risk_score += 0.2
                risk_factors.append("high_amount")
            elif amount > 5000:
                risk_score += 0.1
                risk_factors.append("medium_amount")
        
        # Risk from missing fields
        missing_fields = classification_result.get("missing_fields", [])
        if len(missing_fields) > 3:
            risk_score += 0.15
            risk_factors.append("many_missing_fields")
        elif missing_fields:
            risk_score += 0.05
            risk_factors.append("missing_fields")
        
        # Risk from text patterns
        text = self._extract_text(case_data)
        risk_patterns = self._identify_risk_patterns(text)
        
        if risk_patterns["fraud_indicators"]:
            risk_score += 0.2
            risk_factors.append("fraud_indicators")
        
        if risk_patterns["complexity_indicators"]:
            risk_score += 0.1
            risk_factors.append("complexity_indicators")
        
        # Cap risk score at 1.0
        risk_score = min(1.0, risk_score)
        
        # Determine risk level
        risk_level = self._score_to_risk_level(risk_score)
        
        # Create feature importance for rules
        feature_importance = [
            {"feature": factor, "importance": 0.1} for factor in risk_factors
        ]
        
        return RiskScoreResult(
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=0.7,  # Medium confidence for rules
            rationale=f"Rule-based risk scoring based on {len(risk_factors)} risk factors",
            top_features=feature_importance,
            risk_factors=risk_factors,
            processing_time_ms=0
        )
    
    def _combine_risk_scores(self, ml_result: Optional[RiskScoreResult], 
                           rule_result: RiskScoreResult,
                           features: Dict[str, Any]) -> RiskScoreResult:
        """Combine ML and rule-based risk scores."""
        if not ml_result:
            return rule_result
        
        # Weighted combination (favor ML if available)
        ml_weight = 0.7
        rule_weight = 0.3
        
        combined_score = (ml_result.risk_score * ml_weight + 
                         rule_result.risk_score * rule_weight)
        
        # Combine risk factors
        combined_factors = list(set(ml_result.risk_factors + rule_result.risk_factors))
        
        # Use ML feature importance if available
        top_features = ml_result.top_features if ml_result.top_features else rule_result.top_features
        
        # Determine risk level
        risk_level = self._score_to_risk_level(combined_score)
        
        # Calculate combined confidence
        combined_confidence = (ml_result.confidence * ml_weight + 
                             rule_result.confidence * rule_weight)
        
        return RiskScoreResult(
            risk_score=combined_score,
            risk_level=risk_level,
            confidence=combined_confidence,
            rationale=f"Combined ML ({ml_result.risk_score:.2f}) and rule-based ({rule_result.risk_score:.2f}) scoring",
            top_features=top_features,
            risk_factors=combined_factors,
            processing_time_ms=0
        )
    
    def _score_to_risk_level(self, risk_score: float) -> RiskLevel:
        """Convert risk score to risk level."""
        if risk_score >= self.risk_threshold_high:
            return RiskLevel.HIGH
        elif risk_score >= self.risk_threshold_medium:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _extract_shap_importance(self, shap_values: np.ndarray, 
                                feature_names: List[str]) -> List[Dict[str, Any]]:
        """Extract top features from SHAP values."""
        if len(shap_values) != len(feature_names):
            return []
        
        # Create feature importance pairs
        feature_importance = []
        for i, (shap_value, feature_name) in enumerate(zip(shap_values, feature_names)):
            feature_importance.append({
                "feature": feature_name,
                "importance": abs(shap_value),
                "direction": "positive" if shap_value > 0 else "negative"
            })
        
        # Sort by importance and return top 10
        feature_importance.sort(key=lambda x: x["importance"], reverse=True)
        return feature_importance[:10]
    
    def _extract_risk_factors(self, features: Dict[str, Any]) -> List[str]:
        """Extract risk factors from features."""
        risk_factors = []
        
        if features.get("case_type_fraud"):
            risk_factors.append("fraud_case_type")
        
        if features.get("urgency_critical"):
            risk_factors.append("critical_urgency")
        elif features.get("urgency_high"):
            risk_factors.append("high_urgency")
        
        if features.get("amount", 0) > 10000:
            risk_factors.append("high_amount")
        
        if features.get("fraud_indicators", 0) > 0:
            risk_factors.append("fraud_indicators")
        
        if features.get("complexity_indicators", 0) > 0:
            risk_factors.append("complexity_indicators")
        
        if features.get("missing_fields_count", 0) > 3:
            risk_factors.append("many_missing_fields")
        
        return risk_factors
    
    def to_agent_result(self, result: RiskScoreResult) -> AgentResult:
        """Convert risk score result to agent result format."""
        return AgentResult(
            agent_name="RiskScorerAgent",
            confidence=result.confidence,
            result={
                "risk_score": result.risk_score,
                "risk_level": result.risk_level.value,
                "risk_factors": result.risk_factors,
                "top_features": result.top_features
            },
            reasoning=result.rationale,
            processing_time_ms=result.processing_time_ms
        )
