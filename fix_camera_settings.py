#!/usr/bin/env python3
"""
Fix missing camera settings in configuration files
"""

import json
import os

def fix_camera_settings():
    """Add camera settings to all configuration files"""
    
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
    
    for file_path in settings_files:
        print(f"🔧 Fixing {file_path}...")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Load existing data or create new
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = {}
        else:
            data = {}
        
        # Add camera settings
        data['camera'] = camera_settings
        
        # Write back to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ {file_path} updated successfully")
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")

if __name__ == "__main__":
    fix_camera_settings() 