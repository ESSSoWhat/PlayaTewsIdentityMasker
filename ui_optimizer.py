#!/usr/bin/env python3
"""
UI Optimization System for DeepFaceLive
Enhances UI rendering performance, widget efficiency, and user experience
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Callable, Any
from collections import deque
from dataclasses import dataclass
import weakref

try:
    from xlib import qt as qtx
    from xlib.qt.widgets.QXWidget import QXWidget
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

@dataclass
class UIMetrics:
    """UI performance metrics"""
    render_time_ms: float
    widget_count: int
    update_frequency: float
    memory_usage_mb: float
    frame_drops: int

class UIOptimizer:
    """UI performance optimization system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.render_cache: Dict[str, Any] = {}
        self.widget_pool: Dict[str, List[Any]] = {}
        self.update_schedulers: Dict[str, 'UpdateScheduler'] = {}
        self.metrics = UIMetrics(0, 0, 0, 0, 0)
        self.optimization_enabled = True
        
    def enable_optimizations(self):
        """Enable all UI optimizations"""
        self.optimization_enabled = True
        self.logger.info("UI optimizations enabled")
        
    def disable_optimizations(self):
        """Disable optimizations for debugging"""
        self.optimization_enabled = False
        self.logger.info("UI optimizations disabled")

class OptimizedWidget:
    """Mixin class for optimized widget behavior"""
    
    def __init__(self):
        self._render_cache = {}
        self._last_render_time = 0
        self._render_threshold_ms = 16.67  # 60 FPS
        self._dirty_regions = set()
        self._optimization_enabled = True
        
    def mark_dirty(self, region: str = "all"):
        """Mark a region as needing update"""
        if self._optimization_enabled:
            self._dirty_regions.add(region)
        
    def is_dirty(self, region: str = "all") -> bool:
        """Check if region needs update"""
        return region in self._dirty_regions or "all" in self._dirty_regions
        
    def clear_dirty(self, region: str = None):
        """Clear dirty markers"""
        if region:
            self._dirty_regions.discard(region)
        else:
            self._dirty_regions.clear()

class UpdateScheduler:
    """Intelligent UI update scheduling"""
    
    def __init__(self, target_fps: int = 60):
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.pending_updates: deque = deque()
        self.last_update = time.time()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
    def start(self):
        """Start the update scheduler"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._update_loop)
            self.thread.daemon = True
            self.thread.start()
            
    def stop(self):
        """Stop the update scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
            
    def schedule_update(self, widget, priority: int = 0):
        """Schedule a widget update"""
        self.pending_updates.append((priority, widget, time.time()))
        
    def _update_loop(self):
        """Main update loop"""
        while self.running:
            start_time = time.time()
            
            # Process pending updates
            if self.pending_updates:
                # Sort by priority
                updates = sorted(list(self.pending_updates))
                self.pending_updates.clear()
                
                for priority, widget, timestamp in updates:
                    try:
                        if hasattr(widget, 'optimized_update'):
                            widget.optimized_update()
                        elif hasattr(widget, 'update'):
                            widget.update()
                    except Exception as e:
                        logging.error(f"Error updating widget: {e}")
            
            # Maintain target FPS
            elapsed = time.time() - start_time
            sleep_time = max(0, self.frame_time - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

class RenderCache:
    """Intelligent rendering cache system"""
    
    def __init__(self, max_size_mb: int = 100):
        self.max_size = max_size_mb * 1024 * 1024
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, float] = {}
        self.cache_sizes: Dict[str, int] = {}
        self.total_size = 0
        
    def get(self, key: str) -> Optional[Any]:
        """Get cached render data"""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
        
    def set(self, key: str, data: Any, size_bytes: int):
        """Cache render data"""
        # Remove old data if cache is full
        while self.total_size + size_bytes > self.max_size and self.cache:
            self._evict_lru()
            
        self.cache[key] = data
        self.access_times[key] = time.time()
        self.cache_sizes[key] = size_bytes
        self.total_size += size_bytes
        
    def _evict_lru(self):
        """Evict least recently used item"""
        if not self.access_times:
            return
            
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.total_size -= self.cache_sizes.get(lru_key, 0)
        
        del self.cache[lru_key]
        del self.access_times[lru_key]
        del self.cache_sizes[lru_key]

class WidgetPool:
    """Object pooling for expensive widgets"""
    
    def __init__(self):
        self.pools: Dict[str, List[Any]] = {}
        self.active_widgets: Dict[str, List[Any]] = {}
        
    def get_widget(self, widget_type: str, factory_func: Callable = None) -> Any:
        """Get a widget from the pool or create new one"""
        pool = self.pools.get(widget_type, [])
        
        if pool:
            widget = pool.pop()
        elif factory_func:
            widget = factory_func()
        else:
            return None
            
        # Track active widgets
        if widget_type not in self.active_widgets:
            self.active_widgets[widget_type] = []
        self.active_widgets[widget_type].append(widget)
        
        return widget
        
    def return_widget(self, widget_type: str, widget: Any):
        """Return widget to pool"""
        if widget_type in self.active_widgets:
            try:
                self.active_widgets[widget_type].remove(widget)
            except ValueError:
                pass
                
        # Reset widget state
        if hasattr(widget, 'reset'):
            widget.reset()
            
        # Add to pool
        if widget_type not in self.pools:
            self.pools[widget_type] = []
        self.pools[widget_type].append(widget)

class PerformanceProfiler:
    """UI performance profiling"""
    
    def __init__(self):
        self.render_times: deque = deque(maxlen=100)
        self.update_times: deque = deque(maxlen=100)
        self.frame_drops = 0
        self.target_frame_time = 16.67  # 60 FPS
        
    def start_render(self) -> float:
        """Start render timing"""
        return time.time()
        
    def end_render(self, start_time: float):
        """End render timing"""
        render_time = (time.time() - start_time) * 1000
        self.render_times.append(render_time)
        
        if render_time > self.target_frame_time:
            self.frame_drops += 1
            
    def get_stats(self) -> Dict[str, float]:
        """Get performance statistics"""
        if not self.render_times:
            return {}
            
        return {
            'avg_render_time': sum(self.render_times) / len(self.render_times),
            'max_render_time': max(self.render_times),
            'min_render_time': min(self.render_times),
            'frame_drops': self.frame_drops,
            'effective_fps': 1000 / (sum(self.render_times) / len(self.render_times)) if self.render_times else 0
        }

# Global UI optimizer instance
_ui_optimizer = None

def get_ui_optimizer() -> UIOptimizer:
    """Get global UI optimizer instance"""
    global _ui_optimizer
    if _ui_optimizer is None:
        _ui_optimizer = UIOptimizer()
    return _ui_optimizer

def optimize_widget_rendering(widget_class):
    """Decorator to add rendering optimizations to widget classes"""
    
    class OptimizedWidgetWrapper(widget_class, OptimizedWidget):
        def __init__(self, *args, **kwargs):
            widget_class.__init__(self, *args, **kwargs)
            OptimizedWidget.__init__(self)
            self.profiler = PerformanceProfiler()
            
        def paintEvent(self, event):
            """Optimized paint event"""
            if not self._optimization_enabled:
                return super().paintEvent(event)
                
            # Check if update is needed
            current_time = time.time() * 1000
            if (current_time - self._last_render_time) < self._render_threshold_ms and not self._dirty_regions:
                return
                
            # Profile render time
            start_time = self.profiler.start_render()
            
            try:
                super().paintEvent(event)
                self._last_render_time = current_time
                self.clear_dirty()
            finally:
                self.profiler.end_render(start_time)
                
        def optimized_update(self):
            """Optimized update method"""
            if self.is_dirty():
                self.update()
    
    return OptimizedWidgetWrapper

# UI optimization utilities
def create_optimized_layout(orientation='vertical'):
    """Create an optimized layout"""
    if not QT_AVAILABLE:
        return None
        
    if orientation == 'vertical':
        layout = qtx.QXWidgetVBox()
    else:
        layout = qtx.QXWidgetHBox()
        
    # Apply optimizations
    if hasattr(layout, 'setSpacing'):
        layout.setSpacing(2)  # Reduce spacing for better performance
    if hasattr(layout, 'setContentsMargins'):
        layout.setContentsMargins(2, 2, 2, 2)  # Reduce margins
        
    return layout

def batch_update_widgets(widgets: List[Any]):
    """Batch update multiple widgets efficiently"""
    scheduler = get_ui_optimizer().update_schedulers.get('default')
    if not scheduler:
        scheduler = UpdateScheduler()
        scheduler.start()
        get_ui_optimizer().update_schedulers['default'] = scheduler
        
    for widget in widgets:
        scheduler.schedule_update(widget)

def enable_lazy_loading(widget):
    """Enable lazy loading for expensive widget operations"""
    original_show = widget.show
    widget._content_loaded = False
    
    def lazy_show():
        if not widget._content_loaded:
            if hasattr(widget, 'load_content'):
                widget.load_content()
            widget._content_loaded = True
        original_show()
    
    widget.show = lazy_show
    return widget

# Performance monitoring
def monitor_ui_performance():
    """Monitor and log UI performance metrics"""
    optimizer = get_ui_optimizer()
    
    def log_performance():
        logging.info(f"UI Performance: {optimizer.metrics}")
        
    # Schedule performance logging
    timer = threading.Timer(10.0, log_performance)
    timer.daemon = True
    timer.start()