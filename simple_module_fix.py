#!/usr/bin/env python3
"""
Simple Module Activation Fix
Direct fix for module activation issues
"""

import sys
import os
import json
from pathlib import Path

def create_simple_module_fix():
    """Create a simple fix for module activation"""
    
    print("Creating Simple Module Activation Fix...")
    
    # Create comprehensive settings to force module activation
    settings_dir = Path("settings")
    settings_dir.mkdir(exist_ok=True)
    
    # Camera source state with forced activation
    camera_state = {
        "device_idx": 0,
        "driver": 1,  # DirectShow
        "resolution": [640, 480],
        "fps": 30,
        "enabled": True,
        "auto_start": True,
        "activated": True,
        "force_enable": True
    }
    
    with open(settings_dir / "camera_source_state.json", "w") as f:
        json.dump(camera_state, f, indent=2)
    
    # Global face swap state with all modules forced enabled
    global_state = {
        "camera_source": {
            "enabled": True,
            "device_idx": 0,
            "driver": 1,
            "auto_start": True,
            "activated": True,
            "force_enable": True
        },
        "face_detector": {
            "enabled": True,
            "auto_start": True,
            "activated": True,
            "force_enable": True
        },
        "face_marker": {
            "enabled": True,
            "auto_start": True,
            "activated": True,
            "force_enable": True
        },
        "face_aligner": {
            "enabled": True,
            "auto_start": True,
            "activated": True,
            "force_enable": True
        },
        "face_animator": {
            "enabled": True,
            "auto_start": True,
            "activated": True,
            "force_enable": True
        },
        "face_swap_insight": {
            "enabled": True,
            "auto_start": True,
            "activated": True,
            "force_enable": True
        },
        "face_swap_dfm": {
            "enabled": True,
            "auto_start": True,
            "activated": True,
            "force_enable": True
        },
        "frame_adjuster": {
            "enabled": True,
            "auto_start": True,
            "activated": True,
            "force_enable": True
        },
        "face_merger": {
            "enabled": True,
            "auto_start": True,
            "activated": True,
            "force_enable": True
        },
        "stream_output": {
            "enabled": True,
            "auto_start": True,
            "activated": True,
            "force_enable": True
        },
        "face_swap": {
            "enabled": True,
            "auto_start": True,
            "activated": True,
            "force_enable": True
        }
    }
    
    with open(settings_dir / "global_face_swap_state.json", "w") as f:
        json.dump(global_state, f, indent=2)
    
    # Demo settings
    demo_settings_dir = Path("demo_settings") / "settings"
    demo_settings_dir.mkdir(parents=True, exist_ok=True)
    
    with open(demo_settings_dir / "global_face_swap_state.json", "w") as f:
        json.dump(global_state, f, indent=2)
    
    # Create camera override file
    camera_override = {
        "device_idx": 0,
        "driver": 1,
        "resolution": [640, 480],
        "fps": 30,
        "enabled": True,
        "auto_start": True,
        "activated": True,
        "force_enable": True
    }
    
    with open("camera_override.json", "w") as f:
        json.dump(camera_override, f, indent=2)
    
    print("Simple module activation fix created!")
    print("Settings files updated with forced module activation")
    print("Camera override file created")
    
    print("\nTo test the fix:")
    print("   Run: .\\start_enhanced_camera.bat")
    
    return True

if __name__ == "__main__":
    create_simple_module_fix() 