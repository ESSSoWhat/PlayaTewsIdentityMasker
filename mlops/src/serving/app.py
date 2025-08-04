"""
Model Serving API for MLOps Best Practices

This module implements a comprehensive model serving API with:
- FastAPI framework for high-performance serving
- Health checks and monitoring
- A/B testing capabilities
- Request/response logging
- Rate limiting and caching
- Model versioning and rollback
"""

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

import joblib
import numpy as np
import pandas as pd
import structlog
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import load_config
from utils.logging import setup_logging
from utils.metrics import MetricsCollector

# Configure structured logging
logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
PREDICTION_COUNT = Counter('model_predictions_total', 'Total model predictions', ['model_version', 'model_type'])
PREDICTION_LATENCY = Histogram('model_prediction_duration_seconds', 'Model prediction latency')
MODEL_LOAD_TIME = Histogram('model_load_duration_seconds', 'Model loading time')
ACTIVE_MODELS = Gauge('active_models_total', 'Number of active models')


class PredictionRequest(BaseModel):
    """Request model for predictions"""
    features: List[float] = Field(..., description="Input features")
    model_version: Optional[str] = Field(None, description="Specific model version to use")
    experiment_id: Optional[str] = Field(None, description="A/B testing experiment ID")
    
    class Config:
        schema_extra = {
            "example": {
                "features": [1.0, 2.0, 3.0, 4.0],
                "model_version": "v1.0.0",
                "experiment_id": "ab_test_001"
            }
        }


class PredictionResponse(BaseModel):
    """Response model for predictions"""
    prediction: Union[float, int, str] = Field(..., description="Model prediction")
    probability: Optional[float] = Field(None, description="Prediction probability (for classification)")
    model_version: str = Field(..., description="Model version used")
    prediction_id: str = Field(..., description="Unique prediction ID")
    timestamp: str = Field(..., description="Prediction timestamp")
    experiment_id: Optional[str] = Field(None, description="A/B testing experiment ID")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Health check timestamp")
    model_versions: List[str] = Field(..., description="Available model versions")
    uptime: float = Field(..., description="Service uptime in seconds")


class ModelServer:
    """
    Comprehensive model server with MLOps best practices
    """
    
    def __init__(self, config_path: str = "configs/serving_config.yaml"):
        """Initialize the model server"""
        self.config = load_config(config_path)
        self.metrics = MetricsCollector()
        self.setup_logging()
        self.setup_redis()
        self.setup_app()
        self.load_models()
        
        # A/B testing configuration
        self.ab_tests = self.config.get('ab_tests', {})
        
        logger.info("Model server initialized", config_path=config_path)
    
    def setup_logging(self):
        """Setup structured logging with correlation IDs"""
        setup_logging()
        logger.info("Logging setup completed")
    
    def setup_redis(self):
        """Setup Redis for caching and session management"""
        try:
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning("Redis connection failed, running without cache", error=str(e))
            self.redis_client = None
    
    def setup_app(self):
        """Setup FastAPI application with middleware"""
        self.app = FastAPI(
            title="MLOps Model Serving API",
            description="Production-ready model serving with MLOps best practices",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.get('cors', {}).get('allow_origins', ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup rate limiting
        self.limiter = Limiter(key_func=get_remote_address)
        self.app.state.limiter = self.limiter
        self.app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        # Add middleware for request logging and metrics
        self.app.middleware("http")(self.log_requests)
        self.app.middleware("http")(self.add_correlation_id)
        
        # Setup routes
        self.setup_routes()
        
        logger.info("FastAPI application setup completed")
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/", response_model=Dict)
        async def root():
            """Root endpoint"""
            return {
                "message": "MLOps Model Serving API",
                "version": "1.0.0",
                "docs": "/docs",
                "health": "/health"
            }
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""
            return HealthResponse(
                status="healthy",
                timestamp=datetime.now().isoformat(),
                model_versions=list(self.models.keys()),
                uptime=time.time() - self.start_time
            )
        
        @self.app.post("/predict", response_model=PredictionResponse)
        @self.limiter.limit("100/minute")
        async def predict(request: PredictionRequest, req: Request):
            """Make predictions"""
            return await self.make_prediction(request, req)
        
        @self.app.get("/models")
        async def list_models():
            """List available models"""
            return {
                "models": [
                    {
                        "version": version,
                        "type": model_info["metadata"]["model_type"],
                        "task_type": model_info["metadata"]["task_type"],
                        "metrics": model_info["metadata"]["metrics"],
                        "created_at": model_info["metadata"]["training_timestamp"]
                    }
                    for version, model_info in self.models.items()
                ]
            }
        
        @self.app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint"""
            return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
        
        @self.app.post("/ab-test")
        async def create_ab_test(experiment_config: Dict):
            """Create A/B test configuration"""
            return await self.create_experiment(experiment_config)
        
        @self.app.get("/ab-test/{experiment_id}")
        async def get_ab_test_results(experiment_id: str):
            """Get A/B test results"""
            return await self.get_experiment_results(experiment_id)
    
    def log_requests(self, request: Request, call_next):
        """Middleware to log requests and collect metrics"""
        start_time = time.time()
        
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Process request
        response = call_next(request)
        
        # Calculate latency
        latency = time.time() - start_time
        
        # Log request
        logger.info(
            "HTTP request",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            latency=latency,
            correlation_id=correlation_id
        )
        
        # Update metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        REQUEST_LATENCY.observe(latency)
        
        return response
    
    def add_correlation_id(self, request: Request, call_next):
        """Middleware to add correlation ID to response headers"""
        response = call_next(request)
        if hasattr(request.state, 'correlation_id'):
            response.headers["X-Correlation-ID"] = request.state.correlation_id
        return response
    
    def load_models(self):
        """Load trained models from storage"""
        self.models = {}
        self.start_time = time.time()
        
        try:
            models_dir = self.config.get('models_dir', 'models')
            
            if not os.path.exists(models_dir):
                logger.warning("Models directory not found", models_dir=models_dir)
                return
            
            # Load all model files
            for model_file in os.listdir(models_dir):
                if model_file.endswith('.joblib'):
                    model_path = os.path.join(models_dir, model_file)
                    
                    with MODEL_LOAD_TIME.time():
                        model_data = joblib.load(model_path)
                    
                    # Extract model version from filename
                    model_version = model_file.replace('.joblib', '')
                    
                    self.models[model_version] = {
                        'model': model_data['model'],
                        'scaler': model_data['scaler'],
                        'metadata': model_data['metadata']
                    }
                    
                    logger.info("Model loaded", 
                               version=model_version,
                               type=model_data['metadata']['model_type'])
            
            ACTIVE_MODELS.set(len(self.models))
            logger.info("Model loading completed", model_count=len(self.models))
            
        except Exception as e:
            logger.error("Model loading failed", error=str(e))
            raise
    
    async def make_prediction(self, request: PredictionRequest, req: Request) -> PredictionResponse:
        """Make a prediction using the appropriate model"""
        prediction_start = time.time()
        
        try:
            # Generate prediction ID
            prediction_id = str(uuid.uuid4())
            
            # Check cache first
            cache_key = f"prediction:{hash(tuple(request.features))}"
            if self.redis_client:
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    logger.info("Cache hit", prediction_id=prediction_id)
                    return json.loads(cached_result)
            
            # Determine model version
            model_version = await self.select_model_version(request)
            
            # Get model
            if model_version not in self.models:
                raise HTTPException(status_code=404, detail=f"Model version {model_version} not found")
            
            model_info = self.models[model_version]
            model = model_info['model']
            scaler = model_info['scaler']
            metadata = model_info['metadata']
            
            # Preprocess features
            features = np.array(request.features).reshape(1, -1)
            features_scaled = scaler.transform(features)
            
            # Make prediction
            with PREDICTION_LATENCY.time():
                prediction = model.predict(features_scaled)[0]
                
                # Get probability for classification
                probability = None
                if metadata['task_type'] == 'classification' and hasattr(model, 'predict_proba'):
                    probability = float(model.predict_proba(features_scaled)[0].max())
            
            # Create response
            response = PredictionResponse(
                prediction=float(prediction) if isinstance(prediction, (np.integer, np.floating)) else prediction,
                probability=probability,
                model_version=model_version,
                prediction_id=prediction_id,
                timestamp=datetime.now().isoformat(),
                experiment_id=request.experiment_id
            )
            
            # Cache result
            if self.redis_client:
                self.redis_client.setex(
                    cache_key, 
                    self.config.get('cache', {}).get('ttl', 3600),
                    response.json()
                )
            
            # Update metrics
            PREDICTION_COUNT.labels(
                model_version=model_version,
                model_type=metadata['model_type']
            ).inc()
            
            # Log prediction
            logger.info(
                "Prediction made",
                prediction_id=prediction_id,
                model_version=model_version,
                features=request.features,
                prediction=response.prediction,
                probability=probability,
                latency=time.time() - prediction_start,
                correlation_id=getattr(req.state, 'correlation_id', None)
            )
            
            return response
            
        except Exception as e:
            logger.error("Prediction failed", 
                        error=str(e), 
                        prediction_id=prediction_id,
                        correlation_id=getattr(req.state, 'correlation_id', None))
            raise HTTPException(status_code=500, detail=str(e))
    
    async def select_model_version(self, request: PredictionRequest) -> str:
        """Select model version based on A/B testing or request"""
        
        # If specific version requested, use it
        if request.model_version:
            return request.model_version
        
        # Check A/B testing
        if request.experiment_id and request.experiment_id in self.ab_tests:
            experiment = self.ab_tests[request.experiment_id]
            
            # Simple random assignment based on traffic split
            import random
            if random.random() < experiment.get('traffic_split', 0.5):
                return experiment.get('variant_model', list(self.models.keys())[0])
            else:
                return experiment.get('control_model', list(self.models.keys())[0])
        
        # Default to latest model
        return list(self.models.keys())[-1] if self.models else None
    
    async def create_experiment(self, experiment_config: Dict) -> Dict:
        """Create A/B test experiment"""
        try:
            experiment_id = experiment_config.get('experiment_id')
            if not experiment_id:
                raise HTTPException(status_code=400, detail="experiment_id is required")
            
            # Validate model versions exist
            control_model = experiment_config.get('control_model')
            variant_model = experiment_config.get('variant_model')
            
            if control_model not in self.models:
                raise HTTPException(status_code=404, detail=f"Control model {control_model} not found")
            if variant_model not in self.models:
                raise HTTPException(status_code=404, detail=f"Variant model {variant_model} not found")
            
            # Store experiment configuration
            self.ab_tests[experiment_id] = experiment_config
            
            logger.info("A/B test created", experiment_id=experiment_id, config=experiment_config)
            
            return {
                "experiment_id": experiment_id,
                "status": "created",
                "config": experiment_config
            }
            
        except Exception as e:
            logger.error("Failed to create A/B test", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_experiment_results(self, experiment_id: str) -> Dict:
        """Get A/B test results"""
        try:
            if experiment_id not in self.ab_tests:
                raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found")
            
            # This would typically query a database for actual results
            # For now, return basic experiment info
            experiment = self.ab_tests[experiment_id]
            
            return {
                "experiment_id": experiment_id,
                "config": experiment,
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to get experiment results", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))


def create_app(config_path: str = "configs/serving_config.yaml") -> FastAPI:
    """Create and configure the FastAPI application"""
    server = ModelServer(config_path)
    return server.app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )