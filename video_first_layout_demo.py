#!/usr/bin/env python3
"""
Video-First Layout Demo for PlayaTewsIdentityMasker
Demonstrates UI/UX Design Guidelines with maximum space for merged video feed
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QLabel, QFrame, QGroupBox,
                             QPushButton, QComboBox, QSlider, QProgressBar,
                             QStackedWidget, QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QPainter

# Import our Shadcn UI components
from xlib.qt.widgets.QXShadcnButton import (
    QXShadcnButton, ButtonVariant, ButtonSize
)

class VideoFirstMainWindow(QMainWindow):
    """Main window optimized for video display with maximum space allocation"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlayaTewsIdentityMasker - Video-First Interface")
        self.setMinimumSize(1400, 900)
        
        # Setup central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with video priority
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)  # Minimal margins
        main_layout.setSpacing(5)  # Minimal spacing
        
        # Top bar - Minimal controls (5% height)
        top_bar = self.create_minimal_top_bar()
        main_layout.addWidget(top_bar)
        
        # Main content area (90% height)
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Collapsible (15% width when expanded)
        left_panel = self.create_collapsible_left_panel()
        content_splitter.addWidget(left_panel)
        
        # Center panel - Video feed (80%+ width)
        video_panel = self.create_video_centric_panel()
        content_splitter.addWidget(video_panel)
        
        # Right panel - Settings (5% width when expanded)
        right_panel = self.create_collapsible_right_panel()
        content_splitter.addWidget(right_panel)
        
        # Set initial proportions: 15% | 80% | 5%
        content_splitter.setSizes([210, 1120, 70])
        
        main_layout.addWidget(content_splitter, 1)  # Maximum stretch
        
        # Bottom bar - Status (5% height)
        bottom_bar = self.create_minimal_bottom_bar()
        main_layout.addWidget(bottom_bar)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Setup responsive design
        self.setup_responsive_design()
        
        # Setup accessibility
        self.setup_accessibility()
    
    def create_minimal_top_bar(self):
        """Create minimal top bar with essential controls"""
        top_bar = QFrame()
        top_bar.setFrameStyle(QFrame.StyledPanel)
        top_bar.setMaximumHeight(60)
        top_bar.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """)
        
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # App title
        title = QLabel("🎭 PlayaTewsIdentityMasker")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # One-click actions
        self.stream_button = QXShadcnButton(
            "📹 Start Stream",
            variant=ButtonVariant.DEFAULT,
            size=ButtonSize.MD
        )
        self.stream_button.clicked.connect(self.toggle_stream)
        layout.addWidget(self.stream_button)
        
        self.record_button = QXShadcnButton(
            "🎥 Start Recording",
            variant=ButtonVariant.SECONDARY,
            size=ButtonSize.MD
        )
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)
        
        # Settings button
        settings_button = QXShadcnButton(
            "⚙️",
            variant=ButtonVariant.GHOST,
            size=ButtonSize.SM
        )
        settings_button.clicked.connect(self.show_settings)
        layout.addWidget(settings_button)
        
        return top_bar
    
    def create_collapsible_left_panel(self):
        """Create collapsible left panel with processing controls"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setMaximumWidth(300)
        panel.setMinimumWidth(200)
        panel.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Panel header with collapse button
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        header_label = QLabel("🎛️ Processing Controls")
        header_label.setStyleSheet("font-weight: bold; color: white;")
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        self.collapse_button = QXShadcnButton(
            "◀",
            variant=ButtonVariant.GHOST,
            size=ButtonSize.SM
        )
        self.collapse_button.clicked.connect(self.toggle_left_panel)
        header_layout.addWidget(self.collapse_button)
        
        layout.addWidget(header)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)
        
        # Camera source
        camera_group = self.create_camera_controls()
        content_layout.addWidget(camera_group)
        
        # Face detection
        face_group = self.create_face_detection_controls()
        content_layout.addWidget(face_group)
        
        # Face swap
        swap_group = self.create_face_swap_controls()
        content_layout.addWidget(swap_group)
        
        # Voice changer
        voice_group = self.create_voice_controls()
        content_layout.addWidget(voice_group)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return panel
    
    def create_video_centric_panel(self):
        """Create video-centric panel with maximum space for video feed"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setStyleSheet("""
            QFrame {
                background: #0a0a0a;
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)  # Minimal margins
        layout.setSpacing(5)  # Minimal spacing
        
        # Main video area (95% of panel)
        self.video_area = QFrame()
        self.video_area.setStyleSheet("""
            QFrame {
                background: #000000;
                border: 2px solid #404040;
                border-radius: 8px;
            }
        """)
        self.video_area.setMinimumSize(800, 600)
        
        # Video overlay with controls
        video_overlay = QWidget()
        video_overlay.setStyleSheet("background: transparent;")
        video_overlay_layout = QVBoxLayout(video_overlay)
        video_overlay_layout.setContentsMargins(10, 10, 10, 10)
        
        # Video info
        video_info = QLabel("🎥 Merged Video Feed - 1920x1080 @ 30 FPS")
        video_info.setStyleSheet("""
            QLabel {
                color: white;
                background: rgba(0, 0, 0, 0.7);
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        video_overlay_layout.addWidget(video_info)
        
        video_overlay_layout.addStretch()
        
        # Video controls
        video_controls = QWidget()
        video_controls.setStyleSheet("background: transparent;")
        controls_layout = QHBoxLayout(video_controls)
        
        # Quality indicator
        quality_label = QLabel("⚡ High Quality")
        quality_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                background: rgba(0, 0, 0, 0.7);
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        controls_layout.addWidget(quality_label)
        
        controls_layout.addStretch()
        
        # Fullscreen button
        fullscreen_button = QXShadcnButton(
            "⛶",
            variant=ButtonVariant.GHOST,
            size=ButtonSize.SM
        )
        fullscreen_button.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 0.7);
                color: white;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.9);
            }
        """)
        fullscreen_button.clicked.connect(self.toggle_fullscreen)
        controls_layout.addWidget(fullscreen_button)
        
        video_overlay_layout.addWidget(video_controls)
        
        # Stack video area and overlay
        video_stack = QStackedWidget()
        video_stack.addWidget(self.video_area)
        video_stack.addWidget(video_overlay)
        
        layout.addWidget(video_stack, 1)  # Maximum stretch
        
        # Secondary previews (5% of panel) - Collapsible
        self.secondary_previews = self.create_secondary_previews()
        layout.addWidget(self.secondary_previews)
        
        return panel
    
    def create_collapsible_right_panel(self):
        """Create collapsible right panel with settings"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setMaximumWidth(200)
        panel.setMinimumWidth(100)
        panel.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Panel header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        header_label = QLabel("⚙️ Settings")
        header_label.setStyleSheet("font-weight: bold; color: white;")
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        self.collapse_right_button = QXShadcnButton(
            "▶",
            variant=ButtonVariant.GHOST,
            size=ButtonSize.SM
        )
        self.collapse_right_button.clicked.connect(self.toggle_right_panel)
        header_layout.addWidget(self.collapse_right_button)
        
        layout.addWidget(header)
        
        # Settings content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)
        
        # Stream settings
        stream_group = self.create_stream_settings()
        content_layout.addWidget(stream_group)
        
        # Quality settings
        quality_group = self.create_quality_settings()
        content_layout.addWidget(quality_group)
        
        # Performance settings
        performance_group = self.create_performance_settings()
        content_layout.addWidget(performance_group)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return panel
    
    def create_minimal_bottom_bar(self):
        """Create minimal bottom bar with status information"""
        bottom_bar = QFrame()
        bottom_bar.setFrameStyle(QFrame.StyledPanel)
        bottom_bar.setMaximumHeight(50)
        bottom_bar.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """)
        
        layout = QHBoxLayout(bottom_bar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Status indicators
        self.stream_status = QLabel("🔴 Offline")
        self.stream_status.setStyleSheet("color: #ef4444; font-weight: bold;")
        layout.addWidget(self.stream_status)
        
        self.recording_status = QLabel("⏹️ Not Recording")
        self.recording_status.setStyleSheet("color: #888; font-weight: bold;")
        layout.addWidget(self.recording_status)
        
        self.face_status = QLabel("👤 No Face Detected")
        self.face_status.setStyleSheet("color: #888; font-weight: bold;")
        layout.addWidget(self.face_status)
        
        layout.addStretch()
        
        # Performance metrics
        self.fps_label = QLabel("⚡ 30 FPS")
        self.fps_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        layout.addWidget(self.fps_label)
        
        self.cpu_label = QLabel("🖥️ 45% CPU")
        self.cpu_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        layout.addWidget(self.cpu_label)
        
        self.memory_label = QLabel("💾 1.2GB RAM")
        self.memory_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        layout.addWidget(self.memory_label)
        
        return bottom_bar
    
    def create_camera_controls(self):
        """Create camera source controls"""
        group = QGroupBox("📷 Camera Source")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Camera selection
        camera_combo = QComboBox()
        camera_combo.addItems(["Webcam", "HD Camera", "USB Camera"])
        camera_combo.setStyleSheet("""
            QComboBox {
                background: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 5px;
                color: white;
            }
        """)
        layout.addWidget(camera_combo)
        
        # Resolution
        resolution_combo = QComboBox()
        resolution_combo.addItems(["1080p", "720p", "480p"])
        resolution_combo.setCurrentText("720p")
        layout.addWidget(resolution_combo)
        
        return group
    
    def create_face_detection_controls(self):
        """Create face detection controls"""
        group = QGroupBox("👤 Face Detection")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Detection method
        method_combo = QComboBox()
        method_combo.addItems(["S3FD", "CenterFace", "YOLOv5"])
        method_combo.setCurrentText("S3FD")
        layout.addWidget(method_combo)
        
        # Confidence threshold
        confidence_label = QLabel("Confidence: 0.8")
        layout.addWidget(confidence_label)
        
        confidence_slider = QSlider(Qt.Horizontal)
        confidence_slider.setRange(50, 100)
        confidence_slider.setValue(80)
        layout.addWidget(confidence_slider)
        
        return group
    
    def create_face_swap_controls(self):
        """Create face swap controls"""
        group = QGroupBox("🎭 Face Swap")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Model selection
        model_combo = QComboBox()
        model_combo.addItems(["InsightFace", "DFM Model", "Custom Model"])
        model_combo.setCurrentText("InsightFace")
        layout.addWidget(model_combo)
        
        # Quality slider
        quality_label = QLabel("Quality: High")
        layout.addWidget(quality_label)
        
        quality_slider = QSlider(Qt.Horizontal)
        quality_slider.setRange(1, 3)
        quality_slider.setValue(3)
        layout.addWidget(quality_slider)
        
        return group
    
    def create_voice_controls(self):
        """Create voice changer controls"""
        group = QGroupBox("🎤 Voice Changer")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Voice effect
        effect_combo = QComboBox()
        effect_combo.addItems(["None", "Helium", "Deep Voice", "Robot", "Echo"])
        layout.addWidget(effect_combo)
        
        # Enable checkbox
        enable_button = QXShadcnButton(
            "Enable Voice Changer",
            variant=ButtonVariant.OUTLINE,
            size=ButtonSize.SM
        )
        layout.addWidget(enable_button)
        
        return group
    
    def create_secondary_previews(self):
        """Create secondary previews panel"""
        panel = QFrame()
        panel.setMaximumHeight(120)
        panel.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 6px;
            }
        """)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Source preview
        source_preview = QFrame()
        source_preview.setStyleSheet("""
            QFrame {
                background: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
            }
        """)
        source_preview.setMinimumSize(150, 100)
        
        source_label = QLabel("Source")
        source_label.setStyleSheet("color: white; text-align: center;")
        source_label.setAlignment(Qt.AlignCenter)
        
        source_layout = QVBoxLayout(source_preview)
        source_layout.addWidget(source_label)
        
        layout.addWidget(source_preview)
        
        # Face aligned preview
        aligned_preview = QFrame()
        aligned_preview.setStyleSheet("""
            QFrame {
                background: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
            }
        """)
        aligned_preview.setMinimumSize(150, 100)
        
        aligned_label = QLabel("Face Aligned")
        aligned_label.setStyleSheet("color: white; text-align: center;")
        aligned_label.setAlignment(Qt.AlignCenter)
        
        aligned_layout = QVBoxLayout(aligned_preview)
        aligned_layout.addWidget(aligned_label)
        
        layout.addWidget(aligned_preview)
        
        # Face swapped preview
        swapped_preview = QFrame()
        swapped_preview.setStyleSheet("""
            QFrame {
                background: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
            }
        """)
        swapped_preview.setMinimumSize(150, 100)
        
        swapped_label = QLabel("Face Swapped")
        swapped_label.setStyleSheet("color: white; text-align: center;")
        swapped_label.setAlignment(Qt.AlignCenter)
        
        swapped_layout = QVBoxLayout(swapped_preview)
        swapped_layout.addWidget(swapped_label)
        
        layout.addWidget(swapped_preview)
        
        return panel
    
    def create_stream_settings(self):
        """Create stream settings group"""
        group = QGroupBox("📹 Stream Settings")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Platform
        platform_combo = QComboBox()
        platform_combo.addItems(["Twitch", "YouTube", "Facebook", "Custom RTMP"])
        layout.addWidget(platform_combo)
        
        # Stream key
        key_button = QXShadcnButton(
            "Set Stream Key",
            variant=ButtonVariant.OUTLINE,
            size=ButtonSize.SM
        )
        layout.addWidget(key_button)
        
        return group
    
    def create_quality_settings(self):
        """Create quality settings group"""
        group = QGroupBox("🎨 Quality Settings")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Resolution
        res_combo = QComboBox()
        res_combo.addItems(["1080p", "720p", "480p"])
        res_combo.setCurrentText("720p")
        layout.addWidget(res_combo)
        
        # FPS
        fps_combo = QComboBox()
        fps_combo.addItems(["60 FPS", "30 FPS", "24 FPS"])
        fps_combo.setCurrentText("30 FPS")
        layout.addWidget(fps_combo)
        
        return group
    
    def create_performance_settings(self):
        """Create performance settings group"""
        group = QGroupBox("⚡ Performance")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Performance mode
        mode_combo = QComboBox()
        mode_combo.addItems(["High Quality", "Balanced", "Performance"])
        mode_combo.setCurrentText("Balanced")
        layout.addWidget(mode_combo)
        
        # Auto-optimize
        optimize_button = QXShadcnButton(
            "Auto-Optimize",
            variant=ButtonVariant.SECONDARY,
            size=ButtonSize.SM
        )
        layout.addWidget(optimize_button)
        
        return group
    
    def apply_dark_theme(self):
        """Apply comprehensive dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
                color: #ffffff;
            }
            QWidget {
                background-color: #0a0a0a;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QComboBox {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 5px;
                color: white;
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
            QSlider::groove:horizontal {
                border: 1px solid #404040;
                height: 8px;
                background: #2a2a2a;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #0078d4;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #404040;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #505050;
            }
        """)
    
    def setup_responsive_design(self):
        """Setup responsive design system"""
        # Monitor window size changes
        self.resizeEvent = self.on_resize
        
        # Initial responsive setup
        self.apply_responsive_layout(self.width())
    
    def setup_accessibility(self):
        """Setup accessibility features"""
        # Set accessible names
        self.setAccessibleName("PlayaTewsIdentityMasker Main Window")
        self.setAccessibleDescription("Video-first streaming interface with face swapping capabilities")
        
        # Set focus policy
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for accessibility"""
        # Stream controls
        stream_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        stream_shortcut.activated.connect(self.toggle_stream)
        
        # Recording controls
        record_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        record_shortcut.activated.connect(self.toggle_recording)
        
        # Fullscreen
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
    
    def on_resize(self, event):
        """Handle window resize for responsive design"""
        self.apply_responsive_layout(event.size().width())
        super().resizeEvent(event)
    
    def apply_responsive_layout(self, width):
        """Apply responsive layout based on window width"""
        if width < 1200:
            # Compact layout
            self.apply_compact_layout()
        elif width < 1600:
            # Standard layout
            self.apply_standard_layout()
        else:
            # Wide layout
            self.apply_wide_layout()
    
    def apply_compact_layout(self):
        """Apply compact layout for smaller screens"""
        # Collapse side panels
        self.collapse_left_panel()
        self.collapse_right_panel()
    
    def apply_standard_layout(self):
        """Apply standard layout"""
        # Show side panels with standard sizes
        self.expand_left_panel()
        self.expand_right_panel()
    
    def apply_wide_layout(self):
        """Apply wide layout for ultrawide screens"""
        # Expand side panels for more controls
        self.expand_left_panel()
        self.expand_right_panel()
    
    def toggle_left_panel(self):
        """Toggle left panel visibility"""
        if self.sender().text() == "◀":
            self.collapse_left_panel()
        else:
            self.expand_left_panel()
    
    def toggle_right_panel(self):
        """Toggle right panel visibility"""
        if self.sender().text() == "▶":
            self.expand_right_panel()
        else:
            self.collapse_right_panel()
    
    def collapse_left_panel(self):
        """Collapse left panel"""
        self.collapse_button.setText("▶")
        # Animation would go here
    
    def expand_left_panel(self):
        """Expand left panel"""
        self.collapse_button.setText("◀")
        # Animation would go here
    
    def collapse_right_panel(self):
        """Collapse right panel"""
        self.collapse_right_button.setText("◀")
        # Animation would go here
    
    def expand_right_panel(self):
        """Expand right panel"""
        self.collapse_right_button.setText("▶")
        # Animation would go here
    
    def toggle_stream(self):
        """Toggle streaming"""
        if self.stream_button.text() == "📹 Start Stream":
            self.stream_button.setText("⏹️ Stop Stream")
            self.stream_button.set_variant(ButtonVariant.DESTRUCTIVE)
            self.stream_status.setText("🟢 Live")
            self.stream_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.stream_button.setText("📹 Start Stream")
            self.stream_button.set_variant(ButtonVariant.DEFAULT)
            self.stream_status.setText("🔴 Offline")
            self.stream_status.setStyleSheet("color: #ef4444; font-weight: bold;")
    
    def toggle_recording(self):
        """Toggle recording"""
        if self.record_button.text() == "🎥 Start Recording":
            self.record_button.setText("⏹️ Stop Recording")
            self.record_button.set_variant(ButtonVariant.DESTRUCTIVE)
            self.recording_status.setText("🔴 Recording")
            self.recording_status.setStyleSheet("color: #ef4444; font-weight: bold;")
        else:
            self.record_button.setText("🎥 Start Recording")
            self.record_button.set_variant(ButtonVariant.SECONDARY)
            self.recording_status.setText("⏹️ Not Recording")
            self.recording_status.setStyleSheet("color: #888; font-weight: bold;")
    
    def show_settings(self):
        """Show settings dialog"""
        # Placeholder for settings dialog
        print("Settings dialog would open here")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()


def main():
    """Main function to run the video-first layout demo"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("PlayaTewsIdentityMasker Video-First Demo")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PlayaTewsIdentityMasker")
    
    # Create and show main window
    window = VideoFirstMainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 