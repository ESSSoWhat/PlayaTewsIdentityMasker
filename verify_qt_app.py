#!/usr/bin/env python3
"""
Verify Qt Application for PlayaTewsIdentityMasker
Verifies Qt application is properly initialized for camera display
"""

import time
from pathlib import Path

def verify_qt_application():
    """Verify Qt application is properly initialized"""
    print("🔍 Verifying Qt Application...")
    print("=" * 50)
    
    try:
        # Try to import Qt components
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QThread
        
        # Check if QApplication instance exists
        app = QApplication.instance()
        if app is not None:
            print("✅ QApplication instance exists")
            print(f"   Application name: {app.applicationName()}")
            print(f"   Application version: {app.applicationVersion()}")
            print(f"   Application object: {app}")
            
            # Check if there are any widgets
            widgets = app.allWidgets()
            print(f"   Number of widgets: {len(widgets)}")
            
            # Look for frame viewer widgets
            frame_viewers = [w for w in widgets if 'FrameViewer' in str(type(w))]
            print(f"   Frame viewer widgets: {len(frame_viewers)}")
            
            for i, viewer in enumerate(frame_viewers):
                print(f"     Frame viewer {i+1}: {type(viewer).__name__}")
                print(f"       Visible: {viewer.isVisible()}")
                print(f"       Size: {viewer.size()}")
                print(f"       Position: {viewer.pos()}")
            
            return True
        else:
            print("❌ No QApplication instance found")
            return False
            
    except Exception as e:
        print(f"❌ Qt application verification error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_camera_data_flow():
    """Verify camera data is still flowing"""
    print("\n🔍 Verifying Camera Data Flow...")
    print("=" * 50)
    
    try:
        # Import backend components
        from apps.PlayaTewsIdentityMasker import backend
        
        # Create backend components
        backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)
        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        
        # Check for existing data
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
                    return True
                else:
                    print("❌ No frame image in backend connection")
                    return False
            else:
                print("❌ No backend connection data")
                return False
        else:
            print("❌ No data in backend connection")
            return False
        
    except Exception as e:
        print(f"❌ Camera data flow verification error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎬 PlayaTewsIdentityMasker - Qt Application Verification")
    print("=" * 60)
    print()
    
    # Wait a moment for the app to initialize
    print("⏳ Waiting for app initialization...")
    time.sleep(5)
    
    qt_ok = verify_qt_application()
    camera_ok = verify_camera_data_flow()
    
    print("\n📊 Verification Complete!")
    print("=" * 40)
    
    if qt_ok and camera_ok:
        print("✅ Both Qt application and camera data flow are working!")
        print("🎯 The camera feed should now be visible in the preview area.")
        print("\n🔧 If you still don't see the camera feed:")
        print("1. Check if the main app window is visible")
        print("2. Look for the preview area in the main interface")
        print("3. Try clicking on different tabs or sections")
        print("4. Check if the camera source is enabled in the UI")
    else:
        if not qt_ok:
            print("❌ Qt application is not properly initialized")
        if not camera_ok:
            print("❌ Camera data is not flowing")
        print("\n🔧 Please restart the main application")

if __name__ == "__main__":
    main() 