"""
API Configuration and Security Settings
Handles environment variables, security configurations, and API settings.
"""

import os
import secrets
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """API Configuration class with security and performance settings."""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Security Configuration
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS Configuration
    allowed_origins: list = None
    allowed_methods: list = None
    allowed_headers: list = None
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # File Upload Configuration
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = None
    upload_directory: str = "uploads"
    
    # Caching Configuration
    cache_ttl: int = 300  # 5 minutes
    cache_max_size: int = 1000
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "api.log"
    
    def __post_init__(self):
        """Initialize default values and load from environment."""
        if self.allowed_origins is None:
            self.allowed_origins = ["http://localhost:3000", "http://localhost:8080"]
        
        if self.allowed_methods is None:
            self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        
        if self.allowed_headers is None:
            self.allowed_headers = ["*"]
        
        if self.allowed_file_types is None:
            self.allowed_file_types = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".avi", ".mov"]
        
        # Load from environment variables
        self._load_from_env()
        
        # Generate secret key if not provided
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(32)
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            "API_HOST": "host",
            "API_PORT": "port",
            "API_DEBUG": "debug",
            "API_SECRET_KEY": "secret_key",
            "API_ALGORITHM": "algorithm",
            "API_ACCESS_TOKEN_EXPIRE_MINUTES": "access_token_expire_minutes",
            "API_REFRESH_TOKEN_EXPIRE_DAYS": "refresh_token_expire_days",
            "API_RATE_LIMIT_REQUESTS": "rate_limit_requests",
            "API_RATE_LIMIT_WINDOW": "rate_limit_window",
            "API_MAX_FILE_SIZE": "max_file_size",
            "API_UPLOAD_DIRECTORY": "upload_directory",
            "API_CACHE_TTL": "cache_ttl",
            "API_CACHE_MAX_SIZE": "cache_max_size",
            "API_LOG_LEVEL": "log_level",
            "API_LOG_FILE": "log_file"
        }
        
        for env_var, attr_name in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if attr_name in ["port", "access_token_expire_minutes", "refresh_token_expire_days", 
                               "rate_limit_requests", "rate_limit_window", "max_file_size", 
                               "cache_ttl", "cache_max_size"]:
                    try:
                        setattr(self, attr_name, int(value))
                    except ValueError:
                        logger.warning(f"Invalid integer value for {env_var}: {value}")
                elif attr_name == "debug":
                    setattr(self, attr_name, value.lower() in ["true", "1", "yes"])
                else:
                    setattr(self, attr_name, value)
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        errors = []
        
        if self.port < 1 or self.port > 65535:
            errors.append("Port must be between 1 and 65535")
        
        if self.access_token_expire_minutes < 1:
            errors.append("Access token expire minutes must be at least 1")
        
        if self.rate_limit_requests < 1:
            errors.append("Rate limit requests must be at least 1")
        
        if self.max_file_size < 1:
            errors.append("Max file size must be at least 1 byte")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration validation error: {error}")
            return False
        
        return True

# Global configuration instance
config = APIConfig()

def get_config() -> APIConfig:
    """Get the global API configuration."""
    return config 