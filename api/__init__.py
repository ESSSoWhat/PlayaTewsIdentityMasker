"""
PlayaTewsIdentityMasker API Package
RESTful API for face swapping and identity masking operations.
"""

__version__ = "1.0.0"
__author__ = "PlayaTewsIdentityMasker Team"
__description__ = "Secure RESTful API for real-time face swapping and identity masking"

from .main import app
from .config import APIConfig
from .security import SecurityManager

__all__ = ["app", "APIConfig", "SecurityManager"] 