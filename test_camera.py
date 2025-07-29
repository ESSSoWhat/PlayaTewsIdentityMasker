#!/usr/bin/env python3
"""
Simple Camera Test Script
Tests camera access and displays available devices
"""

import cv2
import platform
import time

def test_camera_devices():
    """Test all available camera devices"""
    print("🔍 Testing Camera Devices...")
    print("=" * 50)
    
    # Test different camera indices
    for i in range(5):  # Test first 5 camera indices
        print(f"\n📹 Testing Camera Index {i}:")
        
        # Try different backends
        backends = [
            (cv2.CAP_ANY, "Any"),
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_GSTREAMER, "GStreamer")
        ]
        
        for backend_id, backend_name in backends:
            try:
                cap = cv2.VideoCapture(i, backend_id)
                if cap.isOpened():
                    # Get camera info
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    
                    print(f"  ✅ {backend_name}: {width}x{height} @ {fps:.1f}fps")
                    
                    # Try to read a frame
                    ret, frame = cap.read()
                    if ret:
                        print(f"    📸 Frame read successful: {frame.shape}")
                        
                        # Display frame briefly
                        cv2.imshow(f'Camera {i} - {backend_name}', frame)
                        cv2.waitKey(1000)  # Show for 1 second
                        cv2.destroyAllWindows()
                    else:
                        print(f"    ❌ Frame read failed")
                    
                    cap.release()
                else:
                    print(f"  ❌ {backend_name}: Failed to open")
            except Exception as e:
                print(f"  ❌ {backend_name}: Error - {e}")

def list_windows_devices():
    """List Windows DirectShow devices"""
    if platform.system() == 'Windows':
        try:
            from xlib.api.win32 import ole32, dshow
            print("\n🖥️ Windows DirectShow Devices:")
            print("=" * 50)
            
            ole32.CoInitializeEx(0, 0)
            devices = dshow.get_video_input_devices_names()
            
            for idx, name in enumerate(devices):
                print(f"  {idx}: {name}")
            
            ole32.CoUninitialize()
            return devices
        except Exception as e:
            print(f"❌ Error listing DirectShow devices: {e}")
            return []
    else:
        print("🖥️ Not on Windows - skipping DirectShow device list")
        return []

def test_simple_camera():
    """Simple camera test with default settings"""
    print("\n🎥 Simple Camera Test:")
    print("=" * 50)
    
    # Try to open camera 0 with default settings
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Failed to open camera 0")
        return False
    
    print("✅ Camera 0 opened successfully")
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Read a few frames
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"  📸 Frame {i+1}: {frame.shape}")
            
            # Display frame
            cv2.imshow('Camera Test', frame)
            cv2.waitKey(500)  # Show for 0.5 seconds
        else:
            print(f"  ❌ Frame {i+1}: Failed to read")
    
    cv2.destroyAllWindows()
    cap.release()
    return True

def main():
    """Main test function"""
    print("🎬 PlayaTewsIdentityMasker - Camera Test")
    print("=" * 60)
    
    # List Windows devices
    devices = list_windows_devices()
    
    # Test simple camera
    simple_test = test_simple_camera()
    
    # Test all camera devices
    test_camera_devices()
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"  Windows Devices Found: {len(devices)}")
    print(f"  Simple Camera Test: {'✅ Passed' if simple_test else '❌ Failed'}")
    
    if not simple_test:
        print("\n🔧 Troubleshooting Tips:")
        print("  1. Check if camera is being used by another application")
        print("  2. Try closing other camera apps (Zoom, Teams, etc.)")
        print("  3. Check camera permissions in Windows Settings")
        print("  4. Try different camera drivers")
        print("  5. Restart the computer if camera is stuck")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main() 