#!/usr/bin/env python3
"""
Comprehensive Face Swap Functionality Test
Tests all components of the face swap pipeline
"""

import sys
import os
import time
import numpy as np
from pathlib import Path

def test_modelhub_imports():
    """Test if all required modelhub components can be imported"""
    print("🔍 Testing modelhub imports...")
    
    try:
        # Test ONNX models
        from modelhub.onnx import InsightFaceSwap, InsightFace2D106, YoloV5Face
        print("✅ ONNX models imported successfully")
        
        # Test DFLive models
        from modelhub import DFLive
        print("✅ DFLive models imported successfully")
        
        # Test backward compatibility
        from modelhub.onnx import FaceSwap
        print("✅ Backward compatibility alias working")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_face_detection():
    """Test face detection functionality"""
    print("\n🔍 Testing face detection...")
    
    try:
        from modelhub.onnx import YoloV5Face
        
        # Create a simple test image (random noise)
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Get available devices
        available_devices = YoloV5Face.get_available_devices()
        print(f"Available devices: {available_devices}")
        
        # Use the first available device
        if available_devices:
            device = available_devices[0]  # Use first device (usually GPU)
            detector = YoloV5Face(device)
            rects = detector.extract(test_image, threshold=0.5)
        else:
            print("No devices available")
            return False
        
        print(f"✅ Face detection working - found {len(rects[0])} faces")
        return True
        
    except Exception as e:
        print(f"❌ Face detection error: {e}")
        return False

def test_face_marker():
    """Test face landmark detection"""
    print("\n🔍 Testing face landmark detection...")
    
    try:
        from modelhub.onnx import InsightFace2D106
        
        # Create a simple test image
        test_image = np.random.randint(0, 255, (192, 192, 3), dtype=np.uint8)
        
        # Get available devices
        available_devices = InsightFace2D106.get_available_devices()
        
        # Use the first available device
        if available_devices:
            device = available_devices[0]  # Use first device (usually GPU)
            marker = InsightFace2D106(device)
            landmarks = marker.extract(test_image)
        else:
            print("No devices available")
            return False
        
        print(f"✅ Face landmark detection working - {landmarks[0].shape} landmarks")
        return True
        
    except Exception as e:
        print(f"❌ Face landmark detection error: {e}")
        return False

def test_face_swap():
    """Test face swap functionality"""
    print("\n🔍 Testing face swap...")
    
    try:
        from modelhub.onnx import InsightFaceSwap
        
        # Create test images
        source_image = np.random.randint(0, 255, (192, 192, 3), dtype=np.uint8)
        target_image = np.random.randint(0, 255, (192, 192, 3), dtype=np.uint8)
        
        # Get available devices
        available_devices = InsightFaceSwap.get_available_devices()
        
        # Use the first available device
        if available_devices:
            device = available_devices[0]  # Use first device (usually GPU)
            swap_model = InsightFaceSwap(device)
        else:
            print("No devices available")
            return False
        
        # Get face vector from source
        face_vector = swap_model.get_face_vector(source_image)
        
        # Generate swapped face
        swapped_image = swap_model.generate(target_image, face_vector)
        
        print(f"✅ Face swap working - output shape: {swapped_image.shape}")
        return True
        
    except Exception as e:
        print(f"❌ Face swap error: {e}")
        return False

def test_backend_components():
    """Test backend components"""
    print("\n🔍 Testing backend components...")
    
    try:
        from apps.PlayaTewsIdentityMasker.backend import (
            FaceDetector, FaceMarker, FaceAligner, 
            FaceSwapInsight, FaceSwapDFM, FaceMerger
        )
        print("✅ Backend components imported successfully")
        
        # Test if we can create instances
        from xlib.mp import csw as lib_csw
        from xlib import os as lib_os
        
        # Create mock components for testing
        from apps.PlayaTewsIdentityMasker.backend import BackendWeakHeap, BackendSignal, BackendConnection
        weak_heap = BackendWeakHeap(size_mb=512)
        reemit_frame_signal = BackendSignal()
        bc_in = BackendConnection()
        bc_out = BackendConnection()
        
        # Test face detector
        face_detector = FaceDetector(weak_heap, reemit_frame_signal, bc_in, bc_out)
        print("✅ FaceDetector created successfully")
        
        # Test face marker
        face_marker = FaceMarker(weak_heap, reemit_frame_signal, bc_in, bc_out)
        print("✅ FaceMarker created successfully")
        
        # Test face aligner
        face_aligner = FaceAligner(weak_heap, reemit_frame_signal, bc_in, bc_out)
        print("✅ FaceAligner created successfully")
        
        # Test face merger
        face_merger = FaceMerger(weak_heap, reemit_frame_signal, bc_in, bc_out)
        print("✅ FaceMerger created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend component error: {e}")
        return False

def test_ui_components():
    """Test UI components"""
    print("\n🔍 Testing UI components...")
    
    try:
        from apps.PlayaTewsIdentityMasker.ui import (
            QFaceDetector, QFaceMarker, QFaceAligner,
            QFaceSwapInsight, QFaceSwapDFM, QFaceMerger
        )
        print("✅ UI components imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ UI component error: {e}")
        return False

def test_voice_changer():
    """Test voice changer functionality"""
    print("\n🔍 Testing voice changer...")
    
    try:
        from apps.PlayaTewsIdentityMasker.backend import VoiceChanger
        print("✅ VoiceChanger backend imported successfully")
        
        # Test UI component
        from apps.PlayaTewsIdentityMasker.ui.QOptimizedOBSStyleUI import QOptimizedOBSStyleUI
        print("✅ Voice changer UI component available")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice changer error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 PlayaTewsIdentityMasker - Comprehensive Functionality Test")
    print("=" * 60)
    
    tests = [
        ("Modelhub Imports", test_modelhub_imports),
        ("Face Detection", test_face_detection),
        ("Face Landmark Detection", test_face_marker),
        ("Face Swap", test_face_swap),
        ("Backend Components", test_backend_components),
        ("UI Components", test_ui_components),
        ("Voice Changer", test_voice_changer),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Face swap functionality should be working.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 