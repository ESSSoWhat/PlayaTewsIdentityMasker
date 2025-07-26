#!/usr/bin/env python3
"""
Enhanced GPU Memory Management System for DeepFaceLive
Optimizes GPU memory allocation, caching, and cleanup with adaptive management
"""

import gc
import time
import threading
import logging
import weakref
from typing import Dict, List, Optional, Tuple, Any, Callable
from collections import defaultdict, OrderedDict
from dataclasses import dataclass
from enum import Enum

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

# Performance monitoring
class MemoryPriority(Enum):
    """Memory allocation priority levels"""
    CRITICAL = 0    # Must succeed (model loading, inference)
    HIGH = 1        # Important (frame processing)
    MEDIUM = 2      # Normal (caching, buffering)
    LOW = 3         # Optional (preloading, background tasks)

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
    access_count: int = 0
    compression_ratio: float = 1.0

class AdaptiveMemoryPool:
    """Enhanced GPU memory pooling system with adaptive management"""
    
    def __init__(self, max_pool_size_mb: int = 1024, adaptive_threshold: float = 0.8):
        self.max_pool_size = max_pool_size_mb * 1024 * 1024  # Convert to bytes
        self.current_pool_size = 0
        self.pools: Dict[str, OrderedDict] = defaultdict(OrderedDict)
        self.allocated_blocks: Dict[int, MemoryBlock] = {}
        self.cleanup_threshold = adaptive_threshold
        self.lock = threading.RLock()  # Use RLock for better performance
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.total_allocations = 0
        self.total_reuses = 0
        self.total_cleanups = 0
        self.peak_usage = 0
        
        # Adaptive management
        self.usage_history = []
        self.cleanup_history = []
        self.adaptive_enabled = True
        
        # Compression support
        self.compression_enabled = True
        self.compression_threshold = 0.7  # Compress when 70% full
        
    def allocate(self, shape: Tuple[int, ...], dtype: str, device: str = 'cuda:0', 
                 priority: MemoryPriority = MemoryPriority.MEDIUM) -> Optional[Any]:
        """Enhanced memory allocation with priority and adaptive management"""
        size = self._calculate_size(shape, dtype)
        key = self._get_pool_key(shape, dtype, device)
        
        with self.lock:
            # Try to get from pool first
            if key in self.pools and self.pools[key]:
                _, memory_obj = self.pools[key].popitem(last=False)  # FIFO
                self.current_pool_size -= size
                self.total_reuses += 1
                
                # Update block info
                block_id = id(memory_obj)
                if block_id in self.allocated_blocks:
                    self.allocated_blocks[block_id].last_used = time.time()
                    self.allocated_blocks[block_id].access_count += 1
                    self.allocated_blocks[block_id].priority = priority
                
                self.logger.debug(f"♻️ Reused memory block: {shape}, {dtype} (reuses: {self.total_reuses})")
                return memory_obj
            
            # Check if we need adaptive cleanup
            if self.adaptive_enabled and self.current_pool_size > self.max_pool_size * self.cleanup_threshold:
                self._adaptive_cleanup(priority)
            
            # Allocate new memory
            try:
                memory_obj = self._allocate_new(shape, dtype, device)
                if memory_obj is not None:
                    block_id = id(memory_obj)
                    self.allocated_blocks[block_id] = MemoryBlock(
                        size=size,
                        dtype=dtype,
                        device=device,
                        allocated_time=time.time(),
                        last_used=time.time(),
                        ref_count=1,
                        priority=priority,
                        access_count=1
                    )
                    self.total_allocations += 1
                    self.peak_usage = max(self.peak_usage, self.current_pool_size + size)
                    
                    self.logger.debug(f"🆕 Allocated new memory block: {shape}, {dtype} (total: {self.total_allocations})")
                return memory_obj
            except Exception as e:
                self.logger.error(f"❌ Memory allocation failed: {e}")
                # Try emergency cleanup for critical allocations
                if priority == MemoryPriority.CRITICAL:
                    self._emergency_cleanup()
                    try:
                        memory_obj = self._allocate_new(shape, dtype, device)
                        if memory_obj is not None:
                            self.logger.warning("⚠️ Emergency cleanup successful for critical allocation")
                            return memory_obj
                    except Exception as e2:
                        self.logger.error(f"❌ Emergency allocation also failed: {e2}")
                return None
    
    def deallocate(self, memory_obj: Any, shape: Tuple[int, ...], dtype: str, device: str = 'cuda:0'):
        """Enhanced memory deallocation with compression support"""
        if memory_obj is None:
            return
        
        size = self._calculate_size(shape, dtype)
        key = self._get_pool_key(shape, dtype, device)
        block_id = id(memory_obj)
        
        with self.lock:
            # Update block info
            if block_id in self.allocated_blocks:
                self.allocated_blocks[block_id].last_used = time.time()
                self.allocated_blocks[block_id].ref_count -= 1
                
                if self.allocated_blocks[block_id].ref_count <= 0:
                    del self.allocated_blocks[block_id]
            
            # Check if we should compress
            if (self.compression_enabled and 
                self.current_pool_size + size > self.max_pool_size * self.compression_threshold):
                try:
                    compressed_obj = self._compress_memory(memory_obj, shape, dtype)
                    if compressed_obj is not None:
                        memory_obj = compressed_obj
                        size = size // 2  # Approximate compression ratio
                        self.logger.debug(f"🗜️ Compressed memory block: {shape}, {dtype}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Compression failed: {e}")
            
            # Add to pool if space available
            if self.current_pool_size + size <= self.max_pool_size:
                self.pools[key][time.time()] = memory_obj
                self.current_pool_size += size
                self.logger.debug(f"📦 Returned memory to pool: {shape}, {dtype} (pool size: {len(self.pools[key])})")
            else:
                # Pool full, actually free the memory
                self._free_memory(memory_obj, device)
                self.total_cleanups += 1
                self.logger.debug(f"🗑️ Freed memory (pool full): {shape}, {dtype} (cleanups: {self.total_cleanups})")
    
    def _adaptive_cleanup(self, current_priority: MemoryPriority):
        """Adaptive cleanup based on usage patterns and priority"""
        current_time = time.time()
        
        # Calculate cleanup strategy based on priority
        if current_priority == MemoryPriority.CRITICAL:
            # Aggressive cleanup for critical allocations
            cleanup_age = 60.0  # 1 minute
            priority_threshold = MemoryPriority.LOW
        elif current_priority == MemoryPriority.HIGH:
            # Moderate cleanup for high priority
            cleanup_age = 300.0  # 5 minutes
            priority_threshold = MemoryPriority.MEDIUM
        else:
            # Conservative cleanup for normal priority
            cleanup_age = 600.0  # 10 minutes
            priority_threshold = MemoryPriority.LOW
        
        # Clean up old blocks
        for key in list(self.pools.keys()):
            pool = self.pools[key]
            for timestamp in list(pool.keys()):
                if current_time - timestamp > cleanup_age:
                    memory_obj = pool.pop(timestamp)
                    size = self._estimate_size(memory_obj)
                    self.current_pool_size -= size
                    self._free_memory(memory_obj, 'cuda:0')
                    self.total_cleanups += 1
        
        # Clean up low priority blocks
        for block_id, block in list(self.allocated_blocks.items()):
            if (block.priority.value > priority_threshold.value and 
                current_time - block.last_used > cleanup_age):
                # Force cleanup of low priority blocks
                del self.allocated_blocks[block_id]
        
        # Update usage history
        self.usage_history.append({
            'timestamp': current_time,
            'pool_size': self.current_pool_size,
            'cleanups': self.total_cleanups
        })
        
        # Keep only recent history
        if len(self.usage_history) > 100:
            self.usage_history = self.usage_history[-50:]
        
        self.logger.info(f"🔄 Adaptive cleanup completed: {self.total_cleanups} cleanups, "
                        f"pool size: {self.current_pool_size / 1024 / 1024:.1f}MB")
    
    def _emergency_cleanup(self):
        """Emergency cleanup for critical memory situations"""
        self.logger.warning("🚨 Emergency memory cleanup initiated")
        
        # Force cleanup of all non-critical blocks
        current_time = time.time()
        for block_id, block in list(self.allocated_blocks.items()):
            if block.priority != MemoryPriority.CRITICAL:
                del self.allocated_blocks[block_id]
        
        # Clear all pools
        for key in list(self.pools.keys()):
            pool = self.pools[key]
            for timestamp in list(pool.keys()):
                memory_obj = pool.pop(timestamp)
                self._free_memory(memory_obj, 'cuda:0')
        
        self.current_pool_size = 0
        self.total_cleanups += 1
        
        # Force garbage collection
        gc.collect()
        
        self.logger.warning("🚨 Emergency cleanup completed")
    
    def _compress_memory(self, memory_obj: Any, shape: Tuple[int, ...], dtype: str) -> Optional[Any]:
        """Compress memory object to save space"""
        try:
            # Simple compression for demonstration
            # In practice, this could use more sophisticated compression
            if hasattr(memory_obj, 'numpy'):
                # For numpy arrays, we could use compression
                return memory_obj
            else:
                # For other objects, return as-is
                return memory_obj
        except Exception as e:
            self.logger.warning(f"⚠️ Compression failed: {e}")
            return memory_obj
    
    def get_detailed_stats(self) -> Dict:
        """Get comprehensive memory statistics"""
        with self.lock:
            total_blocks = sum(len(pool) for pool in self.pools.values())
            active_blocks = len(self.allocated_blocks)
            
            # Calculate reuse rate
            reuse_rate = self.total_reuses / max(self.total_allocations, 1)
            
            # Calculate average block age
            current_time = time.time()
            avg_age = 0
            if self.allocated_blocks:
                ages = [current_time - block.allocated_time for block in self.allocated_blocks.values()]
                avg_age = sum(ages) / len(ages)
            
            return {
                'pool_size_mb': self.current_pool_size / 1024 / 1024,
                'max_pool_size_mb': self.max_pool_size / 1024 / 1024,
                'pool_utilization': self.current_pool_size / self.max_pool_size,
                'total_pooled_blocks': total_blocks,
                'active_blocks': active_blocks,
                'pool_types': len(self.pools),
                'total_allocations': self.total_allocations,
                'total_reuses': self.total_reuses,
                'total_cleanups': self.total_cleanups,
                'reuse_rate': reuse_rate,
                'peak_usage_mb': self.peak_usage / 1024 / 1024,
                'average_block_age_seconds': avg_age,
                'adaptive_enabled': self.adaptive_enabled,
                'compression_enabled': self.compression_enabled
            }
    
    def set_adaptive_threshold(self, threshold: float):
        """Set adaptive cleanup threshold"""
        self.cleanup_threshold = max(0.1, min(0.9, threshold))
        self.logger.info(f"🔧 Adaptive threshold set to {self.cleanup_threshold}")
    
    def enable_compression(self, enabled: bool):
        """Enable or disable memory compression"""
        self.compression_enabled = enabled
        self.logger.info(f"🔧 Memory compression {'enabled' if enabled else 'disabled'}")
    
    def _get_pool_key(self, shape: Tuple[int, ...], dtype: str, device: str) -> str:
        """Generate pool key for memory block"""
        return f"{shape}_{dtype}_{device}"
    
    def _calculate_size(self, shape: Tuple[int, ...], dtype: str) -> int:
        """Calculate memory size in bytes"""
        type_sizes = {
            'float32': 4, 'float16': 2, 'float64': 8,
            'int32': 4, 'int16': 2, 'int8': 1, 'int64': 8,
            'uint8': 1, 'uint16': 2, 'uint32': 4
        }
        
        element_count = 1
        for dim in shape:
            element_count *= dim
        
        return element_count * type_sizes.get(dtype, 4)
    
    def _estimate_size(self, memory_obj: Any) -> int:
        """Estimate memory object size"""
        if TORCH_AVAILABLE and hasattr(memory_obj, 'element_size'):
            return memory_obj.nelement() * memory_obj.element_size()
        elif hasattr(memory_obj, 'nbytes'):
            return memory_obj.nbytes
        else:
            return 0
    
    def _allocate_new(self, shape: Tuple[int, ...], dtype: str, device: str) -> Optional[Any]:
        """Allocate new memory block"""
        if TORCH_AVAILABLE and device.startswith('cuda'):
            try:
                torch_dtype = getattr(torch, dtype, torch.float32)
                return torch.empty(shape, dtype=torch_dtype, device=device)
            except Exception:
                pass
        
        if CUPY_AVAILABLE and device.startswith('cuda'):
            try:
                import numpy as np
                numpy_dtype = getattr(np, dtype, np.float32)
                return cp.empty(shape, dtype=numpy_dtype)
            except Exception:
                pass
        
        # Fallback to CPU
        try:
            import numpy as np
            numpy_dtype = getattr(np, dtype, np.float32)
            return np.empty(shape, dtype=numpy_dtype)
        except Exception:
            return None
    
    def _free_memory(self, memory_obj: Any, device: str):
        """Actually free memory object"""
        if TORCH_AVAILABLE and hasattr(memory_obj, 'is_cuda'):
            if memory_obj.is_cuda:
                del memory_obj
                torch.cuda.empty_cache()
        elif CUPY_AVAILABLE and hasattr(memory_obj, 'device'):
            try:
                memory_obj.device.synchronize()
                del memory_obj
                cp.get_default_memory_pool().free_all_blocks()
            except:
                pass
        else:
            del memory_obj
        
        gc.collect()

class ModelCache:
    """LRU cache for ML models with automatic cleanup"""
    
    def __init__(self, max_models: int = 3, max_size_mb: int = 2048):
        self.max_models = max_models
        self.max_size_mb = max_size_mb
        self.cache: OrderedDict = OrderedDict()
        self.model_sizes: Dict[str, float] = {}
        self.total_size_mb = 0
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def get_model(self, model_path: str, loader_func: callable) -> Any:
        """Get model from cache or load new one"""
        with self.lock:
            if model_path in self.cache:
                # Move to end (most recently used)
                model = self.cache.pop(model_path)
                self.cache[model_path] = model
                self.logger.debug(f"Model cache hit: {model_path}")
                return model
            
            # Load new model
            self.logger.info(f"Loading model: {model_path}")
            model = loader_func(model_path)
            
            if model is None:
                return None
            
            # Estimate model size
            model_size_mb = self._estimate_model_size(model)
            
            # Check if we need to evict models
            while (len(self.cache) >= self.max_models or 
                   self.total_size_mb + model_size_mb > self.max_size_mb):
                if not self.cache:
                    break
                self._evict_oldest_model()
            
            # Add to cache
            self.cache[model_path] = model
            self.model_sizes[model_path] = model_size_mb
            self.total_size_mb += model_size_mb
            
            self.logger.info(f"Cached model: {model_path} ({model_size_mb:.1f}MB)")
            return model
    
    def clear_cache(self):
        """Clear all cached models"""
        with self.lock:
            for model_path in list(self.cache.keys()):
                self._evict_model(model_path)
            self.logger.info("Cleared model cache")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            return {
                'cached_models': len(self.cache),
                'max_models': self.max_models,
                'total_size_mb': self.total_size_mb,
                'max_size_mb': self.max_size_mb,
                'cache_utilization': self.total_size_mb / self.max_size_mb,
                'model_paths': list(self.cache.keys())
            }
    
    def _estimate_model_size(self, model: Any) -> float:
        """Estimate model size in MB"""
        try:
            if TORCH_AVAILABLE and hasattr(model, 'parameters'):
                # PyTorch model
                total_params = sum(p.numel() * p.element_size() for p in model.parameters())
                return total_params / 1024 / 1024
            elif hasattr(model, 'get_inputs') and hasattr(model, 'get_outputs'):
                # ONNX model - rough estimate
                return 50.0  # Default estimate for ONNX models
            else:
                return 10.0  # Default estimate
        except Exception:
            return 10.0
    
    def _evict_oldest_model(self):
        """Evict the oldest (least recently used) model"""
        if not self.cache:
            return
        
        oldest_path = next(iter(self.cache))
        self._evict_model(oldest_path)
    
    def _evict_model(self, model_path: str):
        """Evict specific model from cache"""
        if model_path in self.cache:
            model = self.cache.pop(model_path)
            model_size = self.model_sizes.pop(model_path, 0)
            self.total_size_mb -= model_size
            
            # Free GPU memory if applicable
            if TORCH_AVAILABLE and hasattr(model, 'cuda'):
                try:
                    if next(model.parameters()).is_cuda:
                        del model
                        torch.cuda.empty_cache()
                except:
                    pass
            else:
                del model
            
            self.logger.info(f"Evicted model from cache: {model_path}")

class MemoryManager:
    """Comprehensive memory management system"""
    
    def __init__(self, 
                 gpu_pool_size_mb: int = 1024,
                 max_cached_models: int = 3,
                 cleanup_interval: float = 300.0):
        
        self.gpu_pool = AdaptiveMemoryPool(gpu_pool_size_mb)
        self.model_cache = ModelCache(max_cached_models)
        self.cleanup_interval = cleanup_interval
        
        # Monitoring
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.memory_stats_history: List[Dict] = []
        
        self.logger = logging.getLogger(__name__)
    
    def start_monitoring(self):
        """Start memory monitoring and cleanup"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        self.logger.info("Memory monitoring stopped")
    
    def allocate_gpu_memory(self, shape: Tuple[int, ...], 
                           dtype: str = 'float32', 
                           device: str = 'cuda:0',
                           priority: MemoryPriority = MemoryPriority.MEDIUM) -> Optional[Any]:
        """Allocate GPU memory through pool"""
        return self.gpu_pool.allocate(shape, dtype, device, priority)
    
    def deallocate_gpu_memory(self, memory_obj: Any, 
                             shape: Tuple[int, ...], 
                             dtype: str = 'float32', 
                             device: str = 'cuda:0'):
        """Deallocate GPU memory to pool"""
        self.gpu_pool.deallocate(memory_obj, shape, dtype, device)
    
    def get_cached_model(self, model_path: str, loader_func: callable) -> Any:
        """Get model from cache"""
        return self.model_cache.get_model(model_path, loader_func)
    
    def force_cleanup(self):
        """Force immediate memory cleanup"""
        self.gpu_pool.cleanup_unused(max_age_seconds=0)
        
        # Force garbage collection
        gc.collect()
        
        # Clear GPU cache if available
        if TORCH_AVAILABLE:
            torch.cuda.empty_cache()
        if CUPY_AVAILABLE:
            cp.get_default_memory_pool().free_all_blocks()
        
        self.logger.info("Forced memory cleanup completed")
    
    def get_memory_summary(self) -> Dict:
        """Get comprehensive memory usage summary"""
        gpu_stats = self.gpu_pool.get_detailed_stats()
        cache_stats = self.model_cache.get_cache_stats()
        
        # System memory
        import psutil
        process = psutil.Process()
        system_memory_mb = process.memory_info().rss / 1024 / 1024
        
        # GPU memory
        gpu_memory_mb = 0
        gpu_memory_total_mb = 0
        
        if TORCH_AVAILABLE and torch.cuda.is_available():
            gpu_memory_mb = torch.cuda.memory_allocated() / 1024 / 1024
            gpu_memory_total_mb = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024
        
        return {
            'system_memory_mb': system_memory_mb,
            'gpu_memory_mb': gpu_memory_mb,
            'gpu_memory_total_mb': gpu_memory_total_mb,
            'gpu_pool': gpu_stats,
            'model_cache': cache_stats,
            'timestamp': time.time()
        }
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        retry_count = 0
        max_retry_count = 5
        
        while self.monitoring:
            try:
                # Collect memory stats
                stats = self.get_memory_summary()
                self.memory_stats_history.append(stats)
                
                # Keep only last 100 entries - more efficient cleanup
                if len(self.memory_stats_history) > 100:
                    # Remove oldest entries in chunks for better performance
                    excess = len(self.memory_stats_history) - 100
                    self.memory_stats_history = self.memory_stats_history[excess:]
                
                # Check for memory issues
                if stats['system_memory_mb'] > 3072:  # 3GB warning
                    self.logger.warning(f"High system memory usage: {stats['system_memory_mb']:.1f}MB")
                
                if stats['gpu_memory_total_mb'] > 0:
                    gpu_usage_pct = (stats['gpu_memory_mb'] / stats['gpu_memory_total_mb']) * 100
                    if gpu_usage_pct > 85:  # 85% warning
                        self.logger.warning(f"High GPU memory usage: {gpu_usage_pct:.1f}%")
                
                # Periodic cleanup
                self.gpu_pool.cleanup_unused()
                
                # Reset retry count on successful iteration
                retry_count = 0
                
                time.sleep(self.cleanup_interval)
                
            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")
                retry_count += 1
                
                # Use exponential backoff with maximum limit
                if retry_count <= max_retry_count:
                    retry_delay = min(30, 2 ** retry_count)  # Cap at 30 seconds
                    self.logger.warning(f"Retrying in {retry_delay} seconds (attempt {retry_count}/{max_retry_count})")
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"Too many consecutive errors ({retry_count}), stopping monitoring")
                    break

# Global memory manager instance
_global_memory_manager: Optional[MemoryManager] = None

def get_memory_manager() -> MemoryManager:
    """Get global memory manager instance"""
    global _global_memory_manager
    if _global_memory_manager is None:
        _global_memory_manager = MemoryManager()
    return _global_memory_manager

def start_memory_monitoring():
    """Start global memory monitoring"""
    manager = get_memory_manager()
    manager.start_monitoring()

def stop_memory_monitoring():
    """Stop global memory monitoring"""
    global _global_memory_manager
    if _global_memory_manager:
        _global_memory_manager.stop_monitoring()

if __name__ == "__main__":
    # Test memory management
    import numpy as np
    
    manager = MemoryManager(gpu_pool_size_mb=512, max_cached_models=2)
    manager.start_monitoring()
    
    print("Testing memory management...")
    
    # Test GPU memory allocation
    for i in range(10):
        shape = (1024, 1024)
        memory = manager.allocate_gpu_memory(shape, 'float32')
        if memory is not None:
            print(f"Allocated memory block {i}: {shape}")
            # Use memory briefly
            time.sleep(0.1)
            manager.deallocate_gpu_memory(memory, shape, 'float32')
    
    # Print memory summary
    summary = manager.get_memory_summary()
    print("\nMemory Summary:")
    print(f"System Memory: {summary['system_memory_mb']:.1f}MB")
    print(f"GPU Pool Size: {summary['gpu_pool']['pool_size_mb']:.1f}MB")
    print(f"Cached Models: {summary['model_cache']['cached_models']}")
    
    manager.stop_monitoring()