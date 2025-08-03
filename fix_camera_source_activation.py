#!/usr/bin/env python3
"""
Fix Camera Source Activation
This script directly fixes the camera source activation issue
"""

import sys
import os
import json
from pathlib import Path

def create_camera_source_fix():
    """Create a comprehensive fix for camera source activation"""
    
    print("🔧 Creating Camera Source Activation Fix...")
    
    # 1. Create enhanced camera launcher
    enhanced_launcher_content = '''#!/usr/bin/env python3
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
    
    print("🚀 Enhanced Camera Source Launcher")
    print("=" * 50)
    
    # Step 1: Create QApplication
    print("🔧 Creating QApplication instance...")
    app = QApplication(sys.argv)
    print("✅ QApplication instance created")
    
    # Step 2: Test camera directly
    print("🔍 Testing camera directly...")
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Camera test successful: {frame.shape}")
                cap.release()
            else:
                print("❌ Camera test failed: No frame received")
                return False
        else:
            print("❌ Camera test failed: Could not open camera")
            return False
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False
    
    # Step 3: Import and initialize main app
    print("🔧 Initializing PlayaTewsIdentityMasker...")
    try:
        sys.path.insert(0, str(Path.cwd()))
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        userdata_path = Path.cwd() / "userdata"
        print(f"📁 Using userdata path: {userdata_path}")
        
        # Create main app
        main_app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        print("✅ Main app created successfully")
        
        # Step 4: Force camera source activation
        print("🔧 Forcing camera source activation...")
        
        # Get the camera source from the main app
        if hasattr(main_app, 'q_live_swap') and hasattr(main_app.q_live_swap, 'camera_source'):
            camera_source = main_app.q_live_swap.camera_source
            
            # Force start the camera source
            if hasattr(camera_source, 'start'):
                camera_source.start()
                print("✅ Camera source started")
            
            # Force enable the camera source
            if hasattr(camera_source, 'enable'):
                camera_source.enable()
                print("✅ Camera source enabled")
            
            # Check if there's a worker and force vcap creation
            if hasattr(camera_source, 'worker') and camera_source.worker:
                worker = camera_source.worker
                
                # Force create vcap if it doesn't exist
                if not hasattr(worker, 'vcap') or worker.vcap is None:
                    print("🔧 Creating vcap directly...")
                    worker.vcap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                    if worker.vcap.isOpened():
                        print("✅ vcap created and opened successfully")
                    else:
                        print("❌ Failed to create vcap")
                
                # Force start the worker
                if hasattr(worker, 'start'):
                    worker.start()
                    print("✅ Camera source worker started")
        
        # Step 5: Display main window
        print("🔧 Displaying main window...")
        if hasattr(main_app, 'main_window'):
            main_app.main_window.show()
            print("✅ Main window displayed")
        
        # Step 6: Wait for initialization
        print("⏳ Waiting for camera and UI initialization...")
        time.sleep(3)
        
        print("\\n" + "=" * 50)
        print("🎬 ENHANCED CAMERA LAUNCH COMPLETE!")
        print("=" * 50)
        print("📺 The PlayaTewsIdentityMasker app should now be visible.")
        print("🎬 Camera source should be activated and working.")
        print("\\n🔍 To see the camera feed:")
        print("   1. Look for the PlayaTewsIdentityMasker window")
        print("   2. Click on the 'Viewers' tab")
        print("   3. Check the 'Camera Feed' viewer on the left side")
        print("   4. The camera feed should now be visible!")
        print("\\n🎯 If camera feed is still not visible:")
        print("   - Try clicking on different tabs and back to 'Viewers'")
        print("   - Check camera permissions in Windows")
        print("   - Restart the application if needed")
        
        # Start the application event loop
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    force_camera_source_activation()
'''
    
    with open("enhanced_camera_launcher.py", "w") as f:
        f.write(enhanced_launcher_content)
    
    # 2. Create batch file
    batch_content = '''@echo off
echo ========================================
echo PlayaTews Identity Masker - ENHANCED CAMERA LAUNCHER
echo ========================================
echo.
echo This launcher forces camera source activation
echo and bypasses all API issues for immediate results.
echo.
echo ≡ Terminating any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
echo.
echo ≡ Starting PlayaTewsIdentityMasker with enhanced camera fix...
python enhanced_camera_launcher.py
echo.
echo Application has finished running.
pause
'''
    
    with open("start_enhanced_camera.bat", "w") as f:
        f.write(batch_content)
    
    # 3. Create camera source state file
    camera_state = {
        "device_idx": 0,
        "driver": 1,  # DirectShow
        "resolution": [640, 480],
        "fps": 30,
        "enabled": True,
        "auto_start": True
    }
    
    settings_dir = Path("settings")
    settings_dir.mkdir(exist_ok=True)
    
    with open(settings_dir / "camera_source_state.json", "w") as f:
        json.dump(camera_state, f, indent=2)
    
    # 4. Create global face swap state
    global_state = {
        "camera_source": {
            "enabled": True,
            "device_idx": 0,
            "driver": 1,
            "auto_start": True
        },
        "face_swap": {
            "enabled": True,
            "auto_start": True
        }
    }
    
    with open(settings_dir / "global_face_swap_state.json", "w") as f:
        json.dump(global_state, f, indent=2)
    
    # 5. Create demo settings
    demo_settings_dir = Path("demo_settings") / "settings"
    demo_settings_dir.mkdir(parents=True, exist_ok=True)
    
    with open(demo_settings_dir / "global_face_swap_state.json", "w") as f:
        json.dump(global_state, f, indent=2)
    
    print("✅ Enhanced camera launcher created: enhanced_camera_launcher.py")
    print("✅ Batch file created: start_enhanced_camera.bat")
    print("✅ Camera source state files created")
    print("✅ Global face swap state files created")
    print("✅ Demo settings files created")
    
    print("\\n🚀 To launch with enhanced camera fix:")
    print("   Run: .\\start_enhanced_camera.bat")
    
    return True

if __name__ == "__main__":
    create_camera_source_fix() 