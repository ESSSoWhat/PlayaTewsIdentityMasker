#!/usr/bin/env python3
"""
PyQt5 Migration Verification Script

This script verifies that the PyQt6 to PyQt5 migration was successful
and all components work correctly with PyQt5.
"""

import sys
import importlib
from pathlib import Path

def test_pyqt5_import():
    """Test that PyQt5 can be imported successfully"""
    try:
        import PyQt5
        print(f"✅ PyQt5 imported successfully: {PyQt5.__version__}")
        return True
    except ImportError as e:
        print(f"❌ PyQt5 import failed: {e}")
        return False

def test_pyqt6_import():
    """Test if PyQt6 is still available (should be optional)"""
    try:
        import PyQt6
        print(f"⚠️  PyQt6 is still available: {PyQt6.__version__}")
        return True
    except ImportError:
        print("✅ PyQt6 not available (expected)")
        return False

def test_qt_compatibility_layer():
    """Test the compatibility layer"""
    try:
        from qt_compatibility import get_qt_version, is_pyqt5, is_pyqt6
        version = get_qt_version()
        print(f"✅ Compatibility layer works: Qt version {version}")
        print(f"   is_pyqt5(): {is_pyqt5()}")
        print(f"   is_pyqt6(): {is_pyqt6()}")
        return True
    except Exception as e:
        print(f"❌ Compatibility layer failed: {e}")
        return False

def test_voice_changer_import():
    """Test that voice changer can be imported"""
    try:
        # Test the backend
        from apps.PlayaTewsIdentityMasker.backend.VoiceChanger import VoiceChanger
        print("✅ Voice changer backend imported successfully")
        
        # Test the UI
        from apps.PlayaTewsIdentityMasker.ui.QVoiceChanger import QVoiceChanger
        print("✅ Voice changer UI imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Voice changer import failed: {e}")
        return False

def test_core_qt_library():
    """Test the core Qt library"""
    try:
        from xlib.qt import AlignCenter, AlignLeft, AlignTop
        print("✅ Core Qt library imported successfully")
        print(f"   AlignCenter: {AlignCenter}")
        print(f"   AlignLeft: {AlignLeft}")
        print(f"   AlignTop: {AlignTop}")
        return True
    except Exception as e:
        print(f"❌ Core Qt library import failed: {e}")
        return False

def test_widget_library():
    """Test the widget library"""
    try:
        from xlib.qt.widgets import QXWidget, QXLabel, QXButton
        print("✅ Widget library imported successfully")
        return True
    except Exception as e:
        print(f"❌ Widget library import failed: {e}")
        return False

def test_opengl_widget():
    """Test OpenGL widget"""
    try:
        from xlib.qt.widgets.QXOpenGLWidget import QXOpenGLWidget
        print("✅ OpenGL widget imported successfully")
        return True
    except Exception as e:
        print(f"❌ OpenGL widget import failed: {e}")
        return False

def check_remaining_pyqt6_references():
    """Check for any remaining PyQt6 references in code files"""
    pyqt6_files = []
    
    for filepath in Path('.').rglob('*.py'):
        if any(skip in str(filepath) for skip in ['__pycache__', '.git', 'venv', 'env', 'node_modules']):
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'PyQt6' in content and 'qt_compatibility.py' not in str(filepath):
                    pyqt6_files.append(str(filepath))
        except Exception:
            continue
    
    if pyqt6_files:
        print(f"⚠️  Found {len(pyqt6_files)} files with PyQt6 references:")
        for file in pyqt6_files[:10]:  # Show first 10
            print(f"   - {file}")
        if len(pyqt6_files) > 10:
            print(f"   ... and {len(pyqt6_files) - 10} more")
        return False
    else:
        print("✅ No remaining PyQt6 references found in code files")
        return True

def test_basic_qt_functionality():
    """Test basic Qt functionality"""
    try:
        from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
        from PyQt5.QtCore import Qt
        
        # Create a simple test application
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create a test widget
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("PyQt5 Test")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        widget.setLayout(layout)
        
        print("✅ Basic Qt functionality test passed")
        return True
    except Exception as e:
        print(f"❌ Basic Qt functionality test failed: {e}")
        return False

def main():
    """Main verification function"""
    print("PyQt5 Migration Verification")
    print("=" * 40)
    
    tests = [
        ("PyQt5 Import", test_pyqt5_import),
        ("PyQt6 Import (Optional)", test_pyqt6_import),
        ("Compatibility Layer", test_qt_compatibility_layer),
        ("Voice Changer Import", test_voice_changer_import),
        ("Core Qt Library", test_core_qt_library),
        ("Widget Library", test_widget_library),
        ("OpenGL Widget", test_opengl_widget),
        ("Basic Qt Functionality", test_basic_qt_functionality),
        ("No PyQt6 References", check_remaining_pyqt6_references),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"Verification Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PyQt5 migration is successful.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)