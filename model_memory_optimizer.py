#!/usr/bin/env python3
"""
Model Memory Optimizer for PlayaTewsIdentityMasker
Optimized memory management for large model files and efficient model loading
"""

import os
import gc
import logging
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import weakref
import psutil
import numpy as np

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Model type enumeration"""
    DFM = "dfm"
    ONNX = "onnx"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    UNKNOWN = "unknown"

class ModelPriority(Enum):
    """Model loading priority"""
    CRITICAL = "critical"  # Always loaded
    HIGH = "high"          # Loaded when needed
    MEDIUM = "medium"      # Loaded on demand
    LOW = "low"            # Loaded only when explicitly requested

@dataclass
class ModelInfo:
    """Model information and metadata"""
    name: str
    path: Path
    model_type: ModelType
    size_bytes: int
    priority: ModelPriority
    load_time: float = 0.0
    last_used: float = 0.0
    memory_usage: int = 0
    is_loaded: bool = False
    error_count: int = 0
    compression_ratio: float = 1.0

class ModelCache:
    """Intelligent model caching with memory optimization"""
    
    def __init__(self, max_memory_mb: int = 4096, max_models: int = 10):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.max_models = max_models
        self.models: Dict[str, ModelInfo] = {}
        self.loaded_models: Dict[str, Any] = {}
        self.model_refs: Dict[str, weakref.ref] = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'loads': 0,
            'errors': 0
        }
        self.lock = threading.RLock()
        
        logger.info(f"🧠 Model cache initialized: {max_memory_mb}MB, {max_models} models max")
    
    def add_model(self, model_path: Union[str, Path], priority: ModelPriority = ModelPriority.MEDIUM) -> bool:
        """Add a model to the cache registry"""
        try:
            path = Path(model_path)
            if not path.exists():
                logger.error(f"❌ Model file not found: {path}")
                return False
            
            model_name = path.stem
            size_bytes = path.stat().st_size
            model_type = self._detect_model_type(path)
            
            model_info = ModelInfo(
                name=model_name,
                path=path,
                model_type=model_type,
                size_bytes=size_bytes,
                priority=priority
            )
            
            with self.lock:
                self.models[model_name] = model_info
                logger.info(f"📁 Added model to cache: {model_name} ({size_bytes / 1024 / 1024:.1f}MB)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding model {model_path}: {e}")
            return False
    
    def _detect_model_type(self, path: Path) -> ModelType:
        """Detect model type from file extension"""
        suffix = path.suffix.lower()
        
        if suffix == '.dfm':
            return ModelType.DFM
        elif suffix == '.onnx':
            return ModelType.ONNX
        elif suffix in ['.pth', '.pt']:
            return ModelType.PYTORCH
        elif suffix in ['.pb', '.h5', '.hdf5']:
            return ModelType.TENSORFLOW
        else:
            return ModelType.UNKNOWN
    
    def load_model(self, model_name: str, force_reload: bool = False) -> Optional[Any]:
        """Load a model into memory"""
        with self.lock:
            if model_name not in self.models:
                logger.error(f"❌ Model not found in cache: {model_name}")
                self.cache_stats['misses'] += 1
                return None
            
            model_info = self.models[model_name]
            
            # Check if already loaded
            if model_name in self.loaded_models and not force_reload:
                logger.debug(f"🎯 Model cache hit: {model_name}")
                self.cache_stats['hits'] += 1
                model_info.last_used = time.time()
                return self.loaded_models[model_name]
            
            # Check memory constraints
            if not self._can_load_model(model_info):
                self._evict_models(model_info.size_bytes)
            
            # Load the model
            start_time = time.time()
            try:
                model = self._load_model_file(model_info)
                if model is not None:
                    self.loaded_models[model_name] = model
                    model_info.is_loaded = True
                    model_info.load_time = time.time() - start_time
                    model_info.last_used = time.time()
                    model_info.memory_usage = self._estimate_model_memory(model)
                    
                    # Create weak reference for automatic cleanup
                    self.model_refs[model_name] = weakref.ref(model, 
                        lambda ref, name=model_name: self._on_model_garbage_collected(name))
                    
                    self.cache_stats['loads'] += 1
                    logger.info(f"📥 Loaded model: {model_name} ({model_info.memory_usage / 1024 / 1024:.1f}MB)")
                    return model
                else:
                    model_info.error_count += 1
                    self.cache_stats['errors'] += 1
                    logger.error(f"❌ Failed to load model: {model_name}")
                    return None
                    
            except Exception as e:
                model_info.error_count += 1
                self.cache_stats['errors'] += 1
                logger.error(f"❌ Error loading model {model_name}: {e}")
                return None
    
    def _load_model_file(self, model_info: ModelInfo) -> Optional[Any]:
        """Load model file based on type"""
        try:
            if model_info.model_type == ModelType.DFM:
                return self._load_dfm_model(model_info.path)
            elif model_info.model_type == ModelType.ONNX:
                return self._load_onnx_model(model_info.path)
            elif model_info.model_type == ModelType.PYTORCH:
                return self._load_pytorch_model(model_info.path)
            elif model_info.model_type == ModelType.TENSORFLOW:
                return self._load_tensorflow_model(model_info.path)
            else:
                logger.warning(f"⚠️ Unknown model type: {model_info.model_type}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error loading {model_info.model_type.value} model: {e}")
            return None
    
    def _load_dfm_model(self, path: Path) -> Optional[Any]:
        """Load DFM model file"""
        try:
            # DFM models are typically loaded with specific libraries
            # This is a placeholder for actual DFM loading logic
            logger.debug(f"Loading DFM model: {path}")
            return {"type": "dfm", "path": str(path)}
        except Exception as e:
            logger.error(f"❌ Error loading DFM model: {e}")
            return None
    
    def _load_onnx_model(self, path: Path) -> Optional[Any]:
        """Load ONNX model file"""
        try:
            import onnxruntime as ort
            logger.debug(f"Loading ONNX model: {path}")
            session = ort.InferenceSession(str(path))
            return session
        except ImportError:
            logger.error("❌ ONNX Runtime not available")
            return None
        except Exception as e:
            logger.error(f"❌ Error loading ONNX model: {e}")
            return None
    
    def _load_pytorch_model(self, path: Path) -> Optional[Any]:
        """Load PyTorch model file"""
        try:
            import torch
            logger.debug(f"Loading PyTorch model: {path}")
            model = torch.load(str(path), map_location='cpu')
            return model
        except ImportError:
            logger.error("❌ PyTorch not available")
            return None
        except Exception as e:
            logger.error(f"❌ Error loading PyTorch model: {e}")
            return None
    
    def _load_tensorflow_model(self, path: Path) -> Optional[Any]:
        """Load TensorFlow model file"""
        try:
            import tensorflow as tf
            logger.debug(f"Loading TensorFlow model: {path}")
            model = tf.keras.models.load_model(str(path))
            return model
        except ImportError:
            logger.error("❌ TensorFlow not available")
            return None
        except Exception as e:
            logger.error(f"❌ Error loading TensorFlow model: {e}")
            return None
    
    def _can_load_model(self, model_info: ModelInfo) -> bool:
        """Check if we can load a model without exceeding memory limits"""
        current_memory = sum(info.memory_usage for info in self.models.values() if info.is_loaded)
        return current_memory + model_info.size_bytes <= self.max_memory_bytes
    
    def _evict_models(self, required_bytes: int):
        """Evict models to free up memory"""
        with self.lock:
            # Sort models by priority and last used time
            eviction_candidates = []
            for name, info in self.models.items():
                if info.is_loaded:
                    # Calculate eviction score (lower priority = higher score)
                    priority_score = {
                        ModelPriority.CRITICAL: 0,
                        ModelPriority.HIGH: 1,
                        ModelPriority.MEDIUM: 2,
                        ModelPriority.LOW: 3
                    }[info.priority]
                    
                    # Time since last used (older = higher score)
                    time_score = time.time() - info.last_used
                    
                    eviction_candidates.append((name, priority_score + time_score / 3600))
            
            # Sort by eviction score (highest first)
            eviction_candidates.sort(key=lambda x: x[1], reverse=True)
            
            freed_bytes = 0
            for name, _ in eviction_candidates:
                if freed_bytes >= required_bytes:
                    break
                
                if name in self.loaded_models:
                    model_info = self.models[name]
                    if model_info.priority != ModelPriority.CRITICAL:
                        self._unload_model(name)
                        freed_bytes += model_info.memory_usage
                        self.cache_stats['evictions'] += 1
                        logger.info(f"🗑️ Evicted model: {name}")
    
    def _unload_model(self, model_name: str):
        """Unload a model from memory"""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            if model_name in self.model_refs:
                del self.model_refs[model_name]
            
            self.models[model_name].is_loaded = False
            self.models[model_name].memory_usage = 0
    
    def _on_model_garbage_collected(self, model_name: str):
        """Callback when model is garbage collected"""
        logger.debug(f"🗑️ Model garbage collected: {model_name}")
        if model_name in self.models:
            self.models[model_name].is_loaded = False
            self.models[model_name].memory_usage = 0
    
    def _estimate_model_memory(self, model: Any) -> int:
        """Estimate memory usage of a loaded model"""
        try:
            if hasattr(model, 'nbytes'):
                return model.nbytes
            elif hasattr(model, 'memory_usage'):
                return model.memory_usage()
            else:
                # Rough estimation based on model type
                return 100 * 1024 * 1024  # 100MB default
        except Exception:
            return 100 * 1024 * 1024  # 100MB default
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """Get a model, loading it if necessary"""
        return self.load_model(model_name)
    
    def preload_models(self, model_names: List[str]):
        """Preload multiple models"""
        for name in model_names:
            if name in self.models:
                self.load_model(name)
    
    def unload_model(self, model_name: str):
        """Explicitly unload a model"""
        with self.lock:
            self._unload_model(model_name)
            logger.info(f"📤 Unloaded model: {model_name}")
    
    def clear_cache(self):
        """Clear all loaded models"""
        with self.lock:
            for name in list(self.loaded_models.keys()):
                self._unload_model(name)
            logger.info("🧹 Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            hit_rate = self.cache_stats['hits'] / total_requests if total_requests > 0 else 0
            
            loaded_models = [name for name, info in self.models.items() if info.is_loaded]
            total_memory = sum(info.memory_usage for info in self.models.values() if info.is_loaded)
            
            return {
                'cache_stats': self.cache_stats.copy(),
                'hit_rate': hit_rate,
                'loaded_models': loaded_models,
                'total_memory_mb': total_memory / 1024 / 1024,
                'max_memory_mb': self.max_memory_bytes / 1024 / 1024,
                'memory_usage_percent': (total_memory / self.max_memory_bytes) * 100
            }

class ModelMemoryOptimizer:
    """Main model memory optimization manager"""
    
    def __init__(self, max_memory_mb: int = 4096):
        self.cache = ModelCache(max_memory_mb=max_memory_mb)
        self.optimization_thread = None
        self.optimization_active = False
        self.optimization_interval = 60.0  # seconds
        
        logger.info("🧠 Model memory optimizer initialized")
    
    def start_optimization(self):
        """Start automatic memory optimization"""
        if self.optimization_active:
            return
        
        self.optimization_active = True
        self.optimization_thread = threading.Thread(target=self._optimization_worker, daemon=True)
        self.optimization_thread.start()
        logger.info("🧠 Model memory optimization started")
    
    def stop_optimization(self):
        """Stop automatic memory optimization"""
        self.optimization_active = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=1.0)
        logger.info("🧠 Model memory optimization stopped")
    
    def _optimization_worker(self):
        """Background optimization worker"""
        while self.optimization_active:
            try:
                self._perform_optimization()
                time.sleep(self.optimization_interval)
            except Exception as e:
                logger.error(f"❌ Optimization worker error: {e}")
    
    def _perform_optimization(self):
        """Perform memory optimization"""
        stats = self.cache.get_cache_stats()
        memory_usage = stats['memory_usage_percent']
        
        if memory_usage > 90:
            logger.warning(f"⚠️ High memory usage: {memory_usage:.1f}%")
            self._aggressive_optimization()
        elif memory_usage > 75:
            logger.info(f"📊 Moderate memory usage: {memory_usage:.1f}%")
            self._moderate_optimization()
    
    def _aggressive_optimization(self):
        """Aggressive memory optimization"""
        # Unload low priority models
        with self.cache.lock:
            for name, info in self.cache.models.items():
                if (info.is_loaded and 
                    info.priority in [ModelPriority.LOW, ModelPriority.MEDIUM] and
                    time.time() - info.last_used > 300):  # 5 minutes
                    self.cache._unload_model(name)
                    logger.info(f"🗑️ Aggressive optimization: unloaded {name}")
    
    def _moderate_optimization(self):
        """Moderate memory optimization"""
        # Unload only low priority models that haven't been used recently
        with self.cache.lock:
            for name, info in self.cache.models.items():
                if (info.is_loaded and 
                    info.priority == ModelPriority.LOW and
                    time.time() - info.last_used > 600):  # 10 minutes
                    self.cache._unload_model(name)
                    logger.info(f"🗑️ Moderate optimization: unloaded {name}")
    
    def add_model(self, model_path: Union[str, Path], priority: ModelPriority = ModelPriority.MEDIUM) -> bool:
        """Add a model to the optimizer"""
        return self.cache.add_model(model_path, priority)
    
    def load_model(self, model_name: str) -> Optional[Any]:
        """Load a model with optimization"""
        return self.cache.load_model(model_name)
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """Get a model, loading if necessary"""
        return self.cache.get_model(model_name)
    
    def preload_models(self, model_names: List[str]):
        """Preload multiple models"""
        self.cache.preload_models(model_names)
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        cache_stats = self.cache.get_cache_stats()
        return {
            'cache_stats': cache_stats,
            'optimization_active': self.optimization_active,
            'optimization_interval': self.optimization_interval,
            'system_memory': psutil.virtual_memory().percent
        }
    
    def cleanup(self):
        """Cleanup optimizer resources"""
        self.stop_optimization()
        self.cache.clear_cache()
        logger.info("🧠 Model memory optimizer cleaned up")

# Global optimizer instance
_model_optimizer = None

def get_model_optimizer(max_memory_mb: int = 4096) -> ModelMemoryOptimizer:
    """Get global model optimizer instance"""
    global _model_optimizer
    if _model_optimizer is None:
        _model_optimizer = ModelMemoryOptimizer(max_memory_mb=max_memory_mb)
    return _model_optimizer

def optimize_model_memory():
    """Convenience function for model memory optimization"""
    optimizer = get_model_optimizer()
    optimizer.start_optimization()
    return optimizer 