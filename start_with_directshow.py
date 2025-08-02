#!/usr/bin/env python3
"""
Start PlayaTewsIdentityMasker with DirectShow Backend Forced
This ensures the camera feed appears in the preview area
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def force_directshow_backend():
    """Force DirectShow backend in the app settings"""
    print("🔧 Forcing DirectShow Backend...")
    
    # Create a temporary settings override
    settings_override = {
        "camera_source": {
            "device_idx": 0,
            "driver": 1,  # DirectShow
            "resolution": 3,  # 1280x720
            "fps": 30.0,
            "rotation": 0,
            "flip_horizontal": False,
            "settings_by_idx": {}
        }
    }
    
    # Save to a temporary file that the app can read
    temp_settings = Path("temp_camera_settings.json")
    with open(temp_settings, 'w') as f:
        json.dump(settings_override, f, indent=2)
    
    print("✅ DirectShow settings prepared")
    return temp_settings

def start_app_with_directshow():
    """Start the app with DirectShow backend"""
    print("🚀 Starting PlayaTewsIdentityMasker with DirectShow Backend...")
    print("=" * 60)
    
    try:
        # Force DirectShow backend
        temp_settings = force_directshow_backend()
        
        # Set environment variable to force DirectShow
        env = os.environ.copy()
        env['FORCE_DIRECTSHOW'] = '1'
        env['CAMERA_BACKEND'] = 'DirectShow'
        
        print("📹 Camera Backend: DirectShow (forced)")
        print("📱 Camera Index: 0")
        print("📐 Resolution: 1280x720")
        print("🎬 FPS: 30")
        print()
        print("🎯 Starting application...")
        print("💡 Camera feed should now appear in preview area")
        print()
        
        # Start the main application
        cmd = [sys.executable, "main.py", "run", "PlayaTewsIdentityMasker"]
        subprocess.run(cmd, env=env)
        
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        return False
    
    finally:
        # Clean up temporary file
        if 'temp_settings' in locals():
            try:
                temp_settings.unlink(missing_ok=True)
            except:
                pass
    
    return True

def main():
    print("🎬 PlayaTewsIdentityMasker - DirectShow Backend Launcher")
    print("=" * 60)
    print()
    print("🔍 Issue: Camera feed not appearing in preview area")
    print("🎯 Solution: Force DirectShow backend (compatible with virtual cameras)")
    print()
    
    # Check if virtual camera is available
    print("🔍 Checking camera availability...")
    try:
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✅ Virtual camera detected and working with DirectShow")
                print(f"📐 Frame size: {frame.shape}")
            else:
                print("⚠️ Camera opened but frame read failed")
            cap.release()
        else:
            print("❌ Camera not accessible with DirectShow")
            print("💡 Please ensure your virtual camera app is running")
            return False
    except Exception as e:
        print(f"❌ Error checking camera: {e}")
        return False
    
    print()
    
    # Start the app
    success = start_app_with_directshow()
    
    if not success:
        print("❌ Failed to start application")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 