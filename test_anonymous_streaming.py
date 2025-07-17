#!/usr/bin/env python3
"""
Test script for PlayaTewsIdentityMasker StreamFaceLabs Features
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that StreamFaceLabs component can be imported"""
    try:
        from apps.PlayaTewsIdentityMasker.backend import StreamFaceLabs
from apps.PlayaTewsIdentityMasker.ui import QStreamFaceLabsPanel
        print("✅ StreamFaceLabs component imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_directories():
    """Test that required directories exist or can be created"""
    test_dirs = ['settings', 'dfm_models', 'animatables']
    
    for dir_name in test_dirs:
        test_path = Path(dir_name)
        test_path.mkdir(exist_ok=True)
        if test_path.exists():
            print(f"✅ Directory {dir_name} ready")
        else:
            print(f"❌ Failed to create directory {dir_name}")
            return False
    return True

def test_stream_face_labs():
    """Test StreamFaceLabs component"""
    try:
        from apps.PlayaTewsIdentityMasker.backend import StreamFaceLabs
        
        print("✅ StreamFaceLabs component available")
        return True
    except Exception as e:
        print(f"❌ Error testing StreamFaceLabs: {e}")
        return False

def test_ui_components():
    """Test UI components"""
    try:
        from apps.PlayaTewsIdentityMasker.ui import QStreamFaceLabsPanel
        
        print("✅ StreamFaceLabs UI component available")
        return True
    except Exception as e:
        print(f"❌ Error testing UI components: {e}")
        return False

def test_backend_components():
    """Test backend components"""
    try:
        from apps.PlayaTewsIdentityMasker.backend import StreamFaceLabs
        
        print("✅ StreamFaceLabs backend component available")
        return True
    except Exception as e:
        print(f"❌ Error testing backend components: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing PlayaTewsIdentityMasker StreamFaceLabs Features")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Directory Test", test_directories),
        ("StreamFaceLabs Component Test", test_stream_face_labs),
        ("UI Components Test", test_ui_components),
        ("Backend Components Test", test_backend_components),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! StreamFaceLabs features are ready.")
        print("\n📖 To use the features:")
        print("1. Run: python main.py run PlayaTewsIdentityMasker")
        print("2. Look for the StreamFaceLabs panel in the UI")
        print("3. Configure your model training settings and start training!")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 