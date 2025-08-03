import json
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

from localization import L, Localization
from resources.fonts import QXFontDB
from resources.gfx import QXImageDB
from xlib import os as lib_os
from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel

from . import backend
from .streaming import (
    RecordingEngine,
    StreamConfig,
    StreamingEngine,
    StreamPlatform,
    get_platform_config,
    validate_stream_config,
)
from .ui.QCameraSource import QCameraSource
from .ui.QFaceAligner import QFaceAligner
from .ui.QFaceAnimator import QFaceAnimator
from .ui.QFaceDetector import QFaceDetector
from .ui.QFaceMarker import QFaceMarker
from .ui.QFaceMerger import QFaceMerger
from .ui.QFaceSwapDFM import QFaceSwapDFM
from .ui.QFaceSwapInsight import QFaceSwapInsight
from .ui.QFileSource import QFileSource
from .ui.QFrameAdjuster import QFrameAdjuster
from .ui.QStreamOutput import QStreamOutput
from .ui.widgets.QBCFaceAlignViewer import QBCFaceAlignViewer
from .ui.widgets.QBCFaceSwapViewer import QBCFaceSwapViewer
from .ui.widgets.QBCFrameViewer import QBCFrameViewer
from .ui.widgets.QBCMergedFrameViewer import QBCMergedFrameViewer


@dataclass
class Scene:
    name: str
    sources: List[Dict[str, Any]]
    active: bool = False


class QOBSSceneManager(qtx.QXWidget):
    def __init__(self):
        super().__init__()
        self.scenes = []
        self.current_scene_index = 0
        self._init_ui()

    def _init_ui(self):
        layout = qtx.QXVBoxLayout()

        # Scene controls
        scene_controls_layout = qtx.QXHBoxLayout()

        self.add_scene_btn = qtx.QXPushButton(text="Add Scene", clicked=self._add_scene)
        self.remove_scene_btn = qtx.QXPushButton(
            text="Remove Scene", clicked=self._remove_scene
        )
        self.duplicate_scene_btn = qtx.QXPushButton(
            text="Duplicate Scene", clicked=self._duplicate_scene
        )

        scene_controls_layout.addWidget(self.add_scene_btn)
        scene_controls_layout.addWidget(self.remove_scene_btn)
        scene_controls_layout.addWidget(self.duplicate_scene_btn)

        layout.addLayout(scene_controls_layout)

        # Scene list
        self.scene_list = qtx.QXListWidget()
        self.scene_list.currentRowChanged.connect(self._on_scene_changed)
        layout.addWidget(self.scene_list)

        # Scene sources
        sources_label = qtx.QXLabel(text="Sources")
        sources_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(sources_label)

        # Source controls
        source_controls_layout = qtx.QXHBoxLayout()

        self.add_source_btn = qtx.QXPushButton(text="+", clicked=self._add_source)
        self.remove_source_btn = qtx.QXPushButton(text="-", clicked=self._remove_source)
        self.source_up_btn = qtx.QXPushButton(text="↑", clicked=self._move_source_up)
        self.source_down_btn = qtx.QXPushButton(
            text="↓", clicked=self._move_source_down
        )

        source_controls_layout.addWidget(self.add_source_btn)
        source_controls_layout.addWidget(self.remove_source_btn)
        source_controls_layout.addWidget(self.source_up_btn)
        source_controls_layout.addWidget(self.source_down_btn)
        source_controls_layout.addStretch()

        layout.addLayout(source_controls_layout)

        # Source list
        self.source_list = qtx.QXListWidget()
        layout.addWidget(self.source_list)

        self.setLayout(layout)

        # Add default scene
        self._add_default_scene()

    def _add_default_scene(self):
        default_scene = Scene(name="Scene 1", sources=[], active=True)
        self.scenes.append(default_scene)
        self.scene_list.addItem("Scene 1")
        self.scene_list.setCurrentRow(0)

    def _add_scene(self):
        scene_name = f"Scene {len(self.scenes) + 1}"
        new_scene = Scene(name=scene_name, sources=[])
        self.scenes.append(new_scene)
        self.scene_list.addItem(scene_name)

    def _remove_scene(self):
        current_row = self.scene_list.currentRow()
        if current_row >= 0 and len(self.scenes) > 1:
            self.scenes.pop(current_row)
            self.scene_list.takeItem(current_row)

    def _duplicate_scene(self):
        current_row = self.scene_list.currentRow()
        if current_row >= 0:
            current_scene = self.scenes[current_row]
            new_scene = Scene(
                name=f"{current_scene.name} Copy", sources=current_scene.sources.copy()
            )
            self.scenes.append(new_scene)
            self.scene_list.addItem(new_scene.name)

    def _on_scene_changed(self, index):
        if 0 <= index < len(self.scenes):
            # Deactivate current scene
            if 0 <= self.current_scene_index < len(self.scenes):
                self.scenes[self.current_scene_index].active = False

            # Activate new scene
            self.scenes[index].active = True
            self.current_scene_index = index
            self._update_source_list()

    def _update_source_list(self):
        self.source_list.clear()
        if 0 <= self.current_scene_index < len(self.scenes):
            scene = self.scenes[self.current_scene_index]
            for source in scene.sources:
                self.source_list.addItem(source.get("name", "Unknown Source"))

    def _add_source(self):
        # Create source selection dialog
        source_types = ["Camera", "File Source", "Face Swap", "Text", "Image"]
        source_type, ok = qtx.QXInputDialog.getItem(
            self, "Add Source", "Select source type:", source_types
        )

        if ok and source_type:
            if 0 <= self.current_scene_index < len(self.scenes):
                source = {
                    "name": f"{source_type} {len(self.scenes[self.current_scene_index].sources) + 1}",
                    "type": source_type,
                    "visible": True,
                    "properties": {},
                }
                self.scenes[self.current_scene_index].sources.append(source)
                self._update_source_list()

    def _remove_source(self):
        current_row = self.source_list.currentRow()
        if current_row >= 0 and 0 <= self.current_scene_index < len(self.scenes):
            self.scenes[self.current_scene_index].sources.pop(current_row)
            self._update_source_list()

    def _move_source_up(self):
        current_row = self.source_list.currentRow()
        if current_row > 0 and 0 <= self.current_scene_index < len(self.scenes):
            sources = self.scenes[self.current_scene_index].sources
            sources[current_row], sources[current_row - 1] = (
                sources[current_row - 1],
                sources[current_row],
            )
            self._update_source_list()
            self.source_list.setCurrentRow(current_row - 1)

    def _move_source_down(self):
        current_row = self.source_list.currentRow()
        if (
            current_row >= 0
            and current_row < self.source_list.count() - 1
            and 0 <= self.current_scene_index < len(self.scenes)
        ):
            sources = self.scenes[self.current_scene_index].sources
            sources[current_row], sources[current_row + 1] = (
                sources[current_row + 1],
                sources[current_row],
            )
            self._update_source_list()
            self.source_list.setCurrentRow(current_row + 1)


class QOBSStreamManager(qtx.QXWidget):
    def __init__(self):
        super().__init__()
        self.streaming_engine = StreamingEngine()
        self.recording_engine = RecordingEngine()
        self.stream_configs = []
        self.is_streaming = False
        self.is_recording = False
        self._init_ui()

    def _init_ui(self):
        layout = qtx.QXVBoxLayout()

        # Stream controls
        controls_layout = qtx.QXHBoxLayout()

        self.start_streaming_btn = qtx.QXPushButton(
            text="Start Streaming", clicked=self._toggle_streaming
        )
        self.start_streaming_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )

        self.start_recording_btn = qtx.QXPushButton(
            text="Start Recording", clicked=self._toggle_recording
        )
        self.start_recording_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """
        )

        controls_layout.addWidget(self.start_streaming_btn)
        controls_layout.addWidget(self.start_recording_btn)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Stream status
        self.status_label = qtx.QXLabel(text="Ready to stream")
        self.status_label.setStyleSheet("color: #666; font-size: 11px; margin: 4px;")
        layout.addWidget(self.status_label)

        # Stream platforms
        platforms_label = qtx.QXLabel(text="Stream Platforms")
        platforms_label.setStyleSheet(
            "font-weight: bold; font-size: 12px; margin-top: 10px;"
        )
        layout.addWidget(platforms_label)

        # Platform controls
        platform_controls_layout = qtx.QXHBoxLayout()

        self.add_platform_btn = qtx.QXPushButton(
            text="Add Platform", clicked=self._add_platform
        )
        self.remove_platform_btn = qtx.QXPushButton(
            text="Remove Platform", clicked=self._remove_platform
        )
        self.configure_platform_btn = qtx.QXPushButton(
            text="Configure", clicked=self._configure_platform
        )

        platform_controls_layout.addWidget(self.add_platform_btn)
        platform_controls_layout.addWidget(self.remove_platform_btn)
        platform_controls_layout.addWidget(self.configure_platform_btn)

        layout.addLayout(platform_controls_layout)

        # Platform list
        self.platform_list = qtx.QXListWidget()
        layout.addWidget(self.platform_list)

        # Recording settings
        recording_label = qtx.QXLabel(text="Recording Settings")
        recording_label.setStyleSheet(
            "font-weight: bold; font-size: 12px; margin-top: 10px;"
        )
        layout.addWidget(recording_label)

        # Recording format
        format_layout = qtx.QXHBoxLayout()
        format_layout.addWidget(qtx.QXLabel(text="Format:"))

        self.format_combo = qtx.QXComboBox()
        self.format_combo.addItems(["MP4", "AVI", "MOV", "FLV"])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()

        layout.addLayout(format_layout)

        # Quality settings
        quality_layout = qtx.QXHBoxLayout()
        quality_layout.addWidget(qtx.QXLabel(text="Quality:"))

        self.quality_combo = qtx.QXComboBox()
        self.quality_combo.addItems(["High", "Medium", "Low", "Custom"])
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()

        layout.addLayout(quality_layout)

        self.setLayout(layout)

    def _toggle_streaming(self):
        if not self.is_streaming:
            self._start_streaming()
        else:
            self._stop_streaming()

    def _start_streaming(self):
        if not self.stream_configs:
            qtx.QXMessageBox.warning(self, "Warning", "No stream platforms configured!")
            return

        # Validate all stream configurations
        all_valid = True
        for config in self.stream_configs:
            errors = validate_stream_config(config)
            if errors:
                qtx.QXMessageBox.warning(
                    self,
                    "Configuration Error",
                    f"Invalid configuration for {config.platform.value}:\n"
                    + "\n".join(errors),
                )
                all_valid = False
                break

        if not all_valid:
            return

        # Add configurations to streaming engine
        for config in self.stream_configs:
            self.streaming_engine.add_stream_config(config)

        # Start streaming
        success = self.streaming_engine.start_streaming()

        if success:
            self.is_streaming = True
            self.start_streaming_btn.setText("Stop Streaming")
            self.start_streaming_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """
            )
            self.status_label.setText("🔴 LIVE - Streaming to multiple platforms")
            self.status_label.setStyleSheet(
                "color: #f44336; font-weight: bold; font-size: 11px; margin: 4px;"
            )
        else:
            qtx.QXMessageBox.critical(self, "Error", "Failed to start streaming!")

    def _stop_streaming(self):
        self.streaming_engine.stop_streaming()
        self.is_streaming = False
        self.start_streaming_btn.setText("Start Streaming")
        self.start_streaming_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )
        self.status_label.setText("Stream stopped")
        self.status_label.setStyleSheet("color: #666; font-size: 11px; margin: 4px;")

    def _toggle_recording(self):
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        # Get recording settings
        format = self.format_combo.currentText().lower()
        quality = self.quality_combo.currentText().lower()

        # Generate filename with timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"deepface_recording_{timestamp}.{format}"

        # Get recordings directory (create if needed)
        recordings_dir = Path("recordings")
        recordings_dir.mkdir(exist_ok=True)
        output_path = recordings_dir / filename

        # Start recording
        success = self.recording_engine.start_recording(
            output_path=output_path,
            format=format,
            resolution="1920x1080",  # Could be made configurable
            fps=30,
            quality=quality,
        )

        if success:
            self.is_recording = True
            self.start_recording_btn.setText("Stop Recording")
            self.start_recording_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #ff9800;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #e68900;
                }
            """
            )
        else:
            qtx.QXMessageBox.critical(self, "Error", "Failed to start recording!")

    def _stop_recording(self):
        self.recording_engine.stop_recording()
        self.is_recording = False
        self.start_recording_btn.setText("Start Recording")
        self.start_recording_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """
        )

    def _add_platform(self):
        platforms = ["Twitch", "YouTube", "Facebook", "Custom RTMP"]
        platform, ok = qtx.QXInputDialog.getItem(
            self, "Add Platform", "Select platform:", platforms
        )

        if ok and platform:
            # Map UI platform names to enum values
            platform_mapping = {
                "Twitch": "twitch",
                "YouTube": "youtube",
                "Facebook": "facebook",
                "Custom RTMP": "rtmp_custom",
            }

            stream_config = StreamConfig(
                platform=StreamPlatform(platform_mapping[platform]),
                stream_key="",
                server_url="",
                enabled=True,
            )
            self.stream_configs.append(stream_config)
            self.platform_list.addItem(f"{platform} (Not configured)")

    def _remove_platform(self):
        current_row = self.platform_list.currentRow()
        if current_row >= 0:
            self.stream_configs.pop(current_row)
            self.platform_list.takeItem(current_row)

    def _configure_platform(self):
        current_row = self.platform_list.currentRow()
        if current_row >= 0:
            # Open platform configuration dialog
            self._open_platform_config_dialog(current_row)

    def _open_platform_config_dialog(self, index):
        # Create a configuration dialog for the selected platform
        dialog = qtx.QXDialog(self)
        dialog.setWindowTitle("Platform Configuration")
        dialog.setModal(True)

        layout = qtx.QXVBoxLayout()

        # Stream key input
        layout.addWidget(qtx.QXLabel(text="Stream Key:"))
        stream_key_input = qtx.QXLineEdit()
        stream_key_input.setText(self.stream_configs[index].stream_key)
        layout.addWidget(stream_key_input)

        # Server URL input
        layout.addWidget(qtx.QXLabel(text="Server URL:"))
        server_url_input = qtx.QXLineEdit()
        server_url_input.setText(self.stream_configs[index].server_url)
        layout.addWidget(server_url_input)

        # Bitrate input
        layout.addWidget(qtx.QXLabel(text="Bitrate (kbps):"))
        bitrate_input = qtx.QXSpinBox()
        bitrate_input.setRange(500, 10000)
        bitrate_input.setValue(self.stream_configs[index].bitrate)
        layout.addWidget(bitrate_input)

        # Buttons
        button_layout = qtx.QXHBoxLayout()
        save_btn = qtx.QXPushButton(text="Save")
        cancel_btn = qtx.QXPushButton(text="Cancel")

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        def save_config():
            self.stream_configs[index].stream_key = stream_key_input.text()
            self.stream_configs[index].server_url = server_url_input.text()
            self.stream_configs[index].bitrate = bitrate_input.value()

            # Update list item
            platform_name = self.stream_configs[index].platform.value.title()
            status = "Configured" if stream_key_input.text() else "Not configured"
            self.platform_list.item(index).setText(f"{platform_name} ({status})")

            dialog.accept()

        save_btn.clicked.connect(save_config)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.exec_()

    def send_frame(self, frame):
        """Send frame to streaming and recording engines"""
        if self.is_streaming:
            self.streaming_engine.send_frame(frame)
        if self.is_recording:
            self.recording_engine.record_frame(frame)


class QOBSMainPreview(qtx.QXWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = qtx.QXVBoxLayout()

        # Preview area
        self.preview_area = qtx.QXLabel()
        self.preview_area.setMinimumSize(640, 360)
        self.preview_area.setStyleSheet(
            """
            QLabel {
                background-color: #000;
                border: 2px solid #333;
                border-radius: 4px;
            }
        """
        )
        self.preview_area.setAlignment(qtx.AlignCenter)
        self.preview_area.setText("Main Preview\n(No source active)")
        self.preview_area.setStyleSheet(
            self.preview_area.styleSheet() + "color: #666; font-size: 16px;"
        )

        layout.addWidget(self.preview_area)

        # Preview controls
        controls_layout = qtx.QXHBoxLayout()

        self.studio_mode_btn = qtx.QXPushButton(text="Studio Mode")
        self.fullscreen_btn = qtx.QXPushButton(text="Fullscreen")
        self.screenshot_btn = qtx.QXPushButton(text="Screenshot")

        controls_layout.addWidget(self.studio_mode_btn)
        controls_layout.addWidget(self.fullscreen_btn)
        controls_layout.addWidget(self.screenshot_btn)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        self.setLayout(layout)


class QOBSStyleLiveSwap(qtx.QXWidget):
    def __init__(self, userdata_path: Path, settings_dirpath: Path):
        super().__init__()

        self.userdata_path = userdata_path
        self.settings_dirpath = settings_dirpath

        # Create necessary directories
        dfm_models_path = userdata_path / "dfm_models"
        dfm_models_path.mkdir(parents=True, exist_ok=True)

        animatables_path = userdata_path / "animatables"
        animatables_path.mkdir(parents=True, exist_ok=True)

        output_sequence_path = userdata_path / "output_sequence"
        output_sequence_path.mkdir(parents=True, exist_ok=True)

        # Initialize backend (simplified for OBS-style interface)
        self.backend_db = backend.BackendDB(settings_dirpath / "states.dat")
        self.backend_weak_heap = backend.BackendWeakHeap(size_mb=2048)

        # Current frame for streaming/recording
        self.current_frame = None

        self._init_ui()
        self._init_backends()

        # Timer for processing
        self._timer = qtx.QXTimer(interval=5, timeout=self._on_timer_5ms, start=True)

    def _init_ui(self):
        # Main layout
        main_layout = qtx.QXHBoxLayout()

        # Left panel - Scene and Stream controls
        left_panel = qtx.QXWidget()
        left_panel.setMaximumWidth(300)
        left_panel.setMinimumWidth(250)
        left_layout = qtx.QXVBoxLayout()

        # Scene manager
        self.scene_manager = QOBSSceneManager()
        left_layout.addWidget(self.scene_manager)

        # Stream manager
        self.stream_manager = QOBSStreamManager()
        left_layout.addWidget(self.stream_manager)

        left_panel.setLayout(left_layout)

        # Center panel - Main preview
        center_panel = qtx.QXWidget()
        center_layout = qtx.QXVBoxLayout()

        self.main_preview = QOBSMainPreview()
        center_layout.addWidget(self.main_preview)

        center_panel.setLayout(center_layout)

        # Right panel - DeepFace controls (compact)
        right_panel = qtx.QXWidget()
        right_panel.setMaximumWidth(350)
        right_panel.setMinimumWidth(300)
        right_layout = qtx.QXVBoxLayout()

        # Face processing controls
        face_controls_label = qtx.QXLabel(text="Face Processing")
        face_controls_label.setStyleSheet(
            "font-weight: bold; font-size: 12px; margin-bottom: 5px;"
        )
        right_layout.addWidget(face_controls_label)

        # Compact face processing widgets
        self.camera_source = QCameraSource()
        self.face_detector = QFaceDetector()
        self.face_swapper = QFaceSwapDFM()

        # Create compact versions
        compact_widgets = [
            ("Camera", self.camera_source),
            ("Face Detection", self.face_detector),
            ("Face Swap", self.face_swapper),
        ]

        for name, widget in compact_widgets:
            group = qtx.QXGroupBox(title=name)
            group_layout = qtx.QXVBoxLayout()

            # Add a compact version of the widget
            compact_widget = self._create_compact_widget(widget)
            group_layout.addWidget(compact_widget)

            group.setLayout(group_layout)
            group.setMaximumHeight(120)
            right_layout.addWidget(group)

        right_layout.addStretch()
        right_panel.setLayout(right_layout)

        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(center_panel, 1)  # Center gets most space
        main_layout.addWidget(right_panel)

        self.setLayout(main_layout)

        # Apply OBS-style dark theme
        self._apply_obs_style()

    def _create_compact_widget(self, original_widget):
        # Create a compact version of the widget with essential controls only
        compact = qtx.QXWidget()
        layout = qtx.QXVBoxLayout()

        # Add essential controls based on widget type
        if hasattr(original_widget, "q_switch_button"):
            layout.addWidget(original_widget.q_switch_button)

        if hasattr(original_widget, "q_model_label"):
            layout.addWidget(original_widget.q_model_label)

        compact.setLayout(layout)
        compact.setMaximumHeight(80)

        return compact

    def _init_backends(self):
        # Initialize simplified backend connections for OBS-style interface
        self.all_backends = []

        # This would need to be adapted based on the actual backend structure
        # For now, we'll create placeholder connections

    def _apply_obs_style(self):
        # Apply OBS Studio-like dark theme
        self.setStyleSheet(
            """
            QWidget {
                background-color: #31363b;
                color: #eff0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 1px solid #76797c;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 4px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }
            
            QPushButton {
                background-color: #54595f;
                border: 1px solid #76797c;
                padding: 4px 8px;
                border-radius: 3px;
                font-weight: normal;
            }
            
            QPushButton:hover {
                background-color: #626873;
            }
            
            QPushButton:pressed {
                background-color: #4a5058;
            }
            
            QListWidget {
                background-color: #232629;
                border: 1px solid #76797c;
                border-radius: 3px;
                selection-background-color: #3daee9;
            }
            
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #404040;
            }
            
            QListWidget::item:selected {
                background-color: #3daee9;
            }
            
            QComboBox {
                background-color: #54595f;
                border: 1px solid #76797c;
                padding: 2px 4px;
                border-radius: 3px;
            }
            
            QComboBox:drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            
            QLineEdit {
                background-color: #232629;
                border: 1px solid #76797c;
                padding: 4px;
                border-radius: 3px;
            }
            
            QSpinBox {
                background-color: #232629;
                border: 1px solid #76797c;
                padding: 2px;
                border-radius: 3px;
            }
            
            QLabel {
                background-color: transparent;
            }
        """
        )

    def _on_timer_5ms(self):
        # Process backend messages
        if hasattr(self, "backend_db"):
            self.backend_db.process_messages()

        for backend in getattr(self, "all_backends", []):
            if hasattr(backend, "process_messages"):
                backend.process_messages()

        # Send frame to streaming/recording if available
        if self.current_frame is not None:
            self.stream_manager.send_frame(self.current_frame)

    def initialize(self):
        # Initialize all components
        pass

    def finalize(self):
        # Clean up resources
        if hasattr(self, "_timer"):
            self._timer.stop()


class QOBSStyleAppWindow(qtx.QXWindow):
    def __init__(self, userdata_path, settings_dirpath):
        super().__init__(save_load_state=True, size_policy=("minimum", "minimum"))

        self._userdata_path = userdata_path
        self._settings_dirpath = settings_dirpath

        # Create menu bar
        menu_bar = qtx.QXMenuBar(font=QXFontDB.get_default_font(size=10))

        # File menu
        menu_file = menu_bar.addMenu("File")
        menu_file.addAction("New Scene Collection")
        menu_file.addAction("Import Scene Collection")
        menu_file.addAction("Export Scene Collection")
        menu_file.addSeparator()
        menu_file.addAction("Settings")
        menu_file.addAction("Exit")

        # Edit menu
        menu_edit = menu_bar.addMenu("Edit")
        menu_edit.addAction("Undo")
        menu_edit.addAction("Redo")
        menu_edit.addSeparator()
        menu_edit.addAction("Transform")
        menu_edit.addAction("Reset Transform")

        # View menu
        menu_view = menu_bar.addMenu("View")
        menu_view.addAction("Stats")
        menu_view.addAction("Audio Mixer")
        menu_view.addAction("Scene Transitions")

        # Tools menu
        menu_tools = menu_bar.addMenu("Tools")
        menu_tools.addAction("Auto-Configuration Wizard")
        menu_tools.addAction("Output Timer")
        menu_tools.addAction("Log Files")

        # Help menu
        menu_help = menu_bar.addMenu("Help")
        menu_help.addAction("Help")
        menu_help.addAction("About OBS-Style DeepFaceLive")

        self.setMenuBar(menu_bar)

        # Set window properties
        self.setWindowTitle("OBS-Style DeepFaceLive")
        self.setMinimumSize(1200, 800)

        # Create main widget
        self.q_live_swap = QOBSStyleLiveSwap(
            userdata_path=self._userdata_path, settings_dirpath=self._settings_dirpath
        )

        self.add_widget(self.q_live_swap)

        # Initialize
        self.q_live_swap.initialize()

    def closeEvent(self, event):
        if hasattr(self.q_live_swap, "finalize"):
            self.q_live_swap.finalize()
        event.accept()


class OBSStyleDeepFaceLiveApp(qtx.QXMainApplication):
    def __init__(self, userdata_path):
        self.userdata_path = userdata_path
        settings_dirpath = self.settings_dirpath = userdata_path / "settings"
        if not settings_dirpath.exists():
            settings_dirpath.mkdir(parents=True)

        super().__init__(
            app_name="OBS-Style DeepFaceLive", settings_dirpath=settings_dirpath
        )

        self.setFont(QXFontDB.get_default_font())
        self.setWindowIcon(QXImageDB.app_icon().as_QIcon())

        # Create splash screen
        splash_wnd = self.splash_wnd = qtx.QXSplashWindow(
            layout=qtx.QXVBoxLayout(
                [(qtx.QXLabel(image=QXImageDB.splash_deepfacelive()), qtx.AlignCenter)],
                contents_margins=20,
            )
        )
        splash_wnd.show()
        splash_wnd.center_on_screen()

        self._obs_wnd = None
        self._t = qtx.QXTimer(
            interval=1666,
            timeout=self._on_splash_wnd_expired,
            single_shot=True,
            start=True,
        )
        self.initialize()

    def initialize(self):
        Localization.set_language(self.get_language())

        if self._obs_wnd is None:
            self._obs_wnd = QOBSStyleAppWindow(
                userdata_path=self.userdata_path, settings_dirpath=self.settings_dirpath
            )

    def finalize(self):
        if self._obs_wnd is not None:
            self._obs_wnd.close()
            self._obs_wnd.deleteLater()
            self._obs_wnd = None

    def _on_splash_wnd_expired(self):
        self._obs_wnd.show()

        if self.splash_wnd is not None:
            self.splash_wnd.hide()
            self.splash_wnd.deleteLater()
            self.splash_wnd = None

    def on_reinitialize(self):
        self.finalize()

        import gc

        gc.collect()
        gc.collect()

        self.initialize()
        self._obs_wnd.show()
