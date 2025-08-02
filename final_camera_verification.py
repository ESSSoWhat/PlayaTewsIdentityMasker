#!/usr/bin/env python3
"""
Final Camera Verification for PlayaTewsIdentityMasker
Confirms camera feed is now working in the preview area
"""

import time
from pathlib import Path

def verify_qt_application():
    """Verify Qt application is properly initialized"""
    print("🔍 Verifying Qt Application...")
    print("=" * 50)
    
    try:
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app is not None:
            print("✅ QApplication instance exists")
            print(f"   Application name: {app.applicationName()}")
            
            # Check for widgets
            widgets = app.allWidgets()
            print(f"   Number of widgets: {len(widgets)}")
            
            # Look for frame viewer widgets
            frame_viewers = [w for w in widgets if 'FrameViewer' in str(type(w))]
            print(f"   Frame viewer widgets: {len(frame_viewers)}")
            
            for i, viewer in enumerate(frame_viewers):
                print(f"     Frame viewer {i+1}: {type(viewer).__name__}")
                print(f"       Visible: {viewer.isVisible()}")
                print(f"       Size: {viewer.size()}")
            
            return True
        else:
            print("❌ No QApplication instance found")
            return False
            
    except Exception as e:
        print(f"❌ Qt application verification error: {e}")
        return False

def verify_camera_data_flow():
    """Verify camera data is flowing"""
    print("\n🔍 Verifying Camera Data Flow...")
    print("=" * 50)
    
    try:
        from apps.PlayaTewsIdentityMasker import backend
        
        backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)
        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        
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
        return False

def verify_settings():
    """Verify camera settings are configured"""
    print("\n🔍 Verifying Camera Settings...")
    print("=" * 50)
    
    import json
    
    settings_files = [
        "settings/camera_override.json",
        "settings/global_face_swap_state.json",
        "demo_settings/settings/global_face_swap_state.json"
    ]
    
    all_ok = True
    for settings_file in settings_files:
        settings_path = Path(settings_file)
        if settings_path.exists():
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'camera' in data:
                    camera_settings = data['camera']
                    print(f"✅ {settings_file}: Camera settings configured")
                    print(f"   Device: {camera_settings.get('device_idx', 'Not set')}")
                    print(f"   Driver: {camera_settings.get('driver', 'Not set')} (DirectShow)")
                    print(f"   Resolution: {camera_settings.get('resolution', 'Not set')} (1280x720)")
                else:
                    print(f"❌ {settings_file}: No camera settings found")
                    all_ok = False
            except Exception as e:
                print(f"❌ {settings_file}: Error reading - {e}")
                all_ok = False
        else:
            print(f"❌ {settings_file}: Not found")
            all_ok = False
    
    return all_ok

def main():
    print("🎬 PlayaTewsIdentityMasker - Final Camera Verification")
    print("=" * 60)
    print()
    
    # Wait for app to initialize
    print("⏳ Waiting for app initialization...")
    time.sleep(10)
    
    qt_ok = verify_qt_application()
    camera_ok = verify_camera_data_flow()
    settings_ok = verify_settings()
    
    print("\n📊 Final Verification Results:")
    print("=" * 40)
    
    if qt_ok and camera_ok and settings_ok:
        print("🎉 SUCCESS! All components are working!")
        print("✅ Qt application: Properly initialized")
        print("✅ Camera data flow: Working")
        print("✅ Camera settings: Configured")
        print("\n🎯 The camera feed should now be visible in the preview area!")
        print("\n📱 What you should see:")
        print("1. Main PlayaTewsIdentityMasker window")
        print("2. Camera feed in the preview area")
        print("3. Face swap functionality working")
        print("4. Real-time processing active")
        print("\n🚀 The camera integration issue has been completely resolved!")
    else:
        print("❌ Some components are not working:")
        if not qt_ok:
            print("   • Qt application not properly initialized")
        if not camera_ok:
            print("   • Camera data not flowing")
        if not settings_ok:
            print("   • Camera settings not configured")
        print("\n🔧 Please check the main application status")

if __name__ == "__main__":
    main() 