"""
REST API Module for IPv9 Tool

Provides a robust API interface for programmatic access to IPv9 functionality.
"""

from .server import create_api_app
from .client import IPv9APIClient
from .models import *

__all__ = ['create_api_app', 'IPv9APIClient']
