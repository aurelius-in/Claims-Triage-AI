"""
Data layer for the Claims Triage AI platform.

This package contains:
- Database models and schemas
- Database connection and session management
- Repository pattern implementations
- Data access layer abstractions
"""

from .database import get_db, init_db, close_db
from .models import *
from .schemas import *
from .repository import *

__all__ = [
    "get_db",
    "init_db", 
    "close_db",
]
