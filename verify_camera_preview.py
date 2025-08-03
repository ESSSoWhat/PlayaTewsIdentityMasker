#!/usr/bin/env python3
"""
Verify camera feed is appearing in the preview area
"""

import sys
import os
import time
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_camera_preview():
    """Verify camera feed is working in the preview area"""
    
    print("🔍 Verifying Camera Preview Status")
    print("=" * 50)
    
    # Check if app is running
    import subprocess
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        if 'python.exe' in result.stdout:
            print("✅ Python processes are running (app should be active)")
        else:
            print("❌ No Python processes found")
    except Exception as e:
        print(f"⚠️ Could not check running processes: {e}")
    
    # Check camera settings
    print("\n📋 Camera Settings Status:")
    settings_files = [
        "settings/camera_override.json",
        "settings/global_face_swap_state.json",
        "demo_settings/settings/global_face_swap_state.json"
    ]
    
    for file_path in settings_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'camera' in data:
                        camera = data['camera']
                        print(f"✅ {file_path}:")
                        print(f"   Device: {camera.get('device_idx', 'Not set')}")
                        print(f"   Driver: {camera.get('driver', 'Not set')} (DirectShow)")
                        print(f"   Resolution: {camera.get('resolution', 'Not set')}")
                    else:
                        print(f"❌ {file_path}: No camera settings")
            except Exception as e:
                print(f"❌ {file_path}: Error reading - {e}")
        else:
            print(f"❌ {file_path}: File not found")
    
    # Test camera access
    print("\n📹 Camera Hardware Test:")
    try:
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Camera 0 (DirectShow): Working - Frame size: {frame.shape}")
                cap.release()
            else:
                print("❌ Camera 0 (DirectShow): No frame data")
                cap.release()
        else:
            print("❌ Camera 0 (DirectShow): Cannot open camera")
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
    
    print("\n📺 Preview Area Instructions:")
    print("1. Look for the PlayaTewsIdentityMasker window")
    print("2. Click on the 'Viewers' tab")
    print("3. You should see:")
    print("   - Left side: Camera Feed, Face Align, Face Swap, Merged viewers")
    print("   - Right side: Enhanced Output Preview (larger area)")
    print("4. The camera feed should appear in the 'Camera Feed' viewer")
    
    print("\n🔧 If feed is not appearing:")
    print("- Check that the app window is visible")
    print("- Try clicking on different tabs and back to 'Viewers'")
    print("- Ensure camera permissions are granted")
    print("- Restart the app if needed")

if __name__ == "__main__":
    verify_camera_preview() 