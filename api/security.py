"""
Security Module for PlayaTewsIdentityMasker API
Handles authentication, authorization, input validation, and security utilities.
"""

import re
import hashlib
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from pathlib import Path
import mimetypes
import logging

from pydantic import BaseModel, EmailStr, validator
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import config

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Pydantic models for request/response validation
class UserCreate(BaseModel):
    """User registration model."""
    username: str
    email: EmailStr
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLogin(BaseModel):
    """User login model."""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    """User response model."""
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool

class SecurityManager:
    """Manages authentication, authorization, and security operations."""
    
    def __init__(self):
        self.secret_key = config.secret_key
        self.algorithm = config.algorithm
        self.access_token_expire_minutes = config.access_token_expire_minutes
        self.refresh_token_expire_days = config.refresh_token_expire_days
        
        # In-memory user storage (replace with database in production)
        self.users: Dict[str, Dict[str, Any]] = {}
        self.user_id_counter = 1
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Create a new user."""
        if username in self.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        if any(user['email'] == email for user in self.users.values()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user_id = self.user_id_counter
        self.user_id_counter += 1
        
        user = {
            'id': user_id,
            'username': username,
            'email': email,
            'hashed_password': self.hash_password(password),
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        
        self.users[username] = user
        
        logger.info(f"User created: {username}")
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with username and password."""
        user = self.users.get(username)
        if not user:
            return None
        
        if not self.verify_password(password, user['hashed_password']):
            return None
        
        if not user['is_active']:
            return None
        
        return user
    
    def create_tokens(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Create access and refresh tokens for a user."""
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=self.refresh_token_expire_days)
        
        access_token_data = {
            "sub": str(user['id']),
            "username": user['username'],
            "exp": datetime.utcnow() + access_token_expires,
            "type": "access"
        }
        
        refresh_token_data = {
            "sub": str(user['id']),
            "username": user['username'],
            "exp": datetime.utcnow() + refresh_token_expires,
            "type": "refresh"
        }
        
        access_token = jwt.encode(access_token_data, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_token_data, self.secret_key, algorithm=self.algorithm)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Get the current authenticated user."""
        token = credentials.credentials
        payload = self.verify_token(token, "access")
        
        user_id = int(payload.get("sub"))
        username = payload.get("username")
        
        user = self.users.get(username)
        if user is None or user['id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )
        
        return user

# Global security manager instance
security_manager = SecurityManager()

# Security utility functions
def sanitize_input(input_string: str) -> str:
    """Sanitize user input to prevent XSS and injection attacks."""
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', input_string)
    
    # Limit length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
    
    return sanitized.strip()

def validate_file_type(filename: str, allowed_types: list = None) -> bool:
    """Validate file type based on extension and MIME type."""
    if allowed_types is None:
        allowed_types = config.allowed_file_types
    
    if not filename:
        return False
    
    # Check file extension
    file_ext = Path(filename).suffix.lower()
    if file_ext not in allowed_types:
        return False
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        # Basic MIME type validation
        if file_ext in ['.jpg', '.jpeg', '.png'] and not mime_type.startswith('image/'):
            return False
        if file_ext in ['.mp4', '.avi', '.mov'] and not mime_type.startswith('video/'):
            return False
    
    return True

def generate_file_hash(file_path: Union[str, Path]) -> str:
    """Generate SHA-256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    
    return hash_sha256.hexdigest()

def validate_file_size(file_size: int) -> bool:
    """Validate file size against configured limits."""
    return file_size <= config.max_file_size

# Dependency functions for FastAPI
def get_current_user(user: Dict[str, Any] = Depends(security_manager.get_current_user)) -> Dict[str, Any]:
    """Dependency to get current authenticated user."""
    return user

def require_admin(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency to require admin privileges."""
    # Add admin check logic here when implementing roles
    return user 