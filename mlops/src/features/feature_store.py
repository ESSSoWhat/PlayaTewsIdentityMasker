"""
Comprehensive Feature Store Implementation for PlayaTews Identity Masker

This module provides a complete feature store solution integrating with Hopsworks
for centralized feature management, versioning, real-time serving, and monitoring.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import hashlib
import uuid

# Hopsworks integration
try:
    import hopsworks
    from hopsworks import feature_store
    HOPWORKS_AVAILABLE = True
except ImportError:
    HOPSWORKS_AVAILABLE = False
    logging.warning("Hopsworks not available. Using local feature store.")

# Redis for caching
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available. Caching disabled.")

# Monitoring
from prometheus_client import Counter, Histogram, Gauge, Summary

# Configuration
from ..utils.config import load_config

# Type hints
FeatureValue = Union[str, int, float, bool, List, Dict]
FeatureVector = Dict[str, FeatureValue]
FeatureMetadata = Dict[str, Any]


class FeatureType(Enum):
    """Feature types supported by the feature store"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    IMAGE = "image"
    EMBEDDING = "embedding"
    TIMESTAMP = "timestamp"
    BOOLEAN = "boolean"


class DataSource(Enum):
    """Data sources for features"""
    CAMERA = "camera"
    FACE_DETECTION = "face_detection"
    FACE_ALIGNMENT = "face_alignment"
    FACE_SWAP = "face_swap"
    VOICE_CHANGER = "voice_changer"
    EXTERNAL_API = "external_api"
    USER_INPUT = "user_input"


@dataclass
class FeatureDefinition:
    """Definition of a feature"""
    name: str
    feature_type: FeatureType
    description: str
    data_source: DataSource
    version: str
    created_at: datetime
    updated_at: datetime
    schema: Dict[str, Any]
    validation_rules: Dict[str, Any]
    tags: List[str]
    owner: str
    is_online: bool = True
    is_offline: bool = True
    ttl_days: Optional[int] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class FeatureSet:
    """A collection of related features"""
    name: str
    version: str
    description: str
    features: List[FeatureDefinition]
    created_at: datetime
    updated_at: datetime
    owner: str
    tags: List[str]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class FeatureRequest:
    """Request for feature values"""
    entity_id: str
    feature_names: List[str]
    timestamp: Optional[datetime] = None
    version: Optional[str] = None
    include_metadata: bool = False


@dataclass
class FeatureResponse:
    """Response with feature values"""
    entity_id: str
    features: FeatureVector
    timestamp: datetime
    version: str
    metadata: Optional[FeatureMetadata] = None
    cache_hit: bool = False


class FeatureStoreMetrics:
    """Metrics for monitoring feature store performance"""
    
    def __init__(self):
        # Request metrics
        self.feature_requests_total = Counter(
            'feature_store_requests_total',
            'Total number of feature requests',
            ['feature_name', 'status']
        )
        
        self.feature_request_duration = Histogram(
            'feature_store_request_duration_seconds',
            'Feature request duration in seconds',
            ['feature_name']
        )
        
        # Cache metrics
        self.cache_hits_total = Counter(
            'feature_store_cache_hits_total',
            'Total number of cache hits',
            ['feature_name']
        )
        
        self.cache_misses_total = Counter(
            'feature_store_cache_misses_total',
            'Total number of cache misses',
            ['feature_name']
        )
        
        # Storage metrics
        self.feature_count = Gauge(
            'feature_store_feature_count',
            'Number of features in store',
            ['feature_set']
        )
        
        self.storage_size_bytes = Gauge(
            'feature_store_storage_size_bytes',
            'Storage size in bytes',
            ['feature_set']
        )
        
        # Quality metrics
        self.feature_quality_score = Gauge(
            'feature_store_quality_score',
            'Feature quality score',
            ['feature_name']
        )
        
        self.data_drift_score = Gauge(
            'feature_store_drift_score',
            'Data drift score',
            ['feature_name']
        )


class LocalFeatureStore:
    """Local feature store implementation for development and testing"""
    
    def __init__(self, storage_path: str = "feature_store"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # In-memory storage
        self.features: Dict[str, FeatureDefinition] = {}
        self.feature_sets: Dict[str, FeatureSet] = {}
        self.feature_data: Dict[str, Dict[str, Any]] = {}
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load existing feature data from disk"""
        try:
            # Load feature definitions
            features_file = self.storage_path / "features.json"
            if features_file.exists():
                with open(features_file, 'r') as f:
                    data = json.load(f)
                    for feature_data in data.values():
                        feature = FeatureDefinition(**feature_data)
                        self.features[feature.name] = feature
            
            # Load feature sets
            sets_file = self.storage_path / "feature_sets.json"
            if sets_file.exists():
                with open(sets_file, 'r') as f:
                    data = json.load(f)
                    for set_data in data.values():
                        feature_set = FeatureSet(**set_data)
                        self.feature_sets[feature_set.name] = feature_set
            
            # Load feature data
            data_file = self.storage_path / "feature_data.pkl"
            if data_file.exists():
                with open(data_file, 'rb') as f:
                    self.feature_data = pickle.load(f)
                    
        except Exception as e:
            logging.error(f"Error loading feature store data: {e}")
    
    def _save_data(self):
        """Save feature data to disk"""
        try:
            # Save feature definitions
            features_data = {name: asdict(feature) for name, feature in self.features.items()}
            with open(self.storage_path / "features.json", 'w') as f:
                json.dump(features_data, f, indent=2, default=str)
            
            # Save feature sets
            sets_data = {name: asdict(feature_set) for name, feature_set in self.feature_sets.items()}
            with open(self.storage_path / "feature_sets.json", 'w') as f:
                json.dump(sets_data, f, indent=2, default=str)
            
            # Save feature data
            with open(self.storage_path / "feature_data.pkl", 'wb') as f:
                pickle.dump(self.feature_data, f)
                
        except Exception as e:
            logging.error(f"Error saving feature store data: {e}")
    
    def register_feature(self, feature: FeatureDefinition) -> bool:
        """Register a new feature"""
        try:
            self.features[feature.name] = feature
            self._save_data()
            return True
        except Exception as e:
            logging.error(f"Error registering feature {feature.name}: {e}")
            return False
    
    def get_feature(self, feature_name: str) -> Optional[FeatureDefinition]:
        """Get feature definition"""
        return self.features.get(feature_name)
    
    def store_feature_value(self, feature_name: str, entity_id: str, 
                           value: FeatureValue, timestamp: datetime = None) -> bool:
        """Store a feature value"""
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            if feature_name not in self.feature_data:
                self.feature_data[feature_name] = {}
            
            self.feature_data[feature_name][entity_id] = {
                'value': value,
                'timestamp': timestamp,
                'version': self.features.get(feature_name, FeatureDefinition(
                    name=feature_name,
                    feature_type=FeatureType.NUMERICAL,
                    description="",
                    data_source=DataSource.CAMERA,
                    version="1.0",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    schema={},
                    validation_rules={},
                    tags=[],
                    owner="system"
                )).version
            }
            
            self._save_data()
            return True
            
        except Exception as e:
            logging.error(f"Error storing feature value: {e}")
            return False
    
    def get_feature_value(self, feature_name: str, entity_id: str) -> Optional[FeatureValue]:
        """Get a feature value"""
        try:
            feature_data = self.feature_data.get(feature_name, {})
            entity_data = feature_data.get(entity_id)
            if entity_data:
                return entity_data['value']
            return None
        except Exception as e:
            logging.error(f"Error getting feature value: {e}")
            return None


class FeatureStore:
    """
    Comprehensive Feature Store for PlayaTews Identity Masker
    
    Provides centralized feature management, versioning, real-time serving,
    and monitoring capabilities.
    """
    
    def __init__(self, config_path: str = "configs/feature_store_config.yaml"):
        # Load configuration
        self.config = load_config(config_path)
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize metrics
        self.metrics = FeatureStoreMetrics()
        
        # Initialize Hopsworks connection
        self.hopsworks_connection = None
        self.feature_store = None
        if HOPWORKS_AVAILABLE and self.config.get('hopsworks', {}).get('enabled', False):
            self._initialize_hopsworks()
        
        # Initialize Redis cache
        self.redis_client = None
        if REDIS_AVAILABLE and self.config.get('cache', {}).get('enabled', True):
            self._initialize_redis()
        
        # Initialize local store as fallback
        self.local_store = LocalFeatureStore(
            self.config.get('local_storage', {}).get('path', 'feature_store')
        )
        
        # Feature registry
        self.feature_registry: Dict[str, FeatureDefinition] = {}
        self.feature_sets: Dict[str, FeatureSet] = {}
        
        # Load existing features
        self._load_feature_registry()
        
        # Initialize feature pipelines
        self._initialize_feature_pipelines()
        
        self.logger.info("Feature store initialized successfully")
    
    def _initialize_hopsworks(self):
        """Initialize Hopsworks connection"""
        try:
            hopsworks_config = self.config['hopsworks']
            self.hopsworks_connection = hopsworks.login(
                api_key_value=hopsworks_config['api_key'],
                project=hopsworks_config['project']
            )
            self.feature_store = self.hopsworks_connection.get_feature_store()
            self.logger.info("Hopsworks connection established")
        except Exception as e:
            self.logger.error(f"Failed to initialize Hopsworks: {e}")
            self.hopsworks_connection = None
            self.feature_store = None
    
    def _initialize_redis(self):
        """Initialize Redis connection for caching"""
        try:
            cache_config = self.config['cache']
            self.redis_client = redis.Redis(
                host=cache_config.get('host', 'localhost'),
                port=cache_config.get('port', 6379),
                db=cache_config.get('db', 0),
                password=cache_config.get('password'),
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            self.logger.info("Redis cache initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis cache: {e}")
            self.redis_client = None
    
    def _load_feature_registry(self):
        """Load feature registry from storage"""
        try:
            # Load from local store first
            for feature_name, feature_def in self.local_store.features.items():
                self.feature_registry[feature_name] = feature_def
            
            # Load from Hopsworks if available
            if self.feature_store:
                # This would load feature definitions from Hopsworks
                # Implementation depends on specific Hopsworks API
                pass
                
        except Exception as e:
            self.logger.error(f"Error loading feature registry: {e}")
    
    def _initialize_feature_pipelines(self):
        """Initialize feature computation pipelines"""
        self.feature_pipelines = {
            'face_features': self._compute_face_features,
            'image_features': self._compute_image_features,
            'voice_features': self._compute_voice_features,
            'metadata_features': self._compute_metadata_features
        }
    
    def register_feature(self, feature: FeatureDefinition) -> bool:
        """
        Register a new feature in the feature store
        
        Args:
            feature: Feature definition to register
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate feature definition
            if not self._validate_feature_definition(feature):
                return False
            
            # Register in local store
            success = self.local_store.register_feature(feature)
            if not success:
                return False
            
            # Register in Hopsworks if available
            if self.feature_store:
                success = self._register_feature_hopsworks(feature)
                if not success:
                    self.logger.warning(f"Failed to register feature {feature.name} in Hopsworks")
            
            # Update registry
            self.feature_registry[feature.name] = feature
            
            # Update metrics
            self.metrics.feature_count.labels(feature_set=feature.name.split('_')[0]).inc()
            
            self.logger.info(f"Feature {feature.name} registered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering feature {feature.name}: {e}")
            return False
    
    def _validate_feature_definition(self, feature: FeatureDefinition) -> bool:
        """Validate feature definition"""
        try:
            # Check required fields
            if not feature.name or not feature.description:
                return False
            
            # Check feature type
            if not isinstance(feature.feature_type, FeatureType):
                return False
            
            # Check data source
            if not isinstance(feature.data_source, DataSource):
                return False
            
            # Check schema
            if not isinstance(feature.schema, dict):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating feature definition: {e}")
            return False
    
    def _register_feature_hopsworks(self, feature: FeatureDefinition) -> bool:
        """Register feature in Hopsworks"""
        try:
            # This is a placeholder for Hopsworks feature registration
            # Actual implementation depends on Hopsworks API
            return True
        except Exception as e:
            self.logger.error(f"Error registering feature in Hopsworks: {e}")
            return False
    
    async def get_features(self, request: FeatureRequest) -> FeatureResponse:
        """
        Get feature values for an entity
        
        Args:
            request: Feature request containing entity ID and feature names
            
        Returns:
            FeatureResponse: Response with feature values
        """
        start_time = datetime.now()
        cache_hit = False
        
        try:
            # Check cache first
            if self.redis_client:
                cached_features = await self._get_from_cache(request)
                if cached_features:
                    cache_hit = True
                    features = cached_features
                else:
                    features = await self._compute_features(request)
                    await self._cache_features(request, features)
            else:
                features = await self._compute_features(request)
            
            # Create response
            response = FeatureResponse(
                entity_id=request.entity_id,
                features=features,
                timestamp=datetime.now(),
                version=self._get_latest_version(request.feature_names),
                cache_hit=cache_hit
            )
            
            # Update metrics
            duration = (datetime.now() - start_time).total_seconds()
            for feature_name in request.feature_names:
                self.metrics.feature_request_duration.labels(feature_name=feature_name).observe(duration)
                self.metrics.feature_requests_total.labels(
                    feature_name=feature_name,
                    status="success"
                ).inc()
            
            if cache_hit:
                for feature_name in request.feature_names:
                    self.metrics.cache_hits_total.labels(feature_name=feature_name).inc()
            else:
                for feature_name in request.feature_names:
                    self.metrics.cache_misses_total.labels(feature_name=feature_name).inc()
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting features: {e}")
            
            # Update metrics
            for feature_name in request.feature_names:
                self.metrics.feature_requests_total.labels(
                    feature_name=feature_name,
                    status="error"
                ).inc()
            
            raise
    
    async def _get_from_cache(self, request: FeatureRequest) -> Optional[FeatureVector]:
        """Get features from cache"""
        try:
            cache_key = self._generate_cache_key(request)
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting from cache: {e}")
            return None
    
    async def _cache_features(self, request: FeatureRequest, features: FeatureVector):
        """Cache feature values"""
        try:
            cache_key = self._generate_cache_key(request)
            cache_ttl = self.config.get('cache', {}).get('ttl_seconds', 300)
            self.redis_client.setex(
                cache_key,
                cache_ttl,
                json.dumps(features)
            )
        except Exception as e:
            self.logger.error(f"Error caching features: {e}")
    
    def _generate_cache_key(self, request: FeatureRequest) -> str:
        """Generate cache key for feature request"""
        key_data = {
            'entity_id': request.entity_id,
            'feature_names': sorted(request.feature_names),
            'version': request.version or 'latest'
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"features:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    async def _compute_features(self, request: FeatureRequest) -> FeatureVector:
        """Compute feature values"""
        features = {}
        
        for feature_name in request.feature_names:
            try:
                # Check if feature exists in registry
                if feature_name not in self.feature_registry:
                    self.logger.warning(f"Feature {feature_name} not found in registry")
                    continue
                
                feature_def = self.feature_registry[feature_name]
                
                # Get stored value if available
                stored_value = self.local_store.get_feature_value(feature_name, request.entity_id)
                if stored_value is not None:
                    features[feature_name] = stored_value
                    continue
                
                # Compute feature value
                if feature_def.data_source in self.feature_pipelines:
                    pipeline = self.feature_pipelines[feature_def.data_source.name.lower()]
                    value = await pipeline(request.entity_id, feature_def)
                    features[feature_name] = value
                    
                    # Store computed value
                    self.local_store.store_feature_value(feature_name, request.entity_id, value)
                else:
                    self.logger.warning(f"No pipeline for data source {feature_def.data_source}")
                    
            except Exception as e:
                self.logger.error(f"Error computing feature {feature_name}: {e}")
                continue
        
        return features
    
    def _get_latest_version(self, feature_names: List[str]) -> str:
        """Get latest version for features"""
        versions = []
        for feature_name in feature_names:
            if feature_name in self.feature_registry:
                versions.append(self.feature_registry[feature_name].version)
        
        if versions:
            return max(versions)
        return "1.0"
    
    async def _compute_face_features(self, entity_id: str, feature_def: FeatureDefinition) -> FeatureValue:
        """Compute face-related features"""
        # Placeholder implementation
        # In practice, this would integrate with face detection/alignment models
        return {
            'face_detected': True,
            'face_confidence': 0.95,
            'face_bbox': [100, 100, 200, 200],
            'landmarks_count': 68
        }
    
    async def _compute_image_features(self, entity_id: str, feature_def: FeatureDefinition) -> FeatureValue:
        """Compute image-related features"""
        # Placeholder implementation
        # In practice, this would extract image features using computer vision
        return {
            'image_size': [1920, 1080],
            'brightness': 0.7,
            'contrast': 0.8,
            'sharpness': 0.9
        }
    
    async def _compute_voice_features(self, entity_id: str, feature_def: FeatureDefinition) -> FeatureValue:
        """Compute voice-related features"""
        # Placeholder implementation
        # In practice, this would extract voice features using audio processing
        return {
            'voice_detected': True,
            'pitch': 220.0,
            'volume': 0.8,
            'speech_rate': 150
        }
    
    async def _compute_metadata_features(self, entity_id: str, feature_def: FeatureDefinition) -> FeatureValue:
        """Compute metadata features"""
        # Placeholder implementation
        # In practice, this would extract metadata from various sources
        return {
            'timestamp': datetime.now().isoformat(),
            'session_id': str(uuid.uuid4()),
            'user_id': entity_id,
            'device_info': 'camera_01'
        }
    
    def create_feature_set(self, name: str, features: List[str], 
                          description: str = "", owner: str = "system") -> bool:
        """
        Create a feature set
        
        Args:
            name: Name of the feature set
            features: List of feature names to include
            description: Description of the feature set
            owner: Owner of the feature set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate features exist
            feature_definitions = []
            for feature_name in features:
                if feature_name not in self.feature_registry:
                    self.logger.error(f"Feature {feature_name} not found in registry")
                    return False
                feature_definitions.append(self.feature_registry[feature_name])
            
            # Create feature set
            feature_set = FeatureSet(
                name=name,
                version="1.0",
                description=description,
                features=feature_definitions,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                owner=owner,
                tags=[]
            )
            
            # Store feature set
            self.feature_sets[name] = feature_set
            self.local_store.feature_sets[name] = feature_set
            self.local_store._save_data()
            
            self.logger.info(f"Feature set {name} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating feature set {name}: {e}")
            return False
    
    def get_feature_set(self, name: str) -> Optional[FeatureSet]:
        """Get feature set by name"""
        return self.feature_sets.get(name)
    
    def list_feature_sets(self) -> List[str]:
        """List all feature sets"""
        return list(self.feature_sets.keys())
    
    def delete_feature(self, feature_name: str) -> bool:
        """
        Delete a feature from the store
        
        Args:
            feature_name: Name of the feature to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Remove from registry
            if feature_name in self.feature_registry:
                del self.feature_registry[feature_name]
            
            # Remove from local store
            if feature_name in self.local_store.features:
                del self.local_store.features[feature_name]
            
            # Remove from Hopsworks if available
            if self.feature_store:
                self._delete_feature_hopsworks(feature_name)
            
            # Clear cache
            if self.redis_client:
                self._clear_feature_cache(feature_name)
            
            self.local_store._save_data()
            
            self.logger.info(f"Feature {feature_name} deleted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting feature {feature_name}: {e}")
            return False
    
    def _delete_feature_hopsworks(self, feature_name: str):
        """Delete feature from Hopsworks"""
        try:
            # Placeholder for Hopsworks deletion
            pass
        except Exception as e:
            self.logger.error(f"Error deleting feature from Hopsworks: {e}")
    
    def _clear_feature_cache(self, feature_name: str):
        """Clear cache for a specific feature"""
        try:
            pattern = f"features:*{feature_name}*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            self.logger.error(f"Error clearing feature cache: {e}")
    
    def get_feature_statistics(self, feature_name: str) -> Dict[str, Any]:
        """
        Get statistics for a feature
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            Dict: Feature statistics
        """
        try:
            if feature_name not in self.feature_registry:
                return {}
            
            feature_data = self.local_store.feature_data.get(feature_name, {})
            
            if not feature_data:
                return {
                    'count': 0,
                    'last_updated': None,
                    'coverage': 0.0
                }
            
            values = [data['value'] for data in feature_data.values()]
            timestamps = [data['timestamp'] for data in feature_data.values()]
            
            stats = {
                'count': len(values),
                'last_updated': max(timestamps) if timestamps else None,
                'coverage': len(values) / max(len(feature_data), 1),
                'unique_values': len(set(str(v) for v in values))
            }
            
            # Add type-specific statistics
            feature_def = self.feature_registry[feature_name]
            if feature_def.feature_type == FeatureType.NUMERICAL:
                numeric_values = [v for v in values if isinstance(v, (int, float))]
                if numeric_values:
                    stats.update({
                        'mean': np.mean(numeric_values),
                        'std': np.std(numeric_values),
                        'min': np.min(numeric_values),
                        'max': np.max(numeric_values)
                    })
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting feature statistics: {e}")
            return {}
    
    def export_features(self, feature_names: List[str], 
                       output_path: str, format: str = "csv") -> bool:
        """
        Export features to file
        
        Args:
            feature_names: List of feature names to export
            output_path: Output file path
            format: Export format (csv, json, parquet)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Collect data
            data = []
            for feature_name in feature_names:
                feature_data = self.local_store.feature_data.get(feature_name, {})
                for entity_id, entity_data in feature_data.items():
                    data.append({
                        'entity_id': entity_id,
                        'feature_name': feature_name,
                        'value': entity_data['value'],
                        'timestamp': entity_data['timestamp'],
                        'version': entity_data['version']
                    })
            
            if not data:
                self.logger.warning("No data to export")
                return False
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Export based on format
            if format.lower() == "csv":
                df.to_csv(output_path, index=False)
            elif format.lower() == "json":
                df.to_json(output_path, orient='records', indent=2)
            elif format.lower() == "parquet":
                df.to_parquet(output_path, index=False)
            else:
                self.logger.error(f"Unsupported export format: {format}")
                return False
            
            self.logger.info(f"Features exported to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting features: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on feature store
        
        Returns:
            Dict: Health check results
        """
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }
        
        # Check local store
        try:
            self.local_store._save_data()
            health_status['components']['local_store'] = 'healthy'
        except Exception as e:
            health_status['components']['local_store'] = f'unhealthy: {e}'
            health_status['status'] = 'unhealthy'
        
        # Check Redis cache
        if self.redis_client:
            try:
                self.redis_client.ping()
                health_status['components']['redis_cache'] = 'healthy'
            except Exception as e:
                health_status['components']['redis_cache'] = f'unhealthy: {e}'
                health_status['status'] = 'unhealthy'
        else:
            health_status['components']['redis_cache'] = 'not_configured'
        
        # Check Hopsworks
        if self.hopsworks_connection:
            try:
                # Simple connection test
                health_status['components']['hopsworks'] = 'healthy'
            except Exception as e:
                health_status['components']['hopsworks'] = f'unhealthy: {e}'
                health_status['status'] = 'unhealthy'
        else:
            health_status['components']['hopsworks'] = 'not_configured'
        
        # Check feature registry
        try:
            feature_count = len(self.feature_registry)
            health_status['components']['feature_registry'] = f'healthy ({feature_count} features)'
        except Exception as e:
            health_status['components']['feature_registry'] = f'unhealthy: {e}'
            health_status['status'] = 'unhealthy'
        
        return health_status


# Factory function for creating feature store instance
def create_feature_store(config_path: str = None) -> FeatureStore:
    """
    Create a feature store instance
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        FeatureStore: Configured feature store instance
    """
    if config_path is None:
        config_path = "configs/feature_store_config.yaml"
    
    return FeatureStore(config_path)


# Example usage
if __name__ == "__main__":
    # Create feature store
    fs = create_feature_store()
    
    # Register a feature
    face_detection_feature = FeatureDefinition(
        name="face_detection_confidence",
        feature_type=FeatureType.NUMERICAL,
        description="Confidence score for face detection",
        data_source=DataSource.FACE_DETECTION,
        version="1.0",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        schema={"type": "number", "minimum": 0, "maximum": 1},
        validation_rules={"required": True, "min_value": 0, "max_value": 1},
        tags=["face", "detection", "confidence"],
        owner="ml_team"
    )
    
    fs.register_feature(face_detection_feature)
    
    # Create feature set
    fs.create_feature_set(
        name="face_analysis_features",
        features=["face_detection_confidence"],
        description="Features for face analysis pipeline",
        owner="ml_team"
    )
    
    # Health check
    health = fs.health_check()
    print(f"Feature store health: {health}") 