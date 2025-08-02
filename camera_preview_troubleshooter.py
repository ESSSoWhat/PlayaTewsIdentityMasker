#!/usr/bin/env python3
"""
Camera Preview Troubleshooter for PlayaTewsIdentityMasker
Comprehensive diagnostic tool to troubleshoot camera preview issues
"""

import cv2
import time
import json
import subprocess
import sys
from pathlib import Path

def check_camera_hardware():
    """Check camera hardware availability"""
    print("🔍 Checking Camera Hardware...")
    print("=" * 50)
    
    try:
        # Test different camera indexes
        for idx in range(4):
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ Camera {idx}: Available ({frame.shape})")
                else:
                    print(f"⚠️ Camera {idx}: Opened but no frame")
                cap.release()
            else:
                print(f"❌ Camera {idx}: Not available")
    except Exception as e:
        print(f"❌ Camera hardware check error: {e}")

def check_camera_backends():
    """Test different camera backends"""
    print("\n🔍 Testing Camera Backends...")
    print("=" * 50)
    
    backends = [
        ("DirectShow", cv2.CAP_DSHOW),
        ("Media Foundation", cv2.CAP_MSMF),
        ("Auto", cv2.CAP_ANY)
    ]
    
    for name, backend in backends:
        try:
            cap = cv2.VideoCapture(0, backend)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ {name}: Working ({frame.shape})")
                else:
                    print(f"⚠️ {name}: Opened but no frame")
            else:
                print(f"❌ {name}: Failed to open")
            cap.release()
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

def check_settings_files():
    """Check camera settings files"""
    print("\n🔍 Checking Settings Files...")
    print("=" * 50)
    
    settings_files = [
        "settings/camera_override.json",
        "settings/global_face_swap_state.json",
        "demo_settings/settings/global_face_swap_state.json"
    ]
    
    for settings_file in settings_files:
        settings_path = Path(settings_file)
        if settings_path.exists():
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                print(f"✅ {settings_file}: Valid JSON")
                
                # Check for DirectShow configuration
                if "driver" in settings and settings["driver"] == 1:
                    print(f"   ✅ DirectShow configured (driver: 1)")
                elif "camera_backend" in settings and settings["camera_backend"] == "DirectShow":
                    print(f"   ✅ DirectShow configured (camera_backend: DirectShow)")
                else:
                    print(f"   ⚠️ DirectShow not explicitly configured")
                    
            except Exception as e:
                print(f"❌ {settings_file}: Error - {e}")
        else:
            print(f"⚠️ {settings_file}: Not found")

def check_camera_source_patch():
    """Check if camera source is properly patched"""
    print("\n🔍 Checking Camera Source Patch...")
    print("=" * 50)
    
    camera_source_file = "apps/PlayaTewsIdentityMasker/backend/CameraSource.py"
    
    if Path(camera_source_file).exists():
        with open(camera_source_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "cv_api = cv2.CAP_DSHOW  # Force DirectShow" in content:
            print("✅ DirectShow forcing applied")
        else:
            print("❌ DirectShow forcing not found")
            
        if "print(f\"🔧 Forcing DirectShow backend for camera" in content:
            print("✅ Debug output added")
        else:
            print("❌ Debug output not found")
    else:
        print(f"❌ Camera source file not found")

def check_main_app_patch():
    """Check if main app is properly enhanced"""
    print("\n🔍 Checking Main App Patch...")
    print("=" * 50)
    
    main_app_file = "apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerApp.py"
    
    if Path(main_app_file).exists():
        with open(main_app_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "Enhanced camera source initialization" in content:
            print("✅ Enhanced initialization applied")
        else:
            print("❌ Enhanced initialization not found")
            
        if "camera_source.start()" in content:
            print("✅ Camera auto-start applied")
        else:
            print("❌ Camera auto-start not found")
    else:
        print(f"❌ Main app file not found")

def test_camera_data_flow():
    """Test camera data flow through backend connections"""
    print("\n🔍 Testing Camera Data Flow...")
    print("=" * 50)
    
    try:
        # Import backend components
        sys.path.append('.')
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
        if bcd_id > 0:
            bcd = multi_sources_bc_out.get_by_id(bcd_id)
            if bcd is not None:
                bcd.assign_weak_heap(backend_weak_heap)
                frame_image_name = bcd.get_frame_image_name()
                frame_image = bcd.get_image(frame_image_name)
                
                if frame_image is not None:
                    print(f"✅ Camera data flowing: {frame_image.shape}")
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
        print(f"❌ Camera data flow test error: {e}")

def check_ui_components():
    """Check UI components for camera display"""
    print("\n🔍 Checking UI Components...")
    print("=" * 50)
    
    ui_files = [
        "apps/PlayaTewsIdentityMasker/ui/widgets/QBCFrameViewer.py",
        "apps/PlayaTewsIdentityMasker/ui/widgets/QBCMergedFrameViewer.py",
        "apps/PlayaTewsIdentityMasker/ui/QUnifiedLiveSwap.py"
    ]
    
    for ui_file in ui_files:
        if Path(ui_file).exists():
            print(f"✅ {ui_file}: Exists")
        else:
            print(f"❌ {ui_file}: Not found")

def provide_solutions():
    """Provide solutions based on diagnostic results"""
    print("\n🔧 Troubleshooting Solutions...")
    print("=" * 50)
    
    print("If camera feed still doesn't appear in preview area:")
    print()
    print("1. **Check Virtual Camera App:**")
    print("   • Ensure your virtual camera app is running")
    print("   • Verify it's outputting to camera index 0")
    print("   • Check if it's compatible with DirectShow")
    print()
    print("2. **Check Camera Permissions:**")
    print("   • Go to Windows Settings > Privacy > Camera")
    print("   • Ensure camera access is enabled for applications")
    print("   • Check if any antivirus is blocking camera access")
    print()
    print("3. **Try Different Camera Index:**")
    print("   • Run: python camera_troubleshooting.py")
    print("   • Test different camera indexes (0, 1, 2, etc.)")
    print()
    print("4. **Check Console Output:**")
    print("   • Look for error messages in the application console")
    print("   • Check for DirectShow initialization messages")
    print()
    print("5. **Restart Application:**")
    print("   • Close the application completely")
    print("   • Restart your virtual camera app")
    print("   • Start the application again")
    print()
    print("6. **Alternative Solutions:**")
    print("   • Try running: python working_camera_test.py")
    print("   • This provides a separate camera preview window")
    print("   • Use this as a workaround while fixing main app")

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Preview Troubleshooter")
    print("=" * 70)
    print()
    
    # Run all diagnostic checks
    check_camera_hardware()
    check_camera_backends()
    check_settings_files()
    check_camera_source_patch()
    check_main_app_patch()
    test_camera_data_flow()
    check_ui_components()
    
    # Provide solutions
    provide_solutions()
    
    print("\n📊 Diagnostic Complete!")
    print("=" * 40)
    print("Check the results above to identify the issue.")
    print("Follow the troubleshooting solutions provided.")

if __name__ == "__main__":
    main() 