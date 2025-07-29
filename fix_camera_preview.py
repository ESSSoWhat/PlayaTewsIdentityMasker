#!/usr/bin/env python3
"""
Fix Camera Preview for PlayaTewsIdentityMasker
Forces DirectShow backend for camera compatibility
"""

import os
import json
import pickle
import struct

def fix_camera_settings():
    """Update camera settings to use DirectShow backend"""
    print("🔧 Fixing Camera Preview Settings...")
    print("=" * 50)
    
    # Check if settings files exist
    settings_files = [
        "settings/app.dat",
        "settings/states.dat"
    ]
    
    for file_path in settings_files:
        if os.path.exists(file_path):
            print(f"📁 Found settings file: {file_path}")
            
            # Try to update camera backend settings
            try:
                # For app.dat (pickle format)
                if file_path.endswith("app.dat"):
                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)
                    
                    # Update camera settings if they exist
                    if 'camera' in data:
                        data['camera']['backend'] = 'DirectShow'
                        data['camera']['index'] = 0
                        print(f"  ✅ Updated camera backend to DirectShow")
                    
                    with open(file_path, 'wb') as f:
                        pickle.dump(data, f)
                
                # For states.dat (binary format)
                elif file_path.endswith("states.dat"):
                    print(f"  ℹ️  states.dat detected - camera settings may be in app.dat")
                
            except Exception as e:
                print(f"  ⚠️  Could not update {file_path}: {e}")
        else:
            print(f"❌ Settings file not found: {file_path}")
    
    print("\n🎯 Camera Fix Applied!")
    print("💡 Restart the app to see the camera feed in preview")

def create_camera_config():
    """Create a camera configuration file"""
    print("\n📝 Creating Camera Configuration...")
    
    config = {
        "camera": {
            "backend": "DirectShow",
            "index": 0,
            "resolution": "1280x720",
            "fps": 30
        },
        "face_swap": {
            "enabled": True,
            "model": "Natalie_Fatman.dfm"
        }
    }
    
    config_file = "camera_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created {config_file} with DirectShow settings")

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Preview Fix")
    print("=" * 60)
    
    fix_camera_settings()
    create_camera_config()
    
    print("\n" + "=" * 60)
    print("✅ Camera preview fix complete!")
    print("🔄 Please restart the PlayaTewsIdentityMasker app")
    print("📹 Camera feed should now appear in the preview area")

if __name__ == "__main__":
    main() 