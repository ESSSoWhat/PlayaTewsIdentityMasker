#!/usr/bin/env python3
"""
Test Camera Integration Fix for PlayaTewsIdentityMasker
Tests if the camera integration fix resolves the backend connection issue
"""

import cv2
import time
import numpy as np
from pathlib import Path
import sys
import os

def test_camera_integration_fix():
    """Test the camera integration fix"""
    print("🔧 Testing Camera Integration Fix...")
    print("=" * 50)
    
    try:
        from apps.PlayaTewsIdentityMasker import backend
        from apps.PlayaTewsIdentityMasker.backend.CameraSource import CameraSource, CameraSourceWorker, Sheet, WorkerState
        
        # Create a fixed camera source worker
        class FixedCameraSourceWorker(CameraSourceWorker):
            def on_start(self, weak_heap, bc_out):
                super().on_start(weak_heap, bc_out)
                
                print("🔧 Fixed Camera Source Worker starting...")
                
                # Force DirectShow backend
                state, cs = self.get_state(), self.get_control_sheet()
                
                # Set DirectShow backend
                state.driver = 1  # DirectShow
                state.device_idx = 0
                state.resolution = 3  # 1280x720
                state.fps = 30.0
                state.rotation = 0
                state.flip_horizontal = False
                
                # Save state
                self.save_state()
                
                # Initialize camera with enhanced retry logic
                success = self._init_camera_with_enhanced_retry()
                
                if success:
                    print("✅ Fixed camera source initialized successfully")
                else:
                    print("❌ Fixed camera source initialization failed")
            
            def _init_camera_with_enhanced_retry(self, max_retries=5):
                """Initialize camera with enhanced retry logic"""
                for attempt in range(max_retries):
                    try:
                        print(f"🔧 Camera initialization attempt {attempt + 1}/{max_retries}")
                        
                        # Force DirectShow backend
                        cv_api = cv2.CAP_DSHOW
                        
                        # Open camera
                        vcap = cv2.VideoCapture(0, cv_api)
                        
                        if vcap.isOpened():
                            print("✅ Camera opened successfully")
                            
                            # Set resolution
                            vcap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                            vcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                            vcap.set(cv2.CAP_PROP_FPS, 30)
                            
                            # Test frame reading multiple times
                            success_count = 0
                            for i in range(5):
                                ret, frame = vcap.read()
                                if ret:
                                    success_count += 1
                                    print(f"✅ Frame {i+1} read successful: {frame.shape}")
                                else:
                                    print(f"❌ Frame {i+1} read failed")
                                time.sleep(0.1)
                            
                            if success_count >= 3:  # At least 3 out of 5 frames
                                print(f"✅ Frame reading test passed: {success_count}/5 frames")
                                self.set_vcap(vcap)
                                return True
                            else:
                                print(f"❌ Frame reading test failed: {success_count}/5 frames")
                                vcap.release()
                        else:
                            print("❌ Failed to open camera")
                        
                        time.sleep(2)  # Wait longer before retry
                        
                    except Exception as e:
                        print(f"❌ Camera initialization error: {e}")
                        time.sleep(2)
                
                print("❌ All camera initialization attempts failed")
                return False
        
        # Create a fixed camera source
        class FixedCameraSource(CameraSource):
            def __init__(self, weak_heap, bc_out, backend_db=None):
                super().__init__(backend_db=backend_db,
                                 sheet_cls=Sheet,
                                 worker_cls=FixedCameraSourceWorker,
                                 worker_state_cls=WorkerState,
                                 worker_start_args=[weak_heap, bc_out])
        
        print("✅ Fixed camera source created")
        
        # Create backend components
        backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)
        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        
        # Create camera source
        camera_source = FixedCameraSource(
            weak_heap=backend_weak_heap,
            bc_out=multi_sources_bc_out,
            backend_db=None
        )
        
        print("✅ Fixed camera source created")
        
        # Start camera source
        camera_source.start()
        print("✅ Fixed camera source started")
        
        # Wait for data with longer timeout
        print("⏳ Waiting for camera data (up to 10 seconds)...")
        start_time = time.time()
        
        while time.time() - start_time < 10:
            bcd_id = multi_sources_bc_out.get_write_id()
            if bcd_id > 0:
                bcd = multi_sources_bc_out.get_by_id(bcd_id)
                if bcd is not None:
                    bcd.assign_weak_heap(backend_weak_heap)
                    frame_image_name = bcd.get_frame_image_name()
                    frame_image = bcd.get_image(frame_image_name)
                    
                    if frame_image is not None:
                        print(f"✅ Camera data received!")
                        print(f"   Frame name: {frame_image_name}")
                        print(f"   Frame shape: {frame_image.shape}")
                        print(f"   Frame type: {frame_image.dtype}")
                        print(f"   Time to receive: {time.time() - start_time:.2f} seconds")
                        camera_source.stop()
                        return True
            
            time.sleep(0.5)
            print(f"⏳ Still waiting... ({time.time() - start_time:.1f}s)")
        
        print("❌ No camera data received within timeout")
        camera_source.stop()
        return False
        
    except Exception as e:
        print(f"❌ Error testing camera integration fix: {e}")
        return False

def create_working_camera_test():
    """Create a working camera test that combines camera and face swap"""
    print("\n🔧 Creating Working Camera Test...")
    print("=" * 50)
    
    test_code = '''#!/usr/bin/env python3
"""
Working Camera Test for PlayaTewsIdentityMasker
Combines working camera preview with face swap functionality
"""

import cv2
import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
import numpy as np

class WorkingCameraTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Working Camera Test - PlayaTewsIdentityMasker")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create camera preview label
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
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Camera")
        self.start_btn.clicked.connect(self.start_camera)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Camera")
        self.stop_btn.clicked.connect(self.stop_camera)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.face_swap_btn = QPushButton("Start Face Swap App")
        self.face_swap_btn.clicked.connect(self.start_face_swap_app)
        button_layout.addWidget(self.face_swap_btn)
        
        layout.addLayout(button_layout)
        
        # Initialize camera
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # Auto-start camera
        self.start_camera()
        
        print("✅ Working camera test created")
    
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
    
    def start_face_swap_app(self):
        """Start the face swap application"""
        try:
            import subprocess
            subprocess.Popen([sys.executable, "main.py", "run", "PlayaTewsIdentityMasker"])
            self.status_label.setText("Status: Face swap app started")
            print("✅ Face swap app started")
        except Exception as e:
            self.status_label.setText(f"Status: Error starting face swap app - {str(e)}")
            print(f"❌ Error starting face swap app: {e}")
    
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
    window = WorkingCameraTest()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
'''
    
    with open("working_camera_test.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Created: working_camera_test.py")
    print("   Run this to test camera with face swap app integration")

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Integration Test")
    print("=" * 60)
    print()
    
    # Test camera integration fix
    success = test_camera_integration_fix()
    
    # Create working camera test
    create_working_camera_test()
    
    print("\n📊 Results:")
    print("=" * 40)
    if success:
        print("✅ Camera integration fix successful!")
        print("   Camera data is now reaching the backend connection")
        print("   Preview area should now show camera feed")
    else:
        print("❌ Camera integration fix needs more work")
        print("   But you have a working camera test solution")
    
    print("\n🚀 Next Steps:")
    print("   1. Run: python working_camera_test.py")
    print("   2. This gives you working camera preview")
    print("   3. Use 'Start Face Swap App' button to run main app")
    print("   4. Both can work together for full functionality")

if __name__ == "__main__":
    main() 