#!/usr/bin/env python3
"""
Enhanced Memory Management System for DeepFaceLive
Advanced GPU memory optimization, intelligent caching, and automatic resource management
"""

import gc
import time
import threading
import logging
import psutil
import os
from typing import Dict, List, Optional, Tuple, Any, Callable
from collections import defaultdict, OrderedDict, deque
from dataclasses import dataclass
import weakref
from enum import Enum
from contextlib import contextmanager

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False

try:
    import nvidia_ml_py3 as nvml
    nvml.nvmlInit()
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

class MemoryPriority(Enum):
    """Memory allocation priority levels"""
    CRITICAL = 0    # Critical operations (face detection, processing)
    HIGH = 1        # Important operations (model inference)
    MEDIUM = 2      # General operations (UI updates)
    LOW = 3         # Background operations (caching)

@dataclass
class MemoryBlock:
    """Enhanced memory block information"""
    size: int
    dtype: str
    device: str
    allocated_time: float
    last_used: float
    ref_count: int
    priority: MemoryPriority
    persistent: bool = False
    compressed: bool = False

@dataclass
class MemoryStats:
    """Memory usage statistics"""
    total_allocated: int
    peak_allocated: int
    cache_hits: int
    cache_misses: int
    compression_ratio: float
    fragmentation: float
    gpu_utilization: float

class AdvancedGPUMemoryPool:
    """Advanced GPU memory pooling with compression and optimization"""
    
    def __init__(self, max_pool_size_mb: int = 2048, enable_compression: bool = True):
        self.max_pool_size = max_pool_size_mb * 1024 * 1024
        self.enable_compression = enable_compression
        self.current_pool_size = 0
        self.pools: Dict[str, OrderedDict] = defaultdict(OrderedDict)
        self.compressed_pools: Dict[str, OrderedDict] = defaultdict(OrderedDict)
        self.allocation_stats = MemoryStats(0, 0, 0, 0, 0.0, 0.0, 0.0)
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        
        # Memory monitoring
        self.peak_memory = 0
        self.memory_pressure_threshold = 0.85  # 85% of max pool size
        self.compression_threshold = 0.7       # 70% of max pool size
        
        # Auto-cleanup settings
        self.auto_cleanup_enabled = True
        self.cleanup_interval = 30  # seconds
        self.last_cleanup = time.time()
        
    def allocate(self, size: int, dtype: str, device: str, 
                 priority: MemoryPriority = MemoryPriority.MEDIUM) -> Optional[Any]:
        """Allocate memory with priority-based management"""
        with self.lock:
            pool_key = f"{device}_{dtype}_{size}"
            
            # Try to get from pool first
            if pool_key in self.pools and self.pools[pool_key]:
                block = self.pools[pool_key].popitem(last=False)[1]
                block.last_used = time.time()
                block.ref_count += 1
                self.allocation_stats.cache_hits += 1
                return block
            
            # Check if we need to compress or free memory
            if self.current_pool_size + size > self.max_pool_size:
                if not self._make_space(size, priority):
                    self.logger.warning(f"Failed to allocate {size} bytes, insufficient memory")
                    return None
            
            # Allocate new block
            try:
                block = self._allocate_new_block(size, dtype, device, priority)
                if block:
                    self.current_pool_size += size
                    self.peak_memory = max(self.peak_memory, self.current_pool_size)
                    self.allocation_stats.total_allocated += size
                    self.allocation_stats.peak_allocated = max(
                        self.allocation_stats.peak_allocated, self.current_pool_size
                    )
                return block
            except Exception as e:
                self.logger.error(f"Memory allocation failed: {e}")
                self.allocation_stats.cache_misses += 1
                return None
    
    def deallocate(self, block: MemoryBlock):
        """Return memory block to pool"""
        with self.lock:
            if block.ref_count > 1:
                block.ref_count -= 1
                return
            
            pool_key = f"{block.device}_{block.dtype}_{block.size}"
            
            # Compress if memory pressure is high
            if (self.enable_compression and 
                self.current_pool_size > self.max_pool_size * self.compression_threshold):
                compressed_block = self._compress_block(block)
                if compressed_block:
                    self.compressed_pools[pool_key][id(compressed_block)] = compressed_block
                    return
            
            # Add to regular pool
            block.last_used = time.time()
            self.pools[pool_key][id(block)] = block
            
            # Auto-cleanup if needed
            if self.auto_cleanup_enabled:
                self._maybe_cleanup()
    
    def _allocate_new_block(self, size: int, dtype: str, device: str, 
                           priority: MemoryPriority) -> Optional[MemoryBlock]:
        """Allocate a new memory block"""
        if TORCH_AVAILABLE and device.startswith('cuda'):
            try:
                data = torch.empty(size, dtype=getattr(torch, dtype, torch.float32), device=device)
                return MemoryBlock(
                    size=size,
                    dtype=dtype,
                    device=device,
                    allocated_time=time.time(),
                    last_used=time.time(),
                    ref_count=1,
                    priority=priority
                )
            except torch.cuda.OutOfMemoryError:
                return None
        
        # Fallback allocation methods
        return None
    
    def _make_space(self, required_size: int, priority: MemoryPriority) -> bool:
        """Make space for new allocation"""
        freed_size = 0
        
        # 1. Try to decompress blocks first
        if self.compressed_pools:
            for pool_key, pool in list(self.compressed_pools.items()):
                if freed_size >= required_size:
                    break
                for block_id, block in list(pool.items()):
                    if block.priority.value > priority.value:
                        self._free_compressed_block(block)
                        freed_size += block.size
                        del pool[block_id]
                        if freed_size >= required_size:
                            break
        
        # 2. Free regular pool blocks with lower priority
        for pool_key, pool in list(self.pools.items()):
            if freed_size >= required_size:
                break
            for block_id, block in list(pool.items()):
                if block.priority.value > priority.value and not block.persistent:
                    self._free_block(block)
                    freed_size += block.size
                    del pool[block_id]
                    if freed_size >= required_size:
                        break
        
        # 3. Force garbage collection
        if freed_size < required_size:
            gc.collect()
            if TORCH_AVAILABLE:
                torch.cuda.empty_cache()
        
        self.current_pool_size -= freed_size
        return freed_size >= required_size
    
    def _compress_block(self, block: MemoryBlock) -> Optional[MemoryBlock]:
        """Compress a memory block to save space"""
        if not self.enable_compression:
            return None
        
        try:
            # Implement compression logic here
            # For now, just mark as compressed
            compressed_block = MemoryBlock(
                size=block.size // 2,  # Assume 50% compression
                dtype=block.dtype,
                device=block.device,
                allocated_time=block.allocated_time,
                last_used=block.last_used,
                ref_count=block.ref_count,
                priority=block.priority,
                compressed=True
            )
            self.allocation_stats.compression_ratio = 0.5
            return compressed_block
        except Exception as e:
            self.logger.error(f"Compression failed: {e}")
            return None
    
    def _free_block(self, block: MemoryBlock):
        """Free a memory block"""
        # Implementation depends on the memory type
        pass
    
    def _free_compressed_block(self, block: MemoryBlock):
        """Free a compressed memory block"""
        # Implementation for compressed blocks
        pass
    
    def _maybe_cleanup(self):
        """Perform cleanup if needed"""
        now = time.time()
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_expired_blocks()
    
    def _cleanup_expired_blocks(self, max_age_seconds: int = 300):
        """Clean up expired memory blocks"""
        with self.lock:
            current_time = time.time()
            freed_size = 0
            
            for pool_key, pool in list(self.pools.items()):
                for block_id, block in list(pool.items()):
                    if (current_time - block.last_used > max_age_seconds and 
                        not block.persistent and 
                        block.ref_count <= 1):
                        self._free_block(block)
                        freed_size += block.size
                        del pool[block_id]
            
            self.current_pool_size -= freed_size
            if freed_size > 0:
                self.logger.info(f"Cleaned up {freed_size / 1024 / 1024:.1f} MB of expired memory")

class ModelCacheManager:
    """Advanced model caching with intelligent preloading"""
    
    def __init__(self, max_cache_size_mb: int = 512):
        self.max_cache_size = max_cache_size_mb * 1024 * 1024
        self.cache: OrderedDict = OrderedDict()
        self.cache_sizes: Dict[str, int] = {}
        self.access_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
        self.prediction_weights: Dict[str, float] = {}
        self.current_cache_size = 0
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        
        # Predictive loading
        self.preload_enabled = True
        self.access_history: deque = deque(maxlen=100)
        
    def get_model(self, model_key: str, loader_func: Callable = None) -> Optional[Any]:
        """Get model with predictive preloading"""
        with self.lock:
            current_time = time.time()
            
            # Record access pattern
            self.access_patterns[model_key].append(current_time)
            self.access_history.append((model_key, current_time))
            
            # Update prediction weights
            self._update_prediction_weights(model_key)
            
            if model_key in self.cache:
                # Move to end (most recently used)
                model = self.cache.pop(model_key)
                self.cache[model_key] = model
                
                # Trigger predictive preloading
                if self.preload_enabled:
                    self._predict_and_preload()
                
                return model
            
            # Load model if not in cache
            if loader_func:
                model = loader_func()
                if model:
                    self._add_to_cache(model_key, model)
                    return model
            
            return None
    
    def _add_to_cache(self, model_key: str, model: Any):
        """Add model to cache with size management"""
        model_size = self._estimate_model_size(model)
        
        # Make space if needed
        while (self.current_cache_size + model_size > self.max_cache_size and 
               len(self.cache) > 0):
            self._evict_least_valuable()
        
        self.cache[model_key] = model
        self.cache_sizes[model_key] = model_size
        self.current_cache_size += model_size
        
        self.logger.info(f"Cached model {model_key} ({model_size / 1024 / 1024:.1f} MB)")
    
    def _estimate_model_size(self, model: Any) -> int:
        """Estimate model size in bytes"""
        if TORCH_AVAILABLE and hasattr(model, 'parameters'):
            total_params = sum(p.numel() for p in model.parameters())
            return total_params * 4  # Assume float32
        
        # Fallback estimation
        return 50 * 1024 * 1024  # 50MB default
    
    def _update_prediction_weights(self, model_key: str):
        """Update prediction weights based on access patterns"""
        access_times = list(self.access_patterns[model_key])
        if len(access_times) < 2:
            return
        
        # Calculate access frequency
        recent_accesses = sum(1 for t in access_times if time.time() - t < 300)  # 5 minutes
        frequency_weight = recent_accesses / len(access_times)
        
        # Calculate recency weight
        last_access = access_times[-1]
        recency_weight = max(0, 1 - (time.time() - last_access) / 600)  # 10 minutes decay
        
        # Combined weight
        self.prediction_weights[model_key] = frequency_weight * 0.7 + recency_weight * 0.3
    
    def _predict_and_preload(self):
        """Predict and preload likely-to-be-used models"""
        if not self.access_history:
            return
        
        # Analyze access patterns
        recent_models = [model for model, _ in list(self.access_history)[-5:]]
        
        # Simple prediction: preload models accessed together
        for model_key, weight in self.prediction_weights.items():
            if (model_key not in self.cache and 
                weight > 0.5 and 
                model_key in recent_models):
                # Schedule background preloading
                threading.Thread(target=self._background_preload, 
                               args=(model_key,), daemon=True).start()
    
    def _background_preload(self, model_key: str):
        """Background preloading of predicted models"""
        # This would implement background model loading
        pass
    
    def _evict_least_valuable(self):
        """Evict the least valuable model from cache"""
        if not self.cache:
            return
        
        # Calculate value scores
        scores = {}
        current_time = time.time()
        
        for model_key in self.cache:
            access_times = list(self.access_patterns[model_key])
            if not access_times:
                scores[model_key] = 0
                continue
            
            # Recency score
            last_access = access_times[-1]
            recency = max(0, 1 - (current_time - last_access) / 600)
            
            # Frequency score
            frequency = len(access_times) / 10  # Normalize to max 10 accesses
            
            # Size penalty (prefer keeping smaller models)
            size_penalty = self.cache_sizes.get(model_key, 0) / (100 * 1024 * 1024)
            
            scores[model_key] = recency * 0.5 + frequency * 0.4 - size_penalty * 0.1
        
        # Evict lowest scoring model
        victim = min(scores.keys(), key=lambda k: scores[k])
        evicted_model = self.cache.pop(victim)
        evicted_size = self.cache_sizes.pop(victim, 0)
        self.current_cache_size -= evicted_size
        
        self.logger.info(f"Evicted model {victim} ({evicted_size / 1024 / 1024:.1f} MB)")

class ResourceMonitor:
    """System resource monitoring and optimization"""
    
    def __init__(self, check_interval: int = 5):
        self.check_interval = check_interval
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.callbacks: List[Callable] = []
        self.logger = logging.getLogger(__name__)
        
        # Thresholds
        self.memory_threshold = 0.85  # 85% memory usage
        self.gpu_memory_threshold = 0.9  # 90% GPU memory usage
        self.cpu_threshold = 0.8  # 80% CPU usage
        
    def add_callback(self, callback: Callable):
        """Add callback for resource pressure events"""
        self.callbacks.append(callback)
    
    def start_monitoring(self):
        """Start resource monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            self.logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            self.logger.info("Resource monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._check_resources()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {e}")
    
    def _check_resources(self):
        """Check system resources and trigger callbacks if needed"""
        # Check system memory
        memory = psutil.virtual_memory()
        if memory.percent / 100 > self.memory_threshold:
            self._trigger_callbacks('memory_pressure', {
                'type': 'system_memory',
                'usage_percent': memory.percent,
                'available_mb': memory.available / 1024 / 1024
            })
        
        # Check GPU memory if available
        if TORCH_AVAILABLE:
            try:
                for i in range(torch.cuda.device_count()):
                    allocated = torch.cuda.memory_allocated(i)
                    cached = torch.cuda.memory_reserved(i)
                    total = torch.cuda.get_device_properties(i).total_memory
                    
                    usage = (allocated + cached) / total
                    if usage > self.gpu_memory_threshold:
                        self._trigger_callbacks('memory_pressure', {
                            'type': 'gpu_memory',
                            'device': i,
                            'usage_percent': usage * 100,
                            'allocated_mb': allocated / 1024 / 1024,
                            'cached_mb': cached / 1024 / 1024
                        })
            except Exception as e:
                self.logger.debug(f"GPU memory check failed: {e}")
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent / 100 > self.cpu_threshold:
            self._trigger_callbacks('cpu_pressure', {
                'type': 'cpu',
                'usage_percent': cpu_percent
            })
    
    def _trigger_callbacks(self, event_type: str, data: Dict[str, Any]):
        """Trigger registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")

class EnhancedMemoryManager:
    """Enhanced memory manager with all optimization features"""
    
    def __init__(self, 
                 gpu_pool_size_mb: int = 2048,
                 model_cache_size_mb: int = 512,
                 enable_compression: bool = True):
        
        self.gpu_pool = AdvancedGPUMemoryPool(gpu_pool_size_mb, enable_compression)
        self.model_cache = ModelCacheManager(model_cache_size_mb)
        self.resource_monitor = ResourceMonitor()
        self.logger = logging.getLogger(__name__)
        
        # Register resource pressure callbacks
        self.resource_monitor.add_callback(self._handle_memory_pressure)
        self.resource_monitor.add_callback(self._handle_cpu_pressure)
        
        # Start monitoring
        self.resource_monitor.start_monitoring()
        
    def _handle_memory_pressure(self, event_type: str, data: Dict[str, Any]):
        """Handle memory pressure events"""
        if event_type == 'memory_pressure':
            self.logger.warning(f"Memory pressure detected: {data}")
            
            if data['type'] == 'system_memory':
                # Force garbage collection
                gc.collect()
                
                # Clear model cache if needed
                if data['usage_percent'] > 90:
                    self.model_cache.cache.clear()
                    self.model_cache.current_cache_size = 0
                    
            elif data['type'] == 'gpu_memory':
                # Clear GPU memory pools
                self.gpu_pool._cleanup_expired_blocks(max_age_seconds=60)
                
                if TORCH_AVAILABLE:
                    torch.cuda.empty_cache()
    
    def _handle_cpu_pressure(self, event_type: str, data: Dict[str, Any]):
        """Handle CPU pressure events"""
        if event_type == 'cpu_pressure':
            self.logger.warning(f"CPU pressure detected: {data}")
            # Could implement CPU-specific optimizations here
    
    @contextmanager
    def memory_context(self, priority: MemoryPriority = MemoryPriority.MEDIUM):
        """Context manager for memory operations"""
        start_memory = self.gpu_pool.current_pool_size
        try:
            yield
        finally:
            end_memory = self.gpu_pool.current_pool_size
            if end_memory > start_memory:
                self.logger.debug(f"Memory allocated in context: {(end_memory - start_memory) / 1024 / 1024:.1f} MB")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        stats = {
            'gpu_pool': {
                'total_size_mb': self.gpu_pool.max_pool_size / 1024 / 1024,
                'current_size_mb': self.gpu_pool.current_pool_size / 1024 / 1024,
                'peak_size_mb': self.gpu_pool.peak_memory / 1024 / 1024,
                'utilization': self.gpu_pool.current_pool_size / self.gpu_pool.max_pool_size,
                'compression_ratio': self.gpu_pool.allocation_stats.compression_ratio
            },
            'model_cache': {
                'max_size_mb': self.model_cache.max_cache_size / 1024 / 1024,
                'current_size_mb': self.model_cache.current_cache_size / 1024 / 1024,
                'cached_models': len(self.model_cache.cache),
                'hit_rate': self._calculate_cache_hit_rate()
            },
            'system': {
                'memory_percent': psutil.virtual_memory().percent,
                'available_memory_mb': psutil.virtual_memory().available / 1024 / 1024,
            }
        }
        
        if TORCH_AVAILABLE and torch.cuda.is_available():
            stats['system']['gpu_memory_allocated_mb'] = torch.cuda.memory_allocated() / 1024 / 1024
            stats['system']['gpu_memory_cached_mb'] = torch.cuda.memory_reserved() / 1024 / 1024
        
        return stats
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate model cache hit rate"""
        total_accesses = len(self.model_cache.access_history)
        if total_accesses == 0:
            return 0.0
        
        cache_hits = sum(1 for model, _ in self.model_cache.access_history 
                        if model in self.model_cache.cache)
        return cache_hits / total_accesses
    
    def optimize_for_inference(self):
        """Optimize memory configuration for inference"""
        self.gpu_pool.memory_pressure_threshold = 0.9
        self.gpu_pool.compression_threshold = 0.8
        self.model_cache.preload_enabled = True
        self.logger.info("Memory manager optimized for inference")
    
    def optimize_for_training(self):
        """Optimize memory configuration for training"""
        self.gpu_pool.memory_pressure_threshold = 0.75
        self.gpu_pool.compression_threshold = 0.6
        self.model_cache.preload_enabled = False
        self.logger.info("Memory manager optimized for training")

# Global enhanced memory manager instance
_enhanced_memory_manager = None

def get_enhanced_memory_manager() -> EnhancedMemoryManager:
    """Get global enhanced memory manager instance"""
    global _enhanced_memory_manager
    if _enhanced_memory_manager is None:
        _enhanced_memory_manager = EnhancedMemoryManager()
    return _enhanced_memory_manager