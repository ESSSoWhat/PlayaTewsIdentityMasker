#!/usr/bin/env python3
"""
Processing Window for PlayaTewsIdentityMasker
Separate window containing face-swapping controls and advanced options
"""

from pathlib import Path
from typing import Dict, Optional

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon, QPalette
from PyQt5.QtWidgets import (
    QAction,
    QCheckBox,
    QComboBox,
    QDockWidget,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenuBar,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from localization import L
from resources.fonts import QXFontDB
from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel


class QProcessingWindow(qtx.QXWindow):
    """Separate processing window for face-swapping controls and advanced options"""

    def __init__(self, face_swap_components: Dict = None, parent=None):
        super().__init__(save_load_state=True)
        self.face_swap_components = face_swap_components or {}
        self.parent_window = parent
        self.setup_window()
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()

        # Set window flags to keep it on top of the main window
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def setup_window(self):
        """Setup window properties"""
        self.setWindowTitle("PlayaTewsIdentityMasker - All Controls")
        self.setMinimumSize(1000, 800)
        self.resize(1200, 900)

        # Set window icon if available
        try:
            from resources.gfx import QXImageDB

            icon = QXImageDB.app_icon()
            if icon:
                self.setWindowIcon(icon.as_QIcon())
        except:
            pass

        # Note: QXWindow doesn't have built-in menu bar and status bar support
        # These can be implemented using custom widgets if needed

    def create_menu_bar(self):
        """Create menu bar with processing options"""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        save_settings_action = QAction("Save Settings", self)
        save_settings_action.setShortcut("Ctrl+S")
        save_settings_action.triggered.connect(self.save_settings)
        file_menu.addAction(save_settings_action)

        load_settings_action = QAction("Load Settings", self)
        load_settings_action.setShortcut("Ctrl+O")
        load_settings_action.triggered.connect(self.load_settings)
        file_menu.addAction(load_settings_action)

        file_menu.addSeparator()

        close_action = QAction("Close Window", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)

        # View menu
        view_menu = menu_bar.addMenu("View")

        toggle_dock_action = QAction("Toggle Dock", self)
        toggle_dock_action.setShortcut("Ctrl+D")
        toggle_dock_action.triggered.connect(self.toggle_dock)
        view_menu.addAction(toggle_dock_action)

        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")

        reset_all_action = QAction("Reset All Settings", self)
        reset_all_action.triggered.connect(self.reset_all_settings)
        tools_menu.addAction(reset_all_action)

        optimize_action = QAction("Optimize Performance", self)
        optimize_action.triggered.connect(self.optimize_performance)
        tools_menu.addAction(optimize_action)

        # Help menu
        help_menu = menu_bar.addMenu("Help")

        about_action = QAction("About Processing Window", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_ui(self):
        """Setup the main UI layout"""
        central_widget = QWidget()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(central_widget)

        main_layout = QHBoxLayout()

        # Left panel - Basic controls
        left_panel = self.create_left_panel()

        # Center panel - Advanced controls
        center_panel = self.create_center_panel()

        # Right panel - Monitoring and status
        right_panel = self.create_right_panel()

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 400, 300])

        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)

    def create_left_panel(self):
        """Create the left panel with basic controls"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Input sources group
        input_group = QGroupBox("Input Sources")
        input_layout = QVBoxLayout()

        try:
            if self.face_swap_components and "file_source" in self.face_swap_components:
                input_layout.addWidget(self.face_swap_components["file_source"])
            if (
                self.face_swap_components
                and "camera_source" in self.face_swap_components
            ):
                input_layout.addWidget(self.face_swap_components["camera_source"])
        except Exception as e:
            print(f"Error adding input source components: {e}")
            # Add placeholder labels if components are not available
            input_layout.addWidget(QLabel("File Source: Not Available"))
            input_layout.addWidget(QLabel("Camera Source: Not Available"))

        input_group.setLayout(input_layout)

        # Face detection group
        detection_group = QGroupBox("Face Detection & Alignment")
        detection_layout = QVBoxLayout()

        try:
            if (
                self.face_swap_components
                and "face_detector" in self.face_swap_components
            ):
                detection_layout.addWidget(self.face_swap_components["face_detector"])
            if (
                self.face_swap_components
                and "face_aligner" in self.face_swap_components
            ):
                detection_layout.addWidget(self.face_swap_components["face_aligner"])
        except Exception as e:
            print(f"Error adding detection components: {e}")
            # Add placeholder labels if components are not available
            detection_layout.addWidget(QLabel("Face Detector: Not Available"))
            detection_layout.addWidget(QLabel("Face Aligner: Not Available"))

        detection_group.setLayout(detection_layout)

        layout.addWidget(input_group)
        layout.addWidget(detection_group)
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def create_center_panel(self):
        """Create the center panel with advanced controls"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Create tab widget for different processing options
        self.processing_tabs = QTabWidget()

        # Face processing tab
        face_processing_tab = self.create_face_processing_tab()
        self.processing_tabs.addTab(face_processing_tab, "Face Processing")

        # Frame processing tab
        frame_processing_tab = self.create_frame_processing_tab()
        self.processing_tabs.addTab(frame_processing_tab, "Frame Processing")

        # Advanced options tab
        advanced_tab = self.create_advanced_tab()
        self.processing_tabs.addTab(advanced_tab, "Advanced")

        # Performance tab
        performance_tab = self.create_performance_tab()
        self.processing_tabs.addTab(performance_tab, "Performance")

        # All Controls tab (complete face-swapping pipeline)
        all_controls_tab = self.create_all_controls_tab()
        self.processing_tabs.addTab(all_controls_tab, "All Controls")

        # Streaming settings tab
        streaming_tab = self.create_streaming_tab()
        self.processing_tabs.addTab(streaming_tab, "Streaming")

        # Recording settings tab
        recording_tab = self.create_recording_tab()
        self.processing_tabs.addTab(recording_tab, "Recording")

        # Audio settings tab
        audio_tab = self.create_audio_tab()
        self.processing_tabs.addTab(audio_tab, "Audio")

        # Video settings tab
        video_tab = self.create_video_tab()
        self.processing_tabs.addTab(video_tab, "Video")

        layout.addWidget(self.processing_tabs)
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def create_face_processing_tab(self):
        """Create face processing controls tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Create scroll area for face processing controls
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        try:
            # Face marker
            if self.face_swap_components and "face_marker" in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components["face_marker"])
            else:
                scroll_layout.addWidget(QLabel("Face Marker: Not Available"))

            # Face animator
            if (
                self.face_swap_components
                and "face_animator" in self.face_swap_components
            ):
                scroll_layout.addWidget(self.face_swap_components["face_animator"])
            else:
                scroll_layout.addWidget(QLabel("Face Animator: Not Available"))

            # Face swap insight
            if (
                self.face_swap_components
                and "face_swap_insight" in self.face_swap_components
            ):
                scroll_layout.addWidget(self.face_swap_components["face_swap_insight"])
            else:
                scroll_layout.addWidget(QLabel("Face Swap Insight: Not Available"))

            # Face swap DFM
            if (
                self.face_swap_components
                and "face_swap_dfm" in self.face_swap_components
            ):
                scroll_layout.addWidget(self.face_swap_components["face_swap_dfm"])
            else:
                scroll_layout.addWidget(QLabel("Face Swap DFM: Not Available"))
        except Exception as e:
            print(f"Error adding face processing components: {e}")
            scroll_layout.addWidget(QLabel("Face Processing Components: Error Loading"))

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab

    def create_frame_processing_tab(self):
        """Create frame processing controls tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Create scroll area for frame processing controls
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        try:
            # Frame adjuster
            if (
                self.face_swap_components
                and "frame_adjuster" in self.face_swap_components
            ):
                scroll_layout.addWidget(self.face_swap_components["frame_adjuster"])
            else:
                scroll_layout.addWidget(QLabel("Frame Adjuster: Not Available"))

            # Face merger
            if self.face_swap_components and "face_merger" in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components["face_merger"])
            else:
                scroll_layout.addWidget(QLabel("Face Merger: Not Available"))

            # Stream output
            if (
                self.face_swap_components
                and "stream_output" in self.face_swap_components
            ):
                scroll_layout.addWidget(self.face_swap_components["stream_output"])
            else:
                scroll_layout.addWidget(QLabel("Stream Output: Not Available"))
        except Exception as e:
            print(f"Error adding frame processing components: {e}")
            scroll_layout.addWidget(
                QLabel("Frame Processing Components: Error Loading")
            )

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab

    def create_advanced_tab(self):
        """Create advanced options tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Advanced processing options
        advanced_group = QGroupBox("Advanced Processing")
        advanced_layout = QVBoxLayout()

        # Quality settings
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Processing Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["High", "Medium", "Low", "Ultra Fast"])
        self.quality_combo.setCurrentText("High")
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        advanced_layout.addLayout(quality_layout)

        # Threading options
        threading_layout = QHBoxLayout()
        threading_layout.addWidget(QLabel("Thread Count:"))
        self.thread_spin = QSpinBox()
        self.thread_spin.setRange(1, 16)
        self.thread_spin.setValue(4)
        threading_layout.addWidget(self.thread_spin)
        threading_layout.addStretch()
        advanced_layout.addLayout(threading_layout)

        # Memory management
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory Limit (MB):"))
        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(512, 8192)
        self.memory_spin.setValue(2048)
        self.memory_spin.setSingleStep(256)
        memory_layout.addWidget(self.memory_spin)
        memory_layout.addStretch()
        advanced_layout.addLayout(memory_layout)

        advanced_group.setLayout(advanced_layout)

        # Experimental features
        experimental_group = QGroupBox("Experimental Features")
        experimental_layout = QVBoxLayout()

        self.enable_experimental_checkbox = QCheckBox("Enable Experimental Features")
        self.enable_experimental_checkbox.setChecked(False)
        experimental_layout.addWidget(self.enable_experimental_checkbox)

        self.auto_optimize_checkbox = QCheckBox("Auto-Optimize Settings")
        self.auto_optimize_checkbox.setChecked(True)
        experimental_layout.addWidget(self.auto_optimize_checkbox)

        experimental_group.setLayout(experimental_layout)

        layout.addWidget(advanced_group)
        layout.addWidget(experimental_group)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def create_all_controls_tab(self):
        """Create tab with all face-swapping controls"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Create scroll area for all controls
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Add all face-swapping components in order
        component_order = [
            "file_source",
            "camera_source",
            "face_detector",
            "face_aligner",
            "face_marker",
            "face_animator",
            "face_swap_insight",
            "face_swap_dfm",
            "frame_adjuster",
            "face_merger",
            "stream_output",
        ]

        try:
            for component_name in component_order:
                if (
                    self.face_swap_components
                    and component_name in self.face_swap_components
                ):
                    component = self.face_swap_components[component_name]
                    scroll_layout.addWidget(component)

                    # Add a small spacer between components
                    spacer = QWidget()
                    spacer.setFixedHeight(5)
                    scroll_layout.addWidget(spacer)
                else:
                    # Add placeholder for missing component
                    scroll_layout.addWidget(
                        QLabel(
                            f"{component_name.replace('_', ' ').title()}: Not Available"
                        )
                    )

                    # Add a small spacer between components
                    spacer = QWidget()
                    spacer.setFixedHeight(5)
                    scroll_layout.addWidget(spacer)
        except Exception as e:
            print(f"Error adding all controls components: {e}")
            scroll_layout.addWidget(QLabel("All Controls: Error Loading Components"))

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab

    def create_streaming_tab(self):
        """Create streaming settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Create scroll area for streaming controls
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Platform selection
        platform_group = QGroupBox("Streaming Platform")
        platform_layout = QVBoxLayout()

        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Twitch", "YouTube", "Facebook", "Custom RTMP"])
        platform_layout.addWidget(QLabel("Platform:"))
        platform_layout.addWidget(self.platform_combo)

        # Stream key
        self.stream_key_edit = QLineEdit()
        self.stream_key_edit.setPlaceholderText("Enter your stream key")
        platform_layout.addWidget(QLabel("Stream Key:"))
        platform_layout.addWidget(self.stream_key_edit)

        # Custom RTMP URL
        self.custom_rtmp_edit = QLineEdit()
        self.custom_rtmp_edit.setPlaceholderText("rtmp://your-server.com/live")
        self.custom_rtmp_edit.setEnabled(False)
        platform_layout.addWidget(QLabel("Custom RTMP URL:"))
        platform_layout.addWidget(self.custom_rtmp_edit)

        platform_group.setLayout(platform_layout)
        scroll_layout.addWidget(platform_group)

        # Quality settings
        quality_group = QGroupBox("Stream Quality")
        quality_layout = QVBoxLayout()

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(
            ["1080p 60fps", "1080p 30fps", "720p 60fps", "720p 30fps", "480p 30fps"]
        )
        quality_layout.addWidget(QLabel("Resolution & FPS:"))
        quality_layout.addWidget(self.quality_combo)

        self.bitrate_spin = QSpinBox()
        self.bitrate_spin.setRange(1000, 8000)
        self.bitrate_spin.setValue(4500)
        self.bitrate_spin.setSuffix(" kbps")
        quality_layout.addWidget(QLabel("Bitrate:"))
        quality_layout.addWidget(self.bitrate_spin)

        quality_group.setLayout(quality_layout)
        scroll_layout.addWidget(quality_group)

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab

    def create_recording_tab(self):
        """Create recording settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Create scroll area for recording controls
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Recording format
        format_group = QGroupBox("Recording Format")
        format_layout = QVBoxLayout()

        self.recording_format_combo = QComboBox()
        self.recording_format_combo.addItems(["MP4", "AVI", "MOV", "MKV"])
        format_layout.addWidget(QLabel("Format:"))
        format_layout.addWidget(self.recording_format_combo)

        self.recording_quality_combo = QComboBox()
        self.recording_quality_combo.addItems(["High", "Medium", "Low"])
        format_layout.addWidget(QLabel("Quality:"))
        format_layout.addWidget(self.recording_quality_combo)

        format_group.setLayout(format_layout)
        scroll_layout.addWidget(format_group)

        # Recording settings
        settings_group = QGroupBox("Recording Settings")
        settings_layout = QVBoxLayout()

        self.recording_fps_combo = QComboBox()
        self.recording_fps_combo.addItems(["60", "30", "24"])
        settings_layout.addWidget(QLabel("FPS:"))
        settings_layout.addWidget(self.recording_fps_combo)

        self.recording_bitrate_spin = QSpinBox()
        self.recording_bitrate_spin.setRange(1000, 16000)
        self.recording_bitrate_spin.setValue(8000)
        self.recording_bitrate_spin.setSuffix(" kbps")
        settings_layout.addWidget(QLabel("Bitrate:"))
        settings_layout.addWidget(self.recording_bitrate_spin)

        self.recording_path_edit = QLineEdit()
        self.recording_path_edit.setPlaceholderText("C:/Recordings/")
        settings_layout.addWidget(QLabel("Save Path:"))
        settings_layout.addWidget(self.recording_path_edit)

        settings_group.setLayout(settings_layout)
        scroll_layout.addWidget(settings_group)

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab

    def create_audio_tab(self):
        """Create audio settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Create scroll area for audio controls
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Audio input
        input_group = QGroupBox("Audio Input")
        input_layout = QVBoxLayout()

        self.audio_input_combo = QComboBox()
        self.audio_input_combo.addItems(
            ["Default Microphone", "System Audio", "Custom Device"]
        )
        input_layout.addWidget(QLabel("Input Source:"))
        input_layout.addWidget(self.audio_input_combo)

        self.mic_volume_slider = QSlider(Qt.Horizontal)
        self.mic_volume_slider.setRange(0, 100)
        self.mic_volume_slider.setValue(80)
        input_layout.addWidget(QLabel("Microphone Volume:"))
        input_layout.addWidget(self.mic_volume_slider)

        input_group.setLayout(input_layout)
        scroll_layout.addWidget(input_group)

        # Audio output
        output_group = QGroupBox("Audio Output")
        output_layout = QVBoxLayout()

        self.audio_output_combo = QComboBox()
        self.audio_output_combo.addItems(
            ["Default Speakers", "Headphones", "System Audio"]
        )
        output_layout.addWidget(QLabel("Output Device:"))
        output_layout.addWidget(self.audio_output_combo)

        self.speaker_volume_slider = QSlider(Qt.Horizontal)
        self.speaker_volume_slider.setRange(0, 100)
        self.speaker_volume_slider.setValue(70)
        output_layout.addWidget(QLabel("Speaker Volume:"))
        output_layout.addWidget(self.speaker_volume_slider)

        output_group.setLayout(output_layout)
        scroll_layout.addWidget(output_group)

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

        # Create scroll area for video controls
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Video resolution
        resolution_group = QGroupBox("Video Resolution")
        resolution_layout = QVBoxLayout()

        self.base_resolution_combo = QComboBox()
        self.base_resolution_combo.addItems(["1920x1080", "1280x720", "854x480"])
        resolution_layout.addWidget(QLabel("Base Resolution:"))
        resolution_layout.addWidget(self.base_resolution_combo)

        self.output_resolution_combo = QComboBox()
        self.output_resolution_combo.addItems(["1920x1080", "1280x720", "854x480"])
        resolution_layout.addWidget(QLabel("Output Resolution:"))
        resolution_layout.addWidget(self.output_resolution_combo)

        resolution_group.setLayout(resolution_layout)
        scroll_layout.addWidget(resolution_group)

        # Video settings
        settings_group = QGroupBox("Video Settings")
        settings_layout = QVBoxLayout()

        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["60", "30", "24"])
        settings_layout.addWidget(QLabel("FPS:"))
        settings_layout.addWidget(self.fps_combo)

        self.aspect_ratio_combo = QComboBox()
        self.aspect_ratio_combo.addItems(["16:9", "4:3", "1:1"])
        settings_layout.addWidget(QLabel("Aspect Ratio:"))
        settings_layout.addWidget(self.aspect_ratio_combo)

        settings_group.setLayout(settings_layout)
        scroll_layout.addWidget(settings_group)

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab

    def create_performance_tab(self):
        """Create performance monitoring tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Performance metrics
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QGridLayout()

        self.fps_label = QLabel("FPS: 0.0")
        self.fps_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        metrics_layout.addWidget(QLabel("Current FPS:"), 0, 0)
        metrics_layout.addWidget(self.fps_label, 0, 1)

        self.cpu_label = QLabel("CPU: 0%")
        metrics_layout.addWidget(QLabel("CPU Usage:"), 1, 0)
        metrics_layout.addWidget(self.cpu_label, 1, 1)

        self.memory_label = QLabel("Memory: 0 MB")
        metrics_layout.addWidget(QLabel("Memory Usage:"), 2, 0)
        metrics_layout.addWidget(self.memory_label, 2, 1)

        self.gpu_label = QLabel("GPU: 0%")
        metrics_layout.addWidget(QLabel("GPU Usage:"), 3, 0)
        metrics_layout.addWidget(self.gpu_label, 3, 1)

        metrics_group.setLayout(metrics_layout)

        # Performance controls
        controls_group = QGroupBox("Performance Controls")
        controls_layout = QVBoxLayout()

        self.performance_slider = QSlider(Qt.Horizontal)
        self.performance_slider.setRange(1, 10)
        self.performance_slider.setValue(5)
        self.performance_slider.setTickPosition(QSlider.TicksBelow)
        self.performance_slider.setTickInterval(1)

        controls_layout.addWidget(QLabel("Performance Level (1-10):"))
        controls_layout.addWidget(self.performance_slider)

        self.auto_adjust_checkbox = QCheckBox("Auto-Adjust Performance")
        self.auto_adjust_checkbox.setChecked(True)
        controls_layout.addWidget(self.auto_adjust_checkbox)

        controls_group.setLayout(controls_layout)

        layout.addWidget(metrics_group)
        layout.addWidget(controls_group)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def create_right_panel(self):
        """Create the right panel with monitoring and status"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Status group
        status_group = QGroupBox("Processing Status")
        status_layout = QVBoxLayout()

        self.status_list = QListWidget()
        self.status_list.setMaximumHeight(200)
        status_layout.addWidget(self.status_list)

        # Add some sample status items
        self.status_list.addItem("✅ Face detection active")
        self.status_list.addItem("✅ Face alignment running")
        self.status_list.addItem("⏳ Face swap processing...")
        self.status_list.addItem("✅ Frame merger active")

        status_group.setLayout(status_layout)

        # Quick actions group
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()

        self.start_all_btn = QPushButton("Start All Processing")
        self.start_all_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )

        self.stop_all_btn = QPushButton("Stop All Processing")
        self.stop_all_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """
        )

        self.reset_btn = QPushButton("Reset All")
        self.reset_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """
        )

        actions_layout.addWidget(self.start_all_btn)
        actions_layout.addWidget(self.stop_all_btn)
        actions_layout.addWidget(self.reset_btn)

        actions_group.setLayout(actions_layout)

        layout.addWidget(status_group)
        layout.addWidget(actions_group)
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def setup_styles(self):
        """Setup application styles"""
        self.setStyleSheet(
            """
            QXWindow {
                background-color: #2d2d2d;
                color: #ffffff;
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
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #606060;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
            QScrollArea {
                border: 1px solid #404040;
                background-color: #2d2d2d;
            }
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                color: #ffffff;
            }
            QComboBox, QSpinBox, QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                color: #ffffff;
                padding: 5px;
                border-radius: 3px;
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
        """
        )

    def setup_connections(self):
        """Setup signal connections"""
        self.start_all_btn.clicked.connect(self.start_all_processing)
        self.stop_all_btn.clicked.connect(self.stop_all_processing)
        self.reset_btn.clicked.connect(self.reset_all_settings)

        # Performance monitoring timer
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance_metrics)
        self.performance_timer.start(1000)  # Update every second

    def start_all_processing(self):
        """Start all processing components"""
        self.status_list.addItem("🔄 Starting all processing...")

        # Here you would start all the backend components
        # For now, just update the status

    def stop_all_processing(self):
        """Stop all processing components"""
        self.status_list.addItem("⏹️ Stopping all processing...")

    def reset_all_settings(self):
        """Reset all settings to defaults"""
        self.status_list.addItem("🔄 Resetting all settings...")

    def save_settings(self):
        """Save current settings"""
        self.status_list.addItem("✅ Settings saved")

    def load_settings(self):
        """Load saved settings"""
        self.status_list.addItem("📂 Settings loaded")

    def toggle_dock(self):
        """Toggle dock state"""
        self.status_list.addItem("🔗 Dock toggled")

    def optimize_performance(self):
        """Optimize performance settings"""
        self.status_list.addItem("⚡ Optimizing performance...")

    def show_about(self):
        """Show about dialog"""
        self.status_list.addItem("ℹ️ About Processing Window")

    def update_performance_metrics(self):
        """Update performance metrics display"""
        # Simulate performance metrics
        import random

        fps = random.uniform(25.0, 60.0)
        cpu = random.randint(20, 80)
        memory = random.randint(512, 2048)
        gpu = random.randint(10, 90)

        self.fps_label.setText(f"FPS: {fps:.1f}")
        self.cpu_label.setText(f"CPU: {cpu}%")
        self.memory_label.setText(f"Memory: {memory} MB")
        self.gpu_label.setText(f"GPU: {gpu}%")

    def closeEvent(self, event):
        """Handle window close event"""
        self.hide()  # Hide instead of closing
        event.ignore()  # Prevent actual closing
