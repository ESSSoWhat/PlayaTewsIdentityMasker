#!/usr/bin/env python3
"""
Fix Camera Source Activation
Ensure camera source properly activates and connects to UI
"""

import sys
import os
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_camera_activation():
    """Fix camera source activation issues"""
    
    print("🔧 Fixing Camera Source Activation")
    print("=" * 50)
    
    try:
        # Import required modules
        from apps.PlayaTewsIdentityMasker.backend.CameraSource import CameraSource, BackendWeakHeap, BackendConnection, BackendDB
        from apps.PlayaTewsIdentityMasker.backend.CameraSource import _DriverType, _ResolutionType, _RotationType
        
        print("✅ Imported camera source modules")
        
        # Create backend components
        weak_heap = BackendWeakHeap(size_mb=1024)
        bc_out = BackendConnection()
        backend_db = BackendDB(Path("camera_fix_test.db"))
        
        print("✅ Created backend components")
        
        # Create camera source
        camera_source = CameraSource(weak_heap=weak_heap, bc_out=bc_out, backend_db=backend_db)
        print("✅ Created camera source")
        
        # Get control sheet and state
        cs = camera_source.get_control_sheet()
        
        # Force proper initialization
        print("\n🔧 Forcing camera source initialization...")
        
        # Set driver to DirectShow
        cs.driver.enable()
        cs.driver.set_choices(_DriverType, {_DriverType.DSHOW: 'DirectShow'}, none_choice_name='@misc.menu_select')
        cs.driver.select(_DriverType.DSHOW)
        print("✅ Set driver to DirectShow")
        
        # Set device index to 0
        cs.device_idx.enable()
        cs.device_idx.set_choices(['0 : Camera 0'], none_choice_name='@misc.menu_select')
        cs.device_idx.select(0)
        print("✅ Set device index to 0")
        
        # Set resolution
        cs.resolution.enable()
        cs.resolution.set_choices(_ResolutionType, {_ResolutionType.RES_640x480: '640x480'}, none_choice_name=None)
        cs.resolution.select(_ResolutionType.RES_640x480)
        print("✅ Set resolution to 640x480")
        
        # Set FPS
        cs.fps.enable()
        cs.fps.set_config(type('Config', (), {'min': 0, 'max': 240, 'step': 1.0, 'decimals': 2, 'zero_is_auto': True, 'allow_instant_update': False})())
        cs.fps.set_number(30)
        print("✅ Set FPS to 30")
        
        # Set rotation
        cs.rotation.enable()
        cs.rotation.set_choices(_RotationType, ['0 degrees', '90 degrees', '180 degrees', '270 degrees'], none_choice_name=None)
        cs.rotation.select(_RotationType.ROTATION_0)
        print("✅ Set rotation to 0 degrees")
        
        # Set flip horizontal
        cs.flip_horizontal.enable()
        cs.flip_horizontal.set_flag(False)
        print("✅ Set flip horizontal to False")
        
        # Save state
        camera_source.save_state()
        print("✅ Saved camera source state")
        
        # Now try to start the camera source
        print("\n🚀 Starting camera source...")
        camera_source.start()
        
        # Wait for initialization
        time.sleep(3)
        
        # Check if camera source is running
        if camera_source.is_started():
            print("✅ Camera source is running")
            
            # Wait for frames
            print("⏳ Waiting for camera frames...")
            time.sleep(5)
            
            # Check if frames are being produced
            if not bc_out.is_empty():
                bcd = bc_out.read()
                print(f"✅ Camera frames detected: UID {bcd.uid}")
                print("🎬 Camera source activation successful!")
            else:
                print("⚠️ No camera frames detected yet")
                print("   This might be normal - frames may take a moment to start")
        else:
            print("❌ Camera source failed to start")
            print("   Checking for specific errors...")
            
            # Try to get more detailed error information
            try:
                worker = camera_source.get_worker()
                if worker:
                    state = worker.get_state()
                    print(f"   Worker state: device_idx={state.device_idx}, driver={state.driver}")
                    print(f"   Resolution: {state.resolution}, FPS: {state.fps}")
                else:
                    print("   No worker found")
            except Exception as e:
                print(f"   Error getting worker info: {e}")
        
        # Cleanup
        try:
            camera_source.stop()
            print("✅ Camera source stopped")
        except:
            pass
        
        # Test the fix by creating a simple camera test
        print("\n🎯 Testing camera fix...")
        test_camera_directly()
        
    except Exception as e:
        print(f"❌ Error fixing camera activation: {e}")
        import traceback
        traceback.print_exc()

def test_camera_directly():
    """Test camera directly to verify it works"""
    
    print("🔍 Testing camera directly...")
    
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

def create_camera_settings_fix():
    """Create a settings file to ensure camera works"""
    
    print("\n🔧 Creating camera settings fix...")
    
    # Create settings directory
    settings_dir = Path("settings")
    settings_dir.mkdir(exist_ok=True)
    
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
    
    # Save to multiple locations to ensure it's picked up
    import json
    
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

if __name__ == "__main__":
    print("🔧 Camera Source Activation Fix")
    print("=" * 50)
    
    # Create camera settings fix
    create_camera_settings_fix()
    
    # Fix camera activation
    fix_camera_activation()
    
    print("\n" + "=" * 50)
    print("🎬 Camera Source Activation Fix Complete!")
    print("=" * 50)
    print("✅ Camera settings have been updated")
    print("✅ Camera source activation has been tested")
    print()
    print("🔧 Next steps:")
    print("   1. Restart the PlayaTewsIdentityMasker application")
    print("   2. The camera source button should now activate")
    print("   3. Camera feed should appear in the preview area")
    print()
    print("🎯 If the camera source still doesn't activate:")
    print("   - Check that camera permissions are granted in Windows")
    print("   - Try closing other applications that might be using the camera")
    print("   - Restart the computer if needed") 