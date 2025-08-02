#!/usr/bin/env python3
"""
Test UI Connection for PlayaTewsIdentityMasker
Verifies UI connection and forces camera display refresh
"""

import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.append('.')

def test_ui_connection():
    """Test UI connection and force camera display refresh"""
    print("🔍 Testing UI Connection...")
    print("=" * 50)
    
    try:
        # Import backend components
        from apps.PlayaTewsIdentityMasker import backend
        
        # Create backend components
        backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)
        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        
        # Create camera source
        camera_source = backend.CameraSource(
            weak_heap=backend_weak_heap, 
            bc_out=multi_sources_bc_out, 
            backend_db=None
        )
        
        # Start camera source
        camera_source.start()
        print("✅ Camera source started")
        
        # Wait for initialization
        time.sleep(3)
        
        # Check for data in backend connection
        bcd_id = multi_sources_bc_out.get_write_id()
        print(f"Backend connection write ID: {bcd_id}")
        
        if bcd_id > 0:
            bcd = multi_sources_bc_out.get_by_id(bcd_id)
            if bcd is not None:
                bcd.assign_weak_heap(backend_weak_heap)
                frame_image_name = bcd.get_frame_image_name()
                frame_image = bcd.get_image(frame_image_name)
                
                if frame_image is not None:
                    print(f"✅ Camera data flowing: {frame_image.shape}")
                    print(f"   Frame name: {frame_image_name}")
                    print(f"   Frame number: {bcd.get_frame_num()}")
                    print(f"   Timestamp: {bcd.get_frame_timestamp()}")
                    
                    # Test UI component connection
                    try:
                        from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFrameViewer import QBCFrameViewer
                        
                        # Create UI component
                        frame_viewer = QBCFrameViewer(backend_weak_heap, multi_sources_bc_out)
                        print("✅ QBCFrameViewer created successfully")
                        
                        # Force refresh
                        if hasattr(frame_viewer, 'update'):
                            frame_viewer.update()
                            print("✅ Frame viewer update called")
                        
                        if hasattr(frame_viewer, 'repaint'):
                            frame_viewer.repaint()
                            print("✅ Frame viewer repaint called")
                        
                        print("✅ UI connection test successful")
                        
                    except Exception as e:
                        print(f"❌ UI component test error: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print("❌ No frame image in backend connection")
            else:
                print("❌ No backend connection data")
        else:
            print("❌ No data in backend connection")
        
        # Stop camera source
        camera_source.stop()
        print("✅ Camera source stopped")
        
    except Exception as e:
        print(f"❌ UI connection test error: {e}")
        import traceback
        traceback.print_exc()

def check_ui_component():
    """Check UI component availability"""
    print("\n🔍 Checking UI Component...")
    print("=" * 50)
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFrameViewer import QBCFrameViewer
        print("✅ QBCFrameViewer import successful")
        
        # Check if component has required methods
        if hasattr(QBCFrameViewer, '__init__'):
            print("✅ QBCFrameViewer has __init__ method")
        
        if hasattr(QBCFrameViewer, 'update'):
            print("✅ QBCFrameViewer has update method")
        
        if hasattr(QBCFrameViewer, 'repaint'):
            print("✅ QBCFrameViewer has repaint method")
        
        print("✅ UI component check successful")
        
    except Exception as e:
        print(f"❌ UI component check error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🎬 PlayaTewsIdentityMasker - UI Connection Test")
    print("=" * 60)
    print()
    
    check_ui_component()
    test_ui_connection()
    
    print("\n📊 UI Connection Test Complete!")
    print("=" * 40)

if __name__ == "__main__":
    main() 