#!/usr/bin/env python3
"""
Integrated Optimization System for DeepFaceLive
Combines UI, memory, and processing optimizations with intelligent auto-tuning
"""

import asyncio
import time
import logging
import threading
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import weakref

# Import our optimization modules
try:
    from ui_optimizer import get_ui_optimizer, UIOptimizer, optimize_widget_rendering
    from enhanced_memory_manager import get_enhanced_memory_manager, MemoryPriority
    from performance_monitor import get_performance_monitor
    OPTIMIZATION_MODULES_AVAILABLE = True
except ImportError:
    OPTIMIZATION_MODULES_AVAILABLE = False

# Define ProcessingMode and FrameSkipStrategy here to avoid circular imports
class ProcessingMode(Enum):
    """Processing mode options"""
    REALTIME = "realtime"      # Drop frames to maintain speed
    QUALITY = "quality"        # Process all frames, may queue
    BALANCED = "balanced"      # Adaptive between realtime and quality
    BATCH = "batch"           # Batch processing mode

class FrameSkipStrategy(Enum):
    """Frame skipping strategies"""
    DROP_OLDEST = "drop_oldest"       # Drop oldest frames in queue
    DROP_LOWEST_PRIORITY = "drop_low" # Drop lowest priority frames
    ADAPTIVE = "adaptive"             # Adaptive based on processing load
    NONE = "none"                     # Never drop frames

class OptimizationLevel(Enum):
    """Optimization intensity levels"""
    CONSERVATIVE = "conservative"  # Minimal optimizations, maximum compatibility
    BALANCED = "balanced"         # Balanced performance and stability
    AGGRESSIVE = "aggressive"     # Maximum performance optimizations
    CUSTOM = "custom"            # User-defined settings

class SystemProfile(Enum):
    """System capability profiles"""
    LOW_END = "low_end"         # Limited CPU/GPU, low memory
    MEDIUM = "medium"           # Moderate specs
    HIGH_END = "high_end"       # Powerful hardware
    WORKSTATION = "workstation" # Professional workstation
    AUTO = "auto"               # Auto-detect based on system specs

@dataclass
class OptimizationConfig:
    """Optimization configuration settings"""
    # UI Optimizations
    ui_render_caching: bool = True
    ui_update_batching: bool = True
    ui_lazy_loading: bool = True
    ui_target_fps: int = 60
    
    # Memory Optimizations
    gpu_memory_pool_size_mb: int = 2048
    model_cache_size_mb: int = 512
    memory_compression: bool = True
    auto_cleanup: bool = True
    
    # Processing Optimizations
    processing_workers: int = 4
    frame_buffer_size: int = 5
    processing_mode: ProcessingMode = ProcessingMode.BALANCED
    skip_strategy: FrameSkipStrategy = FrameSkipStrategy.ADAPTIVE
    target_processing_fps: float = 30.0
    
    # Auto-tuning
    auto_tuning_enabled: bool = True
    performance_monitoring: bool = True
    adaptive_quality: bool = True
    
    # System-specific
    optimization_level: OptimizationLevel = OptimizationLevel.BALANCED
    system_profile: SystemProfile = SystemProfile.AUTO

class PerformanceMetrics:
    """Centralized performance metrics"""
    
    def __init__(self):
        self.startup_time = 0.0
        self.avg_frame_time = 0.0
        self.ui_fps = 0.0
        self.processing_fps = 0.0
        self.memory_usage_mb = 0.0
        self.gpu_memory_usage_mb = 0.0
        self.cpu_utilization = 0.0
        self.gpu_utilization = 0.0
        self.frame_drops = 0
        self.cache_hit_rate = 0.0
        self.last_update = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

class AutoTuner:
    """Automatic performance tuning system"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.metrics_history: List[PerformanceMetrics] = []
        self.tuning_enabled = config.auto_tuning_enabled
        self.logger = logging.getLogger(__name__)
        
        # Performance targets
        self.target_fps = config.target_processing_fps
        self.target_memory_usage = 0.8  # 80% of available
        self.target_cpu_usage = 0.7     # 70% CPU utilization
        
        # Tuning parameters
        self.adjustment_threshold = 0.1  # 10% performance difference
        self.stability_window = 10      # Frames to consider for stability
        self.last_adjustment = time.time()
        self.min_adjustment_interval = 5.0  # 5 seconds between adjustments
        
    def analyze_performance(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Analyze current performance and suggest optimizations"""
        self.metrics_history.append(metrics)
        
        # Keep only recent history
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-50:]
        
        if len(self.metrics_history) < self.stability_window:
            return {}
        
        # Calculate trends
        recent_metrics = self.metrics_history[-self.stability_window:]
        
        suggestions = {}
        
        # Analyze FPS performance
        avg_fps = sum(m.processing_fps for m in recent_metrics) / len(recent_metrics)
        if avg_fps < self.target_fps * (1 - self.adjustment_threshold):
            suggestions['fps'] = self._suggest_fps_improvements(avg_fps, recent_metrics)
        
        # Analyze memory usage
        avg_memory = sum(m.memory_usage_mb for m in recent_metrics) / len(recent_metrics)
        if avg_memory > self.target_memory_usage * 1024:  # Convert to MB
            suggestions['memory'] = self._suggest_memory_optimizations(avg_memory, recent_metrics)
        
        # Analyze CPU usage
        avg_cpu = sum(m.cpu_utilization for m in recent_metrics) / len(recent_metrics)
        if avg_cpu > self.target_cpu_usage:
            suggestions['cpu'] = self._suggest_cpu_optimizations(avg_cpu, recent_metrics)
        
        return suggestions
    
    def _suggest_fps_improvements(self, current_fps: float, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Suggest FPS improvement strategies"""
        suggestions = {
            'issue': 'low_fps',
            'current_fps': current_fps,
            'target_fps': self.target_fps,
            'actions': []
        }
        
        # Check frame drops
        total_drops = sum(m.frame_drops for m in metrics)
        if total_drops > 0:
            suggestions['actions'].append({
                'action': 'increase_frame_dropping',
                'reason': f'{total_drops} frames dropped in recent history'
            })
        
        # Check processing mode
        suggestions['actions'].append({
            'action': 'switch_to_realtime_mode',
            'reason': 'Prioritize speed over quality'
        })
        
        # Check quality settings
        suggestions['actions'].append({
            'action': 'reduce_quality',
            'reason': 'Lower quality for better performance'
        })
        
        return suggestions
    
    def _suggest_memory_optimizations(self, current_memory: float, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Suggest memory optimization strategies"""
        suggestions = {
            'issue': 'high_memory_usage',
            'current_memory_mb': current_memory,
            'actions': []
        }
        
        suggestions['actions'].extend([
            {
                'action': 'enable_compression',
                'reason': 'Compress cached data to save memory'
            },
            {
                'action': 'reduce_cache_size',
                'reason': 'Decrease model cache size'
            },
            {
                'action': 'aggressive_cleanup',
                'reason': 'More frequent memory cleanup'
            }
        ])
        
        return suggestions
    
    def _suggest_cpu_optimizations(self, current_cpu: float, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Suggest CPU optimization strategies"""
        suggestions = {
            'issue': 'high_cpu_usage',
            'current_cpu': current_cpu,
            'actions': []
        }
        
        suggestions['actions'].extend([
            {
                'action': 'reduce_worker_threads',
                'reason': 'Decrease parallel processing threads'
            },
            {
                'action': 'increase_frame_skipping',
                'reason': 'Skip more frames to reduce CPU load'
            },
            {
                'action': 'optimize_ui_updates',
                'reason': 'Reduce UI update frequency'
            }
        ])
        
        return suggestions
    
    def apply_suggestions(self, suggestions: Dict[str, Any]) -> bool:
        """Apply optimization suggestions automatically"""
        if not self.tuning_enabled:
            return False
        
        current_time = time.time()
        if current_time - self.last_adjustment < self.min_adjustment_interval:
            return False
        
        applied_any = False
        
        for category, suggestion in suggestions.items():
            if category == 'fps':
                applied_any |= self._apply_fps_optimizations(suggestion)
            elif category == 'memory':
                applied_any |= self._apply_memory_optimizations(suggestion)
            elif category == 'cpu':
                applied_any |= self._apply_cpu_optimizations(suggestion)
        
        if applied_any:
            self.last_adjustment = current_time
            self.logger.info("Applied automatic optimizations")
        
        return applied_any
    
    def _apply_fps_optimizations(self, suggestion: Dict[str, Any]) -> bool:
        """Apply FPS optimization suggestions"""
        try:
            if OPTIMIZATION_MODULES_AVAILABLE:
                try:
                    from enhanced_async_processor import get_global_processor
                    processor = get_global_processor()
                    
                    for action in suggestion['actions']:
                        if action['action'] == 'switch_to_realtime_mode':
                            processor.set_processing_mode(ProcessingMode.REALTIME)
                            return True
                        elif action['action'] == 'increase_frame_dropping':
                            processor.set_skip_strategy(FrameSkipStrategy.ADAPTIVE)
                            return True
                except ImportError:
                    pass
            
        except Exception as e:
            self.logger.error(f"Failed to apply FPS optimizations: {e}")
        
        return False
    
    def _apply_memory_optimizations(self, suggestion: Dict[str, Any]) -> bool:
        """Apply memory optimization suggestions"""
        try:
            if OPTIMIZATION_MODULES_AVAILABLE:
                memory_manager = get_enhanced_memory_manager()
                
                for action in suggestion['actions']:
                    if action['action'] == 'enable_compression':
                        memory_manager.gpu_pool.enable_compression = True
                        return True
                    elif action['action'] == 'aggressive_cleanup':
                        memory_manager.gpu_pool._cleanup_expired_blocks(max_age_seconds=60)
                        return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply memory optimizations: {e}")
        
        return False
    
    def _apply_cpu_optimizations(self, suggestion: Dict[str, Any]) -> bool:
        """Apply CPU optimization suggestions"""
        try:
            if OPTIMIZATION_MODULES_AVAILABLE:
                ui_optimizer = get_ui_optimizer()
                
                for action in suggestion['actions']:
                    if action['action'] == 'optimize_ui_updates':
                        # Reduce UI update frequency
                        for scheduler in ui_optimizer.update_schedulers.values():
                            scheduler.target_fps = max(30, scheduler.target_fps - 10)
                        return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply CPU optimizations: {e}")
        
        return False

class IntegratedOptimizer:
    """Main integrated optimization system"""
    
    def __init__(self, config: OptimizationConfig = None):
        self.config = config or OptimizationConfig()
        self.metrics = PerformanceMetrics()
        self.auto_tuner = AutoTuner(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Component references
        self.ui_optimizer: Optional[UIOptimizer] = None
        self.memory_manager = None
        self.video_processor = None
        self.performance_monitor = None
        
        # State
        self.initialized = False
        self.monitoring_enabled = False
        self.optimization_active = False
        
        # Performance tracking
        self.startup_start_time = time.time()
        self.monitoring_thread: Optional[threading.Thread] = None
        
    def initialize(self):
        """Initialize all optimization components"""
        if self.initialized:
            return
        
        self.logger.info("Initializing integrated optimization system")
        
        try:
            if OPTIMIZATION_MODULES_AVAILABLE:
                # Initialize UI optimizer
                self.ui_optimizer = get_ui_optimizer()
                self.ui_optimizer.enable_optimizations()
                
                # Initialize memory manager
                self.memory_manager = get_enhanced_memory_manager()
                self.memory_manager.optimize_for_inference()
                
                # Initialize video processor
                try:
                    from enhanced_async_processor import get_global_processor
                    self.video_processor = get_global_processor()
                    self._configure_video_processor()
                except ImportError:
                    self.video_processor = None
                
                # Initialize performance monitor
                self.performance_monitor = get_performance_monitor()
                
                self.logger.info("All optimization modules initialized successfully")
            else:
                self.logger.warning("Optimization modules not available, using fallback mode")
            
            # Apply system profile optimizations
            self._apply_system_profile()
            
            self.initialized = True
            self.metrics.startup_time = time.time() - self.startup_start_time
            
        except Exception as e:
            self.logger.error(f"Failed to initialize optimization system: {e}")
    
    def start_optimization(self):
        """Start the optimization system"""
        if not self.initialized:
            self.initialize()
        
        if self.optimization_active:
            return
        
        self.optimization_active = True
        self.logger.info("Starting optimization system")
        
        # Start monitoring
        if self.config.performance_monitoring:
            self.start_monitoring()
        
        # Start auto-tuning
        if self.config.auto_tuning_enabled:
            self.auto_tuner.tuning_enabled = True
    
    def stop_optimization(self):
        """Stop the optimization system"""
        if not self.optimization_active:
            return
        
        self.optimization_active = False
        self.logger.info("Stopping optimization system")
        
        # Stop monitoring
        self.stop_monitoring()
        
        # Stop auto-tuning
        self.auto_tuner.tuning_enabled = False
    
    def start_monitoring(self):
        """Start performance monitoring"""
        if self.monitoring_enabled:
            return
        
        self.monitoring_enabled = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        if not self.monitoring_enabled:
            return
        
        self.monitoring_enabled = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
        self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_enabled:
            try:
                self._update_metrics()
                
                # Auto-tune if enabled
                if self.auto_tuner.tuning_enabled:
                    suggestions = self.auto_tuner.analyze_performance(self.metrics)
                    if suggestions:
                        self.auto_tuner.apply_suggestions(suggestions)
                
                time.sleep(1.0)  # Update every second
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
    
    def _update_metrics(self):
        """Update performance metrics"""
        try:
            # Update basic metrics
            self.metrics.last_update = time.time()
            
            if OPTIMIZATION_MODULES_AVAILABLE and self.performance_monitor:
                # Get metrics from performance monitor
                perf_stats = self.performance_monitor.get_current_metrics()
                if perf_stats:
                    self.metrics.avg_frame_time = perf_stats.latency_ms
                    self.metrics.memory_usage_mb = perf_stats.memory_mb
                    self.metrics.gpu_memory_usage_mb = perf_stats.gpu_memory_mb
            
            if self.video_processor:
                # Get processing stats
                proc_stats = self.video_processor.get_stats()
                self.metrics.processing_fps = proc_stats.effective_fps
                self.metrics.frame_drops = proc_stats.frames_dropped
            
            if self.memory_manager:
                # Get memory stats
                memory_stats = self.memory_manager.get_memory_stats()
                cache_hit_rate = memory_stats.get('model_cache', {}).get('hit_rate', 0.0)
                self.metrics.cache_hit_rate = cache_hit_rate
            
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")
    
    def _configure_video_processor(self):
        """Configure video processor based on config"""
        if not self.video_processor:
            return
        
        # Set processing mode
        self.video_processor.set_processing_mode(self.config.processing_mode)
        self.video_processor.set_skip_strategy(self.config.skip_strategy)
        self.video_processor.set_target_fps(self.config.target_processing_fps)
        
        # Configure buffer size
        self.video_processor.buffer_size = self.config.frame_buffer_size
    
    def _apply_system_profile(self):
        """Apply optimizations based on system profile"""
        if self.config.system_profile == SystemProfile.AUTO:
            # Auto-detect system capabilities
            detected_profile = self._detect_system_profile()
            self.config.system_profile = detected_profile
        
        profile = self.config.system_profile
        
        if profile == SystemProfile.LOW_END:
            self._apply_low_end_optimizations()
        elif profile == SystemProfile.MEDIUM:
            self._apply_medium_optimizations()
        elif profile == SystemProfile.HIGH_END:
            self._apply_high_end_optimizations()
        elif profile == SystemProfile.WORKSTATION:
            self._apply_workstation_optimizations()
        
        self.logger.info(f"Applied optimizations for {profile.value} system profile")
    
    def _detect_system_profile(self) -> SystemProfile:
        """Detect system capabilities automatically"""
        try:
            import psutil
            
            # Get system specs
            cpu_count = psutil.cpu_count()
            memory_gb = psutil.virtual_memory().total / (1024**3)
            
            # Simple heuristic for system classification
            if cpu_count >= 16 and memory_gb >= 32:
                return SystemProfile.WORKSTATION
            elif cpu_count >= 8 and memory_gb >= 16:
                return SystemProfile.HIGH_END
            elif cpu_count >= 4 and memory_gb >= 8:
                return SystemProfile.MEDIUM
            else:
                return SystemProfile.LOW_END
                
        except ImportError:
            return SystemProfile.MEDIUM  # Default fallback
    
    def _apply_low_end_optimizations(self):
        """Apply optimizations for low-end systems"""
        self.config.processing_workers = 2
        self.config.frame_buffer_size = 2
        self.config.gpu_memory_pool_size_mb = 512
        self.config.model_cache_size_mb = 256
        self.config.processing_mode = ProcessingMode.REALTIME
        self.config.ui_target_fps = 30
    
    def _apply_medium_optimizations(self):
        """Apply optimizations for medium systems"""
        self.config.processing_workers = 4
        self.config.frame_buffer_size = 3
        self.config.gpu_memory_pool_size_mb = 1024
        self.config.model_cache_size_mb = 512
        self.config.processing_mode = ProcessingMode.BALANCED
        self.config.ui_target_fps = 45
    
    def _apply_high_end_optimizations(self):
        """Apply optimizations for high-end systems"""
        self.config.processing_workers = 6
        self.config.frame_buffer_size = 5
        self.config.gpu_memory_pool_size_mb = 2048
        self.config.model_cache_size_mb = 1024
        self.config.processing_mode = ProcessingMode.BALANCED
        self.config.ui_target_fps = 60
    
    def _apply_workstation_optimizations(self):
        """Apply optimizations for workstation systems"""
        self.config.processing_workers = 8
        self.config.frame_buffer_size = 8
        self.config.gpu_memory_pool_size_mb = 4096
        self.config.model_cache_size_mb = 2048
        self.config.processing_mode = ProcessingMode.QUALITY
        self.config.ui_target_fps = 60
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        return self.metrics
    
    def get_config(self) -> OptimizationConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, new_config: OptimizationConfig):
        """Update configuration"""
        self.config = new_config
        
        # Reconfigure components
        if self.initialized:
            self._configure_video_processor()
            self._apply_system_profile()
    
    def save_config(self, filepath: str):
        """Save configuration to file"""
        try:
            config_dict = asdict(self.config)
            # Convert enums to strings
            config_dict['optimization_level'] = self.config.optimization_level.value
            config_dict['system_profile'] = self.config.system_profile.value
            config_dict['processing_mode'] = self.config.processing_mode.value
            config_dict['skip_strategy'] = self.config.skip_strategy.value
            
            with open(filepath, 'w') as f:
                json.dump(config_dict, f, indent=2)
                
            self.logger.info(f"Configuration saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def load_config(self, filepath: str) -> bool:
        """Load configuration from file"""
        try:
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
            
            # Convert string enums back
            config_dict['optimization_level'] = OptimizationLevel(config_dict['optimization_level'])
            config_dict['system_profile'] = SystemProfile(config_dict['system_profile'])
            config_dict['processing_mode'] = ProcessingMode(config_dict['processing_mode'])
            config_dict['skip_strategy'] = FrameSkipStrategy(config_dict['skip_strategy'])
            
            self.config = OptimizationConfig(**config_dict)
            self.logger.info(f"Configuration loaded from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False

# Global optimizer instance
_global_optimizer = None

def get_integrated_optimizer() -> IntegratedOptimizer:
    """Get global integrated optimizer instance"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = IntegratedOptimizer()
    return _global_optimizer

def initialize_optimizations(config: OptimizationConfig = None):
    """Initialize and start the integrated optimization system"""
    optimizer = get_integrated_optimizer()
    if config:
        optimizer.update_config(config)
    optimizer.initialize()
    optimizer.start_optimization()
    return optimizer

def optimize_for_performance():
    """Quick setup for maximum performance"""
    config = OptimizationConfig(
        optimization_level=OptimizationLevel.AGGRESSIVE,
        processing_mode=ProcessingMode.REALTIME,
        skip_strategy=FrameSkipStrategy.ADAPTIVE,
        memory_compression=True,
        auto_tuning_enabled=True
    )
    return initialize_optimizations(config)

def optimize_for_quality():
    """Quick setup for maximum quality"""
    config = OptimizationConfig(
        optimization_level=OptimizationLevel.CONSERVATIVE,
        processing_mode=ProcessingMode.QUALITY,
        skip_strategy=FrameSkipStrategy.NONE,
        memory_compression=False,
        auto_tuning_enabled=False
    )
    return initialize_optimizations(config)