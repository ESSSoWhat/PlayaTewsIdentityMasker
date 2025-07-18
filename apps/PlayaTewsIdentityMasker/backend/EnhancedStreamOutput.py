from enum import IntEnum
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import cv2
import numpy as np
import json
import time
import threading
from datetime import datetime

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


class StreamingPlatform(IntEnum):
    TWITCH = 0
    YOUTUBE = 1
    FACEBOOK = 2
    CUSTOM_RTMP = 3
    MULTI_PLATFORM = 4


class RecordingFormat(IntEnum):
    MP4 = 0
    MKV = 1
    AVI = 2
    MOV = 3


class Scene:
    """Represents a scene with multiple sources"""
    def __init__(self, name: str):
        self.name = name
        self.sources = []
        self.active = True
        
    def add_source(self, source):
        self.sources.append(source)
        
    def remove_source(self, source):
        if source in self.sources:
            self.sources.remove(source)
            
    def get_active_sources(self):
        return [s for s in self.sources if s.active]


class Source:
    """Base class for all sources"""
    def __init__(self, name: str, source_type: str):
        self.name = name
        self.source_type = source_type
        self.active = True
        self.visible = True
        self.x = 0
        self.y = 0
        self.width = 1920
        self.height = 1080
        
    def get_frame(self):
        """Get the current frame from this source"""
        return None


class CameraSource(Source):
    """Camera source"""
    def __init__(self, name: str, camera_index: int = 0):
        super().__init__(name, "camera")
        self.camera_index = camera_index
        self.cap = None
        
    def initialize(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        
    def get_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None
        
    def release(self):
        if self.cap:
            self.cap.release()


class EnhancedStreamOutput(BackendHost):
    """
    Enhanced streaming output with multi-platform support and scene management
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

        self.fps_counter = lib_time.FPSCounter()
        self.buffered_frames = lib_logic.DelayedBuffers()
        self.is_show_window = False
        self.prev_frame_num = -1

        self._wnd_name = 'DeepFaceLive Enhanced Output'
        self._wnd_showing = False

        # Enhanced streaming components
        self._streamers = {}  # Multiple streamers for different platforms
        self._recorder = None
        self._scenes = {}
        self._current_scene = None
        self._sources = {}
        
        # Multi-platform streaming settings
        self.streaming_platforms = {
            StreamingPlatform.TWITCH: {
                'name': 'Twitch',
                'rtmp_base': 'rtmp://live.twitch.tv/app/',
                'enabled': False,
                'stream_key': '',
                'quality': '720p',
                'fps': 30,
                'bitrate': 2500
            },
            StreamingPlatform.YOUTUBE: {
                'name': 'YouTube',
                'rtmp_base': 'rtmp://a.rtmp.youtube.com/live2/',
                'enabled': False,
                'stream_key': '',
                'quality': '720p',
                'fps': 30,
                'bitrate': 2500
            },
            StreamingPlatform.FACEBOOK: {
                'name': 'Facebook',
                'rtmp_base': 'rtmp://live-api-s.facebook.com/rtmp/',
                'enabled': False,
                'stream_key': '',
                'quality': '720p',
                'fps': 30,
                'bitrate': 2500
            },
            StreamingPlatform.CUSTOM_RTMP: {
                'name': 'Custom RTMP',
                'rtmp_url': '',
                'enabled': False,
                'quality': '720p',
                'fps': 30,
                'bitrate': 2500
            }
        }
        
        # Recording settings
        self.recording_settings = {
            'enabled': False,
            'format': RecordingFormat.MP4,
            'quality': '1080p',
            'fps': 30,
            'bitrate': 8000,
            'path': save_default_path / 'recordings' if save_default_path else Path('recordings'),
            'filename_pattern': '{date}_{time}_{scene}'
        }

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
        cs.multi_platform_streaming.call_on_flag(self.on_cs_multi_platform_streaming)
        cs.recording_enabled.call_on_flag(self.on_cs_recording_enabled)
        cs.scene_name.call_on_text(self.on_cs_scene_name)
        cs.add_scene.call_on_signal(self.on_cs_add_scene)
        cs.remove_scene.call_on_signal(self.on_cs_remove_scene)

        # Initialize control sheet
        cs.source_type.enable()
        cs.source_type.set_choices(SourceType, ViewModeNames, none_choice_name='@misc.menu_select')
        cs.source_type.select(state.source_type)

        cs.target_delay.enable()
        cs.target_delay.set_config(lib_csw.Number.Config(min=0, max=5000, step=100, decimals=0, allow_instant_update=True))
        cs.target_delay.set_number(state.target_delay if state.target_delay is not None else 500)

        cs.avg_fps.enable()
        cs.avg_fps.set_config(lib_csw.Number.Config(min=0, max=240, decimals=1, read_only=True))
        cs.avg_fps.set_number(0)

        cs.show_hide_window.enable()
        self.hide_window()

        if state.is_showing_window is None:
            state.is_showing_window = False

        if state.is_showing_window:
            state.is_showing_window = not state.is_showing_window
            cs.show_hide_window.signal()

        cs.save_sequence_path.enable()
        cs.save_sequence_path.set_config( lib_csw.Paths.Config.Directory('Choose output sequence directory', directory_path=save_default_path) )
        cs.save_sequence_path.set_paths(state.sequence_path)

        cs.save_fill_frame_gap.enable()
        cs.save_fill_frame_gap.set_flag(state.save_fill_frame_gap if state.save_fill_frame_gap is not None else True )

        cs.is_streaming.enable()
        cs.is_streaming.set_flag(state.is_streaming if state.is_streaming is not None else False )

        cs.stream_addr.enable()
        cs.stream_addr.set_text(state.stream_addr if state.stream_addr is not None else '127.0.0.1')

        cs.stream_port.enable()
        cs.stream_port.set_config(lib_csw.Number.Config(min=1, max=9999, decimals=0, allow_instant_update=True))
        cs.stream_port.set_number(state.stream_port if state.stream_port is not None else 1234)
        
        # Enhanced controls
        cs.multi_platform_streaming.enable()
        cs.multi_platform_streaming.set_flag(state.multi_platform_streaming if state.multi_platform_streaming is not None else False)
        
        cs.recording_enabled.enable()
        cs.recording_enabled.set_flag(state.recording_enabled if state.recording_enabled is not None else False)
        
        cs.scene_name.enable()
        cs.scene_name.set_text(state.scene_name if state.scene_name is not None else 'Default Scene')
        
        cs.add_scene.enable()
        cs.remove_scene.enable()
        
        # Initialize default scene
        self.initialize_default_scene()

    def on_stop(self):
        """Stop all streaming and recording"""
        self.stop_all_streaming()
        self.stop_recording()
        
        # Release all sources
        for source in self._sources.values():
            if hasattr(source, 'release'):
                source.release()

    def initialize_default_scene(self):
        """Initialize the default scene with basic sources"""
        default_scene = Scene("Default Scene")
        self._scenes["Default Scene"] = default_scene
        self._current_scene = "Default Scene"
        
        # Add default camera source
        camera_source = CameraSource("Camera", 0)
        camera_source.initialize()
        self._sources["Camera"] = camera_source
        default_scene.add_source(camera_source)

    def start_streaming(self, platform: StreamingPlatform, stream_key: str = None):
        """Start streaming to a specific platform"""
        if platform not in self.streaming_platforms:
            return False
            
        platform_config = self.streaming_platforms[platform]
        
        if platform == StreamingPlatform.CUSTOM_RTMP:
            rtmp_url = platform_config['rtmp_url']
        else:
            if not stream_key:
                return False
            rtmp_url = platform_config['rtmp_base'] + stream_key
            
        # Create streamer for this platform
        streamer = FFMPEGStreamer()
        if streamer.start(rtmp_url):
            self._streamers[platform] = streamer
            platform_config['enabled'] = True
            return True
        return False

    def stop_streaming(self, platform: StreamingPlatform):
        """Stop streaming to a specific platform"""
        if platform in self._streamers:
            self._streamers[platform].stop()
            del self._streamers[platform]
            self.streaming_platforms[platform]['enabled'] = False

    def stop_all_streaming(self):
        """Stop all streaming"""
        for platform in list(self._streamers.keys()):
            self.stop_streaming(platform)

    def start_recording(self):
        """Start recording"""
        if self.recording_settings['enabled']:
            return
            
        # Create recording directory
        recording_path = self.recording_settings['path']
        recording_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        now = datetime.now()
        filename = self.recording_settings['filename_pattern'].format(
            date=now.strftime('%Y%m%d'),
            time=now.strftime('%H%M%S'),
            scene=self._current_scene or 'default'
        )
        
        # Add extension based on format
        format_extensions = {
            RecordingFormat.MP4: '.mp4',
            RecordingFormat.MKV: '.mkv',
            RecordingFormat.AVI: '.avi',
            RecordingFormat.MOV: '.mov'
        }
        
        extension = format_extensions.get(self.recording_settings['format'], '.mp4')
        filepath = recording_path / f"{filename}{extension}"
        
        # Start recording
        self._recorder = FFMPEGStreamer()
        if self._recorder.start(str(filepath)):
            self.recording_settings['enabled'] = True
            return True
        return False

    def stop_recording(self):
        """Stop recording"""
        if self._recorder:
            self._recorder.stop()
            self._recorder = None
            self.recording_settings['enabled'] = False

    def add_scene(self, name: str):
        """Add a new scene"""
        if name not in self._scenes:
            scene = Scene(name)
            self._scenes[name] = scene
            return True
        return False

    def remove_scene(self, name: str):
        """Remove a scene"""
        if name in self._scenes and name != "Default Scene":
            del self._scenes[name]
            if self._current_scene == name:
                self._current_scene = "Default Scene"
            return True
        return False

    def switch_scene(self, name: str):
        """Switch to a different scene"""
        if name in self._scenes:
            self._current_scene = name
            return True
        return False

    def add_source_to_scene(self, scene_name: str, source: Source):
        """Add a source to a scene"""
        if scene_name in self._scenes:
            self._scenes[scene_name].add_source(source)
            self._sources[source.name] = source
            return True
        return False

    def compose_scene_frame(self):
        """Compose the current scene frame from all active sources"""
        if not self._current_scene or self._current_scene not in self._scenes:
            return None
            
        scene = self._scenes[self._current_scene]
        active_sources = scene.get_active_sources()
        
        if not active_sources:
            return None
            
        # For now, just return the first active source frame
        # In a full implementation, this would composite multiple sources
        for source in active_sources:
            if source.visible:
                frame = source.get_frame()
                if frame is not None:
                    return frame
        return None

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

    def show_window(self):
        state, cs = self.get_state(), self.get_control_sheet()
        cv2.namedWindow(self._wnd_name)
        self._wnd_showing = True

    def hide_window(self):
        state, cs = self.get_state(), self.get_control_sheet()
        if self._wnd_showing:
            cv2.destroyAllWindows()
            self._wnd_showing = False

    def on_cs_show_hide_window_signal(self,):
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

    def on_cs_save_sequence_path(self, paths : List[Path], prev_paths):
        state, cs = self.get_state(), self.get_control_sheet()
        cs.save_sequence_path_error.set_error(None)
        sequence_path = paths[0] if len(paths) != 0 else None

        if sequence_path is None or sequence_path.exists():
            state.sequence_path = sequence_path
            cs.save_sequence_path.set_paths(sequence_path, block_event=True)
        else:
            cs.save_sequence_path_error.set_error('Directory does not exist')
            cs.save_sequence_path.set_paths(prev_paths, block_event=True)

        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_save_fill_frame_gap(self, save_fill_frame_gap):
        state, cs = self.get_state(), self.get_control_sheet()
        state.save_fill_frame_gap = save_fill_frame_gap
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_is_streaming(self, is_streaming):
        state, cs = self.get_state(), self.get_control_sheet()
        state.is_streaming = is_streaming
        
        if is_streaming:
            # Start streaming to all enabled platforms
            for platform, config in self.streaming_platforms.items():
                if config['enabled']:
                    self.start_streaming(platform, config.get('stream_key'))
        else:
            # Stop all streaming
            self.stop_all_streaming()
            
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_stream_addr(self, stream_addr):
        state, cs = self.get_state(), self.get_control_sheet()
        state.stream_addr = stream_addr
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_stream_port(self, stream_port):
        state, cs = self.get_state(), self.get_control_sheet()
        state.stream_port = stream_port
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_multi_platform_streaming(self, multi_platform_streaming):
        state, cs = self.get_state(), self.get_control_sheet()
        state.multi_platform_streaming = multi_platform_streaming
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_recording_enabled(self, recording_enabled):
        state, cs = self.get_state(), self.get_control_sheet()
        state.recording_enabled = recording_enabled
        
        if recording_enabled:
            self.start_recording()
        else:
            self.stop_recording()
            
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_scene_name(self, scene_name):
        state, cs = self.get_state(), self.get_control_sheet()
        state.scene_name = scene_name
        self.switch_scene(scene_name)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_add_scene(self):
        state, cs = self.get_state(), self.get_control_sheet()
        scene_name = f"Scene {len(self._scenes) + 1}"
        if self.add_scene(scene_name):
            cs.scene_name.set_text(scene_name)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_remove_scene(self):
        state, cs = self.get_state(), self.get_control_sheet()
        current_scene = cs.scene_name.get_text()
        if self.remove_scene(current_scene):
            cs.scene_name.set_text("Default Scene")
        self.save_state()
        self.reemit_frame_signal.send()

    def on_tick(self):
        state, cs = self.get_state(), self.get_control_sheet()

        if self.bc_in.has_data():
            frame = self.bc_in.get()
            if frame is not None:
                # Update FPS counter
                self.fps_counter.update()
                cs.avg_fps.set_number(self.fps_counter.get_fps())

                # Process frame based on source type
                processed_frame = self.process_frame(frame, state.source_type, state.aligned_face_id)
                
                if processed_frame is not None:
                    # Add to buffer
                    self.buffered_frames.add(processed_frame)
                    
                    # Get delayed frame
                    delayed_frame = self.buffered_frames.get()
                    if delayed_frame is not None:
                        # Show in window if enabled
                        if state.is_showing_window:
                            if not self._wnd_showing:
                                self.show_window()
                            cv2.imshow(self._wnd_name, delayed_frame)
                            cv2.waitKey(1)
                        
                        # Stream to all active platforms
                        for platform, streamer in self._streamers.items():
                            if streamer.is_running():
                                streamer.write_frame(delayed_frame)
                        
                        # Record if enabled
                        if self._recorder and self._recorder.is_running():
                            self._recorder.write_frame(delayed_frame)
                        
                        # Save sequence if path is set
                        if state.sequence_path is not None:
                            self.save_frame_to_sequence(delayed_frame, state.sequence_path, state.save_fill_frame_gap)

    def process_frame(self, frame, source_type, aligned_face_id):
        """Process frame based on source type"""
        if source_type == SourceType.SOURCE_FRAME:
            return frame
        elif source_type == SourceType.ALIGNED_FACE:
            # Extract aligned face
            # This would need to be implemented based on face detection
            return frame
        elif source_type == SourceType.SWAPPED_FACE:
            # Return swapped face
            return frame
        elif source_type == SourceType.MERGED_FRAME:
            # Return merged frame
            return frame
        else:
            return frame

    def save_frame_to_sequence(self, frame, sequence_path, save_fill_frame_gap):
        """Save frame to sequence directory"""
        if not sequence_path.exists():
            sequence_path.mkdir(parents=True, exist_ok=True)
            
        frame_num = self.prev_frame_num + 1
        filename = f"{frame_num:06d}.png"
        filepath = sequence_path / filename
        
        cv2.imwrite(str(filepath), frame)
        self.prev_frame_num = frame_num


# Reuse existing SourceType and ViewModeNames from StreamOutput
from .StreamOutput import SourceType, ViewModeNames


class Sheet:
    class Host(lib_csw.Sheet.Host):
        def __init__(self):
            super().__init__()
            self.source_type = lib_csw.ControlViewer()
            self.is_showing_window = lib_csw.ControlViewer()
            self.aligned_face_id = lib_csw.ControlViewer()
            self.target_delay = lib_csw.ControlViewer()
            self.sequence_path = lib_csw.ControlViewer()
            self.save_fill_frame_gap = lib_csw.ControlViewer()
            self.is_streaming = lib_csw.ControlViewer()
            self.stream_addr = lib_csw.ControlViewer()
            self.stream_port = lib_csw.ControlViewer()
            self.avg_fps = lib_csw.ControlViewer()
            self.show_hide_window = lib_csw.ControlSignal()
            
            # Enhanced controls
            self.multi_platform_streaming = lib_csw.ControlViewer()
            self.recording_enabled = lib_csw.ControlViewer()
            self.scene_name = lib_csw.ControlViewer()
            self.add_scene = lib_csw.ControlSignal()
            self.remove_scene = lib_csw.ControlSignal()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.source_type = lib_csw.ControlSwitcher()
            self.is_showing_window = lib_csw.ControlSwitcher()
            self.aligned_face_id = lib_csw.ControlSwitcher()
            self.target_delay = lib_csw.ControlSwitcher()
            self.sequence_path = lib_csw.ControlSwitcher()
            self.save_fill_frame_gap = lib_csw.ControlSwitcher()
            self.is_streaming = lib_csw.ControlSwitcher()
            self.stream_addr = lib_csw.ControlSwitcher()
            self.stream_port = lib_csw.ControlSwitcher()
            self.avg_fps = lib_csw.ControlSwitcher()
            self.show_hide_window = lib_csw.ControlSwitcher()
            
            # Enhanced controls
            self.multi_platform_streaming = lib_csw.ControlSwitcher()
            self.recording_enabled = lib_csw.ControlSwitcher()
            self.scene_name = lib_csw.ControlSwitcher()
            self.add_scene = lib_csw.ControlSwitcher()
            self.remove_scene = lib_csw.ControlSwitcher()


class WorkerState(BackendWorkerState):
    source_type : SourceType = SourceType.SOURCE_FRAME
    is_showing_window : bool = None
    aligned_face_id : int = None
    target_delay : int = None
    sequence_path : Path = None
    save_fill_frame_gap : bool = None
    is_streaming : bool = None
    stream_addr : str = None
    stream_port : int = None
    
    # Enhanced state
    multi_platform_streaming : bool = None
    recording_enabled : bool = None
    scene_name : str = None