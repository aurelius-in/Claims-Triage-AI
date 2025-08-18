package routing

# Default routing decision
default decision = {
    "team": "Tier-2",
    "sla_hours": 72,
    "escalation": false,
    "confidence": 0.7,
    "reasoning": "Default routing to Tier-2"
}

# High-risk escalation policy
decision = {
    "team": "Escalation",
    "sla_hours": 4,
    "escalation": true,
    "confidence": 0.95,
    "reasoning": "High-risk case escalated for immediate review"
} {
    input.case.risk_level == "high"
    input.case.urgency == "critical"
}

decision = {
    "team": "Escalation", 
    "sla_hours": 4,
    "escalation": true,
    "confidence": 0.9,
    "reasoning": "Extreme risk case escalated"
} {
    input.case.risk_level == "extreme"
}

# Fraud review policy
decision = {
    "team": "Fraud-Review",
    "sla_hours": 24,
    "escalation": false,
    "confidence": 0.9,
    "reasoning": "Fraud case routed to specialized team"
} {
    input.case.case_type == "fraud_review"
}

decision = {
    "team": "Fraud-Review",
    "sla_hours": 24,
    "escalation": false,
    "confidence": 0.85,
    "reasoning": "High-risk case with fraud indicators"
} {
    input.case.risk_level == "high"
    input.case.case_type == "bank_dispute"
}

# Legal cases policy
decision = {
    "team": "Specialist",
    "sla_hours": 48,
    "escalation": false,
    "confidence": 0.9,
    "reasoning": "Legal case routed to specialist team"
} {
    input.case.case_type == "legal_intake"
}

# Urgent cases policy
decision = {
    "team": "Tier-1",
    "sla_hours": 2,
    "escalation": false,
    "confidence": 0.85,
    "reasoning": "Urgent case routed to Tier-1"
} {
    input.case.urgency == "critical"
    input.case.risk_level != "high"
    input.case.risk_level != "extreme"
}

decision = {
    "team": "Tier-1",
    "sla_hours": 4,
    "escalation": false,
    "confidence": 0.8,
    "reasoning": "High urgency case routed to Tier-1"
} {
    input.case.urgency == "high"
    input.case.risk_level == "low"
}

# Healthcare prior authorization policy
decision = {
    "team": "Specialist",
    "sla_hours": 24,
    "escalation": false,
    "confidence": 0.9,
    "reasoning": "Healthcare prior auth routed to specialist"
} {
    input.case.case_type == "healthcare_prior_auth"
    input.case.urgency == "high"
}

decision = {
    "team": "Tier-2",
    "sla_hours": 72,
    "escalation": false,
    "confidence": 0.8,
    "reasoning": "Standard healthcare prior auth"
} {
    input.case.case_type == "healthcare_prior_auth"
    input.case.urgency == "medium"
}

# High-value cases policy
decision = {
    "team": "Specialist",
    "sla_hours": 24,
    "escalation": false,
    "confidence": 0.85,
    "reasoning": "High-value case routed to specialist"
} {
    input.case.amount > 10000
    input.case.risk_level == "medium"
}

# Team capacity check
decision = {
    "team": alternative_team,
    "sla_hours": decision.sla_hours,
    "escalation": decision.escalation,
    "confidence": decision.confidence * 0.9,
    "reasoning": sprintf("Original team at capacity, routed to %v", [alternative_team])
} {
    original_decision := decision
    original_team := original_decision.team
    team_info := input.teams[original_team]
    
    # Check if team is at capacity (90% threshold)
    team_info.current_load >= team_info.capacity * 0.9
    
    # Find alternative team
    alternative_team := find_alternative_team(original_team, input.case)
}

# Helper function to find alternative team
find_alternative_team(original_team, case) = alternative {
    alternatives := get_team_alternatives(original_team)
    alternative := alternatives[_]
    team_info := input.teams[alternative]
    
    # Check if alternative team can handle this case type
    case.case_type == team_info.case_types[_]
    
    # Check if alternative team has capacity
    team_info.current_load < team_info.capacity * 0.8
}

# Team alternatives mapping
get_team_alternatives("Tier-1") = ["Tier-2", "Specialist"]
get_team_alternatives("Tier-2") = ["Tier-1", "Specialist"]
get_team_alternatives("Specialist") = ["Tier-1", "Tier-2"]
get_team_alternatives("Fraud-Review") = ["Specialist", "Escalation"]
get_team_alternatives("Escalation") = ["Specialist", "Tier-1"]
get_team_alternatives(_) = ["Tier-2"]

# Validation rules
valid_decision(decision) {
    decision.team != ""
    decision.sla_hours > 0
    decision.sla_hours <= 168  # Max 1 week
    decision.confidence >= 0
    decision.confidence <= 1
}

# Policy violations
policy_violations = violations {
    violations := [
        "high_risk_to_tier1" |
        input.case.risk_level == "high"
        decision.team == "Tier-1"
    ]
}

policy_violations = violations {
    violations := [
        "extreme_risk_to_tier2" |
        input.case.risk_level == "extreme"
        decision.team == "Tier-2"
    ]
}

# Audit information
audit_info = {
    "policy_version": "1.0",
    "decision_timestamp": time.now_ns(),
    "case_id": input.case.id,
    "original_decision": decision,
    "policy_violations": policy_violations,
    "team_capacity_used": {
        team: input.teams[team].current_load |
        team := decision.team
    }
}
