from pathlib import Path
from typing import List, Dict, Optional
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QPushButton, QLabel, QComboBox, QSpinBox, QLineEdit,
                            QCheckBox, QGroupBox, QTabWidget, QSplitter, 
                            QListWidget, QListWidgetItem, QSlider, QFrame,
                            QTextEdit, QProgressBar, QScrollArea, QSizePolicy)

from localization import L
from resources.fonts import QXFontDB
from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel

from .widgets.QBackendPanel import QBackendPanel
from .widgets.QCheckBoxCSWFlag import QCheckBoxCSWFlag
from .widgets.QComboBoxCSWDynamicSingleSwitch import QComboBoxCSWDynamicSingleSwitch
from .widgets.QErrorCSWError import QErrorCSWError
from .widgets.QLabelCSWNumber import QLabelCSWNumber
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QLineEditCSWText import QLineEditCSWText
from .widgets.QPathEditCSWPaths import QPathEditCSWPaths
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber
from .widgets.QXPushButtonCSWSignal import QXPushButtonCSWSignal

from ..backend import StreamOutput
from ..backend.StreamOutput import SourceType


class QOBSStyleUI(QWidget):
    """OBS Studio-style UI for DeepFaceLive with enhanced streaming and recording capabilities"""
    
    def __init__(self, stream_output_backend: StreamOutput, userdata_path: Path, face_swap_components=None, viewers_components=None):
        super().__init__()
        self.stream_output_backend = stream_output_backend
        self.userdata_path = userdata_path
        self.face_swap_components = face_swap_components or {}
        self.viewers_components = viewers_components or {}
        self.scenes = []
        self.current_scene = None
        self.sources_by_scene = {}  # Track sources per scene
        self.streaming_platforms = {
            'twitch': {'name': 'Twitch', 'rtmp': 'rtmp://live.twitch.tv/app/'},
            'youtube': {'name': 'YouTube', 'rtmp': 'rtmp://a.rtmp.youtube.com/live2/'},
            'facebook': {'name': 'Facebook', 'rtmp': 'rtmp://live-api-s.facebook.com/rtmp/'},
            'custom': {'name': 'Custom RTMP', 'rtmp': ''}
        }
        self.recording_formats = ['mp4', 'mkv', 'avi', 'mov']
        self.recording_qualities = ['1080p', '720p', '480p', '360p']
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        main_layout = QHBoxLayout()
        
        # Left panel - Sources and Scenes
        left_panel = self.create_left_panel()
        
        # Center panel - Preview and Controls
        center_panel = self.create_center_panel()
        
        # Right panel - Settings and Audio
        right_panel = self.create_right_panel()
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([250, 600, 300])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
    def create_left_panel(self):
        """Create the left panel with scenes and sources"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Scenes section
        scenes_group = QGroupBox("Scenes")
        scenes_layout = QVBoxLayout()
        
        self.scenes_list = QListWidget()
        self.scenes_list.setMaximumHeight(150)
        scenes_layout.addWidget(self.scenes_list)
        
        scenes_buttons_layout = QHBoxLayout()
        self.add_scene_btn = QPushButton("+")
        self.add_scene_btn.setMaximumWidth(30)
        self.remove_scene_btn = QPushButton("-")
        self.remove_scene_btn.setMaximumWidth(30)
        self.duplicate_scene_btn = QPushButton("Copy")
        
        scenes_buttons_layout.addWidget(self.add_scene_btn)
        scenes_buttons_layout.addWidget(self.remove_scene_btn)
        scenes_buttons_layout.addWidget(self.duplicate_scene_btn)
        scenes_buttons_layout.addStretch()
        
        scenes_layout.addLayout(scenes_buttons_layout)
        scenes_group.setLayout(scenes_layout)
        
        # Sources section
        sources_group = QGroupBox("Sources")
        sources_layout = QVBoxLayout()
        
        self.sources_list = QListWidget()
        sources_layout.addWidget(self.sources_list)
        
        sources_buttons_layout = QHBoxLayout()
        self.add_source_btn = QPushButton("+")
        self.add_source_btn.setMaximumWidth(30)
        self.remove_source_btn = QPushButton("-")
        self.remove_source_btn.setMaximumWidth(30)
        self.source_properties_btn = QPushButton("Properties")
        
        sources_buttons_layout.addWidget(self.add_source_btn)
        sources_buttons_layout.addWidget(self.remove_source_btn)
        sources_buttons_layout.addWidget(self.source_properties_btn)
        sources_buttons_layout.addStretch()
        
        sources_layout.addLayout(sources_buttons_layout)
        sources_group.setLayout(sources_layout)
        
        layout.addWidget(scenes_group)
        layout.addWidget(sources_group)
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
        
    def create_center_panel(self):
        """Create the center panel with preview, controls, and viewers"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Top section: Preview and Controls
        top_section = QWidget()
        top_layout = QHBoxLayout()
        
        # Preview area (left side of top section)
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("Preview Area")
        self.preview_label.setMinimumSize(800, 450)  # Larger preview
        self.preview_label.setMaximumSize(800, 450)  # Fixed size
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 5px;
                color: #ffffff;
                font-size: 16px;
            }
        """)
        self.preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        
        # Controls area (right side of top section)
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        
        # Streaming controls
        self.stream_btn = QPushButton("Start Streaming")
        self.stream_btn.setMinimumHeight(40)
        self.stream_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
        # Recording controls
        self.record_btn = QPushButton("Start Recording")
        self.record_btn.setMinimumHeight(40)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
        """)
        
        # Settings button
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setMinimumHeight(30)
        
        # Processing window button
        self.processing_btn = QPushButton("Processing Controls")
        self.processing_btn.setMinimumHeight(30)
        self.processing_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        controls_layout.addWidget(self.stream_btn)
        controls_layout.addWidget(self.record_btn)
        controls_layout.addWidget(self.settings_btn)
        controls_layout.addWidget(self.processing_btn)
        controls_layout.addStretch()
        
        controls_group.setLayout(controls_layout)
        
        # Add preview and controls to top section
        top_layout.addWidget(preview_group)
        top_layout.addWidget(controls_group)
        top_section.setLayout(top_layout)
        
        # Bottom section: Viewers
        bottom_section = QWidget()
        bottom_layout = QVBoxLayout()
        
        # Viewers group
        viewers_group = QGroupBox("Processing Views")
        viewers_layout = QHBoxLayout()
        
        # Use actual viewers if available, otherwise create placeholders
        if 'frame_viewer' in self.viewers_components:
            frame_viewer = self.viewers_components['frame_viewer']
            frame_viewer.setMinimumSize(150, 120)  # Smaller size
        else:
            frame_viewer = QLabel("Frame Viewer")
            frame_viewer.setMinimumSize(150, 120)  # Smaller size
            frame_viewer.setStyleSheet("""
                QLabel {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #cccccc;
                    font-size: 12px;
                }
            """)
            frame_viewer.setAlignment(Qt.AlignCenter)
        
        if 'face_align_viewer' in self.viewers_components:
            face_align_viewer = self.viewers_components['face_align_viewer']
            face_align_viewer.setMinimumSize(150, 120)  # Smaller size
        else:
            face_align_viewer = QLabel("Face Align Viewer")
            face_align_viewer.setMinimumSize(150, 120)  # Smaller size
            face_align_viewer.setStyleSheet("""
                QLabel {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #cccccc;
                    font-size: 12px;
                }
            """)
            face_align_viewer.setAlignment(Qt.AlignCenter)
        
        if 'face_swap_viewer' in self.viewers_components:
            face_swap_viewer = self.viewers_components['face_swap_viewer']
            face_swap_viewer.setMinimumSize(150, 120)  # Smaller size
        else:
            face_swap_viewer = QLabel("Face Swap Viewer")
            face_swap_viewer.setMinimumSize(150, 120)  # Smaller size
            face_swap_viewer.setStyleSheet("""
                QLabel {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #cccccc;
                    font-size: 12px;
                }
            """)
            face_swap_viewer.setAlignment(Qt.AlignCenter)
        
        # Merged frame viewer (stretches to fit - much larger)
        if 'merged_frame_viewer' in self.viewers_components:
            merged_frame_viewer = self.viewers_components['merged_frame_viewer']
            merged_frame_viewer.setMinimumSize(600, 200)  # Much larger
        else:
            merged_frame_viewer = QLabel("Merged Frame Viewer")
            merged_frame_viewer.setMinimumSize(600, 200)  # Much larger
            merged_frame_viewer.setStyleSheet("""
                QLabel {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #cccccc;
                    font-size: 12px;
                }
            """)
            merged_frame_viewer.setAlignment(Qt.AlignCenter)
        
        viewers_layout.addWidget(frame_viewer)
        viewers_layout.addWidget(face_align_viewer)
        viewers_layout.addWidget(face_swap_viewer)
        viewers_layout.addWidget(merged_frame_viewer, 3)  # Much more stretch weight
        
        viewers_group.setLayout(viewers_layout)
        bottom_layout.addWidget(viewers_group)
        bottom_section.setLayout(bottom_layout)
        
        # Add sections to main layout
        layout.addWidget(top_section)
        layout.addWidget(bottom_section)
        
        panel.setLayout(layout)
        return panel
        
    def create_right_panel(self):
        """Create the right panel with settings and audio controls"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Create tab widget for different settings
        self.settings_tabs = QTabWidget()
        
        # Face Swap settings tab (if components are available)
        if self.face_swap_components:
            face_swap_tab = self.create_face_swap_tab()
            self.settings_tabs.addTab(face_swap_tab, "Face Swap")
        
        # Streaming settings tab
        streaming_tab = self.create_streaming_tab()
        self.settings_tabs.addTab(streaming_tab, "Streaming")
        
        # Recording settings tab
        recording_tab = self.create_recording_tab()
        self.settings_tabs.addTab(recording_tab, "Recording")
        
        # Audio settings tab
        audio_tab = self.create_audio_tab()
        self.settings_tabs.addTab(audio_tab, "Audio")
        
        # Video settings tab
        video_tab = self.create_video_tab()
        self.settings_tabs.addTab(video_tab, "Video")
        
        layout.addWidget(self.settings_tabs)
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
        
    def create_streaming_tab(self):
        """Create streaming settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Platform selection
        platform_group = QGroupBox("Streaming Platform")
        platform_layout = QVBoxLayout()
        
        self.platform_combo = QComboBox()
        for key, platform in self.streaming_platforms.items():
            self.platform_combo.addItem(platform['name'], key)
        
        platform_layout.addWidget(QLabel("Platform:"))
        platform_layout.addWidget(self.platform_combo)
        
        # Stream key
        self.stream_key_edit = QLineEdit()
        self.stream_key_edit.setPlaceholderText("Enter your stream key")
        self.stream_key_edit.setEchoMode(QLineEdit.Password)
        self.stream_key_edit.setMaxLength(100)  # Limit stream key length
        
        platform_layout.addWidget(QLabel("Stream Key:"))
        platform_layout.addWidget(self.stream_key_edit)
        
        # Custom RTMP URL
        self.custom_rtmp_edit = QLineEdit()
        self.custom_rtmp_edit.setPlaceholderText("rtmp://your-server.com/live/stream-key")
        self.custom_rtmp_edit.setEnabled(False)  # Initially disabled
        
        platform_layout.addWidget(QLabel("Custom RTMP URL:"))
        platform_layout.addWidget(self.custom_rtmp_edit)
        
        platform_group.setLayout(platform_layout)
        
        # Stream settings
        stream_settings_group = QGroupBox("Stream Settings")
        stream_settings_layout = QGridLayout()
        
        self.stream_quality_combo = QComboBox()
        self.stream_quality_combo.addItems(['1080p', '720p', '480p', '360p'])
        self.stream_quality_combo.setCurrentText('720p')
        
        self.stream_fps_combo = QComboBox()
        self.stream_fps_combo.addItems(['30', '60'])
        self.stream_fps_combo.setCurrentText('30')
        
        self.stream_bitrate_spin = QSpinBox()
        self.stream_bitrate_spin.setRange(1000, 8000)
        self.stream_bitrate_spin.setValue(2500)
        self.stream_bitrate_spin.setSuffix(" kbps")
        self.stream_bitrate_spin.setSingleStep(100)  # Step by 100 kbps
        
        stream_settings_layout.addWidget(QLabel("Quality:"), 0, 0)
        stream_settings_layout.addWidget(self.stream_quality_combo, 0, 1)
        stream_settings_layout.addWidget(QLabel("FPS:"), 1, 0)
        stream_settings_layout.addWidget(self.stream_fps_combo, 1, 1)
        stream_settings_layout.addWidget(QLabel("Bitrate:"), 2, 0)
        stream_settings_layout.addWidget(self.stream_bitrate_spin, 2, 1)
        
        stream_settings_group.setLayout(stream_settings_layout)
        
        layout.addWidget(platform_group)
        layout.addWidget(stream_settings_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_recording_tab(self):
        """Create recording settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Recording format
        format_group = QGroupBox("Recording Format")
        format_layout = QVBoxLayout()
        
        self.recording_format_combo = QComboBox()
        self.recording_format_combo.addItems(self.recording_formats)
        self.recording_format_combo.setCurrentText('mp4')
        
        format_layout.addWidget(QLabel("Format:"))
        format_layout.addWidget(self.recording_format_combo)
        
        format_group.setLayout(format_layout)
        
        # Recording quality
        quality_group = QGroupBox("Recording Quality")
        quality_layout = QGridLayout()
        
        self.recording_quality_combo = QComboBox()
        self.recording_quality_combo.addItems(self.recording_qualities)
        self.recording_quality_combo.setCurrentText('1080p')
        
        self.recording_fps_combo = QComboBox()
        self.recording_fps_combo.addItems(['30', '60'])
        self.recording_fps_combo.setCurrentText('30')
        
        self.recording_bitrate_spin = QSpinBox()
        self.recording_bitrate_spin.setRange(1000, 50000)
        self.recording_bitrate_spin.setValue(8000)
        self.recording_bitrate_spin.setSuffix(" kbps")
        self.recording_bitrate_spin.setSingleStep(500)  # Step by 500 kbps
        
        quality_layout.addWidget(QLabel("Quality:"), 0, 0)
        quality_layout.addWidget(self.recording_quality_combo, 0, 1)
        quality_layout.addWidget(QLabel("FPS:"), 1, 0)
        quality_layout.addWidget(self.recording_fps_combo, 1, 1)
        quality_layout.addWidget(QLabel("Bitrate:"), 2, 0)
        quality_layout.addWidget(self.recording_bitrate_spin, 2, 1)
        
        quality_group.setLayout(quality_layout)
        
        # Recording path
        path_group = QGroupBox("Recording Path")
        path_layout = QVBoxLayout()
        
        self.recording_path_edit = QLineEdit()
        recording_path = self.userdata_path / "recordings"
        self.recording_path_edit.setText(str(recording_path))
        # Ensure the directory exists
        recording_path.mkdir(parents=True, exist_ok=True)
        
        path_layout.addWidget(QLabel("Save recordings to:"))
        path_layout.addWidget(self.recording_path_edit)
        
        path_group.setLayout(path_layout)
        
        layout.addWidget(format_group)
        layout.addWidget(quality_group)
        layout.addWidget(path_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_audio_tab(self):
        """Create audio settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Audio sources
        audio_sources_group = QGroupBox("Audio Sources")
        audio_sources_layout = QVBoxLayout()
        
        self.mic_volume_slider = QSlider(Qt.Horizontal)
        self.mic_volume_slider.setRange(0, 100)
        self.mic_volume_slider.setValue(50)
        self.mic_volume_slider.setTickPosition(QSlider.TicksBelow)
        self.mic_volume_slider.setTickInterval(10)
        
        self.desktop_audio_checkbox = QCheckBox("Include Desktop Audio")
        self.desktop_audio_checkbox.setChecked(True)
        self.desktop_audio_checkbox.toggled.connect(self.on_desktop_audio_toggled)
        
        audio_sources_layout.addWidget(QLabel("Microphone Volume:"))
        audio_sources_layout.addWidget(self.mic_volume_slider)
        audio_sources_layout.addWidget(self.desktop_audio_checkbox)
        
        audio_sources_group.setLayout(audio_sources_layout)
        
        # Audio monitoring
        monitoring_group = QGroupBox("Audio Monitoring")
        monitoring_layout = QVBoxLayout()
        
        self.monitor_audio_checkbox = QCheckBox("Monitor Audio Output")
        self.monitor_audio_checkbox.toggled.connect(self.on_monitor_audio_toggled)
        self.monitor_volume_slider = QSlider(Qt.Horizontal)
        self.monitor_volume_slider.setRange(0, 100)
        self.monitor_volume_slider.setValue(30)
        self.monitor_volume_slider.setTickPosition(QSlider.TicksBelow)
        self.monitor_volume_slider.setTickInterval(10)
        
        monitoring_layout.addWidget(self.monitor_audio_checkbox)
        monitoring_layout.addWidget(QLabel("Monitor Volume:"))
        monitoring_layout.addWidget(self.monitor_volume_slider)
        
        monitoring_group.setLayout(monitoring_layout)
        
        layout.addWidget(audio_sources_group)
        layout.addWidget(monitoring_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_face_swap_tab(self):
        """Create face swap settings tab with traditional controls"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Create scroll area for face swap controls
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Add face swap components if available
        if self.face_swap_components:
            # File and Camera sources
            if 'file_source' in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components['file_source'])
            if 'camera_source' in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components['camera_source'])
            
            # Face detection and alignment
            if 'face_detector' in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components['face_detector'])
            if 'face_aligner' in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components['face_aligner'])
            
            # Face processing
            if 'face_marker' in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components['face_marker'])
            if 'face_animator' in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components['face_animator'])
            if 'face_swap_insight' in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components['face_swap_insight'])
            if 'face_swap_dfm' in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components['face_swap_dfm'])
            
            # Frame processing
            if 'frame_adjuster' in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components['frame_adjuster'])
            if 'face_merger' in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components['face_merger'])
            if 'stream_output' in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components['stream_output'])
        
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab
        
    def create_video_tab(self):
        """Create video settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Video settings
        video_settings_group = QGroupBox("Video Settings")
        video_settings_layout = QGridLayout()
        
        self.base_resolution_combo = QComboBox()
        self.base_resolution_combo.addItems(['1920x1080', '1280x720', '854x480'])
        self.base_resolution_combo.setCurrentText('1920x1080')
        
        self.output_resolution_combo = QComboBox()
        self.output_resolution_combo.addItems(['1920x1080', '1280x720', '854x480'])
        self.output_resolution_combo.setCurrentText('1280x720')
        
        # Connect resolution changes to validate compatibility
        self.base_resolution_combo.currentTextChanged.connect(self.on_resolution_changed)
        self.output_resolution_combo.currentTextChanged.connect(self.on_resolution_changed)
        
        self.downscale_filter_combo = QComboBox()
        self.downscale_filter_combo.addItems(['Bicubic', 'Bilinear', 'Lanczos'])
        self.downscale_filter_combo.setCurrentText('Bicubic')
        
        video_settings_layout.addWidget(QLabel("Base Resolution:"), 0, 0)
        video_settings_layout.addWidget(self.base_resolution_combo, 0, 1)
        video_settings_layout.addWidget(QLabel("Output Resolution:"), 1, 0)
        video_settings_layout.addWidget(self.output_resolution_combo, 1, 1)
        video_settings_layout.addWidget(QLabel("Downscale Filter:"), 2, 0)
        video_settings_layout.addWidget(self.downscale_filter_combo, 2, 1)
        
        video_settings_group.setLayout(video_settings_layout)
        
        # Face swap settings
        face_swap_group = QGroupBox("Face Swap Settings")
        face_swap_layout = QVBoxLayout()
        
        self.face_swap_enabled_checkbox = QCheckBox("Enable Face Swap")
        self.face_swap_enabled_checkbox.setChecked(True)
        self.face_swap_enabled_checkbox.toggled.connect(self.on_face_swap_toggled)
        
        self.face_swap_quality_combo = QComboBox()
        self.face_swap_quality_combo.addItems(['High', 'Medium', 'Low'])
        self.face_swap_quality_combo.setCurrentText('High')
        self.face_swap_quality_combo.setEnabled(True)  # Enable by default
        
        face_swap_layout.addWidget(self.face_swap_enabled_checkbox)
        face_swap_layout.addWidget(QLabel("Face Swap Quality:"))
        face_swap_layout.addWidget(self.face_swap_quality_combo)
        
        face_swap_group.setLayout(face_swap_layout)
        
        layout.addWidget(video_settings_group)
        layout.addWidget(face_swap_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def setup_styles(self):
        """Setup the OBS Studio-like dark theme"""
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QPushButton {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
                color: #ffffff;
            }
            
            QPushButton:hover {
                background-color: #505050;
            }
            
            QPushButton:pressed {
                background-color: #303030;
            }
            
            QComboBox {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
                color: #ffffff;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            
            QLineEdit {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
                color: #ffffff;
            }
            
            QSpinBox {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
                color: #ffffff;
            }
            
            QCheckBox {
                spacing: 5px;
            }
            
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
            
            QCheckBox::indicator:unchecked {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 2px;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
                border-radius: 2px;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #606060;
                height: 8px;
                background: #404040;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #0078d4;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            
            QTabWidget::pane {
                border: 1px solid #606060;
                background-color: #2b2b2b;
            }
            
            QTabBar::tab {
                background-color: #404040;
                border: 1px solid #606060;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            
            QListWidget {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 3px;
                color: #ffffff;
            }
            
            QListWidget::item {
                padding: 5px;
            }
            
            QListWidget::item:selected {
                background-color: #0078d4;
            }
        """)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.stream_btn.clicked.connect(self.toggle_streaming)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.settings_btn.clicked.connect(self.open_settings)
        self.processing_btn.clicked.connect(self.open_processing_window)
        
        self.add_scene_btn.clicked.connect(self.add_scene)
        self.remove_scene_btn.clicked.connect(self.remove_scene)
        self.duplicate_scene_btn.clicked.connect(self.duplicate_scene)
        
        self.add_source_btn.clicked.connect(self.add_source)
        self.remove_source_btn.clicked.connect(self.remove_source)
        self.source_properties_btn.clicked.connect(self.source_properties)
        
        self.platform_combo.currentIndexChanged.connect(self.on_platform_changed)
        
        # Connect scene selection changes
        self.scenes_list.currentItemChanged.connect(self.on_scene_changed)
        
        # Initialize default scene
        self.add_default_scene()
        
        # Initialize processing window
        self.processing_window = None
        
    def add_default_scene(self):
        """Add a default scene"""
        try:
            scene_item = QListWidgetItem("Default Scene")
            self.scenes_list.addItem(scene_item)
            self.scenes_list.setCurrentItem(scene_item)
            self.current_scene = "Default Scene"
            self.scenes.append("Default Scene")
            self.sources_by_scene["Default Scene"] = []
            
            # Add default sources
            sources = ["Camera Source", "Face Swap", "Audio Input"]
            for source in sources:
                source_item = QListWidgetItem(source)
                self.sources_list.addItem(source_item)
                self.sources_by_scene["Default Scene"].append(source)
        except Exception as e:
            # Handle any errors in scene creation
            pass
            
    def toggle_streaming(self):
        """Toggle streaming on/off"""
        if self.stream_btn.text() == "Start Streaming":
            self.start_streaming()
        else:
            self.stop_streaming()
            
    def start_streaming(self):
        """Start streaming"""
        platform_key = self.platform_combo.currentData()
        stream_key = self.stream_key_edit.text()
        
        if not stream_key and platform_key != 'custom':
            # Show error message for missing stream key
            return
            
        # Configure streaming backend
        cs = self.stream_output_backend.get_control_sheet()
        cs.is_streaming.set_flag(True)
        
        # Set stream address based on platform
        if platform_key == 'custom':
            rtmp_url = self.custom_rtmp_edit.text()
            if not rtmp_url:
                # Show error message for missing custom RTMP URL
                return
        else:
            platform = self.streaming_platforms[platform_key]
            rtmp_url = platform['rtmp'] + stream_key
            
        # Parse RTMP URL to get address and port
        try:
            if rtmp_url.startswith('rtmp://'):
                parts = rtmp_url[7:].split('/')
                if len(parts) > 0:
                    addr_port = parts[0].split(':')
                    if len(addr_port) == 2:
                        cs.stream_addr.set_text(addr_port[0])
                        cs.stream_port.set_number(int(addr_port[1]))
                    else:
                        cs.stream_addr.set_text(addr_port[0])
                        cs.stream_port.set_number(1935)  # Default RTMP port
                else:
                    # Invalid RTMP URL format
                    cs.is_streaming.set_flag(False)
                    return
            else:
                # Invalid RTMP URL format
                cs.is_streaming.set_flag(False)
                return
        except (ValueError, IndexError) as e:
            # Handle parsing errors
            cs.is_streaming.set_flag(False)
            return
        
        self.stream_btn.setText("Stop Streaming")
        self.stream_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        
    def stop_streaming(self):
        """Stop streaming"""
        cs = self.stream_output_backend.get_control_sheet()
        cs.is_streaming.set_flag(False)
        
        self.stream_btn.setText("Start Streaming")
        self.stream_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
    def toggle_recording(self):
        """Toggle recording on/off"""
        if self.record_btn.text() == "Start Recording":
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        """Start recording"""
        # Configure recording settings
        format_type = self.recording_format_combo.currentText()
        quality = self.recording_quality_combo.currentText()
        try:
            fps = int(self.recording_fps_combo.currentText())
        except ValueError:
            fps = 30  # Default FPS if conversion fails
        bitrate = self.recording_bitrate_spin.value()
        
        # Set recording path
        try:
            recording_path = Path(self.recording_path_edit.text())
            recording_path.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            # Handle directory creation errors
            return
        
        # Configure backend for recording
        cs = self.stream_output_backend.get_control_sheet()
        cs.save_sequence_path.set_paths([recording_path])
        
        self.record_btn.setText("Stop Recording")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        
    def stop_recording(self):
        """Stop recording"""
        cs = self.stream_output_backend.get_control_sheet()
        cs.save_sequence_path.set_paths([])
        
        self.record_btn.setText("Start Recording")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
        """)
        
    def open_settings(self):
        """Open settings dialog"""
        # This could open a more detailed settings dialog
        # For now, just show a message that settings are accessible via tabs
        pass
        
    def open_processing_window(self):
        """Open the processing controls window"""
        # For now, show a message that processing controls are available in the main interface
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Processing Controls", 
                              "Processing controls are integrated in the main interface.\n"
                              "Use the Face Swap tab in the right panel for advanced controls.")
        
        # TODO: Implement separate processing window when xlib compatibility issues are resolved
        # The separate window approach has compatibility issues with the xlib framework
        # For now, we'll keep the controls integrated in the main interface
        
    def add_scene(self):
        """Add a new scene"""
        scene_name = f"Scene {self.scenes_list.count() + 1}"
        scene_item = QListWidgetItem(scene_name)
        self.scenes_list.addItem(scene_item)
        self.scenes_list.setCurrentItem(scene_item)
        self.current_scene = scene_name
        self.scenes.append(scene_name)
        
    def remove_scene(self):
        """Remove the selected scene"""
        current_item = self.scenes_list.currentItem()
        if current_item and self.scenes_list.count() > 1:
            self.scenes_list.takeItem(self.scenes_list.row(current_item))
            
    def duplicate_scene(self):
        """Duplicate the selected scene"""
        current_item = self.scenes_list.currentItem()
        if current_item:
            scene_name = f"{current_item.text()} (Copy)"
            scene_item = QListWidgetItem(scene_name)
            self.scenes_list.addItem(scene_item)
            
    def add_source(self):
        """Add a new source"""
        source_types = ["Camera", "Image", "Video", "Audio", "Text", "Browser"]
        # This could open a dialog to select source type
        source_name = f"Source {self.sources_list.count() + 1}"
        source_item = QListWidgetItem(source_name)
        self.sources_list.addItem(source_item)
        
    def remove_source(self):
        """Remove the selected source"""
        current_item = self.sources_list.currentItem()
        if current_item:
            self.sources_list.takeItem(self.sources_list.row(current_item))
            
    def source_properties(self):
        """Open source properties dialog"""
        current_item = self.sources_list.currentItem()
        if current_item:
            # This could open a properties dialog for the selected source
            pass
            
    def on_platform_changed(self):
        """Handle platform selection change"""
        platform_key = self.platform_combo.currentData()
        if platform_key == 'custom':
            self.custom_rtmp_edit.setEnabled(True)
            self.stream_key_edit.setEnabled(False)
        else:
            self.custom_rtmp_edit.setEnabled(False)
            self.stream_key_edit.setEnabled(True)
            
    def on_scene_changed(self, current, previous):
        """Handle scene selection change"""
        if current:
            self.current_scene = current.text()
            
    def on_resolution_changed(self):
        """Handle resolution changes and validate compatibility"""
        base_res = self.base_resolution_combo.currentText()
        output_res = self.output_resolution_combo.currentText()
        
        # Basic validation - output resolution should not be higher than base
        base_width, base_height = map(int, base_res.split('x'))
        output_width, output_height = map(int, output_res.split('x'))
        
        if output_width > base_width or output_height > base_height:
            # Reset to base resolution if output is higher
            self.output_resolution_combo.setCurrentText(base_res)
            
    def on_face_swap_toggled(self, enabled):
        """Handle face swap enable/disable"""
        self.face_swap_quality_combo.setEnabled(enabled)
        
    def on_desktop_audio_toggled(self, enabled):
        """Handle desktop audio enable/disable"""
        # This could trigger backend audio configuration changes
        pass
        
    def on_monitor_audio_toggled(self, enabled):
        """Handle monitor audio enable/disable"""
        self.monitor_volume_slider.setEnabled(enabled)
        
    def update_preview(self, frame):
        """Update the preview with a new frame"""
        if frame is not None:
            # Convert frame to QPixmap and display in preview_label
            # This would need to be implemented based on the frame format
            pass
            
    def closeEvent(self, event):
        """Handle close event - ensure processing window is closed"""
        if self.processing_window and self.processing_window.isVisible():
            self.processing_window.close()
        event.accept()