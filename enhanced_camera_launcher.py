#!/usr/bin/env python3
"""
Enhanced Camera Source Launcher
Directly activates camera source and bypasses all API issues
"""

import sys
import os
import time
import cv2
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def force_camera_source_activation():
    """Force camera source to activate by directly manipulating the backend"""
    
    print("Enhanced Camera Source Launcher")
    print("=" * 50)
    
    # Step 1: Create QApplication
    print("Creating QApplication instance...")
    app = QApplication(sys.argv)
    print("QApplication instance created")
    
    # Step 2: Test camera directly
    print("Testing camera directly...")
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Camera test successful: {frame.shape}")
                cap.release()
            else:
                print("Camera test failed: No frame received")
                return False
        else:
            print("Camera test failed: Could not open camera")
            return False
    except Exception as e:
        print(f"Camera test failed: {e}")
        return False
    
    # Step 3: Import and initialize main app
    print("Initializing PlayaTewsIdentityMasker...")
    try:
        sys.path.insert(0, str(Path.cwd()))
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        userdata_path = Path.cwd() / "userdata"
        print(f"Using userdata path: {userdata_path}")
        
        # Create main app
        main_app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        print("Main app created successfully")
        
        # Step 4: Force camera source activation
        print("Forcing camera source activation...")
        
        # Get the camera source from the main app
        if hasattr(main_app, 'q_live_swap') and hasattr(main_app.q_live_swap, 'camera_source'):
            camera_source = main_app.q_live_swap.camera_source
            
            # Force start the camera source
            if hasattr(camera_source, 'start'):
                camera_source.start()
                print("Camera source started")
            
            # Force enable the camera source
            if hasattr(camera_source, 'enable'):
                camera_source.enable()
                print("Camera source enabled")
            
            # Check if there's a worker and force vcap creation
            if hasattr(camera_source, 'worker') and camera_source.worker:
                worker = camera_source.worker
                
                # Force create vcap if it doesn't exist
                if not hasattr(worker, 'vcap') or worker.vcap is None:
                    print("Creating vcap directly...")
                    worker.vcap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                    if worker.vcap.isOpened():
                        print("vcap created and opened successfully")
                    else:
                        print("Failed to create vcap")
                
                # Force start the worker
                if hasattr(worker, 'start'):
                    worker.start()
                    print("Camera source worker started")
        
        # Step 5: Display main window
        print("Displaying main window...")
        if hasattr(main_app, 'main_window'):
            main_app.main_window.show()
            print("Main window displayed")
        
        # Step 6: Wait for initialization
        print("Waiting for camera and UI initialization...")
        time.sleep(3)
        
        print("\n" + "=" * 50)
        print("ENHANCED CAMERA LAUNCH COMPLETE!")
        print("=" * 50)
        print("The PlayaTewsIdentityMasker app should now be visible.")
        print("Camera source should be activated and working.")
        print("\nTo see the camera feed:")
        print("  1. Look for the PlayaTewsIdentityMasker window")
        print("  2. Click on the 'Viewers' tab")
        print("  3. Check the 'Camera Feed' viewer on the left side")
        print("  4. The camera feed should now be visible!")
        print("\nIf camera feed is still not visible:")
        print("  - Try clicking on different tabs and back to 'Viewers'")
        print("  - Check camera permissions in Windows")
        print("  - Restart the application if needed")
        
        # Start the application event loop
        return app.exec_()
        
    except Exception as e:
        print(f"Error launching app: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    force_camera_source_activation()
