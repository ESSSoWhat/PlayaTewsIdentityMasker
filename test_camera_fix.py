#!/usr/bin/env python3
"""
Camera and Model Test Script
Tests camera functionality and model loading for DeepFaceLive
"""

import sys
import time
import cv2
import numpy as np

def test_camera_devices():
    """Test available camera devices"""
    print("🔍 Testing Camera Devices...")
    
    # Test OpenCV camera detection
    available_cameras = []
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Camera {i}: Available (Resolution: {frame.shape[1]}x{frame.shape[0]})")
                available_cameras.append(i)
            cap.release()
        else:
            print(f"❌ Camera {i}: Not available")
    
    return available_cameras

def test_modelhub_imports():
    """Test modelhub imports"""
    print("\n🔍 Testing ModelHub Imports...")
    
    try:
        from modelhub import DFLive
        print("✅ DFLive import successful")
        
        # Test available devices
        devices = DFLive.get_available_devices()
        print(f"✅ Available devices: {devices}")
        
        return True
    except Exception as e:
        print(f"❌ ModelHub import error: {e}")
        return False

def test_onnx_models():
    """Test ONNX model imports"""
    print("\n🔍 Testing ONNX Models...")
    
    try:
        from modelhub.onnx import InsightFaceSwap
        print("✅ InsightFaceSwap import successful")
        
        # Test available devices for InsightFaceSwap
        devices = InsightFaceSwap.get_available_devices()
        print(f"✅ InsightFaceSwap devices: {devices}")
        
        return True
    except Exception as e:
        print(f"❌ ONNX models error: {e}")
        return False

def test_dfm_models():
    """Test DFM model loading"""
    print("\n🔍 Testing DFM Models...")
    
    try:
        from pathlib import Path
        dfm_models_path = Path("dfm_models")
        
        if dfm_models_path.exists():
            dfm_files = list(dfm_models_path.glob("*.dfm"))
            print(f"✅ Found {len(dfm_files)} DFM model files:")
            for dfm_file in dfm_files:
                print(f"   - {dfm_file.name}")
            return True
        else:
            print("❌ dfm_models directory not found")
            return False
    except Exception as e:
        print(f"❌ DFM models error: {e}")
        return False

def test_camera_capture():
    """Test actual camera capture"""
    print("\n🔍 Testing Camera Capture...")
    
    cameras = test_camera_devices()
    if not cameras:
        print("❌ No cameras available for testing")
        return False
    
    # Test the first available camera
    camera_id = cameras[0]
    print(f"📹 Testing camera {camera_id}...")
    
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"❌ Failed to open camera {camera_id}")
        return False
    
    # Try to capture a few frames
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"✅ Frame {i+1}: Captured successfully (Shape: {frame.shape})")
        else:
            print(f"❌ Frame {i+1}: Failed to capture")
            cap.release()
            return False
    
    cap.release()
    print("✅ Camera capture test successful")
    return True

def main():
    """Run all camera and model tests"""
    print("=" * 60)
    print("CAMERA AND MODEL TESTING")
    print("=" * 60)
    
    results = {}
    
    # Test camera devices
    results['camera_devices'] = test_camera_devices()
    print()
    
    # Test camera capture
    results['camera_capture'] = test_camera_capture()
    print()
    
    # Test modelhub imports
    results['modelhub'] = test_modelhub_imports()
    print()
    
    # Test ONNX models
    results['onnx_models'] = test_onnx_models()
    print()
    
    # Test DFM models
    results['dfm_models'] = test_dfm_models()
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if results['camera_devices']:
        print("✅ Camera devices detected")
    else:
        print("❌ No camera devices found")
    
    if results['camera_capture']:
        print("✅ Camera capture working")
    else:
        print("❌ Camera capture failed")
    
    if results['modelhub']:
        print("✅ ModelHub imports working")
    else:
        print("❌ ModelHub imports failed")
    
    if results['onnx_models']:
        print("✅ ONNX models working")
    else:
        print("❌ ONNX models failed")
    
    if results['dfm_models']:
        print("✅ DFM models available")
    else:
        print("❌ DFM models not found")
    
    print()
    print("RECOMMENDATIONS:")
    
    if all(results.values()):
        print("✅ Everything is working! Camera should appear in DeepFaceLive.")
        print("   - Camera devices are detected and working")
        print("   - Models are loading properly")
        print("   - Face swap functionality should work")
    elif results['camera_devices'] and results['camera_capture']:
        print("✅ Camera is working, but there may be model issues")
        print("   - Try restarting the application")
        print("   - Check if face swap models are selected")
    else:
        print("❌ Camera issues detected")
        print("   - Check camera permissions")
        print("   - Ensure camera is not being used by another application")
        print("   - Try different camera settings in DeepFaceLive")

if __name__ == "__main__":
    main() 