
import gc
import psutil
import threading
import time
from typing import Dict, List, Optional, Callable
import weakref

class EnhancedMemoryManager:
    """Enhanced memory management system"""
    
    def __init__(self):
        self.memory_threshold = 0.8  # 80% memory usage threshold
        self.cleanup_interval = 30.0  # 30 seconds
        self.monitoring_enabled = True
        self.cleanup_callbacks: List[Callable] = []
        self.monitor_thread = None
        self._stop_monitoring = False
        
    def start_monitoring(self):
        """Start memory monitoring"""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self._stop_monitoring = False
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("✅ Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self._stop_monitoring = True
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        logger.info("✅ Memory monitoring stopped")
    
    def _monitor_loop(self):
        """Memory monitoring loop"""
        while not self._stop_monitoring:
            try:
                memory_usage = psutil.virtual_memory().percent / 100.0
                
                if memory_usage > self.memory_threshold:
                    logger.warning(f"High memory usage detected: {memory_usage:.1%}")
                    self._perform_cleanup()
                
                time.sleep(self.cleanup_interval)
                
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                time.sleep(5.0)
    
    def _perform_cleanup(self):
        """Perform memory cleanup"""
        logger.info("Performing memory cleanup...")
        
        # Force garbage collection
        collected = gc.collect()
        logger.info(f"Garbage collection freed {collected} objects")
        
        # Call registered cleanup callbacks
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Cleanup callback error: {e}")
        
        # Clear weak references
        gc.collect()
    
    def register_cleanup_callback(self, callback: Callable):
        """Register a cleanup callback"""
        self.cleanup_callbacks.append(callback)
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        memory = psutil.virtual_memory()
        return {
            'total_mb': memory.total / (1024 * 1024),
            'available_mb': memory.available / (1024 * 1024),
            'used_mb': memory.used / (1024 * 1024),
            'percent': memory.percent
        }

# Global memory manager instance
_memory_manager = None

def get_memory_manager() -> EnhancedMemoryManager:
    """Get the global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = EnhancedMemoryManager()
    return _memory_manager

def start_memory_monitoring():
    """Start memory monitoring"""
    get_memory_manager().start_monitoring()

def stop_memory_monitoring():
    """Stop memory monitoring"""
    get_memory_manager().stop_monitoring()
