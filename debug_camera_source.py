#!/usr/bin/env python3
"""
Debug Camera Source
Check exactly why camera source is not working
"""

import sys
import os
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_camera_source():
    """Debug the camera source issue"""
    
    print("🔍 Debugging Camera Source")
    print("=" * 50)
    
    try:
        # Import required modules
        from apps.PlayaTewsIdentityMasker.backend.CameraSource import CameraSource, BackendWeakHeap, BackendConnection, BackendDB
        from apps.PlayaTewsIdentityMasker.backend.CameraSource import _DriverType, _ResolutionType, _RotationType
        
        print("✅ Imported camera source modules")
        
        # Create backend components
        weak_heap = BackendWeakHeap(size_mb=1024)
        bc_out = BackendConnection()
        backend_db = BackendDB(Path("debug_camera_test.db"))
        
        print("✅ Created backend components")
        
        # Create camera source
        camera_source = CameraSource(weak_heap=weak_heap, bc_out=bc_out, backend_db=backend_db)
        print("✅ Created camera source")
        
        # Get control sheet and state
        cs = camera_source.get_control_sheet()
        state = camera_source.get_state()
        
        print(f"\n🔍 Initial state:")
        print(f"   - device_idx: {state.device_idx}")
        print(f"   - driver: {state.driver}")
        print(f"   - resolution: {state.resolution}")
        print(f"   - fps: {state.fps}")
        
        # Start camera source
        print("\n🚀 Starting camera source...")
        camera_source.start()
        
        # Wait a moment
        time.sleep(3)
        
        # Check if camera source is running
        if camera_source.is_started():
            print("✅ Camera source is running")
            
            # Get the worker
            worker = camera_source.get_worker()
            if worker:
                print("✅ Worker found")
                
                # Check worker state
                worker_state = worker.get_state()
                print(f"🔍 Worker state:")
                print(f"   - device_idx: {worker_state.device_idx}")
                print(f"   - driver: {worker_state.driver}")
                print(f"   - resolution: {worker_state.resolution}")
                print(f"   - fps: {worker_state.fps}")
                
                # Check if vcap exists
                if hasattr(worker, 'vcap'):
                    if worker.vcap is not None:
                        print("✅ vcap exists")
                        if worker.vcap.isOpened():
                            print("✅ vcap is opened")
                            
                            # Try to read a frame
                            ret, frame = worker.vcap.read()
                            if ret and frame is not None:
                                print(f"✅ Frame read successful: {frame.shape}")
                            else:
                                print("❌ Frame read failed")
                        else:
                            print("❌ vcap is not opened")
                    else:
                        print("❌ vcap is None")
                else:
                    print("❌ vcap attribute not found")
                
                # Check if frames are being produced
                print("\n⏳ Waiting for frames...")
                time.sleep(5)
                
                if not bc_out.is_empty():
                    bcd = bc_out.read()
                    print(f"✅ Camera frames detected: UID {bcd.uid}")
                else:
                    print("❌ No camera frames detected")
                    
                    # Check if there are any pending frames
                    if hasattr(worker, 'pending_bcd') and worker.pending_bcd is not None:
                        print("⚠️ Pending frame exists but not sent")
                    else:
                        print("❌ No pending frames")
            else:
                print("❌ No worker found")
        else:
            print("❌ Camera source failed to start")
        
        # Cleanup
        try:
            camera_source.stop()
            print("✅ Camera source stopped")
        except:
            pass
        
    except Exception as e:
        print(f"❌ Error debugging camera source: {e}")
        import traceback
        traceback.print_exc()

def test_camera_directly_with_same_settings():
    """Test camera directly with the same settings the camera source uses"""
    
    print("\n🎯 Testing camera directly with same settings...")
    
    try:
        import cv2
        
        # Use the same settings as camera source
        device_idx = 0
        cv_api = cv2.CAP_DSHOW  # DirectShow
        resolution = (640, 480)
        fps = 30
        
        print(f"🔧 Opening camera {device_idx} with DirectShow...")
        cap = cv2.VideoCapture(device_idx, cv_api)
        
        if cap.isOpened():
            print("✅ Camera opened successfully")
            
            # Set the same properties as camera source
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
            cap.set(cv2.CAP_PROP_FPS, fps)
            
            # Check what was actually set
            actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            actual_fps = cap.get(cv2.CAP_PROP_FPS)
            
            print(f"🔍 Actual camera properties:")
            print(f"   - Width: {actual_width}")
            print(f"   - Height: {actual_height}")
            print(f"   - FPS: {actual_fps}")
            
            # Try to read a frame
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Frame captured: {frame.shape}")
                print("🎬 Camera is working correctly!")
                
                # Try to display frame
                try:
                    cv2.imshow('Camera Debug Test', frame)
                    print("✅ Frame displayed (press any key to close)")
                    cv2.waitKey(2000)  # Wait 2 seconds
                    cv2.destroyAllWindows()
                except Exception as e:
                    print(f"⚠️ Could not display frame: {e}")
            else:
                print("❌ Could not capture frame")
        else:
            print("❌ Could not open camera")
            
            # Try alternative backends
            print("\n🔧 Trying alternative backends...")
            
            for backend_name, backend_api in [
                ("MSMF", cv2.CAP_MSMF),
                ("ANY", cv2.CAP_ANY),
                ("GSTREAMER", cv2.CAP_GSTREAMER)
            ]:
                print(f"   Trying {backend_name}...")
                cap = cv2.VideoCapture(device_idx, backend_api)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"   ✅ {backend_name} works: {frame.shape}")
                        cap.release()
                        break
                    else:
                        print(f"   ❌ {backend_name} opened but no frame")
                        cap.release()
                else:
                    print(f"   ❌ {backend_name} failed to open")
        
        cap.release()
        
    except Exception as e:
        print(f"❌ Error testing camera directly: {e}")

def check_camera_permissions():
    """Check camera permissions"""
    
    print("\n🔍 Checking camera permissions...")
    
    try:
        import cv2
        
        # Try to open camera with different approaches
        print("🔧 Testing camera access...")
        
        # Method 1: DirectShow
        cap1 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap1.isOpened():
            print("✅ DirectShow access granted")
            cap1.release()
        else:
            print("❌ DirectShow access denied")
        
        # Method 2: MSMF
        cap2 = cv2.VideoCapture(0, cv2.CAP_MSMF)
        if cap2.isOpened():
            print("✅ MSMF access granted")
            cap2.release()
        else:
            print("❌ MSMF access denied")
        
        # Method 3: ANY
        cap3 = cv2.VideoCapture(0, cv2.CAP_ANY)
        if cap3.isOpened():
            print("✅ ANY backend access granted")
            cap3.release()
        else:
            print("❌ ANY backend access denied")
        
        print("\n💡 If all access methods are denied:")
        print("   - Check Windows camera permissions")
        print("   - Go to Settings > Privacy & Security > Camera")
        print("   - Ensure 'Camera access' is turned On")
        print("   - Ensure 'Let apps access your camera' is turned On")
        
    except Exception as e:
        print(f"❌ Error checking camera permissions: {e}")

if __name__ == "__main__":
    print("🔍 Camera Source Debug")
    print("=" * 50)
    
    # Debug camera source
    debug_camera_source()
    
    # Test camera directly
    test_camera_directly_with_same_settings()
    
    # Check permissions
    check_camera_permissions()
    
    print("\n" + "=" * 50)
    print("🎬 Camera Source Debug Complete!")
    print("=" * 50)
    print("📋 This debug will help identify:")
    print("   - If camera source is starting properly")
    print("   - If vcap is being created")
    print("   - If frames are being captured")
    print("   - If there are permission issues")
    print("   - Which backend works best") 