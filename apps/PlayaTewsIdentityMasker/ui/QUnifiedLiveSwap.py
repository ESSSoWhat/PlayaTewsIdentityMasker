#!/usr/bin/env python3
"""
Unified LiveSwap Component
Consolidates all LiveSwap implementations into a single component
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QGroupBox as QXGroupBox
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QScrollArea as QXScrollArea
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QTabWidget as QXTabWidget
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel
from xlib.qt.widgets.QXWidget import QXWidget


class UIMode(Enum):
    TRADITIONAL = "traditional"
    OBS_STYLE = "obs_style"
    OPTIMIZED = "optimized"
    COMPACT = "compact"


class QDFMQuickAccessPanel(QXWidget):
    """Quick access panel for DFM models with last 6 used models"""

    def __init__(self, face_swap_dfm_widget):
        super().__init__()
        self.face_swap_dfm_widget = face_swap_dfm_widget
        self.dfm_buttons = []
        self.last_used_models = []

        self.setup_ui()
        self.load_last_used_models()

    def setup_ui(self):
        """Setup the DFM quick access panel"""
        layout = QVBoxLayout()

        # Title
        title = QXLabel(text="DFM Quick Access", font=QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Description
        desc = QXLabel(text="Click to switch to model", font=QFont("Arial", 9))
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        # Buttons grid
        self.buttons_layout = QGridLayout()
        self.buttons_layout.setSpacing(5)

        # Create 6 placeholder buttons
        for i in range(6):
            row = i // 2
            col = i % 2
            button = QPushButton(f"Model {i+1}")
            button.setMinimumHeight(40)
            button.setStyleSheet(
                """
                QPushButton {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                    border: 1px solid #777777;
                }
                QPushButton:pressed {
                    background-color: #1d1d1d;
                }
            """
            )
            button.clicked.connect(
                lambda checked, idx=i: self.on_model_button_clicked(idx)
            )
            self.dfm_buttons.append(button)
            self.buttons_layout.addWidget(button, row, col)

        layout.addLayout(self.buttons_layout)

        # Refresh button
        refresh_btn = QPushButton("Refresh Models")
        refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """
        )
        refresh_btn.clicked.connect(self.refresh_models)
        layout.addWidget(refresh_btn)

        layout.addStretch()
        self.setLayout(layout)

        # Set panel properties
        self.setMaximumWidth(200)
        self.setMinimumWidth(180)

    def load_last_used_models(self):
        """Load the last 6 used DFM models"""
        try:
            # This would typically load from a settings file
            # For now, we'll create placeholder models
            self.last_used_models = [
                "Model_1.dfm",
                "Model_2.dfm",
                "Model_3.dfm",
                "Model_4.dfm",
                "Model_5.dfm",
                "Model_6.dfm",
            ]
            self.update_buttons()
        except Exception as e:
            print(f"Warning: Could not load last used models: {e}")

    def update_buttons(self):
        """Update button labels with actual model names"""
        for i, button in enumerate(self.dfm_buttons):
            if i < len(self.last_used_models):
                model_name = self.last_used_models[i]
                # Truncate long names
                display_name = (
                    model_name[:15] + "..." if len(model_name) > 15 else model_name
                )
                button.setText(display_name)
                button.setToolTip(model_name)
                button.setEnabled(True)
            else:
                button.setText("Empty")
                button.setToolTip("No model loaded")
                button.setEnabled(False)

    def on_model_button_clicked(self, index):
        """Handle model button click"""
        if index < len(self.last_used_models):
            model_name = self.last_used_models[index]
            print(f"Switching to DFM model: {model_name}")

            # Try to switch the model in the face swap widget
            try:
                if hasattr(self.face_swap_dfm_widget, "switch_to_model"):
                    self.face_swap_dfm_widget.switch_to_model(model_name)
                else:
                    print("Face swap widget doesn't support model switching")
            except Exception as e:
                print(f"Error switching model: {e}")

    def refresh_models(self):
        """Refresh the list of available models"""
        print("Refreshing DFM models...")
        self.load_last_used_models()


class QUnifiedLiveSwap(QXWidget):
    """Unified LiveSwap component with multiple presentation modes"""

    def __init__(self, mode: UIMode, *ui_components):
        super().__init__()
        self.mode = mode
        self.ui_components = ui_components

        # Extract components by type
        self.extract_components()

        # Create UI based on mode
        self.setup_ui()

    def extract_components(self):
        """Extract UI components by their type"""
        self.q_file_source = None
        self.q_camera_source = None
        self.q_face_detector = None
        self.q_face_marker = None
        self.q_face_aligner = None
        self.q_face_animator = None
        self.q_face_swap_insight = None
        self.q_face_swap_dfm = None
        self.q_frame_adjuster = None
        self.q_face_merger = None
        self.q_stream_output = None
        self.q_voice_changer = None
        self.q_ds_frame_viewer = None
        self.q_ds_fa_viewer = None
        self.q_ds_fc_viewer = None
        self.q_ds_merged_frame_viewer = None

        # Map components by their class names
        for component in self.ui_components:
            class_name = component.__class__.__name__
            if class_name == "QFileSource":
                self.q_file_source = component
            elif class_name == "QCameraSource":
                self.q_camera_source = component
            elif class_name == "QFaceDetector":
                self.q_face_detector = component
            elif class_name == "QFaceMarker":
                self.q_face_marker = component
            elif class_name == "QFaceAligner":
                self.q_face_aligner = component
            elif class_name == "QFaceAnimator":
                self.q_face_animator = component
            elif class_name == "QFaceSwapInsight":
                self.q_face_swap_insight = component
            elif class_name == "QFaceSwapDFM":
                self.q_face_swap_dfm = component
            elif class_name == "QFrameAdjuster":
                self.q_frame_adjuster = component
            elif class_name == "QFaceMerger":
                self.q_face_merger = component
            elif class_name in ["QStreamOutput", "QEnhancedStreamOutput"]:
                self.q_stream_output = component
            elif class_name == "QVoiceChanger":
                self.q_voice_changer = component
            elif "FrameViewer" in class_name:
                self.q_ds_frame_viewer = component
            elif "FaceAlignViewer" in class_name:
                self.q_ds_fa_viewer = component
            elif "FaceSwapViewer" in class_name:
                self.q_ds_fc_viewer = component
            elif "MergedFrameViewer" in class_name:
                self.q_ds_merged_frame_viewer = component

    def setup_ui(self):
        """Setup UI based on selected mode"""
        if self.mode == UIMode.OBS_STYLE:
            self.setup_obs_style_layout()
        elif self.mode == UIMode.OPTIMIZED:
            self.setup_optimized_layout()
        else:
            self.setup_traditional_layout()

    def setup_obs_style_layout(self):
        """OBS-style layout with DFM quick access panel"""
        main_layout = qtx.QXHBoxLayout()

        # Left panel - DFM Quick Access and Input Sources
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)

        # Center panel - Main processing and viewers
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 1)  # Center gets most space

        # Right panel - Output and settings
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel)

        self.setLayout(main_layout)

    def create_left_panel(self):
        """Create left panel with DFM quick access and input sources"""
        panel = QXWidget()
        panel.setMaximumWidth(250)
        panel.setMinimumWidth(220)

        layout = qtx.QXVBoxLayout()

        # DFM Quick Access Panel
        if self.q_face_swap_dfm:
            dfm_panel = QDFMQuickAccessPanel(self.q_face_swap_dfm)
            layout.addWidget(dfm_panel)

        # Input Sources Group
        input_group = QXGroupBox(title="Input Sources")
        input_layout = qtx.QXVBoxLayout()

        if self.q_file_source:
            input_layout.addWidget(self.q_file_source)
        if self.q_camera_source:
            input_layout.addWidget(self.q_camera_source)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Voice Changer (if available)
        if self.q_voice_changer:
            voice_group = QXGroupBox(title="Voice Changer")
            voice_layout = qtx.QXVBoxLayout()
            voice_layout.addWidget(self.q_voice_changer)
            voice_group.setLayout(voice_layout)
            layout.addWidget(voice_group)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def create_center_panel(self):
        """Create center panel with main processing and viewers"""
        panel = QXWidget()

        # Create tab widget for better organization
        tab_widget = QXTabWidget()

        # Processing tab
        processing_tab = self.create_processing_tab()
        tab_widget.addTab(processing_tab, "Processing")

        # Viewers tab
        viewers_tab = self.create_viewers_tab()
        tab_widget.addTab(viewers_tab, "Viewers")

        panel.setLayout(qtx.QXVBoxLayout([tab_widget]))
        return panel

    def create_processing_tab(self):
        """Create processing tab with face processing components"""
        tab = QXWidget()
        layout = qtx.QXHBoxLayout()

        # Detection column
        detection_group = QXGroupBox(title="Detection")
        detection_layout = qtx.QXVBoxLayout()
        if self.q_face_detector:
            detection_layout.addWidget(self.q_face_detector)
        if self.q_face_marker:
            detection_layout.addWidget(self.q_face_marker)
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)

        # Alignment column
        alignment_group = QXGroupBox(title="Alignment")
        alignment_layout = qtx.QXVBoxLayout()
        if self.q_face_aligner:
            alignment_layout.addWidget(self.q_face_aligner)
        if self.q_face_animator:
            alignment_layout.addWidget(self.q_face_animator)
        alignment_group.setLayout(alignment_layout)
        layout.addWidget(alignment_group)

        # Face Swap column
        swap_group = QXGroupBox(title="Face Swap")
        swap_layout = qtx.QXVBoxLayout()
        if self.q_face_swap_insight:
            swap_layout.addWidget(self.q_face_swap_insight)
        if self.q_face_swap_dfm:
            swap_layout.addWidget(self.q_face_swap_dfm)
        swap_group.setLayout(swap_layout)
        layout.addWidget(swap_group)

        # Enhancement column
        enhancement_group = QXGroupBox(title="Enhancement")
        enhancement_layout = qtx.QXVBoxLayout()
        if self.q_frame_adjuster:
            enhancement_layout.addWidget(self.q_frame_adjuster)
        if self.q_face_merger:
            enhancement_layout.addWidget(self.q_face_merger)
        enhancement_group.setLayout(enhancement_layout)
        layout.addWidget(enhancement_group)

        tab.setLayout(layout)
        return tab

    def create_viewers_tab(self):
        """Create viewers tab with all preview components including enhanced output"""
        tab = QXWidget()
        layout = qtx.QXHBoxLayout()

        # Left side - Camera and processing viewers
        left_viewers = QXWidget()
        left_layout = qtx.QXVBoxLayout()

        # Add camera and processing viewers
        viewers = []
        if self.q_ds_frame_viewer:
            viewers.append(("Camera Feed", self.q_ds_frame_viewer))
        if self.q_ds_fa_viewer:
            viewers.append(("Face Align", self.q_ds_fa_viewer))
        if self.q_ds_fc_viewer:
            viewers.append(("Face Swap", self.q_ds_fc_viewer))
        if self.q_ds_merged_frame_viewer:
            viewers.append(("Merged", self.q_ds_merged_frame_viewer))

        # Create a grid layout for the viewers
        viewers_grid = qtx.QXGridLayout()
        for i, (title, viewer) in enumerate(viewers):
            row = i // 2
            col = i % 2
            group = QXGroupBox(title=title)
            group_layout = qtx.QXVBoxLayout()
            group_layout.addWidget(viewer)
            group.setLayout(group_layout)
            viewers_grid.addWidget(group, row, col)

        left_layout.addLayout(viewers_grid)
        left_viewers.setLayout(left_layout)

        # Right side - Enhanced Output Preview
        right_viewers = QXWidget()
        right_layout = qtx.QXVBoxLayout()

        # Import and create enhanced preview widget
        try:
            from .widgets.QEnhancedPreviewWidget import QEnhancedPreviewWidget
            enhanced_preview = QEnhancedPreviewWidget("Enhanced Output Preview")
            
            # Connect signals
            enhanced_preview.fullscreen_requested.connect(self.on_fullscreen_requested)
            enhanced_preview.maximize_requested.connect(self.on_maximize_requested)
            enhanced_preview.settings_requested.connect(self.on_settings_requested)
            
            # Add enhanced preview as the main display
            enhanced_group = QXGroupBox(title="🎬 Enhanced Output Preview")
            enhanced_layout = qtx.QXVBoxLayout()
            enhanced_layout.addWidget(enhanced_preview)
            enhanced_group.setLayout(enhanced_layout)
            right_layout.addWidget(enhanced_group)
            
            # Store reference for later use
            self.enhanced_preview = enhanced_preview
            
        except ImportError:
            # Fallback to original stream output if enhanced preview is not available
            if hasattr(self, "q_stream_output") and self.q_stream_output:
                enhanced_group = QXGroupBox(title="Enhanced Output Preview")
                enhanced_layout = qtx.QXVBoxLayout()
                enhanced_layout.addWidget(self.q_stream_output)
                enhanced_group.setLayout(enhanced_layout)
                right_layout.addWidget(enhanced_group)

        # Add original stream output controls below the enhanced preview
        if hasattr(self, "q_stream_output") and self.q_stream_output:
            controls_group = QXGroupBox(title="Stream Controls")
            controls_layout = qtx.QXVBoxLayout()
            controls_layout.addWidget(self.q_stream_output)
            controls_group.setLayout(controls_layout)
            right_layout.addWidget(controls_group)

        right_viewers.setLayout(right_layout)

        # Add both sides to main layout with enhanced preview getting more space
        layout.addWidget(left_viewers, 1)  # 1 part width
        layout.addWidget(right_viewers, 3)  # 3 parts width (larger for enhanced output)

        tab.setLayout(layout)
        return tab

    def create_right_panel(self):
        """Create right panel with output and settings"""
        panel = QXWidget()
        panel.setMaximumWidth(300)
        panel.setMinimumWidth(250)

        layout = qtx.QXVBoxLayout()

        # Output Group
        output_group = QXGroupBox(title="Output")
        output_layout = qtx.QXVBoxLayout()
        if self.q_stream_output:
            output_layout.addWidget(self.q_stream_output)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Settings placeholder (for future use)
        settings_group = QXGroupBox(title="Settings")
        settings_layout = qtx.QXVBoxLayout()
        settings_label = QXLabel(text="Settings panel\n(Coming soon)")
        settings_label.setAlignment(Qt.AlignCenter)
        settings_layout.addWidget(settings_label)
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def setup_optimized_layout(self):
        """Optimized layout with logical grouping"""
        main_layout = qtx.QXHBoxLayout()

        # Input Panel (File, Camera, Voice)
        input_panel = self.create_input_panel()

        # Detection Panel (Face Detector, Face Marker)
        detection_panel = self.create_detection_panel()

        # Processing Panel (Face Aligner, Face Animator, Face Swap Insight)
        processing_panel = self.create_processing_panel()

        # Enhancement Panel (Face Swap DFM, Frame Adjuster, Face Merger)
        enhancement_panel = self.create_enhancement_panel()

        # Output Panel (Stream Output)
        output_panel = self.create_output_panel()

        # Add panels to layout
        main_layout.addWidget(input_panel)
        main_layout.addWidget(detection_panel)
        main_layout.addWidget(processing_panel)
        main_layout.addWidget(enhancement_panel)
        main_layout.addWidget(output_panel)

        self.setLayout(main_layout)

    def setup_traditional_layout(self):
        """Traditional layout for backward compatibility"""
        # Simple horizontal layout with all components
        layout = qtx.QXHBoxLayout()

        for component in self.ui_components:
            if component:
                layout.addWidget(component)

        self.setLayout(layout)

    def create_input_panel(self):
        """Create input panel with File, Camera, and Voice Changer"""
        panel = QXWidget()
        layout = qtx.QXVBoxLayout()

        if self.q_file_source:
            layout.addWidget(self.q_file_source)
        if self.q_camera_source:
            layout.addWidget(self.q_camera_source)
        if self.q_voice_changer:
            layout.addWidget(self.q_voice_changer)

        panel.setLayout(layout)
        return panel

    def create_detection_panel(self):
        """Create detection panel"""
        panel = QXWidget()
        layout = qtx.QXVBoxLayout()

        if self.q_face_detector:
            layout.addWidget(self.q_face_detector)
        if self.q_face_marker:
            layout.addWidget(self.q_face_marker)

        panel.setLayout(layout)
        return panel

    def create_processing_panel(self):
        """Create processing panel"""
        panel = QXWidget()
        layout = qtx.QXVBoxLayout()

        if self.q_face_aligner:
            layout.addWidget(self.q_face_aligner)
        if self.q_face_animator:
            layout.addWidget(self.q_face_animator)
        if self.q_face_swap_insight:
            layout.addWidget(self.q_face_swap_insight)

        panel.setLayout(layout)
        return panel

    def create_enhancement_panel(self):
        """Create enhancement panel"""
        panel = QXWidget()
        layout = qtx.QXVBoxLayout()

        if self.q_face_swap_dfm:
            layout.addWidget(self.q_face_swap_dfm)
        if self.q_frame_adjuster:
            layout.addWidget(self.q_frame_adjuster)
        if self.q_face_merger:
            layout.addWidget(self.q_face_merger)

        panel.setLayout(layout)
        return panel

    def create_output_panel(self):
        """Create output panel"""
        panel = QXWidget()
        layout = qtx.QXVBoxLayout()

        if self.q_stream_output:
            layout.addWidget(self.q_stream_output)

        panel.setLayout(layout)
        return panel

    def _process_messages(self):
        """Process messages for all components"""
        for component in self.ui_components:
            if hasattr(component, "_process_messages"):
                component._process_messages()

    def _on_timer_5ms(self):
        """Handle timer events for all components"""
        for component in self.ui_components:
            if hasattr(component, "_on_timer_5ms"):
                component._on_timer_5ms()

    # Enhanced Preview Signal Handlers
    def on_fullscreen_requested(self):
        """Handle fullscreen request from enhanced preview"""
        print("🎬 Fullscreen requested from enhanced preview")
        # This would integrate with the backend to toggle fullscreen
        if hasattr(self, 'enhanced_preview'):
            self.enhanced_preview.update_status_display("🖥️ Fullscreen Mode", "#ffff00")

    def on_maximize_requested(self):
        """Handle maximize request from enhanced preview"""
        print("📺 Maximize requested from enhanced preview")
        # This would maximize the preview area
        if hasattr(self, 'enhanced_preview'):
            self.enhanced_preview.update_status_display("📺 Preview Maximized", "#00ffff")

    def on_settings_requested(self):
        """Handle settings request from enhanced preview"""
        print("⚙️ Settings requested from enhanced preview")
        # This would open settings dialog
        if hasattr(self, 'enhanced_preview'):
            self.enhanced_preview.update_status_display("⚙️ Settings Open", "#ff00ff")
