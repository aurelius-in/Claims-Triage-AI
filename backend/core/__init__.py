"""
Core configuration and utilities for the Claims Triage AI platform.

This module contains:
- Configuration management
- Logging setup
- Monitoring and telemetry
- Authentication and authorization
- Database connections
"""

from .config import Settings, get_settings
from .logging import setup_logging
from .monitoring import setup_monitoring
from .auth import get_current_user, create_access_token

__all__ = [
    "Settings",
    "get_settings", 
    "setup_logging",
    "setup_monitoring",
    "get_current_user",
    "create_access_token"
]
