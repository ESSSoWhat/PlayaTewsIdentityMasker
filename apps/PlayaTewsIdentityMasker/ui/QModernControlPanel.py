#!/usr/bin/env python3
"""
Modern Control Panel Component
Implements responsive design, consistent patterns, and improved accessibility
"""

from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QPushButton, QLabel, QComboBox, QSpinBox, QLineEdit,
                            QCheckBox, QGroupBox, QTabWidget, QListWidget, QListWidgetItem,
                            QSlider, QFrame, QProgressBar, QSizePolicy,
                            QToolButton, QMenu, QAction, QApplication, QStyleFactory)


class QModernControlPanel(QWidget):
    """Modern control panel with improved layout and accessibility"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()
        self.setup_animations()
        self.setup_accessibility()
        
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
        """Create main control buttons with modern design"""
        controls_group = QGroupBox("Main Controls")
        controls_group.setObjectName("main-controls-group")
        controls_layout = QGridLayout()
        controls_layout.setSpacing(12)
        
        # Streaming controls
        self.stream_btn = self.create_modern_button("Start Streaming", "#e74c3c", "stream-btn")
        self.record_btn = self.create_modern_button("Start Recording", "#e67e22", "record-btn")
        
        # Face swap controls
        self.face_swap_btn = self.create_modern_button("Face Swap: ON", "#27ae60", "face-swap-btn")
        self.face_swap_btn.setCheckable(True)
        self.face_swap_btn.setChecked(True)
        
        # Settings button
        self.settings_btn = self.create_modern_button("Settings", "#3498db", "settings-btn")
        
        # Layout buttons in responsive grid
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
        sources_tab = self.create_sources_tab()
        self.tab_widget.addTab(sources_tab, "Sources")
        
        # Models tab
        models_tab = self.create_models_tab()
        self.tab_widget.addTab(models_tab, "Models")
        
        # Voice tab
        voice_tab = self.create_voice_tab()
        self.tab_widget.addTab(voice_tab, "Voice")
        
        layout.addWidget(self.tab_widget)
        
    def create_sources_tab(self):
        """Create sources management tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Sources list
        self.sources_list = QListWidget()
        self.sources_list.setMaximumHeight(120)
        self.sources_list.setObjectName("sources-list")
        
        # Add some sample sources
        sample_sources = ["Camera 1", "Camera 2", "Video File", "Image Sequence"]
        for source in sample_sources:
            item = QListWidgetItem(source)
            self.sources_list.addItem(item)
            
        # Source controls
        source_controls = QHBoxLayout()
        add_source_btn = self.create_modern_button("+", "#27ae60", "add-btn")
        add_source_btn.setMaximumWidth(40)
        remove_source_btn = self.create_modern_button("-", "#e74c3c", "remove-btn")
        remove_source_btn.setMaximumWidth(40)
        
        source_controls.addWidget(add_source_btn)
        source_controls.addWidget(remove_source_btn)
        source_controls.addStretch()
        
        layout.addWidget(self.sources_list)
        layout.addLayout(source_controls)
        tab.setLayout(layout)
        return tab
        
    def create_models_tab(self):
        """Create models management tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Models list
        self.models_list = QListWidget()
        self.models_list.setMaximumHeight(120)
        self.models_list.setObjectName("models-list")
        
        # Add some sample models
        sample_models = ["Model 1", "Model 2", "Model 3", "Custom Model"]
        for model in sample_models:
            item = QListWidgetItem(model)
            self.models_list.addItem(item)
            
        # Model controls
        model_controls = QHBoxLayout()
        load_model_btn = self.create_modern_button("Load", "#3498db", "load-btn")
        refresh_btn = self.create_modern_button("Refresh", "#f39c12", "refresh-btn")
        
        model_controls.addWidget(load_model_btn)
        model_controls.addWidget(refresh_btn)
        model_controls.addStretch()
        
        layout.addWidget(self.models_list)
        layout.addLayout(model_controls)
        tab.setLayout(layout)
        return tab
        
    def create_voice_tab(self):
        """Create voice changer tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Voice controls
        self.voice_enabled = QCheckBox("Voice Changer")
        self.voice_enabled.setObjectName("voice-enabled")
        
        self.voice_effect = QComboBox()
        self.voice_effect.addItems(["None", "Echo", "Pitch", "Reverb", "Robot"])
        self.voice_effect.setObjectName("voice-effect")
        
        # Voice sliders
        pitch_layout = QHBoxLayout()
        pitch_layout.addWidget(QLabel("Pitch:"))
        self.pitch_slider = QSlider(Qt.Horizontal)
        self.pitch_slider.setRange(-12, 12)
        self.pitch_slider.setValue(0)
        self.pitch_slider.setObjectName("pitch-slider")
        pitch_layout.addWidget(self.pitch_slider)
        
        echo_layout = QHBoxLayout()
        echo_layout.addWidget(QLabel("Echo:"))
        self.echo_slider = QSlider(Qt.Horizontal)
        self.echo_slider.setRange(0, 100)
        self.echo_slider.setValue(0)
        self.echo_slider.setObjectName("echo-slider")
        echo_layout.addWidget(self.echo_slider)
        
        layout.addWidget(self.voice_enabled)
        layout.addWidget(QLabel("Effect:"))
        layout.addWidget(self.voice_effect)
        layout.addLayout(pitch_layout)
        layout.addLayout(echo_layout)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_status_indicators(self, layout):
        """Create status indicators with modern design"""
        status_group = QGroupBox("Status")
        status_group.setObjectName("status-group")
        status_layout = QVBoxLayout()
        status_layout.setSpacing(8)
        
        # Performance indicators
        self.fps_label = QLabel("FPS: 30")
        self.memory_label = QLabel("Memory: 2.1 GB")
        self.cpu_label = QLabel("CPU: 45%")
        
        for label in [self.fps_label, self.memory_label, self.cpu_label]:
            label.setObjectName("status-label")
            status_layout.addWidget(label)
            
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("status-progress")
        status_layout.addWidget(self.progress_bar)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
    def create_modern_button(self, text, color, object_name):
        """Create a modern styled button with hover effects"""
        btn = QPushButton(text)
        btn.setObjectName(object_name)
        btn.setMinimumHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        
        # Set accessible name for screen readers
        btn.setAccessibleName(text)
        
        # Apply modern styling
        btn.setStyleSheet(f"""
            QPushButton#{object_name} {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                padding: 8px 16px;
                min-height: 40px;
            }}
            QPushButton#{object_name}:hover {{
                background-color: {self.darken_color(color)};
                transform: translateY(-1px);
            }}
            QPushButton#{object_name}:pressed {{
                background-color: {self.darken_color(color, 0.3)};
                transform: translateY(0px);
            }}
            QPushButton#{object_name}:disabled {{
                background-color: #666666;
                color: #999999;
            }}
        """)
        return btn
        
    def darken_color(self, color, factor=0.2):
        """Darken a hex color for hover effects"""
        # Simple color darkening - in production, use proper color manipulation
        if color.startswith('#'):
            # Convert hex to RGB, darken, then back to hex
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
        
    def setup_styles(self):
        """Setup comprehensive modern styling"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 16px;
                background-color: #2a2a2a;
                color: #ffffff;
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
                font-weight: 500;
            }
            
            QTabBar::tab:selected {
                background-color: #2196F3;
            }
            
            QTabBar::tab:hover {
                background-color: #505050;
            }
            
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #ffffff;
                font-size: 12px;
            }
            
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #303030;
            }
            
            QListWidget::item:selected {
                background-color: #2196F3;
            }
            
            QListWidget::item:hover {
                background-color: #404040;
            }
            
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
                font-size: 13px;
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
            
            QCheckBox::indicator:hover {
                border-color: #606060;
            }
            
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px 12px;
                color: #ffffff;
                min-height: 20px;
                font-size: 12px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid white;
            }
            
            QComboBox QAbstractItemView {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                selection-background-color: #2196F3;
                color: #ffffff;
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
            
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            
            QLabel#status-label {
                color: #b0b0b0;
                font-size: 12px;
                padding: 4px 0;
            }
            
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 4px;
                text-align: center;
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        
    def setup_animations(self):
        """Setup smooth animations for UI elements"""
        # Button hover animations
        self.button_animations = {}
        
    def setup_accessibility(self):
        """Setup accessibility features"""
        # Set accessible names and descriptions
        self.setAccessibleName("Control Panel")
        self.setAccessibleDescription("Main control panel for face swapping and streaming")
        
        # Setup keyboard navigation
        self.setup_keyboard_navigation()
        
    def setup_keyboard_navigation(self):
        """Setup keyboard navigation for accessibility"""
        # Tab order setup
        self.setTabOrder(self.stream_btn, self.record_btn)
        self.setTabOrder(self.record_btn, self.face_swap_btn)
        self.setTabOrder(self.face_swap_btn, self.settings_btn)
        
        # Keyboard shortcuts
        stream_action = QAction("Toggle Streaming", self)
        stream_action.setShortcut("Ctrl+S")
        stream_action.triggered.connect(self.on_stream_toggle)
        self.addAction(stream_action)
        
        record_action = QAction("Toggle Recording", self)
        record_action.setShortcut("Ctrl+R")
        record_action.triggered.connect(self.on_record_toggle)
        self.addAction(record_action)
        
    def on_stream_toggle(self):
        """Handle streaming toggle"""
        if self.stream_btn.text() == "Start Streaming":
            self.stream_btn.setText("Stop Streaming")
            self.stream_btn.setStyleSheet(self.stream_btn.styleSheet().replace("#e74c3c", "#c0392b"))
        else:
            self.stream_btn.setText("Start Streaming")
            self.stream_btn.setStyleSheet(self.stream_btn.styleSheet().replace("#c0392b", "#e74c3c"))
            
    def on_record_toggle(self):
        """Handle recording toggle"""
        if self.record_btn.text() == "Start Recording":
            self.record_btn.setText("Stop Recording")
            self.record_btn.setStyleSheet(self.record_btn.styleSheet().replace("#e67e22", "#d35400"))
        else:
            self.record_btn.setText("Start Recording")
            self.record_btn.setStyleSheet(self.record_btn.styleSheet().replace("#d35400", "#e67e22"))
            
    def update_status(self, fps=None, memory=None, cpu=None):
        """Update status indicators"""
        if fps is not None:
            self.fps_label.setText(f"FPS: {fps:.0f}")
        if memory is not None:
            self.memory_label.setText(f"Memory: {memory:.1f} GB")
        if cpu is not None:
            self.cpu_label.setText(f"CPU: {cpu:.0f}%")
            
    def show_progress(self, visible=True, value=0):
        """Show/hide progress bar"""
        self.progress_bar.setVisible(visible)
        if visible:
            self.progress_bar.setValue(value)
            
    def resizeEvent(self, event):
        """Handle responsive resizing"""
        super().resizeEvent(event)
        # Adjust layout based on available space
        width = self.width()
        if width < 300:
            # Compact mode
            self.tab_widget.setMaximumHeight(80)
        else:
            # Normal mode
            self.tab_widget.setMaximumHeight(120) 