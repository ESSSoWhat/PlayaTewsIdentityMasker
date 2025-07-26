#!/usr/bin/env python3
"""
Video Loopback System for DeepFaceLive
Provides fallback video sources when the merged feed stops
"""

import time
import threading
import logging
import asyncio
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import random
from collections import deque
import weakref

@dataclass
class LoopbackSource:
    """Loopback video source configuration"""
    name: str
    source_type: str
    path: Optional[Path] = None
    duration: float = 0.0
    loop: bool = True
    fade_in: float = 0.0
    fade_out: float = 0.0
    priority: int = 0
    enabled: bool = True

class SourceType(Enum):
    """Loopback source types"""
    VIDEO_FILE = "video_file"
    IMAGE_SEQUENCE = "image_sequence"
    STATIC_IMAGE = "static_image"
    COLOR_BARS = "color_bars"
    TEST_PATTERN = "test_pattern"
    CAMERA_FALLBACK = "camera_fallback"
    STREAM_FALLBACK = "stream_fallback"

class LoopbackMode(Enum):
    """Loopback operation modes"""
    DISABLED = "disabled"
    IMMEDIATE = "immediate"      # Switch immediately when feed stops
    DELAYED = "delayed"         # Wait before switching
    GRADUAL = "gradual"         # Gradual transition
    ROTATING = "rotating"       # Rotate through multiple sources

@dataclass
class LoopbackSettings:
    """Loopback system settings"""
    mode: LoopbackMode = LoopbackMode.IMMEDIATE
    detection_timeout: float = 2.0  # Seconds to wait before detecting feed loss
    transition_duration: float = 1.0  # Transition duration in seconds
    auto_recovery: bool = True  # Automatically recover when feed returns
    recovery_delay: float = 3.0  # Delay before attempting recovery
    max_sources: int = 10  # Maximum number of loopback sources
    default_source: str = "color_bars"  # Default fallback source

class VideoSource:
    """Base class for video sources"""
    
    def __init__(self, config: LoopbackSource):
        self.config = config
        self.current_frame = None
        self.start_time = time.time()
        self.frame_count = 0
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame from source"""
        return self.current_frame
    
    def update(self) -> bool:
        """Update source state, return True if frame changed"""
        return False
    
    def reset(self):
        """Reset source to beginning"""
        self.start_time = time.time()
        self.frame_count = 0

class VideoFileSource(VideoSource):
    """Video file source"""
    
    def __init__(self, config: LoopbackSource):
        super().__init__(config)
        self.cap = None
        self.fps = 30.0
        self.frame_delay = 1.0 / self.fps
        self.last_frame_time = 0
        
        if config.path and config.path.exists():
            self._initialize_video()
    
    def _initialize_video(self):
        """Initialize video capture"""
        try:
            self.cap = cv2.VideoCapture(str(self.config.path))
            if self.cap.isOpened():
                self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                if self.fps <= 0:
                    self.fps = 30.0
                self.frame_delay = 1.0 / self.fps
                self.logger.info(f"Video file loaded: {self.config.path}")
            else:
                self.logger.error(f"Failed to open video file: {self.config.path}")
        except Exception as e:
            self.logger.error(f"Error initializing video file: {e}")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame"""
        return self.current_frame
    
    def update(self) -> bool:
        """Update video frame"""
        if not self.cap or not self.cap.isOpened():
            return False
        
        current_time = time.time()
        if current_time - self.last_frame_time < self.frame_delay:
            return False
        
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            self.frame_count += 1
            self.last_frame_time = current_time
            
            # Check if video ended
            if self.frame_count >= self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                if self.config.loop:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.frame_count = 0
                else:
                    return False
            
            return True
        else:
            # Video ended
            if self.config.loop:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.frame_count = 0
            return False
    
    def reset(self):
        """Reset video to beginning"""
        super().reset()
        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    def __del__(self):
        """Cleanup"""
        if self.cap:
            self.cap.release()

class ImageSequenceSource(VideoSource):
    """Image sequence source"""
    
    def __init__(self, config: LoopbackSource):
        super().__init__(config)
        self.images = []
        self.current_index = 0
        self.frame_delay = 1.0 / 30.0  # 30 FPS default
        self.last_frame_time = 0
        
        if config.path and config.path.exists():
            self._load_images()
    
    def _load_images(self):
        """Load images from directory"""
        try:
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            if self.config.path.is_dir():
                for ext in image_extensions:
                    self.images.extend(list(self.config.path.glob(f"*{ext}")))
                    self.images.extend(list(self.config.path.glob(f"*{ext.upper()}")))
            
            # Sort images by name
            self.images.sort()
            
            if self.images:
                self.logger.info(f"Loaded {len(self.images)} images from {self.config.path}")
            else:
                self.logger.warning(f"No images found in {self.config.path}")
        except Exception as e:
            self.logger.error(f"Error loading images: {e}")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame"""
        return self.current_frame
    
    def update(self) -> bool:
        """Update image frame"""
        if not self.images:
            return False
        
        current_time = time.time()
        if current_time - self.last_frame_time < self.frame_delay:
            return False
        
        try:
            image_path = self.images[self.current_index]
            frame = cv2.imread(str(image_path))
            if frame is not None:
                self.current_frame = frame
                self.frame_count += 1
                self.last_frame_time = current_time
                
                # Move to next image
                self.current_index += 1
                if self.current_index >= len(self.images):
                    if self.config.loop:
                        self.current_index = 0
                    else:
                        return False
                
                return True
        except Exception as e:
            self.logger.error(f"Error loading image: {e}")
        
        return False
    
    def reset(self):
        """Reset to first image"""
        super().reset()
        self.current_index = 0

class StaticImageSource(VideoSource):
    """Static image source"""
    
    def __init__(self, config: LoopbackSource):
        super().__init__(config)
        if config.path and config.path.exists():
            self._load_image()
    
    def _load_image(self):
        """Load static image"""
        try:
            self.current_frame = cv2.imread(str(self.config.path))
            if self.current_frame is not None:
                self.logger.info(f"Static image loaded: {self.config.path}")
            else:
                self.logger.error(f"Failed to load image: {self.config.path}")
        except Exception as e:
            self.logger.error(f"Error loading static image: {e}")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get static frame"""
        return self.current_frame

class ColorBarsSource(VideoSource):
    """Color bars test pattern source"""
    
    def __init__(self, config: LoopbackSource):
        super().__init__(config)
        self._generate_color_bars()
    
    def _generate_color_bars(self):
        """Generate color bars test pattern"""
        height, width = 720, 1280
        
        # Create color bars pattern
        bars = []
        colors = [
            (255, 255, 255),  # White
            (255, 255, 0),    # Yellow
            (0, 255, 255),    # Cyan
            (0, 255, 0),      # Green
            (255, 0, 255),    # Magenta
            (255, 0, 0),      # Red
            (0, 0, 255),      # Blue
            (0, 0, 0),        # Black
        ]
        
        bar_width = width // len(colors)
        for color in colors:
            bar = np.full((height, bar_width, 3), color, dtype=np.uint8)
            bars.append(bar)
        
        # Add remaining pixels to last bar
        remaining_width = width - (bar_width * len(colors))
        if remaining_width > 0:
            bars[-1] = np.concatenate([bars[-1], np.full((height, remaining_width, 3), colors[-1], dtype=np.uint8)], axis=1)
        
        self.current_frame = np.concatenate(bars, axis=1)
        self.logger.info("Color bars pattern generated")

class TestPatternSource(VideoSource):
    """Test pattern source with moving elements"""
    
    def __init__(self, config: LoopbackSource):
        super().__init__(config)
        self.height, self.width = 720, 1280
        self.animation_time = 0
        self._generate_base_pattern()
    
    def _generate_base_pattern(self):
        """Generate base test pattern"""
        # Create checkerboard pattern
        square_size = 40
        pattern = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        for y in range(0, self.height, square_size):
            for x in range(0, self.width, square_size):
                if (x // square_size + y // square_size) % 2 == 0:
                    pattern[y:y+square_size, x:x+square_size] = [128, 128, 128]
        
        self.base_pattern = pattern
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get animated test pattern"""
        return self.current_frame
    
    def update(self) -> bool:
        """Update animated pattern"""
        self.animation_time += 0.033  # 30 FPS
        
        # Create animated pattern
        frame = self.base_pattern.copy()
        
        # Add moving circle
        center_x = int(self.width // 2 + 100 * np.sin(self.animation_time))
        center_y = int(self.height // 2 + 50 * np.cos(self.animation_time * 0.5))
        cv2.circle(frame, (center_x, center_y), 30, (0, 255, 0), -1)
        
        # Add moving text
        text = f"TEST PATTERN {int(self.animation_time)}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, text, (50, 50), font, 1, (255, 255, 255), 2)
        
        self.current_frame = frame
        return True

class VideoLoopbackSystem:
    """Main video loopback system"""
    
    def __init__(self, settings: LoopbackSettings = None):
        self.settings = settings or LoopbackSettings()
        self.sources: Dict[str, VideoSource] = {}
        self.active_source: Optional[str] = None
        self.feed_detected = True
        self.feed_loss_time = 0
        self.transition_start_time = 0
        self.transition_progress = 0.0
        
        # State tracking
        self.running = False
        self.monitoring = False
        self.recovery_attempts = 0
        self.max_recovery_attempts = 5
        
        # Callbacks
        self.on_feed_loss: Optional[Callable[[], None]] = None
        self.on_feed_recovery: Optional[Callable[[], None]] = None
        self.on_source_change: Optional[Callable[[str], None]] = None
        
        # Threading
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize default sources
        self._initialize_default_sources()
    
    def _initialize_default_sources(self):
        """Initialize default loopback sources"""
        # Color bars
        color_bars_config = LoopbackSource(
            name="color_bars",
            source_type=SourceType.COLOR_BARS.value,
            priority=0
        )
        self.add_source(color_bars_config)
        
        # Test pattern
        test_pattern_config = LoopbackSource(
            name="test_pattern",
            source_type=SourceType.TEST_PATTERN.value,
            priority=1
        )
        self.add_source(test_pattern_config)
    
    def add_source(self, config: LoopbackSource) -> bool:
        """Add a loopback source"""
        try:
            if config.source_type == SourceType.VIDEO_FILE.value:
                source = VideoFileSource(config)
            elif config.source_type == SourceType.IMAGE_SEQUENCE.value:
                source = ImageSequenceSource(config)
            elif config.source_type == SourceType.STATIC_IMAGE.value:
                source = StaticImageSource(config)
            elif config.source_type == SourceType.COLOR_BARS.value:
                source = ColorBarsSource(config)
            elif config.source_type == SourceType.TEST_PATTERN.value:
                source = TestPatternSource(config)
            else:
                self.logger.error(f"Unknown source type: {config.source_type}")
                return False
            
            self.sources[config.name] = source
            self.logger.info(f"Added loopback source: {config.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding source {config.name}: {e}")
            return False
    
    def remove_source(self, name: str) -> bool:
        """Remove a loopback source"""
        if name in self.sources:
            del self.sources[name]
            if self.active_source == name:
                self.active_source = None
            self.logger.info(f"Removed loopback source: {name}")
            return True
        return False
    
    def start(self):
        """Start loopback system"""
        if self.running:
            return
        
        self.running = True
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Video loopback system started")
    
    def stop(self):
        """Stop loopback system"""
        self.running = False
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        self.logger.info("Video loopback system stopped")
    
    def feed_heartbeat(self):
        """Signal that main feed is active"""
        with self.lock:
            if not self.feed_detected:
                self.feed_detected = True
                self.feed_loss_time = 0
                self.recovery_attempts = 0
                self.logger.info("Main feed detected")
                
                if self.on_feed_recovery:
                    self.on_feed_recovery()
    
    def get_loopback_frame(self) -> Optional[np.ndarray]:
        """Get current loopback frame"""
        if not self.feed_detected and self.active_source:
            source = self.sources.get(self.active_source)
            if source:
                source.update()
                return source.get_frame()
        return None
    
    def is_loopback_active(self) -> bool:
        """Check if loopback is currently active"""
        return not self.feed_detected and self.active_source is not None
    
    def get_active_source_name(self) -> Optional[str]:
        """Get name of currently active source"""
        return self.active_source if self.is_loopback_active() else None
    
    def switch_source(self, source_name: str) -> bool:
        """Switch to a specific loopback source"""
        if source_name not in self.sources:
            self.logger.error(f"Source not found: {source_name}")
            return False
        
        with self.lock:
            old_source = self.active_source
            self.active_source = source_name
            
            # Reset the new source
            self.sources[source_name].reset()
            
            self.logger.info(f"Switched to loopback source: {source_name}")
            
            if self.on_source_change:
                self.on_source_change(source_name)
            
            return True
    
    def _detect_feed_loss(self):
        """Detect if main feed has been lost"""
        current_time = time.time()
        
        if not self.feed_detected:
            return
        
        # Check if feed has been lost for too long
        if current_time - self.feed_loss_time > self.settings.detection_timeout:
            self.feed_detected = False
            self.logger.warning("Main feed lost, activating loopback")
            
            # Activate loopback based on mode
            if self.settings.mode == LoopbackMode.IMMEDIATE:
                self._activate_loopback()
            elif self.settings.mode == LoopbackMode.DELAYED:
                self.transition_start_time = current_time
            elif self.settings.mode == LoopbackMode.GRADUAL:
                self.transition_start_time = current_time
                self.transition_progress = 0.0
            
            if self.on_feed_loss:
                self.on_feed_loss()
    
    def _activate_loopback(self):
        """Activate loopback system"""
        if self.settings.mode == LoopbackMode.ROTATING:
            # Rotate through available sources
            available_sources = [name for name, source in self.sources.items() if source.config.enabled]
            if available_sources:
                if self.active_source in available_sources:
                    current_index = available_sources.index(self.active_source)
                    next_index = (current_index + 1) % len(available_sources)
                    self.switch_source(available_sources[next_index])
                else:
                    self.switch_source(available_sources[0])
        else:
            # Use default source or highest priority source
            if self.settings.default_source in self.sources:
                self.switch_source(self.settings.default_source)
            else:
                # Find highest priority enabled source
                enabled_sources = [(name, source.config.priority) 
                                 for name, source in self.sources.items() 
                                 if source.config.enabled]
                if enabled_sources:
                    best_source = max(enabled_sources, key=lambda x: x[1])[0]
                    self.switch_source(best_source)
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                self._detect_feed_loss()
                
                # Handle transitions
                if not self.feed_detected and self.settings.mode in [LoopbackMode.DELAYED, LoopbackMode.GRADUAL]:
                    current_time = time.time()
                    if self.settings.mode == LoopbackMode.DELAYED:
                        if current_time - self.transition_start_time >= self.settings.transition_duration:
                            self._activate_loopback()
                    elif self.settings.mode == LoopbackMode.GRADUAL:
                        progress = (current_time - self.transition_start_time) / self.settings.transition_duration
                        if progress >= 1.0:
                            self._activate_loopback()
                        else:
                            self.transition_progress = progress
                
                time.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(1.0)
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            'running': self.running,
            'feed_detected': self.feed_detected,
            'active_source': self.active_source,
            'mode': self.settings.mode.value,
            'sources_count': len(self.sources),
            'recovery_attempts': self.recovery_attempts,
            'transition_progress': self.transition_progress
        }

# Global loopback system instance
_global_loopback_system: Optional[VideoLoopbackSystem] = None

def get_loopback_system() -> VideoLoopbackSystem:
    """Get global loopback system instance"""
    global _global_loopback_system
    if _global_loopback_system is None:
        _global_loopback_system = VideoLoopbackSystem()
    return _global_loopback_system

def start_loopback_system(settings: LoopbackSettings = None):
    """Start global loopback system"""
    system = get_loopback_system()
    if settings:
        system.settings = settings
    system.start()

def stop_loopback_system():
    """Stop global loopback system"""
    global _global_loopback_system
    if _global_loopback_system:
        _global_loopback_system.stop()