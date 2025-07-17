from localization import L
from resources.fonts import QXFontDB
from xlib import qt as qtx
import numpy as np
import time
from typing import Optional, Dict, Any

from ... import backend


class QOptimizedFrameViewer(qtx.QXCollapsibleSection):
    """Optimized frame viewer with reduced redraws and memory-efficient rendering"""
    
    def __init__(self, backed_weak_heap: backend.BackendWeakHeap,
                 bc: backend.BackendConnection,
                 preview_width=256,
                 update_interval_ms=33):  # ~30 FPS instead of 60 FPS
        self._timer = qtx.QXTimer(interval=update_interval_ms, timeout=self._on_timer_update, start=True)
        
        self._backed_weak_heap = backed_weak_heap
        self._bc = bc
        self._bcd_id = None
        
        # Performance optimization flags
        self._is_visible = True
        self._is_minimized = False
        self._last_update_time = 0
        self._min_update_interval = 1.0 / 30.0  # Max 30 FPS
        
        # Memory optimization
        self._cached_image = None
        self._cached_image_hash = None
        self._frame_skip_counter = 0
        self._max_frame_skip = 2  # Skip every 2nd frame if needed
        
        # Layered images with optimization
        self._layered_images = qtx.QXFixedLayeredImages(preview_width, preview_width)
        self._info_label = qtx.QXLabel(font=QXFontDB.get_fixedwidth_font(size=7))
        
        # Performance metrics
        self._update_count = 0
        self._skip_count = 0
        self._last_performance_log = time.time()
        
        main_l = qtx.QXVBoxLayout([
            (self._layered_images, qtx.AlignCenter),
            (self._info_label, qtx.AlignCenter),
        ])
        super().__init__(title=L('@QBCFrameViewer.title'), content_layout=main_l)
        
        # Connect visibility signals
        self.visibilityChanged.connect(self._on_visibility_changed)
    
    def _on_visibility_changed(self, visible: bool):
        """Handle visibility changes to optimize updates"""
        self._is_visible = visible
        if not visible:
            self._clear_cached_data()
    
    def _clear_cached_data(self):
        """Clear cached data to free memory"""
        self._cached_image = None
        self._cached_image_hash = None
        self._layered_images.clear_images()
    
    def _on_timer_update(self):
        """Optimized timer callback with performance checks"""
        current_time = time.time()
        
        # Check if we should skip this update
        if not self._should_update(current_time):
            self._skip_count += 1
            return
        
        # Get window state
        top_qx = self.get_top_QXWindow()
        if top_qx is not None:
            self._is_minimized = top_qx.is_minimized()
        
        if not self.is_opened() or not self._is_visible or self._is_minimized:
            return
        
        # Check for new data
        bcd_id = self._bc.get_write_id()
        if self._bcd_id != bcd_id:
            self._update_frame(bcd_id, current_time)
        
        # Log performance metrics periodically
        if current_time - self._last_performance_log > 10.0:  # Every 10 seconds
            self._log_performance_metrics()
            self._last_performance_log = current_time
    
    def _should_update(self, current_time: float) -> bool:
        """Determine if we should perform an update based on performance metrics"""
        # Enforce minimum update interval
        if current_time - self._last_update_time < self._min_update_interval:
            return False
        
        # Frame skipping logic for performance
        self._frame_skip_counter += 1
        if self._frame_skip_counter % (self._max_frame_skip + 1) == 0:
            return False
        
        return True
    
    def _update_frame(self, bcd_id: int, current_time: float):
        """Update frame with optimized rendering"""
        try:
            # Get new data
            bcd, self._bcd_id = self._bc.get_by_id(bcd_id), bcd_id
            
            if bcd is not None:
                bcd.assign_weak_heap(self._backed_weak_heap)
                
                frame_image_name = bcd.get_frame_image_name()
                frame_image = bcd.get_image(frame_image_name)
                
                if frame_image is not None:
                    # Check if image has changed (simple hash-based check)
                    image_hash = self._calculate_image_hash(frame_image)
                    
                    if image_hash != self._cached_image_hash:
                        # Only update if image actually changed
                        self._update_display(frame_image, frame_image_name)
                        self._cached_image_hash = image_hash
                        self._cached_image = frame_image.copy()
                
                self._last_update_time = current_time
                self._update_count += 1
                
        except Exception as e:
            # Log error but don't crash
            print(f"Frame update error: {e}")
    
    def _calculate_image_hash(self, image: np.ndarray) -> int:
        """Calculate a simple hash for image change detection"""
        if image is None:
            return 0
        
        # Use shape and a sample of pixels for quick hash
        try:
            # Sample every 10th pixel for performance
            sample = image[::10, ::10]
            return hash((image.shape, sample.tobytes()[:100]))  # First 100 bytes
        except:
            return hash(str(image.shape))
    
    def _update_display(self, frame_image: np.ndarray, frame_image_name: str):
        """Update the display with new frame data"""
        # Clear and add new image
        self._layered_images.clear_images()
        self._layered_images.add_image(frame_image)
        
        # Update info label
        h, w = frame_image.shape[:2]
        self._info_label.setText(f'{frame_image_name} {w}x{h}')
    
    def _log_performance_metrics(self):
        """Log performance metrics for monitoring"""
        total_updates = self._update_count + self._skip_count
        if total_updates > 0:
            skip_rate = (self._skip_count / total_updates) * 100
            print(f"FrameViewer Performance: {self._update_count} updates, {self._skip_count} skips ({skip_rate:.1f}% skip rate)")
    
    def clear(self):
        """Clear the viewer and cached data"""
        self._clear_cached_data()
    
    def set_update_interval(self, interval_ms: int):
        """Dynamically adjust update interval for performance"""
        self._timer.setInterval(interval_ms)
        self._min_update_interval = interval_ms / 1000.0
    
    def set_frame_skip(self, max_skip: int):
        """Set maximum frame skip for performance tuning"""
        self._max_frame_skip = max(0, max_skip)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        return {
            'update_count': self._update_count,
            'skip_count': self._skip_count,
            'skip_rate': (self._skip_count / (self._update_count + self._skip_count)) * 100 if (self._update_count + self._skip_count) > 0 else 0,
            'is_visible': self._is_visible,
            'is_minimized': self._is_minimized
        }