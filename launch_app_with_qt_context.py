#!/usr/bin/env python3
"""
Launch PlayaTewsIdentityMasker with proper QApplication context
and ensure all UI components are properly initialized
"""

import sys
import os
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def launch_app_with_qt_context():
    """Launch the app with proper QApplication initialization"""
    
    print("🚀 Launching PlayaTewsIdentityMasker with proper Qt context...")
    
    # Create QApplication if it doesn't exist
    app = QApplication.instance()
    if app is None:
        print("🔧 Creating QApplication instance...")
        app = QApplication(sys.argv)
        print("✅ QApplication instance created")
    else:
        print("✅ QApplication instance already exists")
    
    try:
        # Import the main app
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        print("🔧 Initializing PlayaTewsIdentityMasker...")
        
        # Set up userdata path
        userdata_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "userdata")
        print(f"📁 Using userdata path: {userdata_path}")
        
        # Create the main app with userdata path
        main_app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        
        # Show the main window
        if hasattr(main_app, 'show'):
            main_app.show()
            print("✅ Main window displayed")
        
        # Wait for initialization
        print("⏳ Waiting for camera and UI initialization...")
        time.sleep(3)
        
        # Check camera source status
        if hasattr(main_app, 'camera_source') and main_app.camera_source:
            if hasattr(main_app.camera_source, 'is_started') and main_app.camera_source.is_started():
                print("✅ Camera source is running")
            else:
                print("⚠️ Camera source may not be running properly")
        else:
            print("⚠️ Camera source not found")
        
        # Check UI components
        if hasattr(main_app, 'q_unified_live_swap'):
            print("✅ Unified LiveSwap UI component created")
            
            # Check if viewers are present
            if hasattr(main_app.q_unified_live_swap, 'q_ds_frame_viewer'):
                print("✅ Frame viewer component present")
            else:
                print("⚠️ Frame viewer component missing")
                
            if hasattr(main_app.q_unified_live_swap, 'q_stream_output'):
                print("✅ Enhanced stream output component present")
            else:
                print("⚠️ Enhanced stream output component missing")
        else:
            print("⚠️ Unified LiveSwap UI component not found")
        
        print("🎬 App launched successfully!")
        print("📺 Check the 'Viewers' tab for the integrated preview area")
        print("   - Left side: Camera feed and processing viewers")
        print("   - Right side: Enhanced Output Preview (2/3 width)")
        print()
        print("🔧 If feeds are not appearing:")
        print("   1. Click on the 'Viewers' tab")
        print("   2. Check that camera permissions are granted")
        print("   3. Try clicking on different tabs and back to 'Viewers'")
        print("   4. Restart the app if needed")
        
        # Start the event loop
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(launch_app_with_qt_context()) 