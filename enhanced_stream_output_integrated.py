#!/usr/bin/env python3
"""
Enhanced StreamOutput with Integrated FPS Optimization and Video Loopback
Combines performance monitoring, adaptive quality control, and fallback video sources
"""

import time
import threading
import logging
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import IntEnum
import json

# Import our optimization systems
try:
    from fps_optimizer import (
        FPSOptimizer, OptimizationSettings, OptimizationStrategy, 
        QualityLevel, get_fps_optimizer, start_fps_optimization
    )
    from video_loopback_system import (
        VideoLoopbackSystem, LoopbackSettings, LoopbackMode,
        LoopbackSource, SourceType, get_loopback_system, start_loopback_system
    )
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False

from xlib import cv as lib_cv
from xlib import logic as lib_logic
from xlib import os as lib_os
from xlib import time as lib_time
from xlib.image import ImageProcessor
from xlib.mp import csw as lib_csw
from xlib.streamer import FFMPEGStreamer

from .BackendBase import (BackendConnection, BackendDB, BackendHost,
                          BackendSignal, BackendWeakHeap, BackendWorker,
                          BackendWorkerState)

class SourceType(IntEnum):
    SOURCE_FRAME = 0
    ALIGNED_FACE = 1
    SWAPPED_FACE = 2
    MERGED_FRAME = 3
    MERGED_FRAME_OR_SOURCE_FRAME = 4
    SOURCE_N_MERGED_FRAME = 5
    SOURCE_N_MERGED_FRAME_OR_SOURCE_FRAME = 6
    ALIGNED_N_SWAPPED_FACE = 7

ViewModeNames = ['@StreamOutput.SourceType.SOURCE_FRAME',
                 '@StreamOutput.SourceType.ALIGNED_FACE',
                 '@StreamOutput.SourceType.SWAPPED_FACE',
                 '@StreamOutput.SourceType.MERGED_FRAME',
                 '@StreamOutput.SourceType.MERGED_FRAME_OR_SOURCE_FRAME',
                 '@StreamOutput.SourceType.SOURCE_N_MERGED_FRAME',
                 '@StreamOutput.SourceType.SOURCE_N_MERGED_FRAME_OR_SOURCE_FRAME',
                 '@StreamOutput.SourceType.ALIGNED_N_SWAPPED_FACE',
                 ]

@dataclass
class PerformanceConfig:
    """Performance configuration settings"""
    target_fps: float = 30.0
    min_fps: float = 15.0
    max_fps: float = 60.0
    optimization_strategy: str = "adaptive"
    quality_level: str = "medium"
    auto_optimization: bool = True
    loopback_enabled: bool = True
    loopback_timeout: float = 2.0
    loopback_mode: str = "immediate"

class EnhancedStreamOutput(BackendHost):
    """
    Enhanced streaming output with integrated FPS optimization and video loopback
    """
    def __init__(self, weak_heap : BackendWeakHeap,
                       reemit_frame_signal : BackendSignal,
                       bc_in : BackendConnection,
                       save_default_path : Path = None,
                       backend_db : BackendDB = None):

        super().__init__(backend_db=backend_db,
                         sheet_cls=Sheet,
                         worker_cls=EnhancedStreamOutputWorker,
                         worker_state_cls=WorkerState,
                         worker_start_args=[weak_heap, reemit_frame_signal, bc_in, save_default_path] )

    def get_control_sheet(self) -> 'Sheet.Host': return super().get_control_sheet()

class EnhancedStreamOutputWorker(BackendWorker):
    def get_state(self) -> 'WorkerState': return super().get_state()
    def get_control_sheet(self) -> 'Sheet.Worker': return super().get_control_sheet()

    def on_start(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal,
                       bc_in : BackendConnection,
                       save_default_path : Path):
        self.weak_heap = weak_heap
        self.reemit_frame_signal = reemit_frame_signal
        self.bc_in = bc_in
        self.save_default_path = save_default_path

        # Core components
        self.fps_counter = lib_time.FPSCounter()
        self.buffered_frames = lib_logic.DelayedBuffers()
        self.is_show_window = False
        self.prev_frame_num = -1

        self._wnd_name = 'DeepFaceLive Enhanced Output'
        self._wnd_showing = False
        self._streamer = FFMPEGStreamer()

        # Performance tracking
        self.last_frame_time = time.time()
        self.frame_processing_times = []
        self.quality_adjustments = []
        
        # Initialize optimization systems
        self._initialize_optimization_systems()

        lib_os.set_timer_resolution(1)

        state, cs = self.get_state(), self.get_control_sheet()

        # Setup control sheet callbacks
        cs.source_type.call_on_selected(self.on_cs_source_type)
        cs.show_hide_window.call_on_signal(self.on_cs_show_hide_window_signal)
        cs.aligned_face_id.call_on_number(self.on_cs_aligned_face_id)
        cs.target_delay.call_on_number(self.on_cs_target_delay)
        cs.save_sequence_path.call_on_paths(self.on_cs_save_sequence_path)
        cs.save_fill_frame_gap.call_on_flag(self.on_cs_save_fill_frame_gap)
        cs.is_streaming.call_on_flag(self.on_cs_is_streaming)
        cs.stream_addr.call_on_text(self.on_cs_stream_addr)
        cs.stream_port.call_on_number(self.on_cs_stream_port)
        
        # Enhanced controls
        cs.performance_monitoring.call_on_flag(self.on_cs_performance_monitoring)
        cs.auto_optimization.call_on_flag(self.on_cs_auto_optimization)
        cs.loopback_enabled.call_on_flag(self.on_cs_loopback_enabled)
        cs.quality_level.call_on_selected(self.on_cs_quality_level)
        cs.optimization_strategy.call_on_selected(self.on_cs_optimization_strategy)

        # Initialize UI controls
        self._initialize_ui_controls(state, cs)

    def _initialize_optimization_systems(self):
        """Initialize FPS optimization and loopback systems"""
        if not OPTIMIZATION_AVAILABLE:
            self.logger.warning("Optimization systems not available")
            return
        
        try:
            # Initialize FPS optimizer
            fps_settings = OptimizationSettings(
                target_fps=30.0,
                min_fps=15.0,
                max_fps=60.0,
                strategy=OptimizationStrategy.ADAPTIVE,
                quality_level=QualityLevel.MEDIUM,
                auto_optimization=True
            )
            
            self.fps_optimizer = get_fps_optimizer()
            self.fps_optimizer.settings = fps_settings
            
            # Set up callbacks
            self.fps_optimizer.on_quality_change = self._on_quality_change
            self.fps_optimizer.on_fps_warning = self._on_fps_warning
            
            # Initialize loopback system
            loopback_settings = LoopbackSettings(
                mode=LoopbackMode.IMMEDIATE,
                detection_timeout=2.0,
                transition_duration=1.0,
                auto_recovery=True,
                recovery_delay=3.0
            )
            
            self.loopback_system = get_loopback_system()
            self.loopback_system.settings = loopback_settings
            
            # Set up callbacks
            self.loopback_system.on_feed_loss = self._on_feed_loss
            self.loopback_system.on_feed_recovery = self._on_feed_recovery
            self.loopback_system.on_source_change = self._on_source_change
            
            # Start systems
            self.fps_optimizer.start()
            self.loopback_system.start()
            
            self.logger.info("Optimization systems initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize optimization systems: {e}")

    def _initialize_ui_controls(self, state, cs):
        """Initialize UI controls with current state"""
        # Source type
        cs.source_type.enable()
        cs.source_type.set_choices(SourceType, ViewModeNames, none_choice_name='@misc.menu_select')
        cs.source_type.select(state.source_type)

        # Target delay
        cs.target_delay.enable()
        cs.target_delay.set_config(lib_csw.Number.Config(min=0, max=5000, step=100, decimals=0, allow_instant_update=True))
        cs.target_delay.set_number(state.target_delay if state.target_delay is not None else 500)

        # FPS display
        cs.avg_fps.enable()
        cs.avg_fps.set_config(lib_csw.Number.Config(min=0, max=240, decimals=1, read_only=True))
        cs.avg_fps.set_number(0)

        # Window controls
        cs.show_hide_window.enable()
        self.hide_window()

        if state.is_showing_window is None:
            state.is_showing_window = False

        if state.is_showing_window:
            state.is_showing_window = not state.is_showing_window
            cs.show_hide_window.signal()

        # Recording controls
        cs.save_sequence_path.enable()
        cs.save_sequence_path.set_config(lib_csw.Paths.Config.Directory('Choose output sequence directory', directory_path=self.save_default_path))
        cs.save_sequence_path.set_paths(state.sequence_path)

        cs.save_fill_frame_gap.enable()
        cs.save_fill_frame_gap.set_flag(state.save_fill_frame_gap if state.save_fill_frame_gap is not None else True)

        # Streaming controls
        cs.is_streaming.enable()
        cs.is_streaming.set_flag(state.is_streaming if state.is_streaming is not None else False)

        cs.stream_addr.enable()
        cs.stream_addr.set_text(state.stream_addr if state.stream_addr is not None else '127.0.0.1')

        cs.stream_port.enable()
        cs.stream_port.set_config(lib_csw.Number.Config(min=1, max=9999, decimals=0, allow_instant_update=True))
        cs.stream_port.set_number(state.stream_port if state.stream_port is not None else 1234)

        # Enhanced controls
        cs.performance_monitoring.enable()
        cs.performance_monitoring.set_flag(state.performance_monitoring if state.performance_monitoring is not None else True)

        cs.auto_optimization.enable()
        cs.auto_optimization.set_flag(state.auto_optimization if state.auto_optimization is not None else True)

        cs.loopback_enabled.enable()
        cs.loopback_enabled.set_flag(state.loopback_enabled if state.loopback_enabled is not None else True)

        cs.quality_level.enable()
        quality_levels = ['ultra_low', 'low', 'medium', 'high', 'ultra_high']
        cs.quality_level.set_choices(quality_levels, quality_levels, none_choice_name='@misc.menu_select')
        cs.quality_level.select(state.quality_level if state.quality_level is not None else 'medium')

        cs.optimization_strategy.enable()
        strategies = ['aggressive', 'balanced', 'conservative', 'adaptive']
        cs.optimization_strategy.set_choices(strategies, strategies, none_choice_name='@misc.menu_select')
        cs.optimization_strategy.select(state.optimization_strategy if state.optimization_strategy is not None else 'adaptive')

    def on_stop(self):
        """Stop worker and cleanup"""
        if hasattr(self, '_streamer'):
            self._streamer.stop()
        
        # Stop optimization systems
        if OPTIMIZATION_AVAILABLE:
            if hasattr(self, 'fps_optimizer'):
                self.fps_optimizer.stop()
            if hasattr(self, 'loopback_system'):
                self.loopback_system.stop()

    def _on_quality_change(self, new_quality: float):
        """Handle quality level changes from FPS optimizer"""
        self.logger.info(f"Quality adjusted to {new_quality:.2f}")
        self.quality_adjustments.append({
            'timestamp': time.time(),
            'quality': new_quality
        })
        
        # Update UI if needed
        state, cs = self.get_state(), self.get_control_sheet()
        if hasattr(cs, 'current_quality'):
            cs.current_quality.set_number(new_quality)

    def _on_fps_warning(self, fps: float):
        """Handle FPS warnings"""
        self.logger.warning(f"Low FPS detected: {fps:.1f}")
        
        # Could trigger additional optimizations here
        if hasattr(self, 'loopback_system') and self.loopback_system.is_loopback_active():
            self.logger.info("Loopback is active, main feed may be struggling")

    def _on_feed_loss(self):
        """Handle main feed loss"""
        self.logger.warning("Main feed lost, loopback activated")
        
        # Update UI to show loopback status
        state, cs = self.get_state(), self.get_control_sheet()
        if hasattr(cs, 'loopback_status'):
            cs.loopback_status.set_text("ACTIVE")

    def _on_feed_recovery(self):
        """Handle main feed recovery"""
        self.logger.info("Main feed recovered")
        
        # Update UI to show normal status
        state, cs = self.get_state(), self.get_control_sheet()
        if hasattr(cs, 'loopback_status'):
            cs.loopback_status.set_text("NORMAL")

    def _on_source_change(self, source_name: str):
        """Handle loopback source changes"""
        self.logger.info(f"Loopback source changed to: {source_name}")
        
        # Update UI to show current source
        state, cs = self.get_state(), self.get_control_sheet()
        if hasattr(cs, 'current_loopback_source'):
            cs.current_loopback_source.set_text(source_name)

    def on_tick(self):
        """Main processing tick with enhanced features"""
        cs, state = self.get_state(), self.get_control_sheet()
        
        processing_start_time = time.time()
        
        # Read input data
        bcd = self.bc_in.read(timeout=0.005)
        if bcd is not None:
            bcd.assign_weak_heap(self.weak_heap)
            
            # Signal feed heartbeat to loopback system
            if OPTIMIZATION_AVAILABLE and hasattr(self, 'loopback_system'):
                self.loopback_system.feed_heartbeat()
            
            # Update FPS counter
            current_fps = self.fps_counter.step()
            cs.avg_fps.set_number(current_fps)
            
            # Record frame for FPS optimization
            if OPTIMIZATION_AVAILABLE and hasattr(self, 'fps_optimizer'):
                queue_size = self.buffered_frames.get_queue_size() if hasattr(self.buffered_frames, 'get_queue_size') else 0
                self.fps_optimizer.record_frame(processing_start_time, queue_size)

            # Frame number tracking
            prev_frame_num = self.prev_frame_num
            frame_num = self.prev_frame_num = bcd.get_frame_num()
            if frame_num < prev_frame_num:
                prev_frame_num = self.prev_frame_num = -1

            # Process frame based on source type
            view_image = self._process_frame(bcd, state)
            
            if view_image is not None:
                # Add to buffer
                self.buffered_frames.add_buffer(bcd.get_frame_timestamp(), view_image)
                
                # Save sequence if enabled
                if state.sequence_path is not None:
                    self._save_frame_to_sequence(view_image, frame_num, state)
                
                # Process buffered frame
                pr = self.buffered_frames.process()
                img = pr.new_data
                
                if img is not None:
                    # Streaming
                    if state.is_streaming:
                        img = ImageProcessor(view_image).to_uint8().get_image('HWC')
                        self._streamer.push_frame(img)
                    
                    # Display window
                    if state.is_showing_window:
                        cv2.imshow(self._wnd_name, img)
        else:
            # No input data - check if we should use loopback
            if OPTIMIZATION_AVAILABLE and hasattr(self, 'loopback_system') and state.loopback_enabled:
                loopback_frame = self.loopback_system.get_loopback_frame()
                if loopback_frame is not None:
                    # Use loopback frame
                    if state.is_showing_window:
                        cv2.imshow(self._wnd_name, loopback_frame)
                    
                    if state.is_streaming:
                        img = ImageProcessor(loopback_frame).to_uint8().get_image('HWC')
                        self._streamer.push_frame(img)

        # Handle window events
        if state.is_showing_window:
            cv2.waitKey(1)

    def _process_frame(self, bcd, state) -> Optional[np.ndarray]:
        """Process frame based on source type with enhanced features"""
        source_type = state.source_type
        view_image = None
        
        if source_type == SourceType.SOURCE_FRAME:
            view_image = bcd.get_image(bcd.get_frame_image_name())
        elif source_type in [SourceType.MERGED_FRAME, SourceType.MERGED_FRAME_OR_SOURCE_FRAME]:
            view_image = bcd.get_image(bcd.get_merged_image_name())
            if view_image is None and source_type == SourceType.MERGED_FRAME_OR_SOURCE_FRAME:
                view_image = bcd.get_image(bcd.get_frame_image_name())
        elif source_type == SourceType.ALIGNED_FACE:
            aligned_face_id = state.aligned_face_id
            for i, fsi in enumerate(bcd.get_face_swap_info_list()):
                if aligned_face_id == i:
                    view_image = bcd.get_image(fsi.face_align_image_name)
                    break
        elif source_type == SourceType.SWAPPED_FACE:
            for fsi in bcd.get_face_swap_info_list():
                view_image = bcd.get_image(fsi.face_swap_image_name)
                if view_image is not None:
                    break
        elif source_type in [SourceType.SOURCE_N_MERGED_FRAME, SourceType.SOURCE_N_MERGED_FRAME_OR_SOURCE_FRAME]:
            source_frame = bcd.get_image(bcd.get_frame_image_name())
            if source_frame is not None:
                source_frame = ImageProcessor(source_frame).to_ufloat32().get_image('HWC')
            
            merged_frame = bcd.get_image(bcd.get_merged_image_name())
            
            if merged_frame is None and source_type == SourceType.SOURCE_N_MERGED_FRAME_OR_SOURCE_FRAME:
                merged_frame = source_frame
            
            if source_frame is not None and merged_frame is not None:
                view_image = np.concatenate((source_frame, merged_frame), 1)
        elif source_type == SourceType.ALIGNED_N_SWAPPED_FACE:
            aligned_face_id = state.aligned_face_id
            aligned_face = None
            swapped_face = None
            
            for i, fsi in enumerate(bcd.get_face_swap_info_list()):
                if aligned_face_id == i:
                    aligned_face = bcd.get_image(fsi.face_align_image_name)
                    break
            
            for fsi in bcd.get_face_swap_info_list():
                swapped_face = bcd.get_image(fsi.face_swap_image_name)
                if swapped_face is not None:
                    break
            
            if aligned_face is not None and swapped_face is not None:
                view_image = np.concatenate((aligned_face, swapped_face), 1)
        
        # Apply quality adjustments if optimization is available
        if OPTIMIZATION_AVAILABLE and hasattr(self, 'fps_optimizer') and view_image is not None:
            quality_settings = self.fps_optimizer.quality_controller.get_quality_settings()
            view_image = self._apply_quality_settings(view_image, quality_settings)
        
        return view_image

    def _apply_quality_settings(self, image: np.ndarray, settings: Dict[str, Any]) -> np.ndarray:
        """Apply quality settings to image"""
        try:
            # Apply resolution scaling
            if settings.get('resolution_scale', 1.0) != 1.0:
                scale = settings['resolution_scale']
                new_height = int(image.shape[0] * scale)
                new_width = int(image.shape[1] * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            # Apply compression quality for streaming
            if settings.get('compression_quality', 100) != 100:
                # This would be applied during streaming, not here
                pass
            
            return image
        except Exception as e:
            self.logger.error(f"Error applying quality settings: {e}")
            return image

    def _save_frame_to_sequence(self, view_image: np.ndarray, frame_num: int, state):
        """Save frame to sequence with enhanced features"""
        try:
            img = ImageProcessor(view_image, copy=True).to_uint8().get_image('HWC')
            
            file_ext, cv_args = '.jpg', [int(cv2.IMWRITE_JPEG_QUALITY), 100]
            
            frame_diff = abs(frame_num - self.prev_frame_num) if state.save_fill_frame_gap else 1
            for i in range(frame_diff):
                n = frame_num - i
                filename = f'{n:06}'
                lib_cv.imwrite(state.sequence_path / (filename + file_ext), img, cv_args)
        except Exception as e:
            self.logger.error(f"Error saving frame to sequence: {e}")

    # Control sheet callbacks
    def on_cs_source_type(self, idx, source_type):
        state, cs = self.get_state(), self.get_control_sheet()
        if source_type in [SourceType.ALIGNED_FACE, SourceType.ALIGNED_N_SWAPPED_FACE]:
            cs.aligned_face_id.enable()
            cs.aligned_face_id.set_config(lib_csw.Number.Config(min=0, max=16, step=1, allow_instant_update=True))
            cs.aligned_face_id.set_number(state.aligned_face_id or 0)
        else:
            cs.aligned_face_id.disable()
        state.source_type = source_type
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_show_hide_window_signal(self):
        state, cs = self.get_state(), self.get_control_sheet()
        state.is_showing_window = not state.is_showing_window
        if state.is_showing_window:
            cv2.namedWindow(self._wnd_name)
        else:
            cv2.destroyAllWindows()
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_aligned_face_id(self, aligned_face_id):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.aligned_face_id.get_config()
        aligned_face_id = state.aligned_face_id = np.clip(aligned_face_id, cfg.min, cfg.max)
        cs.aligned_face_id.set_number(aligned_face_id)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_target_delay(self, target_delay):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.target_delay.get_config()
        target_delay = state.target_delay = int(np.clip(target_delay, cfg.min, cfg.max))
        self.buffered_frames.set_target_delay(target_delay / 1000.0)
        cs.target_delay.set_number(target_delay)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_save_sequence_path(self, paths: List[Path], prev_paths):
        state, cs = self.get_state(), self.get_control_sheet()
        cs.save_sequence_path_error.set_error(None)
        sequence_path = paths[0] if len(paths) != 0 else None

        if sequence_path is None or sequence_path.exists():
            state.sequence_path = sequence_path
            cs.save_sequence_path.set_paths(sequence_path, block_event=True)
        else:
            cs.save_sequence_path_error.set_error(f'{sequence_path} does not exist.')
            cs.save_sequence_path.set_paths(prev_paths, block_event=True)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_save_fill_frame_gap(self, save_fill_frame_gap):
        state, cs = self.get_state(), self.get_control_sheet()
        state.save_fill_frame_gap = save_fill_frame_gap
        self.save_state()

    def on_cs_is_streaming(self, is_streaming):
        state, cs = self.get_state(), self.get_control_sheet()
        state.is_streaming = is_streaming
        self.save_state()

    def on_cs_stream_addr(self, stream_addr):
        state, cs = self.get_state(), self.get_control_sheet()
        state.stream_addr = stream_addr
        self.save_state()
        self._streamer.set_addr_port(state.stream_addr, state.stream_port)

    def on_cs_stream_port(self, stream_port):
        state, cs = self.get_state(), self.get_control_sheet()
        state.stream_port = stream_port
        self.save_state()
        self._streamer.set_addr_port(state.stream_addr, state.stream_port)

    # Enhanced control callbacks
    def on_cs_performance_monitoring(self, performance_monitoring):
        state, cs = self.get_state(), self.get_control_sheet()
        state.performance_monitoring = performance_monitoring
        self.save_state()

    def on_cs_auto_optimization(self, auto_optimization):
        state, cs = self.get_state(), self.get_control_sheet()
        state.auto_optimization = auto_optimization
        
        if OPTIMIZATION_AVAILABLE and hasattr(self, 'fps_optimizer'):
            self.fps_optimizer.settings.auto_optimization = auto_optimization
        
        self.save_state()

    def on_cs_loopback_enabled(self, loopback_enabled):
        state, cs = self.get_state(), self.get_control_sheet()
        state.loopback_enabled = loopback_enabled
        self.save_state()

    def on_cs_quality_level(self, idx, quality_level):
        state, cs = self.get_state(), self.get_control_sheet()
        state.quality_level = quality_level
        
        if OPTIMIZATION_AVAILABLE and hasattr(self, 'fps_optimizer'):
            quality_map = {
                'ultra_low': QualityLevel.ULTRA_LOW,
                'low': QualityLevel.LOW,
                'medium': QualityLevel.MEDIUM,
                'high': QualityLevel.HIGH,
                'ultra_high': QualityLevel.ULTRA_HIGH
            }
            if quality_level in quality_map:
                self.fps_optimizer.settings.quality_level = quality_map[quality_level]
        
        self.save_state()

    def on_cs_optimization_strategy(self, idx, strategy):
        state, cs = self.get_state(), self.get_control_sheet()
        state.optimization_strategy = strategy
        
        if OPTIMIZATION_AVAILABLE and hasattr(self, 'fps_optimizer'):
            strategy_map = {
                'aggressive': OptimizationStrategy.AGGRESSIVE,
                'balanced': OptimizationStrategy.BALANCED,
                'conservative': OptimizationStrategy.CONSERVATIVE,
                'adaptive': OptimizationStrategy.ADAPTIVE
            }
            if strategy in strategy_map:
                self.fps_optimizer.set_optimization_strategy(strategy_map[strategy])
        
        self.save_state()

    def show_window(self):
        state, cs = self.get_state(), self.get_control_sheet()
        cv2.namedWindow(self._wnd_name)
        self._wnd_showing = True

    def hide_window(self):
        state, cs = self.get_state(), self.get_control_sheet()
        if self._wnd_showing:
            cv2.destroyAllWindows()
            self._wnd_showing = False

class Sheet:
    class Host(lib_csw.Sheet.Host):
        def __init__(self):
            super().__init__()
            # Standard controls
            self.source_type = lib_csw.DynamicSingleSwitch.Client()
            self.aligned_face_id = lib_csw.Number.Client()
            self.target_delay = lib_csw.Number.Client()
            self.avg_fps = lib_csw.Number.Client()
            self.show_hide_window = lib_csw.Signal.Client()
            self.save_sequence_path = lib_csw.Paths.Client()
            self.save_sequence_path_error = lib_csw.Error.Client()
            self.save_fill_frame_gap = lib_csw.Flag.Client()
            self.is_streaming = lib_csw.Flag.Client()
            self.stream_addr = lib_csw.Text.Client()
            self.stream_port = lib_csw.Number.Client()
            
            # Enhanced controls
            self.performance_monitoring = lib_csw.Flag.Client()
            self.auto_optimization = lib_csw.Flag.Client()
            self.loopback_enabled = lib_csw.Flag.Client()
            self.quality_level = lib_csw.DynamicSingleSwitch.Client()
            self.optimization_strategy = lib_csw.DynamicSingleSwitch.Client()
            self.current_quality = lib_csw.Number.Client()
            self.loopback_status = lib_csw.Text.Client()
            self.current_loopback_source = lib_csw.Text.Client()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            # Standard controls
            self.source_type = lib_csw.DynamicSingleSwitch.Host()
            self.aligned_face_id = lib_csw.Number.Host()
            self.target_delay = lib_csw.Number.Host()
            self.avg_fps = lib_csw.Number.Host()
            self.show_hide_window = lib_csw.Signal.Host()
            self.save_sequence_path = lib_csw.Paths.Host()
            self.save_sequence_path_error = lib_csw.Error.Host()
            self.save_fill_frame_gap = lib_csw.Flag.Host()
            self.is_streaming = lib_csw.Flag.Host()
            self.stream_addr = lib_csw.Text.Host()
            self.stream_port = lib_csw.Number.Host()
            
            # Enhanced controls
            self.performance_monitoring = lib_csw.Flag.Host()
            self.auto_optimization = lib_csw.Flag.Host()
            self.loopback_enabled = lib_csw.Flag.Host()
            self.quality_level = lib_csw.DynamicSingleSwitch.Host()
            self.optimization_strategy = lib_csw.DynamicSingleSwitch.Host()
            self.current_quality = lib_csw.Number.Host()
            self.loopback_status = lib_csw.Text.Host()
            self.current_loopback_source = lib_csw.Text.Host()

class WorkerState(BackendWorkerState):
    # Standard state
    source_type: SourceType = SourceType.SOURCE_FRAME
    is_showing_window: bool = None
    aligned_face_id: int = None
    target_delay: int = None
    sequence_path: Path = None
    save_fill_frame_gap: bool = None
    is_streaming: bool = None
    stream_addr: str = None
    stream_port: int = None
    
    # Enhanced state
    performance_monitoring: bool = None
    auto_optimization: bool = None
    loopback_enabled: bool = None
    quality_level: str = None
    optimization_strategy: str = None