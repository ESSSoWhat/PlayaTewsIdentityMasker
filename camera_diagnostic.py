#!/usr/bin/env python3
"""
Camera Diagnostic Script
Check camera status and fix camera source activation
"""

import cv2
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose_camera():
    """Diagnose camera issues"""
    
    print("🔍 Camera Diagnostic")
    print("=" * 50)
    
    # Test 1: Check available cameras
    print("\n📹 Test 1: Checking available cameras...")
    available_cameras = []
    
    for i in range(10):  # Check first 10 camera indices
        try:
            # Try DirectShow first
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ Camera {i}: DirectShow - Working (Frame: {frame.shape})")
                    available_cameras.append((i, "DirectShow"))
                else:
                    print(f"⚠️ Camera {i}: DirectShow - Opened but no frame")
            else:
                print(f"❌ Camera {i}: DirectShow - Failed to open")
            cap.release()
            
            # Try MSMF
            cap = cv2.VideoCapture(i, cv2.CAP_MSMF)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ Camera {i}: MSMF - Working (Frame: {frame.shape})")
                    available_cameras.append((i, "MSMF"))
                else:
                    print(f"⚠️ Camera {i}: MSMF - Opened but no frame")
            else:
                print(f"❌ Camera {i}: MSMF - Failed to open")
            cap.release()
            
        except Exception as e:
            print(f"❌ Camera {i}: Error - {e}")
    
    print(f"\n📊 Summary: Found {len(available_cameras)} working camera(s)")
    for idx, backend in available_cameras:
        print(f"   - Camera {idx} with {backend} backend")
    
    # Test 2: Check camera source settings
    print("\n🔧 Test 2: Checking camera source settings...")
    try:
        from apps.PlayaTewsIdentityMasker.backend.CameraSource import CameraSource, BackendWeakHeap, BackendConnection, BackendDB
        from apps.PlayaTewsIdentityMasker.backend import BackendConnection as BC
        
        # Create temporary backend components
        weak_heap = BackendWeakHeap(size_mb=1024)
        bc_out = BackendConnection()
        backend_db = BackendDB(Path("temp_camera_test.db"))
        
        # Create camera source
        camera_source = CameraSource(weak_heap=weak_heap, bc_out=bc_out, backend_db=backend_db)
        
        # Get control sheet
        cs = camera_source.get_control_sheet()
        
        print("✅ Camera source created successfully")
        print(f"   - Driver: {cs.driver.get_selected_choice()}")
        print(f"   - Device: {cs.device_idx.get_selected_choice()}")
        print(f"   - Resolution: {cs.resolution.get_selected_choice()}")
        print(f"   - FPS: {cs.fps.get_number()}")
        
        # Try to start camera source
        print("\n🚀 Test 3: Starting camera source...")
        camera_source.start()
        
        # Wait a moment
        import time
        time.sleep(2)
        
        # Check if camera source is running
        if camera_source.is_started():
            print("✅ Camera source is running")
            
            # Check if frames are being produced
            time.sleep(3)
            if not bc_out.is_empty():
                bcd = bc_out.read()
                print(f"✅ Camera frames detected: UID {bcd.uid}")
            else:
                print("⚠️ No camera frames detected")
        else:
            print("❌ Camera source failed to start")
        
        # Cleanup
        camera_source.stop()
        weak_heap.clear()
        
    except Exception as e:
        print(f"❌ Error testing camera source: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Check if camera is being used by another process
    print("\n🔍 Test 4: Checking for camera conflicts...")
    try:
        import psutil
        camera_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'camera' in cmdline.lower() or 'opencv' in cmdline.lower():
                        camera_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if camera_processes:
            print(f"⚠️ Found {len(camera_processes)} potential camera processes:")
            for proc in camera_processes:
                print(f"   - PID {proc['pid']}: {proc['name']} - {proc['cmdline']}")
        else:
            print("✅ No conflicting camera processes found")
            
    except Exception as e:
        print(f"⚠️ Could not check for camera conflicts: {e}")
    
    # Test 5: Try to open camera directly
    print("\n🎯 Test 5: Direct camera test...")
    if available_cameras:
        best_camera = available_cameras[0]  # Use first available camera
        device_idx, backend = best_camera
        
        if backend == "DirectShow":
            cv_api = cv2.CAP_DSHOW
        elif backend == "MSMF":
            cv_api = cv2.CAP_MSMF
        else:
            cv_api = cv2.CAP_ANY
        
        print(f"🎬 Testing camera {device_idx} with {backend} backend...")
        
        cap = cv2.VideoCapture(device_idx, cv_api)
        if cap.isOpened():
            print("✅ Camera opened successfully")
            
            # Try to read a frame
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Frame captured: {frame.shape}")
                
                # Try to display frame (optional)
                try:
                    cv2.imshow('Camera Test', frame)
                    print("✅ Frame displayed (press any key to close)")
                    cv2.waitKey(3000)  # Wait 3 seconds
                    cv2.destroyAllWindows()
                except Exception as e:
                    print(f"⚠️ Could not display frame: {e}")
            else:
                print("❌ Could not capture frame")
        else:
            print("❌ Could not open camera")
        
        cap.release()
    else:
        print("❌ No working cameras found for direct test")
    
    print("\n" + "=" * 50)
    print("🎬 Camera Diagnostic Complete!")
    print("=" * 50)
    
    if available_cameras:
        print("✅ Working cameras found - camera source should work")
        print("🔧 If camera source button still doesn't activate:")
        print("   1. Check that the correct camera is selected in the UI")
        print("   2. Try restarting the application")
        print("   3. Check camera permissions in Windows")
    else:
        print("❌ No working cameras found")
        print("🔧 Troubleshooting steps:")
        print("   1. Check camera hardware connections")
        print("   2. Update camera drivers")
        print("   3. Check Windows camera permissions")
        print("   4. Try a different camera or USB port")

if __name__ == "__main__":
    diagnose_camera() 