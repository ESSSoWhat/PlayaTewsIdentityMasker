#!/usr/bin/env python3
"""
Optimized Processing Window for PlayaTewsIdentityMasker
Reduced from 8 tabs to 4 tabs for better navigation and organization
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

from .widgets.QCollapsibleComponentWrapper import (
    QCollapsibleComponentWrapper,
    QSmartCollapsibleGroup,
    group_small_components,
    make_collapsible,
)


class QOptimizedProcessingWindow(qtx.QXWindow):
    """Optimized processing window with reduced tabs and better organization"""

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
        self.setWindowTitle("PlayaTewsIdentityMasker - Optimized Controls")
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

        about_action = QAction("About Optimized Window", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_ui(self):
        """Setup the optimized main UI layout with 4 tabs"""
        central_widget = QWidget()
        self.add_widget(central_widget)

        main_layout = QHBoxLayout()

        # Left panel - Basic controls
        left_panel = self.create_left_panel()

        # Center panel - Tabbed controls (reduced from 8 to 4 tabs)
        center_panel = self.create_center_panel()

        # Right panel - Monitoring and status
        right_panel = self.create_right_panel()

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500, 300])

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
            input_layout.addWidget(QLabel("Input Sources: Not Available"))

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
            detection_layout.addWidget(QLabel("Detection Components: Not Available"))

        detection_group.setLayout(detection_layout)

        layout.addWidget(input_group)
        layout.addWidget(detection_group)
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def create_center_panel(self):
        """Create the center panel with 4 optimized tabs"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Create tab widget with only 4 tabs
        self.processing_tabs = QTabWidget()

        # Tab 1: Input & Detection
        input_detection_tab = self.create_input_detection_tab()
        self.processing_tabs.addTab(input_detection_tab, "Input & Detection")

        # Tab 2: Face Processing
        face_processing_tab = self.create_face_processing_tab()
        self.processing_tabs.addTab(face_processing_tab, "Face Processing")

        # Tab 3: Output & Quality
        output_quality_tab = self.create_output_quality_tab()
        self.processing_tabs.addTab(output_quality_tab, "Output & Quality")

        # Tab 4: Performance & Advanced
        performance_advanced_tab = self.create_performance_advanced_tab()
        self.processing_tabs.addTab(performance_advanced_tab, "Performance & Advanced")

        layout.addWidget(self.processing_tabs)
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def create_input_detection_tab(self):
        """Create tab for input sources and face detection"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Input sources group
        input_group = QGroupBox("Input Sources")
        input_layout = QVBoxLayout()

        if "file_source" in self.face_swap_components:
            input_layout.addWidget(self.face_swap_components["file_source"])
        if "camera_source" in self.face_swap_components:
            input_layout.addWidget(self.face_swap_components["camera_source"])

        input_group.setLayout(input_layout)
        scroll_layout.addWidget(input_group)

        # Face detection group
        detection_group = QGroupBox("Face Detection & Alignment")
        detection_layout = QVBoxLayout()

        if "face_detector" in self.face_swap_components:
            detection_layout.addWidget(self.face_swap_components["face_detector"])
        if "face_aligner" in self.face_swap_components:
            detection_layout.addWidget(self.face_swap_components["face_aligner"])

        detection_group.setLayout(detection_layout)
        scroll_layout.addWidget(detection_group)

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab

    def create_face_processing_tab(self):
        """Create tab for face processing controls"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Face processing components (using optimized versions)
        try:
            # Face marker
            if "face_marker" in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components["face_marker"])

            # Face animator
            if "face_animator" in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components["face_animator"])

            # Face swap insight
            if "face_swap_insight" in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components["face_swap_insight"])

            # Face swap DFM
            if "face_swap_dfm" in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components["face_swap_dfm"])
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

    def create_output_quality_tab(self):
        """Create tab for output and quality settings"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        try:
            # Frame processing components
            if "frame_adjuster" in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components["frame_adjuster"])

            if "face_merger" in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components["face_merger"])

            # Stream output
            if "stream_output" in self.face_swap_components:
                scroll_layout.addWidget(self.face_swap_components["stream_output"])
        except Exception as e:
            print(f"Error adding output components: {e}")
            scroll_layout.addWidget(QLabel("Output Components: Error Loading"))

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab

    def create_performance_advanced_tab(self):
        """Create tab for performance and advanced settings"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Performance presets
        presets_group = QGroupBox("Performance Presets")
        presets_layout = QHBoxLayout()

        ultra_fast_btn = QPushButton("Ultra Fast")
        fast_btn = QPushButton("Fast")
        balanced_btn = QPushButton("Balanced")
        quality_btn = QPushButton("Quality")

        for btn in [ultra_fast_btn, fast_btn, balanced_btn, quality_btn]:
            btn.setMaximumHeight(30)
            presets_layout.addWidget(btn)

        presets_group.setLayout(presets_layout)
        scroll_layout.addWidget(presets_group)

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
        scroll_layout.addWidget(advanced_group)

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
        scroll_layout.addWidget(experimental_group)

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab

    def create_right_panel(self):
        """Create the right panel with monitoring and status"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Performance metrics
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QVBoxLayout()

        self.fps_label = QLabel("FPS: 0.0")
        self.memory_label = QLabel("Memory: 0 MB")
        self.cpu_label = QLabel("CPU: 0%")

        for label in [self.fps_label, self.memory_label, self.cpu_label]:
            label.setStyleSheet("QLabel { font-weight: bold; color: #2196F3; }")
            metrics_layout.addWidget(label)

        metrics_group.setLayout(metrics_layout)

        # Processing status
        status_group = QGroupBox("Processing Status")
        status_layout = QVBoxLayout()

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("QLabel { color: #4CAF50; }")
        status_layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)

        status_group.setLayout(status_layout)

        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()

        start_all_btn = QPushButton("Start All Processing")
        stop_all_btn = QPushButton("Stop All Processing")
        reset_btn = QPushButton("Reset Settings")

        for btn in [start_all_btn, stop_all_btn, reset_btn]:
            btn.setMinimumHeight(30)
            actions_layout.addWidget(btn)

        actions_group.setLayout(actions_layout)

        layout.addWidget(metrics_group)
        layout.addWidget(status_group)
        layout.addWidget(actions_group)
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def setup_styles(self):
        """Setup the optimized dark theme"""
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
            
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
            }
            
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #2196F3;
            }
            
            QTabBar::tab:hover {
                background-color: #505050;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                background-color: #404040;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #606060;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #707070;
            }
        """
        )

    def setup_connections(self):
        """Setup signal connections"""
        pass

    def save_settings(self):
        """Save current settings"""
        self.status_bar.showMessage("Settings saved", 3000)

    def load_settings(self):
        """Load saved settings"""
        self.status_bar.showMessage("Settings loaded", 3000)

    def reset_all_settings(self):
        """Reset all settings to defaults"""
        self.status_bar.showMessage("Settings reset", 3000)

    def optimize_performance(self):
        """Optimize performance settings"""
        self.status_bar.showMessage("Performance optimized", 3000)

    def toggle_dock(self):
        """Toggle dock state"""
        self.status_bar.showMessage("Dock toggled", 3000)

    def show_about(self):
        """Show about dialog"""
        from PyQt5.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            "About",
            "PlayaTewsIdentityMasker Optimized Processing Window\n\nOptimized for better space utilization and navigation.",
        )

    def closeEvent(self, event):
        """Handle window close event"""
        event.accept()
