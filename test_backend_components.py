#!/usr/bin/env python3
"""
Test Backend Components Script
Tests individual backend components to identify which one is causing CSW flag errors
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

def test_backend_components():
    """Test individual backend components"""
    app = QApplication(sys.argv)
    
    # Create a simple main window
    window = QMainWindow()
    window.setWindowTitle("Backend Components Test")
    window.setGeometry(100, 100, 800, 600)
    
    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # Create layout
    layout = QVBoxLayout()
    central_widget.setLayout(layout)
    
    # Add test results
    results_label = QLabel("Testing Backend Components...")
    results_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(results_label)
    
    results = []
    
    try:
        # Test 1: Basic imports
        print("Testing basic imports...")
        from apps.PlayaTewsIdentityMasker import backend
        results.append("✅ Basic backend imports: OK")
        
        # Test 2: Backend DB
        print("Testing BackendDB...")
        backend_db = backend.BackendDB(Path.cwd() / 'settings' / 'test_states.dat')
        results.append("✅ BackendDB: OK")
        
        # Test 3: Backend Weak Heap
        print("Testing BackendWeakHeap...")
        backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)
        results.append("✅ BackendWeakHeap: OK")
        
        # Test 4: Backend Signal
        print("Testing BackendSignal...")
        reemit_frame_signal = backend.BackendSignal()
        results.append("✅ BackendSignal: OK")
        
        # Test 5: Backend Connection
        print("Testing BackendConnection...")
        bc_out = backend.BackendConnection()
        results.append("✅ BackendConnection: OK")
        
        # Test 6: File Source
        print("Testing FileSource...")
        file_source = backend.FileSource(
            weak_heap=backend_weak_heap, 
            reemit_frame_signal=reemit_frame_signal, 
            bc_out=bc_out, 
            backend_db=backend_db
        )
        results.append("✅ FileSource: OK")
        
        # Test 7: Camera Source
        print("Testing CameraSource...")
        camera_source = backend.CameraSource(
            weak_heap=backend_weak_heap, 
            bc_out=bc_out, 
            backend_db=backend_db
        )
        results.append("✅ CameraSource: OK")
        
        # Test 8: Face Detector
        print("Testing FaceDetector...")
        face_detector = backend.FaceDetector(
            weak_heap=backend_weak_heap, 
            reemit_frame_signal=reemit_frame_signal, 
            bc_in=bc_out, 
            bc_out=backend.BackendConnection(), 
            backend_db=backend_db
        )
        results.append("✅ FaceDetector: OK")
        
        # Test 9: Enhanced Stream Output
        print("Testing EnhancedStreamOutput...")
        try:
            from apps.PlayaTewsIdentityMasker.backend.EnhancedStreamOutput import EnhancedStreamOutput
            stream_output = EnhancedStreamOutput(
                weak_heap=backend_weak_heap, 
                reemit_frame_signal=reemit_frame_signal, 
                bc_in=backend.BackendConnection(), 
                save_default_path=Path.cwd(), 
                backend_db=backend_db
            )
            results.append("✅ EnhancedStreamOutput: OK")
        except Exception as e:
            results.append(f"❌ EnhancedStreamOutput: {e}")
        
        # Test 10: UI Components
        print("Testing UI Components...")
        try:
            from apps.PlayaTewsIdentityMasker.ui.QFileSource import QFileSource
            q_file_source = QFileSource(file_source)
            results.append("✅ QFileSource: OK")
        except Exception as e:
            results.append(f"❌ QFileSource: {e}")
        
        try:
            from apps.PlayaTewsIdentityMasker.ui.QCameraSource import QCameraSource
            q_camera_source = QCameraSource(camera_source)
            results.append("✅ QCameraSource: OK")
        except Exception as e:
            results.append(f"❌ QCameraSource: {e}")
        
        try:
            from apps.PlayaTewsIdentityMasker.ui.QEnhancedStreamOutput import QEnhancedStreamOutput
            q_stream_output = QEnhancedStreamOutput(stream_output)
            results.append("✅ QEnhancedStreamOutput: OK")
        except Exception as e:
            results.append(f"❌ QEnhancedStreamOutput: {e}")
        
    except Exception as e:
        results.append(f"❌ General Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Update results display
    results_text = "\n".join(results)
    results_label.setText(f"Backend Components Test Results:\n\n{results_text}")
    
    # Add close button
    close_btn = QPushButton("Close")
    close_btn.clicked.connect(window.close)
    layout.addWidget(close_btn)
    
    # Show the window
    window.show()
    
    print("✅ Backend components test window should be visible")
    print("Check the window for detailed results")
    
    # Run the app
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_backend_components() 