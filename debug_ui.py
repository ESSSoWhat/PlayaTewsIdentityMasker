#!/usr/bin/env python3
"""
Debug script to test UI components and identify issues
"""

import sys
import os
from pathlib import Path

def setup_local_python_environment():
    """Set up the environment to use local Python311 directory"""
    
    # Get the current script directory
    script_dir = Path(__file__).parent.absolute()
    
    # Set up paths for local Python311
    local_site_packages = script_dir / "Python311" / "site-packages"
    local_scripts = script_dir / "Python311" / "Scripts"
    
    # Add local site-packages to Python path
    if str(local_site_packages) not in sys.path:
        sys.path.insert(0, str(local_site_packages))
        print(f"✅ Added local site-packages to Python path: {local_site_packages}")
    
    # Set environment variables
    os.environ['PYTHONPATH'] = str(local_site_packages) + os.pathsep + os.environ.get('PYTHONPATH', '')
    os.environ['PATH'] = str(local_scripts) + os.pathsep + os.environ.get('PATH', '')
    
    return True

def test_basic_imports():
    """Test basic imports"""
    print("\n🔍 Testing Basic Imports...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5.QtWidgets imported")
    except ImportError as e:
        print(f"❌ PyQt5.QtWidgets import failed: {e}")
        return False
    
    try:
        from xlib import qt as qtx
        print("✅ xlib.qt imported")
    except ImportError as e:
        print(f"❌ xlib.qt import failed: {e}")
        return False
    
    return True

def test_app_imports():
    """Test application-specific imports"""
    print("\n🔍 Testing Application Imports...")
    
    try:
        from apps.PlayaTewsIdentityMasker.backend import BackendDB, BackendWeakHeap, BackendSignal, BackendConnection
        print("✅ Backend components imported")
    except ImportError as e:
        print(f"❌ Backend components import failed: {e}")
        return False
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.QFileSource import QFileSource
        print("✅ QFileSource imported")
    except ImportError as e:
        print(f"❌ QFileSource import failed: {e}")
        return False
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.QCameraSource import QCameraSource
        print("✅ QCameraSource imported")
    except ImportError as e:
        print(f"❌ QCameraSource import failed: {e}")
        return False
    
    return True

def test_obs_ui_import():
    """Test OBS UI import specifically"""
    print("\n🔍 Testing OBS UI Import...")
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.QOBSStyleUI import QOBSStyleUI
        print("✅ QOBSStyleUI imported successfully")
        return True
    except ImportError as e:
        print(f"❌ QOBSStyleUI import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_simple_test_app():
    """Create a simple test application"""
    print("\n🎯 Creating Simple Test Application...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
        from PyQt5.QtCore import Qt
        
        app = QApplication(sys.argv)
        
        # Create main window
        window = QMainWindow()
        window.setWindowTitle("PlayaTewsIdentityMasker - Debug Test")
        window.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Add test label
        label = QLabel("PlayaTewsIdentityMasker Debug Test")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("QLabel { font-size: 18px; font-weight: bold; margin: 20px; }")
        layout.addWidget(label)
        
        # Add test button
        button = QPushButton("Test Button")
        button.setStyleSheet("QPushButton { font-size: 14px; padding: 10px; }")
        layout.addWidget(button)
        
        central_widget.setLayout(layout)
        window.setCentralWidget(central_widget)
        
        window.show()
        
        print("✅ Simple test application created and shown")
        return app, window
        
    except Exception as e:
        print(f"❌ Failed to create test application: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def main():
    """Main debug function"""
    
    print("🚀 PlayaTewsIdentityMasker - UI Debug Test")
    print("=" * 60)
    
    # Set up local Python environment
    if not setup_local_python_environment():
        print("❌ Failed to set up local Python environment")
        return 1
    
    # Test basic imports
    if not test_basic_imports():
        print("❌ Basic imports failed")
        return 1
    
    # Test app imports
    if not test_app_imports():
        print("❌ Application imports failed")
        return 1
    
    # Test OBS UI import
    obs_ui_works = test_obs_ui_import()
    
    # Create simple test app
    app, window = create_simple_test_app()
    if app is None:
        print("❌ Failed to create test application")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ Debug test completed!")
    print(f"📊 OBS UI Import: {'✅ Working' if obs_ui_works else '❌ Failed'}")
    print("\n🎯 Test application should be visible on screen.")
    print("   Close the window to exit.")
    
    # Run the application
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main()) 