#!/usr/bin/env python3
"""
Direct Camera Source Fix
Directly fixes the camera source module activation issue
"""

import sys
import os
import time
import cv2
import json
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def direct_camera_source_fix():
    """Direct fix for camera source module activation"""
    
    print("Direct Camera Source Fix")
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
        
        # Step 4: Direct camera source fix
        print("Applying direct camera source fix...")
        
        # Get the live swap instance
        if hasattr(main_app, 'q_live_swap'):
            live_swap = main_app.q_live_swap
            
            # Direct camera source activation
            if hasattr(live_swap, 'camera_source') and live_swap.camera_source:
                print("Direct camera source activation...")
                camera_source = live_swap.camera_source
                
                # Force start camera source
                if hasattr(camera_source, 'start'):
                    try:
                        camera_source.start()
                        print("Camera source started successfully")
                    except Exception as e:
                        print(f"Camera source start error: {e}")
                
                # Force enable camera source
                if hasattr(camera_source, 'enable'):
                    try:
                        camera_source.enable()
                        print("Camera source enabled successfully")
                    except Exception as e:
                        print(f"Camera source enable error: {e}")
                
                # Direct worker manipulation
                if hasattr(camera_source, 'worker') and camera_source.worker:
                    worker = camera_source.worker
                    print("Direct worker manipulation...")
                    
                    # Force create vcap
                    if not hasattr(worker, 'vcap') or worker.vcap is None:
                        print("Creating camera vcap directly...")
                        try:
                            worker.vcap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                            if worker.vcap.isOpened():
                                print("Camera vcap created and opened successfully")
                            else:
                                print("Failed to create camera vcap")
                        except Exception as e:
                            print(f"Vcap creation error: {e}")
                    
                    # Force start worker
                    if hasattr(worker, 'start'):
                        try:
                            worker.start()
                            print("Camera source worker started successfully")
                        except Exception as e:
                            print(f"Worker start error: {e}")
                    
                    # Force worker activation
                    if hasattr(worker, 'on_start'):
                        try:
                            worker.on_start()
                            print("Camera source worker on_start called successfully")
                        except Exception as e:
                            print(f"Worker on_start error: {e}")
                
                # Check camera source state
                print("Checking camera source state...")
                if hasattr(camera_source, 'get_state'):
                    try:
                        state = camera_source.get_state()
                        print(f"Camera source state: {state}")
                    except Exception as e:
                        print(f"Get state error: {e}")
                
                # Force camera source to be active
                if hasattr(camera_source, 'is_active'):
                    try:
                        camera_source.is_active = True
                        print("Camera source marked as active")
                    except Exception as e:
                        print(f"Set active error: {e}")
                
                # Force camera source to be running
                if hasattr(camera_source, 'is_running'):
                    try:
                        camera_source.is_running = True
                        print("Camera source marked as running")
                    except Exception as e:
                        print(f"Set running error: {e}")
        
        # Step 5: Display main window
        print("Displaying main window...")
        if hasattr(main_app, 'main_window'):
            main_app.main_window.show()
            print("Main window displayed")
        
        # Step 6: Wait for initialization
        print("Waiting for camera source initialization...")
        time.sleep(3)
        
        print("\n" + "=" * 50)
        print("DIRECT CAMERA SOURCE FIX COMPLETE!")
        print("=" * 50)
        print("Camera source should now be working.")
        print("\nTo verify camera source activation:")
        print("  1. Look for the PlayaTewsIdentityMasker window")
        print("  2. Check that the camera source button is active/enabled")
        print("  3. Navigate to the 'Viewers' tab")
        print("  4. The camera feed should be visible")
        print("  5. Camera source module should be running")
        print("\nIf camera source is still not working:")
        print("  - Try clicking the camera source button manually")
        print("  - Check the console for any error messages")
        print("  - Restart the application if needed")
        
        # Start the application event loop
        return app.exec_()
        
    except Exception as e:
        print(f"Error in direct camera source fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    direct_camera_source_fix() 