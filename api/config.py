"""
API Configuration Module
Handles all configuration settings for the PlayaTewsIdentityMasker API.
"""

import os
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class APIConfig:
    """Configuration class for API settings."""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    
    # Security Configuration
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS Configuration
    allowed_origins: List[str] = None
    allowed_methods: List[str] = None
    allowed_headers: List[str] = None
    allow_credentials: bool = True
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = None
    upload_dir: str = "uploads"
    
    # Caching Configuration
    cache_ttl: int = 300  # 5 minutes
    cache_max_size: int = 1000
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "api.log"
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.allowed_origins is None:
            self.allowed_origins = ["http://localhost:3000", "http://localhost:8080"]
        
        if self.allowed_methods is None:
            self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        
        if self.allowed_headers is None:
            self.allowed_headers = ["*"]
        
        if self.allowed_file_types is None:
            self.allowed_file_types = [".jpg", ".jpeg", ".png", ".mp4", ".avi", ".mov"]
        
        # Load from environment variables
        self._load_from_env()
        
        # Validate configuration
        self.validate()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        self.host = os.getenv("API_HOST", self.host)
        self.port = int(os.getenv("API_PORT", self.port))
        self.debug = os.getenv("API_DEBUG", "false").lower() == "true"
        self.reload = os.getenv("API_RELOAD", "false").lower() == "true"
        
        # Security
        self.secret_key = os.getenv("API_SECRET_KEY", self.secret_key)
        self.algorithm = os.getenv("API_ALGORITHM", self.algorithm)
        self.access_token_expire_minutes = int(os.getenv("API_ACCESS_TOKEN_EXPIRE", self.access_token_expire_minutes))
        self.refresh_token_expire_days = int(os.getenv("API_REFRESH_TOKEN_EXPIRE", self.refresh_token_expire_days))
        
        # CORS
        if os.getenv("API_ALLOWED_ORIGINS"):
            self.allowed_origins = os.getenv("API_ALLOWED_ORIGINS").split(",")
        
        # Rate Limiting
        self.rate_limit_requests = int(os.getenv("API_RATE_LIMIT_REQUESTS", self.rate_limit_requests))
        self.rate_limit_window = int(os.getenv("API_RATE_LIMIT_WINDOW", self.rate_limit_window))
        
        # File Upload
        self.max_file_size = int(os.getenv("API_MAX_FILE_SIZE", self.max_file_size))
        if os.getenv("API_ALLOWED_FILE_TYPES"):
            self.allowed_file_types = os.getenv("API_ALLOWED_FILE_TYPES").split(",")
        
        # Caching
        self.cache_ttl = int(os.getenv("API_CACHE_TTL", self.cache_ttl))
        self.cache_max_size = int(os.getenv("API_CACHE_MAX_SIZE", self.cache_max_size))
        
        # Logging
        self.log_level = os.getenv("API_LOG_LEVEL", self.log_level)
        self.log_file = os.getenv("API_LOG_FILE", self.log_file)
    
    def validate(self):
        """Validate configuration settings."""
        if not self.secret_key or self.secret_key == "your-secret-key-change-in-production":
            raise ValueError("API_SECRET_KEY must be set in production")
        
        if self.port < 1 or self.port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        
        if self.rate_limit_requests < 1:
            raise ValueError("Rate limit requests must be positive")
        
        if self.max_file_size < 1:
            raise ValueError("Max file size must be positive")
        
        # Create upload directory if it doesn't exist
        Path(self.upload_dir).mkdir(exist_ok=True)
    
    def get_cors_config(self):
        """Get CORS configuration dictionary."""
        return {
            "allow_origins": self.allowed_origins,
            "allow_credentials": self.allow_credentials,
            "allow_methods": self.allowed_methods,
            "allow_headers": self.allowed_headers,
        }
    
    def get_security_config(self):
        """Get security configuration dictionary."""
        return {
            "secret_key": self.secret_key,
            "algorithm": self.algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
            "refresh_token_expire_days": self.refresh_token_expire_days,
        }


# Global configuration instance
config = APIConfig() 