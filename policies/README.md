# OPA Policies

This directory contains Open Policy Agent (OPA) policies for the Claims Triage AI platform.

## Policy Types

### 1. Routing Policies (`routing_policy.rego`)
- Case assignment based on type, risk level, and urgency
- Team assignment logic
- SLA requirements
- Escalation rules

### 2. Compliance Policies (`compliance_policy.rego`)
- Data validation rules
- PII compliance checks
- Regulatory compliance (HIPAA, GDPR, etc.)
- Audit trail requirements

### 3. Access Control Policies (`access_control_policy.rego`)
- Role-based access control (RBAC)
- Team-based access control
- Time-based access restrictions
- Risk-based access control

### 4. Data Governance Policies (`data_governance_policy.rego`)
- Data retention rules
- Data classification
- Export and deletion policies
- Encryption requirements

## Policy Management

### Hot-Reloading
Policies are automatically reloaded when files are modified. The system monitors this directory for changes and updates OPA accordingly.

### Validation
All policies are validated for:
- Rego syntax correctness
- Policy structure
- OPA server compatibility

### Version Control
Policies should be version controlled and changes should be reviewed before deployment.

## Usage

### Creating Custom Policies
1. Create a new `.rego` file in this directory
2. Follow the Rego syntax and structure
3. Include proper package declarations
4. Test the policy using the validation endpoint

### Example Custom Policy
```rego
package custom_policy

default allow = false

allow {
    input.case.risk_level == "low"
    input.case.urgency_level == "normal"
    input.case.case_type == "auto_insurance"
}

team_assignment = "tier_1" {
    input.case.risk_level == "low"
}
```

## Testing Policies

Use the API endpoints to test policies:
- `POST /api/v1/policies/validate` - Validate policy syntax
- `POST /api/v1/policies/routing/evaluate` - Test routing policies
- `POST /api/v1/policies/compliance/evaluate` - Test compliance policies

## Best Practices

1. **Keep policies simple and readable**
2. **Use descriptive rule names**
3. **Include comments for complex logic**
4. **Test policies thoroughly before deployment**
5. **Version control all policy changes**
6. **Document policy requirements and assumptions**
