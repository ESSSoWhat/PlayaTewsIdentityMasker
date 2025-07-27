#!/usr/bin/env python3
"""
Test Device Availability for Face Swap Models
"""

def test_available_devices():
    """Test what devices are available for each model"""
    print("🔍 Testing available devices for face swap models...")
    
    try:
        from modelhub.onnx import InsightFaceSwap, InsightFace2D106, YoloV5Face
        
        print("\n📋 Available devices for each model:")
        
        # Test InsightFaceSwap
        print(f"InsightFaceSwap: {InsightFaceSwap.get_available_devices()}")
        
        # Test InsightFace2D106
        print(f"InsightFace2D106: {InsightFace2D106.get_available_devices()}")
        
        # Test YoloV5Face
        print(f"YoloV5Face: {YoloV5Face.get_available_devices()}")
        
        # Test DFLive
        from modelhub import DFLive
        print(f"DFLive: {DFLive.get_available_devices()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing devices: {e}")
        return False

def test_csw_components():
    """Test csw module components"""
    print("\n🔍 Testing csw module components...")
    
    try:
        from xlib.mp import csw as lib_csw
        
        # Check what's available in csw
        print(f"Available csw components: {dir(lib_csw)}")
        
        # Try to find WeakHeap or similar
        for attr in dir(lib_csw):
            if 'heap' in attr.lower() or 'weak' in attr.lower():
                print(f"Found potential heap component: {attr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing csw: {e}")
        return False

if __name__ == "__main__":
    test_available_devices()
    test_csw_components() 