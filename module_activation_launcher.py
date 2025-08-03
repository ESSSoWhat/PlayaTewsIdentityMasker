#!/usr/bin/env python3
"""
Enhanced Module Activation Launcher
Ensures all modules activate properly and start working
"""

import sys
import os
import time
import cv2
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def force_module_activation():
    """Force all modules to activate properly"""
    
    print("Enhanced Module Activation Launcher")
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
        
        # Step 4: Force activate all modules
        print("Forcing module activation...")
        
        # Get the live swap instance
        if hasattr(main_app, 'q_live_swap'):
            live_swap = main_app.q_live_swap
            
            # Force activate camera source
            if hasattr(live_swap, 'camera_source') and live_swap.camera_source:
                print("Activating camera source...")
                camera_source = live_swap.camera_source
                
                # Force start camera source
                if hasattr(camera_source, 'start'):
                    camera_source.start()
                    print("Camera source started")
                
                # Force enable camera source
                if hasattr(camera_source, 'enable'):
                    camera_source.enable()
                    print("Camera source enabled")
                
                # Force worker activation
                if hasattr(camera_source, 'worker') and camera_source.worker:
                    worker = camera_source.worker
                    
                    # Create vcap if needed
                    if not hasattr(worker, 'vcap') or worker.vcap is None:
                        print("Creating camera vcap...")
                        worker.vcap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                        if worker.vcap.isOpened():
                            print("Camera vcap created successfully")
                    
                    # Start worker
                    if hasattr(worker, 'start'):
                        worker.start()
                        print("Camera source worker started")
            
            # Force activate face detector
            if hasattr(live_swap, 'face_detector') and live_swap.face_detector:
                print("Activating face detector...")
                face_detector = live_swap.face_detector
                
                if hasattr(face_detector, 'start'):
                    face_detector.start()
                    print("Face detector started")
                
                if hasattr(face_detector, 'enable'):
                    face_detector.enable()
                    print("Face detector enabled")
            
            # Force activate face marker
            if hasattr(live_swap, 'face_marker') and live_swap.face_marker:
                print("Activating face marker...")
                face_marker = live_swap.face_marker
                
                if hasattr(face_marker, 'start'):
                    face_marker.start()
                    print("Face marker started")
                
                if hasattr(face_marker, 'enable'):
                    face_marker.enable()
                    print("Face marker enabled")
            
            # Force activate face aligner
            if hasattr(live_swap, 'face_aligner') and live_swap.face_aligner:
                print("Activating face aligner...")
                face_aligner = live_swap.face_aligner
                
                if hasattr(face_aligner, 'start'):
                    face_aligner.start()
                    print("Face aligner started")
                
                if hasattr(face_aligner, 'enable'):
                    face_aligner.enable()
                    print("Face aligner enabled")
            
            # Force activate face animator
            if hasattr(live_swap, 'face_animator') and live_swap.face_animator:
                print("Activating face animator...")
                face_animator = live_swap.face_animator
                
                if hasattr(face_animator, 'start'):
                    face_animator.start()
                    print("Face animator started")
                
                if hasattr(face_animator, 'enable'):
                    face_animator.enable()
                    print("Face animator enabled")
            
            # Force activate face swap insight
            if hasattr(live_swap, 'face_swap_insight') and live_swap.face_swap_insight:
                print("Activating face swap insight...")
                face_swap_insight = live_swap.face_swap_insight
                
                if hasattr(face_swap_insight, 'start'):
                    face_swap_insight.start()
                    print("Face swap insight started")
                
                if hasattr(face_swap_insight, 'enable'):
                    face_swap_insight.enable()
                    print("Face swap insight enabled")
            
            # Force activate face swap DFM
            if hasattr(live_swap, 'face_swap_dfm') and live_swap.face_swap_dfm:
                print("Activating face swap DFM...")
                face_swap_dfm = live_swap.face_swap_dfm
                
                if hasattr(face_swap_dfm, 'start'):
                    face_swap_dfm.start()
                    print("Face swap DFM started")
                
                if hasattr(face_swap_dfm, 'enable'):
                    face_swap_dfm.enable()
                    print("Face swap DFM enabled")
            
            # Force activate frame adjuster
            if hasattr(live_swap, 'frame_adjuster') and live_swap.frame_adjuster:
                print("Activating frame adjuster...")
                frame_adjuster = live_swap.frame_adjuster
                
                if hasattr(frame_adjuster, 'start'):
                    frame_adjuster.start()
                    print("Frame adjuster started")
                
                if hasattr(frame_adjuster, 'enable'):
                    frame_adjuster.enable()
                    print("Frame adjuster enabled")
            
            # Force activate face merger
            if hasattr(live_swap, 'face_merger') and live_swap.face_merger:
                print("Activating face merger...")
                face_merger = live_swap.face_merger
                
                if hasattr(face_merger, 'start'):
                    face_merger.start()
                    print("Face merger started")
                
                if hasattr(face_merger, 'enable'):
                    face_merger.enable()
                    print("Face merger enabled")
            
            # Force activate stream output
            if hasattr(live_swap, 'stream_output') and live_swap.stream_output:
                print("Activating stream output...")
                stream_output = live_swap.stream_output
                
                if hasattr(stream_output, 'start'):
                    stream_output.start()
                    print("Stream output started")
                
                if hasattr(stream_output, 'enable'):
                    stream_output.enable()
                    print("Stream output enabled")
        
        # Step 5: Display main window
        print("Displaying main window...")
        if hasattr(main_app, 'main_window'):
            main_app.main_window.show()
            print("Main window displayed")
        
        # Step 6: Wait for initialization
        print("Waiting for module initialization...")
        time.sleep(5)
        
        print("\n" + "=" * 50)
        print("MODULE ACTIVATION COMPLETE!")
        print("=" * 50)
        print("All modules should now be activated and working.")
        print("\nTo verify module activation:")
        print("  1. Look for the PlayaTewsIdentityMasker window")
        print("  2. Check that all module buttons are active/enabled")
        print("  3. Navigate to the 'Viewers' tab")
        print("  4. The camera feed should be visible")
        print("  5. Face detection and processing should be working")
        print("\nIf modules are still not activating:")
        print("  - Try clicking the module buttons manually")
        print("  - Check the console for any error messages")
        print("  - Restart the application if needed")
        
        # Start the application event loop
        return app.exec_()
        
    except Exception as e:
        print(f"Error launching app: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    force_module_activation()
