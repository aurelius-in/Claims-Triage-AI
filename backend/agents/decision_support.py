"""
Decision Support Agent for providing next actions and recommendations using RAG.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
import os

from ..core.config import settings
from ..data.schemas import AgentResult

logger = logging.getLogger(__name__)


@dataclass
class DecisionSupportResult:
    """Result of decision support analysis."""
    suggested_actions: List[str]
    template_response: str
    checklist: List[str]
    knowledge_sources: List[str]
    confidence: float
    reasoning: str
    processing_time_ms: int


class DecisionSupportAgent:
    """
    Agent responsible for providing decision support and next actions.
    
    Features:
    - RAG over knowledge base (policies, SOPs)
    - Template response generation
    - Action checklist creation
    - Knowledge source attribution
    """
    
    def __init__(self):
        self.kb_path = os.path.join(settings.rag_path, "kb")
        self.templates_path = os.path.join(settings.rag_path, "templates")
        
        # Load knowledge base and templates
        self._load_knowledge_base()
        self._load_templates()
        
        # Decision support patterns
        self.action_patterns = {
            "insurance_claim": {
                "high_risk": [
                    "Request additional documentation",
                    "Schedule fraud investigation",
                    "Notify compliance team",
                    "Set up monitoring alerts"
                ],
                "medium_risk": [
                    "Review claim details",
                    "Request supporting documents",
                    "Verify policy coverage",
                    "Calculate settlement amount"
                ],
                "low_risk": [
                    "Process standard approval",
                    "Send confirmation letter",
                    "Update customer records",
                    "Close case"
                ]
            },
            "healthcare_prior_auth": {
                "high_risk": [
                    "Request medical records",
                    "Consult with medical director",
                    "Schedule peer review",
                    "Notify provider of decision"
                ],
                "medium_risk": [
                    "Review treatment plan",
                    "Verify medical necessity",
                    "Check coverage criteria",
                    "Make determination"
                ],
                "low_risk": [
                    "Approve treatment",
                    "Send approval letter",
                    "Update authorization system",
                    "Notify provider"
                ]
            },
            "bank_dispute": {
                "high_risk": [
                    "Freeze account activity",
                    "Initiate fraud investigation",
                    "Contact law enforcement",
                    "Notify compliance officer"
                ],
                "medium_risk": [
                    "Review transaction history",
                    "Contact customer for details",
                    "Investigate merchant",
                    "Make provisional credit decision"
                ],
                "low_risk": [
                    "Process chargeback",
                    "Send dispute letter",
                    "Update customer account",
                    "Monitor for resolution"
                ]
            },
            "legal_intake": {
                "high_risk": [
                    "Schedule urgent consultation",
                    "Prepare legal documents",
                    "Notify senior attorney",
                    "Set up case management"
                ],
                "medium_risk": [
                    "Review case details",
                    "Schedule consultation",
                    "Prepare initial assessment",
                    "Assign case number"
                ],
                "low_risk": [
                    "Schedule standard consultation",
                    "Send welcome packet",
                    "Create client file",
                    "Assign paralegal"
                ]
            }
        }
    
    def _load_knowledge_base(self):
        """Load knowledge base documents."""
        self.knowledge_base = {}
        
        try:
            kb_files = [
                "insurance_policies.md",
                "healthcare_procedures.md", 
                "banking_regulations.md",
                "legal_procedures.md",
                "fraud_detection.md",
                "compliance_guidelines.md"
            ]
            
            for filename in kb_files:
                filepath = os.path.join(self.kb_path, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.knowledge_base[filename] = content
            
            logger.info(f"Loaded {len(self.knowledge_base)} knowledge base documents")
            
        except Exception as e:
            logger.warning(f"Failed to load knowledge base: {str(e)}")
            self.knowledge_base = {}
    
    def _load_templates(self):
        """Load response templates."""
        self.templates = {}
        
        try:
            template_files = [
                "insurance_approval.json",
                "insurance_denial.json",
                "healthcare_approval.json",
                "healthcare_denial.json",
                "bank_credit.json",
                "bank_debit.json",
                "legal_consultation.json"
            ]
            
            for filename in template_files:
                filepath = os.path.join(self.templates_path, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        template = json.load(f)
                        self.templates[filename] = template
            
            logger.info(f"Loaded {len(self.templates)} response templates")
            
        except Exception as e:
            logger.warning(f"Failed to load templates: {str(e)}")
            self.templates = {}
    
    async def provide_support(self, case_data: Dict[str, Any],
                            classification_result: Dict[str, Any],
                            risk_result: Dict[str, Any],
                            routing_result: Dict[str, Any]) -> DecisionSupportResult:
        """
        Provide decision support for a case.
        
        Args:
            case_data: Case information
            classification_result: Results from ClassifierAgent
            risk_result: Results from RiskScorerAgent
            routing_result: Results from RouterAgent
        
        Returns:
            DecisionSupportResult with recommendations
        """
        start_time = time.time()
        
        try:
            # Extract case context
            case_type = classification_result.get("case_type", "insurance_claim")
            risk_level = risk_result.get("risk_level", "low")
            urgency = classification_result.get("urgency", "medium")
            team = routing_result.get("recommended_team", "Tier-2")
            
            # Generate suggested actions
            suggested_actions = self._generate_actions(case_type, risk_level, urgency, team)
            
            # Generate template response
            template_response = self._generate_template_response(case_data, case_type, risk_level)
            
            # Create checklist
            checklist = self._create_checklist(case_data, classification_result, risk_result)
            
            # Retrieve relevant knowledge
            knowledge_sources = self._retrieve_knowledge(case_type, risk_level)
            
            # Calculate confidence
            confidence = self._calculate_confidence(classification_result, risk_result, routing_result)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(case_type, risk_level, team, knowledge_sources)
            
            processing_time = int((time.time() - start_time) * 1000)
            return DecisionSupportResult(
                suggested_actions=suggested_actions,
                template_response=template_response,
                checklist=checklist,
                knowledge_sources=knowledge_sources,
                confidence=confidence,
                reasoning=reasoning,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Decision support failed: {str(e)}")
            # Return safe defaults
            processing_time = int((time.time() - start_time) * 1000)
            return DecisionSupportResult(
                suggested_actions=["Review case manually"],
                template_response="Please review this case and take appropriate action.",
                checklist=["Verify case details", "Check documentation"],
                knowledge_sources=[],
                confidence=0.5,
                reasoning=f"Decision support failed: {str(e)}",
                processing_time_ms=processing_time
            )
    
    def _generate_actions(self, case_type: str, risk_level: str, 
                         urgency: str, team: str) -> List[str]:
        """Generate suggested actions based on case context."""
        actions = []
        
        # Get base actions for case type and risk level
        case_patterns = self.action_patterns.get(case_type, {})
        risk_actions = case_patterns.get(risk_level, case_patterns.get("medium_risk", []))
        actions.extend(risk_actions)
        
        # Add urgency-based actions
        if urgency in ["critical", "high"]:
            actions.extend([
                "Prioritize for immediate review",
                "Set up escalation monitoring",
                "Notify management team"
            ])
        
        # Add team-specific actions
        if team == "Fraud-Review":
            actions.extend([
                "Initiate fraud investigation",
                "Freeze related accounts",
                "Contact law enforcement if needed"
            ])
        elif team == "Specialist":
            actions.extend([
                "Schedule specialist review",
                "Prepare detailed analysis",
                "Coordinate with external experts"
            ])
        elif team == "Escalation":
            actions.extend([
                "Immediate management review",
                "Prepare escalation report",
                "Coordinate cross-functional response"
            ])
        
        # Add compliance actions for high-risk cases
        if risk_level in ["high", "extreme"]:
            actions.extend([
                "Document decision rationale",
                "Update compliance logs",
                "Schedule follow-up review"
            ])
        
        return list(set(actions))  # Remove duplicates
    
    def _generate_template_response(self, case_data: Dict[str, Any], 
                                  case_type: str, risk_level: str) -> str:
        """Generate template response for the case."""
        try:
            # Select appropriate template
            template_key = self._select_template(case_type, risk_level)
            template = self.templates.get(template_key, {})
            
            if not template:
                return self._generate_fallback_template(case_data, case_type, risk_level)
            
            # Fill template with case data
            response = template.get("body", "")
            
            # Replace placeholders
            replacements = {
                "{customer_name}": case_data.get("customer_id", "Customer"),
                "{case_id}": str(case_data.get("id", "N/A")),
                "{amount}": str(case_data.get("amount", "N/A")),
                "{case_type}": case_type.replace("_", " ").title(),
                "{risk_level}": risk_level.title()
            }
            
            for placeholder, value in replacements.items():
                response = response.replace(placeholder, value)
            
            return response
            
        except Exception as e:
            logger.warning(f"Template generation failed: {str(e)}")
            return self._generate_fallback_template(case_data, case_type, risk_level)
    
    def _select_template(self, case_type: str, risk_level: str) -> str:
        """Select appropriate template based on case type and risk level."""
        template_mapping = {
            "insurance_claim": {
                "low": "insurance_approval.json",
                "medium": "insurance_approval.json",
                "high": "insurance_denial.json",
                "extreme": "insurance_denial.json"
            },
            "healthcare_prior_auth": {
                "low": "healthcare_approval.json",
                "medium": "healthcare_approval.json",
                "high": "healthcare_denial.json",
                "extreme": "healthcare_denial.json"
            },
            "bank_dispute": {
                "low": "bank_credit.json",
                "medium": "bank_credit.json",
                "high": "bank_debit.json",
                "extreme": "bank_debit.json"
            },
            "legal_intake": {
                "low": "legal_consultation.json",
                "medium": "legal_consultation.json",
                "high": "legal_consultation.json",
                "extreme": "legal_consultation.json"
            }
        }
        
        case_templates = template_mapping.get(case_type, {})
        return case_templates.get(risk_level, "legal_consultation.json")
    
    def _generate_fallback_template(self, case_data: Dict[str, Any], 
                                  case_type: str, risk_level: str) -> str:
        """Generate fallback template when specific template is not available."""
        return f"""
        Dear {case_data.get('customer_id', 'Customer')},
        
        Thank you for submitting your {case_type.replace('_', ' ')} case. 
        We have reviewed your case and determined it requires {risk_level} level processing.
        
        Our team will process your case according to our standard procedures. 
        You will receive further communication regarding the status of your case.
        
        If you have any questions, please contact our support team.
        
        Best regards,
        Claims Triage AI Team
        """
    
    def _create_checklist(self, case_data: Dict[str, Any],
                         classification_result: Dict[str, Any],
                         risk_result: Dict[str, Any]) -> List[str]:
        """Create checklist of required actions and verifications."""
        checklist = []
        
        # Basic verification items
        checklist.extend([
            "Verify case information is complete",
            "Check all required documents are attached",
            "Validate customer information",
            "Review case classification accuracy"
        ])
        
        # Add missing fields to checklist
        missing_fields = classification_result.get("missing_fields", [])
        for field in missing_fields:
            checklist.append(f"Request missing {field}")
        
        # Add risk-specific items
        risk_level = risk_result.get("risk_level", "low")
        if risk_level in ["high", "extreme"]:
            checklist.extend([
                "Perform additional verification",
                "Document risk assessment rationale",
                "Set up monitoring and alerts",
                "Schedule follow-up review"
            ])
        
        # Add case type specific items
        case_type = classification_result.get("case_type", "insurance_claim")
        if case_type == "insurance_claim":
            checklist.extend([
                "Verify policy coverage",
                "Check claim amount against limits",
                "Review medical documentation",
                "Calculate settlement amount"
            ])
        elif case_type == "healthcare_prior_auth":
            checklist.extend([
                "Verify medical necessity",
                "Check treatment plan",
                "Review provider credentials",
                "Validate diagnosis codes"
            ])
        elif case_type == "bank_dispute":
            checklist.extend([
                "Review transaction details",
                "Verify customer identity",
                "Check account activity",
                "Investigate merchant information"
            ])
        elif case_type == "legal_intake":
            checklist.extend([
                "Schedule initial consultation",
                "Prepare case summary",
                "Check conflicts of interest",
                "Assign case number"
            ])
        
        return checklist
    
    def _retrieve_knowledge(self, case_type: str, risk_level: str) -> List[str]:
        """Retrieve relevant knowledge sources."""
        knowledge_sources = []
        
        # Map case types to knowledge base files
        type_to_kb = {
            "insurance_claim": ["insurance_policies.md", "compliance_guidelines.md"],
            "healthcare_prior_auth": ["healthcare_procedures.md", "compliance_guidelines.md"],
            "bank_dispute": ["banking_regulations.md", "fraud_detection.md"],
            "legal_intake": ["legal_procedures.md", "compliance_guidelines.md"],
            "fraud_review": ["fraud_detection.md", "compliance_guidelines.md"]
        }
        
        # Get relevant knowledge base files
        relevant_files = type_to_kb.get(case_type, ["compliance_guidelines.md"])
        
        # Add risk-specific knowledge
        if risk_level in ["high", "extreme"]:
            relevant_files.append("fraud_detection.md")
        
        # Check which files are available
        for filename in relevant_files:
            if filename in self.knowledge_base:
                knowledge_sources.append(filename)
        
        return knowledge_sources
    
    def _calculate_confidence(self, classification_result: Dict[str, Any],
                            risk_result: Dict[str, Any],
                            routing_result: Dict[str, Any]) -> float:
        """Calculate confidence in decision support recommendations."""
        # Weight the confidence from each agent
        classification_confidence = classification_result.get("confidence", 0.5)
        risk_confidence = risk_result.get("confidence", 0.5)
        routing_confidence = routing_result.get("confidence", 0.5)
        
        # Weighted average (classification and risk are more important for decision support)
        weighted_confidence = (
            classification_confidence * 0.4 +
            risk_confidence * 0.4 +
            routing_confidence * 0.2
        )
        
        return min(1.0, weighted_confidence)
    
    def _generate_reasoning(self, case_type: str, risk_level: str, 
                          team: str, knowledge_sources: List[str]) -> str:
        """Generate reasoning for decision support recommendations."""
        reasoning_parts = []
        
        reasoning_parts.append(f"Based on the case classification as {case_type} with {risk_level} risk level,")
        reasoning_parts.append(f"this case has been routed to the {team} team.")
        
        if knowledge_sources:
            reasoning_parts.append(f"Recommendations are based on knowledge from: {', '.join(knowledge_sources)}.")
        
        if risk_level in ["high", "extreme"]:
            reasoning_parts.append("Due to the high risk level, additional verification and monitoring are recommended.")
        
        if team in ["Fraud-Review", "Escalation"]:
            reasoning_parts.append("Specialized handling is required due to the nature of this case.")
        
        return " ".join(reasoning_parts)
    
    def to_agent_result(self, result: DecisionSupportResult) -> AgentResult:
        """Convert decision support result to agent result format."""
        return AgentResult(
            agent_name="DecisionSupportAgent",
            confidence=result.confidence,
            result={
                "suggested_actions": result.suggested_actions,
                "template_response": result.template_response,
                "checklist": result.checklist,
                "knowledge_sources": result.knowledge_sources
            },
            reasoning=result.reasoning,
            processing_time_ms=result.processing_time_ms
        )
