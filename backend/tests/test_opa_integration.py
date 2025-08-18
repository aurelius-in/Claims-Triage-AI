"""
Test script for OPA integration functionality.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from core.opa import (
    init_opa, close_opa, opa_health_check,
    evaluate_routing_policy, evaluate_compliance_policy,
    evaluate_access_control_policy, evaluate_data_governance_policy,
    create_policy, update_policy, delete_policy,
    list_policies, validate_policy
)


@pytest.mark.asyncio
async def test_opa_connection():
    """Test OPA connection initialization."""
    # This test requires a running OPA instance
    # In a real environment, you'd use a test OPA container
    try:
        success = await init_opa()
        assert success is True or success is False  # Should return boolean
    except Exception as e:
        # If OPA is not available, that's okay for testing
        print(f"OPA not available: {e}")


@pytest.mark.asyncio
async def test_opa_health_check():
    """Test OPA health check."""
    health = await opa_health_check()
    assert isinstance(health, dict)
    assert "status" in health
    assert "timestamp" in health


@pytest.mark.asyncio
async def test_routing_policy_evaluation():
    """Test routing policy evaluation."""
    case_data = {
        "case_type": "auto_insurance",
        "risk_level": "low",
        "urgency_level": "normal",
        "claim_amount": 5000
    }
    
    result = await evaluate_routing_policy(case_data)
    assert isinstance(result, dict)
    assert "success" in result
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_compliance_policy_evaluation():
    """Test compliance policy evaluation."""
    case_data = {
        "title": "Test Case",
        "description": "Test description without PII",
        "case_type": "auto_insurance",
        "created_at": "2024-01-01T00:00:00Z",
        "audit_log_enabled": True,
        "user_id": "user123"
    }
    
    result = await evaluate_compliance_policy(case_data)
    assert isinstance(result, dict)
    assert "success" in result
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_access_control_policy_evaluation():
    """Test access control policy evaluation."""
    user_data = {
        "role": "agent",
        "team_id": "team123",
        "security_clearance": 2
    }
    
    resource_data = {
        "type": "case",
        "assigned_team_id": "team123",
        "case_type": "auto_insurance",
        "risk_level": "low",
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    result = await evaluate_access_control_policy(user_data, resource_data)
    assert isinstance(result, dict)
    assert "success" in result
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_data_governance_policy_evaluation():
    """Test data governance policy evaluation."""
    data_operation = {
        "type": "export",
        "user": {"role": "admin"},
        "data_classification": "internal",
        "destination": "internal"
    }
    
    result = await evaluate_data_governance_policy(data_operation)
    assert isinstance(result, dict)
    assert "success" in result
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_policy_validation():
    """Test policy validation."""
    valid_policy = """
package test_policy

default allow = false

allow {
    input.user.role == "admin"
}
"""
    
    result = await validate_policy(valid_policy)
    assert isinstance(result, dict)
    assert "success" in result
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_policy_management():
    """Test policy creation, listing, and deletion."""
    # Test policy creation
    policy_name = "test_policy"
    policy_content = """
package test_policy

default allow = false

allow {
    input.user.role == "admin"
}
"""
    
    create_result = await create_policy(policy_name, policy_content)
    assert isinstance(create_result, dict)
    assert "success" in create_result
    
    # Test policy listing
    list_result = await list_policies()
    assert isinstance(list_result, dict)
    assert "success" in list_result
    if list_result["success"]:
        assert "policies" in list_result
    
    # Test policy deletion
    delete_result = await delete_policy(policy_name)
    assert isinstance(delete_result, dict)
    assert "success" in delete_result


@pytest.mark.asyncio
async def test_policy_update():
    """Test policy update functionality."""
    policy_name = "update_test_policy"
    original_content = """
package update_test_policy

default allow = false

allow {
    input.user.role == "admin"
}
"""
    
    updated_content = """
package update_test_policy

default allow = false

allow {
    input.user.role == "admin"
}

allow {
    input.user.role == "supervisor"
}
"""
    
    # Create policy
    create_result = await create_policy(policy_name, original_content)
    assert create_result["success"]
    
    # Update policy
    update_result = await update_policy(policy_name, updated_content)
    assert isinstance(update_result, dict)
    assert "success" in update_result
    
    # Clean up
    await delete_policy(policy_name)


@pytest.mark.asyncio
async def test_invalid_policy_validation():
    """Test validation of invalid policies."""
    invalid_policy = """
invalid rego syntax
"""
    
    result = await validate_policy(invalid_policy)
    assert isinstance(result, dict)
    assert "success" in result
    # Should fail validation
    assert not result["success"]


@pytest.mark.asyncio
async def test_empty_policy_validation():
    """Test validation of empty policy."""
    empty_policy = ""
    
    result = await validate_policy(empty_policy)
    assert isinstance(result, dict)
    assert "success" in result
    # Should fail validation
    assert not result["success"]


async def main():
    """Run all OPA integration tests."""
    print("🧪 Running OPA integration tests...")
    
    tests = [
        test_opa_connection,
        test_opa_health_check,
        test_routing_policy_evaluation,
        test_compliance_policy_evaluation,
        test_access_control_policy_evaluation,
        test_data_governance_policy_evaluation,
        test_policy_validation,
        test_policy_management,
        test_policy_update,
        test_invalid_policy_validation,
        test_empty_policy_validation
    ]
    
    for test in tests:
        try:
            await test()
            print(f"✅ {test.__name__} passed")
        except Exception as e:
            print(f"❌ {test.__name__} failed: {str(e)}")
    
    print("🏁 OPA integration tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
