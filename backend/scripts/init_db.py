#!/usr/bin/env python3
"""
Database initialization script for Claims Triage AI.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from data.database import init_db, close_db
from core.logging import setup_logging

async def main():
    """Initialize the database."""
    setup_logging()
    
    print("Initializing Claims Triage AI database...")
    
    try:
        await init_db()
        print("✅ Database initialized successfully!")
        print("\nDefault credentials:")
        print("Username: admin")
        print("Password: admin123")
        print("\nDefault teams created:")
        print("- Auto Insurance Team")
        print("- Health Insurance Team") 
        print("- Fraud Review Team")
        print("- Legal Team")
        print("- Healthcare Team")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
