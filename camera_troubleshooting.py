#!/usr/bin/env python3
"""
Camera Troubleshooting for PlayaTewsIdentityMasker
Helps diagnose and fix camera feed issues
"""

import cv2
import os
import sys
import time

def test_camera_backends():
    """Test different camera backends"""
    print("🔍 Testing Camera Backends...")
    print("=" * 50)
    
    backends = [
        (cv2.CAP_ANY, "Any"),
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_GSTREAMER, "GStreamer")
    ]
    
    for backend, name in backends:
        print(f"\n📹 Testing {name} backend:")
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            print(f"  ✅ {name}: Camera opened successfully")
            ret, frame = cap.read()
            if ret:
                print(f"  ✅ {name}: Frame read successfully - {frame.shape}")
            else:
                print(f"  ❌ {name}: Frame read failed")
            cap.release()
        else:
            print(f"  ❌ {name}: Failed to open camera")

def test_camera_indexes():
    """Test different camera indexes"""
    print("\n🔍 Testing Camera Indexes...")
    print("=" * 50)
    
    for i in range(5):
        print(f"\n📹 Testing Camera Index {i}:")
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            print(f"  ✅ Index {i}: Camera opened successfully")
            ret, frame = cap.read()
            if ret:
                print(f"  ✅ Index {i}: Frame read successfully - {frame.shape}")
                # Try to get camera properties
                width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                fps = cap.get(cv2.CAP_PROP_FPS)
                print(f"  📐 Resolution: {width}x{height}, FPS: {fps}")
            else:
                print(f"  ❌ Index {i}: Frame read failed")
            cap.release()
        else:
            print(f"  ❌ Index {i}: Failed to open camera")

def test_virtual_camera():
    """Test virtual camera specifically"""
    print("\n🔍 Testing Virtual Camera...")
    print("=" * 50)
    
    # Try different approaches for virtual camera
    approaches = [
        (0, cv2.CAP_DSHOW, "DirectShow Index 0"),
        (0, cv2.CAP_MSMF, "Media Foundation Index 0"),
        (1, cv2.CAP_DSHOW, "DirectShow Index 1"),
        (1, cv2.CAP_MSMF, "Media Foundation Index 1"),
    ]
    
    for index, backend, name in approaches:
        print(f"\n📹 Testing {name}:")
        cap = cv2.VideoCapture(index, backend)
        if cap.isOpened():
            print(f"  ✅ {name}: Camera opened successfully")
            
            # Try multiple frame reads
            success_count = 0
            for attempt in range(5):
                ret, frame = cap.read()
                if ret:
                    success_count += 1
                    print(f"  ✅ Frame {attempt + 1}: Success - {frame.shape}")
                else:
                    print(f"  ❌ Frame {attempt + 1}: Failed")
                time.sleep(0.1)
            
            print(f"  📊 Success Rate: {success_count}/5 frames")
            cap.release()
        else:
            print(f"  ❌ {name}: Failed to open camera")

def suggest_fixes():
    """Suggest fixes for common camera issues"""
    print("\n🔧 Camera Troubleshooting Suggestions:")
    print("=" * 50)
    
    print("\n1. 📱 Virtual Camera Issues:")
    print("   - Ensure your phone's virtual camera app is running")
    print("   - Try restarting the virtual camera app")
    print("   - Check if the virtual camera is set as default")
    
    print("\n2. 🖥️ Physical Camera Issues:")
    print("   - Check if camera is connected and recognized by Windows")
    print("   - Try using a different USB port")
    print("   - Update camera drivers")
    
    print("\n3. 🎯 App Settings:")
    print("   - Try different camera indexes (0, 1, 2)")
    print("   - Switch between DirectShow and Media Foundation backends")
    print("   - Restart the PlayaTewsIdentityMasker app")
    
    print("\n4. 🔄 System Solutions:")
    print("   - Restart Windows Camera app")
    print("   - Check Windows Privacy Settings (Camera access)")
    print("   - Disable other apps using the camera")

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Troubleshooting")
    print("=" * 60)
    
    # Test different approaches
    test_camera_backends()
    test_camera_indexes()
    test_virtual_camera()
    suggest_fixes()
    
    print("\n" + "=" * 60)
    print("✅ Camera troubleshooting complete!")
    print("💡 If issues persist, try restarting the app with different camera settings")

if __name__ == "__main__":
    main() 