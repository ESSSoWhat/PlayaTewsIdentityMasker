#!/usr/bin/env python3
"""
Simple Face Swap Application
Works around DLL issues by using only basic OpenCV functionality
"""

import sys
import time
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QWidget, QGroupBox, QCheckBox,
                            QComboBox, QSpinBox, QSlider, QTabWidget, QTextEdit,
                            QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QImage
import cv2
import numpy as np

class SimpleFaceSwapApp(QMainWindow):
    """Simple face swap application with basic OpenCV functionality"""
    
    def __init__(self):
        super().__init__()
        self.userdata_path = Path("simple_settings")
        self.userdata_path.mkdir(exist_ok=True)
        
        # Camera and processing state
        self.cap = None
        self.is_preview_active = False
        self.is_processing = False
        self.current_frame = None
        self.face_cascade = None
        
        # UI components
        self.camera_combo = None
        self.preview_label = None
        self.status_label = None
        self.face_detection_cb = None
        
        self.setup_ui()
        self.setup_face_detection()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("Simple Face Swap Application")
        self.setGeometry(100, 100, 1000, 700)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Simple Face Swap Application")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Camera tab
        camera_tab = self.create_camera_tab()
        tab_widget.addTab(camera_tab, "Camera Setup")
        
        # Face Detection tab
        detection_tab = self.create_detection_tab()
        tab_widget.addTab(detection_tab, "Face Detection")
        
        # Preview tab
        preview_tab = self.create_preview_tab()
        tab_widget.addTab(preview_tab, "Preview")
        
        # Control panel
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Status bar
        self.status_label = QLabel("Ready - No DLL dependencies")
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
        self.camera_combo.addItems(["Camera 0", "Camera 1", "Camera 2", "Camera 3"])
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
        
        # Camera info
        info_label = QLabel("This version uses basic OpenCV without complex dependencies")
        info_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        layout.addWidget(info_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_detection_tab(self):
        """Create face detection configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Face detection settings
        detection_group = QGroupBox("Face Detection Settings")
        detection_layout = QVBoxLayout()
        
        self.face_detection_cb = QCheckBox("Enable Face Detection")
        self.face_detection_cb.setChecked(True)
        detection_layout.addWidget(self.face_detection_cb)
        
        self.detection_scale = QSlider(Qt.Horizontal)
        self.detection_scale.setRange(10, 50)
        self.detection_scale.setValue(20)
        detection_layout.addWidget(QLabel("Detection Scale Factor:"))
        detection_layout.addWidget(self.detection_scale)
        
        self.detection_neighbors = QSlider(Qt.Horizontal)
        self.detection_neighbors.setRange(1, 10)
        self.detection_neighbors.setValue(3)
        detection_layout.addWidget(QLabel("Min Neighbors:"))
        detection_layout.addWidget(self.detection_neighbors)
        
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)
        
        # Detection info
        info_label = QLabel("Uses OpenCV Haar Cascade for face detection")
        info_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        layout.addWidget(info_label)
        
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
        
        self.screenshot_btn = QPushButton("Take Screenshot")
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        preview_controls.addWidget(self.screenshot_btn)
        
        layout.addLayout(preview_controls)
        widget.setLayout(layout)
        return widget
    
    def create_control_panel(self):
        """Create main control panel"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Start/Stop processing
        self.start_processing_btn = QPushButton("Start Face Detection")
        self.start_processing_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.start_processing_btn)
        
        self.stop_processing_btn = QPushButton("Stop Face Detection")
        self.stop_processing_btn.clicked.connect(self.stop_processing)
        self.stop_processing_btn.setEnabled(False)
        layout.addWidget(self.stop_processing_btn)
        
        # Global controls
        self.global_enable_cb = QCheckBox("Enable All Features")
        self.global_enable_cb.setChecked(True)
        self.global_enable_cb.stateChanged.connect(self.on_global_enable_changed)
        layout.addWidget(self.global_enable_cb)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def setup_face_detection(self):
        """Setup face detection cascade"""
        try:
            # Load OpenCV face cascade
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            if self.face_cascade.empty():
                self.status_label.setText("Warning: Face cascade not loaded")
            else:
                self.status_label.setText("Face detection ready")
        except Exception as e:
            self.status_label.setText(f"Face detection setup failed: {e}")
    
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
                # Set camera resolution
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width.value())
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height.value())
                
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
        if self.cap:
            self.cap.release()
            self.cap = None
        self.start_preview_btn.setEnabled(True)
        self.stop_preview_btn.setEnabled(False)
        self.preview_label.setText("Preview stopped")
        self.status_label.setText("Preview stopped")
    
    def update_preview(self):
        """Update preview frame with face detection"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                
                # Apply face detection if enabled
                if self.is_processing and self.face_detection_cb.isChecked():
                    frame = self.detect_faces(frame)
                
                self.show_frame(frame)
    
    def detect_faces(self, frame):
        """Detect faces in frame"""
        if self.face_cascade is None:
            return frame
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            scale_factor = self.detection_scale.value() / 10.0
            min_neighbors = self.detection_neighbors.value()
            
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=scale_factor, 
                minNeighbors=min_neighbors,
                minSize=(30, 30)
            )
            
            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, 'Face', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Update status with face count
            if len(faces) > 0:
                self.status_label.setText(f"Detected {len(faces)} face(s)")
            
        except Exception as e:
            print(f"Face detection error: {e}")
        
        return frame
    
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
    
    def take_screenshot(self):
        """Take a screenshot of the current frame"""
        if self.current_frame is not None:
            try:
                filename, _ = QFileDialog.getSaveFileName(
                    self, "Save Screenshot", 
                    f"screenshot_{int(time.time())}.png",
                    "PNG Files (*.png);;JPEG Files (*.jpg)"
                )
                
                if filename:
                    cv2.imwrite(filename, self.current_frame)
                    self.status_label.setText(f"Screenshot saved: {filename}")
                    
            except Exception as e:
                self.status_label.setText(f"Screenshot failed: {e}")
        else:
            self.status_label.setText("No frame to capture")
    
    def start_processing(self):
        """Start face detection processing"""
        if not self.is_processing:
            self.is_processing = True
            self.start_processing_btn.setEnabled(False)
            self.stop_processing_btn.setEnabled(True)
            self.status_label.setText("Face detection processing started")
    
    def stop_processing(self):
        """Stop face detection processing"""
        self.is_processing = False
        self.start_processing_btn.setEnabled(True)
        self.stop_processing_btn.setEnabled(False)
        self.status_label.setText("Face detection processing stopped")
    
    def on_global_enable_changed(self, state):
        """Handle global enable checkbox"""
        enabled = state == Qt.Checked
        if enabled:
            self.status_label.setText("All features enabled")
        else:
            self.status_label.setText("All features disabled")

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = SimpleFaceSwapApp()
    window.show()
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 