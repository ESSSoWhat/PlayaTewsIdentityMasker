#!/usr/bin/env python3
"""
Camera Activation Launcher
Ensures camera source activates properly
"""

import sys
import os
import time
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def launch_with_camera_fix():
    """Launch the app with camera activation fix"""
    
    print("🚀 Camera Activation Launcher")
    print("=" * 50)
    
    # Step 1: Create QApplication
    app = QApplication.instance()
    if app is None:
        print("🔧 Creating QApplication instance...")
        app = QApplication(sys.argv)
        print("✅ QApplication instance created")
    else:
        print("✅ QApplication instance already exists")
    
    try:
        # Step 2: Import and initialize main app
        print("\n🔧 Step 2: Initializing PlayaTewsIdentityMasker...")
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        # Set up userdata path as Path object
        userdata_path = Path(os.path.dirname(os.path.abspath(__file__))) / "userdata"
        print(f"📁 Using userdata path: {userdata_path}")
        
        # Create the main app
        main_app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        print("✅ Main app created successfully")
        
        # Step 3: Force camera source activation
        print("\n🔧 Step 3: Forcing camera source activation...")
        if hasattr(main_app, 'q_live_swap') and hasattr(main_app.q_live_swap, 'camera_source'):
            camera_source = main_app.q_live_swap.camera_source
            
            # Ensure camera source is started
            if not camera_source.is_started():
                print("🔧 Starting camera source...")
                camera_source.start()
                time.sleep(2)
            
            if camera_source.is_started():
                print("✅ Camera source is running")
            else:
                print("⚠️ Camera source may not be running properly")
        
        # Step 4: Show the main window
        if hasattr(main_app, 'main_window'):
            main_app.main_window.show()
            print("✅ Main window displayed")
        
        # Step 5: Wait for initialization
        print("\n⏳ Step 5: Waiting for camera and UI initialization...")
        time.sleep(5)
        
        # Step 6: Final status
        print("\n" + "=" * 50)
        print("🎬 CAMERA ACTIVATION LAUNCH COMPLETE!")
        print("=" * 50)
        print("📺 The PlayaTewsIdentityMasker app should now be visible.")
        print("🎬 Camera source should be activated and working.")
        print()
        print("🔍 To see the camera feed:")
        print("   1. Look for the PlayaTewsIdentityMasker window")
        print("   2. Click on the 'Viewers' tab")
        print("   3. Check the 'Camera Feed' viewer on the left side")
        print("   4. The camera feed should now be visible!")
        print()
        print("🎯 If camera feed is still not visible:")
        print("   - Try clicking on different tabs and back to 'Viewers'")
        print("   - Check camera permissions in Windows")
        print("   - Restart the application if needed")
        
        # Start the event loop
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(launch_with_camera_fix())
