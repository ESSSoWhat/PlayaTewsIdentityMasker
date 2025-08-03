from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon, QPalette
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from localization import L
from resources.fonts import QXFontDB
from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel

from ..backend import StreamOutput
from ..backend.StreamOutput import SourceType
from ..backend.EnhancedStreamOutput import (
    EnhancedStreamOutput,
    RecordingFormat,
    StreamingPlatform,
)
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


class PlatformSettingsDialog(QDialog):
    """Dialog for configuring streaming platform settings"""

    def __init__(self, platform: StreamingPlatform, parent=None):
        super().__init__(parent)
        self.platform = platform
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Configure {self.platform.name}")
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout()

        # Platform-specific settings
        form_layout = QFormLayout()

        self.enabled_checkbox = QCheckBox("Enable this platform")
        form_layout.addRow("Enabled:", self.enabled_checkbox)

        if self.platform != StreamingPlatform.CUSTOM_RTMP:
            self.stream_key_edit = QLineEdit()
            self.stream_key_edit.setPlaceholderText("Enter your stream key")
            self.stream_key_edit.setEchoMode(QLineEdit.Password)
            form_layout.addRow("Stream Key:", self.stream_key_edit)
        else:
            self.rtmp_url_edit = QLineEdit()
            self.rtmp_url_edit.setPlaceholderText(
                "rtmp://your-server.com/live/stream-key"
            )
            form_layout.addRow("RTMP URL:", self.rtmp_url_edit)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["1080p", "720p", "480p", "360p"])
        self.quality_combo.setCurrentText("720p")
        form_layout.addRow("Quality:", self.quality_combo)

        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["30", "60"])
        self.fps_combo.setCurrentText("30")
        form_layout.addRow("FPS:", self.fps_combo)

        self.bitrate_spin = QSpinBox()
        self.bitrate_spin.setRange(1000, 8000)
        self.bitrate_spin.setValue(2500)
        self.bitrate_spin.setSuffix(" kbps")
        form_layout.addRow("Bitrate:", self.bitrate_spin)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)


class QOBSStyleUI(qtx.QXWindow):
    """OBS Studio-style UI for DeepFaceLive with enhanced streaming and recording capabilities"""

    def __init__(
        self,
        stream_output_backend: StreamOutput,
        userdata_path: Path,
        face_swap_components=None,
        viewers_components=None,
    ):
        super().__init__()
        self.stream_output_backend = stream_output_backend
        self.userdata_path = userdata_path
        self.face_swap_components = face_swap_components or {}
        self.viewers_components = viewers_components or {}
        self.scenes = []
        self.current_scene = None
        self.sources_by_scene = {}  # Track sources per scene
        self.streaming_platforms = {
            "twitch": {"name": "Twitch", "rtmp": "rtmp://live.twitch.tv/app/"},
            "youtube": {"name": "YouTube", "rtmp": "rtmp://a.rtmp.youtube.com/live2/"},
            "facebook": {
                "name": "Facebook",
                "rtmp": "rtmp://live-api-s.facebook.com/rtmp/",
            },
            "custom": {"name": "Custom RTMP", "rtmp": ""},
        }
        self.recording_formats = ["mp4", "mkv", "avi", "mov"]
        self.recording_qualities = ["1080p", "720p", "480p", "360p"]

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

        # Create splitter for resizable panels (removed right panel)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.setSizes([250, 800])  # Adjusted sizes for two panels

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

        # Preview area (left side of top section) - Now contains merged frame viewer
        preview_group = QGroupBox("Active Screen")
        preview_layout = QVBoxLayout()

        # Use merged frame viewer as the main preview
        if "merged_frame_viewer" in self.viewers_components:
            self.main_preview = self.viewers_components["merged_frame_viewer"]
            # Remove size constraints and let it stretch to fill
            self.main_preview.setMinimumSize(400, 300)  # Smaller minimum
            self.main_preview.setMaximumSize(
                16777215, 16777215
            )  # Remove maximum size constraint
            self.main_preview.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )  # Stretch to fit
            # Set stretch factor to take all available space
            preview_layout.addWidget(self.main_preview, 1)  # Stretch factor of 1
        else:
            self.main_preview = QLabel("Merged Frame Preview")
            self.main_preview.setMinimumSize(400, 300)  # Smaller minimum
            self.main_preview.setMaximumSize(
                16777215, 16777215
            )  # Remove maximum size constraint
            self.main_preview.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )  # Stretch to fit
            self.main_preview.setStyleSheet(
                """
                QLabel {
                    background-color: #1e1e1e;
                    border: 2px solid #404040;
                    border-radius: 5px;
                    color: #ffffff;
                    font-size: 16px;
                }
            """
            )
            self.main_preview.setAlignment(Qt.AlignCenter)
            # Set stretch factor to take all available space
            preview_layout.addWidget(self.main_preview, 1)  # Stretch factor of 1

        preview_group.setLayout(preview_layout)

        # Controls area (right side of top section)
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()

        # Streaming controls
        self.stream_btn = QPushButton("Start Streaming")
        self.stream_btn.setMinimumHeight(40)
        self.stream_btn.setStyleSheet(
            """
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
        """
        )

        # Recording controls
        self.record_btn = QPushButton("Start Recording")
        self.record_btn.setMinimumHeight(40)
        self.record_btn.setStyleSheet(
            """
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
        """
        )

        # Global Face Swap Control Button
        self.global_face_swap_btn = QPushButton("Face Swap: ON")
        self.global_face_swap_btn.setMinimumHeight(40)
        self.global_face_swap_btn.setCheckable(True)
        self.global_face_swap_btn.setChecked(True)  # Default to ON
        self.global_face_swap_btn.setToolTip(
            "Click to toggle all face swap components on/off\nGreen = ON, Red = OFF"
        )
        self.global_face_swap_btn.setStyleSheet(
            """
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
            QPushButton:checked {
                background-color: #27ae60;
            }
            QPushButton:!checked {
                background-color: #e74c3c;
            }
        """
        )

        # Settings button
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setMinimumHeight(30)

        # Processing window button
        self.processing_btn = QPushButton("All Controls")
        self.processing_btn.setMinimumHeight(30)
        self.processing_btn.setStyleSheet(
            """
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
        """
        )

        controls_layout.addWidget(self.stream_btn)
        controls_layout.addWidget(self.record_btn)
        controls_layout.addWidget(self.global_face_swap_btn)
        controls_layout.addWidget(self.settings_btn)
        controls_layout.addWidget(self.processing_btn)
        controls_layout.addStretch()

        controls_group.setLayout(controls_layout)

        # Add preview and controls to top section - give more space to preview
        top_layout.addWidget(preview_group, 3)  # Stretch factor of 3 for preview
        top_layout.addWidget(controls_group, 1)  # Stretch factor of 1 for controls
        top_section.setLayout(top_layout)

        # Bottom section: Viewers
        bottom_section = QWidget()
        bottom_layout = QVBoxLayout()

        # Viewers group
        viewers_group = QGroupBox("Processing Views")
        viewers_layout = QHBoxLayout()

        # Use actual viewers if available, otherwise create placeholders
        if "frame_viewer" in self.viewers_components:
            frame_viewer = self.viewers_components["frame_viewer"]
            frame_viewer.setMinimumSize(150, 120)  # Smaller size
        else:
            frame_viewer = QLabel("Frame Viewer")
            frame_viewer.setMinimumSize(150, 120)  # Smaller size
            frame_viewer.setStyleSheet(
                """
                QLabel {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #cccccc;
                    font-size: 12px;
                }
            """
            )
            frame_viewer.setAlignment(Qt.AlignCenter)

        if "face_align_viewer" in self.viewers_components:
            face_align_viewer = self.viewers_components["face_align_viewer"]
            face_align_viewer.setMinimumSize(150, 120)  # Smaller size
        else:
            face_align_viewer = QLabel("Face Align Viewer")
            face_align_viewer.setMinimumSize(150, 120)  # Smaller size
            face_align_viewer.setStyleSheet(
                """
                QLabel {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #cccccc;
                    font-size: 12px;
                }
            """
            )
            face_align_viewer.setAlignment(Qt.AlignCenter)

        if "face_swap_viewer" in self.viewers_components:
            face_swap_viewer = self.viewers_components["face_swap_viewer"]
            face_swap_viewer.setMinimumSize(150, 120)  # Smaller size
        else:
            face_swap_viewer = QLabel("Face Swap Viewer")
            face_swap_viewer.setMinimumSize(150, 120)  # Smaller size
            face_swap_viewer.setStyleSheet(
                """
                QLabel {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #cccccc;
                    font-size: 12px;
                }
            """
            )
            face_swap_viewer.setAlignment(Qt.AlignCenter)

        # Only show the smaller viewers in the bottom section
        viewers_layout.addWidget(frame_viewer)
        viewers_layout.addWidget(face_align_viewer)
        viewers_layout.addWidget(face_swap_viewer)

        viewers_group.setLayout(viewers_layout)
        bottom_layout.addWidget(viewers_group)
        bottom_section.setLayout(bottom_layout)

        # Add sections to main layout - give more space to preview area
        layout.addWidget(top_section, 4)  # Stretch factor of 4 for preview area
        layout.addWidget(bottom_section, 1)  # Stretch factor of 1 for bottom viewers

        panel.setLayout(layout)
        return panel 

    def create_enhanced_streaming_tab(self):
        """Create the enhanced streaming configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Main streaming controls
        controls_group = QGroupBox("Streaming Controls")
        controls_layout = QGridLayout()

        # FPS display
        q_average_fps_label = QLabelPopupInfo(
            label=L("@QEnhancedStreamOutput.avg_fps"),
            popup_info_text=L("@QEnhancedStreamOutput.help.avg_fps"),
        )
        try:
            if hasattr(self.stream_output_backend, 'get_control_sheet'):
                cs = self.stream_output_backend.get_control_sheet()
                q_average_fps = QLabelCSWNumber(
                    cs.avg_fps, reflect_state_widgets=[q_average_fps_label]
                )
            else:
                q_average_fps = QLabel("0.0")
                q_average_fps.setStyleSheet("QLabel { color: #888888; }")
        except Exception as e:
            print(f"Warning: Could not create FPS display: {e}")
            q_average_fps = QLabel("0.0")
            q_average_fps.setStyleSheet("QLabel { color: #888888; }")

        # Streaming toggle
        q_is_streaming_label = QLabelPopupInfo(label="Multi-Platform Streaming")
        try:
            if hasattr(self.stream_output_backend, 'get_control_sheet'):
                cs = self.stream_output_backend.get_control_sheet()
                q_is_streaming = QCheckBoxCSWFlag(
                    cs.is_streaming, reflect_state_widgets=[q_is_streaming_label]
                )
            else:
                q_is_streaming = QCheckBox("Streaming")
        except Exception as e:
            print(f"Warning: Could not create streaming toggle: {e}")
            q_is_streaming = QCheckBox("Streaming")

        # Multi-platform toggle
        q_multi_platform_label = QLabelPopupInfo(label="Enable Multi-Platform")
        try:
            if hasattr(self.stream_output_backend, 'get_control_sheet'):
                cs = self.stream_output_backend.get_control_sheet()
                q_multi_platform = QCheckBoxCSWFlag(
                    cs.multi_platform_streaming, reflect_state_widgets=[q_multi_platform_label]
                )
            else:
                q_multi_platform = QCheckBox("Multi-Platform")
        except Exception as e:
            print(f"Warning: Could not create multi-platform toggle: {e}")
            q_multi_platform = QCheckBox("Multi-Platform")

        controls_layout.addWidget(q_average_fps_label, 0, 0)
        controls_layout.addWidget(q_average_fps, 0, 1)
        controls_layout.addWidget(q_is_streaming_label, 1, 0)
        controls_layout.addWidget(q_is_streaming, 1, 1)
        controls_layout.addWidget(q_multi_platform_label, 2, 0)
        controls_layout.addWidget(q_multi_platform, 2, 1)

        controls_group.setLayout(controls_layout)

        # Platform configuration
        platforms_group = QGroupBox("Streaming Platforms")
        platforms_layout = QVBoxLayout()

        self.platform_buttons = {}
        for platform in StreamingPlatform:
            if platform != StreamingPlatform.MULTI_PLATFORM:
                btn = QPushButton(f"Configure {platform.name}")
                btn.clicked.connect(
                    lambda checked, p=platform: self.configure_platform(p)
                )
                self.platform_buttons[platform] = btn
                platforms_layout.addWidget(btn)

        platforms_group.setLayout(platforms_layout)

        # Legacy streaming settings (for backward compatibility)
        legacy_group = QGroupBox("Legacy Streaming")
        legacy_layout = QGridLayout()

        try:
            if hasattr(self.stream_output_backend, 'get_control_sheet'):
                cs = self.stream_output_backend.get_control_sheet()
                q_stream_addr = QLineEditCSWText(
                    cs.stream_addr, font=QXFontDB.get_fixedwidth_font()
                )
                q_stream_port = QSpinBoxCSWNumber(cs.stream_port)
            else:
                q_stream_addr = QLineEdit()
                q_stream_port = QSpinBox()
        except Exception as e:
            print(f"Warning: Could not create legacy streaming controls: {e}")
            q_stream_addr = QLineEdit()
            q_stream_port = QSpinBox()

        legacy_layout.addWidget(QLabel("Stream Address:"), 0, 0)
        legacy_layout.addWidget(q_stream_addr, 0, 1)
        legacy_layout.addWidget(QLabel("Stream Port:"), 1, 0)
        legacy_layout.addWidget(q_stream_port, 1, 1)

        legacy_group.setLayout(legacy_layout)

        layout.addWidget(controls_group)
        layout.addWidget(platforms_group)
        layout.addWidget(legacy_group)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def create_enhanced_recording_tab(self):
        """Create the enhanced recording configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Recording controls
        recording_group = QGroupBox("Recording Controls")
        recording_layout = QGridLayout()

        try:
            if hasattr(self.stream_output_backend, 'get_control_sheet'):
                cs = self.stream_output_backend.get_control_sheet()
                q_recording_enabled_label = QLabelPopupInfo(label="Enable Recording")
                q_recording_enabled = QCheckBoxCSWFlag(
                    cs.recording_enabled, reflect_state_widgets=[q_recording_enabled_label]
                )
            else:
                q_recording_enabled_label = QLabel("Enable Recording")
                q_recording_enabled = QCheckBox("Recording")
        except Exception as e:
            print(f"Warning: Could not create recording controls: {e}")
            q_recording_enabled_label = QLabel("Enable Recording")
            q_recording_enabled = QCheckBox("Recording")

        recording_layout.addWidget(q_recording_enabled_label, 0, 0)
        recording_layout.addWidget(q_recording_enabled, 0, 1)

        recording_group.setLayout(recording_layout)

        # Recording settings
        settings_group = QGroupBox("Recording Settings")
        settings_layout = QGridLayout()

        self.recording_format_combo = QComboBox()
        for format_type in RecordingFormat:
            self.recording_format_combo.addItem(format_type.name, format_type)
        self.recording_format_combo.setCurrentText("MP4")

        self.recording_quality_combo = QComboBox()
        self.recording_quality_combo.addItems(["1080p", "720p", "480p", "360p"])
        self.recording_quality_combo.setCurrentText("1080p")

        self.recording_fps_combo = QComboBox()
        self.recording_fps_combo.addItems(["30", "60"])
        self.recording_fps_combo.setCurrentText("30")

        self.recording_bitrate_spin = QSpinBox()
        self.recording_bitrate_spin.setRange(1000, 50000)
        self.recording_bitrate_spin.setValue(8000)
        self.recording_bitrate_spin.setSuffix(" kbps")

        settings_layout.addWidget(QLabel("Format:"), 0, 0)
        settings_layout.addWidget(self.recording_format_combo, 0, 1)
        settings_layout.addWidget(QLabel("Quality:"), 1, 0)
        settings_layout.addWidget(self.recording_quality_combo, 1, 1)
        settings_layout.addWidget(QLabel("FPS:"), 2, 0)
        settings_layout.addWidget(self.recording_fps_combo, 2, 1)
        settings_layout.addWidget(QLabel("Bitrate:"), 3, 0)
        settings_layout.addWidget(self.recording_bitrate_spin, 3, 1)

        settings_group.setLayout(settings_layout)

        # Legacy recording settings
        legacy_group = QGroupBox("Legacy Recording")
        legacy_layout = QGridLayout()

        try:
            if hasattr(self.stream_output_backend, 'get_control_sheet'):
                cs = self.stream_output_backend.get_control_sheet()
                q_save_sequence_path_label = QLabelPopupInfo(
                    label=L("@QEnhancedStreamOutput.save_sequence_path"),
                    popup_info_text=L("@QEnhancedStreamOutput.help.save_sequence_path"),
                )
                q_save_sequence_path = QPathEditCSWPaths(
                    cs.save_sequence_path, reflect_state_widgets=[q_save_sequence_path_label]
                )
                q_save_sequence_path_error = QErrorCSWError(cs.save_sequence_path_error)

                q_save_fill_frame_gap_label = QLabelPopupInfo(
                    label=L("@QEnhancedStreamOutput.save_fill_frame_gap"),
                    popup_info_text=L("@QEnhancedStreamOutput.help.save_fill_frame_gap"),
                )
                q_save_fill_frame_gap = QCheckBoxCSWFlag(
                    cs.save_fill_frame_gap, reflect_state_widgets=[q_save_fill_frame_gap_label]
                )
            else:
                q_save_sequence_path_label = QLabel("Save Sequence Path")
                q_save_sequence_path = QLineEdit()
                q_save_sequence_path_error = QLabel("")
                q_save_fill_frame_gap_label = QLabel("Fill Frame Gap")
                q_save_fill_frame_gap = QCheckBox()
        except Exception as e:
            print(f"Warning: Could not create legacy recording controls: {e}")
            q_save_sequence_path_label = QLabel("Save Sequence Path")
            q_save_sequence_path = QLineEdit()
            q_save_sequence_path_error = QLabel("")
            q_save_fill_frame_gap_label = QLabel("Fill Frame Gap")
            q_save_fill_frame_gap = QCheckBox()

        legacy_layout.addWidget(q_save_sequence_path_label, 0, 0)
        legacy_layout.addWidget(q_save_sequence_path, 0, 1)
        legacy_layout.addWidget(q_save_sequence_path_error, 1, 0, 1, 2)
        legacy_layout.addWidget(q_save_fill_frame_gap_label, 2, 0)
        legacy_layout.addWidget(q_save_fill_frame_gap, 2, 1)

        legacy_group.setLayout(legacy_layout)

        layout.addWidget(recording_group)
        layout.addWidget(settings_group)
        layout.addWidget(legacy_group)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def configure_platform(self, platform: StreamingPlatform):
        """Open platform configuration dialog"""
        dialog = PlatformSettingsDialog(platform, self)
        if dialog.exec_() == QDialog.Accepted:
            # Apply platform settings
            # This would update the backend with the new settings
            pass

    def setup_styles(self):
        """Setup the OBS Studio-like dark theme"""
        self.setStyleSheet(
            """
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
        """
        )

    def setup_connections(self):
        """Setup signal connections"""
        # Connect processing window button
        self.processing_btn.clicked.connect(self.open_processing_window)

        # Connect global face swap control
        self.global_face_swap_btn.toggled.connect(self.on_global_face_swap_toggled)

        # Connect streaming and recording buttons
        self.stream_btn.clicked.connect(self.toggle_streaming)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.settings_btn.clicked.connect(self.open_settings_window)

        # Initialize processing window
        self.processing_window = None
        self.settings_window = None

        # Initialize global face swap state
        self.initialize_global_face_swap_state()

    def toggle_streaming(self):
        """Toggle streaming on/off"""
        try:
            if hasattr(self.stream_output_backend, 'get_control_sheet'):
                cs = self.stream_output_backend.get_control_sheet()
                if hasattr(cs, 'is_streaming'):
                    current_state = cs.is_streaming.get()
                    cs.is_streaming.set(not current_state)
                    
                    if not current_state:
                        self.stream_btn.setText("Stop Streaming")
                        self.stream_btn.setStyleSheet(
                            """
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
                        """
                        )
                    else:
                        self.stream_btn.setText("Start Streaming")
                        self.stream_btn.setStyleSheet(
                            """
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
                        """
                        )
        except Exception as e:
            print(f"Error toggling streaming: {e}")

    def toggle_recording(self):
        """Toggle recording on/off"""
        try:
            if hasattr(self.stream_output_backend, 'get_control_sheet'):
                cs = self.stream_output_backend.get_control_sheet()
                if hasattr(cs, 'recording_enabled'):
                    current_state = cs.recording_enabled.get()
                    cs.recording_enabled.set(not current_state)
                    
                    if not current_state:
                        self.record_btn.setText("Stop Recording")
                        self.record_btn.setStyleSheet(
                            """
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
                        """
                        )
                    else:
                        self.record_btn.setText("Start Recording")
                        self.record_btn.setStyleSheet(
                            """
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
                        """
                        )
        except Exception as e:
            print(f"Error toggling recording: {e}")

    def open_settings_window(self):
        """Open the settings window with enhanced streaming controls"""
        if self.settings_window is None or not self.settings_window.isVisible():
            try:
                self.settings_window = self.create_settings_window()
                self.settings_window.show()
            except Exception as e:
                print(f"Error creating settings window: {e}")
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Settings",
                    "Settings window not available.\n"
                    "Settings are integrated in the main interface.",
                )
        else:
            self.settings_window.raise_()
            self.settings_window.activateWindow()

    def create_settings_window(self):
        """Create a settings window with enhanced streaming controls"""
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget

        # Create dialog window
        window = QDialog(self)
        window.setWindowTitle("PlayaTewsIdentityMasker - Settings")
        window.setMinimumSize(800, 600)
        window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)

        # Main layout
        layout = QVBoxLayout()

        # Create tab widget
        tab_widget = QTabWidget()

        # Create tabs for different categories
        tabs = {
            "Enhanced Streaming": self.create_enhanced_streaming_tab(),
            "Enhanced Recording": self.create_enhanced_recording_tab(),
            "Input Sources": self.create_input_sources_tab(),
            "Face Detection": self.create_face_detection_tab(),
            "Face Swapping": self.create_face_swapping_tab(),
            "Animation & Effects": self.create_animation_effects_tab(),
            "Output & Streaming": self.create_output_streaming_tab(),
        }

        # Add tabs to widget
        for tab_name, tab_widget_content in tabs.items():
            tab_widget.addTab(tab_widget_content, tab_name)

        layout.addWidget(tab_widget)
        window.setLayout(layout)

        return window

    def open_processing_window(self):
        """Open the processing controls window"""
        if self.processing_window is None or not self.processing_window.isVisible():
            try:
                # Create a safer processing window that handles CSW issues
                self.processing_window = self.create_safe_processing_window()
                self.processing_window.show()
            except Exception as e:
                print(f"Error creating processing window: {e}")
                # Fallback: show a simple message
                from PyQt5.QtWidgets import QMessageBox

                QMessageBox.information(
                    self,
                    "All Controls",
                    "All controls window not available.\n"
                    "Controls are integrated in the main interface.",
                )
        else:
            self.processing_window.raise_()
            self.processing_window.activateWindow()

    def create_safe_processing_window(self):
        """Create a safe processing window that handles CSW issues"""
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import (
            QDialog,
            QGroupBox,
            QLabel,
            QPushButton,
            QScrollArea,
            QTabWidget,
            QVBoxLayout,
            QWidget,
        )

        # Create dialog window
        window = QDialog(self)
        window.setWindowTitle("PlayaTewsIdentityMasker - All Controls")
        window.setMinimumSize(1000, 700)
        window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)

        # Main layout
        layout = QVBoxLayout()

        # Create tab widget
        tab_widget = QTabWidget()

        # Create tabs for different categories
        tabs = {
            "Input Sources": self.create_input_sources_tab(),
            "Face Detection": self.create_face_detection_tab(),
            "Face Swapping": self.create_face_swapping_tab(),
            "Animation & Effects": self.create_animation_effects_tab(),
            "Output & Streaming": self.create_output_streaming_tab(),
        }

        # Add tabs to widget
        for tab_name, tab_widget_content in tabs.items():
            tab_widget.addTab(tab_widget_content, tab_name)

        layout.addWidget(tab_widget)
        window.setLayout(layout)

        return window

    def create_input_sources_tab(self):
        """Create input sources tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # File Source
        if "file_source" in self.face_swap_components:
            try:
                file_source = self.face_swap_components["file_source"]
                if hasattr(file_source, "widget"):
                    layout.addWidget(QLabel("📁 File Source"))
                    layout.addWidget(file_source.widget())
                elif hasattr(file_source, "__class__"):
                    layout.addWidget(QLabel("📁 File Source"))
                    layout.addWidget(file_source)
                else:
                    layout.addWidget(QLabel("📁 File Source: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"📁 File Source: Error - {e}"))
        else:
            layout.addWidget(QLabel("📁 File Source: Not Available"))

        # Camera Source
        if "camera_source" in self.face_swap_components:
            try:
                camera_source = self.face_swap_components["camera_source"]
                if hasattr(camera_source, "widget"):
                    layout.addWidget(QLabel("📹 Camera Source"))
                    layout.addWidget(camera_source.widget())
                elif hasattr(camera_source, "__class__"):
                    layout.addWidget(QLabel("📹 Camera Source"))
                    layout.addWidget(camera_source)
                else:
                    layout.addWidget(QLabel("📹 Camera Source: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"📹 Camera Source: Error - {e}"))
        else:
            layout.addWidget(QLabel("📹 Camera Source: Not Available"))

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def create_face_detection_tab(self):
        """Create face detection tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Face Detector
        if "face_detector" in self.face_swap_components:
            try:
                face_detector = self.face_swap_components["face_detector"]
                if hasattr(face_detector, "widget"):
                    layout.addWidget(QLabel("👁️ Face Detector"))
                    layout.addWidget(face_detector.widget())
                elif hasattr(face_detector, "__class__"):
                    layout.addWidget(QLabel("👁️ Face Detector"))
                    layout.addWidget(face_detector)
                else:
                    layout.addWidget(QLabel("👁️ Face Detector: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"👁️ Face Detector: Error - {e}"))
        else:
            layout.addWidget(QLabel("👁️ Face Detector: Not Available"))

        # Face Marker
        if "face_marker" in self.face_swap_components:
            try:
                face_marker = self.face_swap_components["face_marker"]
                if hasattr(face_marker, "widget"):
                    layout.addWidget(QLabel("📍 Face Marker"))
                    layout.addWidget(face_marker.widget())
                elif hasattr(face_marker, "__class__"):
                    layout.addWidget(QLabel("📍 Face Marker"))
                    layout.addWidget(face_marker)
                else:
                    layout.addWidget(QLabel("📍 Face Marker: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"📍 Face Marker: Error - {e}"))
        else:
            layout.addWidget(QLabel("📍 Face Marker: Not Available"))

        # Face Aligner
        if "face_aligner" in self.face_swap_components:
            try:
                face_aligner = self.face_swap_components["face_aligner"]
                if hasattr(face_aligner, "widget"):
                    layout.addWidget(QLabel("🎯 Face Aligner"))
                    layout.addWidget(face_aligner.widget())
                elif hasattr(face_aligner, "__class__"):
                    layout.addWidget(QLabel("🎯 Face Aligner"))
                    layout.addWidget(face_aligner)
                else:
                    layout.addWidget(QLabel("🎯 Face Aligner: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"🎯 Face Aligner: Error - {e}"))
        else:
            layout.addWidget(QLabel("🎯 Face Aligner: Not Available"))

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def create_face_swapping_tab(self):
        """Create face swapping tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Face Swap Insight
        if "face_swap_insight" in self.face_swap_components:
            try:
                face_swap_insight = self.face_swap_components["face_swap_insight"]
                if hasattr(face_swap_insight, "widget"):
                    layout.addWidget(QLabel("🔄 Face Swap Insight"))
                    layout.addWidget(face_swap_insight.widget())
                elif hasattr(face_swap_insight, "__class__"):
                    layout.addWidget(QLabel("🔄 Face Swap Insight"))
                    layout.addWidget(face_swap_insight)
                else:
                    layout.addWidget(QLabel("🔄 Face Swap Insight: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"🔄 Face Swap Insight: Error - {e}"))
        else:
            layout.addWidget(QLabel("🔄 Face Swap Insight: Not Available"))

        # Face Swap DFM
        if "face_swap_dfm" in self.face_swap_components:
            try:
                face_swap_dfm = self.face_swap_components["face_swap_dfm"]
                if hasattr(face_swap_dfm, "widget"):
                    layout.addWidget(QLabel("🔄 Face Swap DFM"))
                    layout.addWidget(face_swap_dfm.widget())
                elif hasattr(face_swap_dfm, "__class__"):
                    layout.addWidget(QLabel("🔄 Face Swap DFM"))
                    layout.addWidget(face_swap_dfm)
                else:
                    layout.addWidget(QLabel("🔄 Face Swap DFM: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"🔄 Face Swap DFM: Error - {e}"))
        else:
            layout.addWidget(QLabel("🔄 Face Swap DFM: Not Available"))

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def create_animation_effects_tab(self):
        """Create animation and effects tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Face Animator
        if "face_animator" in self.face_swap_components:
            try:
                face_animator = self.face_swap_components["face_animator"]
                if hasattr(face_animator, "widget"):
                    layout.addWidget(QLabel("🎭 Face Animator"))
                    layout.addWidget(face_animator.widget())
                elif hasattr(face_animator, "__class__"):
                    layout.addWidget(QLabel("🎭 Face Animator"))
                    layout.addWidget(face_animator)
                else:
                    layout.addWidget(QLabel("🎭 Face Animator: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"🎭 Face Animator: Error - {e}"))
        else:
            layout.addWidget(QLabel("🎭 Face Animator: Not Available"))

        # Frame Adjuster
        if "frame_adjuster" in self.face_swap_components:
            try:
                frame_adjuster = self.face_swap_components["frame_adjuster"]
                if hasattr(frame_adjuster, "widget"):
                    layout.addWidget(QLabel("🎨 Frame Adjuster"))
                    layout.addWidget(frame_adjuster.widget())
                elif hasattr(frame_adjuster, "__class__"):
                    layout.addWidget(QLabel("🎨 Frame Adjuster"))
                    layout.addWidget(frame_adjuster)
                else:
                    layout.addWidget(QLabel("🎨 Frame Adjuster: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"🎨 Frame Adjuster: Error - {e}"))
        else:
            layout.addWidget(QLabel("🎨 Frame Adjuster: Not Available"))

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def create_output_streaming_tab(self):
        """Create output and streaming tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Face Merger
        if "face_merger" in self.face_swap_components:
            try:
                face_merger = self.face_swap_components["face_merger"]
                if hasattr(face_merger, "widget"):
                    layout.addWidget(QLabel("🔗 Face Merger"))
                    layout.addWidget(face_merger.widget())
                elif hasattr(face_merger, "__class__"):
                    layout.addWidget(QLabel("🔗 Face Merger"))
                    layout.addWidget(face_merger)
                else:
                    layout.addWidget(QLabel("🔗 Face Merger: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"🔗 Face Merger: Error - {e}"))
        else:
            layout.addWidget(QLabel("🔗 Face Merger: Not Available"))

        # Stream Output
        if "stream_output" in self.face_swap_components:
            try:
                stream_output = self.face_swap_components["stream_output"]
                if hasattr(stream_output, "widget"):
                    layout.addWidget(QLabel("📺 Stream Output"))
                    layout.addWidget(stream_output.widget())
                elif hasattr(stream_output, "__class__"):
                    layout.addWidget(QLabel("📺 Stream Output"))
                    layout.addWidget(stream_output)
                else:
                    layout.addWidget(QLabel("📺 Stream Output: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"📺 Stream Output: Error - {e}"))
        else:
            layout.addWidget(QLabel("📺 Stream Output: Not Available"))

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def closeEvent(self, event):
        """Handle close event - ensure processing window is closed"""
        if self.processing_window and self.processing_window.isVisible():
            self.processing_window.close()
        if self.settings_window and self.settings_window.isVisible():
            self.settings_window.close()
        event.accept()

    # Global face swap control methods
    def on_global_face_swap_toggled(self, enabled):
        """Handle global face swap enable/disable"""
        try:
            if enabled:
                self.global_face_swap_btn.setText("Face Swap: ON")
                self.global_face_swap_btn.setToolTip(
                    "Face swap is ENABLED\nAll components are running\nClick to disable"
                )
                self.enable_all_face_swap_components()
                print("Global face swap enabled")
            else:
                self.global_face_swap_btn.setText("Face Swap: OFF")
                self.global_face_swap_btn.setToolTip(
                    "Face swap is DISABLED\nAll components are stopped\nClick to enable"
                )
                self.disable_all_face_swap_components()
                print("Global face swap disabled")

            # Save the state
            self.save_global_face_swap_state(enabled)

        except Exception as e:
            print(f"Error toggling global face swap: {e}")

    def enable_all_face_swap_components(self):
        """Enable all face swap components"""
        if not self.face_swap_components:
            return

        # List of components to enable
        components_to_enable = [
            "face_detector",
            "face_marker",
            "face_aligner",
            "face_swap_dfm",
            "frame_adjuster",
            "face_merger",
        ]

        for component_name in components_to_enable:
            if component_name in self.face_swap_components:
                component = self.face_swap_components[component_name]
                try:
                    # Try to enable the component through its backend
                    if hasattr(component, "_backend") and hasattr(
                        component._backend, "start"
                    ):
                        component._backend.start()
                    # Also try to enable any checkboxes in the component
                    self._enable_component_checkboxes(component, True)
                except Exception as e:
                    print(f"Error enabling {component_name}: {e}")

    def disable_all_face_swap_components(self):
        """Disable all face swap components"""
        if not self.face_swap_components:
            return

        # List of components to disable
        components_to_disable = [
            "face_detector",
            "face_marker",
            "face_aligner",
            "face_swap_dfm",
            "frame_adjuster",
            "face_merger",
        ]

        for component_name in components_to_disable:
            if component_name in self.face_swap_components:
                component = self.face_swap_components[component_name]
                try:
                    # Try to disable the component through its backend
                    if hasattr(component, "_backend") and hasattr(
                        component._backend, "stop"
                    ):
                        component._backend.stop()
                    # Also try to disable any checkboxes in the component
                    self._enable_component_checkboxes(component, False)
                except Exception as e:
                    print(f"Error disabling {component_name}: {e}")

    def _enable_component_checkboxes(self, component, enabled):
        """Enable or disable checkboxes in a component"""
        try:
            from PyQt5.QtWidgets import QCheckBox

            checkboxes = component.findChildren(QCheckBox)
            for checkbox in checkboxes:
                if checkbox.isCheckable():
                    checkbox.setChecked(enabled)
        except Exception as e:
            print(f"Error setting checkboxes in component: {e}")

    def save_global_face_swap_state(self, enabled):
        """Save the global face swap state to persistent storage"""
        try:
            import json
            from pathlib import Path

            # Create settings directory if it doesn't exist
            settings_dir = Path(self.userdata_path) / "settings"
            settings_dir.mkdir(parents=True, exist_ok=True)

            # Save to a JSON file
            state_file = settings_dir / "global_face_swap_state.json"
            state_data = {
                "enabled": enabled,
                "timestamp": str(Path().stat().st_mtime) if Path().exists() else "0",
            }

            with open(state_file, "w") as f:
                json.dump(state_data, f, indent=2)

        except Exception as e:
            print(f"Error saving global face swap state: {e}")

    def load_global_face_swap_state(self):
        """Load the global face swap state from persistent storage"""
        try:
            import json
            from pathlib import Path

            state_file = (
                Path(self.userdata_path) / "settings" / "global_face_swap_state.json"
            )

            if state_file.exists():
                with open(state_file, "r") as f:
                    state_data = json.load(f)

                enabled = state_data.get("enabled", True)  # Default to True
                return enabled
            else:
                return True  # Default to enabled if no saved state

        except Exception as e:
            print(f"Error loading global face swap state: {e}")
            return True  # Default to enabled on error

    def initialize_global_face_swap_state(self):
        """Initialize the global face swap state on startup"""
        try:
            enabled = self.load_global_face_swap_state()
            self.global_face_swap_btn.setChecked(enabled)
            self.on_global_face_swap_toggled(enabled)
        except Exception as e:
            print(f"Error initializing global face swap state: {e}") 