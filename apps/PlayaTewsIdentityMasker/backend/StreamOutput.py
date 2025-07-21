from enum import IntEnum
from pathlib import Path
from typing import List
import os
import sys

import cv2
import numpy as np
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


class StreamOutput(BackendHost):
    """
    Bufferizes and shows the stream in separated window.
    """
    def __init__(self, weak_heap : BackendWeakHeap,
                       reemit_frame_signal : BackendSignal,
                       bc_in : BackendConnection,
                       save_default_path : Path = None,
                       backend_db : BackendDB = None):

        super().__init__(backend_db=backend_db,
                         sheet_cls=Sheet,
                         worker_cls=StreamOutputWorker,
                         worker_state_cls=WorkerState,
                         worker_start_args=[weak_heap, reemit_frame_signal, bc_in, save_default_path] )

    def get_control_sheet(self) -> 'Sheet.Host': return super().get_control_sheet()


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


class StreamOutputWorker(BackendWorker):
    def get_state(self) -> 'WorkerState': return super().get_state()
    def get_control_sheet(self) -> 'Sheet.Worker': return super().get_control_sheet()

    def on_start(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal,
                       bc_in : BackendConnection,
                       save_default_path : Path):
        self.weak_heap = weak_heap
        self.reemit_frame_signal = reemit_frame_signal
        self.bc_in = bc_in

        self.fps_counter = lib_time.FPSCounter()
        self.buffered_frames = lib_logic.DelayedBuffers()
        self.is_show_window = False
        self.prev_frame_num = -1

        self._wnd_name = 'PlayaTewsIdentityMasker output'
        self._wnd_showing = False

        # Initialize FFmpeg path
        self._setup_ffmpeg_path()
        
        # Initialize streamer with proper error handling
        self._streamer = None
        self._streamer_initialized = False
        self._streaming_error = None
        
        # Performance tracking
        self._frame_count = 0
        self._last_error_time = 0
        self._error_count = 0

        lib_os.set_timer_resolution(1)

        state, cs = self.get_state(), self.get_control_sheet()

        cs.source_type.call_on_selected(self.on_cs_source_type)
        cs.show_hide_window.call_on_signal(self.on_cs_show_hide_window_signal)
        cs.aligned_face_id.call_on_number(self.on_cs_aligned_face_id)
        cs.target_delay.call_on_number(self.on_cs_target_delay)
        cs.save_sequence_path.call_on_paths(self.on_cs_save_sequence_path)
        cs.save_fill_frame_gap.call_on_flag(self.on_cs_save_fill_frame_gap)
        cs.is_streaming.call_on_flag(self.on_cs_is_streaming)
        cs.stream_addr.call_on_text(self.on_cs_stream_addr)
        cs.stream_port.call_on_number(self.on_cs_stream_port)

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

    def _setup_ffmpeg_path(self):
        """Setup FFmpeg path for the system"""
        try:
            # Check if FFmpeg is already in PATH
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ FFmpeg found in system PATH")
                return
        except:
            pass
        
        # Try to find FFmpeg in the project directory
        project_root = Path(__file__).parent.parent.parent.parent
        ffmpeg_paths = [
            project_root / "ffmpeg_enhanced" / "ffmpeg-master-latest-win64-gpl" / "bin",
            project_root / "ffmpeg" / "bin",
            project_root / "tools" / "ffmpeg" / "bin"
        ]
        
        for ffmpeg_path in ffmpeg_paths:
            if ffmpeg_path.exists() and (ffmpeg_path / "ffmpeg.exe").exists():
                # Add to PATH for this process
                current_path = os.environ.get('PATH', '')
                os.environ['PATH'] = str(ffmpeg_path) + os.pathsep + current_path
                print(f"✅ FFmpeg found and added to PATH: {ffmpeg_path}")
                return
        
        print("⚠️ FFmpeg not found. Streaming functionality may not work properly.")
        print("   Please install FFmpeg or ensure it's in the system PATH.")

    def _initialize_streamer(self):
        """Initialize the FFMPEG streamer with error handling"""
        try:
            if self._streamer is None:
                self._streamer = FFMPEGStreamer()
                self._streamer_initialized = True
                self._streaming_error = None
                print("✅ FFMPEG streamer initialized successfully")
            return True
        except Exception as e:
            self._streaming_error = str(e)
            print(f"❌ Failed to initialize FFMPEG streamer: {e}")
            return False

    def on_stop(self):
        """Stop streaming and cleanup"""
        if self._streamer is not None:
            self._streamer.stop()
            self._streamer = None
        self._streamer_initialized = False

    def on_cs_source_type(self, idx, source_type):
        state, cs = self.get_state(), self.get_control_sheet()
        state.source_type = source_type
        self.save_state()
        self.reemit_frame_signal.send()

    def show_window(self):
        self._wnd_showing = True
        cv2.namedWindow(self._wnd_name, cv2.WINDOW_NORMAL)

    def hide_window(self):
        self._wnd_showing = False
        cv2.destroyWindow(self._wnd_name)

    def on_cs_show_hide_window_signal(self,):
        state, cs = self.get_state(), self.get_control_sheet()
        state.is_showing_window = not state.is_showing_window
        if state.is_showing_window:
            self.show_window()
        else:
            self.hide_window()
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_aligned_face_id(self, aligned_face_id):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.aligned_face_id.get_config()
        aligned_face_id = state.aligned_face_id = int(np.clip(aligned_face_id, cfg.min, cfg.max))
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
        
        if is_streaming:
            # Initialize streamer if not already done
            if not self._initialize_streamer():
                print("❌ Cannot start streaming - streamer initialization failed")
                state.is_streaming = False
                cs.is_streaming.set_flag(False, block_event=True)
                return
        
        self.save_state()

    def on_cs_stream_addr(self, stream_addr):
        state, cs = self.get_state(), self.get_control_sheet()
        state.stream_addr = stream_addr
        self.save_state()
        if self._streamer is not None:
            self._streamer.set_addr_port(state.stream_addr, state.stream_port)

    def on_cs_stream_port(self, stream_port):
        state, cs = self.get_state(), self.get_control_sheet()
        state.stream_port = stream_port
        self.save_state()
        if self._streamer is not None:
            self._streamer.set_addr_port(state.stream_addr, state.stream_port)

    def _process_frame_for_streaming(self, view_image):
        """Process frame for streaming with error handling"""
        try:
            if view_image is None:
                return None
                
            # Convert to uint8 format for streaming
            img = ImageProcessor(view_image).to_uint8().get_image('HWC')
            
            # Ensure proper dimensions
            if len(img.shape) != 3 or img.shape[2] != 3:
                print(f"⚠️ Invalid frame shape for streaming: {img.shape}")
                return None
                
            return img
            
        except Exception as e:
            current_time = time.time()
            if current_time - self._last_error_time > 5:  # Log error only every 5 seconds
                print(f"❌ Error processing frame for streaming: {e}")
                self._last_error_time = current_time
                self._error_count += 1
            return None

    def _safe_stream_frame(self, img):
        """Safely stream a frame with error handling"""
        try:
            if self._streamer is not None and self._streamer_initialized:
                self._streamer.push_frame(img)
                self._frame_count += 1
                return True
        except Exception as e:
            current_time = time.time()
            if current_time - self._last_error_time > 5:  # Log error only every 5 seconds
                print(f"❌ Error streaming frame: {e}")
                self._last_error_time = current_time
                self._error_count += 1
                
                # Try to reinitialize streamer on repeated errors
                if self._error_count > 10:
                    print("🔄 Attempting to reinitialize streamer due to repeated errors")
                    self._initialize_streamer()
                    self._error_count = 0
        return False

    def on_tick(self):
        cs, state = self.get_state(), self.get_control_sheet()

        bcd = self.bc_in.read(timeout=0.005)
        if bcd is not None:
            bcd.assign_weak_heap(self.weak_heap)
            cs.avg_fps.set_number( self.fps_counter.step() )

            prev_frame_num = self.prev_frame_num
            frame_num = self.prev_frame_num = bcd.get_frame_num()
            if frame_num < prev_frame_num:
                prev_frame_num = self.prev_frame_num = -1

            source_type = state.source_type
            if source_type is not None and \
                (state.is_showing_window or \
                 state.sequence_path is not None or \
                 state.is_streaming):
                buffered_frames = self.buffered_frames

                view_image = None

                # Process frame based on source type
                try:
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
                            view_image = np.concatenate( (source_frame, merged_frame), 1 )

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
                            view_image = np.concatenate( (aligned_face, swapped_face), 1 )

                except Exception as e:
                    print(f"❌ Error processing frame for source type {source_type}: {e}")
                    view_image = None

                if view_image is not None:
                    # Add to buffer
                    buffered_frames.add_buffer( bcd.get_frame_timestamp(), view_image )

                    # Save sequence if enabled
                    if state.sequence_path is not None:
                        try:
                            img = ImageProcessor(view_image, copy=True).to_uint8().get_image('HWC')
                            file_ext, cv_args = '.jpg', [int(cv2.IMWRITE_JPEG_QUALITY), 100]

                            frame_diff = abs(frame_num - prev_frame_num) if state.save_fill_frame_gap else 1
                            for i in range(frame_diff):
                                n = frame_num - i
                                filename = f'{n:06}'
                                lib_cv.imwrite(state.sequence_path / (filename+file_ext), img, cv_args)
                        except Exception as e:
                            print(f"❌ Error saving frame sequence: {e}")

                    # Process buffered frame
                    pr = buffered_frames.process()
                    img = pr.new_data
                    
                    if img is not None:
                        # Handle streaming
                        if state.is_streaming:
                            stream_img = self._process_frame_for_streaming(view_image)
                            if stream_img is not None:
                                self._safe_stream_frame(stream_img)

                        # Handle window display
                        if state.is_showing_window:
                            try:
                                cv2.imshow(self._wnd_name, img)
                            except Exception as e:
                                print(f"❌ Error displaying window: {e}")

        # Handle window events
        if state.is_showing_window:
            try:
                cv2.waitKey(1)
            except Exception as e:
                print(f"❌ Error in window event loop: {e}")

class Sheet:
    class Host(lib_csw.Sheet.Host):
        def __init__(self):
            super().__init__()
            self.source_type = lib_csw.DynamicSingleSwitch()
            self.show_hide_window = lib_csw.Signal()
            self.aligned_face_id = lib_csw.Number()
            self.target_delay = lib_csw.Number()
            self.avg_fps = lib_csw.Number()
            self.save_sequence_path = lib_csw.Paths()
            self.save_sequence_path_error = lib_csw.Error()
            self.save_fill_frame_gap = lib_csw.Flag()
            self.is_streaming = lib_csw.Flag()
            self.stream_addr = lib_csw.Text()
            self.stream_port = lib_csw.Number()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.source_type = lib_csw.DynamicSingleSwitch()
            self.show_hide_window = lib_csw.Signal()
            self.aligned_face_id = lib_csw.Number()
            self.target_delay = lib_csw.Number()
            self.avg_fps = lib_csw.Number()
            self.save_sequence_path = lib_csw.Paths()
            self.save_sequence_path_error = lib_csw.Error()
            self.save_fill_frame_gap = lib_csw.Flag()
            self.is_streaming = lib_csw.Flag()
            self.stream_addr = lib_csw.Text()
            self.stream_port = lib_csw.Number()


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
