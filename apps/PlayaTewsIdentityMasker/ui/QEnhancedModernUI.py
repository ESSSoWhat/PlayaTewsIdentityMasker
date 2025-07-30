#!/usr/bin/env python3
"""
Enhanced Modern UI for PlayaTewsIdentityMasker
Implements comprehensive UI/UX improvements following modern design principles
"""

from pathlib import Path
from typing import List, Dict, Optional, Any
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize, QRect
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon, QPixmap, QPainter, QBrush, QPen
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QPushButton, QLabel, QComboBox, QSpinBox, QLineEdit,
                            QCheckBox, QGroupBox, QSplitter, QTabWidget,
                            QListWidget, QListWidgetItem, QSlider, QFrame,
                            QTextEdit, QProgressBar, QScrollArea, QSizePolicy,
                            QToolButton, QMenu, QAction, QStatusBar, QToolBar,
                            QDockWidget, QMainWindow, QApplication, QStyleFactory)

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
from .widgets.QCollapsibleComponentWrapper import (
    QCollapsibleComponentWrapper, 
    QSmartCollapsibleGroup,
    make_collapsible,
    group_small_components
)

from ..backend import StreamOutput
from ..backend.StreamOutput import SourceType


class QModernVideoDisplay(QWidget):
    """Enhanced video display with stretch-fit and fullscreen capabilities"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()
        self.is_fullscreen = False
        self.original_geometry = None
        
    def setup_ui(self):
        """Setup the video display UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Video display area (80%+ of available space)
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("Video Feed")
        self.video_label.setObjectName("video-display")
        
        # Control overlay (appears on hover)
        self.control_overlay = QWidget()
        self.control_overlay.setObjectName("control-overlay")
        overlay_layout = QHBoxLayout()
        overlay_layout.setContentsMargins(16, 16, 16, 16)
        
        # Fullscreen button
        self.fullscreen_btn = QToolButton()
        self.fullscreen_btn.setIcon(self.style().standardIcon(QStyleFactory.SP_TitleBarMaxButton))
        self.fullscreen_btn.setToolTip("Toggle Fullscreen (F11)")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        self.fullscreen_btn.setObjectName("fullscreen-btn")
        
        # Fit mode selector
        self.fit_combo = QComboBox()
        self.fit_combo.addItems(["Stretch", "Fit", "Fill", "Original"])
        self.fit_combo.setCurrentText("Stretch")
        self.fit_combo.currentTextChanged.connect(self.on_fit_mode_changed)
        self.fit_combo.setObjectName("fit-mode-combo")
        
        overlay_layout.addWidget(self.fullscreen_btn)
        overlay_layout.addStretch()
        overlay_layout.addWidget(QLabel("Fit Mode:"))
        overlay_layout.addWidget(self.fit_combo)
        
        self.control_overlay.setLayout(overlay_layout)
        
        # Stack video and overlay
        self.video_container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.video_label)
        container_layout.addWidget(self.control_overlay)
        self.video_container.setLayout(container_layout)
        
        layout.addWidget(self.video_container)
        self.setLayout(layout)
        
        # Setup hover detection
        self.video_container.enterEvent = self.on_enter
        self.video_container.leaveEvent = self.on_leave
        
    def setup_styles(self):
        """Setup modern video display styles"""
        self.setStyleSheet("""
            QWidget#video-display {
                background-color: #1a1a1a;
                border: 2px solid #404040;
                border-radius: 8px;
                color: #ffffff;
                font-size: 18px;
                font-weight: 500;
            }
            
            QWidget#control-overlay {
                background-color: rgba(0, 0, 0, 0.7);
                border-radius: 8px;
                margin: 8px;
            }
            
            QToolButton#fullscreen-btn {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            
            QToolButton#fullscreen-btn:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            QComboBox#fit-mode-combo {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                padding: 6px 12px;
                color: white;
                min-width: 100px;
            }
            
            QComboBox#fit-mode-combo::drop-down {
                border: none;
            }
            
            QComboBox#fit-mode-combo::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
            }
        """)
        
    def on_enter(self, event):
        """Show controls on hover"""
        self.control_overlay.show()
        
    def on_leave(self, event):
        """Hide controls when not hovering"""
        if not self.is_fullscreen:
            self.control_overlay.hide()
            
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
        self.control_overlay.show()
        
    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        self.is_fullscreen = False
        self.showNormal()
        if self.original_geometry:
            self.setGeometry(self.original_geometry)
        self.control_overlay.hide()
        
    def on_fit_mode_changed(self, mode):
        """Handle fit mode changes"""
        # Implementation for different fit modes
        pass
        
    def update_video_frame(self, frame):
        """Update the video display with a new frame"""
        if frame is not None:
            # Convert frame to QPixmap and display
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QPixmap.fromImage(
                QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            )
            self.video_label.setPixmap(q_image.scaled(
                self.video_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))


class QModernControlPanel(QWidget):
    """Modern control panel with improved layout and accessibility"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Setup the modern control panel"""
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Main control buttons
        self.create_main_controls(layout)
        
        # Quick access tabs
        self.create_quick_access_tabs(layout)
        
        # Status indicators
        self.create_status_indicators(layout)
        
        self.setLayout(layout)
        
    def create_main_controls(self, layout):
        """Create main control buttons"""
        controls_group = QGroupBox("Main Controls")
        controls_layout = QGridLayout()
        controls_layout.setSpacing(12)
        
        # Streaming controls
        self.stream_btn = self.create_modern_button("Start Streaming", "#e74c3c", "stream")
        self.record_btn = self.create_modern_button("Start Recording", "#e67e22", "record")
        
        # Face swap controls
        self.face_swap_btn = self.create_modern_button("Face Swap: ON", "#27ae60", "face-swap")
        self.face_swap_btn.setCheckable(True)
        self.face_swap_btn.setChecked(True)
        
        # Settings button
        self.settings_btn = self.create_modern_button("Settings", "#3498db", "settings")
        
        # Layout buttons in grid
        controls_layout.addWidget(self.stream_btn, 0, 0)
        controls_layout.addWidget(self.record_btn, 0, 1)
        controls_layout.addWidget(self.face_swap_btn, 1, 0, 1, 2)
        controls_layout.addWidget(self.settings_btn, 2, 0, 1, 2)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
    def create_quick_access_tabs(self, layout):
        """Create quick access tabs for common functions"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("quick-access-tabs")
        
        # Sources tab
        sources_tab = QWidget()
        sources_layout = QVBoxLayout()
        self.sources_list = QListWidget()
        self.sources_list.setMaximumHeight(120)
        sources_layout.addWidget(self.sources_list)
        sources_tab.setLayout(sources_layout)
        
        # Models tab
        models_tab = QWidget()
        models_layout = QVBoxLayout()
        self.models_list = QListWidget()
        self.models_list.setMaximumHeight(120)
        models_layout.addWidget(self.models_list)
        models_tab.setLayout(models_layout)
        
        # Voice tab
        voice_tab = QWidget()
        voice_layout = QVBoxLayout()
        self.voice_enabled = QCheckBox("Voice Changer")
        self.voice_effect = QComboBox()
        self.voice_effect.addItems(["None", "Echo", "Pitch", "Reverb"])
        voice_layout.addWidget(self.voice_enabled)
        voice_layout.addWidget(self.voice_effect)
        voice_layout.addStretch()
        voice_tab.setLayout(voice_layout)
        
        self.tab_widget.addTab(sources_tab, "Sources")
        self.tab_widget.addTab(models_tab, "Models")
        self.tab_widget.addTab(voice_tab, "Voice")
        
        layout.addWidget(self.tab_widget)
        
    def create_status_indicators(self, layout):
        """Create status indicators"""
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        
        # Performance indicators
        self.fps_label = QLabel("FPS: 30")
        self.memory_label = QLabel("Memory: 2.1 GB")
        self.cpu_label = QLabel("CPU: 45%")
        
        for label in [self.fps_label, self.memory_label, self.cpu_label]:
            label.setObjectName("status-label")
            status_layout.addWidget(label)
            
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
    def create_modern_button(self, text, color, object_name):
        """Create a modern styled button"""
        btn = QPushButton(text)
        btn.setObjectName(object_name)
        btn.setMinimumHeight(40)
        btn.setStyleSheet(f"""
            QPushButton#{object_name} {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                padding: 8px 16px;
            }}
            QPushButton#{object_name}:hover {{
                background-color: {self.darken_color(color)};
                transform: translateY(-1px);
            }}
            QPushButton#{object_name}:pressed {{
                background-color: {self.darken_color(color, 0.3)};
                transform: translateY(0px);
            }}
        """)
        return btn
        
    def darken_color(self, color, factor=0.2):
        """Darken a hex color"""
        # Simple color darkening - in production, use proper color manipulation
        return color
        
    def setup_styles(self):
        """Setup modern control panel styles"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 16px;
                background-color: #2a2a2a;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px 0 8px;
                color: #ffffff;
            }
            
            QTabWidget::pane {
                border: 1px solid #404040;
                border-radius: 4px;
                background-color: #2a2a2a;
            }
            
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #2196F3;
            }
            
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #ffffff;
            }
            
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #303030;
            }
            
            QListWidget::item:selected {
                background-color: #2196F3;
            }
            
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #404040;
                border-radius: 3px;
                background-color: #1e1e1e;
            }
            
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #2196F3;
            }
            
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px 12px;
                color: #ffffff;
                min-height: 20px;
            }
            
            QLabel#status-label {
                color: #ffffff;
                font-size: 12px;
                padding: 4px 0;
            }
        """)


class QEnhancedModernUI(QWidget):
    """Enhanced Modern UI implementing comprehensive UI/UX improvements"""
    
    def __init__(self, stream_output_backend: StreamOutput, userdata_path: Path, 
                 face_swap_components=None, viewers_components=None, voice_changer_backend=None):
        super().__init__()
        self.stream_output_backend = stream_output_backend
        self.userdata_path = userdata_path
        self.face_swap_components = face_swap_components or {}
        self.viewers_components = viewers_components or {}
        self.voice_changer_backend = voice_changer_backend
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.setup_animations()
        self.setup_accessibility()
        
    def setup_ui(self):
        """Setup the enhanced modern UI layout"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create main splitter for responsive layout
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Modern control panel (20% of space)
        self.left_panel = QModernControlPanel()
        self.left_panel.setMinimumWidth(300)
        self.left_panel.setMaximumWidth(400)
        
        # Center panel - Video display (80% of space)
        self.center_panel = self.create_center_panel()
        
        # Right panel - Settings (collapsible, 20% when expanded)
        self.right_panel = self.create_right_panel()
        
        # Add panels to splitter
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.center_panel)
        self.main_splitter.addWidget(self.right_panel)
        
        # Set initial splitter sizes (20% - 60% - 20%)
        self.main_splitter.setSizes([300, 800, 300])
        
        main_layout.addWidget(self.main_splitter)
        self.setLayout(main_layout)
        
    def create_center_panel(self):
        """Create the center panel with video display"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Video display (80%+ of center panel)
        self.video_display = QModernVideoDisplay()
        layout.addWidget(self.video_display, 1)  # Takes all available space
        
        # Bottom toolbar (minimal)
        toolbar = self.create_bottom_toolbar()
        layout.addWidget(toolbar)
        
        panel.setLayout(layout)
        return panel
        
    def create_bottom_toolbar(self):
        """Create minimal bottom toolbar"""
        toolbar = QWidget()
        toolbar.setObjectName("bottom-toolbar")
        toolbar.setMaximumHeight(40)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status-label")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("progress-bar")
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.progress_bar)
        
        toolbar.setLayout(layout)
        return toolbar
        
    def create_right_panel(self):
        """Create collapsible right panel for settings"""
        panel = QWidget()
        panel.setObjectName("right-panel")
        panel.setMinimumWidth(250)
        panel.setMaximumWidth(350)
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Collapsible sections
        self.create_collapsible_sections(layout)
        
        panel.setLayout(layout)
        return panel
        
    def create_collapsible_sections(self, layout):
        """Create collapsible settings sections"""
        # Input Detection
        input_section = self.create_collapsible_group("Input Detection", [
            ("Camera Source", QComboBox()),
            ("File Source", QLineEdit()),
            ("Detection Threshold", QSlider(Qt.Horizontal))
        ])
        layout.addWidget(input_section)
        
        # Face Processing
        face_section = self.create_collapsible_group("Face Processing", [
            ("Face Detection", QCheckBox()),
            ("Face Alignment", QCheckBox()),
            ("Face Swap Model", QComboBox()),
            ("Quality", QSlider(Qt.Horizontal))
        ])
        layout.addWidget(face_section)
        
        # Output Settings
        output_section = self.create_collapsible_group("Output Settings", [
            ("Stream Quality", QComboBox()),
            ("Recording Format", QComboBox()),
            ("Output Path", QLineEdit())
        ])
        layout.addWidget(output_section)
        
        # Performance
        performance_section = self.create_collapsible_group("Performance", [
            ("Target FPS", QSpinBox()),
            ("Memory Limit", QSpinBox()),
            ("GPU Acceleration", QCheckBox())
        ])
        layout.addWidget(performance_section)
        
        layout.addStretch()
        
    def create_collapsible_group(self, title, controls):
        """Create a collapsible group with controls"""
        group = QGroupBox(title)
        group.setObjectName("collapsible-group")
        group.setCheckable(True)
        group.setChecked(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        for label_text, control in controls:
            if label_text:
                label = QLabel(label_text)
                label.setObjectName("control-label")
                layout.addWidget(label)
            layout.addWidget(control)
            
        group.setLayout(layout)
        return group
        
    def setup_styles(self):
        """Setup comprehensive modern styling"""
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 13px;
            }
            
            QSplitter::handle {
                background-color: #404040;
                width: 2px;
            }
            
            QSplitter::handle:hover {
                background-color: #606060;
            }
            
            QWidget#right-panel {
                background-color: #2a2a2a;
                border-left: 1px solid #404040;
            }
            
            QWidget#bottom-toolbar {
                background-color: #2a2a2a;
                border-top: 1px solid #404040;
            }
            
            QLabel#status-label {
                color: #b0b0b0;
                font-size: 12px;
            }
            
            QProgressBar#progress-bar {
                border: 1px solid #404040;
                border-radius: 4px;
                text-align: center;
                background-color: #1e1e1e;
            }
            
            QProgressBar#progress-bar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
            
            QGroupBox#collapsible-group {
                font-weight: 600;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 1ex;
                padding-top: 12px;
                background-color: #2a2a2a;
            }
            
            QGroupBox#collapsible-group::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px 0 6px;
                color: #ffffff;
            }
            
            QLabel#control-label {
                color: #b0b0b0;
                font-size: 12px;
                font-weight: 500;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #404040;
                height: 6px;
                background-color: #1e1e1e;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background-color: #2196F3;
                border: 1px solid #1976D2;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            
            QSlider::handle:horizontal:hover {
                background-color: #1976D2;
            }
        """)
        
    def setup_connections(self):
        """Setup signal connections"""
        # Connect control panel buttons
        if hasattr(self.left_panel, 'stream_btn'):
            self.left_panel.stream_btn.clicked.connect(self.on_stream_toggle)
        if hasattr(self.left_panel, 'record_btn'):
            self.left_panel.record_btn.clicked.connect(self.on_record_toggle)
        if hasattr(self.left_panel, 'face_swap_btn'):
            self.left_panel.face_swap_btn.toggled.connect(self.on_face_swap_toggle)
            
    def setup_animations(self):
        """Setup smooth animations and transitions"""
        # Animation for panel transitions
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def setup_accessibility(self):
        """Setup accessibility features"""
        # Set accessible names and descriptions
        self.setAccessibleName("PlayaTews Identity Masker Main Interface")
        self.setAccessibleDescription("Professional face-swapping and streaming application")
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for accessibility"""
        # F11 for fullscreen
        fullscreen_action = QAction("Toggle Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.video_display.toggle_fullscreen)
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
        
    def on_stream_toggle(self):
        """Handle streaming toggle"""
        # Implementation for streaming toggle
        pass
        
    def on_record_toggle(self):
        """Handle recording toggle"""
        # Implementation for recording toggle
        pass
        
    def on_face_swap_toggle(self, enabled):
        """Handle face swap toggle"""
        # Implementation for face swap toggle
        pass
        
    def update_video_frame(self, frame):
        """Update the video display"""
        self.video_display.update_video_frame(frame)
        
    def show_status_message(self, message, duration=3000):
        """Show a status message"""
        self.status_label.setText(message)
        # Auto-clear after duration
        QTimer.singleShot(duration, lambda: self.status_label.setText("Ready"))
        
    def show_progress(self, visible=True, value=0):
        """Show/hide progress bar"""
        self.progress_bar.setVisible(visible)
        if visible:
            self.progress_bar.setValue(value)
            
    def resizeEvent(self, event):
        """Handle responsive resizing"""
        super().resizeEvent(event)
        # Adjust splitter sizes based on window size
        width = self.width()
        if width > 1200:
            # Large screen: 20% - 60% - 20%
            self.main_splitter.setSizes([width * 0.2, width * 0.6, width * 0.2])
        elif width > 800:
            # Medium screen: 25% - 50% - 25%
            self.main_splitter.setSizes([width * 0.25, width * 0.5, width * 0.25])
        else:
            # Small screen: 30% - 40% - 30%
            self.main_splitter.setSizes([width * 0.3, width * 0.4, width * 0.3]) 