#!/usr/bin/env python3
"""
Fix Camera Backend Issue for PlayaTewsIdentityMasker
Forces DirectShow backend which works with virtual cameras
"""

import json
import os
import sys
from pathlib import Path

def create_camera_fix_settings():
    """Create camera settings that force DirectShow backend"""
    
    # Camera settings that work with virtual cameras
    camera_settings = {
        "camera_source": {
            "device_idx": 0,  # Use camera index 0
            "driver": 1,      # DirectShow backend (1 = DSHOW)
            "resolution": 3,  # 1280x720
            "fps": 30.0,      # 30 FPS
            "rotation": 0,    # No rotation
            "flip_horizontal": False,
            "settings_by_idx": {}
        }
    }
    
    return camera_settings

def apply_camera_fix():
    """Apply the camera backend fix"""
    print("🔧 Applying Camera Backend Fix...")
    print("=" * 50)
    
    # Create settings directory if it doesn't exist
    settings_dir = Path("settings")
    settings_dir.mkdir(exist_ok=True)
    
    # Create camera settings file
    camera_settings_file = settings_dir / "camera_backend_fix.json"
    camera_settings = create_camera_fix_settings()
    
    with open(camera_settings_file, 'w') as f:
        json.dump(camera_settings, f, indent=2)
    
    print(f"✅ Camera settings saved to: {camera_settings_file}")
    print("📹 Backend: DirectShow (forced)")
    print("📱 Camera Index: 0")
    print("📐 Resolution: 1280x720")
    print("🎬 FPS: 30")
    
    # Also update the global face swap state
    global_state_file = settings_dir / "global_face_swap_state.json"
    global_state = {
        "enabled": True,
        "camera_backend": "DirectShow",
        "camera_index": 0,
        "timestamp": str(Path().stat().st_mtime)
    }
    
    with open(global_state_file, 'w') as f:
        json.dump(global_state, f, indent=2)
    
    print(f"✅ Global state updated: {global_state_file}")
    
    return True

def create_quick_fix_bat():
    """Create a batch file for quick camera fix"""
    bat_content = """@echo off
echo 🔧 PlayaTewsIdentityMasker - Camera Backend Fix
echo ================================================
echo.
echo 📹 Fixing camera backend to DirectShow...
echo.

REM Run the camera fix script
python fix_camera_backend.py

echo.
echo ✅ Camera fix applied!
echo 🚀 Starting PlayaTewsIdentityMasker with DirectShow backend...
echo.

REM Start the app with standard settings
python main.py run PlayaTewsIdentityMasker

pause
"""
    
    with open("fix_camera_and_start.bat", 'w') as f:
        f.write(bat_content)
    
    print("✅ Created: fix_camera_and_start.bat")
    print("   Run this file to fix camera and start the app")

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Backend Fix")
    print("=" * 60)
    print()
    print("🔍 Issue: Camera feed not appearing in preview area")
    print("🎯 Solution: Force DirectShow backend (works with virtual cameras)")
    print()
    
    try:
        # Apply the camera fix
        success = apply_camera_fix()
        
        if success:
            # Create quick fix batch file
            create_quick_fix_bat()
            
            print()
            print("🎉 Camera Backend Fix Complete!")
            print("=" * 40)
            print()
            print("📋 What was fixed:")
            print("   ✅ Forced DirectShow backend")
            print("   ✅ Set camera index to 0")
            print("   ✅ Configured 1280x720 resolution")
            print("   ✅ Set 30 FPS for smooth video")
            print()
            print("🚀 Next steps:")
            print("   1. Run: fix_camera_and_start.bat")
            print("   2. Or manually start: start_playatews.bat standard")
            print("   3. Camera feed should now appear in preview area")
            print()
            print("💡 If issues persist:")
            print("   - Ensure virtual camera app is running")
            print("   - Check Windows camera privacy settings")
            print("   - Restart the virtual camera app")
            
        else:
            print("❌ Failed to apply camera fix")
            return False
            
    except Exception as e:
        print(f"❌ Error applying camera fix: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 