"""
API Middleware for PlayaTewsIdentityMasker
Handles rate limiting, caching, security headers, and request monitoring.
"""

import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from collections import defaultdict
import logging

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .config import get_config

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.config = get_config()
        self.rate_limit_store = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        client_ip = request.client.host
        now = datetime.now()
        window_start = now - timedelta(seconds=self.config.rate_limit_window)
        
        # Clean old requests outside the window
        self.rate_limit_store[client_ip] = [
            req_time for req_time in self.rate_limit_store[client_ip]
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.rate_limit_store[client_ip]) >= self.config.rate_limit_requests:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Too many requests. Limit: {self.config.rate_limit_requests} per {self.config.rate_limit_window} seconds",
                    "retry_after": self.config.rate_limit_window
                }
            )
        
        # Add current request
        self.rate_limit_store[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.config.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            self.config.rate_limit_requests - len(self.rate_limit_store[client_ip])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int((now + timedelta(seconds=self.config.rate_limit_window)).timestamp())
        )
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers middleware."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        # HSTS (only for HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request details."""
        start_time = time.time()
        
        # Log request start
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent", ""),
            "content_length": request.headers.get("content-length", "0")
        }
        
        logger.info(f"Request started: {json.dumps(log_entry)}")
        
        # Process request
        try:
            response = await call_next(request)
            processing_time = time.time() - start_time
            
            # Log successful response
            log_entry.update({
                "status_code": response.status_code,
                "processing_time": round(processing_time, 3),
                "response_size": response.headers.get("content-length", "0")
            })
            
            logger.info(f"Request completed: {json.dumps(log_entry)}")
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Log error
            log_entry.update({
                "error": str(e),
                "processing_time": round(processing_time, 3)
            })
            
            logger.error(f"Request failed: {json.dumps(log_entry)}")
            raise

class CacheMiddleware(BaseHTTPMiddleware):
    """Simple in-memory caching middleware."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.config = get_config()
        self.cache = {}
        self.cache_timestamps = {}
    
    def _get_cache_key(self, request: Request) -> str:
        """Generate cache key for request."""
        key_data = f"{request.method}:{request.url.path}:{request.url.query}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_cacheable(self, request: Request, response: Response) -> bool:
        """Check if response is cacheable."""
        # Only cache GET requests
        if request.method != "GET":
            return False
        
        # Only cache successful responses
        if response.status_code != 200:
            return False
        
        # Check if response has cache control headers
        cache_control = response.headers.get("cache-control", "")
        if "no-cache" in cache_control or "no-store" in cache_control:
            return False
        
        return True
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with caching."""
        cache_key = self._get_cache_key(request)
        now = time.time()
        
        # Check cache
        if cache_key in self.cache:
            cache_age = now - self.cache_timestamps[cache_key]
            if cache_age < self.config.cache_ttl:
                # Return cached response
                cached_response = self.cache[cache_key]
                cached_response.headers["X-Cache"] = "HIT"
                cached_response.headers["X-Cache-Age"] = str(int(cache_age))
                return cached_response
        
        # Process request
        response = await call_next(request)
        
        # Cache response if appropriate
        if self._is_cacheable(request, response):
            # Check cache size limit
            if len(self.cache) >= self.config.cache_max_size:
                # Remove oldest entry
                oldest_key = min(self.cache_timestamps.keys(), key=lambda k: self.cache_timestamps[k])
                del self.cache[oldest_key]
                del self.cache_timestamps[oldest_key]
            
            # Store in cache
            self.cache[cache_key] = response
            self.cache_timestamps[cache_key] = now
            response.headers["X-Cache"] = "MISS"
        else:
            response.headers["X-Cache"] = "SKIP"
        
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle errors globally."""
        try:
            return await call_next(request)
        except HTTPException:
            # Re-raise HTTP exceptions as they are already handled
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error: {e}", exc_info=True)
            
            # Return generic error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred",
                    "timestamp": datetime.now().isoformat()
                }
            )

class ValidationMiddleware(BaseHTTPMiddleware):
    """Input validation middleware."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate request input."""
        # Validate content length
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > get_config().max_file_size:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "error": "File too large",
                            "detail": f"File size exceeds maximum allowed size of {get_config().max_file_size} bytes"
                        }
                    )
            except ValueError:
                pass
        
        # Validate content type for POST/PUT requests
        if request.method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if "multipart/form-data" not in content_type and "application/json" not in content_type:
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={
                        "error": "Unsupported media type",
                        "detail": "Only multipart/form-data and application/json are supported"
                    }
                )
        
        return await call_next(request)

# Utility functions for middleware
def setup_middleware(app):
    """Setup all middleware for the application."""
    # Add middleware in order (last added is processed first)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(ValidationMiddleware)
    app.add_middleware(CacheMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware)
    
    logger.info("All middleware configured successfully")

def cleanup_cache():
    """Clean up expired cache entries."""
    config = get_config()
    now = time.time()
    
    # This would be called periodically in a real application
    # For now, it's a utility function
    expired_keys = [
        key for key, timestamp in cache_timestamps.items()
        if now - timestamp > config.cache_ttl
    ]
    
    for key in expired_keys:
        del cache[key]
        del cache_timestamps[key]
    
    if expired_keys:
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries") 