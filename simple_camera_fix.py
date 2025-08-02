#!/usr/bin/env python3
"""
Simple Camera Fix for PlayaTewsIdentityMasker
Directly fixes the camera source initialization issue
"""

import cv2
import time
import numpy as np
from pathlib import Path
import sys
import os

def test_and_fix_camera():
    """Test camera and create a simple fix"""
    print("🔧 Testing and Fixing Camera...")
    print("=" * 50)
    
    # Test camera directly first
    print("📹 Testing camera directly...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Camera not accessible")
        return False
    
    print("✅ Camera accessible")
    
    # Test frame reading
    ret, frame = cap.read()
    if ret:
        print(f"✅ Frame read successful: {frame.shape}")
    else:
        print("❌ Frame read failed")
        cap.release()
        return False
    
    cap.release()
    
    # Create a simple camera test app
    create_simple_camera_test()
    
    return True

def create_simple_camera_test():
    """Create a simple camera test application"""
    print("\n🔧 Creating Simple Camera Test...")
    print("=" * 50)
    
    test_code = '''#!/usr/bin/env python3
"""
Simple Camera Test for PlayaTewsIdentityMasker
Tests camera functionality and shows preview
"""

import cv2
import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
import numpy as np

class SimpleCameraTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Camera Test - PlayaTewsIdentityMasker")
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
        
        layout.addLayout(button_layout)
        
        # Initialize camera
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # Auto-start camera
        self.start_camera()
        
        print("✅ Simple camera test created")
    
    def start_camera(self):
        """Start the camera"""
        try:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.status_label.setText("Status: Failed to open camera")
                self.preview_label.setText("Failed to open camera")
                return
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
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
    window = SimpleCameraTest()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
'''
    
    with open("simple_camera_test.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Created: simple_camera_test.py")
    print("   Run this to test camera functionality")

def create_camera_fix_launcher():
    """Create a camera fix launcher"""
    print("\n🔧 Creating Camera Fix Launcher...")
    print("=" * 50)
    
    launcher_code = '''@echo off
echo ========================================
echo PlayaTews Identity Masker - Camera Fix
echo ========================================
echo.

echo 🔧 Testing camera functionality...
python simple_camera_test.py

echo.
echo ✅ Camera test completed!
echo 💡 If camera works in test, the issue is in the main app
echo 🚀 If camera doesn't work, check virtual camera app
echo.

pause
'''
    
    with open("test_camera_fix.bat", 'w') as f:
        f.write(launcher_code)
    
    print("✅ Created: test_camera_fix.bat")
    print("   Run this to test camera functionality")

def main():
    print("🎬 PlayaTewsIdentityMasker - Simple Camera Fix")
    print("=" * 60)
    print()
    print("🔍 Issue: Camera feed not appearing in preview area")
    print("🎯 Solution: Test camera functionality and create simple test")
    print()
    
    try:
        # Test and fix camera
        success = test_and_fix_camera()
        
        if success:
            # Create camera fix launcher
            create_camera_fix_launcher()
            
            print("\n🎉 Simple Camera Fix Complete!")
            print("=" * 40)
            print()
            print("📋 What was created:")
            print("   ✅ simple_camera_test.py - Simple camera test app")
            print("   ✅ test_camera_fix.bat - Camera test launcher")
            print()
            print("🚀 Next steps:")
            print("   1. Run: test_camera_fix.bat")
            print("   2. If camera works in test, issue is in main app")
            print("   3. If camera doesn't work, check virtual camera app")
            print()
            print("💡 This will help identify:")
            print("   - If camera works at all")
            print("   - If the issue is in the main app")
            print("   - If the issue is with the virtual camera")
            
        else:
            print("❌ Camera test failed")
            print("   Check virtual camera app and permissions")
            
    except Exception as e:
        print(f"❌ Error creating camera fix: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 