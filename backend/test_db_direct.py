#!/usr/bin/env python3
"""
Direct test script to verify the database implementation.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_database():
    """Test the database implementation."""
    try:
        # Import modules directly
        from core.config import get_settings
        from data.database import init_db, get_db_session, close_db
        from data.models import User, Case, CaseStatus, CasePriority, CaseType, UserRole
        from data.repository import user_repository, case_repository
        
        # Simple password hash function for testing
        def get_password_hash(password: str) -> str:
            return f"hashed_{password}"
        
        print("🔧 Testing database implementation...")
        
        # Get settings
        settings = get_settings()
        print(f"✅ Using database: {settings.database_url}")
        
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
        
        # Test health check
        from data.database import health_check
        health_status = await health_check()
        if health_status["status"] == "healthy":
            print("✅ Database health check passed")
        else:
            print(f"❌ Database health check failed: {health_status}")
        
        await close_db()
        print("✅ Database implementation test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database implementation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_database())
    sys.exit(0 if success else 1)
