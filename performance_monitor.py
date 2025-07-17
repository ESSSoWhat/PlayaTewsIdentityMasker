#!/usr/bin/env python3
"""
Performance Monitoring System for DeepFaceLive
Tracks startup time, FPS, memory usage, and GPU utilization
"""

import time
import psutil
import threading
from collections import deque
from dataclasses import dataclass
from typing import Dict, Optional, List
import json
import logging

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: float
    fps: float
    latency_ms: float
    memory_mb: float
    gpu_memory_mb: float
    gpu_utilization: float
    startup_time: float

class PerformanceMonitor:
    """Real-time performance monitoring for DeepFaceLive"""
    
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)
        self.start_time = time.time()
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.fps_history = deque(maxlen=30)  # Last 30 frames for FPS
        self.latency_history = deque(maxlen=10)  # Last 10 operations for latency
        
        # Performance tracking
        self.startup_completed = False
        self.startup_time = 0
        self.peak_memory = 0
        self.peak_gpu_memory = 0
        
        # Monitoring thread
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        self.logger = logging.getLogger(__name__)
    
    def start_monitoring(self, interval: float = 1.0):
        """Start continuous performance monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        self.logger.info("Performance monitoring stopped")
    
    def mark_startup_complete(self):
        """Mark application startup as complete"""
        if not self.startup_completed:
            self.startup_time = time.time() - self.start_time
            self.startup_completed = True
            self.logger.info(f"Startup completed in {self.startup_time:.2f} seconds")
    
    def record_frame_processing(self, processing_start_time: float):
        """Record frame processing metrics"""
        current_time = time.time()
        
        # Calculate FPS
        frame_time = current_time - self.last_frame_time
        fps = 1.0 / frame_time if frame_time > 0 else 0
        self.fps_history.append(fps)
        
        # Calculate latency
        latency_ms = (current_time - processing_start_time) * 1000
        self.latency_history.append(latency_ms)
        
        self.last_frame_time = current_time
        self.frame_count += 1
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics snapshot"""
        current_time = time.time()
        
        # Calculate averages
        avg_fps = sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0
        avg_latency = sum(self.latency_history) / len(self.latency_history) if self.latency_history else 0
        
        # Memory metrics
        memory_mb = self._get_memory_usage()
        gpu_memory_mb, gpu_utilization = self._get_gpu_metrics()
        
        # Update peaks
        self.peak_memory = max(self.peak_memory, memory_mb)
        self.peak_gpu_memory = max(self.peak_gpu_memory, gpu_memory_mb)
        
        return PerformanceMetrics(
            timestamp=current_time,
            fps=avg_fps,
            latency_ms=avg_latency,
            memory_mb=memory_mb,
            gpu_memory_mb=gpu_memory_mb,
            gpu_utilization=gpu_utilization,
            startup_time=self.startup_time
        )
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        current_metrics = self.get_current_metrics()
        
        return {
            'current': {
                'fps': round(current_metrics.fps, 1),
                'latency_ms': round(current_metrics.latency_ms, 1),
                'memory_mb': round(current_metrics.memory_mb, 1),
                'gpu_memory_mb': round(current_metrics.gpu_memory_mb, 1),
                'gpu_utilization': round(current_metrics.gpu_utilization, 1)
            },
            'peaks': {
                'memory_mb': round(self.peak_memory, 1),
                'gpu_memory_mb': round(self.peak_gpu_memory, 1)
            },
            'startup': {
                'time_seconds': round(self.startup_time, 2),
                'completed': self.startup_completed
            },
            'session': {
                'uptime_seconds': round(time.time() - self.start_time, 1),
                'total_frames': self.frame_count
            }
        }
    
    def export_metrics(self, filepath: str):
        """Export metrics history to JSON file"""
        metrics_data = {
            'summary': self.get_performance_summary(),
            'history': [
                {
                    'timestamp': m.timestamp,
                    'fps': m.fps,
                    'latency_ms': m.latency_ms,
                    'memory_mb': m.memory_mb,
                    'gpu_memory_mb': m.gpu_memory_mb,
                    'gpu_utilization': m.gpu_utilization
                }
                for m in self.metrics_history
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        self.logger.info(f"Performance metrics exported to {filepath}")
    
    def _monitoring_loop(self, interval: float):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                metrics = self.get_current_metrics()
                self.metrics_history.append(metrics)
                
                # Log warnings for poor performance
                if metrics.fps < 15 and self.startup_completed:
                    self.logger.warning(f"Low FPS detected: {metrics.fps:.1f}")
                
                if metrics.memory_mb > 2048:  # 2GB warning threshold
                    self.logger.warning(f"High memory usage: {metrics.memory_mb:.1f}MB")
                
                if metrics.latency_ms > 100:  # 100ms latency warning
                    self.logger.warning(f"High latency detected: {metrics.latency_ms:.1f}ms")
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
            
            time.sleep(interval)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0
    
    def _get_gpu_metrics(self) -> tuple:
        """Get GPU memory and utilization metrics"""
        if not GPU_AVAILABLE:
            return 0.0, 0.0
        
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Use first GPU
                memory_mb = gpu.memoryUsed
                utilization = gpu.load * 100
                return memory_mb, utilization
        except Exception:
            pass
        
        return 0.0, 0.0

class PerformanceOptimizer:
    """Automatic performance optimization based on metrics"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.optimization_rules = {
            'low_fps': {'threshold': 20, 'action': 'reduce_quality'},
            'high_memory': {'threshold': 3072, 'action': 'cleanup_memory'},  # 3GB
            'high_latency': {'threshold': 150, 'action': 'skip_frames'}  # 150ms
        }
        self.logger = logging.getLogger(__name__)
    
    def check_and_optimize(self) -> List[str]:
        """Check performance and apply optimizations"""
        metrics = self.monitor.get_current_metrics()
        applied_optimizations = []
        
        # Check FPS
        if metrics.fps < self.optimization_rules['low_fps']['threshold']:
            self._optimize_fps()
            applied_optimizations.append('fps_optimization')
        
        # Check memory
        if metrics.memory_mb > self.optimization_rules['high_memory']['threshold']:
            self._optimize_memory()
            applied_optimizations.append('memory_cleanup')
        
        # Check latency
        if metrics.latency_ms > self.optimization_rules['high_latency']['threshold']:
            self._optimize_latency()
            applied_optimizations.append('latency_optimization')
        
        return applied_optimizations
    
    def _optimize_fps(self):
        """Optimize for better FPS"""
        self.logger.info("Applying FPS optimization: reducing quality settings")
        # Implementation would reduce model complexity, resolution, etc.
    
    def _optimize_memory(self):
        """Optimize memory usage"""
        self.logger.info("Applying memory optimization: cleaning up caches")
        # Implementation would clear model caches, reduce buffers, etc.
    
    def _optimize_latency(self):
        """Optimize for lower latency"""
        self.logger.info("Applying latency optimization: enabling frame skipping")
        # Implementation would skip frames, reduce processing complexity, etc.

# Global performance monitor instance
_global_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor

def start_performance_monitoring(interval: float = 1.0):
    """Start global performance monitoring"""
    monitor = get_performance_monitor()
    monitor.start_monitoring(interval)

def stop_performance_monitoring():
    """Stop global performance monitoring"""
    global _global_monitor
    if _global_monitor:
        _global_monitor.stop_monitoring()

if __name__ == "__main__":
    # Test performance monitoring
    import random
    
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    print("Testing performance monitoring for 10 seconds...")
    
    # Simulate frame processing
    for i in range(100):
        start_time = time.time()
        time.sleep(random.uniform(0.05, 0.15))  # Simulate processing
        monitor.record_frame_processing(start_time)
        
        if i == 30:
            monitor.mark_startup_complete()
    
    # Print summary
    summary = monitor.get_performance_summary()
    print("\nPerformance Summary:")
    print(f"FPS: {summary['current']['fps']}")
    print(f"Latency: {summary['current']['latency_ms']}ms")
    print(f"Memory: {summary['current']['memory_mb']}MB")
    print(f"Startup: {summary['startup']['time_seconds']}s")
    
    monitor.stop_monitoring()