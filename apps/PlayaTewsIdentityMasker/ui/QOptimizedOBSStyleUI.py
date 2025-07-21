#!/usr/bin/env python3
"""
Optimized OBS-Style UI for PlayaTewsIdentityMasker
Implements space optimization, collapsible sections, and better organization
"""

from pathlib import Path
from typing import List, Dict, Optional
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QPushButton, QLabel, QComboBox, QSpinBox, QLineEdit,
                            QCheckBox, QGroupBox, QSplitter, 
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
from .widgets.QCollapsibleComponentWrapper import (
    QCollapsibleComponentWrapper, 
    QSmartCollapsibleGroup,
    make_collapsible,
    group_small_components
)

from ..backend import StreamOutput
from ..backend.StreamOutput import SourceType


class QOptimizedOBSStyleUI(QWidget):
    """Optimized OBS Studio-style UI with better space utilization"""
    
    def __init__(self, stream_output_backend: StreamOutput, userdata_path: Path, face_swap_components=None, viewers_components=None, voice_changer_backend=None):
        super().__init__()
        self.stream_output_backend = stream_output_backend
        self.userdata_path = userdata_path
        self.face_swap_components = face_swap_components or {}
        self.viewers_components = viewers_components or {}
        self.voice_changer_backend = voice_changer_backend
        self.scenes = []
        self.current_scene = None
        self.sources_by_scene = {}
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.initialize_global_face_swap_state()
        
    def setup_ui(self):
        """Setup the optimized main UI layout"""
        main_layout = QHBoxLayout()
        
        # Left panel - Sources and Scenes (increased width)
        left_panel = self.create_optimized_left_panel()
        
        # Center panel - Preview and Controls (responsive)
        center_panel = self.create_optimized_center_panel()
        
        # Right panel - Settings (restored with collapsible sections)
        right_panel = self.create_optimized_right_panel()
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 600, 300])  # Optimized panel sizes
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
    def create_optimized_left_panel(self):
        """Create optimized left panel with better space usage"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Scenes section (compact)
        scenes_group = QGroupBox("Scenes")
        scenes_layout = QVBoxLayout()
        
        self.scenes_list = QListWidget()
        self.scenes_list.setMaximumHeight(120)  # Reduced height
        scenes_layout.addWidget(self.scenes_list)
        
        # Compact scene buttons
        scenes_buttons_layout = QHBoxLayout()
        self.add_scene_btn = QPushButton("+")
        self.add_scene_btn.setMaximumWidth(25)
        self.remove_scene_btn = QPushButton("-")
        self.remove_scene_btn.setMaximumWidth(25)
        self.duplicate_scene_btn = QPushButton("Copy")
        self.duplicate_scene_btn.setMaximumWidth(50)
        
        scenes_buttons_layout.addWidget(self.add_scene_btn)
        scenes_buttons_layout.addWidget(self.remove_scene_btn)
        scenes_buttons_layout.addWidget(self.duplicate_scene_btn)
        scenes_buttons_layout.addStretch()
        
        scenes_layout.addLayout(scenes_buttons_layout)
        scenes_group.setLayout(scenes_layout)
        
        # Sources section (compact)
        sources_group = QGroupBox("Sources")
        sources_layout = QVBoxLayout()
        
        self.sources_list = QListWidget()
        sources_layout.addWidget(self.sources_list)
        
        # Compact source buttons
        sources_buttons_layout = QHBoxLayout()
        self.add_source_btn = QPushButton("+")
        self.add_source_btn.setMaximumWidth(25)
        self.remove_source_btn = QPushButton("-")
        self.remove_source_btn.setMaximumWidth(25)
        self.source_properties_btn = QPushButton("Props")
        self.source_properties_btn.setMaximumWidth(50)
        
        sources_buttons_layout.addWidget(self.add_source_btn)
        sources_buttons_layout.addWidget(self.remove_source_btn)
        sources_buttons_layout.addWidget(self.source_properties_btn)
        sources_buttons_layout.addStretch()
        
        sources_layout.addLayout(sources_buttons_layout)
        sources_group.setLayout(sources_layout)
        
        layout.addWidget(scenes_group)
        layout.addWidget(sources_group)
        
        # DFM Quick Access section (new addition)
        dfm_quick_access_group = self.create_dfm_quick_access_section()
        layout.addWidget(dfm_quick_access_group)
        
        # Voice Changer section
        voice_changer_group = self.create_voice_changer_section()
        layout.addWidget(voice_changer_group)
        
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
    
    def create_dfm_quick_access_section(self):
        """Create DFM quick access section for the left panel"""
        group = QGroupBox("Quick DFM Models")
        layout = QVBoxLayout()
        
        # Title and refresh button
        title_layout = QHBoxLayout()
        title_label = QLabel("Recent Models")
        title_label.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Refresh button
        self.refresh_dfm_btn = QPushButton("🔄")
        self.refresh_dfm_btn.setMaximumWidth(25)
        self.refresh_dfm_btn.setToolTip("Refresh DFM model list")
        self.refresh_dfm_btn.clicked.connect(self.refresh_dfm_models)
        title_layout.addWidget(self.refresh_dfm_btn)
        
        layout.addLayout(title_layout)
        
        # DFM model buttons (2x3 grid)
        self.dfm_buttons = []
        self.dfm_button_layout = QGridLayout()
        self.dfm_button_layout.setSpacing(5)
        
        for i in range(6):
            row = i // 2
            col = i % 2
            
            btn = QPushButton(f"DFM {i+1}")
            btn.setMinimumHeight(50)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c3e50;
                    border: 2px solid #34495e;
                    border-radius: 5px;
                    color: #ffffff;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #3498db;
                    border-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #e74c3c;
                    border-color: #c0392b;
                }
                QPushButton:disabled {
                    background-color: #34495e;
                    border-color: #2c3e50;
                    color: #7f8c8d;
                }
            """)
            btn.setEnabled(False)
            btn.clicked.connect(lambda checked, idx=i: self.on_dfm_button_clicked(idx))
            
            self.dfm_buttons.append(btn)
            self.dfm_button_layout.addWidget(btn, row, col)
        
        layout.addLayout(self.dfm_button_layout)
        
        # Status label
        self.dfm_status_label = QLabel("No DFM models found")
        self.dfm_status_label.setStyleSheet("color: #95a5a6; font-size: 9px;")
        self.dfm_status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.dfm_status_label)
        
        group.setLayout(layout)
        
        # Initialize DFM models
        self.dfm_models = []
        self.current_dfm_index = -1
        self.load_dfm_models()
        
        return group
    
    def create_voice_changer_section(self):
        """Create voice changer section for the left panel"""
        from .QCompactVoiceChanger import QCompactVoiceChanger
        
        # Create the compact voice changer widget
        if self.voice_changer_backend:
            self.voice_changer_widget = QCompactVoiceChanger(self.voice_changer_backend.get_control_sheet())
        else:
            # Create a placeholder if no voice changer backend is provided
            self.voice_changer_widget = QLabel("Voice Changer: Not Available")
            self.voice_changer_widget.setStyleSheet("""
                QLabel {
                    color: #cccccc;
                    font-size: 10px;
                    padding: 10px;
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                }
            """)
            self.voice_changer_widget.setAlignment(Qt.AlignCenter)
        
        # Create a group box to contain it
        group = QGroupBox("Voice Changer")
        group.setStyleSheet("""
            QGroupBox {
                color: #cccccc;
                font-size: 10px;
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 3px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 5px;
                padding: 0 3px 0 3px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.addWidget(self.voice_changer_widget)
        group.setLayout(layout)
        
        return group
    
    def load_dfm_models(self):
        """Load available DFM models from the universal DFM system"""
        try:
            # Try to import the universal DFM integration
            import sys
            sys.path.append(str(Path(__file__).parent.parent.parent / "universal_dfm"))
            
            try:
                from dfm_integration import get_face_swap_models
                models = get_face_swap_models()
                
                # Sort by priority (active first, then prebuilt)
                models.sort(key=lambda x: 0 if x.get("priority") == "high" else 1)
                
                # Take the first 6 models
                self.dfm_models = models[:6]
                
                # Update button states
                self.update_dfm_buttons()
                
                if self.dfm_models:
                    self.dfm_status_label.setText(f"Loaded {len(self.dfm_models)} models")
                else:
                    self.dfm_status_label.setText("No DFM models found")
                    
            except ImportError:
                # Fallback: scan dfm_models directory directly
                self.load_dfm_models_fallback()
                
        except Exception as e:
            print(f"Error loading DFM models: {e}")
            self.dfm_status_label.setText("Error loading models")
            self.load_dfm_models_fallback()
    
    def load_dfm_models_fallback(self):
        """Fallback method to load DFM models from local directory"""
        try:
            dfm_dir = self.userdata_path / "dfm_models"
            if not dfm_dir.exists():
                dfm_dir = Path("dfm_models")  # Try current directory
            
            if dfm_dir.exists():
                dfm_files = list(dfm_dir.glob("*.dfm"))
                # Sort by modification time (most recent first)
                dfm_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                self.dfm_models = []
                for dfm_file in dfm_files[:6]:
                    self.dfm_models.append({
                        "name": dfm_file.stem,
                        "file": str(dfm_file),
                        "category": "local",
                        "priority": "medium"
                    })
                
                self.update_dfm_buttons()
                
                if self.dfm_models:
                    self.dfm_status_label.setText(f"Loaded {len(self.dfm_models)} local models")
                else:
                    self.dfm_status_label.setText("No local DFM models found")
            else:
                self.dfm_status_label.setText("DFM directory not found")
                
        except Exception as e:
            print(f"Error in fallback DFM loading: {e}")
            self.dfm_status_label.setText("Error loading models")
    
    def update_dfm_buttons(self):
        """Update the DFM buttons with model information"""
        for i, btn in enumerate(self.dfm_buttons):
            if i < len(self.dfm_models):
                model = self.dfm_models[i]
                model_name = model.get("name", "Unknown")
                
                # Truncate name if too long
                display_name = model_name[:15] + "..." if len(model_name) > 15 else model_name
                
                btn.setText(f"DFM {i+1}\n{display_name}")
                btn.setToolTip(f"Model: {model_name}\nPath: {model.get('file', 'Unknown')}")
                btn.setEnabled(True)
                
                # Set different colors based on priority
                if model.get("priority") == "high":
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #27ae60;
                            border: 2px solid #2ecc71;
                            border-radius: 5px;
                            color: #ffffff;
                            font-size: 10px;
                            font-weight: bold;
                            padding: 5px;
                        }
                        QPushButton:hover {
                            background-color: #2ecc71;
                            border-color: #27ae60;
                        }
                        QPushButton:pressed {
                            background-color: #e74c3c;
                            border-color: #c0392b;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #2c3e50;
                            border: 2px solid #34495e;
                            border-radius: 5px;
                            color: #ffffff;
                            font-size: 10px;
                            font-weight: bold;
                            padding: 5px;
                        }
                        QPushButton:hover {
                            background-color: #3498db;
                            border-color: #2980b9;
                        }
                        QPushButton:pressed {
                            background-color: #e74c3c;
                            border-color: #c0392b;
                        }
                    """)
            else:
                btn.setText(f"DFM {i+1}\nEmpty")
                btn.setToolTip("No model available")
                btn.setEnabled(False)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #34495e;
                        border: 2px solid #2c3e50;
                        border-radius: 5px;
                        color: #7f8c8d;
                        font-size: 10px;
                        font-weight: bold;
                        padding: 5px;
                    }
                """)
    
    def on_dfm_button_clicked(self, index):
        """Handle DFM button click to switch models"""
        if index < len(self.dfm_models):
            model = self.dfm_models[index]
            model_name = model.get("name", "Unknown")
            
            # Update button states
            self.current_dfm_index = index
            self.update_button_selection()
            
            # Try to switch the model in the face swap component
            self.switch_dfm_model(model_name, model.get("file"))
            
            print(f"Switched to DFM model: {model_name}")
    
    def update_button_selection(self):
        """Update button selection state"""
        for i, btn in enumerate(self.dfm_buttons):
            if i == self.current_dfm_index:
                # Selected button - red background
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        border: 2px solid #c0392b;
                        border-radius: 5px;
                        color: #ffffff;
                        font-size: 10px;
                        font-weight: bold;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                        border-color: #e74c3c;
                    }
                """)
            elif i < len(self.dfm_models):
                # Unselected button - restore original color
                model = self.dfm_models[i]
                if model.get("priority") == "high":
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #27ae60;
                            border: 2px solid #2ecc71;
                            border-radius: 5px;
                            color: #ffffff;
                            font-size: 10px;
                            font-weight: bold;
                            padding: 5px;
                        }
                        QPushButton:hover {
                            background-color: #2ecc71;
                            border-color: #27ae60;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #2c3e50;
                            border: 2px solid #34495e;
                            border-radius: 5px;
                            color: #ffffff;
                            font-size: 10px;
                            font-weight: bold;
                            padding: 5px;
                        }
                        QPushButton:hover {
                            background-color: #3498db;
                            border-color: #2980b9;
                        }
                    """)
    
    def switch_dfm_model(self, model_name, model_path):
        """Switch to the specified DFM model in the face swap component"""
        try:
            # Find the face swap DFM component
            if 'face_swap_dfm' in self.face_swap_components:
                face_swap_component = self.face_swap_components['face_swap_dfm']
                
                # Get the control sheet
                cs = face_swap_component.get_control_sheet()
                
                # Get available models
                available_models = cs.model.get_choices()
                
                # Find the model by name
                for model in available_models:
                    if model and hasattr(model, 'get_name') and model.get_name() == model_name:
                        # Select the model
                        cs.model.select(model)
                        print(f"Successfully switched to model: {model_name}")
                        return
                
                print(f"Model '{model_name}' not found in available models")
            else:
                print("Face swap DFM component not found")
                
        except Exception as e:
            print(f"Error switching DFM model: {e}")
    
    def refresh_dfm_models(self):
        """Refresh the DFM model list"""
        print("Refreshing DFM models...")
        self.load_dfm_models()
        self.update_dfm_buttons()
        
    def create_optimized_center_panel(self):
        """Create optimized center panel with responsive preview"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Top section: Preview and Controls (responsive)
        top_section = QWidget()
        top_layout = QHBoxLayout()
        
        # Preview area (responsive)
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("Preview Area")
        self.preview_label.setMinimumSize(400, 300)  # Minimum size
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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
        
        # Controls area (compact)
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        
        # Compact control buttons
        self.stream_btn = QPushButton("Start Streaming")
        self.stream_btn.setMinimumHeight(35)
        self.stream_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        self.record_btn = QPushButton("Start Recording")
        self.record_btn.setMinimumHeight(35)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        
        # Global Face Swap Control Button
        self.global_face_swap_btn = QPushButton("Face Swap: ON")
        self.global_face_swap_btn.setMinimumHeight(30)
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
                font-size: 11px;
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
        
        self.processing_btn = QPushButton("All Controls")
        self.processing_btn.setMinimumHeight(30)
        self.processing_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        # Stack buttons vertically with minimal spacing
        for btn in [self.stream_btn, self.record_btn, self.global_face_swap_btn, self.processing_btn]:
            controls_layout.addWidget(btn)
        
        controls_layout.addStretch()
        controls_group.setLayout(controls_layout)
        
        # Add preview and controls to top section with better proportions
        top_layout.addWidget(preview_group, 4)  # 80% of space
        top_layout.addWidget(controls_group, 1)  # 20% of space
        
        top_section.setLayout(top_layout)
        
        # Bottom section: Viewers (collapsible)
        viewers_section = self.create_collapsible_viewers_section()
        
        layout.addWidget(top_section)
        layout.addWidget(viewers_section)
        
        panel.setLayout(layout)
        return panel
    
    def create_collapsible_viewers_section(self):
        """Create collapsible viewers section"""
        content_layout = QHBoxLayout()
        
        # Add viewers with responsive sizing
        viewers = []
        
        if 'frame_viewer' in self.viewers_components:
            frame_viewer = self.viewers_components['frame_viewer']
            frame_viewer.setMinimumSize(120, 90)
            frame_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            viewers.append((frame_viewer, "Frame"))
        
        if 'face_align_viewer' in self.viewers_components:
            face_align_viewer = self.viewers_components['face_align_viewer']
            face_align_viewer.setMinimumSize(120, 90)
            face_align_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            viewers.append((face_align_viewer, "Align"))
        
        if 'face_swap_viewer' in self.viewers_components:
            face_swap_viewer = self.viewers_components['face_swap_viewer']
            face_swap_viewer.setMinimumSize(120, 90)
            face_swap_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            viewers.append((face_swap_viewer, "Swap"))
        
        if 'merged_frame_viewer' in self.viewers_components:
            merged_frame_viewer = self.viewers_components['merged_frame_viewer']
            merged_frame_viewer.setMinimumSize(240, 90)
            merged_frame_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            viewers.append((merged_frame_viewer, "Output"))
        
        # Create smart group for viewers
        if viewers:
            return QSmartCollapsibleGroup(
                title="Processing Views",
                components=viewers,
                max_visible_components=4  # Show all by default
            )
        else:
            # Fallback if no viewers available
            placeholder = QLabel("No viewers available")
            placeholder.setStyleSheet("""
                QLabel {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #cccccc;
                    font-size: 12px;
                    padding: 20px;
                }
            """)
            placeholder.setAlignment(Qt.AlignCenter)
            
            return QCollapsibleComponentWrapper(
                component=placeholder,
                title="Processing Views",
                is_opened=False
            )
        
    def create_optimized_right_panel(self):
        """Create optimized right panel with collapsible settings sections"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Create scroll area for settings
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Input & Detection Section
        input_detection_section = self.create_collapsible_input_detection()
        scroll_layout.addWidget(input_detection_section)
        
        # Face Processing Section
        face_processing_section = self.create_collapsible_face_processing()
        scroll_layout.addWidget(face_processing_section)
        
        # Output & Quality Section
        output_quality_section = self.create_collapsible_output_quality()
        scroll_layout.addWidget(output_quality_section)
        
        # Performance Section
        performance_section = self.create_collapsible_performance()
        scroll_layout.addWidget(performance_section)
        
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        panel.setLayout(layout)
        return panel
    
    def create_collapsible_input_detection(self):
        """Create collapsible section for input and detection settings"""
        components = []
        
        # Add input source components
        if 'file_source' in self.face_swap_components:
            components.append((self.face_swap_components['file_source'], "File Source"))
        if 'camera_source' in self.face_swap_components:
            components.append((self.face_swap_components['camera_source'], "Camera Source"))
        
        # Add detection components
        if 'face_detector' in self.face_swap_components:
            components.append((self.face_swap_components['face_detector'], "Face Detector"))
        if 'face_aligner' in self.face_swap_components:
            components.append((self.face_swap_components['face_aligner'], "Face Aligner"))
        
        if components:
            return QSmartCollapsibleGroup(
                title="Input & Detection",
                components=components,
                max_visible_components=2  # Show 2 by default
            )
        else:
            # Fallback if no components available
            placeholder = QLabel("Input & Detection components not available")
            placeholder.setAlignment(Qt.AlignCenter)
            return QCollapsibleComponentWrapper(
                component=placeholder,
                title="Input & Detection",
                is_opened=False
            )
    
    def create_collapsible_face_processing(self):
        """Create collapsible section for face processing settings"""
        components = []
        
        # Add face processing components
        if 'face_marker' in self.face_swap_components:
            components.append((self.face_swap_components['face_marker'], "Face Marker"))
        if 'face_animator' in self.face_swap_components:
            components.append((self.face_swap_components['face_animator'], "Face Animator"))
        if 'face_swap_insight' in self.face_swap_components:
            components.append((self.face_swap_components['face_swap_insight'], "Face Swap Insight"))
        if 'face_swap_dfm' in self.face_swap_components:
            components.append((self.face_swap_components['face_swap_dfm'], "Face Swap DFM"))
        
        if components:
            return QSmartCollapsibleGroup(
                title="Face Processing",
                components=components,
                max_visible_components=2  # Show 2 by default
            )
        else:
            # Fallback if no components available
            placeholder = QLabel("Face Processing components not available")
            placeholder.setAlignment(Qt.AlignCenter)
            return QCollapsibleComponentWrapper(
                component=placeholder,
                title="Face Processing",
                is_opened=False
            )
    
    def create_collapsible_output_quality(self):
        """Create collapsible section for output and quality settings"""
        components = []
        
        # Add frame processing components
        if 'frame_adjuster' in self.face_swap_components:
            components.append((self.face_swap_components['frame_adjuster'], "Frame Adjuster"))
        if 'face_merger' in self.face_swap_components:
            components.append((self.face_swap_components['face_merger'], "Face Merger"))
        if 'stream_output' in self.face_swap_components:
            components.append((self.face_swap_components['stream_output'], "Stream Output"))
        
        if components:
            return QSmartCollapsibleGroup(
                title="Output & Quality",
                components=components,
                max_visible_components=2  # Show 2 by default
            )
        else:
            # Fallback if no components available
            placeholder = QLabel("Output & Quality components not available")
            placeholder.setAlignment(Qt.AlignCenter)
            return QCollapsibleComponentWrapper(
                component=placeholder,
                title="Output & Quality",
                is_opened=False
            )
    
    def create_collapsible_performance(self):
        """Create collapsible section for performance settings"""
        # Create performance controls
        performance_widget = QWidget()
        performance_layout = QVBoxLayout()
        
        # Performance presets
        presets_group = QGroupBox("Performance Presets")
        presets_layout = QHBoxLayout()
        
        ultra_fast_btn = QPushButton("Ultra Fast")
        fast_btn = QPushButton("Fast")
        balanced_btn = QPushButton("Balanced")
        quality_btn = QPushButton("Quality")
        
        for btn in [ultra_fast_btn, fast_btn, balanced_btn, quality_btn]:
            btn.setMaximumHeight(25)
            presets_layout.addWidget(btn)
        
        presets_group.setLayout(presets_layout)
        performance_layout.addWidget(presets_group)
        
        # Performance metrics
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QVBoxLayout()
        
        self.fps_label = QLabel("FPS: 0.0")
        self.memory_label = QLabel("Memory: 0 MB")
        self.cpu_label = QLabel("CPU: 0%")
        
        for label in [self.fps_label, self.memory_label, self.cpu_label]:
            metrics_layout.addWidget(label)
        
        metrics_group.setLayout(metrics_layout)
        performance_layout.addWidget(metrics_group)
        
        performance_layout.addStretch()
        performance_widget.setLayout(performance_layout)
        
        return QCollapsibleComponentWrapper(
            component=performance_widget,
            title="Performance & Advanced",
            is_opened=False
        )
        
    def setup_styles(self):
        """Setup the optimized OBS Studio-like dark theme"""
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
            
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 3px;
            }
            
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #303030;
            }
            
            QListWidget::item:selected {
                background-color: #2196F3;
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
        """)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.processing_btn.clicked.connect(self.open_processing_window)
        
        # Connect global face swap control
        self.global_face_swap_btn.toggled.connect(self.on_global_face_swap_toggled)
        
        # Connect voice changer controls
        if hasattr(self, 'voice_changer_widget'):
            self.voice_changer_widget.enabled_changed.connect(self.on_voice_changer_toggled)
            self.voice_changer_widget.effect_changed.connect(self.on_voice_effect_changed)
            self.voice_changer_widget.pitch_changed.connect(self.on_pitch_changed)
            self.voice_changer_widget.echo_changed.connect(self.on_echo_changed)
        
    def open_processing_window(self):
        """Open the processing window"""
        from .QProcessingWindow import QProcessingWindow
        self.processing_window = QProcessingWindow(self.face_swap_components, self)
        self.processing_window.show()
    
    # Voice changer event handlers
    def apply_voice_preset(self, effect_name):
        """Apply a voice changer preset"""
        if hasattr(self, 'voice_changer_widget'):
            self.voice_changer_widget.apply_preset(effect_name)
    
    def on_voice_changer_toggled(self, enabled):
        """Handle voice changer enable/disable"""
        print(f"Voice changer {'enabled' if enabled else 'disabled'}")
        # TODO: Connect to actual voice changer backend
    
    def on_voice_effect_changed(self, effect_name):
        """Handle voice effect selection change"""
        print(f"Voice effect changed to: {effect_name}")
        # TODO: Connect to actual voice changer backend
    
    def on_pitch_changed(self, value):
        """Handle pitch slider change"""
        print(f"Pitch changed to: {value}")
        # TODO: Connect to actual voice changer backend
    
    def on_echo_changed(self, value):
        """Handle echo slider change"""
        print(f"Echo delay changed to: {value}")
        # TODO: Connect to actual voice changer backend
    
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
    
    def get_face_swap_components_status(self):
        """Get the current status of all face swap components"""
        if not self.face_swap_components:
            return {}
        
        status = {}
        components_to_check = [
            'face_detector', 'face_marker', 'face_aligner', 
            'face_animator', 'face_swap_insight', 'face_swap_dfm',
            'frame_adjuster', 'face_merger'
        ]
        
        for component_name in components_to_check:
            if component_name in self.face_swap_components:
                component = self.face_swap_components[component_name]
                try:
                    # Check if component has a backend and if it's running
                    if hasattr(component, '_backend'):
                        backend = component._backend
                        if hasattr(backend, 'is_started'):
                            status[component_name] = backend.is_started()
                        elif hasattr(backend, 'is_running'):
                            status[component_name] = backend.is_running()
                        else:
                            status[component_name] = True  # Assume enabled if we can't check
                    else:
                        status[component_name] = True  # Assume enabled if no backend
                except Exception as e:
                    print(f"Error checking status of {component_name}: {e}")
                    status[component_name] = False
        
        return status
        
    def closeEvent(self, event):
        """Handle window close event"""
        if hasattr(self, 'processing_window') and self.processing_window:
            self.processing_window.close()
        event.accept() 