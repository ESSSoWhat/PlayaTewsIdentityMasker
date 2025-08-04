#!/usr/bin/env python3
"""
New Layout UI for PlayaTewsIdentityMasker
Implements the exact layout specified by the user with three-panel design
"""

from pathlib import Path

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QCheckBox,
)

from ..backend import StreamOutput


class QNewLayoutUI(QMainWindow):
    """New Layout UI implementing the exact three-panel design specified"""

    def __init__(
        self,
        stream_output_backend: StreamOutput,
        userdata_path: Path,
        face_swap_components=None,
        viewers_components=None,
        voice_changer_backend=None,
    ):
        super().__init__()
        self.stream_output_backend = stream_output_backend
        self.userdata_path = userdata_path
        self.face_swap_components = face_swap_components or {}
        self.viewers_components = viewers_components or {}
        self.voice_changer_backend = voice_changer_backend

        # UI State
        self.is_fullscreen = False
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance_metrics)
        self.performance_timer.start(1000)

        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.setup_menu_bar()
        self.setup_status_bar()

    def setup_ui(self):
        """Setup the new layout UI with three-panel design"""
        self.setWindowTitle("PlayaTews Identity Masker - New Layout")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.main_splitter = QSplitter(Qt.Horizontal)

        # LEFT PANEL - DFM Quick Access, Input Sources, Voice Changer
        self.left_panel = self.create_left_panel()
        self.left_panel.setMinimumWidth(300)
        self.left_panel.setMaximumWidth(400)

        # CENTER PANEL - Processing Components, Enhanced Output Preview, Large Preview Area
        self.center_panel = self.create_center_panel()

        # RIGHT PANEL - Settings, Additional Controls
        self.right_panel = self.create_right_panel()
        self.right_panel.setMinimumWidth(280)
        self.right_panel.setMaximumWidth(380)

        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.center_panel)
        self.main_splitter.addWidget(self.right_panel)
        self.main_splitter.setSizes([400, 800, 400])

        main_layout.addWidget(self.main_splitter)
        central_widget.setLayout(main_layout)

    def create_left_panel(self):
        """Create LEFT PANEL with DFM Quick Access, Input Sources, Voice Changer"""
        panel = QWidget()
        panel.setObjectName("left-panel")
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # DFM Quick Access Section
        self.create_dfm_quick_access(layout)

        # Input Sources Section
        self.create_input_sources(layout)

        # Voice Changer Section
        self.create_voice_changer(layout)

        panel.setLayout(layout)
        return panel

    def create_dfm_quick_access(self, layout):
        """Create DFM Quick Access section"""
        group = QGroupBox("DFM Quick Access")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)

        self.dfm_model_list = QListWidget()
        self.dfm_model_list.setMaximumHeight(120)
        sample_models = ["Model 1", "Model 2", "Model 3", "Custom Model"]
        for model in sample_models:
            self.dfm_model_list.addItem(QListWidgetItem(model))

        dfm_controls = QHBoxLayout()
        self.load_dfm_btn = QPushButton("Load DFM")
        self.refresh_dfm_btn = QPushButton("Refresh")
        self.refresh_dfm_btn.setMaximumWidth(80)

        dfm_controls.addWidget(self.load_dfm_btn)
        dfm_controls.addWidget(self.refresh_dfm_btn)
        dfm_controls.addStretch()

        group_layout.addWidget(self.dfm_model_list)
        group_layout.addLayout(dfm_controls)
        group.setLayout(group_layout)
        layout.addWidget(group)

    def create_input_sources(self, layout):
        """Create Input Sources section"""
        group = QGroupBox("Input Sources")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)

        source_type_layout = QHBoxLayout()
        source_type_layout.addWidget(QLabel("Type:"))
        self.source_type_combo = QComboBox()
        self.source_type_combo.addItems(["Camera", "File", "Image Sequence"])
        source_type_layout.addWidget(self.source_type_combo)
        source_type_layout.addStretch()

        self.camera_group = QGroupBox("Camera Settings")
        camera_layout = QVBoxLayout()
        self.camera_device_combo = QComboBox()
        self.camera_device_combo.addItems(["Camera 0", "Camera 1", "Camera 2"])
        self.camera_resolution_combo = QComboBox()
        self.camera_resolution_combo.addItems(
            ["1920x1080", "1280x720", "640x480"]
        )
        
        camera_layout.addWidget(QLabel("Device:"))
        camera_layout.addWidget(self.camera_device_combo)
        camera_layout.addWidget(QLabel("Resolution:"))
        camera_layout.addWidget(self.camera_resolution_combo)
        self.camera_group.setLayout(camera_layout)

        self.file_group = QGroupBox("File Settings")
        file_layout = QVBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select video file...")
        self.browse_file_btn = QPushButton("Browse")
        self.browse_file_btn.setMaximumWidth(80)
        
        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(self.file_path_edit)
        file_path_layout.addWidget(self.browse_file_btn)
        
        file_layout.addLayout(file_path_layout)
        self.file_group.setLayout(file_layout)

        group_layout.addLayout(source_type_layout)
        group_layout.addWidget(self.camera_group)
        group_layout.addWidget(self.file_group)
        group.setLayout(group_layout)
        layout.addWidget(group)

    def create_voice_changer(self, layout):
        """Create Voice Changer section"""
        group = QGroupBox("Voice Changer")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)

        self.voice_enable_checkbox = QCheckBox("Enable Voice Changer")

        voice_effect_layout = QHBoxLayout()
        voice_effect_layout.addWidget(QLabel("Effect:"))
        self.voice_effect_combo = QComboBox()
        self.voice_effect_combo.addItems(
            ["None", "Pitch Shift", "Echo", "Reverb", "Custom"]
        )
        voice_effect_layout.addWidget(self.voice_effect_combo)

        self.voice_pitch_slider = QSlider(Qt.Horizontal)
        self.voice_pitch_slider.setRange(-12, 12)
        self.voice_pitch_slider.setValue(0)
        self.voice_pitch_label = QLabel("Pitch: 0")

        group_layout.addWidget(self.voice_enable_checkbox)
        group_layout.addLayout(voice_effect_layout)
        group_layout.addWidget(QLabel("Pitch:"))
        group_layout.addWidget(self.voice_pitch_slider)
        group_layout.addWidget(self.voice_pitch_label)
        group.setLayout(group_layout)
        layout.addWidget(group)

    def create_center_panel(self):
        """Create CENTER PANEL with Processing Components, Enhanced Output Preview, Large Preview Area"""
        panel = QWidget()
        panel.setObjectName("center-panel")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Processing Components Section
        self.create_processing_components(layout)

        # Enhanced Output Preview Section
        self.create_enhanced_output_preview(layout)

        # Viewers & Controls Section
        self.create_viewers_controls(layout)

        panel.setLayout(layout)
        return panel

    def create_processing_components(self, layout):
        """Create Processing Components section"""
        components_widget = QWidget()
        components_widget.setObjectName("processing-components")
        components_widget.setMaximumHeight(60)
        components_layout = QHBoxLayout()
        components_layout.setContentsMargins(16, 8, 16, 8)
        components_layout.setSpacing(16)

        self.detection_btn = QPushButton("Detection")
        self.detection_btn.setCheckable(True)
        self.detection_btn.setChecked(True)

        self.alignment_btn = QPushButton("Alignment")
        self.alignment_btn.setCheckable(True)
        self.alignment_btn.setChecked(True)

        self.face_swap_btn = QPushButton("Face Swap")
        self.face_swap_btn.setCheckable(True)
        self.face_swap_btn.setChecked(True)

        self.enhancement_btn = QPushButton("Enhancement")
        self.enhancement_btn.setCheckable(True)
        self.enhancement_btn.setChecked(True)

        components_layout.addWidget(self.detection_btn)
        components_layout.addWidget(self.alignment_btn)
        components_layout.addWidget(self.face_swap_btn)
        components_layout.addWidget(self.enhancement_btn)
        components_layout.addStretch()

        components_widget.setLayout(components_layout)
        layout.addWidget(components_widget)

    def create_enhanced_output_preview(self, layout):
        """Create Enhanced Output Preview section with large preview area"""
        preview_widget = QWidget()
        preview_widget.setObjectName("enhanced-output-preview")
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(16, 16, 16, 16)
        preview_layout.setSpacing(16)

        # Preview Title
        preview_title = QLabel("🎬 ENHANCED OUTPUT PREVIEW - LIVE FACE SWAP")
        preview_title.setObjectName("preview-title")
        preview_title.setAlignment(Qt.AlignCenter)

        # Large Preview Area
        self.preview_area = QLabel()
        self.preview_area.setMinimumSize(640, 480)
        self.preview_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_area.setAlignment(Qt.AlignCenter)
        self.preview_area.setText("LARGE PREVIEW AREA\n\nClick to enter fullscreen mode")
        self.preview_area.setObjectName("large-preview-area")
        self.preview_area.setCursor(Qt.PointingHandCursor)

        # Preview Controls
        preview_controls = QHBoxLayout()
        self.fullscreen_btn = QPushButton("Fullscreen")
        self.maximize_btn = QPushButton("Maximize")
        self.settings_btn = QPushButton("Settings")

        preview_controls.addWidget(self.fullscreen_btn)
        preview_controls.addWidget(self.maximize_btn)
        preview_controls.addStretch()
        preview_controls.addWidget(self.settings_btn)

        preview_layout.addWidget(preview_title)
        preview_layout.addWidget(self.preview_area, 1)
        preview_layout.addLayout(preview_controls)

        preview_widget.setLayout(preview_layout)
        layout.addWidget(preview_widget, 1)

    def create_viewers_controls(self, layout):
        """Create Viewers & Controls section"""
        viewers_widget = QWidget()
        viewers_widget.setObjectName("viewers-controls")
        viewers_widget.setMaximumHeight(60)
        viewers_layout = QHBoxLayout()
        viewers_layout.setContentsMargins(16, 8, 16, 8)
        viewers_layout.setSpacing(16)

        self.camera_viewer_btn = QPushButton("Camera")
        self.camera_viewer_btn.setCheckable(True)

        self.face_align_viewer_btn = QPushButton("Face Align")
        self.face_align_viewer_btn.setCheckable(True)

        self.face_swap_viewer_btn = QPushButton("Face Swap")
        self.face_swap_viewer_btn.setCheckable(True)

        self.merged_viewer_btn = QPushButton("Merged")
        self.merged_viewer_btn.setCheckable(True)
        self.merged_viewer_btn.setChecked(True)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)

        self.controls_btn = QPushButton("Controls")

        viewers_layout.addWidget(self.camera_viewer_btn)
        viewers_layout.addWidget(self.face_align_viewer_btn)
        viewers_layout.addWidget(self.face_swap_viewer_btn)
        viewers_layout.addWidget(self.merged_viewer_btn)
        viewers_layout.addWidget(separator)
        viewers_layout.addWidget(self.controls_btn)
        viewers_layout.addStretch()

        viewers_widget.setLayout(viewers_layout)
        layout.addWidget(viewers_widget)

    def create_right_panel(self):
        """Create RIGHT PANEL with Settings and Additional Controls"""
        panel = QWidget()
        panel.setObjectName("right-panel")
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Settings Section
        self.create_settings_section(layout)

        # Additional Controls Section
        self.create_additional_controls(layout)

        panel.setLayout(layout)
        return panel

    def create_settings_section(self, layout):
        """Create Settings section"""
        group = QGroupBox("Settings")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)

        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low", "Medium", "High", "Ultra"])
        self.quality_combo.setCurrentText("High")
        quality_layout.addWidget(self.quality_combo)

        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["15", "24", "30", "60"])
        self.fps_combo.setCurrentText("30")
        fps_layout.addWidget(self.fps_combo)

        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory:"))
        self.memory_combo = QComboBox()
        self.memory_combo.addItems(["2GB", "4GB", "8GB", "16GB"])
        self.memory_combo.setCurrentText("4GB")
        memory_layout.addWidget(self.memory_combo)

        self.advanced_settings_checkbox = QCheckBox("Advanced Settings")

        group_layout.addLayout(quality_layout)
        group_layout.addLayout(fps_layout)
        group_layout.addLayout(memory_layout)
        group_layout.addWidget(self.advanced_settings_checkbox)
        group.setLayout(group_layout)
        layout.addWidget(group)

    def create_additional_controls(self, layout):
        """Create Additional Controls section"""
        group = QGroupBox("Additional Controls")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)

        self.record_btn = QPushButton("Start Recording")
        self.stream_btn = QPushButton("Start Streaming")

        self.performance_group = QGroupBox("Performance")
        performance_layout = QVBoxLayout()
        
        self.fps_indicator = QLabel("FPS: 30")
        self.fps_indicator.setObjectName("performance-indicator")
        self.memory_indicator = QLabel("Memory: 2.1 GB")
        self.memory_indicator.setObjectName("performance-indicator")
        self.cpu_indicator = QLabel("CPU: 45%")
        self.cpu_indicator.setObjectName("performance-indicator")

        performance_layout.addWidget(self.fps_indicator)
        performance_layout.addWidget(self.memory_indicator)
        performance_layout.addWidget(self.cpu_indicator)
        self.performance_group.setLayout(performance_layout)

        group_layout.addWidget(self.record_btn)
        group_layout.addWidget(self.stream_btn)
        group_layout.addWidget(self.performance_group)
        group.setLayout(group_layout)
        layout.addWidget(group)

    def setup_styles(self):
        """Setup modern styling for the new layout"""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QWidget#left-panel {
                background-color: #3c3c3c;
                border-right: 1px solid #555555;
            }
            
            QWidget#center-panel {
                background-color: #2b2b2b;
            }
            
            QWidget#right-panel {
                background-color: #3c3c3c;
                border-left: 1px solid #555555;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #404040;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 6px;
                padding: 8px 16px;
                color: #ffffff;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #5a5a5a;
                border-color: #777777;
            }
            
            QPushButton:checked {
                background-color: #007acc;
                border-color: #0099ff;
            }
            
            QLabel#preview-title {
                font-size: 16px;
                font-weight: bold;
                color: #00ff00;
                background-color: #1a1a1a;
                padding: 8px;
                border-radius: 6px;
            }
            
            QLabel#large-preview-area {
                background-color: #1a1a1a;
                border: 2px solid #404040;
                border-radius: 8px;
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
                padding: 20px;
            }
            
            QComboBox {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 6px 12px;
                color: #ffffff;
            }
            
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
            }
            
            QListWidget {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 4px;
                color: #ffffff;
                selection-background-color: #007acc;
            }
            
            QLineEdit {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 6px 12px;
                color: #ffffff;
            }
            
            QLabel#performance-indicator {
                color: #00ff00;
                font-weight: 500;
            }
            """
        )

    def setup_connections(self):
        """Setup signal connections"""
        self.detection_btn.toggled.connect(self.on_detection_toggle)
        self.alignment_btn.toggled.connect(self.on_alignment_toggle)
        self.face_swap_btn.toggled.connect(self.on_face_swap_toggle)
        self.enhancement_btn.toggled.connect(self.on_enhancement_toggle)

        self.camera_viewer_btn.toggled.connect(self.on_camera_viewer_toggle)
        self.face_align_viewer_btn.toggled.connect(self.on_face_align_viewer_toggle)
        self.face_swap_viewer_btn.toggled.connect(self.on_face_swap_viewer_toggle)
        self.merged_viewer_btn.toggled.connect(self.on_merged_viewer_toggle)

        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        self.maximize_btn.clicked.connect(self.maximize_window)
        self.settings_btn.clicked.connect(self.open_settings)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.stream_btn.clicked.connect(self.toggle_streaming)

        self.voice_pitch_slider.valueChanged.connect(self.on_voice_pitch_changed)
        self.source_type_combo.currentTextChanged.connect(self.on_source_type_changed)

    def setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        menubar.addMenu("File")
        menubar.addMenu("View")
        menubar.addMenu("Help")

    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def update_performance_metrics(self):
        """Update performance metrics display"""
        import random
        fps = random.randint(25, 35)
        memory = round(random.uniform(1.8, 2.5), 1)
        cpu = random.randint(40, 60)
        
        self.fps_indicator.setText(f"FPS: {fps}")
        self.memory_indicator.setText(f"Memory: {memory} GB")
        self.cpu_indicator.setText(f"CPU: {cpu}%")

    # Event handlers
    def on_detection_toggle(self, enabled):
        self.status_bar.showMessage(f"Detection: {'ON' if enabled else 'OFF'}")

    def on_alignment_toggle(self, enabled):
        self.status_bar.showMessage(f"Alignment: {'ON' if enabled else 'OFF'}")

    def on_face_swap_toggle(self, enabled):
        self.status_bar.showMessage(f"Face Swap: {'ON' if enabled else 'OFF'}")

    def on_enhancement_toggle(self, enabled):
        self.status_bar.showMessage(f"Enhancement: {'ON' if enabled else 'OFF'}")

    def on_camera_viewer_toggle(self, enabled):
        if enabled:
            self.face_align_viewer_btn.setChecked(False)
            self.face_swap_viewer_btn.setChecked(False)
            self.merged_viewer_btn.setChecked(False)

    def on_face_align_viewer_toggle(self, enabled):
        if enabled:
            self.camera_viewer_btn.setChecked(False)
            self.face_swap_viewer_btn.setChecked(False)
            self.merged_viewer_btn.setChecked(False)

    def on_face_swap_viewer_toggle(self, enabled):
        if enabled:
            self.camera_viewer_btn.setChecked(False)
            self.face_align_viewer_btn.setChecked(False)
            self.merged_viewer_btn.setChecked(False)

    def on_merged_viewer_toggle(self, enabled):
        if enabled:
            self.camera_viewer_btn.setChecked(False)
            self.face_align_viewer_btn.setChecked(False)
            self.face_swap_viewer_btn.setChecked(False)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True

    def maximize_window(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def open_settings(self):
        self.status_bar.showMessage("Opening settings...")

    def toggle_recording(self):
        if self.record_btn.text() == "Start Recording":
            self.record_btn.setText("Stop Recording")
            self.status_bar.showMessage("Recording started")
        else:
            self.record_btn.setText("Start Recording")
            self.status_bar.showMessage("Recording stopped")

    def toggle_streaming(self):
        if self.stream_btn.text() == "Start Streaming":
            self.stream_btn.setText("Stop Streaming")
            self.status_bar.showMessage("Streaming started")
        else:
            self.stream_btn.setText("Start Streaming")
            self.status_bar.showMessage("Streaming stopped")

    def on_voice_pitch_changed(self, value):
        self.voice_pitch_label.setText(f"Pitch: {value}")

    def on_source_type_changed(self, source_type):
        if source_type == "Camera":
            self.camera_group.setVisible(True)
            self.file_group.setVisible(False)
        else:
            self.camera_group.setVisible(False)
            self.file_group.setVisible(True)

    def update_video_frame(self, frame):
        """Update the video preview with a new frame"""
        if frame is not None:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            scaled_pixmap = pixmap.scaled(
                self.preview_area.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.preview_area.setPixmap(scaled_pixmap)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape and self.isFullScreen():
            self.showNormal()
            self.is_fullscreen = False
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle application close"""
        self.performance_timer.stop()
        event.accept() 