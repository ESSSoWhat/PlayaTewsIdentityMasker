from pathlib import Path
from typing import List, Dict, Optional
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QPushButton, QLabel, QComboBox, QSpinBox, QLineEdit,
                            QCheckBox, QGroupBox, QTabWidget, QSplitter, 
                            QListWidget, QListWidgetItem, QSlider, QFrame,
                            QTextEdit, QProgressBar, QScrollArea, QSizePolicy)

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

from ..backend import StreamOutput
from ..backend.StreamOutput import SourceType


class QOBSStyleUI(qtx.QXWindow):
    """OBS Studio-style UI for DeepFaceLive with enhanced streaming and recording capabilities"""
    
    def __init__(self, stream_output_backend: StreamOutput, userdata_path: Path, face_swap_components=None, viewers_components=None):
        super().__init__()
        self.stream_output_backend = stream_output_backend
        self.userdata_path = userdata_path
        self.face_swap_components = face_swap_components or {}
        self.viewers_components = viewers_components or {}
        self.scenes = []
        self.current_scene = None
        self.sources_by_scene = {}  # Track sources per scene
        self.streaming_platforms = {
            'twitch': {'name': 'Twitch', 'rtmp': 'rtmp://live.twitch.tv/app/'},
            'youtube': {'name': 'YouTube', 'rtmp': 'rtmp://a.rtmp.youtube.com/live2/'},
            'facebook': {'name': 'Facebook', 'rtmp': 'rtmp://live-api-s.facebook.com/rtmp/'},
            'custom': {'name': 'Custom RTMP', 'rtmp': ''}
        }
        self.recording_formats = ['mp4', 'mkv', 'avi', 'mov']
        self.recording_qualities = ['1080p', '720p', '480p', '360p']
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        main_layout = QHBoxLayout()
        
        # Left panel - Sources and Scenes
        left_panel = self.create_left_panel()
        
        # Center panel - Preview and Controls
        center_panel = self.create_center_panel()
        
        # Create splitter for resizable panels (removed right panel)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.setSizes([250, 800])  # Adjusted sizes for two panels
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
    def create_left_panel(self):
        """Create the left panel with scenes and sources"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Scenes section
        scenes_group = QGroupBox("Scenes")
        scenes_layout = QVBoxLayout()
        
        self.scenes_list = QListWidget()
        self.scenes_list.setMaximumHeight(150)
        scenes_layout.addWidget(self.scenes_list)
        
        scenes_buttons_layout = QHBoxLayout()
        self.add_scene_btn = QPushButton("+")
        self.add_scene_btn.setMaximumWidth(30)
        self.remove_scene_btn = QPushButton("-")
        self.remove_scene_btn.setMaximumWidth(30)
        self.duplicate_scene_btn = QPushButton("Copy")
        
        scenes_buttons_layout.addWidget(self.add_scene_btn)
        scenes_buttons_layout.addWidget(self.remove_scene_btn)
        scenes_buttons_layout.addWidget(self.duplicate_scene_btn)
        scenes_buttons_layout.addStretch()
        
        scenes_layout.addLayout(scenes_buttons_layout)
        scenes_group.setLayout(scenes_layout)
        
        # Sources section
        sources_group = QGroupBox("Sources")
        sources_layout = QVBoxLayout()
        
        self.sources_list = QListWidget()
        sources_layout.addWidget(self.sources_list)
        
        sources_buttons_layout = QHBoxLayout()
        self.add_source_btn = QPushButton("+")
        self.add_source_btn.setMaximumWidth(30)
        self.remove_source_btn = QPushButton("-")
        self.remove_source_btn.setMaximumWidth(30)
        self.source_properties_btn = QPushButton("Properties")
        
        sources_buttons_layout.addWidget(self.add_source_btn)
        sources_buttons_layout.addWidget(self.remove_source_btn)
        sources_buttons_layout.addWidget(self.source_properties_btn)
        sources_buttons_layout.addStretch()
        
        sources_layout.addLayout(sources_buttons_layout)
        sources_group.setLayout(sources_layout)
        
        layout.addWidget(scenes_group)
        layout.addWidget(sources_group)
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
        
    def create_center_panel(self):
        """Create the center panel with preview, controls, and viewers"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Top section: Preview and Controls
        top_section = QWidget()
        top_layout = QHBoxLayout()
        
        # Preview area (left side of top section) - Now contains merged frame viewer
        preview_group = QGroupBox("Active Screen")
        preview_layout = QVBoxLayout()
        
        # Use merged frame viewer as the main preview
        if 'merged_frame_viewer' in self.viewers_components:
            self.main_preview = self.viewers_components['merged_frame_viewer']
            # Remove size constraints and let it stretch to fill
            self.main_preview.setMinimumSize(400, 300)  # Smaller minimum
            self.main_preview.setMaximumSize(16777215, 16777215)  # Remove maximum size constraint
            self.main_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Stretch to fit
            # Set stretch factor to take all available space
            preview_layout.addWidget(self.main_preview, 1)  # Stretch factor of 1
        else:
            self.main_preview = QLabel("Merged Frame Preview")
            self.main_preview.setMinimumSize(400, 300)  # Smaller minimum
            self.main_preview.setMaximumSize(16777215, 16777215)  # Remove maximum size constraint
            self.main_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Stretch to fit
            self.main_preview.setStyleSheet("""
                QLabel {
                    background-color: #1e1e1e;
                    border: 2px solid #404040;
                    border-radius: 5px;
                    color: #ffffff;
                    font-size: 16px;
                }
            """)
            self.main_preview.setAlignment(Qt.AlignCenter)
            # Set stretch factor to take all available space
            preview_layout.addWidget(self.main_preview, 1)  # Stretch factor of 1
        
        preview_group.setLayout(preview_layout)
        
        # Controls area (right side of top section)
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        
        # Streaming controls
        self.stream_btn = QPushButton("Start Streaming")
        self.stream_btn.setMinimumHeight(40)
        self.stream_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
        # Recording controls
        self.record_btn = QPushButton("Start Recording")
        self.record_btn.setMinimumHeight(40)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
        """)
        
        # Global Face Swap Control Button
        self.global_face_swap_btn = QPushButton("Face Swap: ON")
        self.global_face_swap_btn.setMinimumHeight(40)
        self.global_face_swap_btn.setCheckable(True)
        self.global_face_swap_btn.setChecked(True)  # Default to ON
        self.global_face_swap_btn.setToolTip("Click to toggle all face swap components on/off\nGreen = ON, Red = OFF")
        self.global_face_swap_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:checked {
                background-color: #27ae60;
            }
            QPushButton:!checked {
                background-color: #e74c3c;
            }
        """)
        
        # Settings button
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setMinimumHeight(30)
        
        # Processing window button
        self.processing_btn = QPushButton("All Controls")
        self.processing_btn.setMinimumHeight(30)
        self.processing_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        controls_layout.addWidget(self.stream_btn)
        controls_layout.addWidget(self.record_btn)
        controls_layout.addWidget(self.global_face_swap_btn)
        controls_layout.addWidget(self.settings_btn)
        controls_layout.addWidget(self.processing_btn)
        controls_layout.addStretch()
        
        controls_group.setLayout(controls_layout)
        
        # Add preview and controls to top section - give more space to preview
        top_layout.addWidget(preview_group, 3)  # Stretch factor of 3 for preview
        top_layout.addWidget(controls_group, 1)  # Stretch factor of 1 for controls
        top_section.setLayout(top_layout)
        
        # Bottom section: Viewers
        bottom_section = QWidget()
        bottom_layout = QVBoxLayout()
        
        # Viewers group
        viewers_group = QGroupBox("Processing Views")
        viewers_layout = QHBoxLayout()
        
        # Use actual viewers if available, otherwise create placeholders
        if 'frame_viewer' in self.viewers_components:
            frame_viewer = self.viewers_components['frame_viewer']
            frame_viewer.setMinimumSize(150, 120)  # Smaller size
        else:
            frame_viewer = QLabel("Frame Viewer")
            frame_viewer.setMinimumSize(150, 120)  # Smaller size
            frame_viewer.setStyleSheet("""
                QLabel {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #cccccc;
                    font-size: 12px;
                }
            """)
            frame_viewer.setAlignment(Qt.AlignCenter)
        
        if 'face_align_viewer' in self.viewers_components:
            face_align_viewer = self.viewers_components['face_align_viewer']
            face_align_viewer.setMinimumSize(150, 120)  # Smaller size
        else:
            face_align_viewer = QLabel("Face Align Viewer")
            face_align_viewer.setMinimumSize(150, 120)  # Smaller size
            face_align_viewer.setStyleSheet("""
                QLabel {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #cccccc;
                    font-size: 12px;
                }
            """)
            face_align_viewer.setAlignment(Qt.AlignCenter)
        
        if 'face_swap_viewer' in self.viewers_components:
            face_swap_viewer = self.viewers_components['face_swap_viewer']
            face_swap_viewer.setMinimumSize(150, 120)  # Smaller size
        else:
            face_swap_viewer = QLabel("Face Swap Viewer")
            face_swap_viewer.setMinimumSize(150, 120)  # Smaller size
            face_swap_viewer.setStyleSheet("""
                QLabel {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #cccccc;
                    font-size: 12px;
                }
            """)
            face_swap_viewer.setAlignment(Qt.AlignCenter)
        
        # Only show the smaller viewers in the bottom section
        viewers_layout.addWidget(frame_viewer)
        viewers_layout.addWidget(face_align_viewer)
        viewers_layout.addWidget(face_swap_viewer)
        
        viewers_group.setLayout(viewers_layout)
        bottom_layout.addWidget(viewers_group)
        bottom_section.setLayout(bottom_layout)
        
        # Add sections to main layout - give more space to preview area
        layout.addWidget(top_section, 4)  # Stretch factor of 4 for preview area
        layout.addWidget(bottom_section, 1)  # Stretch factor of 1 for bottom viewers
        
        panel.setLayout(layout)
        return panel
        
    def create_right_panel(self):
        """Create the right panel with settings and audio controls"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Create simplified right panel with just info
        info_label = QLabel("PlayaTewsIdentityMasker OBS-Style Interface\n\nAll controls have been moved to the All Controls window for a cleaner interface.\n\nClick the 'All Controls' button in the center panel to access:\n• Face Swap Processing\n• Streaming Settings\n• Recording Settings\n• Audio Settings\n• Video Settings\n• Performance Controls")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 5px;
                color: #ffffff;
                font-size: 12px;
                padding: 30px;
                line-height: 1.5;
            }
        """)
        
        # Create simple layout for right panel
        right_layout = QVBoxLayout()
        right_layout.addWidget(info_label)
        right_layout.addStretch()
        
        # Create a simple widget instead of tab widget
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        layout.addWidget(right_widget)
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
        


        
    def setup_styles(self):
        """Setup the OBS Studio-like dark theme"""
        self.setStyleSheet("""
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
            
            QComboBox {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
                color: #ffffff;
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
            
            QLineEdit {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
                color: #ffffff;
            }
            
            QSpinBox {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
                color: #ffffff;
            }
            
            QCheckBox {
                spacing: 5px;
            }
            
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
            
            QCheckBox::indicator:unchecked {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 2px;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
                border-radius: 2px;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #606060;
                height: 8px;
                background: #404040;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #0078d4;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            
            QTabWidget::pane {
                border: 1px solid #606060;
                background-color: #2b2b2b;
            }
            
            QTabBar::tab {
                background-color: #404040;
                border: 1px solid #606060;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            
            QListWidget {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 3px;
                color: #ffffff;
            }
            
            QListWidget::item {
                padding: 5px;
            }
            
            QListWidget::item:selected {
                background-color: #0078d4;
            }
        """)
        
    def setup_connections(self):
        """Setup signal connections"""
        # Connect processing window button
        self.processing_btn.clicked.connect(self.open_processing_window)
        
        # Connect global face swap control
        self.global_face_swap_btn.toggled.connect(self.on_global_face_swap_toggled)
        
        # Initialize processing window
        self.processing_window = None
        
        # Initialize global face swap state
        self.initialize_global_face_swap_state()
        
    def open_processing_window(self):
        """Open the processing controls window"""
        if self.processing_window is None or not self.processing_window.isVisible():
            try:
                # Create a safer processing window that handles CSW issues
                self.processing_window = self.create_safe_processing_window()
                self.processing_window.show()
            except Exception as e:
                print(f"Error creating processing window: {e}")
                # Fallback: show a simple message
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "All Controls", 
                                      "All controls window not available.\n"
                                      "Controls are integrated in the main interface.")
        else:
            self.processing_window.raise_()
            self.processing_window.activateWindow()
    
    def create_safe_processing_window(self):
        """Create a safe processing window that handles CSW issues"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QWidget, QLabel, QScrollArea, QGroupBox, QPushButton
        from PyQt5.QtCore import Qt
        
        # Create dialog window
        window = QDialog(self)
        window.setWindowTitle("PlayaTewsIdentityMasker - All Controls")
        window.setMinimumSize(1000, 700)
        window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Create tabs for different categories
        tabs = {
            "Input Sources": self.create_input_sources_tab(),
            "Face Detection": self.create_face_detection_tab(),
            "Face Swapping": self.create_face_swapping_tab(),
            "Animation & Effects": self.create_animation_effects_tab(),
            "Output & Streaming": self.create_output_streaming_tab()
        }
        
        # Add tabs to widget
        for tab_name, tab_widget_content in tabs.items():
            tab_widget.addTab(tab_widget_content, tab_name)
        
        layout.addWidget(tab_widget)
        window.setLayout(layout)
        
        return window
    
    def create_input_sources_tab(self):
        """Create input sources tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # File Source
        if 'file_source' in self.face_swap_components:
            try:
                file_source = self.face_swap_components['file_source']
                if hasattr(file_source, 'widget'):
                    layout.addWidget(QLabel("📁 File Source"))
                    layout.addWidget(file_source.widget())
                elif hasattr(file_source, '__class__'):
                    layout.addWidget(QLabel("📁 File Source"))
                    layout.addWidget(file_source)
                else:
                    layout.addWidget(QLabel("📁 File Source: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"📁 File Source: Error - {e}"))
        else:
            layout.addWidget(QLabel("📁 File Source: Not Available"))
        
        # Camera Source
        if 'camera_source' in self.face_swap_components:
            try:
                camera_source = self.face_swap_components['camera_source']
                if hasattr(camera_source, 'widget'):
                    layout.addWidget(QLabel("📹 Camera Source"))
                    layout.addWidget(camera_source.widget())
                elif hasattr(camera_source, '__class__'):
                    layout.addWidget(QLabel("📹 Camera Source"))
                    layout.addWidget(camera_source)
                else:
                    layout.addWidget(QLabel("📹 Camera Source: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"📹 Camera Source: Error - {e}"))
        else:
            layout.addWidget(QLabel("📹 Camera Source: Not Available"))
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_face_detection_tab(self):
        """Create face detection tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Face Detector
        if 'face_detector' in self.face_swap_components:
            try:
                face_detector = self.face_swap_components['face_detector']
                if hasattr(face_detector, 'widget'):
                    layout.addWidget(QLabel("👁️ Face Detector"))
                    layout.addWidget(face_detector.widget())
                elif hasattr(face_detector, '__class__'):
                    layout.addWidget(QLabel("👁️ Face Detector"))
                    layout.addWidget(face_detector)
                else:
                    layout.addWidget(QLabel("👁️ Face Detector: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"👁️ Face Detector: Error - {e}"))
        else:
            layout.addWidget(QLabel("👁️ Face Detector: Not Available"))
        
        # Face Marker
        if 'face_marker' in self.face_swap_components:
            try:
                face_marker = self.face_swap_components['face_marker']
                if hasattr(face_marker, 'widget'):
                    layout.addWidget(QLabel("📍 Face Marker"))
                    layout.addWidget(face_marker.widget())
                elif hasattr(face_marker, '__class__'):
                    layout.addWidget(QLabel("📍 Face Marker"))
                    layout.addWidget(face_marker)
                else:
                    layout.addWidget(QLabel("📍 Face Marker: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"📍 Face Marker: Error - {e}"))
        else:
            layout.addWidget(QLabel("📍 Face Marker: Not Available"))
        
        # Face Aligner
        if 'face_aligner' in self.face_swap_components:
            try:
                face_aligner = self.face_swap_components['face_aligner']
                if hasattr(face_aligner, 'widget'):
                    layout.addWidget(QLabel("🎯 Face Aligner"))
                    layout.addWidget(face_aligner.widget())
                elif hasattr(face_aligner, '__class__'):
                    layout.addWidget(QLabel("🎯 Face Aligner"))
                    layout.addWidget(face_aligner)
                else:
                    layout.addWidget(QLabel("🎯 Face Aligner: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"🎯 Face Aligner: Error - {e}"))
        else:
            layout.addWidget(QLabel("🎯 Face Aligner: Not Available"))
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_face_swapping_tab(self):
        """Create face swapping tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Face Swap Insight
        if 'face_swap_insight' in self.face_swap_components:
            try:
                face_swap_insight = self.face_swap_components['face_swap_insight']
                if hasattr(face_swap_insight, 'widget'):
                    layout.addWidget(QLabel("🔄 Face Swap Insight"))
                    layout.addWidget(face_swap_insight.widget())
                elif hasattr(face_swap_insight, '__class__'):
                    layout.addWidget(QLabel("🔄 Face Swap Insight"))
                    layout.addWidget(face_swap_insight)
                else:
                    layout.addWidget(QLabel("🔄 Face Swap Insight: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"🔄 Face Swap Insight: Error - {e}"))
        else:
            layout.addWidget(QLabel("🔄 Face Swap Insight: Not Available"))
        
        # Face Swap DFM
        if 'face_swap_dfm' in self.face_swap_components:
            try:
                face_swap_dfm = self.face_swap_components['face_swap_dfm']
                if hasattr(face_swap_dfm, 'widget'):
                    layout.addWidget(QLabel("🔄 Face Swap DFM"))
                    layout.addWidget(face_swap_dfm.widget())
                elif hasattr(face_swap_dfm, '__class__'):
                    layout.addWidget(QLabel("🔄 Face Swap DFM"))
                    layout.addWidget(face_swap_dfm)
                else:
                    layout.addWidget(QLabel("🔄 Face Swap DFM: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"🔄 Face Swap DFM: Error - {e}"))
        else:
            layout.addWidget(QLabel("🔄 Face Swap DFM: Not Available"))
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_animation_effects_tab(self):
        """Create animation and effects tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Face Animator
        if 'face_animator' in self.face_swap_components:
            try:
                face_animator = self.face_swap_components['face_animator']
                if hasattr(face_animator, 'widget'):
                    layout.addWidget(QLabel("🎭 Face Animator"))
                    layout.addWidget(face_animator.widget())
                elif hasattr(face_animator, '__class__'):
                    layout.addWidget(QLabel("🎭 Face Animator"))
                    layout.addWidget(face_animator)
                else:
                    layout.addWidget(QLabel("🎭 Face Animator: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"🎭 Face Animator: Error - {e}"))
        else:
            layout.addWidget(QLabel("🎭 Face Animator: Not Available"))
        
        # Frame Adjuster
        if 'frame_adjuster' in self.face_swap_components:
            try:
                frame_adjuster = self.face_swap_components['frame_adjuster']
                if hasattr(frame_adjuster, 'widget'):
                    layout.addWidget(QLabel("🎨 Frame Adjuster"))
                    layout.addWidget(frame_adjuster.widget())
                elif hasattr(frame_adjuster, '__class__'):
                    layout.addWidget(QLabel("🎨 Frame Adjuster"))
                    layout.addWidget(frame_adjuster)
                else:
                    layout.addWidget(QLabel("🎨 Frame Adjuster: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"🎨 Frame Adjuster: Error - {e}"))
        else:
            layout.addWidget(QLabel("🎨 Frame Adjuster: Not Available"))
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_output_streaming_tab(self):
        """Create output and streaming tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Face Merger
        if 'face_merger' in self.face_swap_components:
            try:
                face_merger = self.face_swap_components['face_merger']
                if hasattr(face_merger, 'widget'):
                    layout.addWidget(QLabel("🔗 Face Merger"))
                    layout.addWidget(face_merger.widget())
                elif hasattr(face_merger, '__class__'):
                    layout.addWidget(QLabel("🔗 Face Merger"))
                    layout.addWidget(face_merger)
                else:
                    layout.addWidget(QLabel("🔗 Face Merger: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"🔗 Face Merger: Error - {e}"))
        else:
            layout.addWidget(QLabel("🔗 Face Merger: Not Available"))
        
        # Stream Output
        if 'stream_output' in self.face_swap_components:
            try:
                stream_output = self.face_swap_components['stream_output']
                if hasattr(stream_output, 'widget'):
                    layout.addWidget(QLabel("📺 Stream Output"))
                    layout.addWidget(stream_output.widget())
                elif hasattr(stream_output, '__class__'):
                    layout.addWidget(QLabel("📺 Stream Output"))
                    layout.addWidget(stream_output)
                else:
                    layout.addWidget(QLabel("📺 Stream Output: Not Available"))
            except Exception as e:
                layout.addWidget(QLabel(f"📺 Stream Output: Error - {e}"))
        else:
            layout.addWidget(QLabel("📺 Stream Output: Not Available"))
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
        
    def closeEvent(self, event):
        """Handle close event - ensure processing window is closed"""
        if self.processing_window and self.processing_window.isVisible():
            self.processing_window.close()
        event.accept()
    
    # Global face swap control methods
    def on_global_face_swap_toggled(self, enabled):
        """Handle global face swap enable/disable"""
        try:
            if enabled:
                self.global_face_swap_btn.setText("Face Swap: ON")
                self.global_face_swap_btn.setToolTip("Face swap is ENABLED\nAll components are running\nClick to disable")
                self.enable_all_face_swap_components()
                print("Global face swap enabled")
            else:
                self.global_face_swap_btn.setText("Face Swap: OFF")
                self.global_face_swap_btn.setToolTip("Face swap is DISABLED\nAll components are stopped\nClick to enable")
                self.disable_all_face_swap_components()
                print("Global face swap disabled")
            
            # Save the state
            self.save_global_face_swap_state(enabled)
            
        except Exception as e:
            print(f"Error toggling global face swap: {e}")
    
    def enable_all_face_swap_components(self):
        """Enable all face swap components"""
        if not self.face_swap_components:
            return
        
        # List of components to enable
        components_to_enable = [
            'face_detector', 'face_marker', 'face_aligner', 
            'face_animator', 'face_swap_insight', 'face_swap_dfm',
            'frame_adjuster', 'face_merger'
        ]
        
        for component_name in components_to_enable:
            if component_name in self.face_swap_components:
                component = self.face_swap_components[component_name]
                try:
                    # Try to enable the component through its backend
                    if hasattr(component, '_backend') and hasattr(component._backend, 'start'):
                        component._backend.start()
                    # Also try to enable any checkboxes in the component
                    self._enable_component_checkboxes(component, True)
                except Exception as e:
                    print(f"Error enabling {component_name}: {e}")
    
    def disable_all_face_swap_components(self):
        """Disable all face swap components"""
        if not self.face_swap_components:
            return
        
        # List of components to disable
        components_to_disable = [
            'face_detector', 'face_marker', 'face_aligner', 
            'face_animator', 'face_swap_insight', 'face_swap_dfm',
            'frame_adjuster', 'face_merger'
        ]
        
        for component_name in components_to_disable:
            if component_name in self.face_swap_components:
                component = self.face_swap_components[component_name]
                try:
                    # Try to disable the component through its backend
                    if hasattr(component, '_backend') and hasattr(component._backend, 'stop'):
                        component._backend.stop()
                    # Also try to disable any checkboxes in the component
                    self._enable_component_checkboxes(component, False)
                except Exception as e:
                    print(f"Error disabling {component_name}: {e}")
    
    def _enable_component_checkboxes(self, component, enabled):
        """Enable or disable checkboxes in a component"""
        try:
            from PyQt5.QtWidgets import QCheckBox
            checkboxes = component.findChildren(QCheckBox)
            for checkbox in checkboxes:
                if checkbox.isCheckable():
                    checkbox.setChecked(enabled)
        except Exception as e:
            print(f"Error setting checkboxes in component: {e}")
    
    def save_global_face_swap_state(self, enabled):
        """Save the global face swap state to persistent storage"""
        try:
            import json
            from pathlib import Path
            
            # Create settings directory if it doesn't exist
            settings_dir = Path(self.userdata_path) / 'settings'
            settings_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to a JSON file
            state_file = settings_dir / 'global_face_swap_state.json'
            state_data = {
                'enabled': enabled,
                'timestamp': str(Path().stat().st_mtime) if Path().exists() else '0'
            }
            
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving global face swap state: {e}")
    
    def load_global_face_swap_state(self):
        """Load the global face swap state from persistent storage"""
        try:
            import json
            from pathlib import Path
            
            state_file = Path(self.userdata_path) / 'settings' / 'global_face_swap_state.json'
            
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                
                enabled = state_data.get('enabled', True)  # Default to True
                return enabled
            else:
                return True  # Default to enabled if no saved state
                
        except Exception as e:
            print(f"Error loading global face swap state: {e}")
            return True  # Default to enabled on error
    
    def initialize_global_face_swap_state(self):
        """Initialize the global face swap state on startup"""
        try:
            enabled = self.load_global_face_swap_state()
            self.global_face_swap_btn.setChecked(enabled)
            self.on_global_face_swap_toggled(enabled)
        except Exception as e:
            print(f"Error initializing global face swap state: {e}")