#!/usr/bin/env python3
"""
Advanced FPS Optimization System for DeepFaceLive
Provides real-time FPS monitoring, adaptive quality adjustment, and performance tuning
"""

import time
import threading
import logging
import asyncio
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Tuple
from enum import Enum
import numpy as np
import weakref

@dataclass
class FPSMetrics:
    """FPS performance metrics"""
    timestamp: float
    current_fps: float
    target_fps: float
    frame_time_ms: float
    frame_drops: int
    processing_time_ms: float
    queue_size: int
    quality_level: float
    cpu_usage: float
    gpu_usage: float
    memory_usage_mb: float

class QualityLevel(Enum):
    """Quality level presets"""
    ULTRA_LOW = 0.1    # 10% quality for maximum performance
    LOW = 0.25         # 25% quality
    MEDIUM = 0.5       # 50% quality
    HIGH = 0.75        # 75% quality
    ULTRA_HIGH = 1.0   # 100% quality

class OptimizationStrategy(Enum):
    """FPS optimization strategies"""
    AGGRESSIVE = "aggressive"      # Maximum FPS, minimum quality
    BALANCED = "balanced"         # Balance FPS and quality
    CONSERVATIVE = "conservative"  # Maintain quality, optimize FPS
    ADAPTIVE = "adaptive"         # Dynamic adjustment based on performance

@dataclass
class OptimizationSettings:
    """FPS optimization settings"""
    target_fps: float = 30.0
    min_fps: float = 15.0
    max_fps: float = 60.0
    quality_adjustment_rate: float = 0.1
    frame_drop_threshold: int = 5
    processing_time_threshold_ms: float = 33.33  # 30 FPS target
    queue_size_threshold: int = 10
    auto_optimization: bool = True
    strategy: OptimizationStrategy = OptimizationStrategy.ADAPTIVE
    quality_level: QualityLevel = QualityLevel.MEDIUM

class AdaptiveQualityController:
    """Adaptive quality control system"""
    
    def __init__(self, settings: OptimizationSettings):
        self.settings = settings
        self.current_quality = settings.quality_level.value
        self.performance_history = deque(maxlen=60)  # 1 second at 60 FPS
        self.quality_history = deque(maxlen=30)
        self.adjustment_cooldown = 0.5  # Seconds between adjustments
        self.last_adjustment = time.time()
        self.logger = logging.getLogger(__name__)
        
    def update_performance(self, metrics: FPSMetrics) -> Optional[float]:
        """Update performance metrics and suggest quality adjustment"""
        self.performance_history.append(metrics)
        
        if len(self.performance_history) < 10:
            return None
            
        current_time = time.time()
        if current_time - self.last_adjustment < self.adjustment_cooldown:
            return None
            
        # Calculate performance trends
        recent_metrics = list(self.performance_history)[-10:]
        avg_fps = sum(m.current_fps for m in recent_metrics) / len(recent_metrics)
        avg_processing_time = sum(m.processing_time_ms for m in recent_metrics) / len(recent_metrics)
        avg_queue_size = sum(m.queue_size for m in recent_metrics) / len(recent_metrics)
        
        # Determine if adjustment is needed
        new_quality = self.current_quality
        
        if self.settings.strategy == OptimizationStrategy.AGGRESSIVE:
            new_quality = self._adjust_for_aggressive(avg_fps, avg_processing_time, avg_queue_size)
        elif self.settings.strategy == OptimizationStrategy.BALANCED:
            new_quality = self._adjust_for_balanced(avg_fps, avg_processing_time, avg_queue_size)
        elif self.settings.strategy == OptimizationStrategy.CONSERVATIVE:
            new_quality = self._adjust_for_conservative(avg_fps, avg_processing_time, avg_queue_size)
        elif self.settings.strategy == OptimizationStrategy.ADAPTIVE:
            new_quality = self._adjust_adaptive(avg_fps, avg_processing_time, avg_queue_size)
        
        if new_quality != self.current_quality:
            self.current_quality = new_quality
            self.last_adjustment = current_time
            self.quality_history.append(new_quality)
            self.logger.info(f"Quality adjusted to {new_quality:.2f} (FPS: {avg_fps:.1f})")
            return new_quality
            
        return None
    
    def _adjust_for_aggressive(self, avg_fps: float, avg_processing_time: float, avg_queue_size: float) -> float:
        """Aggressive optimization - prioritize FPS"""
        if avg_fps < self.settings.target_fps * 0.8 or avg_processing_time > self.settings.processing_time_threshold_ms:
            return max(0.1, self.current_quality - self.settings.quality_adjustment_rate * 2)
        elif avg_fps > self.settings.target_fps * 1.2 and avg_queue_size < 2:
            return min(1.0, self.current_quality + self.settings.quality_adjustment_rate)
        return self.current_quality
    
    def _adjust_for_balanced(self, avg_fps: float, avg_processing_time: float, avg_queue_size: float) -> float:
        """Balanced optimization"""
        if avg_fps < self.settings.target_fps * 0.9:
            return max(0.25, self.current_quality - self.settings.quality_adjustment_rate)
        elif avg_fps > self.settings.target_fps * 1.1 and avg_queue_size < 3:
            return min(1.0, self.current_quality + self.settings.quality_adjustment_rate * 0.5)
        return self.current_quality
    
    def _adjust_for_conservative(self, avg_fps: float, avg_processing_time: float, avg_queue_size: float) -> float:
        """Conservative optimization - maintain quality"""
        if avg_fps < self.settings.min_fps:
            return max(0.5, self.current_quality - self.settings.quality_adjustment_rate * 0.5)
        elif avg_fps > self.settings.target_fps * 1.3 and avg_queue_size < 1:
            return min(1.0, self.current_quality + self.settings.quality_adjustment_rate * 0.25)
        return self.current_quality
    
    def _adjust_adaptive(self, avg_fps: float, avg_processing_time: float, avg_queue_size: float) -> float:
        """Adaptive optimization based on multiple factors"""
        # Calculate performance score (0-1, higher is better)
        fps_score = min(1.0, avg_fps / self.settings.target_fps)
        processing_score = max(0.0, 1.0 - (avg_processing_time / self.settings.processing_time_threshold_ms))
        queue_score = max(0.0, 1.0 - (avg_queue_size / self.settings.queue_size_threshold))
        
        overall_score = (fps_score + processing_score + queue_score) / 3
        
        if overall_score < 0.6:  # Poor performance
            return max(0.1, self.current_quality - self.settings.quality_adjustment_rate)
        elif overall_score > 0.9:  # Excellent performance
            return min(1.0, self.current_quality + self.settings.quality_adjustment_rate * 0.5)
        
        return self.current_quality
    
    def get_quality_settings(self) -> Dict[str, Any]:
        """Get current quality settings for video processing"""
        return {
            'quality_factor': self.current_quality,
            'resolution_scale': max(0.5, self.current_quality),
            'processing_scale': self.current_quality,
            'skip_frames': max(0, int((1.0 - self.current_quality) * 3)),
            'compression_quality': int(self.current_quality * 100)
        }

class FPSOptimizer:
    """Main FPS optimization system"""
    
    def __init__(self, settings: OptimizationSettings = None):
        self.settings = settings or OptimizationSettings()
        self.quality_controller = AdaptiveQualityController(self.settings)
        
        # Performance tracking
        self.metrics_history = deque(maxlen=300)  # 10 seconds at 30 FPS
        self.frame_timestamps = deque(maxlen=60)
        self.processing_times = deque(maxlen=30)
        
        # State
        self.running = False
        self.monitoring = False
        self.frame_count = 0
        self.frame_drops = 0
        self.last_frame_time = time.time()
        
        # Callbacks
        self.on_quality_change: Optional[Callable[[float], None]] = None
        self.on_fps_warning: Optional[Callable[[float], None]] = None
        self.on_performance_alert: Optional[Callable[[str, Any], None]] = None
        
        # Threading
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Start FPS optimization"""
        if self.running:
            return
            
        self.running = True
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("FPS optimizer started")
    
    def stop(self):
        """Stop FPS optimization"""
        self.running = False
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        self.logger.info("FPS optimizer stopped")
    
    def record_frame(self, processing_start_time: float = None, queue_size: int = 0):
        """Record a frame for FPS calculation"""
        current_time = time.time()
        
        with self.lock:
            # Calculate frame time and FPS
            frame_time = current_time - self.last_frame_time
            fps = 1.0 / frame_time if frame_time > 0 else 0
            
            # Calculate processing time
            processing_time = 0
            if processing_start_time:
                processing_time = (current_time - processing_start_time) * 1000
            
            # Update tracking
            self.frame_timestamps.append(current_time)
            if processing_time > 0:
                self.processing_times.append(processing_time)
            
            # Calculate average FPS from recent frames
            if len(self.frame_timestamps) >= 2:
                recent_fps = len(self.frame_timestamps) / (self.frame_timestamps[-1] - self.frame_timestamps[0])
            else:
                recent_fps = fps
            
            # Create metrics
            metrics = FPSMetrics(
                timestamp=current_time,
                current_fps=recent_fps,
                target_fps=self.settings.target_fps,
                frame_time_ms=frame_time * 1000,
                frame_drops=self.frame_drops,
                processing_time_ms=processing_time,
                queue_size=queue_size,
                quality_level=self.quality_controller.current_quality,
                cpu_usage=self._get_cpu_usage(),
                gpu_usage=self._get_gpu_usage(),
                memory_usage_mb=self._get_memory_usage()
            )
            
            self.metrics_history.append(metrics)
            self.frame_count += 1
            self.last_frame_time = current_time
            
            # Check for frame drops
            if frame_time > (1.0 / self.settings.target_fps) * 1.5:
                self.frame_drops += 1
            
            # Update quality controller
            new_quality = self.quality_controller.update_performance(metrics)
            if new_quality is not None and self.on_quality_change:
                self.on_quality_change(new_quality)
            
            # Check for warnings
            if recent_fps < self.settings.min_fps and self.on_fps_warning:
                self.on_fps_warning(recent_fps)
    
    def get_current_fps(self) -> float:
        """Get current FPS"""
        with self.lock:
            if len(self.frame_timestamps) < 2:
                return 0.0
            return len(self.frame_timestamps) / (self.frame_timestamps[-1] - self.frame_timestamps[0])
    
    def get_metrics(self) -> FPSMetrics:
        """Get latest metrics"""
        with self.lock:
            return self.metrics_history[-1] if self.metrics_history else None
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        with self.lock:
            if not self.metrics_history:
                return {}
            
            recent_metrics = list(self.metrics_history)[-30:]  # Last 30 frames
            
            return {
                'current_fps': self.get_current_fps(),
                'target_fps': self.settings.target_fps,
                'avg_processing_time_ms': sum(m.processing_time_ms for m in recent_metrics) / len(recent_metrics),
                'frame_drops': self.frame_drops,
                'quality_level': self.quality_controller.current_quality,
                'queue_size': recent_metrics[-1].queue_size if recent_metrics else 0,
                'total_frames': self.frame_count,
                'uptime_seconds': time.time() - self.metrics_history[0].timestamp if self.metrics_history else 0
            }
    
    def set_target_fps(self, target_fps: float):
        """Set target FPS"""
        self.settings.target_fps = max(self.settings.min_fps, min(self.settings.max_fps, target_fps))
        self.quality_controller.settings.target_fps = self.settings.target_fps
        self.logger.info(f"Target FPS set to {target_fps}")
    
    def set_optimization_strategy(self, strategy: OptimizationStrategy):
        """Set optimization strategy"""
        self.settings.strategy = strategy
        self.quality_controller.settings.strategy = strategy
        self.logger.info(f"Optimization strategy set to {strategy.value}")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                # Check for performance issues
                metrics = self.get_metrics()
                if metrics:
                    if metrics.current_fps < self.settings.min_fps:
                        self.logger.warning(f"Low FPS detected: {metrics.current_fps:.1f}")
                    
                    if metrics.processing_time_ms > self.settings.processing_time_threshold_ms * 2:
                        self.logger.warning(f"High processing time: {metrics.processing_time_ms:.1f}ms")
                    
                    if metrics.queue_size > self.settings.queue_size_threshold:
                        self.logger.warning(f"Large queue size: {metrics.queue_size}")
                
                time.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(1.0)
    
    def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0
    
    def _get_gpu_usage(self) -> float:
        """Get GPU usage percentage"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].load * 100
        except ImportError:
            pass
        return 0.0
    
    def _get_memory_usage(self) -> float:
        """Get memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0

# Global FPS optimizer instance
_global_fps_optimizer: Optional[FPSOptimizer] = None

def get_fps_optimizer() -> FPSOptimizer:
    """Get global FPS optimizer instance"""
    global _global_fps_optimizer
    if _global_fps_optimizer is None:
        _global_fps_optimizer = FPSOptimizer()
    return _global_fps_optimizer

def start_fps_optimization(settings: OptimizationSettings = None):
    """Start global FPS optimization"""
    optimizer = get_fps_optimizer()
    if settings:
        optimizer.settings = settings
    optimizer.start()

def stop_fps_optimization():
    """Stop global FPS optimization"""
    global _global_fps_optimizer
    if _global_fps_optimizer:
        _global_fps_optimizer.stop()