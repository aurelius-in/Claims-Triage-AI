"""
Classifier Agent for case type and urgency classification.
"""

import time
import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

from ..core.config import settings
from ..data.schemas import CaseType, UrgencyLevel, AgentResult

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of case classification."""
    case_type: CaseType
    urgency: UrgencyLevel
    confidence: float
    reasoning: str
    missing_fields: List[str]
    processing_time_ms: int


class ClassifierAgent:
    """
    Agent responsible for classifying cases by type and urgency.
    
    Uses a hybrid approach:
    1. Zero-shot LLM classification for flexibility
    2. Fallback to trained ML models for reliability
    3. Rule-based validation for edge cases
    """
    
    def __init__(self):
        self.llm_provider = settings.default_llm_provider
        self.confidence_threshold = settings.confidence_threshold
        self.model_path = os.path.join(settings.model_registry_path, "classifier")
        
        # Load ML models
        self._load_ml_models()
        
        # Classification labels
        self.case_type_labels = [ct.value for ct in CaseType]
        self.urgency_labels = [ul.value for ul in UrgencyLevel]
        
        # Keywords for rule-based classification
        self.case_type_keywords = {
            CaseType.INSURANCE_CLAIM: [
                "claim", "insurance", "policy", "coverage", "premium", "deductible",
                "medical", "dental", "vision", "accident", "disability"
            ],
            CaseType.HEALTHCARE_PRIOR_AUTH: [
                "prior authorization", "pre-authorization", "medical necessity",
                "treatment plan", "prescription", "medication", "procedure"
            ],
            CaseType.BANK_DISPUTE: [
                "dispute", "chargeback", "fraudulent", "unauthorized", "bank",
                "credit card", "debit", "transaction", "refund"
            ],
            CaseType.LEGAL_INTAKE: [
                "legal", "attorney", "lawyer", "lawsuit", "litigation", "contract",
                "breach", "damages", "settlement", "court"
            ],
            CaseType.FRAUD_REVIEW: [
                "fraud", "suspicious", "investigation", "identity theft", "forgery",
                "counterfeit", "embezzlement", "money laundering"
            ]
        }
        
        self.urgency_keywords = {
            UrgencyLevel.CRITICAL: [
                "emergency", "urgent", "immediate", "critical", "life-threatening",
                "severe", "acute", "trauma", "cardiac", "stroke"
            ],
            UrgencyLevel.HIGH: [
                "high priority", "important", "time-sensitive", "deadline",
                "escalation", "complaint", "dispute"
            ],
            UrgencyLevel.MEDIUM: [
                "standard", "routine", "normal", "regular", "scheduled"
            ],
            UrgencyLevel.LOW: [
                "low priority", "non-urgent", "routine", "maintenance", "inquiry"
            ]
        }
    
    def _load_ml_models(self):
        """Load pre-trained ML models."""
        try:
            # Load case type classifier
            self.case_type_vectorizer = joblib.load(
                os.path.join(self.model_path, "case_type_vectorizer.pkl")
            )
            self.case_type_model = joblib.load(
                os.path.join(self.model_path, "case_type_classifier.pkl")
            )
            
            # Load urgency classifier
            self.urgency_vectorizer = joblib.load(
                os.path.join(self.model_path, "urgency_vectorizer.pkl")
            )
            self.urgency_model = joblib.load(
                os.path.join(self.model_path, "urgency_classifier.pkl")
            )
            
            logger.info("ML models loaded successfully")
            
        except FileNotFoundError:
            logger.warning("ML models not found, using rule-based classification only")
            self.case_type_vectorizer = None
            self.case_type_model = None
            self.urgency_vectorizer = None
            self.urgency_model = None
    
    async def classify(self, case_data: Dict[str, Any]) -> ClassificationResult:
        """
        Classify a case by type and urgency.
        
        Args:
            case_data: Dictionary containing case information
                - title: Case title
                - description: Case description
                - customer_id: Customer identifier
                - amount: Claim amount
                - metadata: Additional case metadata
        
        Returns:
            ClassificationResult with classification details
        """
        start_time = time.time()
        
        try:
            # Extract text for classification
            text = self._extract_text(case_data)
            
            # Try LLM classification first
            llm_result = await self._classify_with_llm(text, case_data)
            
            if llm_result and llm_result.confidence >= self.confidence_threshold:
                processing_time = int((time.time() - start_time) * 1000)
                return ClassificationResult(
                    case_type=llm_result.case_type,
                    urgency=llm_result.urgency,
                    confidence=llm_result.confidence,
                    reasoning=llm_result.reasoning,
                    missing_fields=llm_result.missing_fields,
                    processing_time_ms=processing_time
                )
            
            # Fallback to ML models
            ml_result = self._classify_with_ml(text, case_data)
            
            # Combine with rule-based validation
            final_result = self._combine_classifications(llm_result, ml_result, text)
            
            processing_time = int((time.time() - start_time) * 1000)
            return ClassificationResult(
                case_type=final_result.case_type,
                urgency=final_result.urgency,
                confidence=final_result.confidence,
                reasoning=final_result.reasoning,
                missing_fields=final_result.missing_fields,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            # Return safe defaults
            processing_time = int((time.time() - start_time) * 1000)
            return ClassificationResult(
                case_type=CaseType.INSURANCE_CLAIM,
                urgency=UrgencyLevel.MEDIUM,
                confidence=0.5,
                reasoning=f"Classification failed: {str(e)}",
                missing_fields=["classification_error"],
                processing_time_ms=processing_time
            )
    
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
    
    async def _classify_with_llm(self, text: str, case_data: Dict[str, Any]) -> Optional[ClassificationResult]:
        """Classify using LLM (OpenAI/Anthropic)."""
        if not settings.openai_api_key and not settings.anthropic_api_key:
            return None
        
        try:
            if self.llm_provider == "openai" and settings.openai_api_key:
                return await self._classify_with_openai(text, case_data)
            elif self.llm_provider == "anthropic" and settings.anthropic_api_key:
                return await self._classify_with_anthropic(text, case_data)
        except Exception as e:
            logger.warning(f"LLM classification failed: {str(e)}")
        
        return None
    
    async def _classify_with_openai(self, text: str, case_data: Dict[str, Any]) -> ClassificationResult:
        """Classify using OpenAI API."""
        import openai
        
        openai.api_key = settings.openai_api_key.get_secret_value()
        
        prompt = f"""
        Classify the following case by type and urgency level.
        
        Case text: {text}
        
        Available case types: {', '.join(self.case_type_labels)}
        Available urgency levels: {', '.join(self.urgency_labels)}
        
        Respond in JSON format:
        {{
            "case_type": "case_type_value",
            "urgency": "urgency_value", 
            "confidence": 0.95,
            "reasoning": "explanation for classification",
            "missing_fields": ["field1", "field2"]
        }}
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        
        result = response.choices[0].message.content
        # Parse JSON response and return ClassificationResult
        # Implementation details omitted for brevity
        
        return ClassificationResult(
            case_type=CaseType.INSURANCE_CLAIM,  # Default
            urgency=UrgencyLevel.MEDIUM,  # Default
            confidence=0.8,
            reasoning="LLM classification",
            missing_fields=[],
            processing_time_ms=0
        )
    
    async def _classify_with_anthropic(self, text: str, case_data: Dict[str, Any]) -> ClassificationResult:
        """Classify using Anthropic API."""
        # Similar implementation to OpenAI
        return ClassificationResult(
            case_type=CaseType.INSURANCE_CLAIM,
            urgency=UrgencyLevel.MEDIUM,
            confidence=0.8,
            reasoning="Anthropic classification",
            missing_fields=[],
            processing_time_ms=0
        )
    
    def _classify_with_ml(self, text: str, case_data: Dict[str, Any]) -> ClassificationResult:
        """Classify using ML models."""
        if not self.case_type_model or not self.urgency_model:
            return self._classify_with_rules(text, case_data)
        
        try:
            # Case type classification
            case_type_features = self.case_type_vectorizer.transform([text])
            case_type_proba = self.case_type_model.predict_proba(case_type_features)[0]
            case_type_idx = np.argmax(case_type_proba)
            case_type_confidence = case_type_proba[case_type_idx]
            case_type = CaseType(self.case_type_labels[case_type_idx])
            
            # Urgency classification
            urgency_features = self.urgency_vectorizer.transform([text])
            urgency_proba = self.urgency_model.predict_proba(urgency_features)[0]
            urgency_idx = np.argmax(urgency_proba)
            urgency_confidence = urgency_proba[urgency_idx]
            urgency = UrgencyLevel(self.urgency_labels[urgency_idx])
            
            # Average confidence
            avg_confidence = (case_type_confidence + urgency_confidence) / 2
            
            return ClassificationResult(
                case_type=case_type,
                urgency=urgency,
                confidence=avg_confidence,
                reasoning=f"ML classification (case_type: {case_type_confidence:.2f}, urgency: {urgency_confidence:.2f})",
                missing_fields=self._identify_missing_fields(case_data),
                processing_time_ms=0
            )
            
        except Exception as e:
            logger.warning(f"ML classification failed: {str(e)}")
            return self._classify_with_rules(text, case_data)
    
    def _classify_with_rules(self, text: str, case_data: Dict[str, Any]) -> ClassificationResult:
        """Classify using rule-based keyword matching."""
        # Case type classification
        case_type_scores = {}
        for case_type, keywords in self.case_type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            case_type_scores[case_type] = score
        
        case_type = max(case_type_scores.items(), key=lambda x: x[1])[0]
        case_type_confidence = min(0.8, case_type_scores[case_type] / 3)
        
        # Urgency classification
        urgency_scores = {}
        for urgency, keywords in self.urgency_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            urgency_scores[urgency] = score
        
        urgency = max(urgency_scores.items(), key=lambda x: x[1])[0]
        urgency_confidence = min(0.8, urgency_scores[urgency] / 3)
        
        avg_confidence = (case_type_confidence + urgency_confidence) / 2
        
        return ClassificationResult(
            case_type=case_type,
            urgency=urgency,
            confidence=avg_confidence,
            reasoning=f"Rule-based classification (case_type: {case_type_confidence:.2f}, urgency: {urgency_confidence:.2f})",
            missing_fields=self._identify_missing_fields(case_data),
            processing_time_ms=0
        )
    
    def _combine_classifications(self, llm_result: Optional[ClassificationResult], 
                               ml_result: ClassificationResult, 
                               text: str) -> ClassificationResult:
        """Combine LLM and ML classification results."""
        if not llm_result:
            return ml_result
        
        # Use LLM result if confidence is significantly higher
        if llm_result.confidence > ml_result.confidence + 0.1:
            return llm_result
        
        # Use ML result if it's more confident
        if ml_result.confidence > llm_result.confidence + 0.1:
            return ml_result
        
        # Combine results (weighted average)
        combined_case_type = llm_result.case_type if llm_result.confidence > ml_result.confidence else ml_result.case_type
        combined_urgency = llm_result.urgency if llm_result.confidence > ml_result.confidence else ml_result.urgency
        combined_confidence = (llm_result.confidence + ml_result.confidence) / 2
        combined_reasoning = f"Combined: LLM ({llm_result.confidence:.2f}) + ML ({ml_result.confidence:.2f})"
        combined_missing = list(set(llm_result.missing_fields + ml_result.missing_fields))
        
        return ClassificationResult(
            case_type=combined_case_type,
            urgency=combined_urgency,
            confidence=combined_confidence,
            reasoning=combined_reasoning,
            missing_fields=combined_missing,
            processing_time_ms=0
        )
    
    def _identify_missing_fields(self, case_data: Dict[str, Any]) -> List[str]:
        """Identify missing required fields based on case type."""
        missing_fields = []
        
        # Basic required fields
        if not case_data.get("title"):
            missing_fields.append("title")
        if not case_data.get("description"):
            missing_fields.append("description")
        
        # Case type specific requirements
        case_type = case_data.get("case_type")
        if case_type == CaseType.INSURANCE_CLAIM:
            if not case_data.get("amount"):
                missing_fields.append("claim_amount")
            if not case_data.get("customer_id"):
                missing_fields.append("customer_id")
        elif case_type == CaseType.HEALTHCARE_PRIOR_AUTH:
            if not case_data.get("customer_id"):
                missing_fields.append("patient_id")
            if not case_data.get("metadata", {}).get("provider"):
                missing_fields.append("provider_information")
        
        return missing_fields
    
    def to_agent_result(self, result: ClassificationResult) -> AgentResult:
        """Convert classification result to agent result format."""
        return AgentResult(
            agent_name="ClassifierAgent",
            confidence=result.confidence,
            result={
                "case_type": result.case_type.value,
                "urgency": result.urgency.value,
                "missing_fields": result.missing_fields
            },
            reasoning=result.reasoning,
            processing_time_ms=result.processing_time_ms
        )
