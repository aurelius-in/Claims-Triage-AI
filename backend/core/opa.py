"""
Open Policy Agent (OPA) integration for policy-as-code.

This module provides:
- OPA client configuration and connection management
- Policy engine integration for routing and compliance decisions
- Policy hot-reloading and management
- Policy validation and testing
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import aiohttp
from datetime import datetime

from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# OPA client configuration
OPA_BASE_URL = os.getenv("OPA_BASE_URL", "http://localhost:8181")
OPA_TIMEOUT = int(os.getenv("OPA_TIMEOUT", "30"))
OPA_POLICIES_PATH = Path(os.getenv("OPA_POLICIES_PATH", "./policies"))

# Policy collections
POLICY_COLLECTIONS = {
    "routing": "routing_policies",
    "compliance": "compliance_policies", 
    "access_control": "access_control_policies",
    "data_governance": "data_governance_policies"
}


class OPAClient:
    """OPA client for policy evaluation and management."""
    
    def __init__(self, base_url: str = OPA_BASE_URL, timeout: int = OPA_TIMEOUT):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.health_status = "unknown"
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def connect(self):
        """Initialize HTTP session."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.info(f"✅ OPA client connected to {self.base_url}")
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("✅ OPA client disconnected")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OPA health status."""
        try:
            await self.connect()
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.health_status = "healthy"
                    return {
                        "status": "healthy",
                        "version": data.get("version", "unknown"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    self.health_status = "unhealthy"
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            self.health_status = "unhealthy"
            logger.error(f"❌ OPA health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def evaluate_policy(
        self, 
        policy_path: str, 
        input_data: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate a policy with given input."""
        try:
            await self.connect()
            
            payload = {"input": input_data}
            if data:
                payload["data"] = data
            
            url = f"{self.base_url}/v1/data/{policy_path}"
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "result": result.get("result", {}),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Policy evaluation failed: {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"❌ Policy evaluation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def load_policy(self, policy_name: str, policy_content: str) -> Dict[str, Any]:
        """Load a policy into OPA."""
        try:
            await self.connect()
            
            url = f"{self.base_url}/v1/policies/{policy_name}"
            
            async with self.session.put(url, data=policy_content) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Policy {policy_name} loaded successfully")
                    return {
                        "success": True,
                        "result": result,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Policy load failed: {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"❌ Policy load error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def delete_policy(self, policy_name: str) -> Dict[str, Any]:
        """Delete a policy from OPA."""
        try:
            await self.connect()
            
            url = f"{self.base_url}/v1/policies/{policy_name}"
            
            async with self.session.delete(url) as response:
                if response.status == 200:
                    logger.info(f"✅ Policy {policy_name} deleted successfully")
                    return {
                        "success": True,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Policy deletion failed: {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"❌ Policy deletion error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def list_policies(self) -> Dict[str, Any]:
        """List all loaded policies."""
        try:
            await self.connect()
            
            url = f"{self.base_url}/v1/policies"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "policies": result.get("result", []),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Policy listing failed: {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"❌ Policy listing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


class PolicyManager:
    """Policy manager for OPA integration."""
    
    def __init__(self):
        self.opa_client = OPAClient()
        self.policies_path = OPA_POLICIES_PATH
        self.policies_path.mkdir(exist_ok=True)
        self.watcher_task: Optional[asyncio.Task] = None
        self.running = False
        
    async def initialize(self) -> bool:
        """Initialize policy manager and load default policies."""
        try:
            # Check OPA health
            health = await self.opa_client.health_check()
            if health["status"] != "healthy":
                logger.warning(f"⚠️ OPA not healthy: {health.get('error', 'unknown')}")
                return False
            
            # Load default policies
            await self.load_default_policies()
            
            # Start policy watcher
            await self.start_policy_watcher()
            
            logger.info("✅ Policy manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Policy manager initialization failed: {str(e)}")
            return False
    
    async def shutdown(self):
        """Shutdown policy manager."""
        self.running = False
        if self.watcher_task:
            self.watcher_task.cancel()
            try:
                await self.watcher_task
            except asyncio.CancelledError:
                pass
        
        await self.opa_client.close()
        logger.info("✅ Policy manager shutdown complete")
    
    async def load_default_policies(self):
        """Load default policies for routing and compliance."""
        default_policies = {
            "routing_policy.rego": ROUTING_POLICY,
            "compliance_policy.rego": COMPLIANCE_POLICY,
            "access_control_policy.rego": ACCESS_CONTROL_POLICY,
            "data_governance_policy.rego": DATA_GOVERNANCE_POLICY
        }
        
        for policy_name, policy_content in default_policies.items():
            policy_path = self.policies_path / policy_name
            policy_path.write_text(policy_content)
            
            # Load into OPA
            result = await self.opa_client.load_policy(policy_name, policy_content)
            if result["success"]:
                logger.info(f"✅ Loaded default policy: {policy_name}")
            else:
                logger.error(f"❌ Failed to load default policy {policy_name}: {result.get('error')}")
    
    async def start_policy_watcher(self):
        """Start policy file watcher for hot-reloading."""
        self.running = True
        self.watcher_task = asyncio.create_task(self._policy_watcher())
        logger.info("✅ Policy watcher started")
    
    async def _policy_watcher(self):
        """Watch for policy file changes and reload automatically."""
        last_modified = {}
        
        while self.running:
            try:
                for policy_file in self.policies_path.glob("*.rego"):
                    current_mtime = policy_file.stat().st_mtime
                    last_mtime = last_modified.get(policy_file.name, 0)
                    
                    if current_mtime > last_mtime:
                        logger.info(f"🔄 Detected change in {policy_file.name}, reloading...")
                        
                        # Read and reload policy
                        policy_content = policy_file.read_text()
                        result = await self.opa_client.load_policy(policy_file.name, policy_content)
                        
                        if result["success"]:
                            logger.info(f"✅ Policy {policy_file.name} reloaded successfully")
                            last_modified[policy_file.name] = current_mtime
                        else:
                            logger.error(f"❌ Failed to reload policy {policy_file.name}: {result.get('error')}")
                
                await asyncio.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                logger.error(f"❌ Policy watcher error: {str(e)}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def evaluate_routing_policy(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate routing policy for case assignment."""
        input_data = {
            "case": case_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.opa_client.evaluate_policy("routing_policy", input_data)
    
    async def evaluate_compliance_policy(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate compliance policy for case validation."""
        input_data = {
            "case": case_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.opa_client.evaluate_policy("compliance_policy", input_data)
    
    async def evaluate_access_control_policy(self, user_data: Dict[str, Any], resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate access control policy."""
        input_data = {
            "user": user_data,
            "resource": resource_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.opa_client.evaluate_policy("access_control_policy", input_data)
    
    async def evaluate_data_governance_policy(self, data_operation: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate data governance policy."""
        input_data = {
            "operation": data_operation,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.opa_client.evaluate_policy("data_governance_policy", input_data)
    
    async def create_policy(self, policy_name: str, policy_content: str) -> Dict[str, Any]:
        """Create a new policy."""
        try:
            # Save to file
            policy_path = self.policies_path / f"{policy_name}.rego"
            policy_path.write_text(policy_content)
            
            # Load into OPA
            result = await self.opa_client.load_policy(f"{policy_name}.rego", policy_content)
            
            if result["success"]:
                logger.info(f"✅ Policy {policy_name} created successfully")
                return {
                    "success": True,
                    "policy_name": policy_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"❌ Policy creation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def update_policy(self, policy_name: str, policy_content: str) -> Dict[str, Any]:
        """Update an existing policy."""
        return await self.create_policy(policy_name, policy_content)
    
    async def delete_policy(self, policy_name: str) -> Dict[str, Any]:
        """Delete a policy."""
        try:
            # Remove from file system
            policy_path = self.policies_path / f"{policy_name}.rego"
            if policy_path.exists():
                policy_path.unlink()
            
            # Remove from OPA
            result = await self.opa_client.delete_policy(f"{policy_name}.rego")
            
            if result["success"]:
                logger.info(f"✅ Policy {policy_name} deleted successfully")
                return {
                    "success": True,
                    "policy_name": policy_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"❌ Policy deletion error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def list_policies(self) -> Dict[str, Any]:
        """List all available policies."""
        try:
            policies = []
            for policy_file in self.policies_path.glob("*.rego"):
                policies.append({
                    "name": policy_file.stem,
                    "filename": policy_file.name,
                    "modified": datetime.fromtimestamp(policy_file.stat().st_mtime).isoformat(),
                    "size": policy_file.stat().st_size
                })
            
            return {
                "success": True,
                "policies": policies,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Policy listing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def validate_policy(self, policy_content: str) -> Dict[str, Any]:
        """Validate policy syntax and structure."""
        try:
            # Basic Rego syntax validation
            if not policy_content.strip():
                return {
                    "success": False,
                    "error": "Policy content is empty",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Check for required Rego elements
            if "package" not in policy_content:
                return {
                    "success": False,
                    "error": "Policy must contain a package declaration",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Try to load into OPA for validation
            temp_policy_name = f"temp_validation_{datetime.utcnow().timestamp()}"
            result = await self.opa_client.load_policy(f"{temp_policy_name}.rego", policy_content)
            
            if result["success"]:
                # Clean up temporary policy
                await self.opa_client.delete_policy(f"{temp_policy_name}.rego")
                return {
                    "success": True,
                    "message": "Policy validation successful",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"❌ Policy validation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Default policies
ROUTING_POLICY = """
package routing_policy

# Default routing decision
default allow = false

# Route cases based on type and risk level
allow {
    input.case.case_type == "auto_insurance"
    input.case.risk_level == "low"
    input.case.urgency_level == "normal"
}

# Route high-risk cases to specialized team
allow {
    input.case.risk_level == "high"
    input.case.case_type == "fraud"
}

# Route urgent cases to priority queue
allow {
    input.case.urgency_level == "high"
    input.case.case_type == "health_insurance"
}

# Route based on claim amount
allow {
    input.case.claim_amount > 10000
    input.case.case_type == "auto_insurance"
}

# Assign team based on case characteristics
team_assignment = "tier_1" {
    input.case.risk_level == "low"
    input.case.urgency_level == "normal"
}

team_assignment = "tier_2" {
    input.case.risk_level == "medium"
    input.case.urgency_level == "normal"
}

team_assignment = "tier_3" {
    input.case.risk_level == "high"
    input.case.urgency_level == "high"
}

team_assignment = "fraud_specialist" {
    input.case.case_type == "fraud"
    input.case.risk_level == "high"
}

# SLA requirements based on case type
sla_hours = 24 {
    input.case.case_type == "auto_insurance"
    input.case.urgency_level == "normal"
}

sla_hours = 4 {
    input.case.urgency_level == "high"
}

sla_hours = 168 {
    input.case.urgency_level == "low"
    input.case.risk_level == "low"
}
"""

COMPLIANCE_POLICY = """
package compliance_policy

# Default compliance check
default compliant = false

# Check for required fields
compliant {
    input.case.title != ""
    input.case.description != ""
    input.case.case_type != ""
}

# Check for PII compliance
pii_compliant {
    not contains(input.case.description, "SSN")
    not contains(input.case.description, "credit card")
    not contains(input.case.description, "password")
}

# Check for data retention compliance
retention_compliant {
    input.case.created_at != ""
    input.case.case_type == "auto_insurance"
}

# Check for regulatory compliance
regulatory_compliant {
    input.case.case_type == "health_insurance"
    input.case.hipaa_compliant == true
}

# Check for audit trail requirements
audit_compliant {
    input.case.audit_log_enabled == true
    input.case.user_id != ""
}

# Data classification
data_classification = "public" {
    input.case.case_type == "general_inquiry"
    input.case.risk_level == "low"
}

data_classification = "internal" {
    input.case.case_type == "auto_insurance"
    input.case.risk_level == "medium"
}

data_classification = "confidential" {
    input.case.case_type == "fraud"
    input.case.risk_level == "high"
}

data_classification = "restricted" {
    input.case.case_type == "health_insurance"
    input.case.hipaa_compliant == true
}
"""

ACCESS_CONTROL_POLICY = """
package access_control_policy

# Default access denied
default allow = false

# Admin access
allow {
    input.user.role == "admin"
}

# Supervisor access to all cases
allow {
    input.user.role == "supervisor"
    input.resource.type == "case"
}

# Agent access to assigned cases
allow {
    input.user.role == "agent"
    input.resource.type == "case"
    input.resource.assigned_team_id == input.user.team_id
}

# Auditor access to audit logs
allow {
    input.user.role == "auditor"
    input.resource.type == "audit_log"
}

# Read-only access for certain roles
read_only {
    input.user.role == "viewer"
    input.resource.type == "case"
    input.resource.status == "closed"
}

# Team-based access control
team_access {
    input.user.role == "agent"
    input.resource.type == "case"
    input.resource.assigned_team_id == input.user.team_id
    input.resource.case_type in ["auto_insurance", "health_insurance"]
}

# Time-based access control
time_based_access {
    input.user.role == "agent"
    input.resource.type == "case"
    input.resource.created_at > "2024-01-01T00:00:00Z"
}

# Risk-based access control
risk_based_access {
    input.user.role == "agent"
    input.resource.type == "case"
    input.resource.risk_level == "low"
    input.user.security_clearance >= 1
}

risk_based_access {
    input.user.role == "supervisor"
    input.resource.type == "case"
    input.resource.risk_level == "high"
    input.user.security_clearance >= 3
}
"""

DATA_GOVERNANCE_POLICY = """
package data_governance_policy

# Default data operation denied
default allow = false

# Allow data export for authorized users
allow {
    input.operation.type == "export"
    input.operation.user.role == "admin"
    input.operation.data_classification == "internal"
}

# Allow data deletion for compliance
allow {
    input.operation.type == "delete"
    input.operation.user.role == "admin"
    input.operation.reason == "compliance"
    input.operation.data_age_days > 2555  # 7 years
}

# Allow data anonymization
allow {
    input.operation.type == "anonymize"
    input.operation.user.role == "data_steward"
    input.operation.data_classification == "confidential"
}

# Data retention rules
retention_required {
    input.operation.type == "delete"
    input.operation.data_classification == "confidential"
    input.operation.data_age_days < 2555
}

# Data encryption requirements
encryption_required {
    input.operation.type == "export"
    input.operation.data_classification == "confidential"
    input.operation.destination == "external"
}

# Data masking requirements
masking_required {
    input.operation.type == "view"
    input.operation.data_classification == "restricted"
    input.operation.user.role == "agent"
}

# Audit requirements
audit_required {
    input.operation.type == "modify"
    input.operation.data_classification == "confidential"
}

audit_required {
    input.operation.type == "export"
    input.operation.data_classification == "restricted"
}

# Data residency requirements
residency_compliant {
    input.operation.type == "store"
    input.operation.data_classification == "restricted"
    input.operation.location == "us_east"
}
"""


# Global policy manager instance
policy_manager = PolicyManager()


# Public API functions
async def init_opa() -> bool:
    """Initialize OPA integration."""
    return await policy_manager.initialize()


async def close_opa():
    """Close OPA integration."""
    await policy_manager.shutdown()


async def opa_health_check() -> Dict[str, Any]:
    """Check OPA health status."""
    return await policy_manager.opa_client.health_check()


async def evaluate_routing_policy(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate routing policy for case assignment."""
    return await policy_manager.evaluate_routing_policy(case_data)


async def evaluate_compliance_policy(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate compliance policy for case validation."""
    return await policy_manager.evaluate_compliance_policy(case_data)


async def evaluate_access_control_policy(user_data: Dict[str, Any], resource_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate access control policy."""
    return await policy_manager.evaluate_access_control_policy(user_data, resource_data)


async def evaluate_data_governance_policy(data_operation: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate data governance policy."""
    return await policy_manager.evaluate_data_governance_policy(data_operation)


async def create_policy(policy_name: str, policy_content: str) -> Dict[str, Any]:
    """Create a new policy."""
    return await policy_manager.create_policy(policy_name, policy_content)


async def update_policy(policy_name: str, policy_content: str) -> Dict[str, Any]:
    """Update an existing policy."""
    return await policy_manager.update_policy(policy_name, policy_content)


async def delete_policy(policy_name: str) -> Dict[str, Any]:
    """Delete a policy."""
    return await policy_manager.delete_policy(policy_name)


async def list_policies() -> Dict[str, Any]:
    """List all available policies."""
    return await policy_manager.list_policies()


async def validate_policy(policy_content: str) -> Dict[str, Any]:
    """Validate policy syntax and structure."""
    return await policy_manager.validate_policy(policy_content)
