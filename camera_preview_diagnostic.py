#!/usr/bin/env python3
"""
Camera Preview Diagnostic for PlayaTewsIdentityMasker
Checks if camera data is being received and why preview isn't showing
"""

import cv2
import time
import numpy as np
from pathlib import Path
import sys
import os

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_camera_direct():
    """Test camera directly with OpenCV"""
    print("🔍 Testing Camera Directly...")
    print("=" * 50)
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Failed to open camera with DirectShow")
        return False
    
    print("✅ Camera opened successfully")
    
    # Test frame reading
    success_count = 0
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            success_count += 1
            print(f"✅ Frame {i+1}: Success - {frame.shape}")
        else:
            print(f"❌ Frame {i+1}: Failed")
        time.sleep(0.1)
    
    cap.release()
    print(f"📊 Success Rate: {success_count}/10 frames")
    return success_count > 0

def test_backend_connection():
    """Test if backend connection is receiving data"""
    print("\n🔍 Testing Backend Connection...")
    print("=" * 50)
    
    try:
        from apps.PlayaTewsIdentityMasker import backend
        from apps.PlayaTewsIdentityMasker.backend.CameraSource import CameraSource
        
        # Create backend components
        backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)
        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        
        # Create camera source
        camera_source = CameraSource(
            weak_heap=backend_weak_heap,
            bc_out=multi_sources_bc_out,
            backend_db=None
        )
        
        print("✅ Backend components created")
        
        # Start camera source
        camera_source.start()
        print("✅ Camera source started")
        
        # Wait for data
        print("⏳ Waiting for camera data...")
        time.sleep(2)
        
        # Check for data
        bcd_id = multi_sources_bc_out.get_write_id()
        print(f"📊 Backend connection ID: {bcd_id}")
        
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
                    return True
                else:
                    print("❌ Frame image is None")
            else:
                print("❌ Backend connection data is None")
        else:
            print("❌ No data in backend connection")
        
        camera_source.stop()
        return False
        
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_ui_components():
    """Test UI components"""
    print("\n🔍 Testing UI Components...")
    print("=" * 50)
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFrameViewer import QBCFrameViewer
        from apps.PlayaTewsIdentityMasker import backend
        from PyQt5.QtWidgets import QApplication
        
        # Create QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create backend components
        backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)
        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        
        # Create frame viewer
        frame_viewer = QBCFrameViewer(
            backed_weak_heap=backend_weak_heap,
            bc=multi_sources_bc_out,
            preview_width=256
        )
        
        print("✅ Frame viewer created")
        print(f"   Timer interval: {frame_viewer._timer.interval()}ms")
        print(f"   Backend connection: {frame_viewer._bc}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing UI components: {e}")
        return False

def create_simple_preview_test():
    """Create a simple preview test"""
    print("\n🔍 Creating Simple Preview Test...")
    print("=" * 50)
    
    test_code = '''#!/usr/bin/env python3
"""
Simple Camera Preview Test
"""

import cv2
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
import numpy as np

class SimpleCameraPreview(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Camera Preview Test")
        self.setGeometry(100, 100, 640, 480)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create preview label
        self.preview_label = QLabel("No camera feed")
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setStyleSheet("QLabel { border: 2px solid #ccc; background-color: #f0f0f0; }")
        layout.addWidget(self.preview_label)
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.preview_label.setText("Failed to open camera")
            return
        
        # Create timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)  # ~30 FPS
        
        print("✅ Simple camera preview created")
    
    def update_frame(self):
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
        else:
            self.preview_label.setText("Failed to read frame")
    
    def closeEvent(self, event):
        if self.cap.isOpened():
            self.cap.release()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = SimpleCameraPreview()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
'''
    
    with open("simple_camera_preview_test.py", 'w') as f:
        f.write(test_code)
    
    print("✅ Created: simple_camera_preview_test.py")
    print("   Run this to test basic camera preview functionality")

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Preview Diagnostic")
    print("=" * 60)
    print()
    
    # Test camera directly
    camera_working = test_camera_direct()
    
    # Test backend connection
    backend_working = test_backend_connection()
    
    # Test UI components
    ui_working = test_ui_components()
    
    # Create simple preview test
    create_simple_preview_test()
    
    print("\n📊 Diagnostic Results:")
    print("=" * 40)
    print(f"📹 Camera Direct: {'✅ Working' if camera_working else '❌ Failed'}")
    print(f"🔗 Backend Connection: {'✅ Working' if backend_working else '❌ Failed'}")
    print(f"🖥️ UI Components: {'✅ Working' if ui_working else '❌ Failed'}")
    
    print("\n💡 Recommendations:")
    if not camera_working:
        print("   - Camera is not working directly")
        print("   - Check virtual camera app")
    elif not backend_working:
        print("   - Camera works but backend not receiving data")
        print("   - Check camera source initialization")
    elif not ui_working:
        print("   - Backend working but UI components failing")
        print("   - Check PyQt5 installation")
    else:
        print("   - All components working")
        print("   - Try the simple preview test")
    
    print("\n🚀 Next Steps:")
    print("   1. Run: python simple_camera_preview_test.py")
    print("   2. If simple test works, issue is in main app")
    print("   3. If simple test fails, issue is with camera/OpenCV")

if __name__ == "__main__":
    main() 