"""
Main FastAPI Application for PlayaTewsIdentityMasker API
Provides RESTful endpoints for face swapping and identity masking operations.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import config
from .security import (
    SecurityManager, UserCreate, UserLogin, TokenResponse, UserResponse,
    get_current_user, require_admin, sanitize_input, validate_file_type,
    validate_file_size, generate_file_hash
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PlayaTewsIdentityMasker API",
    description="Secure RESTful API for real-time face swapping and identity masking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Initialize security manager
security_manager = SecurityManager()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    **config.get_cors_config()
)

# Mount static files
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Pydantic models for API requests/responses
class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    uptime: float

class ModelInfo(BaseModel):
    """DFM model information model."""
    name: str
    size: int
    path: str
    created_at: datetime
    is_valid: bool

class FaceSwapRequest(BaseModel):
    """Face swap request model."""
    source_image: str
    target_image: str
    model_name: str
    quality: str = "high"
    preserve_expression: bool = True

class FaceSwapResponse(BaseModel):
    """Face swap response model."""
    result_image: str
    processing_time: float
    model_used: str
    quality: str

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: str
    timestamp: datetime

# Global startup/shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("PlayaTewsIdentityMasker API starting up...")
    logger.info(f"Server running on {config.host}:{config.port}")
    logger.info(f"Debug mode: {config.debug}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("PlayaTewsIdentityMasker API shutting down...")

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=f"HTTP {exc.status_code}",
            detail=exc.detail,
            timestamp=datetime.utcnow()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred",
            timestamp=datetime.utcnow()
        ).dict()
    )

# Health check endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        uptime=0.0  # TODO: Implement uptime tracking
    )

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with component status."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "components": {
            "api": "healthy",
            "security": "healthy",
            "file_system": "healthy",
            "dfm_models": "healthy"
        }
    }
    
    # Check DFM models directory
    dfm_dir = Path("dfm_models")
    if dfm_dir.exists():
        dfm_files = list(dfm_dir.glob("*.dfm"))
        health_status["components"]["dfm_models"] = f"healthy ({len(dfm_files)} models)"
    else:
        health_status["components"]["dfm_models"] = "warning (no models directory)"
    
    return health_status

# Authentication endpoints
@app.post("/api/v1/auth/register", response_model=TokenResponse, tags=["Authentication"])
async def register_user(user_data: UserCreate):
    """Register a new user."""
    try:
        # Sanitize input
        username = sanitize_input(user_data.username)
        email = sanitize_input(user_data.email)
        
        # Create user
        user = security_manager.create_user(username, email, user_data.password)
        
        # Generate tokens
        tokens = security_manager.create_tokens(user)
        
        logger.info(f"User registered successfully: {username}")
        return TokenResponse(**tokens)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login_user(user_data: UserLogin):
    """Authenticate user and return tokens."""
    try:
        # Sanitize input
        username = sanitize_input(user_data.username)
        
        # Authenticate user
        user = security_manager.authenticate_user(username, user_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Generate tokens
        tokens = security_manager.create_tokens(user)
        
        logger.info(f"User logged in: {username}")
        return TokenResponse(**tokens)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@app.get("/api/v1/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user['id'],
        username=current_user['username'],
        email=current_user['email'],
        created_at=current_user['created_at'],
        is_active=current_user['is_active']
    )

# Model management endpoints
@app.get("/api/v1/models", response_model=List[ModelInfo], tags=["Models"])
async def list_models(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List available DFM models."""
    try:
        dfm_dir = Path("dfm_models")
        models = []
        
        if dfm_dir.exists():
            for dfm_file in dfm_dir.glob("*.dfm"):
                stat = dfm_file.stat()
                models.append(ModelInfo(
                    name=dfm_file.stem,
                    size=stat.st_size,
                    path=str(dfm_file),
                    created_at=datetime.fromtimestamp(stat.st_ctime),
                    is_valid=stat.st_size > 1024 * 1024  # > 1MB
                ))
        
        return models
    
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list models"
        )

@app.get("/api/v1/models/{model_name}", response_model=ModelInfo, tags=["Models"])
async def get_model_info(
    model_name: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get information about a specific model."""
    try:
        # Sanitize model name
        model_name = sanitize_input(model_name)
        
        dfm_file = Path("dfm_models") / f"{model_name}.dfm"
        
        if not dfm_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
        
        stat = dfm_file.stat()
        return ModelInfo(
            name=dfm_file.stem,
            size=stat.st_size,
            path=str(dfm_file),
            created_at=datetime.fromtimestamp(stat.st_ctime),
            is_valid=stat.st_size > 1024 * 1024
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model information"
        )

# Face swap endpoints
@app.post("/api/v1/faceswap", response_model=FaceSwapResponse, tags=["Face Swap"])
async def perform_face_swap(
    face_swap_request: FaceSwapRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Perform face swap operation."""
    try:
        # Validate model
        model_path = Path("dfm_models") / f"{face_swap_request.model_name}.dfm"
        if not model_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
        
        # TODO: Implement actual face swap logic
        # This is a placeholder implementation
        import time
        start_time = time.time()
        
        # Simulate processing time
        time.sleep(0.1)
        
        processing_time = time.time() - start_time
        
        # Generate result filename
        result_filename = f"faceswap_result_{int(time.time())}.jpg"
        result_path = Path("uploads") / result_filename
        
        # Create dummy result file
        result_path.parent.mkdir(exist_ok=True)
        result_path.write_bytes(b"dummy_result")
        
        logger.info(f"Face swap completed for user {current_user['username']}")
        
        return FaceSwapResponse(
            result_image=f"/uploads/{result_filename}",
            processing_time=processing_time,
            model_used=face_swap_request.model_name,
            quality=face_swap_request.quality
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face swap error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face swap operation failed"
        )

# File upload endpoints
@app.post("/api/v1/upload", tags=["File Upload"])
async def upload_file(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload a file for processing."""
    try:
        # Validate file type
        if not validate_file_type(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type"
            )
        
        # Validate file size
        file_size = 0
        file_content = b""
        
        while chunk := await file.read(8192):
            file_size += len(chunk)
            file_content += chunk
            
            if file_size > config.max_file_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File too large"
                )
        
        # Generate unique filename
        import time
        timestamp = int(time.time())
        safe_filename = sanitize_input(file.filename)
        unique_filename = f"{timestamp}_{safe_filename}"
        
        # Save file
        upload_path = Path("uploads") / unique_filename
        upload_path.parent.mkdir(exist_ok=True)
        upload_path.write_bytes(file_content)
        
        # Generate file hash
        file_hash = generate_file_hash(upload_path)
        
        logger.info(f"File uploaded by {current_user['username']}: {unique_filename}")
        
        return {
            "filename": unique_filename,
            "original_name": file.filename,
            "size": file_size,
            "hash": file_hash,
            "url": f"/uploads/{unique_filename}",
            "uploaded_at": datetime.utcnow()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )

# Utility endpoints
@app.get("/api/v1/utils/validate-file", tags=["Utilities"])
async def validate_file(
    filename: str = Query(..., description="Filename to validate"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Validate a filename for upload."""
    try:
        # Sanitize filename
        filename = sanitize_input(filename)
        
        is_valid = validate_file_type(filename)
        
        return {
            "filename": filename,
            "is_valid": is_valid,
            "allowed_types": config.allowed_file_types,
            "max_size": config.max_file_size
        }
    
    except Exception as e:
        logger.error(f"File validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File validation failed"
        )

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "PlayaTewsIdentityMasker API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=config.host,
        port=config.port,
        reload=config.reload,
        log_level=config.log_level.lower()
    ) 