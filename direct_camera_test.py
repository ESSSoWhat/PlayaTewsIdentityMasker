#!/usr/bin/env python3
"""
Direct Camera Test
Shows that camera is working and can be integrated
"""

import cv2
import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
import numpy as np

class DirectCameraTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Direct Camera Test - PlayaTewsIdentityMasker")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create preview label
        self.preview_label = QLabel("Initializing camera...")
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setStyleSheet("QLabel { border: 2px solid #ccc; background-color: #f0f0f0; }")
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)
        
        # Create status label
        self.status_label = QLabel("Status: Initializing...")
        self.status_label.setStyleSheet("QLabel { font-weight: bold; color: #333; }")
        layout.addWidget(self.status_label)
        
        # Create control buttons
        button_layout = QVBoxLayout()
        
        self.start_btn = QPushButton("Start Camera")
        self.start_btn.clicked.connect(self.start_camera)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Camera")
        self.stop_btn.clicked.connect(self.stop_camera)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.launch_app_btn = QPushButton("Launch PlayaTewsIdentityMasker")
        self.launch_app_btn.clicked.connect(self.launch_main_app)
        button_layout.addWidget(self.launch_app_btn)
        
        layout.addLayout(button_layout)
        
        # Initialize camera
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # Auto-start camera
        self.start_camera()
        
        print("✅ Direct camera test created")
    
    def start_camera(self):
        """Start the camera"""
        try:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.status_label.setText("Status: Failed to open camera")
                self.preview_label.setText("Failed to open camera")
                return
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Start timer
            self.timer.start(33)  # ~30 FPS
            
            self.status_label.setText("Status: Camera running")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            print("✅ Camera started successfully")
            
        except Exception as e:
            self.status_label.setText(f"Status: Error - {str(e)}")
            print(f"❌ Error starting camera: {e}")
    
    def stop_camera(self):
        """Stop the camera"""
        self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None
        
        self.preview_label.setText("Camera stopped")
        self.status_label.setText("Status: Camera stopped")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        print("✅ Camera stopped")
    
    def launch_main_app(self):
        """Launch the main PlayaTewsIdentityMasker app"""
        try:
            import subprocess
            subprocess.Popen([sys.executable, "working_camera_launcher.py"])
            print("✅ Launched PlayaTewsIdentityMasker")
        except Exception as e:
            print(f"❌ Error launching main app: {e}")
    
    def update_frame(self):
        """Update the frame display"""
        if self.cap is None or not self.cap.isOpened():
            return
        
        ret, frame = self.cap.read()
        if ret:
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
            
            # Update status
            self.status_label.setText(f"Status: Running - {width}x{height} @ 30 FPS")
        else:
            self.status_label.setText("Status: Failed to read frame")
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.stop_camera()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = DirectCameraTest()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
