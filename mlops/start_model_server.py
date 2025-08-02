#!/usr/bin/env python3
"""
Simple Model Server for PlayaTews Identity Masker MLOps
Starts a FastAPI server with basic model serving capabilities
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PlayaTews Identity Masker MLOps API",
    description="Model serving API for PlayaTews Identity Masker",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global metrics
request_count = 0
start_time = datetime.now()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PlayaTews Identity Masker MLOps API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": str(datetime.now() - start_time)
    }

@app.get("/metrics")
async def get_metrics():
    """Metrics endpoint for monitoring"""
    global request_count
    return {
        "total_requests": request_count,
        "uptime_seconds": (datetime.now() - start_time).total_seconds(),
        "requests_per_second": request_count / max((datetime.now() - start_time).total_seconds(), 1),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict")
async def predict(data: dict):
    """Model prediction endpoint"""
    global request_count
    request_count += 1
    
    try:
        # Simulate model prediction
        logger.info(f"Processing prediction request #{request_count}")
        
        # Add some processing time to simulate model inference
        time.sleep(0.1)
        
        # Return mock prediction result
        result = {
            "prediction_id": f"pred_{request_count}",
            "input_data": data,
            "prediction": {
                "confidence": 0.95,
                "class": "face_detected",
                "bbox": [100, 100, 200, 200]
            },
            "processing_time_ms": 100,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Prediction completed: {result['prediction_id']}")
        return result
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/models")
async def list_models():
    """List available models"""
    return {
        "models": [
            {
                "id": "face_detection_v1",
                "name": "Face Detection Model v1",
                "version": "1.0.0",
                "status": "active",
                "description": "Deep learning model for face detection"
            },
            {
                "id": "identity_masker_v1",
                "name": "Identity Masker Model v1",
                "version": "1.0.0",
                "status": "active",
                "description": "Model for masking personal identity in images"
            }
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/experiments")
async def list_experiments():
    """List MLflow experiments"""
    return {
        "experiments": [
            {
                "id": "exp_001",
                "name": "Face Detection Optimization",
                "status": "completed",
                "metrics": {
                    "accuracy": 0.95,
                    "precision": 0.92,
                    "recall": 0.89
                }
            },
            {
                "id": "exp_002",
                "name": "Identity Masking Performance",
                "status": "running",
                "metrics": {
                    "accuracy": 0.88,
                    "processing_time": 0.15
                }
            }
        ],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("Starting PlayaTews Identity Masker MLOps API Server...")
    logger.info("API will be available at: http://localhost:8000")
    logger.info("Health check: http://localhost:8000/health")
    logger.info("Metrics: http://localhost:8000/metrics")
    logger.info("API docs: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 