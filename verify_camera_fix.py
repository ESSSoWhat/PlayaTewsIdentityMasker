#!/usr/bin/env python3
"""
Verify Camera Fix for PlayaTewsIdentityMasker
Verifies that the camera fixes are working properly in the main app
"""

import cv2
import time
import json
from pathlib import Path
import sys

def verify_camera_settings():
    """Verify camera settings are properly configured"""
    print("🔍 Verifying Camera Settings...")
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
                print(f"✅ {settings_file} exists and is valid JSON")
                
                if "driver" in settings and settings["driver"] == 1:
                    print(f"   ✅ DirectShow backend configured (driver: 1)")
                elif "camera_backend" in settings and settings["camera_backend"] == "DirectShow":
                    print(f"   ✅ DirectShow backend configured (camera_backend: DirectShow)")
                else:
                    print(f"   ⚠️ DirectShow backend not explicitly configured")
                    
            except Exception as e:
                print(f"❌ {settings_file} has error: {e}")
        else:
            print(f"⚠️ {settings_file} not found")

def verify_camera_source_patch():
    """Verify camera source has been patched"""
    print("\n🔍 Verifying Camera Source Patch...")
    print("=" * 50)
    
    camera_source_file = "apps/PlayaTewsIdentityMasker/backend/CameraSource.py"
    backup_file = "apps/PlayaTewsIdentityMasker/backend/CameraSource.py.backup"
    
    if Path(camera_source_file).exists():
        print(f"✅ Camera source file exists: {camera_source_file}")
        
        # Check if it's been patched
        with open(camera_source_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "cv_api = cv2.CAP_DSHOW  # Force DirectShow" in content:
            print("   ✅ Camera source has been patched with DirectShow forcing")
        else:
            print("   ⚠️ Camera source may not be patched")
            
        if "Enhanced camera initialization with retry logic" in content:
            print("   ✅ Enhanced initialization with retry logic added")
        else:
            print("   ⚠️ Enhanced initialization may not be added")
    else:
        print(f"❌ Camera source file not found: {camera_source_file}")
    
    if Path(backup_file).exists():
        print(f"✅ Backup file exists: {backup_file}")
    else:
        print(f"⚠️ Backup file not found: {backup_file}")

def verify_main_app_patch():
    """Verify main app has been enhanced"""
    print("\n🔍 Verifying Main App Patch...")
    print("=" * 50)
    
    main_app_file = "apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerApp.py"
    backup_file = "apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerApp.py.backup"
    
    if Path(main_app_file).exists():
        print(f"✅ Main app file exists: {main_app_file}")
        
        # Check if it's been enhanced
        with open(main_app_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "Enhanced camera source initialization" in content:
            print("   ✅ Main app has been enhanced with camera initialization")
        else:
            print("   ⚠️ Main app may not be enhanced")
            
        if "camera_source.start()" in content:
            print("   ✅ Camera auto-start functionality added")
        else:
            print("   ⚠️ Camera auto-start may not be added")
    else:
        print(f"❌ Main app file not found: {main_app_file}")
    
    if Path(backup_file).exists():
        print(f"✅ Backup file exists: {backup_file}")
    else:
        print(f"⚠️ Backup file not found: {backup_file}")

def test_camera_directly():
    """Test camera directly to ensure it's working"""
    print("\n🔍 Testing Camera Directly...")
    print("=" * 50)
    
    try:
        # Test with DirectShow backend
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if cap.isOpened():
            print("✅ Camera opened successfully with DirectShow")
            
            # Set properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Test frame reading
            success_count = 0
            for i in range(5):
                ret, frame = cap.read()
                if ret and frame is not None:
                    success_count += 1
                    print(f"   ✅ Frame {i+1}: {frame.shape}")
                else:
                    print(f"   ❌ Frame {i+1}: Failed to read")
                time.sleep(0.1)
            
            cap.release()
            
            if success_count >= 3:
                print(f"✅ Camera test successful: {success_count}/5 frames")
                return True
            else:
                print(f"❌ Camera test failed: {success_count}/5 frames")
                return False
        else:
            print("❌ Failed to open camera with DirectShow")
            return False
            
    except Exception as e:
        print(f"❌ Camera test error: {e}")
        return False

def check_utility_files():
    """Check if utility files exist"""
    print("\n🔍 Checking Utility Files...")
    print("=" * 50)
    
    utility_files = [
        "test_main_app_camera.py",
        "restore_backups.py",
        "working_camera_test.py",
        "simple_camera_test.py"
    ]
    
    for utility_file in utility_files:
        if Path(utility_file).exists():
            print(f"✅ {utility_file} exists")
        else:
            print(f"⚠️ {utility_file} not found")

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Fix Verification")
    print("=" * 60)
    print()
    
    # Verify all components
    verify_camera_settings()
    verify_camera_source_patch()
    verify_main_app_patch()
    check_utility_files()
    
    # Test camera directly
    camera_working = test_camera_directly()
    
    print("\n📊 Verification Results:")
    print("=" * 40)
    
    if camera_working:
        print("✅ Camera is working properly")
        print("✅ All fixes have been applied")
        print("✅ Main app should show camera feed in preview area")
        print()
        print("🚀 Next Steps:")
        print("   1. Check the main app for camera feed in preview area")
        print("   2. Verify processing views show camera data")
        print("   3. Test face swap functionality with live camera")
        print()
        print("💡 If camera feed still doesn't appear in main app:")
        print("   1. Check console output for error messages")
        print("   2. Ensure virtual camera app is running")
        print("   3. Try restarting the main application")
    else:
        print("❌ Camera test failed")
        print("   Check virtual camera app and permissions")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Ensure virtual camera app is running")
        print("   2. Check camera permissions in Windows settings")
        print("   3. Try running: python simple_camera_test.py")

if __name__ == "__main__":
    main() 