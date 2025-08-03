#!/usr/bin/env python3
"""
Enhanced Main UI for PlayaTewsIdentityMasker
Integrates optimized video display and modern control panel with comprehensive UI/UX improvements
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon, QImage, QPalette, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
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
    QMainWindow,
    QMenu,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QStyleFactory,
    QTabWidget,
    QTextEdit,
    QToolBar,
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
from .QModernControlPanel import QModernControlPanel
from .QOptimizedVideoDisplay import QOptimizedVideoDisplay


class QEnhancedMainUI(QMainWindow):
    """Enhanced main UI with comprehensive UI/UX improvements"""

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
        self.original_geometry = None
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance_metrics)
        self.performance_timer.start(1000)  # Update every second

        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.setup_accessibility()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_toolbar()

    def setup_ui(self):
        """Setup the enhanced main UI layout"""
        # Set window properties
        self.setWindowTitle("PlayaTews Identity Masker - Enhanced")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Create central widget with responsive layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout with splitter for responsive design
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.main_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Modern control panel (20% of space)
        self.left_panel = QModernControlPanel()
        self.left_panel.setMinimumWidth(280)
        self.left_panel.setMaximumWidth(400)

        # Center panel - Optimized video display (60% of space)
        self.center_panel = self.create_enhanced_center_panel()

        # Right panel - Settings and viewers (20% of space)
        self.right_panel = self.create_enhanced_right_panel()
        self.right_panel.setMinimumWidth(250)
        self.right_panel.setMaximumWidth(350)

        # Add panels to splitter with optimized proportions
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.center_panel)
        self.main_splitter.addWidget(self.right_panel)

        # Set initial splitter sizes (20% - 60% - 20%)
        self.main_splitter.setSizes([300, 800, 300])

        main_layout.addWidget(self.main_splitter)
        central_widget.setLayout(main_layout)

    def create_enhanced_center_panel(self):
        """Create enhanced center panel with optimized video display"""
        panel = QWidget()
        panel.setObjectName("center-panel")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Video display area (90% of center panel)
        self.video_display = QOptimizedVideoDisplay()
        layout.addWidget(self.video_display, 1)  # Takes 90% of space

        # Bottom toolbar (10% of center panel)
        toolbar = self.create_enhanced_toolbar()
        layout.addWidget(toolbar)

        panel.setLayout(layout)
        return panel

    def create_enhanced_toolbar(self):
        """Create enhanced bottom toolbar with status and controls"""
        toolbar = QWidget()
        toolbar.setObjectName("enhanced-toolbar")
        toolbar.setMaximumHeight(40)

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(12)

        # Status indicators
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status-label")

        # Performance indicators
        self.fps_indicator = QLabel("FPS: 30")
        self.fps_indicator.setObjectName("performance-indicator")

        self.memory_indicator = QLabel("Memory: 2.1 GB")
        self.memory_indicator.setObjectName("performance-indicator")

        self.cpu_indicator = QLabel("CPU: 45%")
        self.cpu_indicator.setObjectName("performance-indicator")

        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("enhanced-progress")
        self.progress_bar.setMaximumWidth(200)

        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.fps_indicator)
        layout.addWidget(self.memory_indicator)
        layout.addWidget(self.cpu_indicator)
        layout.addWidget(self.progress_bar)

        toolbar.setLayout(layout)
        return toolbar

    def create_enhanced_right_panel(self):
        """Create enhanced right panel with collapsible sections"""
        panel = QWidget()
        panel.setObjectName("right-panel")

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Create collapsible sections
        self.create_collapsible_sections(layout)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def create_collapsible_sections(self, layout):
        """Create collapsible settings and viewer sections"""
        # Input Settings
        input_group = self.create_collapsible_group(
            "Input Settings",
            [
                ("Camera Source", QComboBox, ["Camera 1", "Camera 2", "File Source"]),
                ("File Path", QLineEdit, ""),
                ("Detection Threshold", QSlider, (0, 100, 50)),
            ],
        )
        layout.addWidget(input_group)

        # Face Processing Settings
        face_group = self.create_collapsible_group(
            "Face Processing",
            [
                ("Face Detection", QCheckBox, True),
                ("Face Alignment", QCheckBox, True),
                ("Face Swap Model", QComboBox, ["Model 1", "Model 2", "Custom Model"]),
                ("Quality Level", QComboBox, ["Low", "Medium", "High", "Ultra"]),
            ],
        )
        layout.addWidget(face_group)

        # Output Settings
        output_group = self.create_collapsible_group(
            "Output Settings",
            [
                ("Stream Quality", QComboBox, ["720p", "1080p", "1440p", "4K"]),
                ("Recording Format", QComboBox, ["MP4", "AVI", "MOV"]),
                ("Output Path", QLineEdit, ""),
                ("Auto Record", QCheckBox, False),
            ],
        )
        layout.addWidget(output_group)

        # Performance Settings
        performance_group = self.create_collapsible_group(
            "Performance",
            [
                ("Target FPS", QSpinBox, (15, 60, 30)),
                ("Memory Limit (GB)", QSpinBox, (1, 16, 4)),
                ("GPU Acceleration", QCheckBox, True),
                ("Optimize for Speed", QCheckBox, False),
            ],
        )
        layout.addWidget(performance_group)

        # Voice Settings
        if self.voice_changer_backend:
            voice_group = self.create_collapsible_group(
                "Voice Settings",
                [
                    ("Voice Changer", QCheckBox, False),
                    (
                        "Effect Type",
                        QComboBox,
                        ["None", "Echo", "Pitch", "Reverb", "Robot"],
                    ),
                    ("Pitch Shift", QSlider, (-12, 12, 0)),
                    ("Echo Level", QSlider, (0, 100, 0)),
                ],
            )
            layout.addWidget(voice_group)

    def create_collapsible_group(self, title, controls):
        """Create a collapsible group with controls"""
        group = QGroupBox(title)
        group.setObjectName("collapsible-group")
        group.setCheckable(True)
        group.setChecked(False)  # Start collapsed

        layout = QVBoxLayout()
        layout.setSpacing(8)

        for label_text, control_type, default_value in controls:
            # Create label
            label = QLabel(label_text)
            label.setObjectName("control-label")
            layout.addWidget(label)

            # Create control
            if control_type == QComboBox:
                control = QComboBox()
                if isinstance(default_value, list):
                    control.addItems(default_value)
                control.setObjectName(f"{label_text.lower().replace(' ', '-')}-combo")
            elif control_type == QLineEdit:
                control = QLineEdit()
                control.setText(str(default_value))
                control.setObjectName(f"{label_text.lower().replace(' ', '-')}-edit")
            elif control_type == QSlider:
                control = QSlider(Qt.Horizontal)
                min_val, max_val, default_val = default_value
                control.setRange(min_val, max_val)
                control.setValue(default_val)
                control.setObjectName(f"{label_text.lower().replace(' ', '-')}-slider")
            elif control_type == QSpinBox:
                control = QSpinBox()
                min_val, max_val, default_val = default_value
                control.setRange(min_val, max_val)
                control.setValue(default_val)
                control.setObjectName(f"{label_text.lower().replace(' ', '-')}-spin")
            elif control_type == QCheckBox:
                control = QCheckBox()
                control.setChecked(default_value)
                control.setObjectName(f"{label_text.lower().replace(' ', '-')}-check")

            layout.addWidget(control)

        group.setLayout(layout)
        return group

    def setup_styles(self):
        """Setup comprehensive modern styling"""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 12px;
            }
            
            QSplitter::handle {
                background-color: #404040;
                width: 2px;
            }
            
            QSplitter::handle:hover {
                background-color: #606060;
            }
            
            QWidget#center-panel {
                background-color: #0a0a0a;
                border: none;
            }
            
            QWidget#right-panel {
                background-color: #2a2a2a;
                border-left: 1px solid #404040;
            }
            
            QWidget#enhanced-toolbar {
                background-color: #2a2a2a;
                border-top: 1px solid #404040;
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
            
            QGroupBox#collapsible-group {
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 1ex;
                padding-top: 12px;
                background-color: #2a2a2a;
            }
            
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            
            QLabel#control-label {
                color: #b0b0b0;
                font-size: 11px;
                font-weight: 500;
                margin-top: 4px;
            }
            
            QLabel#status-label {
                color: #ffffff;
                font-weight: 500;
                font-size: 12px;
            }
            
            QLabel#performance-indicator {
                color: #00ff00;
                font-weight: 600;
                font-size: 11px;
                padding: 2px 6px;
                background-color: rgba(0, 255, 0, 0.1);
                border-radius: 3px;
            }
            
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
                font-size: 11px;
                min-height: 20px;
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
            
            QComboBox QAbstractItemView {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                selection-background-color: #2196F3;
                color: #ffffff;
            }
            
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
                font-size: 11px;
                min-height: 20px;
            }
            
            QLineEdit:focus {
                border-color: #2196F3;
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
            
            QSpinBox {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
                font-size: 11px;
                min-height: 20px;
            }
            
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #404040;
                border: none;
                width: 16px;
            }
            
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #606060;
            }
            
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
                font-size: 11px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #404040;
                border-radius: 3px;
                background-color: #1e1e1e;
            }
            
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #2196F3;
            }
            
            QCheckBox::indicator:hover {
                border-color: #606060;
            }
            
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 4px;
                text-align: center;
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 10px;
            }
            
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
            
            QMenuBar {
                background-color: #2a2a2a;
                color: #ffffff;
                border-bottom: 1px solid #404040;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
            }
            
            QMenuBar::item:selected {
                background-color: #404040;
            }
            
            QMenu {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                color: #ffffff;
            }
            
            QMenu::item {
                padding: 6px 20px;
            }
            
            QMenu::item:selected {
                background-color: #404040;
            }
            
            QStatusBar {
                background-color: #2a2a2a;
                color: #ffffff;
                border-top: 1px solid #404040;
            }
            
            QToolBar {
                background-color: #2a2a2a;
                border-bottom: 1px solid #404040;
                spacing: 4px;
                padding: 4px;
            }
            
            QToolButton {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
                min-width: 24px;
                min-height: 24px;
            }
            
            QToolButton:hover {
                background-color: #606060;
            }
            
            QToolButton:pressed {
                background-color: #505050;
            }
        """
        )

    def setup_connections(self):
        """Setup signal connections"""
        # Connect control panel signals
        if hasattr(self.left_panel, "stream_btn"):
            self.left_panel.stream_btn.clicked.connect(self.on_stream_toggle)
        if hasattr(self.left_panel, "record_btn"):
            self.left_panel.record_btn.clicked.connect(self.on_record_toggle)
        if hasattr(self.left_panel, "face_swap_btn"):
            self.left_panel.face_swap_btn.toggled.connect(self.on_face_swap_toggle)
        if hasattr(self.left_panel, "settings_btn"):
            self.left_panel.settings_btn.clicked.connect(self.open_settings_window)

        # Connect video display signals
        if hasattr(self.video_display, "fullscreen_btn"):
            self.video_display.fullscreen_btn.clicked.connect(self.toggle_fullscreen)

    def setup_accessibility(self):
        """Setup accessibility features"""
        # Set accessible names and descriptions
        self.setAccessibleName("PlayaTews Identity Masker Enhanced")
        self.setAccessibleDescription(
            "Professional face-swapping and streaming application with enhanced UI"
        )

        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()

    def setup_keyboard_shortcuts(self):
        """Setup comprehensive keyboard shortcuts"""
        # Fullscreen
        fullscreen_action = QAction("Toggle Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.addAction(fullscreen_action)

        # Streaming
        stream_action = QAction("Toggle Streaming", self)
        stream_action.setShortcut("Ctrl+S")
        stream_action.triggered.connect(self.on_stream_toggle)
        self.addAction(stream_action)

        # Recording
        record_action = QAction("Toggle Recording", self)
        record_action.setShortcut("Ctrl+R")
        record_action.triggered.connect(self.on_record_toggle)
        self.addAction(record_action)

        # Face Swap
        face_swap_action = QAction("Toggle Face Swap", self)
        face_swap_action.setShortcut("Ctrl+F")
        face_swap_action.triggered.connect(self.on_face_swap_toggle)
        self.addAction(face_swap_action)

        # Settings
        settings_action = QAction("Open Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings_window)
        self.addAction(settings_action)

        # Help
        help_action = QAction("Show Help", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        self.addAction(help_action)

    def setup_menu_bar(self):
        """Setup enhanced menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)

        open_action = QAction("Open Project", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("View")

        fullscreen_action = QAction("Toggle Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings_window)
        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        help_action = QAction("User Guide", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        """Setup enhanced status bar"""
        self.statusBar().showMessage("Ready")

    def setup_toolbar(self):
        """Setup enhanced toolbar"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setObjectName("main-toolbar")

        # Add toolbar actions
        stream_action = QAction("Stream", self)
        stream_action.setIcon(self.style().standardIcon(QStyleFactory.SP_MediaPlay))
        stream_action.triggered.connect(self.on_stream_toggle)
        toolbar.addAction(stream_action)

        record_action = QAction("Record", self)
        record_action.setIcon(self.style().standardIcon(QStyleFactory.SP_MediaRecord))
        record_action.triggered.connect(self.on_record_toggle)
        toolbar.addAction(record_action)

        toolbar.addSeparator()

        settings_action = QAction("Settings", self)
        settings_action.setIcon(
            self.style().standardIcon(QStyleFactory.SP_FileDialogDetailedView)
        )
        settings_action.triggered.connect(self.open_settings_window)
        toolbar.addAction(settings_action)

    def on_stream_toggle(self):
        """Handle streaming toggle"""
        if hasattr(self.left_panel, "stream_btn"):
            if self.left_panel.stream_btn.text() == "Start Streaming":
                self.left_panel.stream_btn.setText("Stop Streaming")
                self.show_status_message("Streaming started")
                self.show_progress(True, 0)
            else:
                self.left_panel.stream_btn.setText("Start Streaming")
                self.show_status_message("Streaming stopped")
                self.show_progress(False)

    def on_record_toggle(self):
        """Handle recording toggle"""
        if hasattr(self.left_panel, "record_btn"):
            if self.left_panel.record_btn.text() == "Start Recording":
                self.left_panel.record_btn.setText("Stop Recording")
                self.show_status_message("Recording started")
            else:
                self.left_panel.record_btn.setText("Start Recording")
                self.show_status_message("Recording stopped")

    def on_face_swap_toggle(self, enabled=None):
        """Handle face swap toggle"""
        if hasattr(self.left_panel, "face_swap_btn"):
            if enabled is None:
                enabled = self.left_panel.face_swap_btn.isChecked()

            if enabled:
                self.left_panel.face_swap_btn.setText("Face Swap: ON")
                self.show_status_message("Face swap enabled")
            else:
                self.left_panel.face_swap_btn.setText("Face Swap: OFF")
                self.show_status_message("Face swap disabled")

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
        if self.original_geometry:
            self.setGeometry(self.original_geometry)

    def update_video_frame(self, frame):
        """Update the video display with a new frame"""
        if hasattr(self, "video_display"):
            self.video_display.update_video_frame(frame)

    def update_performance_metrics(self):
        """Update performance metrics display"""
        # Simulate performance metrics (replace with actual implementation)
        import random

        fps = random.randint(25, 35)
        memory = random.uniform(1.5, 3.0)
        cpu = random.randint(30, 70)

        if hasattr(self, "fps_indicator"):
            self.fps_indicator.setText(f"FPS: {fps}")
        if hasattr(self, "memory_indicator"):
            self.memory_indicator.setText(f"Memory: {memory:.1f} GB")
        if hasattr(self, "cpu_indicator"):
            self.cpu_indicator.setText(f"CPU: {cpu}%")

        # Update video display metrics
        if hasattr(self, "video_display"):
            self.video_display.update_performance_metrics(fps, "HD")

    def show_status_message(self, message, duration=3000):
        """Show a status message"""
        self.statusBar().showMessage(message, duration)
        if hasattr(self, "status_label"):
            self.status_label.setText(message)

    def show_progress(self, visible=True, value=0):
        """Show/hide progress bar"""
        if hasattr(self, "progress_bar"):
            self.progress_bar.setVisible(visible)
            if visible:
                self.progress_bar.setValue(value)

    def open_settings_window(self):
        """Open settings window"""
        # Implementation for settings window
        self.show_status_message("Settings window opened")

    def show_help(self):
        """Show help documentation"""
        # Implementation for help system
        self.show_status_message("Help documentation opened")

    def show_about(self):
        """Show about dialog"""
        # Implementation for about dialog
        self.show_status_message("About dialog opened")

    def resizeEvent(self, event):
        """Handle responsive resizing"""
        super().resizeEvent(event)
        # Adjust splitter sizes based on window size
        width = self.width()
        if width > 1400:
            # Large screen: 20% - 60% - 20%
            self.main_splitter.setSizes([width * 0.2, width * 0.6, width * 0.2])
        elif width > 1000:
            # Medium screen: 25% - 50% - 25%
            self.main_splitter.setSizes([width * 0.25, width * 0.5, width * 0.25])
        else:
            # Small screen: 30% - 40% - 30%
            self.main_splitter.setSizes([width * 0.3, width * 0.4, width * 0.3])

    def keyPressEvent(self, event):
        """Handle keyboard events"""
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape and self.is_fullscreen:
            self.exit_fullscreen()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle application close"""
        # Cleanup and save settings
        self.performance_timer.stop()
        event.accept()
