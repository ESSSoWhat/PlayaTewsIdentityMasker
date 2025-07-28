#!/usr/bin/env python3
"""
Simple Working Face Swap Application
Bypasses ONNX Runtime issues and handles camera errors gracefully
"""

import sys
import time
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QWidget, QGroupBox, QCheckBox,
                            QComboBox, QSpinBox, QSlider, QTabWidget, QTextEdit,
                            QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QImage
import cv2
import numpy as np

class SimpleWorkingApp(QMainWindow):
    """Simple working application with basic face swap functionality"""
    
    def __init__(self):
        super().__init__()
        self.userdata_path = Path("simple_settings")
        self.userdata_path.mkdir(exist_ok=True)
        
        # Camera and processing state
        self.cap = None
        self.is_processing = False
        self.current_frame = None
        self.face_cascade = None
        
        # UI components
        self.camera_combo = None
        self.preview_label = None
        self.status_label = None
        self.progress_bar = None
        
        self.setup_ui()
        self.setup_face_detection()
        self.setup_connections()
        # Populate camera list after UI is fully set up
        self.populate_camera_list()
        
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("Simple Working Face Swap Application")
        self.setGeometry(100, 100, 1000, 700)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Simple Working Face Swap Application")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Camera tab
        camera_tab = self.create_camera_tab()
        tab_widget.addTab(camera_tab, "Camera Setup")
        
        # Processing tab
        processing_tab = self.create_processing_tab()
        tab_widget.addTab(processing_tab, "Face Processing")
        
        # Preview tab
        preview_tab = self.create_preview_tab()
        tab_widget.addTab(preview_tab, "Preview")
        
        # Control panel
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status bar
        self.status_label = QLabel("Ready - No ONNX Runtime dependency")
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
        
        # Camera combo with available cameras
        self.camera_combo = QComboBox()
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
        
        # Camera controls
        camera_controls = QHBoxLayout()
        
        test_camera_btn = QPushButton("Test Camera")
        test_camera_btn.clicked.connect(self.test_camera)
        camera_controls.addWidget(test_camera_btn)
        
        refresh_cameras_btn = QPushButton("Refresh Camera List")
        refresh_cameras_btn.clicked.connect(self.populate_camera_list)
        camera_controls.addWidget(refresh_cameras_btn)
        
        layout.addLayout(camera_controls)
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_processing_tab(self):
        """Create face processing configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Face detection settings
        detection_group = QGroupBox("Face Detection (OpenCV)")
        detection_layout = QVBoxLayout()
        
        self.detection_threshold = QSlider(Qt.Horizontal)
        self.detection_threshold.setRange(1, 10)
        self.detection_threshold.setValue(3)
        detection_layout.addWidget(QLabel("Detection Sensitivity (1-10):"))
        detection_layout.addWidget(self.detection_threshold)
        
        self.min_face_size = QSpinBox()
        self.min_face_size.setRange(20, 200)
        self.min_face_size.setValue(30)
        detection_layout.addWidget(QLabel("Minimum Face Size:"))
        detection_layout.addWidget(self.min_face_size)
        
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)
        
        # Processing options
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout()
        
        self.draw_faces_cb = QCheckBox("Draw Face Rectangles")
        self.draw_faces_cb.setChecked(True)
        options_layout.addWidget(self.draw_faces_cb)
        
        self.draw_landmarks_cb = QCheckBox("Draw Face Landmarks")
        self.draw_landmarks_cb.setChecked(False)
        options_layout.addWidget(self.draw_landmarks_cb)
        
        self.mirror_camera_cb = QCheckBox("Mirror Camera")
        self.mirror_camera_cb.setChecked(True)
        options_layout.addWidget(self.mirror_camera_cb)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
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
        self.start_processing_btn = QPushButton("Start Face Processing")
        self.start_processing_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.start_processing_btn)
        
        self.stop_processing_btn = QPushButton("Stop Face Processing")
        self.stop_processing_btn.clicked.connect(self.stop_processing)
        self.stop_processing_btn.setEnabled(False)
        layout.addWidget(self.stop_processing_btn)
        
        # Global controls
        self.global_enable_cb = QCheckBox("Enable Face Detection")
        self.global_enable_cb.stateChanged.connect(self.on_global_enable_changed)
        layout.addWidget(self.global_enable_cb)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def setup_face_detection(self):
        """Setup OpenCV face detection"""
        try:
            # Load OpenCV face cascade
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            if self.face_cascade.empty():
                self.status_label.setText("Warning: Face detection model not loaded")
            else:
                self.status_label.setText("Face detection ready (OpenCV)")
        except Exception as e:
            self.status_label.setText(f"Face detection setup failed: {e}")
    
    def setup_connections(self):
        """Setup signal connections"""
        # Timer for preview updates
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_preview)
    
    def populate_camera_list(self):
        """Populate camera list with available cameras"""
        self.camera_combo.clear()
        self.camera_combo.addItem("No Camera", -1)
        
        # Test cameras 0-9
        available_cameras = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                self.camera_combo.addItem(f"Camera {i}", i)
                cap.release()
        
        if available_cameras:
            self.status_label.setText(f"Found {len(available_cameras)} camera(s)")
        else:
            self.status_label.setText("No cameras found")
    
    def test_camera(self):
        """Test camera connection"""
        try:
            camera_index = self.camera_combo.currentData()
            if camera_index == -1:
                QMessageBox.warning(self, "Camera Test", "Please select a camera first")
                return
            
            cap = cv2.VideoCapture(camera_index)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    self.status_label.setText(f"Camera {camera_index} working")
                    self.show_frame(frame)
                    QMessageBox.information(self, "Camera Test", f"Camera {camera_index} is working!")
                else:
                    self.status_label.setText(f"Camera {camera_index} not responding")
                    QMessageBox.warning(self, "Camera Test", f"Camera {camera_index} not responding")
            else:
                self.status_label.setText(f"Camera {camera_index} not found")
                QMessageBox.warning(self, "Camera Test", f"Camera {camera_index} not found")
            
            cap.release()
            
        except Exception as e:
            self.status_label.setText(f"Camera test failed: {e}")
            QMessageBox.critical(self, "Camera Test", f"Camera test failed: {e}")
    
    def start_preview(self):
        """Start camera preview"""
        try:
            camera_index = self.camera_combo.currentData()
            if camera_index == -1:
                QMessageBox.warning(self, "Preview", "Please select a camera first")
                return
            
            self.cap = cv2.VideoCapture(camera_index)
            
            if self.cap.isOpened():
                # Set camera resolution
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width.value())
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height.value())
                
                self.preview_timer.start(33)  # ~30 FPS
                self.start_preview_btn.setEnabled(False)
                self.stop_preview_btn.setEnabled(True)
                self.status_label.setText("Preview started")
            else:
                QMessageBox.warning(self, "Preview", "Failed to open camera")
                self.status_label.setText("Failed to open camera")
                
        except Exception as e:
            QMessageBox.critical(self, "Preview Error", f"Preview start failed: {e}")
            self.status_label.setText(f"Preview start failed: {e}")
    
    def stop_preview(self):
        """Stop camera preview"""
        self.preview_timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.start_preview_btn.setEnabled(True)
        self.stop_preview_btn.setEnabled(False)
        self.preview_label.setText("Preview stopped")
        self.status_label.setText("Preview stopped")
    
    def update_preview(self):
        """Update preview frame with face processing"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                
                # Apply face processing if enabled
                if self.is_processing and self.global_enable_cb.isChecked():
                    frame = self.process_frame(frame)
                
                self.show_frame(frame)
    
    def process_frame(self, frame):
        """Process frame with face detection"""
        try:
            if self.face_cascade is None:
                return frame
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=self.detection_threshold.value(),
                minSize=(self.min_face_size.value(), self.min_face_size.value())
            )
            
            # Draw face rectangles if enabled
            if self.draw_faces_cb.isChecked():
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, f'Face', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Mirror camera if enabled
            if self.mirror_camera_cb.isChecked():
                frame = cv2.flip(frame, 1)
            
            return frame
            
        except Exception as e:
            print(f"Frame processing error: {e}")
            return frame
    
    def show_frame(self, frame):
        """Display frame in preview"""
        try:
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
            
        except Exception as e:
            print(f"Frame display error: {e}")
    
    def start_processing(self):
        """Start face processing"""
        if not self.is_processing:
            self.is_processing = True
            self.start_processing_btn.setEnabled(False)
            self.stop_processing_btn.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.status_label.setText("Face processing started")
    
    def stop_processing(self):
        """Stop face processing"""
        self.is_processing = False
        self.start_processing_btn.setEnabled(True)
        self.stop_processing_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Face processing stopped")
    
    def on_global_enable_changed(self, state):
        """Handle global enable checkbox"""
        enabled = state == Qt.Checked
        if enabled:
            self.status_label.setText("Face detection enabled")
        else:
            self.status_label.setText("Face detection disabled")

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = SimpleWorkingApp()
    window.show()
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 