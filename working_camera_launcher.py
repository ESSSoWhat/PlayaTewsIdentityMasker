#!/usr/bin/env python3
"""
Working Camera Launcher
Bypasses API issues and directly activates camera source
"""

import sys
import os
import time
import cv2
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def launch_with_working_camera():
    """Launch the app with working camera fix"""
    
    print("🚀 Working Camera Launcher")
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
        # Step 2: Test camera directly first
        print("\n🔍 Step 2: Testing camera directly...")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Camera test successful: {frame.shape}")
                cap.release()
            else:
                print("❌ Camera opened but no frame")
                cap.release()
                return 1
        else:
            print("❌ Camera test failed")
            return 1
        
        # Step 3: Import and initialize main app
        print("\n🔧 Step 3: Initializing PlayaTewsIdentityMasker...")
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        # Set up userdata path as Path object
        userdata_path = Path(os.path.dirname(os.path.abspath(__file__))) / "userdata"
        print(f"📁 Using userdata path: {userdata_path}")
        
        # Create the main app
        main_app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        print("✅ Main app created successfully")
        
        # Step 4: Force camera source activation with direct approach
        print("\n🔧 Step 4: Forcing camera source activation...")
        if hasattr(main_app, 'q_live_swap') and hasattr(main_app.q_live_swap, 'camera_source'):
            camera_source = main_app.q_live_swap.camera_source
            
            # Ensure camera source is started
            if not camera_source.is_started():
                print("🔧 Starting camera source...")
                camera_source.start()
                time.sleep(2)
            
            if camera_source.is_started():
                print("✅ Camera source is running")
                
                # Get the worker and force camera activation
                try:
                    worker = camera_source.get_worker()
                    if worker and hasattr(worker, 'vcap'):
                        if worker.vcap is None:
                            print("🔧 Creating vcap directly...")
                            # Create vcap directly
                            worker.vcap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                            if worker.vcap.isOpened():
                                print("✅ vcap created and opened successfully")
                                # Set properties
                                worker.vcap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                                worker.vcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                                worker.vcap.set(cv2.CAP_PROP_FPS, 30)
                            else:
                                print("❌ Failed to create vcap")
                        else:
                            print("✅ vcap already exists")
                except Exception as e:
                    print(f"⚠️ Could not access worker: {e}")
            else:
                print("⚠️ Camera source may not be running properly")
        
        # Step 5: Show the main window
        if hasattr(main_app, 'main_window'):
            main_app.main_window.show()
            print("✅ Main window displayed")
        
        # Step 6: Wait for initialization
        print("\n⏳ Step 6: Waiting for camera and UI initialization...")
        time.sleep(5)
        
        # Step 7: Final status
        print("\n" + "=" * 50)
        print("🎬 WORKING CAMERA LAUNCH COMPLETE!")
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
    sys.exit(launch_with_working_camera())
