#!/usr/bin/env python3
"""
Standalone database test with absolute imports.
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime
from typing import Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock settings for testing
class MockSettings:
    database_url = "sqlite+aiosqlite:///./test_claims_triage.db"
    debug = True

# Mock the config module
sys.modules['core.config'] = type('MockConfig', (), {'settings': MockSettings()})()

async def test_database():
    """Test the database implementation."""
    try:
        # Import database modules
        from data.database import init_db, get_db_session, close_db
        from data.models import User, Case, CaseStatus, CasePriority, CaseType, UserRole
        from data.repository import user_repository, case_repository
        
        # Simple password hash function for testing
        def get_password_hash(password: str) -> str:
            return f"hashed_{password}"
        
        print("🔧 Testing database implementation...")
        
        # Initialize database
        await init_db()
        print("✅ Database initialized")
        
        # Test basic operations
        async with get_db_session() as session:
            # Create a test user
            user_data = {
                "username": "testuser",
                "email": "test@example.com",
                "hashed_password": get_password_hash("testpass"),
                "full_name": "Test User",
                "role": UserRole.ANALYST,
                "is_active": True
            }
            
            user = await user_repository.create(session, **user_data)
            print(f"✅ Created user: {user.username}")
            
            # Create a test case
            case_data = {
                "case_number": "TEST-001",
                "title": "Test Case",
                "description": "A test case for testing",
                "case_type": CaseType.AUTO_CLAIM,
                "customer_name": "John Doe",
                "customer_email": "john@example.com",
                "claim_amount": 5000.00,
                "priority": CasePriority.NORMAL,
                "assigned_user_id": user.id
            }
            
            case = await case_repository.create(session, **case_data)
            print(f"✅ Created case: {case.case_number}")
            
            # Test retrieval
            retrieved_user = await user_repository.get_by_username(session, "testuser")
            retrieved_case = await case_repository.get_by_case_number(session, "TEST-001")
            
            if retrieved_user and retrieved_case:
                print("✅ Data retrieval working correctly")
            else:
                print("❌ Data retrieval failed")
        
        await close_db()
        print("✅ Database implementation test completed successfully!")
        
        # Clean up test database
        try:
            os.remove("./test_claims_triage.db")
            print("✅ Test database cleaned up")
        except:
            pass
        
    except Exception as e:
        print(f"❌ Database implementation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_database())
    sys.exit(0 if success else 1)
