#!/usr/bin/env python3
"""
Camera Feed Fix Script
Helps configure the camera device for PlayaTewsIdentityMasker
"""

import json
import os
from pathlib import Path

def fix_camera_settings():
    """Fix camera settings to use the working camera device"""
    print("🔧 Fixing Camera Feed Settings...")
    print("=" * 50)
    
    # Camera settings to apply
    camera_settings = {
        "device_idx": 0,  # Use camera 0 (your working camera)
        "driver": 1,      # DirectShow (working backend)
        "resolution": 3,  # 1280x720 (matches your camera)
        "fps": 30.0,     # 30fps (matches your camera)
        "rotation": 0,   # No rotation
        "flip_horizontal": False
    }
    
    # Find and update settings files
    settings_files = [
        "settings/app.dat",
        "settings/states.dat",
        "simple_settings/app.dat",
        "simple_settings/states.dat"
    ]
    
    for settings_file in settings_files:
        if os.path.exists(settings_file):
            print(f"📝 Updating {settings_file}...")
            try:
                # Read existing settings
                with open(settings_file, 'r') as f:
                    data = f.read()
                
                # Update camera settings
                updated = False
                lines = data.split('\n')
                
                for i, line in enumerate(lines):
                    if 'CameraSource' in line and 'device_idx' in line:
                        lines[i] = f'CameraSource.device_idx = {camera_settings["device_idx"]}'
                        updated = True
                    elif 'CameraSource' in line and 'driver' in line:
                        lines[i] = f'CameraSource.driver = {camera_settings["driver"]}'
                        updated = True
                    elif 'CameraSource' in line and 'resolution' in line:
                        lines[i] = f'CameraSource.resolution = {camera_settings["resolution"]}'
                        updated = True
                    elif 'CameraSource' in line and 'fps' in line:
                        lines[i] = f'CameraSource.fps = {camera_settings["fps"]}'
                        updated = True
                
                # Write updated settings
                with open(settings_file, 'w') as f:
                    f.write('\n'.join(lines))
                
                if updated:
                    print(f"  ✅ Updated camera settings")
                else:
                    print(f"  ⚠️ No camera settings found to update")
                    
            except Exception as e:
                print(f"  ❌ Error updating {settings_file}: {e}")
        else:
            print(f"📄 {settings_file} not found (skipping)")
    
    print("\n✅ Camera settings updated!")
    print("\n📋 Applied Settings:")
    print(f"  Device Index: {camera_settings['device_idx']} (Son's S24 Ultra)")
    print(f"  Driver: {camera_settings['driver']} (DirectShow)")
    print(f"  Resolution: {camera_settings['resolution']} (1280x720)")
    print(f"  FPS: {camera_settings['fps']}")
    print(f"  Rotation: {camera_settings['rotation']} (0 degrees)")
    print(f"  Flip Horizontal: {camera_settings['flip_horizontal']}")

def create_camera_config():
    """Create a camera configuration file"""
    print("\n📄 Creating Camera Configuration...")
    
    config = {
        "camera_device": 0,
        "camera_name": "Son's S24 Ultra (Windows Virtual Camera)",
        "resolution": "1280x720",
        "fps": 30.0,
        "driver": "DirectShow",
        "working": True
    }
    
    with open("camera_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created camera_config.json")

def show_troubleshooting_tips():
    """Show troubleshooting tips for camera feed issues"""
    print("\n🔧 Troubleshooting Tips for Camera Feed:")
    print("=" * 50)
    print("1. 📱 Close other camera apps:")
    print("   - Zoom, Teams, Skype, Discord")
    print("   - Any app using the camera")
    print()
    print("2. 🔄 Restart the PlayaTewsIdentityMasker app")
    print("   - Close the app completely")
    print("   - Run: python run_obs_style.py")
    print()
    print("3. ⚙️ Check camera settings in the app:")
    print("   - Go to Camera Source settings")
    print("   - Select Device Index: 0")
    print("   - Select Driver: DirectShow")
    print("   - Set Resolution: 1280x720")
    print()
    print("4. 🔐 Check Windows camera permissions:")
    print("   - Settings > Privacy > Camera")
    print("   - Allow apps to access camera")
    print()
    print("5. 🖥️ If still no feed:")
    print("   - Try different camera drivers")
    print("   - Check if camera works in other apps")
    print("   - Restart computer if camera is stuck")

def main():
    """Main function"""
    print("🎬 PlayaTewsIdentityMasker - Camera Feed Fix")
    print("=" * 60)
    
    # Fix camera settings
    fix_camera_settings()
    
    # Create config file
    create_camera_config()
    
    # Show troubleshooting tips
    show_troubleshooting_tips()
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("1. Restart the PlayaTewsIdentityMasker app")
    print("2. Check if camera feed appears")
    print("3. If no feed, follow the troubleshooting tips above")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main() 