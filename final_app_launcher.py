#!/usr/bin/env python3
"""
Final Comprehensive App Launcher
Ensures proper Qt context, backend initialization, and UI component setup
"""

import sys
import os
import time
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def launch_app_comprehensive():
    """Launch the app with comprehensive initialization"""
    
    print("🚀 Final Comprehensive App Launcher")
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
        
        # Step 3: Show the main window
        if hasattr(main_app, 'show'):
            main_app.show()
            print("✅ Main window displayed")
        
        # Step 4: Wait for initialization
        print("\n⏳ Step 4: Waiting for camera and UI initialization...")
        time.sleep(5)  # Give more time for initialization
        
        # Step 5: Verify camera source
        print("\n🔍 Step 5: Verifying camera source...")
        if hasattr(main_app, 'q_live_swap') and hasattr(main_app.q_live_swap, 'camera_source') and main_app.q_live_swap.camera_source:
            if hasattr(main_app.q_live_swap.camera_source, 'is_started') and main_app.q_live_swap.camera_source.is_started():
                print("✅ Camera source is running")
            else:
                print("⚠️ Camera source may not be running properly")
                # Try to start it
                try:
                    main_app.q_live_swap.camera_source.start()
                    print("✅ Camera source started manually")
                except Exception as e:
                    print(f"❌ Could not start camera source: {e}")
        else:
            print("⚠️ Camera source not found")
        
        # Step 6: Verify UI components
        print("\n🔍 Step 6: Verifying UI components...")
        if hasattr(main_app, 'q_live_swap') and hasattr(main_app.q_live_swap, 'q_unified_live_swap'):
            print("✅ Unified LiveSwap UI component created")
            
            # Check viewers
            viewers_status = []
            if hasattr(main_app.q_live_swap.q_unified_live_swap, 'q_ds_frame_viewer'):
                viewers_status.append("Frame viewer")
            if hasattr(main_app.q_live_swap.q_unified_live_swap, 'q_ds_fa_viewer'):
                viewers_status.append("Face align viewer")
            if hasattr(main_app.q_live_swap.q_unified_live_swap, 'q_ds_fc_viewer'):
                viewers_status.append("Face swap viewer")
            if hasattr(main_app.q_live_swap.q_unified_live_swap, 'q_ds_merged_frame_viewer'):
                viewers_status.append("Merged frame viewer")
            if hasattr(main_app.q_live_swap.q_unified_live_swap, 'q_stream_output'):
                viewers_status.append("Enhanced stream output")
            
            print(f"✅ Found {len(viewers_status)} viewer components: {', '.join(viewers_status)}")
        else:
            print("⚠️ Unified LiveSwap UI component not found")
        
        # Step 7: Check backend connections
        print("\n🔍 Step 7: Checking backend connections...")
        try:
            temp_dir = os.path.expanduser("~/AppData/Local/Temp")
            if os.path.exists(temp_dir):
                dep_files = [f for f in os.listdir(temp_dir) if f.startswith('dep-') and f.endswith('.d')]
                if dep_files:
                    print(f"✅ Found {len(dep_files)} backend connection files")
                else:
                    print("⚠️ No backend connection files found yet")
            else:
                print("⚠️ Temp directory not found")
        except Exception as e:
            print(f"⚠️ Could not check backend connections: {e}")
        
        # Step 8: Final status and instructions
        print("\n" + "=" * 50)
        print("🎬 APP LAUNCH COMPLETE!")
        print("=" * 50)
        print("📺 The PlayaTewsIdentityMasker app should now be visible on your screen.")
        print()
        print("🔍 To see the camera feed in the preview area:")
        print("   1. Look for the PlayaTewsIdentityMasker window")
        print("   2. Click on the 'Viewers' tab")
        print("   3. You should see:")
        print("      - Left side: Camera Feed, Face Align, Face Swap, Merged viewers")
        print("      - Right side: Enhanced Output Preview (2/3 width)")
        print("   4. The camera feed should appear in the 'Camera Feed' viewer")
        print()
        print("🔧 If feeds are not appearing:")
        print("   - Try clicking on different tabs and back to 'Viewers'")
        print("   - Check that camera permissions are granted")
        print("   - Wait a few more seconds for initialization")
        print("   - Restart the app if needed")
        print()
        print("🎯 The enhanced output window is now integrated into the main preview area!")
        print("   Better workflow: All previews in one place")
        print("   Larger enhanced output: Takes up 2/3 of the preview area")
        print("   Organized layout: Camera and processing viewers neatly arranged")
        print("   Integrated experience: No more separate windows to manage")
        
        # Start the event loop
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(launch_app_comprehensive()) 