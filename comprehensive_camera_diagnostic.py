#!/usr/bin/env python3
"""
Comprehensive Camera Diagnostic for PlayaTewsIdentityMasker
Identifies exactly why camera feed isn't appearing in preview area
"""

import cv2
import time
import json
import sys
import subprocess
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
    """Check different camera backends"""
    print("\n🔍 Checking Camera Backends...")
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
    print("\n🔍 Checking Camera Settings...")
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
                    data = json.load(f)
                    print(f"✅ {settings_file}: Exists")
                    if 'camera' in data:
                        camera_settings = data['camera']
                        print(f"   Device: {camera_settings.get('device_idx', 'Not set')}")
                        print(f"   Driver: {camera_settings.get('driver', 'Not set')}")
                        print(f"   Resolution: {camera_settings.get('resolution', 'Not set')}")
                    else:
                        print(f"   No camera settings found")
            except Exception as e:
                print(f"❌ {settings_file}: Error reading - {e}")
        else:
            print(f"❌ {settings_file}: Not found")

def check_camera_source_file():
    """Check camera source file modifications"""
    print("\n🔍 Checking Camera Source File...")
    print("=" * 50)
    
    camera_source_file = "apps/PlayaTewsIdentityMasker/backend/CameraSource.py"
    
    if Path(camera_source_file).exists():
        try:
            with open(camera_source_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if "cv2.CAP_DSHOW" in content:
                    print("✅ DirectShow forcing: Applied")
                else:
                    print("❌ DirectShow forcing: Not applied")
                
                if "Setting driver to DirectShow" in content:
                    print("✅ Driver auto-setting: Applied")
                else:
                    print("❌ Driver auto-setting: Not applied")
                
                if "Setting device index to 0" in content:
                    print("✅ Device index auto-setting: Applied")
                else:
                    print("❌ Device index auto-setting: Not applied")
                
                if "BackendConnectionData" in content:
                    print("✅ Backend connection: Present")
                else:
                    print("❌ Backend connection: Missing")
                    
        except Exception as e:
            print(f"❌ Camera source file check error: {e}")
    else:
        print(f"❌ Camera source file: Not found")

def check_main_app_file():
    """Check main app file modifications"""
    print("\n🔍 Checking Main App File...")
    print("=" * 50)
    
    main_app_file = "apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerApp.py"
    
    if Path(main_app_file).exists():
        try:
            with open(main_app_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if "Enhanced camera source initialization" in content:
                    print("✅ Enhanced initialization: Applied")
                else:
                    print("❌ Enhanced initialization: Not applied")
                
                if "camera_source.start()" in content:
                    print("✅ Camera auto-start: Applied")
                else:
                    print("❌ Camera auto-start: Not applied")
                
                if "multi_sources_bc_out" in content:
                    print("✅ Backend connection setup: Present")
                else:
                    print("❌ Backend connection setup: Missing")
                    
        except Exception as e:
            print(f"❌ Main app file check error: {e}")
    else:
        print(f"❌ Main app file: Not found")

def test_camera_data_flow():
    """Test camera data flow through backend"""
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
        import traceback
        traceback.print_exc()

def check_ui_components():
    """Check UI components for camera display"""
    print("\n🔍 Checking UI Components...")
    print("=" * 50)
    
    ui_files = [
        "apps/PlayaTewsIdentityMasker/ui/QBCFrameViewer.py",
        "apps/PlayaTewsIdentityMasker/ui/QUnifiedLiveSwap.py",
        "apps/PlayaTewsIdentityMasker/ui/widgets/QBCFrameViewer.py"
    ]
    
    for ui_file in ui_files:
        if Path(ui_file).exists():
            print(f"✅ {ui_file}: Exists")
        else:
            print(f"❌ {ui_file}: Not found")

def check_app_running():
    """Check if the main app is currently running"""
    print("\n🔍 Checking App Status...")
    print("=" * 50)
    
    try:
        # Check for Python processes
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if "python.exe" in result.stdout:
            print("✅ Python processes running")
            lines = result.stdout.split('\n')
            for line in lines:
                if "python.exe" in line:
                    print(f"   {line.strip()}")
        else:
            print("❌ No Python processes running")
            
    except Exception as e:
        print(f"❌ Process check error: {e}")

def main():
    print("🎬 PlayaTewsIdentityMasker - Comprehensive Camera Diagnostic")
    print("=" * 70)
    print()
    
    check_camera_hardware()
    check_camera_backends()
    check_settings_files()
    check_camera_source_file()
    check_main_app_file()
    check_ui_components()
    check_app_running()
    test_camera_data_flow()
    
    print("\n📊 Diagnostic Complete!")
    print("=" * 40)
    print("\n🔧 Next Steps:")
    print("1. Check if camera hardware is available")
    print("2. Verify DirectShow backend is working")
    print("3. Ensure settings files are properly configured")
    print("4. Confirm camera source modifications are applied")
    print("5. Verify main app modifications are applied")
    print("6. Test camera data flow through backend")
    print("7. Check if UI components are properly connected")

if __name__ == "__main__":
    main() 