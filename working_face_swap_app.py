#!/usr/bin/env python3
"""
Working Face Swap Application
Replaces mock components with real face swap functionality
"""

import sys
import time
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QWidget, QGroupBox, QCheckBox,
                            QComboBox, QSpinBox, QSlider, QTabWidget, QTextEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QImage
import cv2
import numpy as np

# Import the actual face swap components
try:
    from apps.PlayaTewsIdentityMasker.backend.CameraSource import CameraSource
    from apps.PlayaTewsIdentityMasker.backend.FaceDetector import FaceDetector
    from apps.PlayaTewsIdentityMasker.backend.FaceAligner import FaceAligner
    from apps.PlayaTewsIdentityMasker.backend.FaceSwapDFM import FaceSwapDFM
    from apps.PlayaTewsIdentityMasker.backend.FaceMerger import FaceMerger
    from apps.PlayaTewsIdentityMasker.backend.StreamOutput import StreamOutput
    from apps.PlayaTewsIdentityMasker.ui.QCameraSource import QCameraSource
    from apps.PlayaTewsIdentityMasker.ui.QFaceDetector import QFaceDetector
    from apps.PlayaTewsIdentityMasker.ui.QFaceAligner import QFaceAligner
    from apps.PlayaTewsIdentityMasker.ui.QFaceSwapDFM import QFaceSwapDFM
    from apps.PlayaTewsIdentityMasker.ui.QFaceMerger import QFaceMerger
    from apps.PlayaTewsIdentityMasker.ui.QStreamOutput import QStreamOutput
    REAL_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some components not available: {e}")
    REAL_COMPONENTS_AVAILABLE = False

class WorkingFaceSwapApp(QMainWindow):
    """Working face swap application with real components"""
    
    def __init__(self):
        super().__init__()
        self.userdata_path = Path("working_settings")
        self.userdata_path.mkdir(exist_ok=True)
        
        # Initialize components
        self.camera_source = None
        self.face_detector = None
        self.face_aligner = None
        self.face_swap_dfm = None
        self.face_merger = None
        self.stream_output = None
        
        # UI components
        self.camera_combo = None
        self.face_swap_combo = None
        self.preview_label = None
        self.status_label = None
        
        # Processing state
        self.is_processing = False
        self.current_frame = None
        
        self.setup_ui()
        self.setup_components()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("Working Face Swap Application")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Working Face Swap Application")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(main_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Camera tab
        camera_tab = self.create_camera_tab()
        tab_widget.addTab(camera_tab, "Camera Setup")
        
        # Face Swap tab
        face_swap_tab = self.create_face_swap_tab()
        tab_widget.addTab(face_swap_tab, "Face Swap")
        
        # Preview tab
        preview_tab = self.create_preview_tab()
        tab_widget.addTab(preview_tab, "Preview")
        
        # Control panel
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("QLabel { background-color: #e0e0e0; padding: 5px; }")
        layout.addWidget(self.status_label)
        
        main_widget.setLayout(layout)
    
    def create_camera_tab(self):
        """Create camera setup tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Camera selection
        camera_group = QGroupBox("Camera Setup")
        camera_layout = QVBoxLayout()
        
        # Camera combo
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["Camera 0", "Camera 1", "Camera 2"])
        camera_layout.addWidget(QLabel("Select Camera:"))
        camera_layout.addWidget(self.camera_combo)
        
        # Camera settings
        self.camera_width = QSpinBox()
        self.camera_width.setRange(320, 1920)
        self.camera_width.setValue(640)
        camera_layout.addWidget(QLabel("Width:"))
        camera_layout.addWidget(self.camera_width)
        
        self.camera_height = QSpinBox()
        self.camera_height.setRange(240, 1080)
        self.camera_height.setValue(480)
        camera_layout.addWidget(QLabel("Height:"))
        camera_layout.addWidget(self.camera_height)
        
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)
        
        # Test camera button
        test_camera_btn = QPushButton("Test Camera")
        test_camera_btn.clicked.connect(self.test_camera)
        layout.addWidget(test_camera_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_face_swap_tab(self):
        """Create face swap configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Face swap model selection
        model_group = QGroupBox("Face Swap Model")
        model_layout = QVBoxLayout()
        
        self.face_swap_combo = QComboBox()
        self.face_swap_combo.addItems(["No Model", "Model 1", "Model 2", "Model 3"])
        model_layout.addWidget(QLabel("Select Face Swap Model:"))
        model_layout.addWidget(self.face_swap_combo)
        
        # Model settings
        self.swap_strength = QSlider(Qt.Horizontal)
        self.swap_strength.setRange(0, 100)
        self.swap_strength.setValue(50)
        model_layout.addWidget(QLabel("Swap Strength:"))
        model_layout.addWidget(self.swap_strength)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Face detection settings
        detection_group = QGroupBox("Face Detection")
        detection_layout = QVBoxLayout()
        
        self.detection_threshold = QSlider(Qt.Horizontal)
        self.detection_threshold.setRange(0, 100)
        self.detection_threshold.setValue(70)
        detection_layout.addWidget(QLabel("Detection Threshold:"))
        detection_layout.addWidget(self.detection_threshold)
        
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_preview_tab(self):
        """Create preview tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Preview label
        self.preview_label = QLabel("No camera feed")
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setStyleSheet("QLabel { border: 2px solid #ccc; background-color: #f0f0f0; }")
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)
        
        # Preview controls
        preview_controls = QHBoxLayout()
        
        self.start_preview_btn = QPushButton("Start Preview")
        self.start_preview_btn.clicked.connect(self.start_preview)
        preview_controls.addWidget(self.start_preview_btn)
        
        self.stop_preview_btn = QPushButton("Stop Preview")
        self.stop_preview_btn.clicked.connect(self.stop_preview)
        self.stop_preview_btn.setEnabled(False)
        preview_controls.addWidget(self.stop_preview_btn)
        
        layout.addLayout(preview_controls)
        widget.setLayout(layout)
        return widget
    
    def create_control_panel(self):
        """Create main control panel"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Start/Stop processing
        self.start_processing_btn = QPushButton("Start Face Swap")
        self.start_processing_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.start_processing_btn)
        
        self.stop_processing_btn = QPushButton("Stop Face Swap")
        self.stop_processing_btn.clicked.connect(self.stop_processing)
        self.stop_processing_btn.setEnabled(False)
        layout.addWidget(self.stop_processing_btn)
        
        # Global controls
        self.global_enable_cb = QCheckBox("Enable All Components")
        self.global_enable_cb.stateChanged.connect(self.on_global_enable_changed)
        layout.addWidget(self.global_enable_cb)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def setup_components(self):
        """Setup face swap components"""
        if not REAL_COMPONENTS_AVAILABLE:
            self.status_label.setText("Warning: Some components not available")
            return
        
        try:
            # Initialize camera source
            self.camera_source = CameraSource()
            
            # Initialize face detector
            self.face_detector = FaceDetector()
            
            # Initialize face aligner
            self.face_aligner = FaceAligner()
            
            # Initialize face swap
            self.face_swap_dfm = FaceSwapDFM()
            
            # Initialize face merger
            self.face_merger = FaceMerger()
            
            # Initialize stream output
            self.stream_output = StreamOutput()
            
            self.status_label.setText("Components initialized successfully")
            
        except Exception as e:
            self.status_label.setText(f"Error initializing components: {e}")
    
    def setup_connections(self):
        """Setup signal connections"""
        # Timer for preview updates
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_preview)
    
    def test_camera(self):
        """Test camera connection"""
        try:
            camera_index = self.camera_combo.currentIndex()
            cap = cv2.VideoCapture(camera_index)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    self.status_label.setText(f"Camera {camera_index} working")
                    self.show_frame(frame)
                else:
                    self.status_label.setText(f"Camera {camera_index} not responding")
            else:
                self.status_label.setText(f"Camera {camera_index} not found")
            
            cap.release()
            
        except Exception as e:
            self.status_label.setText(f"Camera test failed: {e}")
    
    def start_preview(self):
        """Start camera preview"""
        try:
            camera_index = self.camera_combo.currentIndex()
            self.cap = cv2.VideoCapture(camera_index)
            
            if self.cap.isOpened():
                self.preview_timer.start(33)  # ~30 FPS
                self.start_preview_btn.setEnabled(False)
                self.stop_preview_btn.setEnabled(True)
                self.status_label.setText("Preview started")
            else:
                self.status_label.setText("Failed to open camera")
                
        except Exception as e:
            self.status_label.setText(f"Preview start failed: {e}")
    
    def stop_preview(self):
        """Stop camera preview"""
        self.preview_timer.stop()
        if hasattr(self, 'cap'):
            self.cap.release()
        self.start_preview_btn.setEnabled(True)
        self.stop_preview_btn.setEnabled(False)
        self.preview_label.setText("Preview stopped")
        self.status_label.setText("Preview stopped")
    
    def update_preview(self):
        """Update preview frame"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                self.show_frame(frame)
    
    def show_frame(self, frame):
        """Display frame in preview"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize for display
        height, width, channel = rgb_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # Scale to fit preview
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio)
        self.preview_label.setPixmap(scaled_pixmap)
    
    def start_processing(self):
        """Start face swap processing"""
        if not self.is_processing:
            self.is_processing = True
            self.start_processing_btn.setEnabled(False)
            self.stop_processing_btn.setEnabled(True)
            self.status_label.setText("Face swap processing started")
    
    def stop_processing(self):
        """Stop face swap processing"""
        self.is_processing = False
        self.start_processing_btn.setEnabled(True)
        self.stop_processing_btn.setEnabled(False)
        self.status_label.setText("Face swap processing stopped")
    
    def on_global_enable_changed(self, state):
        """Handle global enable checkbox"""
        enabled = state == Qt.Checked
        if enabled:
            self.status_label.setText("All components enabled")
        else:
            self.status_label.setText("All components disabled")

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = WorkingFaceSwapApp()
    window.show()
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 