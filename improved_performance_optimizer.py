#!/usr/bin/env python3
"""
Improved Performance Optimizer
Addresses critical issues found in code analysis:
- Resource management
- Error handling
- Import optimization
- Threading improvements
"""

import asyncio
import logging
import threading
import time
import traceback
import weakref
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import functools

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    max_workers: int = 4
    buffer_size: int = 10
    enable_caching: bool = True
    cache_size_limit: int = 100
    enable_profiling: bool = False
    log_performance: bool = True
    async_processing: bool = True
    resource_pooling: bool = True


class ResourceManager:
    """Improved resource management with proper cleanup"""
    
    def __init__(self):
        self._resources: weakref.WeakSet = weakref.WeakSet()
        self._locks: Dict[str, threading.Lock] = {}
        self._cleanup_callbacks: List[Callable] = []
        self._thread_pool: Optional[ThreadPoolExecutor] = None
        
    def register_resource(self, resource: Any, cleanup_func: Optional[Callable] = None):
        """Register a resource for automatic cleanup"""
        self._resources.add(resource)
        if cleanup_func:
            self._cleanup_callbacks.append(lambda: cleanup_func(resource))
    
    def get_lock(self, name: str) -> threading.Lock:
        """Get a named lock, creating it if necessary"""
        if name not in self._locks:
            self._locks[name] = threading.Lock()
        return self._locks[name]
    
    @contextmanager
    def get_thread_pool(self, max_workers: int = 4):
        """Context manager for thread pool with automatic cleanup"""
        if self._thread_pool is None:
            self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        try:
            yield self._thread_pool
        finally:
            # Don't shutdown here as pool might be reused
            pass
    
    def cleanup_all(self):
        """Clean up all registered resources"""
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error during resource cleanup: {e}")
        
        if self._thread_pool:
            try:
                self._thread_pool.shutdown(wait=True)
            except Exception as e:
                logger.error(f"Error shutting down thread pool: {e}")
            finally:
                self._thread_pool = None
        
        self._cleanup_callbacks.clear()
        self._locks.clear()


class ErrorHandler:
    """Improved error handling with specific exception types"""
    
    @staticmethod
    def handle_io_error(operation: str):
        """Decorator for handling I/O operations"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except (IOError, OSError, FileNotFoundError, PermissionError) as e:
                    logger.error(f"I/O error in {operation}: {e}")
                    return None
                except Exception as e:
                    logger.error(f"Unexpected error in {operation}: {e}")
                    logger.debug(traceback.format_exc())
                    return None
            return wrapper
        return decorator
    
    @staticmethod
    def handle_network_error(operation: str):
        """Decorator for handling network operations"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, TimeoutError, OSError) as e:
                    logger.error(f"Network error in {operation}: {e}")
                    return None
                except Exception as e:
                    logger.error(f"Unexpected error in {operation}: {e}")
                    logger.debug(traceback.format_exc())
                    return None
            return wrapper
        return decorator
    
    @staticmethod
    def handle_processing_error(operation: str):
        """Decorator for handling processing operations"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except (ValueError, TypeError, AttributeError) as e:
                    logger.error(f"Processing error in {operation}: {e}")
                    return None
                except Exception as e:
                    logger.error(f"Unexpected error in {operation}: {e}")
                    logger.debug(traceback.format_exc())
                    return None
            return wrapper
        return decorator


class ImprovedCache:
    """Thread-safe LRU cache with proper cleanup"""
    
    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
        self._cache: Dict[Any, Any] = {}
        self._access_order: List[Any] = []
        self._lock = threading.RLock()
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get item from cache"""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._access_order.remove(key)
                self._access_order.append(key)
                return self._cache[key]
            return default
    
    def put(self, key: Any, value: Any):
        """Put item in cache"""
        with self._lock:
            if key in self._cache:
                # Update existing
                self._cache[key] = value
                self._access_order.remove(key)
                self._access_order.append(key)
            else:
                # Add new
                self._cache[key] = value
                self._access_order.append(key)
                
                # Evict if necessary
                while len(self._cache) > self.maxsize:
                    oldest_key = self._access_order.pop(0)
                    del self._cache[oldest_key]
    
    def clear(self):
        """Clear all cached items"""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        with self._lock:
            return len(self._cache)


class AsyncProcessor:
    """Improved async processor with better error handling"""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self._tasks: List[asyncio.Task] = []
        self._shutdown = False
        self._resource_manager = ResourceManager()
        
    async def process_async(self, func: Callable, *args, **kwargs) -> Any:
        """Process function asynchronously with error handling"""
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                # Run in thread pool for CPU-bound operations
                loop = asyncio.get_event_loop()
                with self._resource_manager.get_thread_pool(self.config.max_workers) as pool:
                    return await loop.run_in_executor(pool, func, *args, **kwargs)
        except asyncio.CancelledError:
            logger.info("Task was cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in async processing: {e}")
            logger.debug(traceback.format_exc())
            return None
    
    async def process_batch(self, tasks: List[tuple]) -> List[Any]:
        """Process multiple tasks in parallel"""
        if not tasks:
            return []
        
        try:
            coroutines = [
                self.process_async(func, *args, **kwargs)
                for func, args, kwargs in tasks
            ]
            
            results = await asyncio.gather(*coroutines, return_exceptions=True)
            
            # Filter out exceptions and log them
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Task {i} failed: {result}")
                    processed_results.append(None)
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            return [None] * len(tasks)
    
    def shutdown(self):
        """Shutdown the processor and clean up resources"""
        self._shutdown = True
        
        # Cancel all running tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
        
        # Clean up resources
        self._resource_manager.cleanup_all()


class PerformanceMonitor:
    """Improved performance monitoring with better metrics"""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self._metrics: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
        self._start_times: Dict[str, float] = {}
    
    @contextmanager
    def measure(self, operation: str):
        """Context manager for measuring operation performance"""
        start_time = time.time()
        self._start_times[operation] = start_time
        
        try:
            yield
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            with self._lock:
                if operation not in self._metrics:
                    self._metrics[operation] = []
                self._metrics[operation].append(duration)
                
                # Keep only recent measurements
                if len(self._metrics[operation]) > 100:
                    self._metrics[operation] = self._metrics[operation][-100:]
            
            if self.config.log_performance:
                logger.debug(f"Operation '{operation}' took {duration:.3f}s")
    
    def get_average_time(self, operation: str) -> Optional[float]:
        """Get average time for an operation"""
        with self._lock:
            times = self._metrics.get(operation, [])
            return sum(times) / len(times) if times else None
    
    def get_metrics_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary of all metrics"""
        with self._lock:
            summary = {}
            for operation, times in self._metrics.items():
                if times:
                    summary[operation] = {
                        'count': len(times),
                        'average': sum(times) / len(times),
                        'min': min(times),
                        'max': max(times),
                        'total': sum(times)
                    }
            return summary


class ImprovedPerformanceOptimizer:
    """Main performance optimizer with all improvements"""
    
    def __init__(self, config: Optional[PerformanceConfig] = None):
        self.config = config or PerformanceConfig()
        self.resource_manager = ResourceManager()
        self.cache = ImprovedCache(maxsize=self.config.cache_size_limit)
        self.async_processor = AsyncProcessor(self.config)
        self.monitor = PerformanceMonitor(self.config)
        self._initialized = False
    
    def initialize(self):
        """Initialize the optimizer"""
        if self._initialized:
            return
        
        logger.info("Initializing improved performance optimizer")
        
        # Register cleanup callback
        import atexit
        atexit.register(self.shutdown)
        
        self._initialized = True
        logger.info("Performance optimizer initialized successfully")
    
    @ErrorHandler.handle_processing_error("cache_operation")
    def cached_call(self, func: Callable, *args, cache_key: Optional[str] = None, **kwargs) -> Any:
        """Call function with caching"""
        if not self.config.enable_caching:
            return func(*args, **kwargs)
        
        # Generate cache key if not provided
        if cache_key is None:
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
        
        # Try to get from cache
        result = self.cache.get(cache_key)
        if result is not None:
            return result
        
        # Execute and cache result
        with self.monitor.measure(f"cached_call_{func.__name__}"):
            result = func(*args, **kwargs)
            if result is not None:
                self.cache.put(cache_key, result)
            return result
    
    async def async_call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function asynchronously"""
        return await self.async_processor.process_async(func, *args, **kwargs)
    
    async def batch_process(self, tasks: List[tuple]) -> List[Any]:
        """Process multiple tasks in batch"""
        return await self.async_processor.process_batch(tasks)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        return {
            'cache_stats': {
                'size': self.cache.size(),
                'max_size': self.cache.maxsize,
                'hit_rate': 'N/A'  # Could implement hit rate tracking
            },
            'timing_stats': self.monitor.get_metrics_summary(),
            'config': {
                'max_workers': self.config.max_workers,
                'buffer_size': self.config.buffer_size,
                'cache_enabled': self.config.enable_caching,
                'async_enabled': self.config.async_processing
            }
        }
    
    def shutdown(self):
        """Shutdown the optimizer and clean up all resources"""
        logger.info("Shutting down performance optimizer")
        
        try:
            self.async_processor.shutdown()
            self.cache.clear()
            self.resource_manager.cleanup_all()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        logger.info("Performance optimizer shutdown complete")


# Global optimizer instance
_global_optimizer: Optional[ImprovedPerformanceOptimizer] = None
_optimizer_lock = threading.Lock()


def get_performance_optimizer(config: Optional[PerformanceConfig] = None) -> ImprovedPerformanceOptimizer:
    """Get global performance optimizer instance"""
    global _global_optimizer
    
    with _optimizer_lock:
        if _global_optimizer is None:
            _global_optimizer = ImprovedPerformanceOptimizer(config)
            _global_optimizer.initialize()
        
        return _global_optimizer


def cleanup_performance_optimizer():
    """Clean up global performance optimizer"""
    global _global_optimizer
    
    with _optimizer_lock:
        if _global_optimizer is not None:
            _global_optimizer.shutdown()
            _global_optimizer = None


# Decorator utilities
def optimize_with_cache(cache_key: Optional[str] = None):
    """Decorator to optimize function with caching"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            optimizer = get_performance_optimizer()
            return optimizer.cached_call(func, *args, cache_key=cache_key, **kwargs)
        return wrapper
    return decorator


def optimize_async(func):
    """Decorator to make function run asynchronously"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        optimizer = get_performance_optimizer()
        return await optimizer.async_call(func, *args, **kwargs)
    return wrapper


def measure_performance(operation_name: Optional[str] = None):
    """Decorator to measure function performance"""
    def decorator(func):
        op_name = operation_name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            optimizer = get_performance_optimizer()
            with optimizer.monitor.measure(op_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator