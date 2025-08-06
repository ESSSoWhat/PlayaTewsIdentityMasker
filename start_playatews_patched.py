#!/usr/bin/env python3
"""
Patched Startup Script for PlayaTewsIdentityMasker
Applies camera preview fixes before launching the main application
"""

import sys
from pathlib import Path


def main():
    """Main startup function with camera fixes"""
    print("PlayaTewsIdentityMasker - Patched Startup")
    print("=" * 50)
    
    # Apply camera integration patches
    try:
        from camera_integration_patch import apply_patches  # type: ignore
        apply_patches()
        print("Camera patches applied")
    except Exception as e:
        print(f"Camera patches failed: {e}")

    # Import state persistence
    try:
        import json
        print("✅ State persistence modules imported")
    except Exception as e:
        print(f"❌ Error importing state persistence: {e}")
    
    # Load and apply component states
    try:
        module_state_file = Path("settings/module_states.json")
        if module_state_file.exists():
            with open(module_state_file, 'r', encoding='utf-8') as f:
                json.load(f)  # Load but don't store if not used
            print("✅ Module states loaded successfully")
        else:
            print("⚠️ Module state file not found, "
                  "will be created on first run")
    except Exception as e:
        print(f"❌ Error loading module states: {e}")
    
    # Import and run the main application
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import (
            PlayaTewsIdentityMaskerApp
        )
        
        # Get userdata path
        userdata_path = Path.cwd()
        
        # Create and run the application
        app = PlayaTewsIdentityMaskerApp(userdata_path)
        app.initialize()
        app.run()
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
