
import time
import threading
import psutil
from typing import Dict, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Performance optimization system"""
    
    def __init__(self):
        self.target_fps = 30.0
        self.frame_skip_threshold = 0.1  # Skip frames if behind by 10%
        self.optimization_enabled = True
        self.monitoring_enabled = True
        self.monitor_thread = None
        self._stop_monitoring = False
        
        # Performance metrics
        self.frame_times: List[float] = []
        self.frame_drops = 0
        self.avg_frame_time = 0.0
        self.last_frame_time = time.time()
        
    def start_monitoring(self):
        """Start performance monitoring"""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self._stop_monitoring = False
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("✅ Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self._stop_monitoring = True
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        logger.info("✅ Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Performance monitoring loop"""
        while not self._stop_monitoring:
            try:
                # Calculate current FPS
                current_time = time.time()
                frame_time = current_time - self.last_frame_time
                
                if frame_time > 0:
                    self.frame_times.append(frame_time)
                    
                    # Keep only recent frame times
                    if len(self.frame_times) > 100:
                        self.frame_times = self.frame_times[-50:]
                    
                    # Calculate average frame time
                    self.avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                    current_fps = 1.0 / self.avg_frame_time if self.avg_frame_time > 0 else 0
                    
                    # Check if we need to drop frames
                    if current_fps < self.target_fps * (1 - self.frame_skip_threshold):
                        self.frame_drops += 1
                        logger.warning(f"Performance issue detected: {current_fps:.1f} FPS, dropping frame")
                
                self.last_frame_time = current_time
                time.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                time.sleep(1.0)
    
    def should_skip_frame(self) -> bool:
        """Determine if current frame should be skipped"""
        if not self.optimization_enabled:
            return False
        
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        
        if frame_time > 0:
            current_fps = 1.0 / frame_time
            return current_fps < self.target_fps * (1 - self.frame_skip_threshold)
        
        return False
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        current_fps = 1.0 / self.avg_frame_time if self.avg_frame_time > 0 else 0
        
        return {
            'current_fps': current_fps,
            'target_fps': self.target_fps,
            'avg_frame_time': self.avg_frame_time,
            'frame_drops': self.frame_drops,
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent
        }
    
    def optimize_for_performance(self):
        """Apply performance optimizations"""
        logger.info("Applying performance optimizations...")
        
        # Reduce target FPS for better performance
        self.target_fps = 25.0
        self.frame_skip_threshold = 0.15
        
        # Force garbage collection
        import gc
        gc.collect()
        
        logger.info("✅ Performance optimizations applied")
    
    def optimize_for_quality(self):
        """Apply quality optimizations"""
        logger.info("Applying quality optimizations...")
        
        # Increase target FPS for better quality
        self.target_fps = 30.0
        self.frame_skip_threshold = 0.05
        
        logger.info("✅ Quality optimizations applied")

# Global performance optimizer instance
_performance_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the global performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer

def start_performance_monitoring():
    """Start performance monitoring"""
    get_performance_optimizer().start_monitoring()

def stop_performance_monitoring():
    """Stop performance monitoring"""
    get_performance_optimizer().stop_monitoring()
