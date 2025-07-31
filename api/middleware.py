"""
Middleware Module for PlayaTewsIdentityMasker API
Provides rate limiting, security headers, logging, caching, and validation middleware.
"""

import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from collections import defaultdict, OrderedDict
import logging

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .config import config

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware based on IP address."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.requests: Dict[str, list] = defaultdict(list)
        self.max_requests = config.rate_limit_requests
        self.window_seconds = config.rate_limit_window
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean old requests
        self._clean_old_requests(client_ip, current_time)
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Too many requests. Limit: {self.max_requests} per {self.window_seconds} seconds",
                    "retry_after": self.window_seconds
                }
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(self.max_requests - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _clean_old_requests(self, client_ip: str, current_time: float):
        """Remove old requests outside the time window."""
        cutoff_time = current_time - self.window_seconds
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff_time
        ]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response."""
        start_time = time.time()
        
        # Log request
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
            "content_length": request.headers.get("Content-Length", 0)
        }
        
        logger.info(f"API Request: {json.dumps(log_data)}")
        
        # Process request
        try:
            response = await call_next(request)
            processing_time = time.time() - start_time
            
            # Log response
            response_log = {
                "timestamp": datetime.utcnow().isoformat(),
                "status_code": response.status_code,
                "processing_time": round(processing_time, 3),
                "content_length": response.headers.get("Content-Length", 0)
            }
            
            logger.info(f"API Response: {json.dumps(response_log)}")
            
            # Add processing time header
            response.headers["X-Processing-Time"] = str(processing_time)
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"API Error: {str(e)} (processing_time: {processing_time:.3f}s)")
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


class CacheMiddleware(BaseHTTPMiddleware):
    """Simple in-memory caching middleware."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.cache: OrderedDict = OrderedDict()
        self.max_size = config.cache_max_size
        self.ttl = config.cache_ttl
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with caching."""
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Generate cache key
        cache_key = self._generate_cache_key(request)
        
        # Check cache
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            logger.debug(f"Cache hit for key: {cache_key}")
            return cached_response
        
        # Process request
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200:
            self._cache_response(cache_key, response)
        
        return response
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key from request."""
        key_data = f"{request.method}:{request.url.path}:{request.url.query}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Response]:
        """Get cached response if valid."""
        if cache_key not in self.cache:
            return None
        
        cached_data = self.cache[cache_key]
        if time.time() - cached_data["timestamp"] > self.ttl:
            # Expired, remove from cache
            del self.cache[cache_key]
            return None
        
        # Return cached response
        response = Response(
            content=cached_data["content"],
            status_code=cached_data["status_code"],
            headers=cached_data["headers"]
        )
        response.headers["X-Cache"] = "HIT"
        return response
    
    def _cache_response(self, cache_key: str, response: Response):
        """Cache response."""
        # Check cache size
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            self.cache.popitem(last=False)
        
        # Cache response
        self.cache[cache_key] = {
            "content": response.body,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "timestamp": time.time()
        }
        
        # Add cache header
        response.headers["X-Cache"] = "MISS"


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle errors globally."""
        try:
            return await call_next(request)
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            
            # Return generic error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )


class ValidationMiddleware(BaseHTTPMiddleware):
    """Input validation middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate request input."""
        # Validate request size
        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > config.max_file_size:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "error": "Request too large",
                    "detail": f"Request size exceeds limit of {config.max_file_size} bytes"
                }
            )
        
        # Validate content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("Content-Type", "")
            if not self._is_valid_content_type(content_type):
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={
                        "error": "Unsupported media type",
                        "detail": f"Content-Type '{content_type}' is not supported"
                    }
                )
        
        return await call_next(request)
    
    def _is_valid_content_type(self, content_type: str) -> bool:
        """Check if content type is valid."""
        valid_types = [
            "application/json",
            "multipart/form-data",
            "application/x-www-form-urlencoded",
            "text/plain"
        ]
        
        return any(valid_type in content_type for valid_type in valid_types)


def setup_middleware(app: ASGIApp) -> ASGIApp:
    """Setup all middleware for the FastAPI application."""
    # Add middleware in order (last added is processed first)
    app = ValidationMiddleware(app)
    app = ErrorHandlingMiddleware(app)
    app = CacheMiddleware(app)
    app = RequestLoggingMiddleware(app)
    app = SecurityHeadersMiddleware(app)
    app = RateLimitMiddleware(app)
    
    return app 