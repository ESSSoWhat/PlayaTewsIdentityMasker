#!/usr/bin/env python3
"""
Standalone Camera Test for PlayaTewsIdentityMasker
Tests camera functionality without app interference
"""

import cv2
import time
import sys
from pathlib import Path

def test_camera_direct():
    """Test camera directly with OpenCV"""
    print("🔍 Testing Camera Directly...")
    print("=" * 50)
    
    try:
        # Test camera with DirectShow
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if cap.isOpened():
            print("✅ Camera opened successfully")
            
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            print("✅ Camera properties set")
            
            # Read a few frames
            for i in range(5):
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ Frame {i+1}: {frame.shape}")
                    if i == 0:
                        print(f"   Frame size: {frame.shape}")
                        print(f"   Frame type: {frame.dtype}")
                else:
                    print(f"❌ Frame {i+1}: Failed to read")
                time.sleep(0.1)
            
            cap.release()
            print("✅ Camera test completed successfully")
            return True
        else:
            print("❌ Failed to open camera")
            return False
            
    except Exception as e:
        print(f"❌ Camera test error: {e}")
        return False

def test_camera_with_backend():
    """Test camera with backend components"""
    print("\n🔍 Testing Camera with Backend...")
    print("=" * 50)
    
    try:
        # Import backend components
        sys.path.append('.')
        from apps.PlayaTewsIdentityMasker import backend
        
        # Create backend components
        backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)
        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        
        print("✅ Backend components created")
        
        # Create camera source
        camera_source = backend.CameraSource(
            weak_heap=backend_weak_heap, 
            bc_out=multi_sources_bc_out, 
            backend_db=None
        )
        
        print("✅ Camera source created")
        
        # Start camera source
        camera_source.start()
        print("✅ Camera source started")
        
        # Wait for initialization
        time.sleep(5)
        
        # Check for data multiple times
        for i in range(10):
            bcd_id = multi_sources_bc_out.get_write_id()
            print(f"Check {i+1}: Backend connection write ID: {bcd_id}")
            
            if bcd_id > 0:
                bcd = multi_sources_bc_out.get_by_id(bcd_id)
                if bcd is not None:
                    bcd.assign_weak_heap(backend_weak_heap)
                    frame_image_name = bcd.get_frame_image_name()
                    frame_image = bcd.get_image(frame_image_name)
                    
                    if frame_image is not None:
                        print(f"✅ Camera data flowing: {frame_image.shape}")
                        print(f"   Frame name: {frame_image_name}")
                        print(f"   Frame number: {bcd.get_frame_num()}")
                        print(f"   Timestamp: {bcd.get_frame_timestamp()}")
                        
                        # Stop camera source
                        camera_source.stop()
                        print("✅ Camera source stopped")
                        return True
                    else:
                        print(f"   ❌ No frame image in backend connection")
                else:
                    print(f"   ❌ No backend connection data")
            else:
                print(f"   ❌ No data in backend connection")
            
            time.sleep(1)
        
        # Stop camera source
        camera_source.stop()
        print("❌ No camera data received after 10 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Backend camera test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎬 PlayaTewsIdentityMasker - Standalone Camera Test")
    print("=" * 60)
    print()
    
    direct_ok = test_camera_direct()
    backend_ok = test_camera_with_backend()
    
    print("\n📊 Test Results:")
    print("=" * 40)
    
    if direct_ok and backend_ok:
        print("🎉 SUCCESS! Camera is working perfectly!")
        print("✅ Direct camera access: Working")
        print("✅ Backend camera integration: Working")
        print("\n🔧 The issue might be in the UI connection or app configuration")
    elif direct_ok and not backend_ok:
        print("⚠️ Camera hardware works but backend integration fails")
        print("✅ Direct camera access: Working")
        print("❌ Backend camera integration: Failed")
        print("\n🔧 The issue is in the backend camera source")
    elif not direct_ok:
        print("❌ Camera hardware or driver issue")
        print("❌ Direct camera access: Failed")
        print("❌ Backend camera integration: Failed")
        print("\n🔧 Check camera hardware and drivers")
    else:
        print("❌ Unknown issue")
    
    print("\n💡 Next steps:")
    if direct_ok and backend_ok:
        print("   • Check UI component connection")
        print("   • Verify app configuration")
        print("   • Look for Qt application issues")
    elif direct_ok and not backend_ok:
        print("   • Fix backend camera source")
        print("   • Check camera source initialization")
        print("   • Verify backend connection setup")

if __name__ == "__main__":
    main() 