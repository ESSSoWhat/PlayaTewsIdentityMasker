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


class QOBSStyleUI(QWidget):
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
        
        # Preview area (left side of top section)
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("Preview Area")
        self.preview_label.setMinimumSize(800, 450)  # Larger preview
        self.preview_label.setMaximumSize(800, 450)  # Fixed size
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 5px;
                color: #ffffff;
                font-size: 16px;
            }
        """)
        self.preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.preview_label)
        
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
        controls_layout.addWidget(self.settings_btn)
        controls_layout.addWidget(self.processing_btn)
        controls_layout.addStretch()
        
        controls_group.setLayout(controls_layout)
        
        # Add preview and controls to top section
        top_layout.addWidget(preview_group)
        top_layout.addWidget(controls_group)
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
        
        # Merged frame viewer (stretches to fit - much larger)
        if 'merged_frame_viewer' in self.viewers_components:
            merged_frame_viewer = self.viewers_components['merged_frame_viewer']
            merged_frame_viewer.setMinimumSize(600, 200)  # Much larger
        else:
            merged_frame_viewer = QLabel("Merged Frame Viewer")
            merged_frame_viewer.setMinimumSize(600, 200)  # Much larger
            merged_frame_viewer.setStyleSheet("""
                QLabel {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #cccccc;
                    font-size: 12px;
                }
            """)
            merged_frame_viewer.setAlignment(Qt.AlignCenter)
        
        viewers_layout.addWidget(frame_viewer)
        viewers_layout.addWidget(face_align_viewer)
        viewers_layout.addWidget(face_swap_viewer)
        viewers_layout.addWidget(merged_frame_viewer, 3)  # Much more stretch weight
        
        viewers_group.setLayout(viewers_layout)
        bottom_layout.addWidget(viewers_group)
        bottom_section.setLayout(bottom_layout)
        
        # Add sections to main layout
        layout.addWidget(top_section)
        layout.addWidget(bottom_section)
        
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
        
        # Initialize processing window
        self.processing_window = None
        
    def open_processing_window(self):
        """Open the processing controls window"""
        if self.processing_window is None or not self.processing_window.isVisible():
            try:
                from .QProcessingWindow import QProcessingWindow
                self.processing_window = QProcessingWindow(self.face_swap_components)
                self.processing_window.show()
            except ImportError as e:
                print(f"Could not import QProcessingWindow: {e}")
                # Fallback: show a simple message
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "All Controls", 
                                      "All controls window not available.\n"
                                      "Controls are integrated in the main interface.")
        else:
            self.processing_window.raise_()
            self.processing_window.activateWindow()
        
    def closeEvent(self, event):
        """Handle close event - ensure processing window is closed"""
        if self.processing_window and self.processing_window.isVisible():
            self.processing_window.close()
        event.accept()