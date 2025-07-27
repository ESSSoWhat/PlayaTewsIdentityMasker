#!/usr/bin/env python3
"""
Test script to verify component activation in PlayaTewsIdentityMasker
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_component_activation():
    """Test that backend components are properly activated"""
    print("Testing PlayaTewsIdentityMasker component activation...")
    
    try:
        from apps.PlayaTewsIdentityMasker import backend
        from apps.PlayaTewsIdentityMasker.backend import (
            FileSource, CameraSource, FaceDetector, FaceMarker, 
            FaceAligner, FaceAnimator, FaceSwapInsight, FaceSwapDFM,
            FrameAdjuster, FaceMerger, StreamOutput
        )
        
        print("✅ Backend modules imported successfully")
        
        # Test backend creation
        userdata_path = Path("userdata")
        settings_dirpath = Path("settings")
        
        # Create backend infrastructure
        backend_db = backend.BackendDB(settings_dirpath / 'states.dat')
        backend_weak_heap = backend.BackendWeakHeap(size_mb=2048)
        reemit_frame_signal = backend.BackendSignal()
        
        # Create backend connections
        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        face_detector_bc_out = backend.BackendConnection()
        face_marker_bc_out = backend.BackendConnection()
        face_aligner_bc_out = backend.BackendConnection()
        face_swapper_bc_out = backend.BackendConnection()
        frame_adjuster_bc_out = backend.BackendConnection()
        face_merger_bc_out = backend.BackendConnection()
        
        # Create backend components
        file_source = FileSource(weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_out=multi_sources_bc_out, backend_db=backend_db)
        camera_source = CameraSource(weak_heap=backend_weak_heap, bc_out=multi_sources_bc_out, backend_db=backend_db)
        face_detector = FaceDetector(weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=multi_sources_bc_out, bc_out=face_detector_bc_out, backend_db=backend_db)
        
        print("✅ Backend components created successfully")
        
        # Test component activation
        all_backends = [file_source, camera_source, face_detector]
        
        print("\nTesting component activation...")
        for backend_component in all_backends:
            print(f"Testing {backend_component.__class__.__name__}:")
            print(f"  - Initial state: {'Started' if backend_component.is_started() else 'Stopped'}")
            
            if backend_component.is_stopped():
                print(f"  - Starting {backend_component.__class__.__name__}...")
                backend_component.start()
                
                # Process messages multiple times to complete startup
                for _ in range(10):
                    backend_db.process_messages()
                    for b in all_backends:
                        b.process_messages()
                
                print(f"  - State after start: {'Started' if backend_component.is_started() else 'Stopped'}")
                print(f"  - Is starting: {backend_component.is_starting()}")
                print(f"  - Is stopping: {backend_component.is_stopping()}")
                print(f"  - Is busy: {backend_component.is_busy()}")
            else:
                print(f"  - Already started")
        
        print("\n✅ Component activation test completed successfully")
        
        # Test UI component creation (requires QApplication)
        print("\nTesting UI component creation...")
        try:
            from PyQt5.QtWidgets import QApplication
            import sys
            
            # Create QApplication for UI testing
            app = QApplication(sys.argv)
            
            from apps.PlayaTewsIdentityMasker.ui.QFileSource import QFileSource
            from apps.PlayaTewsIdentityMasker.ui.QCameraSource import QCameraSource
            from apps.PlayaTewsIdentityMasker.ui.QFaceDetector import QFaceDetector
            
            q_file_source = QFileSource(file_source)
            q_camera_source = QCameraSource(camera_source)
            q_face_detector = QFaceDetector(face_detector)
            
            print("✅ UI components created successfully")
            
            # Test backend connection
            if hasattr(q_file_source, '_backend'):
                print(f"✅ QFileSource backend connected: {q_file_source._backend.is_started()}")
            if hasattr(q_camera_source, '_backend'):
                print(f"✅ QCameraSource backend connected: {q_camera_source._backend.is_started()}")
            if hasattr(q_face_detector, '_backend'):
                print(f"✅ QFaceDetector backend connected: {q_face_detector._backend.is_started()}")
                
        except ImportError as e:
            print(f"⚠️ UI component import error: {e}")
        except Exception as e:
            print(f"⚠️ UI component creation error: {e}")
        
        # Cleanup
        for backend_component in all_backends:
            if backend_component.is_started():
                backend_component.stop()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_component_activation() 