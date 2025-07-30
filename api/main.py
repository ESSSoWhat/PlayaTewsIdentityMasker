"""
PlayaTewsIdentityMasker API - Main Application
RESTful API for face swapping and identity masking operations.
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import logging
import time
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from .config import get_config
from .security import (
    SecurityManager, UserCreate, UserLogin, TokenResponse,
    get_current_user, sanitize_input, validate_file_type
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PlayaTewsIdentityMasker API",
    description="Secure RESTful API for real-time face swapping and identity masking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Get configuration
config = get_config()

# Security manager
security_manager = SecurityManager()

# Request/Response Models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str

class FaceSwapResponse(BaseModel):
    """Face swap response model."""
    result_image: str  # Base64 encoded result
    processing_time: float
    model_used: str
    confidence_score: float

class ModelInfo(BaseModel):
    """Model information response."""
    name: str
    size_mb: float
    quality: str
    description: str
    is_available: bool

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=config.allowed_methods,
    allow_headers=config.allowed_headers,
)

# Utility functions
def log_request(request_type: str, user_id: Optional[str] = None, details: Optional[Dict] = None):
    """Log API request."""
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "request_type": request_type,
        "user_id": user_id,
        "details": details or {}
    }
    logger.info(f"API Request: {json.dumps(log_entry)}")

def validate_image_file(file: UploadFile) -> bool:
    """Validate uploaded image file."""
    if not file.filename:
        return False
    
    allowed_types = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    return validate_file_type(file.filename, allowed_types)

# Health and Status Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health information."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
    )

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "features": {
            "face_swapping": "available",
            "model_management": "available",
            "user_management": "available"
        }
    }

# Authentication Endpoints
@app.post("/api/v1/auth/register", response_model=Dict[str, Any])
async def register_user(user_data: UserCreate):
    """Register a new user."""
    try:
        user = security_manager.create_user(user_data)
        log_request("user_register", user["id"])
        return {
            "message": "User registered successfully",
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Login user and return tokens."""
    try:
        user = security_manager.authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        tokens = security_manager.create_tokens(user["id"])
        log_request("user_login", user["id"])
        
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/api/v1/auth/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information."""
    return {
        "user": {k: v for k, v in current_user.items() if k != 'password_hash'}
    }

# Model Management Endpoints
@app.get("/api/v1/models", response_model=List[ModelInfo])
async def list_models():
    """List available face swap models."""
    try:
        models_dir = Path("dfm_models")
        models = []
        
        if models_dir.exists():
            for model_file in models_dir.glob("*.dfm"):
                size_mb = model_file.stat().st_size / (1024 * 1024)
                models.append(ModelInfo(
                    name=model_file.stem,
                    size_mb=round(size_mb, 2),
                    quality="high" if size_mb > 100 else "medium",
                    description=f"Face swap model: {model_file.stem}",
                    is_available=True
                ))
        
        return models
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail="Failed to list models")

@app.get("/api/v1/models/{model_name}")
async def get_model_info(model_name: str):
    """Get specific model information."""
    try:
        model_path = Path(f"dfm_models/{model_name}.dfm")
        if not model_path.exists():
            raise HTTPException(status_code=404, detail="Model not found")
        
        size_mb = model_path.stat().st_size / (1024 * 1024)
        return ModelInfo(
            name=model_name,
            size_mb=round(size_mb, 2),
            quality="high" if size_mb > 100 else "medium",
            description=f"Face swap model: {model_name}",
            is_available=True
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model info")

# Face Swap Endpoints
@app.post("/api/v1/faceswap", response_model=FaceSwapResponse)
async def face_swap(
    background_tasks: BackgroundTasks,
    source_image: UploadFile = File(...),
    target_image: UploadFile = File(...),
    model_name: Optional[str] = Form(None),
    quality: Optional[str] = Form("high"),
    preserve_expression: Optional[bool] = Form(True),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Perform face swap operation."""
    try:
        # Validate files
        if not validate_image_file(source_image) or not validate_image_file(target_image):
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Validate quality parameter
        if quality not in ["low", "medium", "high"]:
            raise HTTPException(status_code=400, detail="Invalid quality parameter")
        
        # Log request
        log_request("face_swap", current_user["id"], {
            "model_name": model_name,
            "quality": quality,
            "preserve_expression": preserve_expression
        })
        
        # TODO: Implement actual face swap logic here
        # This is a placeholder response
        processing_time = 2.5  # Simulated processing time
        
        return FaceSwapResponse(
            result_image="base64_encoded_result_image_placeholder",
            processing_time=processing_time,
            model_used=model_name or "default",
            confidence_score=0.95
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face swap error: {e}")
        raise HTTPException(status_code=500, detail="Face swap operation failed")

# File Upload Endpoints
@app.post("/api/v1/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload a file for processing."""
    try:
        # Validate file type
        if not validate_file_type(file.filename, config.allowed_file_types):
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # Create upload directory
        upload_dir = Path(config.upload_directory)
        upload_dir.mkdir(exist_ok=True)
        
        # Save file
        file_path = upload_dir / f"{current_user['id']}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        log_request("file_upload", current_user["id"], {
            "filename": file.filename,
            "file_size": len(content)
        })
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "file_path": str(file_path),
            "file_size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "detail": "The requested resource was not found",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An internal server error occurred",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("PlayaTewsIdentityMasker API starting up...")
    
    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        raise RuntimeError("Invalid configuration")
    
    # Create necessary directories
    Path(config.upload_directory).mkdir(exist_ok=True)
    
    logger.info("PlayaTewsIdentityMasker API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("PlayaTewsIdentityMasker API shutting down...")

# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level=config.log_level.lower()
    ) 