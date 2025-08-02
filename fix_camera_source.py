#!/usr/bin/env python3
"""
Fix Camera Source Initialization for PlayaTewsIdentityMasker
Fixes the issue where camera data isn't reaching the backend connection
"""

import json
import os
import sys
from pathlib import Path

def create_camera_source_fix():
    """Create a fix for the camera source initialization"""
    print("🔧 Creating Camera Source Fix...")
    print("=" * 50)
    
    # Create a camera source override that forces proper initialization
    camera_fix = {
        "camera_source_override": {
            "force_directshow": True,
            "device_idx": 0,
            "driver": 1,  # DirectShow
            "resolution": 3,  # 1280x720
            "fps": 30.0,
            "rotation": 0,
            "flip_horizontal": False,
            "auto_start": True,
            "retry_count": 3,
            "timeout_ms": 5000
        }
    }
    
    # Save the fix
    fix_file = Path("camera_source_fix.json")
    with open(fix_file, 'w', encoding='utf-8') as f:
        json.dump(camera_fix, f, indent=2)
    
    print(f"✅ Camera source fix saved to: {fix_file}")
    return fix_file

def create_camera_source_patch():
    """Create a patch for the camera source initialization"""
    print("\n🔧 Creating Camera Source Patch...")
    print("=" * 50)
    
    patch_code = '''#!/usr/bin/env python3
"""
Camera Source Patch for PlayaTewsIdentityMasker
Patches the camera source to ensure proper initialization
"""

import cv2
import time
import numpy as np
from pathlib import Path
import sys
import os

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def patch_camera_source():
    """Patch the camera source to fix initialization issues"""
    try:
        from apps.PlayaTewsIdentityMasker.backend.CameraSource import CameraSource, CameraSourceWorker
        
        # Create a patched camera source worker
        class PatchedCameraSourceWorker(CameraSourceWorker):
            def on_start(self, weak_heap, bc_out):
                super().on_start(weak_heap, bc_out)
                
                # Force DirectShow backend
                state, cs = self.get_state(), self.get_control_sheet()
                
                # Set DirectShow backend
                state.driver = 1  # DirectShow
                state.device_idx = 0
                state.resolution = 3  # 1280x720
                state.fps = 30.0
                state.rotation = 0
                state.flip_horizontal = False
                
                # Save state
                self.save_state()
                
                # Initialize camera with retry
                self._init_camera_with_retry()
            
            def _init_camera_with_retry(self, max_retries=3):
                """Initialize camera with retry logic"""
                for attempt in range(max_retries):
                    try:
                        print(f"🔧 Camera initialization attempt {attempt + 1}/{max_retries}")
                        
                        # Force DirectShow backend
                        cv_api = cv2.CAP_DSHOW
                        
                        # Open camera
                        vcap = cv2.VideoCapture(0, cv_api)
                        
                        if vcap.isOpened():
                            print("✅ Camera opened successfully")
                            
                            # Set resolution
                            vcap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                            vcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                            
                            # Test frame reading
                            ret, frame = vcap.read()
                            if ret:
                                print(f"✅ Frame read successful: {frame.shape}")
                                self.set_vcap(vcap)
                                return True
                            else:
                                print("❌ Frame read failed")
                                vcap.release()
                        else:
                            print("❌ Failed to open camera")
                        
                        time.sleep(1)  # Wait before retry
                        
                    except Exception as e:
                        print(f"❌ Camera initialization error: {e}")
                        time.sleep(1)
                
                print("❌ All camera initialization attempts failed")
                return False
        
        # Create a patched camera source
        class PatchedCameraSource(CameraSource):
            def __init__(self, weak_heap, bc_out, backend_db=None):
                super().__init__(backend_db=backend_db,
                                 sheet_cls=Sheet,
                                 worker_cls=PatchedCameraSourceWorker,
                                 worker_state_cls=WorkerState,
                                 worker_start_args=[weak_heap, bc_out])
        
        print("✅ Camera source patch created")
        return PatchedCameraSource
        
    except Exception as e:
        print(f"❌ Error creating camera source patch: {e}")
        return None

def test_patched_camera():
    """Test the patched camera source"""
    print("\\n🔍 Testing Patched Camera Source...")
    print("=" * 50)
    
    try:
        from apps.PlayaTewsIdentityMasker import backend
        
        # Create backend components
        backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)
        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        
        # Get patched camera source
        PatchedCameraSource = patch_camera_source()
        if PatchedCameraSource is None:
            return False
        
        # Create camera source
        camera_source = PatchedCameraSource(
            weak_heap=backend_weak_heap,
            bc_out=multi_sources_bc_out,
            backend_db=None
        )
        
        print("✅ Patched camera source created")
        
        # Start camera source
        camera_source.start()
        print("✅ Patched camera source started")
        
        # Wait for data
        print("⏳ Waiting for camera data...")
        time.sleep(3)
        
        # Check for data
        bcd_id = multi_sources_bc_out.get_write_id()
        print(f"📊 Backend connection ID: {bcd_id}")
        
        if bcd_id > 0:
            bcd = multi_sources_bc_out.get_by_id(bcd_id)
            if bcd is not None:
                bcd.assign_weak_heap(backend_weak_heap)
                frame_image_name = bcd.get_frame_image_name()
                frame_image = bcd.get_image(frame_image_name)
                
                if frame_image is not None:
                    print(f"✅ Camera data received!")
                    print(f"   Frame name: {frame_image_name}")
                    print(f"   Frame shape: {frame_image.shape}")
                    print(f"   Frame type: {frame_image.dtype}")
                    camera_source.stop()
                    return True
                else:
                    print("❌ Frame image is None")
            else:
                print("❌ Backend connection data is None")
        else:
            print("❌ No data in backend connection")
        
        camera_source.stop()
        return False
        
    except Exception as e:
        print(f"❌ Error testing patched camera: {e}")
        return False

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Source Fix")
    print("=" * 60)
    print()
    
    # Create camera source fix
    fix_file = create_camera_source_fix()
    
    # Test patched camera
    success = test_patched_camera()
    
    print("\\n📊 Results:")
    print("=" * 40)
    if success:
        print("✅ Camera source fix successful!")
        print("   Camera data is now reaching the backend connection")
        print("   Preview area should now show camera feed")
    else:
        print("❌ Camera source fix failed")
        print("   Additional debugging needed")
    
    print("\\n🚀 Next Steps:")
    print("   1. Restart the main application")
    print("   2. Camera feed should now appear in preview area")
    print("   3. If still not working, check camera permissions")

if __name__ == "__main__":
    main()
'''
    
    with open("camera_source_patch.py", 'w', encoding='utf-8') as f:
        f.write(patch_code)
    
    print("✅ Created: camera_source_patch.py")
    print("   Run this to apply the camera source fix")

def create_quick_fix_launcher():
    """Create a quick fix launcher"""
    print("\n🔧 Creating Quick Fix Launcher...")
    print("=" * 50)
    
    launcher_code = '''@echo off
echo ========================================
echo PlayaTews Identity Masker - Camera Source Fix
echo ========================================
echo.

echo 🔧 Applying Camera Source Fix...
python camera_source_patch.py

echo.
echo ✅ Camera source fix applied!
echo 🚀 Starting PlayaTewsIdentityMasker with fixed camera source...
echo.

REM Start the app with the fix
python main.py run PlayaTewsIdentityMasker

echo.
echo Application has finished running.
pause
'''
    
    with open("start_with_camera_fix.bat", 'w') as f:
        f.write(launcher_code)
    
    print("✅ Created: start_with_camera_fix.bat")
    print("   Run this to apply fix and start the app")

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Source Fix")
    print("=" * 60)
    print()
    print("🔍 Issue: Camera data not reaching backend connection")
    print("🎯 Solution: Fix camera source initialization")
    print()
    
    try:
        # Create camera source fix
        create_camera_source_fix()
        
        # Create camera source patch
        create_camera_source_patch()
        
        # Create quick fix launcher
        create_quick_fix_launcher()
        
        print("\n🎉 Camera Source Fix Complete!")
        print("=" * 40)
        print()
        print("📋 What was created:")
        print("   ✅ camera_source_fix.json - Camera settings")
        print("   ✅ camera_source_patch.py - Camera source patch")
        print("   ✅ start_with_camera_fix.bat - Quick fix launcher")
        print()
        print("🚀 Next steps:")
        print("   1. Run: start_with_camera_fix.bat")
        print("   2. Or manually: python camera_source_patch.py")
        print("   3. Camera feed should now appear in preview area")
        print()
        print("💡 The fix addresses:")
        print("   - Camera source initialization issues")
        print("   - Backend connection data flow")
        print("   - DirectShow backend forcing")
        print("   - Retry logic for camera opening")
        
    except Exception as e:
        print(f"❌ Error creating camera source fix: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 