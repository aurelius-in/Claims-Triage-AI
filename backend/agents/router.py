"""
Router Agent for intelligent case routing using OPA policies and business rules.
"""

import time
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import aiohttp
import json

from ..core.config import settings
from ..data.schemas import AgentResult

logger = logging.getLogger(__name__)


@dataclass
class RoutingResult:
    """Result of case routing."""
    recommended_team: str
    sla_target_hours: int
    escalation_flag: bool
    confidence: float
    reasoning: str
    policy_applied: str
    alternative_routes: List[str]
    processing_time_ms: int


class RouterAgent:
    """
    Agent responsible for routing cases to appropriate teams/queues.
    
    Features:
    - OPA policy-based routing decisions
    - Business rule evaluation
    - Team capacity consideration
    - SLA target calculation
    - Escalation detection
    """
    
    def __init__(self):
        self.opa_url = settings.opa_url
        self.default_teams = settings.default_teams
        
        # Routing rules and policies
        self.routing_policies = {
            "high_risk_escalation": {
                "condition": "risk_level == 'high' OR risk_level == 'extreme'",
                "action": "escalate",
                "team": "Escalation",
                "sla_hours": 4
            },
            "fraud_review": {
                "condition": "case_type == 'fraud_review' OR fraud_indicators > 0",
                "action": "route",
                "team": "Fraud-Review",
                "sla_hours": 24
            },
            "legal_cases": {
                "condition": "case_type == 'legal_intake' OR legal_indicators > 0",
                "action": "route",
                "team": "Specialist",
                "sla_hours": 48
            },
            "urgent_cases": {
                "condition": "urgency == 'critical' OR urgency == 'high'",
                "action": "route",
                "team": "Tier-1",
                "sla_hours": 2
            },
            "standard_processing": {
                "condition": "risk_level == 'low' AND urgency == 'low'",
                "action": "route",
                "team": "Tier-2",
                "sla_hours": 72
            }
        }
        
        # Team capacity and capabilities
        self.team_capabilities = {
            "Tier-1": {
                "case_types": ["insurance_claim", "healthcare_prior_auth", "bank_dispute"],
                "max_risk_level": "high",
                "capacity": 100,
                "current_load": 0,
                "sla_target_hours": 2
            },
            "Tier-2": {
                "case_types": ["insurance_claim", "healthcare_prior_auth"],
                "max_risk_level": "medium",
                "capacity": 200,
                "current_load": 0,
                "sla_target_hours": 72
            },
            "Specialist": {
                "case_types": ["legal_intake", "fraud_review", "healthcare_prior_auth"],
                "max_risk_level": "extreme",
                "capacity": 50,
                "current_load": 0,
                "sla_target_hours": 48
            },
            "Fraud-Review": {
                "case_types": ["fraud_review", "bank_dispute"],
                "max_risk_level": "extreme",
                "capacity": 30,
                "current_load": 0,
                "sla_target_hours": 24
            },
            "Escalation": {
                "case_types": ["insurance_claim", "healthcare_prior_auth", "bank_dispute", "legal_intake"],
                "max_risk_level": "extreme",
                "capacity": 20,
                "current_load": 0,
                "sla_target_hours": 4
            }
        }
    
    async def route_case(self, case_data: Dict[str, Any],
                        classification_result: Dict[str, Any],
                        risk_result: Dict[str, Any]) -> RoutingResult:
        """
        Route a case to the appropriate team.
        
        Args:
            case_data: Case information
            classification_result: Results from ClassifierAgent
            risk_result: Results from RiskScorerAgent
        
        Returns:
            RoutingResult with routing decision
        """
        start_time = time.time()
        
        try:
            # Prepare input for OPA
            opa_input = self._prepare_opa_input(case_data, classification_result, risk_result)
            
            # Get OPA routing decision
            opa_result = await self._get_opa_decision(opa_input)
            
            # Apply business rules
            business_result = self._apply_business_rules(case_data, classification_result, risk_result)
            
            # Combine OPA and business rule results
            final_result = self._combine_routing_decisions(opa_result, business_result)
            
            # Validate team capacity
            final_result = self._validate_team_capacity(final_result)
            
            processing_time = int((time.time() - start_time) * 1000)
            return RoutingResult(
                recommended_team=final_result.recommended_team,
                sla_target_hours=final_result.sla_target_hours,
                escalation_flag=final_result.escalation_flag,
                confidence=final_result.confidence,
                reasoning=final_result.reasoning,
                policy_applied=final_result.policy_applied,
                alternative_routes=final_result.alternative_routes,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Routing failed: {str(e)}")
            # Return safe defaults
            processing_time = int((time.time() - start_time) * 1000)
            return RoutingResult(
                recommended_team="Tier-2",
                sla_target_hours=72,
                escalation_flag=False,
                confidence=0.5,
                reasoning=f"Routing failed: {str(e)}",
                policy_applied="default",
                alternative_routes=["Tier-1", "Specialist"],
                processing_time_ms=processing_time
            )
    
    def _prepare_opa_input(self, case_data: Dict[str, Any],
                          classification_result: Dict[str, Any],
                          risk_result: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input data for OPA decision."""
        return {
            "case": {
                "id": case_data.get("id"),
                "title": case_data.get("title"),
                "description": case_data.get("description"),
                "case_type": classification_result.get("case_type"),
                "urgency": classification_result.get("urgency"),
                "risk_level": risk_result.get("risk_level"),
                "risk_score": risk_result.get("risk_score"),
                "amount": case_data.get("amount"),
                "customer_id": case_data.get("customer_id"),
                "metadata": case_data.get("metadata", {}),
                "missing_fields": classification_result.get("missing_fields", [])
            },
            "teams": self.team_capabilities,
            "policies": self.routing_policies
        }
    
    async def _get_opa_decision(self, opa_input: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get routing decision from OPA."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.opa_url}/v1/data/routing/decision",
                    json={"input": opa_input},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("result", {})
                    else:
                        logger.warning(f"OPA request failed with status {response.status}")
                        return None
                        
        except Exception as e:
            logger.warning(f"OPA request failed: {str(e)}")
            return None
    
    def _apply_business_rules(self, case_data: Dict[str, Any],
                            classification_result: Dict[str, Any],
                            risk_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business rules for routing."""
        case_type = classification_result.get("case_type", "insurance_claim")
        urgency = classification_result.get("urgency", "medium")
        risk_level = risk_result.get("risk_level", "low")
        risk_score = risk_result.get("risk_score", 0.0)
        
        # Apply routing policies in priority order
        for policy_name, policy in self.routing_policies.items():
            if self._evaluate_policy_condition(policy["condition"], {
                "case_type": case_type,
                "urgency": urgency,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "fraud_indicators": len(risk_result.get("risk_factors", [])),
                "legal_indicators": 1 if "legal" in case_type else 0
            }):
                return {
                    "team": policy["team"],
                    "sla_hours": policy["sla_hours"],
                    "escalation": policy["action"] == "escalate",
                    "confidence": 0.9,
                    "reasoning": f"Applied {policy_name} policy",
                    "policy_applied": policy_name
                }
        
        # Default routing
        if risk_level in ["high", "extreme"]:
            return {
                "team": "Specialist",
                "sla_hours": 48,
                "escalation": False,
                "confidence": 0.7,
                "reasoning": "High risk case routed to specialist",
                "policy_applied": "default_high_risk"
            }
        elif urgency in ["critical", "high"]:
            return {
                "team": "Tier-1",
                "sla_hours": 2,
                "escalation": False,
                "confidence": 0.7,
                "reasoning": "High urgency case routed to Tier-1",
                "policy_applied": "default_high_urgency"
            }
        else:
            return {
                "team": "Tier-2",
                "sla_hours": 72,
                "escalation": False,
                "confidence": 0.7,
                "reasoning": "Standard case routed to Tier-2",
                "policy_applied": "default_standard"
            }
    
    def _evaluate_policy_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a policy condition string."""
        try:
            # Simple condition evaluation (in production, use a proper expression evaluator)
            condition = condition.replace("==", "==").replace("OR", "or").replace("AND", "and")
            
            # Create a safe evaluation context
            safe_context = {
                "case_type": context.get("case_type"),
                "urgency": context.get("urgency"),
                "risk_level": context.get("risk_level"),
                "risk_score": context.get("risk_score"),
                "fraud_indicators": context.get("fraud_indicators"),
                "legal_indicators": context.get("legal_indicators")
            }
            
            # Simple string matching for now
            if "risk_level == 'high'" in condition and safe_context["risk_level"] == "high":
                return True
            if "risk_level == 'extreme'" in condition and safe_context["risk_level"] == "extreme":
                return True
            if "case_type == 'fraud_review'" in condition and safe_context["case_type"] == "fraud_review":
                return True
            if "urgency == 'critical'" in condition and safe_context["urgency"] == "critical":
                return True
            if "urgency == 'high'" in condition and safe_context["urgency"] == "high":
                return True
            if "fraud_indicators > 0" in condition and safe_context["fraud_indicators"] > 0:
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Policy condition evaluation failed: {str(e)}")
            return False
    
    def _combine_routing_decisions(self, opa_result: Optional[Dict[str, Any]],
                                 business_result: Dict[str, Any]) -> Dict[str, Any]:
        """Combine OPA and business rule routing decisions."""
        if not opa_result:
            return business_result
        
        # Use OPA result if available and valid
        if opa_result.get("team") and opa_result.get("team") in self.team_capabilities:
            return {
                "team": opa_result["team"],
                "sla_hours": opa_result.get("sla_hours", business_result["sla_hours"]),
                "escalation": opa_result.get("escalation", business_result["escalation"]),
                "confidence": 0.95,  # Higher confidence for OPA
                "reasoning": f"OPA decision: {opa_result.get('reasoning', 'Policy-based routing')}",
                "policy_applied": opa_result.get("policy", "opa_policy")
            }
        
        return business_result
    
    def _validate_team_capacity(self, routing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and adjust routing based on team capacity."""
        team = routing_result["team"]
        team_info = self.team_capabilities.get(team)
        
        if not team_info:
            # Fallback to Tier-2 if team doesn't exist
            return {
                **routing_result,
                "team": "Tier-2",
                "reasoning": f"Team {team} not found, routed to Tier-2",
                "confidence": routing_result["confidence"] * 0.8
            }
        
        # Check capacity
        if team_info["current_load"] >= team_info["capacity"] * 0.9:  # 90% capacity threshold
            # Find alternative team
            alternative = self._find_alternative_team(team, routing_result)
            if alternative:
                return {
                    **routing_result,
                    "team": alternative,
                    "reasoning": f"Team {team} at capacity, routed to {alternative}",
                    "confidence": routing_result["confidence"] * 0.9
                }
        
        return routing_result
    
    def _find_alternative_team(self, original_team: str, routing_result: Dict[str, Any]) -> Optional[str]:
        """Find alternative team when original is at capacity."""
        # Priority order for alternatives
        alternatives = {
            "Tier-1": ["Tier-2", "Specialist"],
            "Tier-2": ["Tier-1", "Specialist"],
            "Specialist": ["Tier-1", "Tier-2"],
            "Fraud-Review": ["Specialist", "Escalation"],
            "Escalation": ["Specialist", "Tier-1"]
        }
        
        for alternative in alternatives.get(original_team, ["Tier-2"]):
            team_info = self.team_capabilities.get(alternative)
            if team_info and team_info["current_load"] < team_info["capacity"] * 0.8:
                return alternative
        
        return "Tier-2"  # Final fallback
    
    def get_alternative_routes(self, case_data: Dict[str, Any],
                             classification_result: Dict[str, Any],
                             risk_result: Dict[str, Any]) -> List[str]:
        """Get alternative routing options."""
        case_type = classification_result.get("case_type", "insurance_claim")
        risk_level = risk_result.get("risk_level", "low")
        urgency = classification_result.get("urgency", "medium")
        
        alternatives = []
        
        # Add teams that can handle this case type
        for team, capabilities in self.team_capabilities.items():
            if case_type in capabilities["case_types"]:
                # Check risk level compatibility
                risk_levels = ["low", "medium", "high", "extreme"]
                max_risk_idx = risk_levels.index(capabilities["max_risk_level"])
                case_risk_idx = risk_levels.index(risk_level)
                
                if case_risk_idx <= max_risk_idx:
                    alternatives.append(team)
        
        # Remove duplicates and return
        return list(set(alternatives))
    
    def update_team_load(self, team: str, load_change: int = 1):
        """Update team load (called when cases are assigned/unassigned)."""
        if team in self.team_capabilities:
            self.team_capabilities[team]["current_load"] += load_change
            self.team_capabilities[team]["current_load"] = max(0, self.team_capabilities[team]["current_load"])
    
    def to_agent_result(self, result: RoutingResult) -> AgentResult:
        """Convert routing result to agent result format."""
        return AgentResult(
            agent_name="RouterAgent",
            confidence=result.confidence,
            result={
                "recommended_team": result.recommended_team,
                "sla_target_hours": result.sla_target_hours,
                "escalation_flag": result.escalation_flag,
                "policy_applied": result.policy_applied,
                "alternative_routes": result.alternative_routes
            },
            reasoning=result.reasoning,
            processing_time_ms=result.processing_time_ms
        )
