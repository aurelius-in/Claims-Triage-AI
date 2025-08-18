"""
Agent Orchestrator for managing the triage workflow and coordinating all agents.
"""

import time
import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

from .classifier import ClassifierAgent
from .risk_scorer import RiskScorerAgent
from .router import RouterAgent
from .decision_support import DecisionSupportAgent
from .compliance import ComplianceAgent
from ..core.config import settings
from ..data.schemas import TriageResponse, AgentResult

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationResult:
    """Result of agent orchestration."""
    triage_id: str
    case_id: str
    agent_results: List[AgentResult]
    final_decision: Dict[str, Any]
    processing_time_ms: int
    success: bool
    error_message: Optional[str] = None


class AgentOrchestrator:
    """
    Orchestrator responsible for managing the triage workflow.
    
    Features:
    - Parallel/serial agent execution
    - Retry logic with circuit breakers
    - Timeout management
    - Structured event emission
    - Error handling and fallbacks
    """
    
    def __init__(self):
        # Initialize agents
        self.classifier_agent = ClassifierAgent()
        self.risk_scorer_agent = RiskScorerAgent()
        self.router_agent = RouterAgent()
        self.decision_support_agent = DecisionSupportAgent()
        self.compliance_agent = ComplianceAgent()
        
        # Configuration
        self.max_retries = 3
        self.timeout_seconds = 30
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 60
        
        # Circuit breaker state
        self.failure_count = 0
        self.last_failure_time = None
        self.circuit_open = False
    
    async def run_triage(self, case_data: Dict[str, Any], 
                        force_reprocess: bool = False) -> OrchestrationResult:
        """
        Run the complete triage workflow.
        
        Args:
            case_data: Case information
            force_reprocess: Force reprocessing even if already triaged
        
        Returns:
            OrchestrationResult with complete triage results
        """
        start_time = time.time()
        triage_id = str(uuid.uuid4())
        
        try:
            # Check circuit breaker
            if self.circuit_open:
                if time.time() - self.last_failure_time < self.circuit_breaker_timeout:
                    raise Exception("Circuit breaker is open")
                else:
                    self.circuit_open = False
                    self.failure_count = 0
            
            # Run agent pipeline
            agent_results = await self._run_agent_pipeline(case_data, triage_id)
            
            # Generate final decision
            final_decision = self._generate_final_decision(agent_results)
            
            # Reset failure count on success
            self.failure_count = 0
            
            processing_time = int((time.time() - start_time) * 1000)
            return OrchestrationResult(
                triage_id=triage_id,
                case_id=case_data.get("id", "unknown"),
                agent_results=agent_results,
                final_decision=final_decision,
                processing_time_ms=processing_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Triage orchestration failed: {str(e)}")
            
            # Update circuit breaker
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.circuit_breaker_threshold:
                self.circuit_open = True
            
            processing_time = int((time.time() - start_time) * 1000)
            return OrchestrationResult(
                triage_id=triage_id,
                case_id=case_data.get("id", "unknown"),
                agent_results=[],
                final_decision={},
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )
    
    async def _run_agent_pipeline(self, case_data: Dict[str, Any], 
                                triage_id: str) -> List[AgentResult]:
        """Run the agent pipeline with proper coordination."""
        agent_results = []
        
        # Step 1: Classification (required for all subsequent steps)
        classification_result = await self._run_with_retry(
            self.classifier_agent.classify, case_data
        )
        agent_results.append(classification_result.to_agent_result(classification_result))
        
        # Step 2: Risk Scoring (depends on classification)
        risk_result = await self._run_with_retry(
            self.risk_scorer_agent.score_risk, 
            case_data, 
            classification_result.__dict__
        )
        agent_results.append(risk_result.to_agent_result(risk_result))
        
        # Step 3: Routing (depends on classification and risk)
        routing_result = await self._run_with_retry(
            self.router_agent.route_case,
            case_data,
            classification_result.__dict__,
            risk_result.__dict__
        )
        agent_results.append(routing_result.to_agent_result(routing_result))
        
        # Step 4: Decision Support (depends on all previous results)
        decision_result = await self._run_with_retry(
            self.decision_support_agent.provide_support,
            case_data,
            classification_result.__dict__,
            risk_result.__dict__,
            routing_result.__dict__
        )
        agent_results.append(decision_result.to_agent_result(decision_result))
        
        # Step 5: Compliance (can run in parallel with decision support)
        compliance_result = await self._run_with_retry(
            self.compliance_agent.process_compliance,
            case_data,
            [result.__dict__ for result in agent_results]
        )
        agent_results.append(compliance_result.to_agent_result(compliance_result))
        
        return agent_results
    
    async def _run_with_retry(self, agent_func, *args, **kwargs):
        """Run agent function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                # Run with timeout
                result = await asyncio.wait_for(
                    agent_func(*args, **kwargs),
                    timeout=self.timeout_seconds
                )
                return result
                
            except asyncio.TimeoutError:
                last_exception = Exception(f"Agent timeout on attempt {attempt + 1}")
                logger.warning(f"Agent timeout on attempt {attempt + 1}")
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Agent error on attempt {attempt + 1}: {str(e)}")
                
                # Don't retry for certain types of errors
                if "circuit_breaker" in str(e).lower():
                    raise e
            
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
        
        # All retries failed
        raise last_exception or Exception("Agent execution failed after all retries")
    
    def _generate_final_decision(self, agent_results: List[AgentResult]) -> Dict[str, Any]:
        """Generate final triage decision from agent results."""
        # Extract results from each agent
        classification_result = self._find_agent_result(agent_results, "ClassifierAgent")
        risk_result = self._find_agent_result(agent_results, "RiskScorerAgent")
        routing_result = self._find_agent_result(agent_results, "RouterAgent")
        decision_result = self._find_agent_result(agent_results, "DecisionSupportAgent")
        compliance_result = self._find_agent_result(agent_results, "ComplianceAgent")
        
        # Build final decision
        final_decision = {
            "case_type": classification_result.get("result", {}).get("case_type", "insurance_claim"),
            "urgency": classification_result.get("result", {}).get("urgency", "medium"),
            "risk_level": risk_result.get("result", {}).get("risk_level", "low"),
            "risk_score": risk_result.get("result", {}).get("risk_score", 0.0),
            "recommended_team": routing_result.get("result", {}).get("recommended_team", "Tier-2"),
            "sla_target_hours": routing_result.get("result", {}).get("sla_target_hours", 72),
            "escalation_flag": routing_result.get("result", {}).get("escalation_flag", False),
            "suggested_actions": decision_result.get("result", {}).get("suggested_actions", []),
            "missing_fields": classification_result.get("result", {}).get("missing_fields", []),
            "compliance_issues": compliance_result.get("result", {}).get("compliance_issues", []),
            "pii_detected": compliance_result.get("result", {}).get("pii_detected", False),
            "overall_confidence": self._calculate_overall_confidence(agent_results)
        }
        
        return final_decision
    
    def _find_agent_result(self, agent_results: List[AgentResult], agent_name: str) -> Dict[str, Any]:
        """Find result from specific agent."""
        for result in agent_results:
            if result.agent_name == agent_name:
                return result.__dict__
        return {}
    
    def _calculate_overall_confidence(self, agent_results: List[AgentResult]) -> float:
        """Calculate overall confidence from all agents."""
        if not agent_results:
            return 0.0
        
        # Weight different agents differently
        weights = {
            "ClassifierAgent": 0.25,
            "RiskScorerAgent": 0.25,
            "RouterAgent": 0.20,
            "DecisionSupportAgent": 0.15,
            "ComplianceAgent": 0.15
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for result in agent_results:
            weight = weights.get(result.agent_name, 0.1)
            weighted_sum += result.confidence * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def to_triage_response(self, orchestration_result: OrchestrationResult) -> TriageResponse:
        """Convert orchestration result to triage response."""
        if not orchestration_result.success:
            raise Exception(orchestration_result.error_message or "Triage failed")
        
        final_decision = orchestration_result.final_decision
        
        return TriageResponse(
            case_id=orchestration_result.case_id,
            triage_id=orchestration_result.triage_id,
            case_type=final_decision["case_type"],
            urgency=final_decision["urgency"],
            risk_level=final_decision["risk_level"],
            risk_score=final_decision["risk_score"],
            recommended_team=final_decision["recommended_team"],
            sla_target_hours=final_decision["sla_target_hours"],
            escalation_flag=final_decision["escalation_flag"],
            agent_results=orchestration_result.agent_results,
            suggested_actions=final_decision["suggested_actions"],
            missing_fields=final_decision["missing_fields"],
            compliance_issues=final_decision["compliance_issues"],
            processing_time_ms=orchestration_result.processing_time_ms,
            created_at=datetime.utcnow()
        )
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        return {
            "classifier_agent": {
                "status": "ready",
                "model_loaded": hasattr(self.classifier_agent, 'case_type_model')
            },
            "risk_scorer_agent": {
                "status": "ready",
                "model_loaded": hasattr(self.risk_scorer_agent, 'risk_model')
            },
            "router_agent": {
                "status": "ready",
                "teams_configured": len(self.router_agent.team_capabilities)
            },
            "decision_support_agent": {
                "status": "ready",
                "templates_loaded": len(self.decision_support_agent.templates)
            },
            "compliance_agent": {
                "status": "ready",
                "pii_detection_enabled": self.compliance_agent.pii_detection_enabled
            },
            "orchestrator": {
                "status": "ready",
                "circuit_breaker_open": self.circuit_open,
                "failure_count": self.failure_count
            }
        }
    
    def reset_circuit_breaker(self):
        """Reset circuit breaker state."""
        self.circuit_open = False
        self.failure_count = 0
        self.last_failure_time = None
        logger.info("Circuit breaker reset")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of all agents."""
        health_status = {
            "overall_status": "healthy",
            "agents": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check each agent
        agents = [
            ("classifier", self.classifier_agent),
            ("risk_scorer", self.risk_scorer_agent),
            ("router", self.router_agent),
            ("decision_support", self.decision_support_agent),
            ("compliance", self.compliance_agent)
        ]
        
        for agent_name, agent in agents:
            try:
                # Simple health check - try to access agent attributes
                if hasattr(agent, '__dict__'):
                    health_status["agents"][agent_name] = {
                        "status": "healthy",
                        "details": "Agent initialized successfully"
                    }
                else:
                    health_status["agents"][agent_name] = {
                        "status": "unhealthy",
                        "details": "Agent not properly initialized"
                    }
            except Exception as e:
                health_status["agents"][agent_name] = {
                    "status": "unhealthy",
                    "details": str(e)
                }
                health_status["overall_status"] = "unhealthy"
        
        # Check circuit breaker
        if self.circuit_open:
            health_status["overall_status"] = "degraded"
            health_status["circuit_breaker"] = {
                "status": "open",
                "failure_count": self.failure_count,
                "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None
            }
        
        return health_status
