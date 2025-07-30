"""
Security Module for PlayaTewsIdentityMasker API
Handles authentication, authorization, and security utilities.
"""

import jwt
import bcrypt
import secrets
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from functools import wraps
import logging
from pathlib import Path
import json

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator

from .config import get_config

logger = logging.getLogger(__name__)

# Security schemas
class UserCreate(BaseModel):
    """User creation schema with validation."""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', v):
            raise ValueError('Username must be 3-20 characters, alphanumeric and underscore only')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    """User login schema."""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class SecurityManager:
    """Security manager for authentication and authorization."""
    
    def __init__(self):
        self.config = get_config()
        self.users_file = Path("api/data/users.json")
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        self.users = self._load_users()
        self.blacklisted_tokens = set()
    
    def _load_users(self) -> Dict[str, Dict[str, Any]]:
        """Load users from JSON file."""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading users: {e}")
        return {}
    
    def _save_users(self):
        """Save users to JSON file."""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
                logger.error(f"Error saving users: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """Create a new user."""
        if user_data.username in [u['username'] for u in self.users.values()]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        user_id = secrets.token_urlsafe(16)
        hashed_password = self.hash_password(user_data.password)
        
        user = {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "password_hash": hashed_password,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": None
        }
        
        self.users[user_id] = user
        self._save_users()
        
        return {k: v for k, v in user.items() if k != 'password_hash'}
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user credentials."""
        for user in self.users.values():
            if user['username'] == username and self.verify_password(password, user['password_hash']):
                return user
        return None
    
    def create_tokens(self, user_id: str) -> TokenResponse:
        """Create access and refresh tokens."""
        now = datetime.now(timezone.utc)
        
        # Access token
        access_token_expires = now + timedelta(minutes=self.config.access_token_expire_minutes)
        access_token_data = {
            "sub": user_id,
            "type": "access",
            "exp": access_token_expires,
            "iat": now
        }
        access_token = jwt.encode(access_token_data, self.config.secret_key, algorithm=self.config.algorithm)
        
        # Refresh token
        refresh_token_expires = now + timedelta(days=self.config.refresh_token_expire_days)
        refresh_token_data = {
            "sub": user_id,
            "type": "refresh",
            "exp": refresh_token_expires,
            "iat": now
        }
        refresh_token = jwt.encode(refresh_token_data, self.config.secret_key, algorithm=self.config.algorithm)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.config.access_token_expire_minutes * 60
        )
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])
            
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            if token in self.blacklisted_tokens:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
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

# Global security manager instance
security_manager = SecurityManager()

# Security dependencies
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user."""
    payload = security_manager.verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    if user_id not in security_manager.users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    user = security_manager.users[user_id]
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    return user

# Input validation utilities
def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS."""
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text.strip()

def validate_file_type(filename: str, allowed_types: list) -> bool:
    """Validate file type based on extension."""
    from pathlib import Path
    file_ext = Path(filename).suffix.lower()
    return file_ext in allowed_types 