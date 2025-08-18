"""
Compliance Agent for PII detection, redaction, and audit logging.
"""

import time
import logging
import re
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import uuid

from ..core.config import settings
from ..data.schemas import AgentResult

logger = logging.getLogger(__name__)


@dataclass
class ComplianceResult:
    """Result of compliance analysis."""
    pii_detected: bool
    pii_types: List[str]
    redacted_content: Dict[str, Any]
    audit_log: Dict[str, Any]
    compliance_issues: List[str]
    confidence: float
    reasoning: str
    processing_time_ms: int


class ComplianceAgent:
    """
    Agent responsible for compliance and security.
    
    Features:
    - PII detection and redaction
    - Audit log generation
    - Compliance issue identification
    - Data retention management
    """
    
    def __init__(self):
        self.pii_detection_enabled = settings.pii_detection_enabled
        
        # PII patterns for detection
        self.pii_patterns = {
            "ssn": {
                "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
                "replacement": "[SSN_REDACTED]",
                "description": "Social Security Number"
            },
            "credit_card": {
                "pattern": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
                "replacement": "[CC_REDACTED]",
                "description": "Credit Card Number"
            },
            "phone": {
                "pattern": r"\b\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}\b",
                "replacement": "[PHONE_REDACTED]",
                "description": "Phone Number"
            },
            "email": {
                "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "replacement": "[EMAIL_REDACTED]",
                "description": "Email Address"
            },
            "address": {
                "pattern": r"\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b",
                "replacement": "[ADDRESS_REDACTED]",
                "description": "Street Address"
            },
            "account_number": {
                "pattern": r"\b\d{8,}\b",
                "replacement": "[ACCOUNT_REDACTED]",
                "description": "Account Number"
            },
            "date_of_birth": {
                "pattern": r"\b(?:DOB|Date of Birth|Birth Date)[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
                "replacement": "[DOB_REDACTED]",
                "description": "Date of Birth"
            }
        }
        
        # Compliance rules
        self.compliance_rules = {
            "data_retention": {
                "audit_logs": 365,  # days
                "case_data": 2555,  # 7 years
                "pii_data": 90      # days
            },
            "required_fields": {
                "insurance_claim": ["customer_id", "amount", "description"],
                "healthcare_prior_auth": ["patient_id", "provider", "treatment"],
                "bank_dispute": ["account_number", "transaction_id", "amount"],
                "legal_intake": ["client_name", "case_type", "description"]
            },
            "sensitive_keywords": [
                "confidential", "secret", "private", "internal", "restricted",
                "classified", "sensitive", "proprietary", "trade secret"
            ]
        }
    
    async def process_compliance(self, case_data: Dict[str, Any],
                               agent_results: List[Dict[str, Any]]) -> ComplianceResult:
        """
        Process compliance requirements for a case.
        
        Args:
            case_data: Case information
            agent_results: Results from all agents
        
        Returns:
            ComplianceResult with compliance analysis
        """
        start_time = time.time()
        
        try:
            # Detect PII
            pii_result = self._detect_pii(case_data) if self.pii_detection_enabled else {
                "detected": False,
                "types": [],
                "redacted_content": case_data
            }
            
            # Generate audit log
            audit_log = self._generate_audit_log(case_data, agent_results, pii_result)
            
            # Check compliance issues
            compliance_issues = self._check_compliance_issues(case_data, agent_results)
            
            # Calculate confidence
            confidence = self._calculate_compliance_confidence(pii_result, compliance_issues)
            
            # Generate reasoning
            reasoning = self._generate_compliance_reasoning(pii_result, compliance_issues)
            
            processing_time = int((time.time() - start_time) * 1000)
            return ComplianceResult(
                pii_detected=pii_result["detected"],
                pii_types=pii_result["types"],
                redacted_content=pii_result["redacted_content"],
                audit_log=audit_log,
                compliance_issues=compliance_issues,
                confidence=confidence,
                reasoning=reasoning,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Compliance processing failed: {str(e)}")
            # Return safe defaults
            processing_time = int((time.time() - start_time) * 1000)
            return ComplianceResult(
                pii_detected=False,
                pii_types=[],
                redacted_content=case_data,
                audit_log={"error": str(e)},
                compliance_issues=["compliance_processing_error"],
                confidence=0.5,
                reasoning=f"Compliance processing failed: {str(e)}",
                processing_time_ms=processing_time
            )
    
    def _detect_pii(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect PII in case data."""
        detected_types = []
        redacted_content = case_data.copy()
        
        # Convert case data to string for pattern matching
        case_text = self._extract_text(case_data)
        
        # Check each PII pattern
        for pii_type, pattern_info in self.pii_patterns.items():
            matches = re.findall(pattern_info["pattern"], case_text, re.IGNORECASE)
            if matches:
                detected_types.append(pii_type)
                # Redact the content
                redacted_content = self._redact_content(redacted_content, pattern_info)
        
        return {
            "detected": len(detected_types) > 0,
            "types": detected_types,
            "redacted_content": redacted_content
        }
    
    def _extract_text(self, case_data: Dict[str, Any]) -> str:
        """Extract text from case data for PII detection."""
        text_parts = []
        
        # Extract from basic fields
        for field in ["title", "description", "customer_id"]:
            if case_data.get(field):
                text_parts.append(str(case_data[field]))
        
        # Extract from metadata
        metadata = case_data.get("metadata", {})
        for key, value in metadata.items():
            if isinstance(value, str):
                text_parts.append(f"{key}: {value}")
        
        return " ".join(text_parts)
    
    def _redact_content(self, content: Dict[str, Any], pattern_info: Dict[str, str]) -> Dict[str, Any]:
        """Redact PII from content."""
        redacted = content.copy()
        
        # Redact from basic fields
        for field in ["title", "description", "customer_id"]:
            if field in redacted and isinstance(redacted[field], str):
                redacted[field] = re.sub(
                    pattern_info["pattern"],
                    pattern_info["replacement"],
                    redacted[field],
                    flags=re.IGNORECASE
                )
        
        # Redact from metadata
        if "metadata" in redacted:
            metadata = redacted["metadata"].copy()
            for key, value in metadata.items():
                if isinstance(value, str):
                    metadata[key] = re.sub(
                        pattern_info["pattern"],
                        pattern_info["replacement"],
                        value,
                        flags=re.IGNORECASE
                    )
            redacted["metadata"] = metadata
        
        return redacted
    
    def _generate_audit_log(self, case_data: Dict[str, Any],
                          agent_results: List[Dict[str, Any]],
                          pii_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive audit log."""
        audit_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Create audit trail hash
        audit_trail = {
            "case_id": case_data.get("id"),
            "timestamp": timestamp,
            "audit_id": audit_id,
            "pii_detected": pii_result["detected"],
            "pii_types": pii_result["types"],
            "agent_results": [
                {
                    "agent": result.get("agent_name", "Unknown"),
                    "confidence": result.get("confidence", 0.0),
                    "processing_time_ms": result.get("processing_time_ms", 0)
                }
                for result in agent_results
            ]
        }
        
        # Calculate hash for integrity
        audit_hash = hashlib.sha256(
            json.dumps(audit_trail, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "audit_trail": audit_trail,
            "integrity_hash": audit_hash,
            "retention_date": self._calculate_retention_date("audit_logs")
        }
    
    def _check_compliance_issues(self, case_data: Dict[str, Any],
                               agent_results: List[Dict[str, Any]]) -> List[str]:
        """Check for compliance issues."""
        issues = []
        
        # Check required fields
        case_type = self._extract_case_type(agent_results)
        required_fields = self.compliance_rules["required_fields"].get(case_type, [])
        
        for field in required_fields:
            if not case_data.get(field):
                issues.append(f"missing_required_field: {field}")
        
        # Check for sensitive keywords
        case_text = self._extract_text(case_data).lower()
        for keyword in self.compliance_rules["sensitive_keywords"]:
            if keyword in case_text:
                issues.append(f"sensitive_keyword_detected: {keyword}")
        
        # Check agent confidence levels
        for result in agent_results:
            agent_name = result.get("agent_name", "Unknown")
            confidence = result.get("confidence", 0.0)
            if confidence < 0.7:
                issues.append(f"low_confidence_agent: {agent_name} ({confidence:.2f})")
        
        # Check for potential data retention issues
        if case_data.get("created_at"):
            try:
                created_date = datetime.fromisoformat(case_data["created_at"].replace("Z", "+00:00"))
                retention_limit = datetime.utcnow().replace(tzinfo=None) - datetime.timedelta(
                    days=self.compliance_rules["data_retention"]["case_data"]
                )
                if created_date < retention_limit:
                    issues.append("data_retention_limit_exceeded")
            except:
                pass
        
        return issues
    
    def _extract_case_type(self, agent_results: List[Dict[str, Any]]) -> str:
        """Extract case type from agent results."""
        for result in agent_results:
            if result.get("agent_name") == "ClassifierAgent":
                agent_result = result.get("result", {})
                return agent_result.get("case_type", "insurance_claim")
        return "insurance_claim"
    
    def _calculate_compliance_confidence(self, pii_result: Dict[str, Any],
                                       compliance_issues: List[str]) -> float:
        """Calculate confidence in compliance assessment."""
        base_confidence = 0.8
        
        # Reduce confidence for PII detection
        if pii_result["detected"]:
            base_confidence -= 0.1
        
        # Reduce confidence for compliance issues
        issue_penalty = min(0.3, len(compliance_issues) * 0.05)
        base_confidence -= issue_penalty
        
        return max(0.0, base_confidence)
    
    def _generate_compliance_reasoning(self, pii_result: Dict[str, Any],
                                     compliance_issues: List[str]) -> str:
        """Generate reasoning for compliance assessment."""
        reasoning_parts = []
        
        if pii_result["detected"]:
            pii_types = ", ".join(pii_result["types"])
            reasoning_parts.append(f"PII detected: {pii_types}")
        else:
            reasoning_parts.append("No PII detected")
        
        if compliance_issues:
            reasoning_parts.append(f"Compliance issues found: {len(compliance_issues)}")
            for issue in compliance_issues[:3]:  # Show first 3 issues
                reasoning_parts.append(f"- {issue}")
        else:
            reasoning_parts.append("No compliance issues detected")
        
        return ". ".join(reasoning_parts)
    
    def _calculate_retention_date(self, data_type: str) -> str:
        """Calculate retention date for data type."""
        retention_days = self.compliance_rules["data_retention"].get(data_type, 365)
        retention_date = datetime.utcnow() + datetime.timedelta(days=retention_days)
        return retention_date.isoformat()
    
    def export_audit_packet(self, case_id: str, audit_log: Dict[str, Any],
                          format: str = "json") -> str:
        """Export audit packet in specified format."""
        try:
            if format.lower() == "json":
                return json.dumps(audit_log, indent=2)
            elif format.lower() == "csv":
                return self._audit_to_csv(audit_log)
            elif format.lower() == "pdf":
                return self._audit_to_pdf(audit_log)
            else:
                raise ValueError(f"Unsupported format: {format}")
        except Exception as e:
            logger.error(f"Audit export failed: {str(e)}")
            return f"Export failed: {str(e)}"
    
    def _audit_to_csv(self, audit_log: Dict[str, Any]) -> str:
        """Convert audit log to CSV format."""
        csv_lines = ["audit_id,timestamp,case_id,pii_detected,pii_types,agent_count"]
        
        audit_trail = audit_log.get("audit_trail", {})
        csv_lines.append(",".join([
            audit_log.get("audit_id", ""),
            audit_trail.get("timestamp", ""),
            audit_trail.get("case_id", ""),
            str(audit_trail.get("pii_detected", False)),
            ";".join(audit_trail.get("pii_types", [])),
            str(len(audit_trail.get("agent_results", [])))
        ]))
        
        return "\n".join(csv_lines)
    
    def _audit_to_pdf(self, audit_log: Dict[str, Any]) -> str:
        """Convert audit log to PDF format (placeholder)."""
        # In a real implementation, this would generate a PDF
        return f"PDF export for audit {audit_log.get('audit_id', 'unknown')}"
    
    def to_agent_result(self, result: ComplianceResult) -> AgentResult:
        """Convert compliance result to agent result format."""
        return AgentResult(
            agent_name="ComplianceAgent",
            confidence=result.confidence,
            result={
                "pii_detected": result.pii_detected,
                "pii_types": result.pii_types,
                "compliance_issues": result.compliance_issues,
                "audit_id": result.audit_log.get("audit_id")
            },
            reasoning=result.reasoning,
            processing_time_ms=result.processing_time_ms
        )
