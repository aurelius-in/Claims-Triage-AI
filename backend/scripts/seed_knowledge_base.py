"""
Knowledge base seeder script for the Claims Triage AI platform.

This script populates the vector store with initial knowledge base entries,
policies, and SOPs for different domains.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add the backend directory to the Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.vector_store import (
    init_vector_store,
    close_vector_store,
    add_knowledge_base_entry,
    add_policy,
    add_sop
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Knowledge base content for different domains
INSURANCE_KNOWLEDGE = [
    {
        "content": "Auto insurance claims typically require police reports, photos of damage, and witness statements. Claims exceeding $10,000 require additional documentation and may trigger fraud investigation protocols.",
        "metadata": {
            "domain": "insurance",
            "category": "auto_claims",
            "priority": "high",
            "tags": ["auto", "claims", "documentation", "fraud"]
        },
        "category": "auto_claims"
    },
    {
        "content": "Health insurance claims require medical bills, diagnosis codes, and treatment plans. Pre-authorization is required for procedures over $5,000. Emergency room visits are automatically approved within 48 hours.",
        "metadata": {
            "domain": "insurance",
            "category": "health_claims",
            "priority": "high",
            "tags": ["health", "medical", "billing", "authorization"]
        },
        "category": "health_claims"
    },
    {
        "content": "Property damage claims require immediate documentation including photos, repair estimates, and proof of ownership. Claims over $25,000 require structural engineer assessment.",
        "metadata": {
            "domain": "insurance",
            "category": "property_claims",
            "priority": "medium",
            "tags": ["property", "damage", "assessment", "documentation"]
        },
        "category": "property_claims"
    }
]

HEALTHCARE_KNOWLEDGE = [
    {
        "content": "Prior authorization requests must be submitted 72 hours before non-emergency procedures. Required documents include medical necessity justification, clinical notes, and cost estimates.",
        "metadata": {
            "domain": "healthcare",
            "category": "prior_auth",
            "priority": "high",
            "tags": ["authorization", "medical", "procedures", "documentation"]
        },
        "category": "prior_auth"
    },
    {
        "content": "Medical coding errors are the leading cause of claim denials. Ensure ICD-10 codes match diagnosis and CPT codes align with procedures performed. Regular audits reduce error rates by 40%.",
        "metadata": {
            "domain": "healthcare",
            "category": "coding",
            "priority": "high",
            "tags": ["coding", "ICD-10", "CPT", "denials", "audits"]
        },
        "category": "coding"
    },
    {
        "content": "Emergency department claims require triage notes, vital signs, and treatment timeline. Claims without proper documentation are automatically flagged for review.",
        "metadata": {
            "domain": "healthcare",
            "category": "emergency",
            "priority": "medium",
            "tags": ["emergency", "triage", "documentation", "review"]
        },
        "category": "emergency"
    }
]

FINANCE_KNOWLEDGE = [
    {
        "content": "Credit card dispute claims require transaction details, merchant communication records, and evidence of attempted resolution. Claims over $500 require additional fraud screening.",
        "metadata": {
            "domain": "finance",
            "category": "disputes",
            "priority": "high",
            "tags": ["credit", "disputes", "fraud", "documentation"]
        },
        "category": "disputes"
    },
    {
        "content": "Loan applications require income verification, credit history, and debt-to-income ratio analysis. Applications with DTI over 43% require additional underwriting review.",
        "metadata": {
            "domain": "finance",
            "category": "loans",
            "priority": "medium",
            "tags": ["loans", "underwriting", "credit", "verification"]
        },
        "category": "loans"
    },
    {
        "content": "Investment fraud claims require transaction records, communication history, and regulatory filing documentation. Claims exceeding $10,000 trigger mandatory regulatory reporting.",
        "metadata": {
            "domain": "finance",
            "category": "fraud",
            "priority": "high",
            "tags": ["investment", "fraud", "regulatory", "reporting"]
        },
        "category": "fraud"
    }
]

LEGAL_KNOWLEDGE = [
    {
        "content": "Personal injury cases require medical records, accident reports, and witness statements. Cases with damages over $50,000 require expert witness testimony and economic analysis.",
        "metadata": {
            "domain": "legal",
            "category": "personal_injury",
            "priority": "high",
            "tags": ["injury", "medical", "witness", "expert", "damages"]
        },
        "category": "personal_injury"
    },
    {
        "content": "Contract disputes require original agreements, amendment history, and performance documentation. Cases involving amounts over $100,000 require mandatory mediation before trial.",
        "metadata": {
            "domain": "legal",
            "category": "contracts",
            "priority": "medium",
            "tags": ["contracts", "mediation", "performance", "agreements"]
        },
        "category": "contracts"
    },
    {
        "content": "Employment law cases require personnel files, performance reviews, and incident documentation. Cases alleging discrimination require EEOC filing within 180 days of incident.",
        "metadata": {
            "domain": "legal",
            "category": "employment",
            "priority": "high",
            "tags": ["employment", "discrimination", "EEOC", "personnel"]
        },
        "category": "employment"
    }
]

# Policies
POLICIES = [
    {
        "name": "Data Privacy Policy",
        "content": "All personal information must be encrypted at rest and in transit. Access to sensitive data requires multi-factor authentication. Data retention is limited to 7 years unless required by law. Breach notification must occur within 72 hours of discovery.",
        "metadata": {
            "policy_type": "compliance",
            "version": "1.0",
            "effective_date": "2024-01-01",
            "tags": ["privacy", "security", "compliance", "retention"]
        }
    },
    {
        "name": "Fraud Detection Policy",
        "content": "All claims over $10,000 require automated fraud screening. High-risk indicators include multiple claims in short period, inconsistent documentation, and suspicious patterns. Manual review is required for claims scoring above 0.7 risk threshold.",
        "metadata": {
            "policy_type": "fraud",
            "version": "1.0",
            "effective_date": "2024-01-01",
            "tags": ["fraud", "screening", "risk", "review"]
        }
    },
    {
        "name": "SLA Policy",
        "content": "Standard claims must be processed within 5 business days. High-priority claims require 24-hour response. Emergency claims must be processed within 4 hours. SLA breaches trigger automatic escalation and notification.",
        "metadata": {
            "policy_type": "sla",
            "version": "1.0",
            "effective_date": "2024-01-01",
            "tags": ["sla", "processing", "escalation", "notification"]
        }
    }
]

# Standard Operating Procedures
SOPS = [
    {
        "name": "Claim Intake Procedure",
        "content": "1. Verify claimant identity using government-issued ID\n2. Collect initial claim details and supporting documentation\n3. Assign unique claim number and priority level\n4. Route to appropriate team based on claim type and complexity\n5. Send confirmation email with claim number and next steps",
        "metadata": {
            "sop_type": "intake",
            "version": "1.0",
            "effective_date": "2024-01-01",
            "tags": ["intake", "verification", "routing", "communication"]
        }
    },
    {
        "name": "Document Review Procedure",
        "content": "1. Scan all documents for completeness and legibility\n2. Verify document authenticity and validity\n3. Extract key information and enter into system\n4. Flag missing or inconsistent information\n5. Request additional documentation if needed\n6. Update claim status and notify relevant parties",
        "metadata": {
            "sop_type": "review",
            "version": "1.0",
            "effective_date": "2024-01-01",
            "tags": ["review", "verification", "extraction", "communication"]
        }
    },
    {
        "name": "Escalation Procedure",
        "content": "1. Identify escalation triggers (SLA breach, high risk, complex case)\n2. Notify supervisor and relevant stakeholders\n3. Assign senior analyst or specialist\n4. Implement additional review and approval steps\n5. Update case priority and monitoring\n6. Document escalation rationale and actions taken",
        "metadata": {
            "sop_type": "escalation",
            "version": "1.0",
            "effective_date": "2024-01-01",
            "tags": ["escalation", "notification", "approval", "documentation"]
        }
    }
]

async def seed_knowledge_base():
    """Seed the knowledge base with initial data."""
    try:
        logger.info("🚀 Starting knowledge base seeding...")
        
        # Initialize vector store
        success = await init_vector_store()
        if not success:
            logger.error("❌ Failed to initialize vector store")
            return False
        
        # Add knowledge base entries
        logger.info("📚 Adding knowledge base entries...")
        for domain_data in [INSURANCE_KNOWLEDGE, HEALTHCARE_KNOWLEDGE, FINANCE_KNOWLEDGE, LEGAL_KNOWLEDGE]:
            for entry in domain_data:
                try:
                    entry_id = await add_knowledge_base_entry(
                        content=entry["content"],
                        metadata=entry["metadata"],
                        category=entry["category"]
                    )
                    logger.info(f"✅ Added knowledge base entry: {entry_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to add knowledge base entry: {str(e)}")
        
        # Add policies
        logger.info("📋 Adding policies...")
        for policy in POLICIES:
            try:
                policy_id = await add_policy(
                    policy_name=policy["name"],
                    content=policy["content"],
                    metadata=policy["metadata"]
                )
                logger.info(f"✅ Added policy: {policy_id}")
            except Exception as e:
                logger.error(f"❌ Failed to add policy: {str(e)}")
        
        # Add SOPs
        logger.info("📖 Adding Standard Operating Procedures...")
        for sop in SOPS:
            try:
                sop_id = await add_sop(
                    sop_name=sop["name"],
                    content=sop["content"],
                    metadata=sop["metadata"]
                )
                logger.info(f"✅ Added SOP: {sop_id}")
            except Exception as e:
                logger.error(f"❌ Failed to add SOP: {str(e)}")
        
        logger.info("🎉 Knowledge base seeding completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Knowledge base seeding failed: {str(e)}")
        return False
    finally:
        await close_vector_store()

async def main():
    """Main function to run the seeder."""
    success = await seed_knowledge_base()
    if success:
        logger.info("✅ Knowledge base seeding completed successfully")
    else:
        logger.error("❌ Knowledge base seeding failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
