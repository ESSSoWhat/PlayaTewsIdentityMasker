#!/usr/bin/env python3
"""
Direct App Launcher
Launches PlayaTewsIdentityMasker with proper path setup
"""

import sys
from pathlib import Path


def main() -> int:
    # Add the project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    print("🚀 Starting PlayaTewsIdentityMasker...")
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python path: {sys.path[0]}")
    
    try:
        # Import and run the main application
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import (
            PlayaTewsIdentityMaskerApp
        )
        
        userdata_path = project_root / "userdata"
        print(f"📂 Userdata path: {userdata_path}")
        
        # Create and run the application
        app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        
        # Show the main window
        if hasattr(app, 'main_window'):
            app.main_window.show()
            print("✅ Main window displayed")
        
        # Start the application event loop
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 