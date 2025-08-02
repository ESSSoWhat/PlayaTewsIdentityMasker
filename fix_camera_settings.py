#!/usr/bin/env python3
"""
Fix Camera Settings for PlayaTewsIdentityMasker
Adds missing camera configuration to settings files
"""

import json
from pathlib import Path

def fix_camera_settings():
    """Fix camera settings in all configuration files"""
    print("🔧 Fixing Camera Settings...")
    print("=" * 50)
    
    # Camera settings to add
    camera_settings = {
        "device_idx": 0,
        "driver": 1,  # DirectShow
        "resolution": 3,  # 1280x720
        "fps": 30.0,
        "rotation": 0,
        "flip_horizontal": False
    }
    
    settings_files = [
        "settings/camera_override.json",
        "settings/global_face_swap_state.json",
        "demo_settings/settings/global_face_swap_state.json"
    ]
    
    for settings_file in settings_files:
        settings_path = Path(settings_file)
        
        # Create directory if it doesn't exist
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing settings or create new
        if settings_path.exists():
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = {}
        else:
            data = {}
        
        # Add camera settings
        data['camera'] = camera_settings
        
        # Save updated settings
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ {settings_file}: Camera settings added")
        except Exception as e:
            print(f"❌ {settings_file}: Error saving - {e}")

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Settings Fix")
    print("=" * 50)
    print()
    
    fix_camera_settings()
    
    print("\n📊 Settings Fix Complete!")
    print("=" * 30)

if __name__ == "__main__":
    main() 