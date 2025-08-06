#!/usr/bin/env python3
"""
Enhanced New Layout UI for PlayaTewsIdentityMasker
Integrates accessibility, multiple themes, and comprehensive backend integration
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor
from PyQt5.QtWidgets import (
    QComboBox, QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QPushButton, QSizePolicy,
    QSlider, QSplitter, QStatusBar, QVBoxLayout, QWidget, QCheckBox,
    QTabWidget, QScrollArea, QProgressBar, QToolButton, QMenu, QAction
)

# Import accessibility manager
try:
    from accessibility_manager import get_accessibility_manager, announce, register_focusable_element
    ACCESSIBILITY_AVAILABLE = True
except ImportError:
    ACCESSIBILITY_AVAILABLE = False
    def get_accessibility_manager(): return None
    def announce(message, priority="normal"): pass
    def register_focusable_element(*args): pass

from ..backend import StreamOutput


class QEnhancedNewLayoutUI(QMainWindow):
    """Enhanced New Layout UI with accessibility, themes, and backend integration"""

    # Theme definitions
    THEMES = {
        'dark': {
            'name': 'Dark Theme',
            'background': '#2b2b2b',
            'surface': '#3c3c3c',
            'primary': '#007acc',
            'secondary': '#4a4a4a',
            'text': '#ffffff',
            'text_secondary': '#cccccc',
            'accent': '#00ff00',
            'error': '#e74c3c',
            'warning': '#e67e22',
            'success': '#27ae60'
        },
        'light': {
            'name': 'Light Theme',
            'background': '#f5f5f5',
            'surface': '#ffffff',
            'primary': '#1976d2',
            'secondary': '#e0e0e0',
            'text': '#212121',
            'text_secondary': '#757575',
            'accent': '#00c853',
            'error': '#d32f2f',
            'warning': '#f57c00',
            'success': '#388e3c'
        },
        'blue': {
            'name': 'Blue Theme',
            'background': '#1a237e',
            'surface': '#283593',
            'primary': '#42a5f5',
            'secondary': '#3949ab',
            'text': '#ffffff',
            'text_secondary': '#e3f2fd',
            'accent': '#00bcd4',
            'error': '#f44336',
            'warning': '#ff9800',
            'success': '#4caf50'
        },
        'green': {
            'name': 'Green Theme',
            'background': '#1b5e20',
            'surface': '#2e7d32',
            'primary': '#66bb6a',
            'secondary': '#388e3c',
            'text': '#ffffff',
            'text_secondary': '#e8f5e8',
            'accent': '#00e676',
            'error': '#f44336',
            'warning': '#ff9800',
            'success': '#4caf50'
        }
    }

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
        self.current_theme = 'dark'
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance_metrics)
        self.performance_timer.start(1000)

        # Accessibility
        self.accessibility_manager = get_accessibility_manager() if ACCESSIBILITY_AVAILABLE else None

        # Backend state
        self.is_streaming = False
        self.is_recording = False
        self.face_swap_enabled = True

        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.setup_accessibility()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_animations()

    def setup_ui(self):
        """Setup the enhanced new layout UI with three-panel design"""
        self.setWindowTitle("PlayaTews Identity Masker - Enhanced Layout")
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
        group.setObjectName("dfm-quick-access")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)

        self.dfm_model_list = QListWidget()
        self.dfm_model_list.setMaximumHeight(120)
        self.dfm_model_list.setObjectName("dfm-model-list")

        # Add sample DFM models
        sample_models = ["Model 1", "Model 2", "Model 3", "Custom Model"]
        for model in sample_models:
            self.dfm_model_list.addItem(QListWidgetItem(model))

        dfm_controls = QHBoxLayout()
        self.load_dfm_btn = QPushButton("Load DFM")
        self.load_dfm_btn.setObjectName("load-dfm-btn")
        self.refresh_dfm_btn = QPushButton("Refresh")
        self.refresh_dfm_btn.setObjectName("refresh-btn")
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
        group.setObjectName("input-sources")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)

        source_type_layout = QHBoxLayout()
        source_type_layout.addWidget(QLabel("Type:"))
        self.source_type_combo = QComboBox()
        self.source_type_combo.addItems(["Camera", "File", "Image Sequence"])
        self.source_type_combo.setObjectName("source-type-combo")
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
        group.setObjectName("voice-changer")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)

        self.voice_enable_checkbox = QCheckBox("Enable Voice Changer")
        self.voice_enable_checkbox.setObjectName("voice-enable-checkbox")

        voice_effect_layout = QHBoxLayout()
        voice_effect_layout.addWidget(QLabel("Effect:"))
        self.voice_effect_combo = QComboBox()
        self.voice_effect_combo.addItems(
            ["None", "Pitch Shift", "Echo", "Reverb", "Custom"]
        )
        self.voice_effect_combo.setObjectName("voice-effect-combo")
        voice_effect_layout.addWidget(self.voice_effect_combo)

        self.voice_pitch_slider = QSlider(Qt.Horizontal)
        self.voice_pitch_slider.setRange(-12, 12)
        self.voice_pitch_slider.setValue(0)
        self.voice_pitch_slider.setObjectName("voice-pitch-slider")
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
        self.detection_btn.setObjectName("processing-btn")
        self.detection_btn.setCheckable(True)
        self.detection_btn.setChecked(True)

        self.alignment_btn = QPushButton("Alignment")
        self.alignment_btn.setObjectName("processing-btn")
        self.alignment_btn.setCheckable(True)
        self.alignment_btn.setChecked(True)

        self.face_swap_btn = QPushButton("Face Swap")
        self.face_swap_btn.setObjectName("processing-btn")
        self.face_swap_btn.setCheckable(True)
        self.face_swap_btn.setChecked(True)

        self.enhancement_btn = QPushButton("Enhancement")
        self.enhancement_btn.setObjectName("processing-btn")
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
        self.fullscreen_btn.setObjectName("fullscreen-btn")
        self.maximize_btn = QPushButton("Maximize")
        self.maximize_btn.setObjectName("maximize-btn")
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setObjectName("settings-btn")

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
        self.camera_viewer_btn.setObjectName("viewer-btn")
        self.camera_viewer_btn.setCheckable(True)

        self.face_align_viewer_btn = QPushButton("Face Align")
        self.face_align_viewer_btn.setObjectName("viewer-btn")
        self.face_align_viewer_btn.setCheckable(True)

        self.face_swap_viewer_btn = QPushButton("Face Swap")
        self.face_swap_viewer_btn.setObjectName("viewer-btn")
        self.face_swap_viewer_btn.setCheckable(True)

        self.merged_viewer_btn = QPushButton("Merged")
        self.merged_viewer_btn.setObjectName("viewer-btn")
        self.merged_viewer_btn.setCheckable(True)
        self.merged_viewer_btn.setChecked(True)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setObjectName("viewer-separator")

        self.controls_btn = QPushButton("Controls")
        self.controls_btn.setObjectName("controls-btn")

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
        group.setObjectName("settings")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)

        # Theme Selection
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(self.THEMES.keys()))
        self.theme_combo.setCurrentText("dark")
        self.theme_combo.setObjectName("theme-combo")
        theme_layout.addWidget(self.theme_combo)

        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low", "Medium", "High", "Ultra"])
        self.quality_combo.setCurrentText("High")
        self.quality_combo.setObjectName("quality-combo")
        quality_layout.addWidget(self.quality_combo)

        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["15", "24", "30", "60"])
        self.fps_combo.setCurrentText("30")
        self.fps_combo.setObjectName("fps-combo")
        fps_layout.addWidget(self.fps_combo)

        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory:"))
        self.memory_combo = QComboBox()
        self.memory_combo.addItems(["2GB", "4GB", "8GB", "16GB"])
        self.memory_combo.setCurrentText("4GB")
        self.memory_combo.setObjectName("memory-combo")
        memory_layout.addWidget(self.memory_combo)

        self.advanced_settings_checkbox = QCheckBox("Advanced Settings")
        self.advanced_settings_checkbox.setObjectName("advanced-settings-checkbox")

        group_layout.addLayout(theme_layout)
        group_layout.addLayout(quality_layout)
        group_layout.addLayout(fps_layout)
        group_layout.addLayout(memory_layout)
        group_layout.addWidget(self.advanced_settings_checkbox)
        group.setLayout(group_layout)
        layout.addWidget(group)

    def create_additional_controls(self, layout):
        """Create Additional Controls section"""
        group = QGroupBox("Additional Controls")
        group.setObjectName("additional-controls")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)

        self.record_btn = QPushButton("Start Recording")
        self.record_btn.setObjectName("record-btn")

        self.stream_btn = QPushButton("Start Streaming")
        self.stream_btn.setObjectName("stream-btn")

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
        """Setup modern styling with theme support"""
        self.apply_theme(self.current_theme)

    def apply_theme(self, theme_name: str):
        """Apply a specific theme"""
        if theme_name not in self.THEMES:
            theme_name = 'dark'
        
        self.current_theme = theme_name
        theme = self.THEMES[theme_name]
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
            
            QWidget#left-panel {{
                background-color: {theme['surface']};
                border-right: 1px solid {theme['secondary']};
            }}
            
            QWidget#center-panel {{
                background-color: {theme['background']};
            }}
            
            QWidget#right-panel {{
                background-color: {theme['surface']};
                border-left: 1px solid {theme['secondary']};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {theme['secondary']};
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: {theme['surface']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {theme['text']};
            }}
            
            QPushButton {{
                background-color: {theme['secondary']};
                border: 1px solid {theme['primary']};
                border-radius: 6px;
                padding: 8px 16px;
                color: {theme['text']};
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background-color: {theme['primary']};
                border-color: {theme['accent']};
            }}
            
            QPushButton:checked {{
                background-color: {theme['success']};
                border-color: {theme['accent']};
            }}
            
            QPushButton#processing-btn {{
                background-color: {theme['primary']};
                border-color: {theme['accent']};
            }}
            
            QPushButton#processing-btn:checked {{
                background-color: {theme['success']};
                border-color: {theme['accent']};
            }}
            
            QPushButton#viewer-btn {{
                background-color: {theme['secondary']};
                border-color: {theme['primary']};
            }}
            
            QPushButton#viewer-btn:checked {{
                background-color: {theme['primary']};
                border-color: {theme['accent']};
            }}
            
            QPushButton#fullscreen-btn, QPushButton#maximize-btn, QPushButton#settings-btn {{
                background-color: {theme['warning']};
                border-color: {theme['accent']};
            }}
            
            QPushButton#fullscreen-btn:hover, QPushButton#maximize-btn:hover, QPushButton#settings-btn:hover {{
                background-color: {theme['accent']};
                border-color: {theme['primary']};
            }}
            
            QLabel#preview-title {{
                font-size: 16px;
                font-weight: bold;
                color: {theme['accent']};
                background-color: {theme['surface']};
                padding: 8px;
                border-radius: 6px;
            }}
            
            QLabel#large-preview-area {{
                background-color: {theme['surface']};
                border: 2px solid {theme['secondary']};
                border-radius: 8px;
                color: {theme['text']};
                font-size: 14px;
                font-weight: 500;
                padding: 20px;
            }}
            
            QComboBox {{
                background-color: {theme['secondary']};
                border: 1px solid {theme['primary']};
                border-radius: 4px;
                padding: 6px 12px;
                color: {theme['text']};
            }}
            
            QComboBox:hover {{
                border-color: {theme['accent']};
            }}
            
            QCheckBox {{
                color: {theme['text']};
                spacing: 8px;
            }}
            
            QListWidget {{
                background-color: {theme['secondary']};
                border: 1px solid {theme['primary']};
                border-radius: 4px;
                color: {theme['text']};
                selection-background-color: {theme['primary']};
            }}
            
            QLineEdit {{
                background-color: {theme['secondary']};
                border: 1px solid {theme['primary']};
                border-radius: 4px;
                padding: 6px 12px;
                color: {theme['text']};
            }}
            
            QLineEdit:focus {{
                border-color: {theme['accent']};
            }}
            
            QLabel#performance-indicator {{
                color: {theme['accent']};
                font-weight: 500;
            }}
            
            QFrame#viewer-separator {{
                background-color: {theme['secondary']};
            }}
        """)

    def setup_connections(self):
        """Setup signal connections"""
        # Processing component connections
        self.detection_btn.toggled.connect(self.on_detection_toggle)
        self.alignment_btn.toggled.connect(self.on_alignment_toggle)
        self.face_swap_btn.toggled.connect(self.on_face_swap_toggle)
        self.enhancement_btn.toggled.connect(self.on_enhancement_toggle)

        # Viewer connections
        self.camera_viewer_btn.toggled.connect(self.on_camera_viewer_toggle)
        self.face_align_viewer_btn.toggled.connect(self.on_face_align_viewer_toggle)
        self.face_swap_viewer_btn.toggled.connect(self.on_face_swap_viewer_toggle)
        self.merged_viewer_btn.toggled.connect(self.on_merged_viewer_toggle)

        # Control connections
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        self.maximize_btn.clicked.connect(self.maximize_window)
        self.settings_btn.clicked.connect(self.open_settings)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.stream_btn.clicked.connect(self.toggle_streaming)

        # Voice changer connections
        self.voice_pitch_slider.valueChanged.connect(self.on_voice_pitch_changed)

        # Source type connection
        self.source_type_combo.currentTextChanged.connect(self.on_source_type_changed)

        # Theme connection
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)

    def setup_accessibility(self):
        """Setup accessibility features"""
        if not self.accessibility_manager:
            return

        # Register focusable elements
        register_focusable_element("dfm-model-list", "list", "DFM Model List")
        register_focusable_element("load-dfm-btn", "button", "Load DFM Button")
        register_focusable_element("source-type-combo", "combobox", "Source Type Selection")
        register_focusable_element("voice-enable-checkbox", "checkbox", "Voice Changer Enable")
        register_focusable_element("detection-btn", "button", "Detection Toggle")
        register_focusable_element("alignment-btn", "button", "Alignment Toggle")
        register_focusable_element("face-swap-btn", "button", "Face Swap Toggle")
        register_focusable_element("enhancement-btn", "button", "Enhancement Toggle")
        register_focusable_element("preview-area", "display", "Video Preview Area")
        register_focusable_element("fullscreen-btn", "button", "Fullscreen Button")
        register_focusable_element("record-btn", "button", "Recording Button")
        register_focusable_element("stream-btn", "button", "Streaming Button")

        announce("Enhanced layout interface loaded successfully")

    def setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        new_action = QAction("New", self)
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        exit_action = QAction("Exit", self)
        
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("View")
        fullscreen_action = QAction("Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        view_menu.addAction(fullscreen_action)

        # Theme menu
        theme_menu = menubar.addMenu("Theme")
        for theme_name in self.THEMES.keys():
            theme_action = QAction(self.THEMES[theme_name]['name'], self)
            theme_action.triggered.connect(lambda checked, name=theme_name: self.apply_theme(name))
            theme_menu.addAction(theme_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_animations(self):
        """Setup UI animations"""
        # Button hover animations
        for btn in self.findChildren(QPushButton):
            if btn.objectName():
                self.setup_button_animation(btn)

    def setup_button_animation(self, button):
        """Setup animation for a button"""
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(150)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        button.animation = animation

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
        message = f"Detection: {'ON' if enabled else 'OFF'}"
        self.status_bar.showMessage(message)
        if self.accessibility_manager:
            announce(message)

    def on_alignment_toggle(self, enabled):
        message = f"Alignment: {'ON' if enabled else 'OFF'}"
        self.status_bar.showMessage(message)
        if self.accessibility_manager:
            announce(message)

    def on_face_swap_toggle(self, enabled):
        message = f"Face Swap: {'ON' if enabled else 'OFF'}"
        self.status_bar.showMessage(message)
        if self.accessibility_manager:
            announce(message)

    def on_enhancement_toggle(self, enabled):
        message = f"Enhancement: {'ON' if enabled else 'OFF'}"
        self.status_bar.showMessage(message)
        if self.accessibility_manager:
            announce(message)

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
            if self.accessibility_manager:
                announce("Exited fullscreen mode")
        else:
            self.showFullScreen()
            self.is_fullscreen = True
            if self.accessibility_manager:
                announce("Entered fullscreen mode")

    def maximize_window(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def open_settings(self):
        self.status_bar.showMessage("Opening settings...")
        if self.accessibility_manager:
            announce("Opening settings window")

    def toggle_recording(self):
        if self.record_btn.text() == "Start Recording":
            self.record_btn.setText("Stop Recording")
            self.is_recording = True
            message = "Recording started"
            self.status_bar.showMessage(message)
            if self.accessibility_manager:
                announce(message)
        else:
            self.record_btn.setText("Start Recording")
            self.is_recording = False
            message = "Recording stopped"
            self.status_bar.showMessage(message)
            if self.accessibility_manager:
                announce(message)

    def toggle_streaming(self):
        if self.stream_btn.text() == "Start Streaming":
            self.stream_btn.setText("Stop Streaming")
            self.is_streaming = True
            message = "Streaming started"
            self.status_bar.showMessage(message)
            if self.accessibility_manager:
                announce(message)
        else:
            self.stream_btn.setText("Start Streaming")
            self.is_streaming = False
            message = "Streaming stopped"
            self.status_bar.showMessage(message)
            if self.accessibility_manager:
                announce(message)

    def on_voice_pitch_changed(self, value):
        self.voice_pitch_label.setText(f"Pitch: {value}")

    def on_source_type_changed(self, source_type):
        if source_type == "Camera":
            self.camera_group.setVisible(True)
            self.file_group.setVisible(False)
        else:
            self.camera_group.setVisible(False)
            self.file_group.setVisible(True)

    def on_theme_changed(self, theme_name):
        self.apply_theme(theme_name)
        if self.accessibility_manager:
            announce(f"Theme changed to {self.THEMES[theme_name]['name']}")

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
        if self.accessibility_manager:
            announce("Application closing")
        event.accept()
