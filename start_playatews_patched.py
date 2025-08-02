#!/usr/bin/env python3
"""
Patched Startup Script for PlayaTewsIdentityMasker
Applies camera preview fixes before launching the main application
"""

import sys
import os
from pathlib import Path

def main():
    """Main startup function with camera fixes"""
    print("PlayaTewsIdentityMasker - Patched Startup")
    print("=" * 50)
    
    # Apply camera integration patches
    try:
        from camera_integration_patch import apply_patches
        apply_patches()
        print("Camera patches applied")
    except Exception as e:
        print(f"Camera patches failed: {e}")
    
    # Import and run the main application
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
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
