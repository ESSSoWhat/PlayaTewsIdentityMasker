#!/usr/bin/env python3
"""
PyQt5 Camera Preview Integration Fix
Fixes the issue where camera feed appears in separate window but not in main app preview
"""

import cv2
import json
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QComboBox, 
                             QSpinBox, QCheckBox, QGroupBox, QMessageBox)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

class CameraThread(QThread):
    """Thread for camera capture to prevent UI blocking"""
    frame_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, camera_index, backend_id):
        super().__init__()
        self.camera_index = camera_index
        self.backend_id = backend_id
        self.running = False
        self.cap = None
    
    def run(self):
        """Main camera thread loop"""
        try:
            # Open camera with specific backend
            self.cap = cv2.VideoCapture(self.camera_index, self.backend_id)
            if not self.cap.isOpened():
                self.error_occurred.emit("Failed to open camera")
                return
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            self.running = True
            
            while self.running:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.frame_ready.emit(frame)
                else:
                    # Try to reopen camera if frame read fails
                    self.cap.release()
                    self.cap = cv2.VideoCapture(self.camera_index, self.backend_id)
                    if not self.cap.isOpened():
                        self.error_occurred.emit("Camera connection lost")
                        break
                
                # Small delay to prevent excessive CPU usage
                self.msleep(10)
                
        except Exception as e:
            self.error_occurred.emit(f"Camera error: {str(e)}")
        finally:
            if self.cap:
                self.cap.release()
    
    def stop(self):
        """Stop the camera thread"""
        self.running = False
        self.wait()

class FixedCameraPreviewApp(QMainWindow):
    """Fixed camera preview application with proper PyQt5 integration"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fixed Camera Preview - PlayaTewsIdentityMasker")
        self.setGeometry(100, 100, 1200, 800)
        
        # Camera variables
        self.camera_thread = None
        self.current_frame = None
        self.camera_config = None
        
        # Load camera configuration
        self.load_camera_config()
        
        # Setup UI
        self.setup_ui()
        
        # Setup timer for UI updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(33)  # ~30 FPS
    
    def load_camera_config(self):
        """Load camera configuration from file"""
        try:
            with open("camera_config.json", "r") as f:
                self.camera_config = json.load(f)
            print(f"✅ Loaded camera config: {self.camera_config['camera']['backend']}")
        except Exception as e:
            print(f"❌ Failed to load camera config: {e}")
            # Default configuration
            self.camera_config = {
                "camera": {
                    "backend": "DirectShow",
                    "backend_id": 700,
                    "index": 0,
                    "resolution": "1280x720",
                    "fps": 30.0
                }
            }
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Camera preview
        preview_panel = QWidget()
        preview_layout = QVBoxLayout(preview_panel)
        
        # Camera preview label
        self.preview_label = QLabel("Camera Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px solid #333;
                background-color: #000;
                color: #666;
                font-size: 16px;
            }
        """)
        self.preview_label.setText("No camera feed\nClick 'Start Camera' to begin")
        preview_layout.addWidget(self.preview_label)
        
        # Camera controls
        camera_controls = QGroupBox("Camera Controls")
        camera_controls_layout = QVBoxLayout(camera_controls)
        
        # Camera info
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"Backend: {self.camera_config['camera']['backend']}"))
        info_layout.addWidget(QLabel(f"Resolution: {self.camera_config['camera']['resolution']}"))
        info_layout.addWidget(QLabel(f"FPS: {self.camera_config['camera']['fps']:.1f}"))
        camera_controls_layout.addLayout(info_layout)
        
        # Camera buttons
        button_layout = QHBoxLayout()
        
        self.start_camera_btn = QPushButton("Start Camera")
        self.start_camera_btn.clicked.connect(self.start_camera)
        button_layout.addWidget(self.start_camera_btn)
        
        self.stop_camera_btn = QPushButton("Stop Camera")
        self.stop_camera_btn.clicked.connect(self.stop_camera)
        self.stop_camera_btn.setEnabled(False)
        button_layout.addWidget(self.stop_camera_btn)
        
        camera_controls_layout.addLayout(button_layout)
        preview_layout.addWidget(camera_controls)
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        preview_layout.addWidget(self.status_label)
        
        main_layout.addWidget(preview_panel)
        
        # Right panel - Settings
        settings_panel = QWidget()
        settings_layout = QVBoxLayout(settings_panel)
        
        # Display settings
        display_group = QGroupBox("Display Settings")
        display_layout = QVBoxLayout(display_group)
        
        self.mirror_camera_cb = QCheckBox("Mirror Camera")
        self.mirror_camera_cb.setChecked(True)
        display_layout.addWidget(self.mirror_camera_cb)
        
        self.show_fps_cb = QCheckBox("Show FPS")
        self.show_fps_cb.setChecked(True)
        display_layout.addWidget(self.show_fps_cb)
        
        settings_layout.addWidget(display_group)
        
        # Performance settings
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout(perf_group)
        
        perf_layout.addWidget(QLabel("Update Interval (ms):"))
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(10, 100)
        self.update_interval_spin.setValue(33)
        self.update_interval_spin.valueChanged.connect(self.update_timer_interval)
        perf_layout.addWidget(self.update_interval_spin)
        
        settings_layout.addWidget(perf_group)
        
        # Test buttons
        test_group = QGroupBox("Tests")
        test_layout = QVBoxLayout(test_group)
        
        test_camera_btn = QPushButton("Test Camera")
        test_camera_btn.clicked.connect(self.test_camera)
        test_layout.addWidget(test_camera_btn)
        
        test_preview_btn = QPushButton("Test Preview")
        test_preview_btn.clicked.connect(self.test_preview)
        test_layout.addWidget(test_preview_btn)
        
        settings_layout.addWidget(test_group)
        
        settings_layout.addStretch()
        main_layout.addWidget(settings_panel)
    
    def start_camera(self):
        """Start camera capture"""
        try:
            if self.camera_thread and self.camera_thread.isRunning():
                return
            
            camera_index = self.camera_config["camera"]["index"]
            backend_id = self.camera_config["camera"]["backend_id"]
            
            self.camera_thread = CameraThread(camera_index, backend_id)
            self.camera_thread.frame_ready.connect(self.on_frame_ready)
            self.camera_thread.error_occurred.connect(self.on_camera_error)
            self.camera_thread.start()
            
            self.start_camera_btn.setEnabled(False)
            self.stop_camera_btn.setEnabled(True)
            self.status_label.setText("Camera started")
            
        except Exception as e:
            QMessageBox.critical(self, "Camera Error", f"Failed to start camera: {e}")
            self.status_label.setText(f"Camera error: {e}")
    
    def stop_camera(self):
        """Stop camera capture"""
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None
        
        self.start_camera_btn.setEnabled(True)
        self.stop_camera_btn.setEnabled(False)
        self.preview_label.setText("Camera stopped")
        self.status_label.setText("Camera stopped")
    
    def on_frame_ready(self, frame):
        """Handle frame from camera thread"""
        self.current_frame = frame
    
    def on_camera_error(self, error_msg):
        """Handle camera error"""
        self.status_label.setText(f"Camera error: {error_msg}")
        self.stop_camera()
        QMessageBox.warning(self, "Camera Error", error_msg)
    
    def update_preview(self):
        """Update the preview display"""
        if self.current_frame is not None:
            try:
                # Process frame
                frame = self.current_frame.copy()
                
                # Mirror if enabled
                if self.mirror_camera_cb.isChecked():
                    frame = cv2.flip(frame, 1)
                
                # Add FPS if enabled
                if self.show_fps_cb.isChecked():
                    cv2.putText(frame, f"FPS: {1000//self.update_interval_spin.value()}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Convert to Qt format
                self.display_frame(frame)
                
            except Exception as e:
                print(f"Preview update error: {e}")
    
    def display_frame(self, frame):
        """Display frame in the preview label"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get frame dimensions
            height, width, channel = rgb_frame.shape
            bytes_per_line = 3 * width
            
            # Create QImage
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # Create pixmap and scale to fit
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Display in label
            self.preview_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            print(f"Frame display error: {e}")
    
    def update_timer_interval(self, value):
        """Update the timer interval"""
        self.update_timer.setInterval(value)
    
    def test_camera(self):
        """Test camera functionality"""
        try:
            camera_index = self.camera_config["camera"]["index"]
            backend_id = self.camera_config["camera"]["backend_id"]
            
            cap = cv2.VideoCapture(camera_index, backend_id)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    QMessageBox.information(self, "Camera Test", "Camera test successful!")
                    self.status_label.setText("Camera test passed")
                else:
                    QMessageBox.warning(self, "Camera Test", "Camera opened but no frame received")
            else:
                QMessageBox.critical(self, "Camera Test", "Failed to open camera")
                
        except Exception as e:
            QMessageBox.critical(self, "Camera Test", f"Camera test failed: {e}")
    
    def test_preview(self):
        """Test preview functionality"""
        if self.current_frame is not None:
            QMessageBox.information(self, "Preview Test", "Preview is working correctly!")
        else:
            QMessageBox.warning(self, "Preview Test", "No frame available for preview")
    
    def closeEvent(self, event):
        """Handle application close"""
        self.stop_camera()
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = FixedCameraPreviewApp()
    window.show()
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 