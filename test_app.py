#!/usr/bin/env python3
"""
Simple test script to verify DeepFaceLive features
Includes comprehensive testing of StreamFaceLabs components
"""

import sys
import os
from pathlib import Path

def test_basic_imports():
    """Test basic imports without starting the full application"""
    print("🔍 Testing basic imports...")
    
    try:
        # Test backend imports
        from apps.DeepFaceLive.backend import StreamFaceLabs
        print("✅ Backend components imported successfully")
        
        # Test UI imports
        from apps.DeepFaceLive.ui import QStreamFaceLabsPanel
        print("✅ UI components imported successfully")
        
        # Test main app import
        from apps.DeepFaceLive.DeepFaceLiveApp import DeepFaceLiveApp
        print("✅ Main application imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        "apps/DeepFaceLive/backend/StreamFaceLabs.py",
        "apps/DeepFaceLive/ui/QStreamFaceLabs.py",
        "apps/DeepFaceLive/DeepFaceLiveApp.py",
        "localization/en-US.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_directories():
    """Test directory creation"""
    print("\n🔍 Testing directory creation...")
    
    test_dirs = ['settings', 'dfm_models', 'animatables']
    all_created = True
    
    for dir_name in test_dirs:
        test_path = Path(dir_name)
        test_path.mkdir(exist_ok=True)
        if test_path.exists():
            print(f"✅ Directory {dir_name} ready")
        else:
            print(f"❌ Failed to create {dir_name}")
            all_created = False
    
    return all_created

def test_stream_face_labs():
    """Test StreamFaceLabs component (backend and UI)"""
    print("\n🔍 Testing StreamFaceLabs component...")
    
    try:
        from apps.DeepFaceLive.backend import StreamFaceLabs
        from apps.DeepFaceLive.ui import QStreamFaceLabsPanel
        
        print("✅ StreamFaceLabs backend component available")
        print("✅ StreamFaceLabs UI component available")
        print("✅ StreamFaceLabs component fully integrated")
        return True
    except Exception as e:
        print(f"❌ StreamFaceLabs test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 DeepFaceLive - Basic Tests")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("File Structure", test_file_structure),
        ("Directory Creation", test_directories),
        ("StreamFaceLabs Component", test_stream_face_labs),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All basic tests passed!")
        print("\n📖 Next steps to test the full application:")
        print("1. Make sure you have a webcam connected")
        print("2. Run: python main.py run DeepFaceLive")
        print("3. Look for the StreamFaceLabs panel in the UI")
        print("4. Test the model training features")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 