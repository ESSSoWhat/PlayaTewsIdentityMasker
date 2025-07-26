# Live Streaming Implementation Plan

## Phase 1: Enhanced Streaming Engine

### 1.1 Create LiveStreamingManager
```python
# apps/PlayaTewsIdentityMasker/backend/LiveStreamingManager.py
from enum import Enum
from typing import Dict, List, Optional, Callable
import threading
import queue
import time
import cv2
import numpy as np
from pathlib import Path
import subprocess
import json

class StreamPlatform(Enum):
    TWITCH = "twitch"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    CUSTOM_RTMP = "custom_rtmp"

class StreamConfig:
    def __init__(self, platform: StreamPlatform, stream_key: str, 
                 server_url: str = "", enabled: bool = True,
                 bitrate: int = 2500, resolution: str = "1920x1080",
                 fps: int = 30, encoder: str = "libx264"):
        self.platform = platform
        self.stream_key = stream_key
        self.server_url = server_url
        self.enabled = enabled
        self.bitrate = bitrate
        self.resolution = resolution
        self.fps = fps
        self.encoder = encoder

class LiveStreamingManager:
    def __init__(self):
        self.streams: Dict[str, 'StreamProcess'] = {}
        self.is_streaming = False
        self.frame_queue = queue.Queue(maxsize=60)  # Increased buffer
        self.stream_configs: List[StreamConfig] = []
        self.frame_callback: Optional[Callable] = None
        self.stream_stats = {}
        
    def add_stream_config(self, config: StreamConfig):
        """Add streaming configuration"""
        self.stream_configs.append(config)
        
    def start_streaming(self, frame_callback: Callable = None):
        """Start streaming to all configured platforms"""
        if self.is_streaming:
            return False
            
        self.frame_callback = frame_callback
        self.is_streaming = True
        
        # Start streams for each enabled configuration
        for config in self.stream_configs:
            if config.enabled and config.stream_key:
                stream_id = f"{config.platform.value}_{config.stream_key[:8]}"
                stream_process = StreamProcess(config)
                
                if stream_process.start():
                    self.streams[stream_id] = stream_process
                    print(f"✅ Started streaming to {config.platform.value}")
                else:
                    print(f"❌ Failed to start streaming to {config.platform.value}")
                    
        # Start frame processing thread
        self.frame_thread = threading.Thread(target=self._frame_processor, daemon=True)
        self.frame_thread.start()
        
        return len(self.streams) > 0
        
    def stop_streaming(self):
        """Stop all active streams"""
        self.is_streaming = False
        
        for stream_id, stream_process in self.streams.items():
            stream_process.stop()
            print(f"🛑 Stopped stream: {stream_id}")
            
        self.streams.clear()
        
    def send_frame(self, frame: np.ndarray):
        """Send frame to all active streams"""
        if not self.is_streaming or not self.streams:
            return
            
        try:
            self.frame_queue.put_nowait(frame)
        except queue.Full:
            # Drop frame if queue is full
            pass
            
    def _frame_processor(self):
        """Process frames for streaming"""
        while self.is_streaming:
            try:
                frame = self.frame_queue.get(timeout=1.0)
                
                # Send frame to all active streams
                for stream_process in self.streams.values():
                    stream_process.send_frame(frame)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Frame processing error: {e}")
                
    def get_stream_stats(self) -> Dict[str, Dict]:
        """Get statistics for all streams"""
        stats = {}
        for stream_id, stream_process in self.streams.items():
            stats[stream_id] = stream_process.get_stats()
        return stats
```

### 1.2 Enhanced StreamProcess
```python
class StreamProcess:
    def __init__(self, config: StreamConfig):
        self.config = config
        self.process = None
        self.is_running = False
        self.frame_count = 0
        self.start_time = None
        self.last_frame_time = None
        
    def start(self) -> bool:
        """Start the streaming process"""
        try:
            rtmp_url = self._get_rtmp_url()
            if not rtmp_url:
                return False
                
            # Build FFmpeg command
            cmd = self._build_ffmpeg_command(rtmp_url)
            
            # Start FFmpeg process
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.is_running = True
            self.start_time = time.time()
            return True
            
        except Exception as e:
            print(f"❌ Failed to start stream: {e}")
            return False
            
    def _build_ffmpeg_command(self, rtmp_url: str) -> List[str]:
        """Build FFmpeg command for streaming"""
        width, height = map(int, self.config.resolution.split('x'))
        
        cmd = [
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', f'{width}x{height}',
            '-r', str(self.config.fps),
            '-i', '-',
            '-c:v', self.config.encoder,
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-b:v', f'{self.config.bitrate}k',
            '-maxrate', f'{self.config.bitrate}k',
            '-bufsize', f'{self.config.bitrate * 2}k',
            '-g', str(self.config.fps * 2),
            '-f', 'flv',
            rtmp_url
        ]
        
        return cmd
        
    def send_frame(self, frame: np.ndarray):
        """Send frame to stream"""
        if not self.is_running or not self.process:
            return
            
        try:
            # Resize frame if needed
            width, height = map(int, self.config.resolution.split('x'))
            if frame.shape[1] != width or frame.shape[0] != height:
                frame = cv2.resize(frame, (width, height))
                
            # Send frame to FFmpeg
            self.process.stdin.write(frame.tobytes())
            self.process.stdin.flush()
            
            self.frame_count += 1
            self.last_frame_time = time.time()
            
        except Exception as e:
            print(f"❌ Frame send error: {e}")
            self.stop()
            
    def stop(self):
        """Stop the streaming process"""
        self.is_running = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            finally:
                self.process = None
                
    def get_stats(self) -> Dict:
        """Get stream statistics"""
        if not self.start_time:
            return {}
            
        runtime = time.time() - self.start_time
        fps = self.frame_count / runtime if runtime > 0 else 0
        
        return {
            'runtime': runtime,
            'frame_count': self.frame_count,
            'fps': fps,
            'is_running': self.is_running
        }
```

## Phase 2: Professional Recording System

### 2.1 Create ProfessionalRecorder
```python
# apps/PlayaTewsIdentityMasker/backend/ProfessionalRecorder.py
from enum import Enum
from pathlib import Path
import cv2
import numpy as np
import threading
import time
from typing import Optional, Dict

class RecordingFormat(Enum):
    MP4 = "mp4"
    MKV = "mkv"
    AVI = "avi"
    MOV = "mov"

class RecordingQuality(Enum):
    ULTRA_HD = "4k"
    FULL_HD = "1080p"
    HD = "720p"
    SD = "480p"

class ProfessionalRecorder:
    def __init__(self):
        self.is_recording = False
        self.recorder = None
        self.output_path = None
        self.recording_format = RecordingFormat.MP4
        self.recording_quality = RecordingQuality.FULL_HD
        self.fps = 30
        self.start_time = None
        self.frame_count = 0
        
    def start_recording(self, output_path: Path, 
                       format: RecordingFormat = RecordingFormat.MP4,
                       quality: RecordingQuality = RecordingQuality.FULL_HD,
                       fps: int = 30) -> bool:
        """Start recording"""
        if self.is_recording:
            return False
            
        try:
            self.output_path = output_path
            self.recording_format = format
            self.recording_quality = quality
            self.fps = fps
            
            # Get video codec and settings
            codec, bitrate = self._get_recording_settings()
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*codec)
            width, height = self._get_resolution()
            
            self.recorder = cv2.VideoWriter(
                str(output_path),
                fourcc,
                fps,
                (width, height)
            )
            
            if not self.recorder.isOpened():
                return False
                
            self.is_recording = True
            self.start_time = time.time()
            self.frame_count = 0
            
            print(f"✅ Started recording: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start recording: {e}")
            return False
            
    def stop_recording(self):
        """Stop recording"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        if self.recorder:
            self.recorder.release()
            self.recorder = None
            
        runtime = time.time() - self.start_time if self.start_time else 0
        print(f"🛑 Stopped recording. Runtime: {runtime:.1f}s, Frames: {self.frame_count}")
        
    def record_frame(self, frame: np.ndarray):
        """Record a frame"""
        if not self.is_recording or not self.recorder:
            return
            
        try:
            # Resize frame if needed
            width, height = self._get_resolution()
            if frame.shape[1] != width or frame.shape[0] != height:
                frame = cv2.resize(frame, (width, height))
                
            self.recorder.write(frame)
            self.frame_count += 1
            
        except Exception as e:
            print(f"❌ Frame recording error: {e}")
            self.stop_recording()
            
    def _get_recording_settings(self) -> tuple:
        """Get codec and bitrate for recording format"""
        settings = {
            RecordingFormat.MP4: ('mp4v', 8000),
            RecordingFormat.MKV: ('XVID', 8000),
            RecordingFormat.AVI: ('XVID', 6000),
            RecordingFormat.MOV: ('mp4v', 8000)
        }
        return settings.get(self.recording_format, ('mp4v', 8000))
        
    def _get_resolution(self) -> tuple:
        """Get resolution for quality setting"""
        resolutions = {
            RecordingQuality.ULTRA_HD: (3840, 2160),
            RecordingQuality.FULL_HD: (1920, 1080),
            RecordingQuality.HD: (1280, 720),
            RecordingQuality.SD: (854, 480)
        }
        return resolutions.get(self.recording_quality, (1920, 1080))
        
    def get_recording_stats(self) -> Dict:
        """Get recording statistics"""
        if not self.start_time:
            return {}
            
        runtime = time.time() - self.start_time
        fps = self.frame_count / runtime if runtime > 0 else 0
        
        return {
            'runtime': runtime,
            'frame_count': self.frame_count,
            'fps': fps,
            'is_recording': self.is_recording,
            'output_path': str(self.output_path) if self.output_path else None
        }
```

## Phase 3: Integration with Existing System

### 3.1 Enhanced Main Application
```python
# apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerLiveApp.py
from pathlib import Path
from typing import List
from xlib import qt as qtx

from .backend.LiveStreamingManager import LiveStreamingManager, StreamConfig, StreamPlatform
from .backend.ProfessionalRecorder import ProfessionalRecorder, RecordingFormat, RecordingQuality
from .ui.QLiveStreamingPanel import QLiveStreamingPanel
from .ui.QProfessionalRecorderPanel import QProfessionalRecorderPanel

class QLiveSwapEnhanced(qtx.QXWidget):
    def __init__(self, userdata_path: Path, settings_dirpath: Path):
        super().__init__()
        
        # Initialize existing components
        self._init_existing_components(userdata_path, settings_dirpath)
        
        # Initialize new streaming and recording components
        self._init_streaming_components()
        self._init_recording_components()
        
        # Setup UI
        self._setup_enhanced_ui()
        
    def _init_streaming_components(self):
        """Initialize streaming components"""
        self.live_streaming_manager = LiveStreamingManager()
        
        # Add default streaming configurations
        self._setup_default_stream_configs()
        
    def _init_recording_components(self):
        """Initialize recording components"""
        self.professional_recorder = ProfessionalRecorder()
        
        # Setup recording output directory
        recording_path = self.userdata_path / 'recordings'
        recording_path.mkdir(exist_ok=True)
        self.recording_path = recording_path
        
    def _setup_default_stream_configs(self):
        """Setup default streaming configurations"""
        # Twitch configuration
        twitch_config = StreamConfig(
            platform=StreamPlatform.TWITCH,
            stream_key="",  # User will enter their key
            server_url="rtmp://live.twitch.tv/app/",
            enabled=False,
            bitrate=2500,
            resolution="1920x1080",
            fps=30
        )
        self.live_streaming_manager.add_stream_config(twitch_config)
        
        # YouTube configuration
        youtube_config = StreamConfig(
            platform=StreamPlatform.YOUTUBE,
            stream_key="",
            server_url="rtmp://a.rtmp.youtube.com/live2/",
            enabled=False,
            bitrate=2500,
            resolution="1920x1080",
            fps=30
        )
        self.live_streaming_manager.add_stream_config(youtube_config)
        
    def _setup_enhanced_ui(self):
        """Setup enhanced UI with streaming and recording panels"""
        # Create main layout
        main_layout = qtx.QXHBoxLayout()
        
        # Left panel - Sources and Controls
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Center panel - Preview and Face Swap
        center_panel = self._create_center_panel()
        main_layout.addWidget(center_panel, 2)
        
        # Right panel - Streaming and Recording
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
        
    def _create_right_panel(self):
        """Create right panel with streaming and recording controls"""
        panel = qtx.QXWidget()
        layout = qtx.QXVBoxLayout()
        
        # Streaming panel
        self.q_live_streaming_panel = QLiveStreamingPanel(self.live_streaming_manager)
        layout.addWidget(self.q_live_streaming_panel)
        
        # Recording panel
        self.q_professional_recorder_panel = QProfessionalRecorderPanel(
            self.professional_recorder, self.recording_path
        )
        layout.addWidget(self.q_professional_recorder_panel)
        
        panel.setLayout(layout)
        return panel
        
    def start_streaming(self):
        """Start streaming with current face swap output"""
        def frame_callback():
            # Get the current processed frame from face merger
            return self.face_merger.get_last_frame()
            
        success = self.live_streaming_manager.start_streaming(frame_callback)
        if success:
            print("✅ Live streaming started successfully!")
        else:
            print("❌ Failed to start live streaming")
            
    def stop_streaming(self):
        """Stop streaming"""
        self.live_streaming_manager.stop_streaming()
        print("🛑 Live streaming stopped")
        
    def start_recording(self):
        """Start recording with current face swap output"""
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"face_swap_recording_{timestamp}.mp4"
        output_path = self.recording_path / filename
        
        success = self.professional_recorder.start_recording(
            output_path=output_path,
            format=RecordingFormat.MP4,
            quality=RecordingQuality.FULL_HD,
            fps=30
        )
        
        if success:
            print(f"✅ Recording started: {output_path}")
        else:
            print("❌ Failed to start recording")
            
    def stop_recording(self):
        """Stop recording"""
        self.professional_recorder.stop_recording()
        print("🛑 Recording stopped")
```

## Phase 4: UI Components

### 4.1 Live Streaming Panel
```python
# apps/PlayaTewsIdentityMasker/ui/QLiveStreamingPanel.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QComboBox, QLineEdit, QCheckBox, QGroupBox,
                            QSpinBox, QFormLayout, QTabWidget)
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from ..backend.LiveStreamingManager import StreamPlatform, StreamConfig

class QLiveStreamingPanel(QWidget):
    def __init__(self, streaming_manager):
        super().__init__()
        self.streaming_manager = streaming_manager
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the streaming panel UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Live Streaming")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Platform tabs
        self.tab_widget = QTabWidget()
        
        # Twitch tab
        self.twitch_tab = self._create_platform_tab("Twitch", StreamPlatform.TWITCH)
        self.tab_widget.addTab(self.twitch_tab, "Twitch")
        
        # YouTube tab
        self.youtube_tab = self._create_platform_tab("YouTube", StreamPlatform.YOUTUBE)
        self.tab_widget.addTab(self.youtube_tab, "YouTube")
        
        # Custom RTMP tab
        self.custom_tab = self._create_custom_rtmp_tab()
        self.tab_widget.addTab(self.custom_tab, "Custom RTMP")
        
        layout.addWidget(self.tab_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Streaming")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Streaming")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("Status: Not Streaming")
        self.status_label.setStyleSheet("color: #6c757d; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def _create_platform_tab(self, platform_name: str, platform: StreamPlatform) -> QWidget:
        """Create a tab for a specific platform"""
        tab = QWidget()
        layout = QFormLayout()
        
        # Enable checkbox
        self.enable_checkbox = QCheckBox(f"Enable {platform_name} streaming")
        layout.addRow("Enabled:", self.enable_checkbox)
        
        # Stream key
        self.stream_key_edit = QLineEdit()
        self.stream_key_edit.setPlaceholderText("Enter your stream key")
        self.stream_key_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("Stream Key:", self.stream_key_edit)
        
        # Quality settings
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(['1080p', '720p', '480p'])
        self.quality_combo.setCurrentText('720p')
        layout.addRow("Quality:", self.quality_combo)
        
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(['30', '60'])
        self.fps_combo.setCurrentText('30')
        layout.addRow("FPS:", self.fps_combo)
        
        self.bitrate_spin = QSpinBox()
        self.bitrate_spin.setRange(1000, 8000)
        self.bitrate_spin.setValue(2500)
        self.bitrate_spin.setSuffix(" kbps")
        layout.addRow("Bitrate:", self.bitrate_spin)
        
        tab.setLayout(layout)
        return tab
        
    def _create_custom_rtmp_tab(self) -> QWidget:
        """Create custom RTMP tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        # Enable checkbox
        self.custom_enable_checkbox = QCheckBox("Enable Custom RTMP streaming")
        layout.addRow("Enabled:", self.custom_enable_checkbox)
        
        # RTMP URL
        self.rtmp_url_edit = QLineEdit()
        self.rtmp_url_edit.setPlaceholderText("rtmp://your-server.com/live/stream-key")
        layout.addRow("RTMP URL:", self.rtmp_url_edit)
        
        # Quality settings (same as platform tabs)
        self.custom_quality_combo = QComboBox()
        self.custom_quality_combo.addItems(['1080p', '720p', '480p'])
        self.custom_quality_combo.setCurrentText('720p')
        layout.addRow("Quality:", self.custom_quality_combo)
        
        self.custom_fps_combo = QComboBox()
        self.custom_fps_combo.addItems(['30', '60'])
        self.custom_fps_combo.setCurrentText('30')
        layout.addRow("FPS:", self.custom_fps_combo)
        
        self.custom_bitrate_spin = QSpinBox()
        self.custom_bitrate_spin.setRange(1000, 8000)
        self.custom_bitrate_spin.setValue(2500)
        self.custom_bitrate_spin.setSuffix(" kbps")
        layout.addRow("Bitrate:", self.custom_bitrate_spin)
        
        tab.setLayout(layout)
        return tab
        
    def setup_connections(self):
        """Setup signal connections"""
        self.start_button.clicked.connect(self.start_streaming)
        self.stop_button.clicked.connect(self.stop_streaming)
        
        # Update status timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
        
    def start_streaming(self):
        """Start streaming"""
        # Get current tab configuration
        current_tab = self.tab_widget.currentWidget()
        
        if current_tab == self.twitch_tab:
            self._start_platform_streaming(StreamPlatform.TWITCH)
        elif current_tab == self.youtube_tab:
            self._start_platform_streaming(StreamPlatform.YOUTUBE)
        elif current_tab == self.custom_tab:
            self._start_custom_rtmp_streaming()
            
    def _start_platform_streaming(self, platform: StreamPlatform):
        """Start streaming to a specific platform"""
        # Get configuration from UI
        stream_key = self.stream_key_edit.text()
        if not stream_key:
            print("❌ Please enter a stream key")
            return
            
        # Update configuration
        config = self._get_platform_config(platform)
        config.stream_key = stream_key
        config.enabled = True
        
        # Start streaming
        success = self.streaming_manager.start_streaming()
        if success:
            self.status_label.setText("Status: Streaming")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
        else:
            self.status_label.setText("Status: Failed to start")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            
    def stop_streaming(self):
        """Stop streaming"""
        self.streaming_manager.stop_streaming()
        self.status_label.setText("Status: Not Streaming")
        self.status_label.setStyleSheet("color: #6c757d; font-weight: bold;")
        
    def update_status(self):
        """Update streaming status"""
        if self.streaming_manager.is_streaming:
            stats = self.streaming_manager.get_stream_stats()
            if stats:
                # Show active stream info
                active_streams = list(stats.keys())
                self.status_label.setText(f"Status: Streaming to {len(active_streams)} platform(s)")
            else:
                self.status_label.setText("Status: No active streams")
        else:
            self.status_label.setText("Status: Not Streaming")
```

## Implementation Steps

### Step 1: Create Core Components
1. Create `LiveStreamingManager.py` in backend
2. Create `ProfessionalRecorder.py` in backend
3. Create UI panels for streaming and recording

### Step 2: Integrate with Existing System
1. Modify main application to include new components
2. Connect face swap output to streaming/recording
3. Add streaming and recording controls to UI

### Step 3: Testing and Optimization
1. Test streaming to different platforms
2. Test recording with different formats
3. Optimize performance for real-time processing
4. Add error handling and recovery

### Step 4: Advanced Features
1. Add scene management
2. Add virtual camera support
3. Add advanced audio processing
4. Add stream analytics and monitoring

## Key Benefits

1. **Professional Streaming**: Multi-platform support with automatic reconnection
2. **High-Quality Recording**: Multiple formats and quality options
3. **Real-time Performance**: Optimized for live streaming
4. **User-Friendly Interface**: Intuitive controls for content creators
5. **Extensible Architecture**: Easy to add new platforms and features

This implementation plan provides a solid foundation for transforming the face swap application into a professional live streaming and recording platform.