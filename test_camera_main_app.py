#!/usr/bin/env python3
"""
Simple Camera Preview Test for Main Application
Tests if the camera preview works in the main app context
"""

import cv2
import json
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

class SimpleCameraTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Preview Test - Main App Context")
        self.setGeometry(100, 100, 800, 600)
        
        # Load camera config
        try:
            with open("camera_config.json", "r") as f:
                self.camera_config = json.load(f)
        except Exception as e:
            print(f"Failed to load camera config: {e}")
            self.camera_config = {
                "camera": {
                    "backend": "DirectShow",
                    "backend_id": 700,
                    "index": 0,
                    "resolution": "1280x720",
                    "fps": 30.0
                }
            }
        
        self.setup_ui()
        self.setup_camera()
        
    def setup_ui(self):
        """Setup the UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
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
        layout.addWidget(self.preview_label)
        
        # Control buttons
        self.start_btn = QPushButton("Start Camera")
        self.start_btn.clicked.connect(self.start_camera)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Camera")
        self.stop_btn.clicked.connect(self.stop_camera)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
    def setup_camera(self):
        """Setup camera"""
        self.cap = None
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_frame)
        
    def start_camera(self):
        """Start camera"""
        try:
            camera_index = self.camera_config["camera"]["index"]
            backend_id = self.camera_config["camera"]["backend_id"]
            
            self.cap = cv2.VideoCapture(camera_index, backend_id)
            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                
                self.camera_timer.start(33)  # ~30 FPS
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.status_label.setText("Camera started")
            else:
                self.status_label.setText("Failed to open camera")
                
        except Exception as e:
            self.status_label.setText(f"Camera error: {e}")
    
    def stop_camera(self):
        """Stop camera"""
        self.camera_timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.preview_label.setText("Camera stopped")
        self.status_label.setText("Camera stopped")
    
    def update_frame(self):
        """Update frame display"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
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
    
    def closeEvent(self, event):
        """Handle close event"""
        self.stop_camera()
        event.accept()

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    window = SimpleCameraTest()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
