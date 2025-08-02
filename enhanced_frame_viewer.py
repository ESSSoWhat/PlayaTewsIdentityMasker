#!/usr/bin/env python3
"""
Enhanced Frame Viewer for PlayaTewsIdentityMasker
Fixes camera preview display issues
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

class EnhancedFrameViewer(QWidget):
    """Enhanced frame viewer with proper camera frame display"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_frame = None
        self.camera_config = None
        self.load_camera_config()
        
        # Setup timer for frame updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_frame)
        self.update_timer.start(33)  # ~30 FPS
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        
        # Frame display label
        self.frame_label = QLabel("Camera Preview")
        self.frame_label.setAlignment(Qt.AlignCenter)
        self.frame_label.setMinimumSize(640, 480)
        self.frame_label.setStyleSheet("""
            QLabel {
                border: 2px solid #333;
                background-color: #000;
                color: #666;
                font-size: 16px;
            }
        """)
        self.frame_label.setText("No camera feed\nCamera will display here when active")
        layout.addWidget(self.frame_label)
    
    def load_camera_config(self):
        """Load camera configuration"""
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
    
    def set_frame(self, frame):
        """Set the current frame to display"""
        if frame is not None:
            self.current_frame = frame.copy()
    
    def update_frame(self):
        """Update the frame display"""
        if self.current_frame is not None:
            try:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                
                # Get frame dimensions
                height, width, channel = rgb_frame.shape
                bytes_per_line = 3 * width
                
                # Create QImage
                q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                
                # Create pixmap and scale to fit
                pixmap = QPixmap.fromImage(q_image)
                scaled_pixmap = pixmap.scaled(self.frame_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # Display in label
                self.frame_label.setPixmap(scaled_pixmap)
                
            except Exception as e:
                print(f"Frame display error: {e}")
    
    def clear(self):
        """Clear the frame display"""
        self.current_frame = None
        self.frame_label.setText("No camera feed\nCamera will display here when active")

# Usage example:
# viewer = EnhancedFrameViewer()
# viewer.set_frame(camera_frame)
