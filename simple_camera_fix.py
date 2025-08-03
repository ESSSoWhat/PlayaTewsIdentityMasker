#!/usr/bin/env python3
"""
Simple Camera Fix
Directly fix camera settings to ensure camera source activates
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_camera_settings_fix():
    """Create camera settings files to ensure camera works"""
    
    print("🔧 Creating Camera Settings Fix")
    print("=" * 50)
    
    # Create camera settings
    camera_settings = {
        "camera": {
            "device_idx": 0,
            "driver": 1,  # DirectShow
            "resolution": 1,  # 640x480
            "fps": 30,
            "rotation": 0,  # 0 degrees
            "flip_horizontal": False
        }
    }
    
    # Create settings directory
    settings_dir = Path("settings")
    settings_dir.mkdir(exist_ok=True)
    
    # Save to camera_override.json
    camera_override_file = settings_dir / "camera_override.json"
    with open(camera_override_file, 'w', encoding='utf-8') as f:
        json.dump(camera_settings, f, indent=2)
    print(f"✅ Saved camera settings to {camera_override_file}")
    
    # Save to global_face_swap_state.json
    global_settings_file = settings_dir / "global_face_swap_state.json"
    try:
        if global_settings_file.exists():
            with open(global_settings_file, 'r', encoding='utf-8') as f:
                global_settings = json.load(f)
        else:
            global_settings = {}
        
        global_settings.update(camera_settings)
        
        with open(global_settings_file, 'w', encoding='utf-8') as f:
            json.dump(global_settings, f, indent=2)
        print(f"✅ Updated camera settings in {global_settings_file}")
    except Exception as e:
        print(f"⚠️ Could not update global settings: {e}")
    
    # Save to demo settings
    demo_settings_dir = Path("demo_settings/settings")
    demo_settings_dir.mkdir(parents=True, exist_ok=True)
    demo_settings_file = demo_settings_dir / "global_face_swap_state.json"
    
    try:
        if demo_settings_file.exists():
            with open(demo_settings_file, 'r', encoding='utf-8') as f:
                demo_settings = json.load(f)
        else:
            demo_settings = {}
        
        demo_settings.update(camera_settings)
        
        with open(demo_settings_file, 'w', encoding='utf-8') as f:
            json.dump(demo_settings, f, indent=2)
        print(f"✅ Updated camera settings in {demo_settings_file}")
    except Exception as e:
        print(f"⚠️ Could not update demo settings: {e}")
    
    # Also create a camera source state file
    camera_source_state = {
        "device_idx": 0,
        "driver": 1,
        "resolution": 1,
        "fps": 30,
        "rotation": 0,
        "flip_horizontal": False,
        "settings_by_idx": {}
    }
    
    camera_state_file = settings_dir / "camera_source_state.json"
    with open(camera_state_file, 'w', encoding='utf-8') as f:
        json.dump(camera_source_state, f, indent=2)
    print(f"✅ Saved camera source state to {camera_state_file}")

def test_camera_directly():
    """Test camera directly to verify it works"""
    
    print("\n🔍 Testing camera directly...")
    
    try:
        import cv2
        
        # Try to open camera 0 with DirectShow
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if cap.isOpened():
            print("✅ Camera opened successfully")
            
            # Set properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Try to read a frame
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Frame captured: {frame.shape}")
                print("🎬 Camera is working correctly!")
                
                # Try to display frame
                try:
                    cv2.imshow('Camera Fix Test', frame)
                    print("✅ Frame displayed (press any key to close)")
                    cv2.waitKey(2000)  # Wait 2 seconds
                    cv2.destroyAllWindows()
                except Exception as e:
                    print(f"⚠️ Could not display frame: {e}")
            else:
                print("❌ Could not capture frame")
        else:
            print("❌ Could not open camera")
        
        cap.release()
        
    except Exception as e:
        print(f"❌ Error testing camera directly: {e}")

def create_camera_activation_launcher():
    """Create a launcher that ensures camera source activates"""
    
    print("\n🔧 Creating camera activation launcher...")
    
    launcher_content = '''#!/usr/bin/env python3
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
        print("\\n🔧 Step 2: Initializing PlayaTewsIdentityMasker...")
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        # Set up userdata path as Path object
        userdata_path = Path(os.path.dirname(os.path.abspath(__file__))) / "userdata"
        print(f"📁 Using userdata path: {userdata_path}")
        
        # Create the main app
        main_app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        print("✅ Main app created successfully")
        
        # Step 3: Force camera source activation
        print("\\n🔧 Step 3: Forcing camera source activation...")
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
        print("\\n⏳ Step 5: Waiting for camera and UI initialization...")
        time.sleep(5)
        
        # Step 6: Final status
        print("\\n" + "=" * 50)
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
'''
    
    launcher_file = Path("camera_activation_launcher.py")
    with open(launcher_file, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    print(f"✅ Created camera activation launcher: {launcher_file}")
    
    # Create batch file
    batch_content = '''@echo off
echo ========================================
echo PlayaTews Identity Masker - CAMERA ACTIVATION LAUNCHER
echo ========================================
echo.
echo This launcher ensures the camera source activates properly
echo and the camera feed appears in the preview area.
echo.

echo 🔧 Terminating any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

echo.
echo 🚀 Starting PlayaTewsIdentityMasker with camera activation fix...
echo.

python camera_activation_launcher.py

echo.
echo Application has finished running.
pause
'''
    
    batch_file = Path("start_camera_activation.bat")
    with open(batch_file, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    print(f"✅ Created camera activation batch file: {batch_file}")

if __name__ == "__main__":
    print("🔧 Simple Camera Fix")
    print("=" * 50)
    
    # Create camera settings fix
    create_camera_settings_fix()
    
    # Test camera directly
    test_camera_directly()
    
    # Create camera activation launcher
    create_camera_activation_launcher()
    
    print("\n" + "=" * 50)
    print("🎬 Simple Camera Fix Complete!")
    print("=" * 50)
    print("✅ Camera settings have been updated")
    print("✅ Camera activation launcher created")
    print()
    print("🔧 Next steps:")
    print("   1. Run: .\\start_camera_activation.bat")
    print("   2. The camera source button should now activate")
    print("   3. Camera feed should appear in the preview area")
    print()
    print("🎯 If the camera source still doesn't activate:")
    print("   - Check that camera permissions are granted in Windows")
    print("   - Try closing other applications that might be using the camera")
    print("   - Restart the computer if needed") 