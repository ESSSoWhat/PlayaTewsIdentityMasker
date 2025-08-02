#!/usr/bin/env python3
"""
Camera Preview Fix Script
Fixes the camera feed preview issues in PlayaTewsIdentityMasker
"""

import cv2
import json
import os
import sys
from pathlib import Path

def test_camera_backends():
    """Test different camera backends to find the most stable one"""
    print("🔍 Testing Camera Backends...")
    print("=" * 50)
    
    camera_index = 0
    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_ANY, "Auto-detect")
    ]
    
    working_backend = None
    working_config = None
    
    for backend, name in backends:
        print(f"\n📹 Testing {name} backend...")
        try:
            cap = cv2.VideoCapture(camera_index, backend)
            if not cap.isOpened():
                print(f"  ❌ {name}: Failed to open camera")
                continue
            
            # Set properties for better compatibility
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Test frame reading
            success_count = 0
            total_tests = 10
            
            for i in range(total_tests):
                ret, frame = cap.read()
                if ret and frame is not None:
                    success_count += 1
                    if i == 0:  # First successful frame
                        height, width = frame.shape[:2]
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        print(f"  ✅ Frame {i+1}: {width}x{height} @ {fps:.1f}fps")
                else:
                    print(f"  ❌ Frame {i+1}: Failed to read")
            
            success_rate = (success_count / total_tests) * 100
            print(f"  📊 Success Rate: {success_count}/{total_tests} ({success_rate:.1f}%)")
            
            if success_rate >= 80:  # 80% success rate threshold
                working_backend = backend
                working_config = {
                    "backend": name,
                    "backend_id": backend,
                    "success_rate": success_rate,
                    "width": width,
                    "height": height,
                    "fps": fps
                }
                print(f"  🎯 {name} selected as working backend!")
                break
            
            cap.release()
            
        except Exception as e:
            print(f"  ❌ {name}: Error - {e}")
            continue
    
    return working_backend, working_config

def update_settings_files(backend_config):
    """Update all settings files with the working camera configuration"""
    print(f"\n📝 Updating Settings Files...")
    print("=" * 50)
    
    # Settings to apply
    settings = {
        "CameraSource.device_idx": 0,
        "CameraSource.driver": backend_config["backend_id"],
        "CameraSource.resolution": 3,  # 1280x720
        "CameraSource.fps": backend_config["fps"],
        "CameraSource.rotation": 0,
        "CameraSource.flip_horizontal": False,
        "CameraSource.capture_width": backend_config["width"],
        "CameraSource.capture_height": backend_config["height"]
    }
    
    # Settings files to update
    settings_files = [
        "settings/app.dat",
        "settings/states.dat", 
        "simple_settings/app.dat",
        "simple_settings/states.dat",
        "working_settings/app.dat",
        "working_settings/states.dat"
    ]
    
    updated_files = 0
    
    for settings_file in settings_files:
        if os.path.exists(settings_file):
            print(f"📄 Updating {settings_file}...")
            try:
                # Read existing settings
                with open(settings_file, 'r') as f:
                    lines = f.readlines()
                
                # Update camera settings
                updated = False
                for i, line in enumerate(lines):
                    for key, value in settings.items():
                        if key in line and '=' in line:
                            lines[i] = f"{key} = {value}\n"
                            updated = True
                            break
                
                # Write updated settings
                with open(settings_file, 'w') as f:
                    f.writelines(lines)
                
                if updated:
                    print(f"  ✅ Updated successfully")
                    updated_files += 1
                else:
                    print(f"  ⚠️ No camera settings found")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        else:
            print(f"📄 {settings_file} not found (skipping)")
    
    return updated_files

def create_camera_config_file(backend_config):
    """Create a comprehensive camera configuration file"""
    print(f"\n📄 Creating Camera Configuration...")
    
    config = {
        "camera": {
            "backend": backend_config["backend"],
            "backend_id": backend_config["backend_id"],
            "index": 0,
            "resolution": f"{backend_config['width']}x{backend_config['height']}",
            "fps": backend_config["fps"],
            "success_rate": backend_config["success_rate"]
        },
        "face_swap": {
            "enabled": True,
            "model": "Natalie_Fatman.dfm"
        },
        "preview": {
            "enabled": True,
            "show_fps": True,
            "show_face_detection": True
        }
    }
    
    with open("camera_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created camera_config.json")

def test_preview_fix():
    """Test the camera preview with the new settings"""
    print(f"\n🎬 Testing Camera Preview...")
    print("=" * 50)
    
    try:
        # Load the camera configuration
        with open("camera_config.json", "r") as f:
            config = json.load(f)
        
        backend_id = config["camera"]["backend_id"]
        camera_index = config["camera"]["index"]
        
        print(f"📹 Opening camera with {config['camera']['backend']} backend...")
        
        cap = cv2.VideoCapture(camera_index, backend_id)
        if not cap.isOpened():
            print("❌ Failed to open camera")
            return False
        
        # Set properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        print("📸 Testing frame capture...")
        
        # Test multiple frames
        success_count = 0
        for i in range(5):
            ret, frame = cap.read()
            if ret and frame is not None:
                success_count += 1
                height, width = frame.shape[:2]
                print(f"  ✅ Frame {i+1}: {width}x{height}")
            else:
                print(f"  ❌ Frame {i+1}: Failed")
        
        cap.release()
        
        if success_count >= 3:
            print(f"✅ Preview test successful! ({success_count}/5 frames)")
            return True
        else:
            print(f"❌ Preview test failed ({success_count}/5 frames)")
            return False
            
    except Exception as e:
        print(f"❌ Preview test error: {e}")
        return False

def main():
    """Main function to fix camera preview issues"""
    print("🔧 PlayaTewsIdentityMasker - Camera Preview Fix")
    print("=" * 60)
    
    # Step 1: Test camera backends
    working_backend, backend_config = test_camera_backends()
    
    if not working_backend:
        print("\n❌ No working camera backend found!")
        print("💡 Try these solutions:")
        print("   1. Check if your camera is connected and working")
        print("   2. Try a different camera application")
        print("   3. Restart your computer")
        return
    
    # Step 2: Update settings files
    updated_files = update_settings_files(backend_config)
    
    # Step 3: Create configuration file
    create_camera_config_file(backend_config)
    
    # Step 4: Test the fix
    preview_working = test_preview_fix()
    
    # Summary
    print(f"\n📋 Fix Summary:")
    print("=" * 50)
    print(f"✅ Working Backend: {backend_config['backend']}")
    print(f"✅ Success Rate: {backend_config['success_rate']:.1f}%")
    print(f"✅ Resolution: {backend_config['width']}x{backend_config['height']}")
    print(f"✅ FPS: {backend_config['fps']:.1f}")
    print(f"✅ Settings Files Updated: {updated_files}")
    print(f"✅ Preview Test: {'PASSED' if preview_working else 'FAILED'}")
    
    if preview_working:
        print(f"\n🎉 Camera preview should now work!")
        print(f"💡 Try running your main application now.")
    else:
        print(f"\n⚠️ Preview test failed. Try these additional steps:")
        print(f"   1. Restart the application")
        print(f"   2. Check camera permissions")
        print(f"   3. Try a different camera index")

if __name__ == "__main__":
    main() 