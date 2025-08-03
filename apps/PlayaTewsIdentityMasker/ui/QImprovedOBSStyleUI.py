#!/usr/bin/env python3
"""
Improved OBS-Style UI for PlayaTewsIdentityMasker
Addresses key UI/UX issues: video feed optimization, responsive design, accessibility
"""

from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np
from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon, QImage, QPalette, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QStyleFactory,
    QTabWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from localization import L
from resources.fonts import QXFontDB
from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel

from ..backend import StreamOutput
from ..backend.StreamOutput import SourceType
from .widgets.QBackendPanel import QBackendPanel
from .widgets.QCheckBoxCSWFlag import QCheckBoxCSWFlag
from .widgets.QCollapsibleComponentWrapper import (
    QCollapsibleComponentWrapper,
    QSmartCollapsibleGroup,
    group_small_components,
    make_collapsible,
)
from .widgets.QComboBoxCSWDynamicSingleSwitch import QComboBoxCSWDynamicSingleSwitch
from .widgets.QErrorCSWError import QErrorCSWError
from .widgets.QLabelCSWNumber import QLabelCSWNumber
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QLineEditCSWText import QLineEditCSWText
from .widgets.QPathEditCSWPaths import QPathEditCSWPaths
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber
from .widgets.QXPushButtonCSWSignal import QXPushButtonCSWSignal


class QImprovedOBSStyleUI(QWidget):
    """Improved OBS Studio-style UI with enhanced UX and video feed optimization"""

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
        self.scenes = []
        self.current_scene = None
        self.sources_by_scene = {}

        # UI State
        self.is_fullscreen = False
        self.video_fit_mode = "Stretch"  # Stretch, Fit, Fill, Original

        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.setup_accessibility()
        self.initialize_global_face_swap_state()

    def setup_ui(self):
        """Setup the improved main UI layout with video feed optimization"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create responsive splitter
        self.main_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Compact controls (15% of space)
        left_panel = self.create_compact_left_panel()
        left_panel.setMinimumWidth(250)
        left_panel.setMaximumWidth(350)

        # Center panel - Video display (70% of space)
        center_panel = self.create_optimized_center_panel()

        # Right panel - Settings (15% of space, collapsible)
        right_panel = self.create_compact_right_panel()
        right_panel.setMinimumWidth(200)
        right_panel.setMaximumWidth(300)

        # Add panels to splitter with optimized proportions
        self.main_splitter.addWidget(left_panel)
        self.main_splitter.addWidget(center_panel)
        self.main_splitter.addWidget(right_panel)

        # Set initial splitter sizes (15% - 70% - 15%)
        self.main_splitter.setSizes([300, 800, 250])

        main_layout.addWidget(self.main_splitter)
        self.setLayout(main_layout)

    def create_compact_left_panel(self):
        """Create compact left panel with essential controls"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Main action buttons
        self.create_main_action_buttons(layout)

        # Quick access tabs
        self.create_quick_access_tabs(layout)

        # Status indicators
        self.create_status_indicators(layout)

        panel.setLayout(layout)
        return panel

    def create_main_action_buttons(self, layout):
        """Create main action buttons with modern design"""
        group = QGroupBox("Actions")
        group.setObjectName("actions-group")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(8)

        # Streaming button
        self.stream_btn = self.create_modern_button(
            "Start Streaming", "#e74c3c", "stream"
        )
        self.stream_btn.setMinimumHeight(40)

        # Recording button
        self.record_btn = self.create_modern_button(
            "Start Recording", "#e67e22", "record"
        )
        self.record_btn.setMinimumHeight(40)

        # Face swap toggle
        self.global_face_swap_btn = self.create_modern_button(
            "Face Swap: ON", "#27ae60", "face-swap"
        )
        self.global_face_swap_btn.setCheckable(True)
        self.global_face_swap_btn.setChecked(True)
        self.global_face_swap_btn.setMinimumHeight(35)

        # Settings button
        self.settings_btn = self.create_modern_button("Settings", "#3498db", "settings")
        self.settings_btn.setMinimumHeight(35)

        for btn in [
            self.stream_btn,
            self.record_btn,
            self.global_face_swap_btn,
            self.settings_btn,
        ]:
            group_layout.addWidget(btn)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def create_quick_access_tabs(self, layout):
        """Create compact quick access tabs"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("quick-tabs")
        self.tab_widget.setMaximumHeight(150)

        # Sources tab
        sources_tab = QWidget()
        sources_layout = QVBoxLayout()
        self.sources_list = QListWidget()
        self.sources_list.setMaximumHeight(80)
        sources_layout.addWidget(self.sources_list)
        sources_tab.setLayout(sources_layout)

        # Models tab
        models_tab = QWidget()
        models_layout = QVBoxLayout()
        self.models_list = QListWidget()
        self.models_list.setMaximumHeight(80)
        models_layout.addWidget(self.models_list)
        models_tab.setLayout(models_layout)

        self.tab_widget.addTab(sources_tab, "Sources")
        self.tab_widget.addTab(models_tab, "Models")

        layout.addWidget(self.tab_widget)

    def create_status_indicators(self, layout):
        """Create compact status indicators"""
        status_group = QGroupBox("Status")
        status_group.setObjectName("status-group")
        status_layout = QVBoxLayout()
        status_layout.setSpacing(4)

        self.fps_label = QLabel("FPS: 30")
        self.memory_label = QLabel("Memory: 2.1 GB")
        self.cpu_label = QLabel("CPU: 45%")

        for label in [self.fps_label, self.memory_label, self.cpu_label]:
            label.setObjectName("status-label")
            status_layout.addWidget(label)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

    def create_optimized_center_panel(self):
        """Create center panel with maximized video display"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Video display area (90% of center panel)
        video_group = QGroupBox("Video Feed")
        video_group.setObjectName("video-group")
        video_layout = QVBoxLayout()
        video_layout.setContentsMargins(8, 8, 8, 8)

        # Video display with stretch-fit
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("Video Feed\n\nClick for fullscreen (F11)")
        self.video_label.setObjectName("video-display")
        self.video_label.setCursor(Qt.PointingHandCursor)

        # Video controls overlay
        self.create_video_controls(video_layout)

        video_layout.addWidget(self.video_label, 1)  # Takes all available space
        video_group.setLayout(video_layout)

        layout.addWidget(video_group, 1)  # Takes 90% of center panel

        # Bottom toolbar (10% of center panel)
        toolbar = self.create_bottom_toolbar()
        layout.addWidget(toolbar)

        panel.setLayout(layout)
        return panel

    def create_video_controls(self, layout):
        """Create video control overlay"""
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 8)

        # Fit mode selector
        self.fit_combo = QComboBox()
        self.fit_combo.addItems(["Stretch", "Fit", "Fill", "Original"])
        self.fit_combo.setCurrentText("Stretch")
        self.fit_combo.currentTextChanged.connect(self.on_fit_mode_changed)
        self.fit_combo.setObjectName("fit-combo")
        self.fit_combo.setMaximumWidth(100)

        # Fullscreen button
        self.fullscreen_btn = QToolButton()
        self.fullscreen_btn.setIcon(
            self.style().standardIcon(QStyleFactory.SP_TitleBarMaxButton)
        )
        self.fullscreen_btn.setToolTip("Toggle Fullscreen (F11)")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        self.fullscreen_btn.setObjectName("fullscreen-btn")

        controls_layout.addWidget(QLabel("Fit:"))
        controls_layout.addWidget(self.fit_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(self.fullscreen_btn)

        layout.addLayout(controls_layout)

    def create_bottom_toolbar(self):
        """Create minimal bottom toolbar"""
        toolbar = QWidget()
        toolbar.setObjectName("bottom-toolbar")
        toolbar.setMaximumHeight(30)

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status-label")

        layout.addWidget(self.status_label)
        layout.addStretch()

        toolbar.setLayout(layout)
        return toolbar

    def create_compact_right_panel(self):
        """Create compact right panel for settings"""
        panel = QWidget()
        panel.setObjectName("right-panel")

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # Collapsible settings sections
        self.create_collapsible_settings(layout)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def create_collapsible_settings(self, layout):
        """Create collapsible settings sections"""
        # Input settings
        input_group = QGroupBox("Input")
        input_group.setCheckable(True)
        input_group.setChecked(False)
        input_layout = QVBoxLayout()

        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["Camera 1", "Camera 2", "File"])
        input_layout.addWidget(QLabel("Source:"))
        input_layout.addWidget(self.camera_combo)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Face settings
        face_group = QGroupBox("Face")
        face_group.setCheckable(True)
        face_group.setChecked(False)
        face_layout = QVBoxLayout()

        self.face_model_combo = QComboBox()
        self.face_model_combo.addItems(["Model 1", "Model 2", "Custom"])
        face_layout.addWidget(QLabel("Model:"))
        face_layout.addWidget(self.face_model_combo)

        face_group.setLayout(face_layout)
        layout.addWidget(face_group)

        # Output settings
        output_group = QGroupBox("Output")
        output_group.setCheckable(True)
        output_group.setChecked(False)
        output_layout = QVBoxLayout()

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["HD", "Full HD", "4K"])
        output_layout.addWidget(QLabel("Quality:"))
        output_layout.addWidget(self.quality_combo)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

    def create_modern_button(self, text, color, object_name):
        """Create a modern styled button"""
        btn = QPushButton(text)
        btn.setObjectName(object_name)
        btn.setCursor(Qt.PointingHandCursor)

        btn.setStyleSheet(
            f"""
            QPushButton#{object_name} {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
                padding: 8px 12px;
            }}
            QPushButton#{object_name}:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton#{object_name}:pressed {{
                background-color: {self.darken_color(color, 0.3)};
            }}
        """
        )
        return btn

    def darken_color(self, color, factor=0.2):
        """Darken a hex color"""
        if color.startswith("#"):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)

            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))

            return f"#{r:02x}{g:02x}{b:02x}"
        return color

    def setup_styles(self):
        """Setup improved modern styling"""
        self.setStyleSheet(
            """
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            
            QSplitter::handle {
                background-color: #404040;
                width: 2px;
            }
            
            QSplitter::handle:hover {
                background-color: #606060;
            }
            
            QGroupBox {
                font-weight: 600;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 1ex;
                padding-top: 12px;
                background-color: #2a2a2a;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px 0 6px;
                color: #ffffff;
            }
            
            QGroupBox#video-group {
                border: 2px solid #404040;
                background-color: #0a0a0a;
            }
            
            QLabel#video-display {
                background-color: #1a1a1a;
                border: 2px solid #404040;
                border-radius: 6px;
                color: #ffffff;
                font-size: 16px;
                font-weight: 500;
                padding: 20px;
            }
            
            QLabel#video-display:hover {
                border-color: #606060;
            }
            
            QTabWidget::pane {
                border: 1px solid #404040;
                border-radius: 4px;
                background-color: #2a2a2a;
            }
            
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 6px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11px;
            }
            
            QTabBar::tab:selected {
                background-color: #2196F3;
            }
            
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #ffffff;
                font-size: 11px;
            }
            
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #303030;
            }
            
            QListWidget::item:selected {
                background-color: #2196F3;
            }
            
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
                font-size: 11px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 16px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 3px solid white;
            }
            
            QToolButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                padding: 4px;
                color: white;
                min-width: 24px;
                min-height: 24px;
            }
            
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            QLabel#status-label {
                color: #b0b0b0;
                font-size: 11px;
            }
            
            QWidget#bottom-toolbar {
                background-color: #2a2a2a;
                border-top: 1px solid #404040;
            }
        """
        )

    def setup_connections(self):
        """Setup signal connections"""
        # Connect buttons
        if hasattr(self, "stream_btn"):
            self.stream_btn.clicked.connect(self.on_stream_toggle)
        if hasattr(self, "record_btn"):
            self.record_btn.clicked.connect(self.on_record_toggle)
        if hasattr(self, "global_face_swap_btn"):
            self.global_face_swap_btn.toggled.connect(self.on_global_face_swap_toggled)
        if hasattr(self, "settings_btn"):
            self.settings_btn.clicked.connect(self.open_processing_window)

        # Connect video controls
        if hasattr(self, "video_label"):
            self.video_label.mousePressEvent = self.on_video_click

    def setup_accessibility(self):
        """Setup accessibility features"""
        # Set accessible names
        self.setAccessibleName("PlayaTews Identity Masker")
        self.setAccessibleDescription(
            "Professional face-swapping and streaming application"
        )

        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        # F11 for fullscreen
        fullscreen_action = QAction("Toggle Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.addAction(fullscreen_action)

        # Ctrl+S for streaming
        stream_action = QAction("Toggle Streaming", self)
        stream_action.setShortcut("Ctrl+S")
        stream_action.triggered.connect(self.on_stream_toggle)
        self.addAction(stream_action)

        # Ctrl+R for recording
        record_action = QAction("Toggle Recording", self)
        record_action.setShortcut("Ctrl+R")
        record_action.triggered.connect(self.on_record_toggle)
        self.addAction(record_action)

    def on_fit_mode_changed(self, mode):
        """Handle video fit mode changes"""
        self.video_fit_mode = mode
        # Re-apply current frame with new fit mode
        if hasattr(self, "_current_frame"):
            self.update_video_frame(self._current_frame)

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if not self.is_fullscreen:
            self.enter_fullscreen()
        else:
            self.exit_fullscreen()

    def enter_fullscreen(self):
        """Enter fullscreen mode"""
        self.original_geometry = self.geometry()
        self.is_fullscreen = True
        self.showFullScreen()

    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        self.is_fullscreen = False
        self.showNormal()
        if hasattr(self, "original_geometry") and self.original_geometry:
            self.setGeometry(self.original_geometry)

    def on_video_click(self, event):
        """Handle video click for fullscreen"""
        if event.button() == Qt.LeftButton:
            self.toggle_fullscreen()

    def update_video_frame(self, frame):
        """Update the video display with a new frame"""
        if frame is not None:
            self._current_frame = frame

            # Convert numpy array to QImage
            if frame.dtype != np.uint8:
                frame = (frame * 255).astype(np.uint8)

            height, width, channel = frame.shape
            bytes_per_line = 3 * width

            # Convert BGR to RGB if needed
            if channel == 3:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                frame_rgb = frame

            q_image = QImage(
                frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888
            )
            q_pixmap = QPixmap.fromImage(q_image)

            # Apply fit mode
            scaled_pixmap = self.apply_fit_mode(q_pixmap, self.video_label.size())
            self.video_label.setPixmap(scaled_pixmap)

    def apply_fit_mode(self, pixmap, target_size):
        """Apply the selected fit mode to the pixmap"""
        if self.video_fit_mode == "Stretch":
            return pixmap.scaled(
                target_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )
        elif self.video_fit_mode == "Fit":
            return pixmap.scaled(
                target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        elif self.video_fit_mode == "Fill":
            return pixmap.scaled(
                target_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
        else:  # Original
            return pixmap

    def on_stream_toggle(self):
        """Handle streaming toggle"""
        if self.stream_btn.text() == "Start Streaming":
            self.stream_btn.setText("Stop Streaming")
            self.show_status_message("Streaming started")
        else:
            self.stream_btn.setText("Start Streaming")
            self.show_status_message("Streaming stopped")

    def on_record_toggle(self):
        """Handle recording toggle"""
        if self.record_btn.text() == "Start Recording":
            self.record_btn.setText("Stop Recording")
            self.show_status_message("Recording started")
        else:
            self.record_btn.setText("Start Recording")
            self.show_status_message("Recording stopped")

    def on_global_face_swap_toggled(self, enabled):
        """Handle global face swap toggle"""
        if enabled:
            self.global_face_swap_btn.setText("Face Swap: ON")
            self.enable_all_face_swap_components()
            self.show_status_message("Face swap enabled")
        else:
            self.global_face_swap_btn.setText("Face Swap: OFF")
            self.disable_all_face_swap_components()
            self.show_status_message("Face swap disabled")

    def show_status_message(self, message):
        """Show a status message"""
        if hasattr(self, "status_label"):
            self.status_label.setText(message)

    def enable_all_face_swap_components(self):
        """Enable all face swap components"""
        # Implementation for enabling face swap components
        pass

    def disable_all_face_swap_components(self):
        """Disable all face swap components"""
        # Implementation for disabling face swap components
        pass

    def open_processing_window(self):
        """Open the processing window"""
        from .QProcessingWindow import QProcessingWindow

        self.processing_window = QProcessingWindow(self.face_swap_components, self)
        self.processing_window.show()

    def initialize_global_face_swap_state(self):
        """Initialize global face swap state"""
        # Implementation for initializing face swap state
        pass

    def resizeEvent(self, event):
        """Handle responsive resizing"""
        super().resizeEvent(event)
        # Adjust splitter sizes based on window size
        width = self.width()
        if width > 1200:
            # Large screen: 15% - 70% - 15%
            self.main_splitter.setSizes([width * 0.15, width * 0.7, width * 0.15])
        elif width > 800:
            # Medium screen: 20% - 60% - 20%
            self.main_splitter.setSizes([width * 0.2, width * 0.6, width * 0.2])
        else:
            # Small screen: 25% - 50% - 25%
            self.main_splitter.setSizes([width * 0.25, width * 0.5, width * 0.25])

    def keyPressEvent(self, event):
        """Handle keyboard events"""
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape and self.is_fullscreen:
            self.exit_fullscreen()
        else:
            super().keyPressEvent(event)
