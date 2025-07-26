#!/usr/bin/env python3
"""
Comprehensive fix for PlayaTewsIdentityMasker OBS-style interface issues
"""

import sys
import os
from pathlib import Path

def setup_local_python_environment():
    """Set up the environment to use local Python311 directory"""
    
    script_dir = Path(__file__).parent.absolute()
    local_site_packages = script_dir / "Python311" / "site-packages"
    local_scripts = script_dir / "Python311" / "Scripts"
    
    if str(local_site_packages) not in sys.path:
        sys.path.insert(0, str(local_site_packages))
        print(f"✅ Added local site-packages to Python path: {local_site_packages}")
    
    os.environ['PYTHONPATH'] = str(local_site_packages) + os.pathsep + os.environ.get('PYTHONPATH', '')
    os.environ['PATH'] = str(local_scripts) + os.pathsep + os.environ.get('PATH', '')
    
    return True

def install_missing_dependencies():
    """Install any missing dependencies"""
    print("\n🔧 Installing missing dependencies...")
    
    missing_packages = [
        'asyncio-compat',
        'deep-translator', 
        'gtts',
    ]
    
    for package in missing_packages:
        try:
            print(f"Installing {package}...")
            os.system(f"Python311\\Scripts\\pip.exe install --target=Python311\\site-packages {package}")
        except Exception as e:
            print(f"Warning: Could not install {package}: {e}")

def create_fixed_obs_launcher():
    """Create a fixed OBS-style launcher"""
    
    print("\n🔧 Creating fixed OBS-style launcher...")
    
    fixed_launcher_code = '''#!/usr/bin/env python3
"""
PlayaTewsIdentityMasker - Fixed OBS-Style Interface Launcher
"""

import sys
import os
from pathlib import Path
from PyQt5.QtCore import Qt

def setup_local_python_environment():
    script_dir = Path(__file__).parent.absolute()
    local_site_packages = script_dir / "Python311" / "site-packages"
    local_scripts = script_dir / "Python311" / "Scripts"
    
    if str(local_site_packages) not in sys.path:
        sys.path.insert(0, str(local_site_packages))
        print(f"✅ Added local site-packages to Python path: {local_site_packages}")
    
    os.environ['PYTHONPATH'] = str(local_site_packages) + os.pathsep + os.environ.get('PYTHONPATH', '')
    os.environ['PATH'] = str(local_scripts) + os.pathsep + os.environ.get('PATH', '')
    
    return True

def create_safe_obs_ui(stream_output, userdata_path):
    """Create a safe OBS-style UI with error handling"""
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.QOBSStyleUI import QOBSStyleUI
        print("✅ QOBSStyleUI imported successfully")
        return QOBSStyleUI(stream_output, userdata_path)
    except ImportError as e:
        print(f"⚠️ QOBSStyleUI import failed: {e}")
        # Create a fallback UI
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
        from PyQt5.QtCore import Qt
        
        fallback_widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("OBS-Style Interface")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("QLabel { font-size: 18px; font-weight: bold; margin: 20px; }")
        layout.addWidget(label)
        
        info_label = QLabel("Enhanced streaming interface with multi-platform support")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("QLabel { margin: 10px; }")
        layout.addWidget(info_label)
        
        # Add some basic controls
        stream_btn = QPushButton("Start Streaming")
        stream_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(stream_btn)
        
        record_btn = QPushButton("Start Recording")
        record_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        layout.addWidget(record_btn)
        
        fallback_widget.setLayout(layout)
        return fallback_widget

def main():
    """Main function to launch the fixed OBS-style application"""
    
    print("🚀 PlayaTewsIdentityMasker - Fixed OBS-Style Interface")
    print("=" * 60)
    
    if not setup_local_python_environment():
        print("❌ Failed to set up local Python environment")
        return 1
    
    print("\\n🔍 Testing local package imports...")
    
    try:
        import numpy
        print(f"✅ NumPy {numpy.__version__} imported from local directory")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
    
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__} imported from local directory")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
    
    try:
        from PyQt5 import QtWidgets
        print("✅ PyQt5 imported from local directory")
    except ImportError as e:
        print(f"❌ PyQt5 import failed: {e}")
    
    print("\\n🎯 Launching PlayaTewsIdentityMasker with Fixed OBS-Style Interface...")
    print("=" * 60)
    
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerOBSStyleApp import PlayaTewsIdentityMaskerOBSStyleApp
        
        userdata_path = Path.cwd()
        app = PlayaTewsIdentityMaskerOBSStyleApp(userdata_path=userdata_path)
        app.run()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\\n🔧 Troubleshooting:")
        print("1. Make sure all dependencies are installed in the local Python311 directory")
        print("2. Run: Python311\\\\Scripts\\\\pip.exe install --target=Python311\\\\site-packages -r requirements_minimal.txt")
        return 1
    except Exception as e:
        print(f"❌ Application Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    
    with open('run_obs_fixed.py', 'w') as f:
        f.write(fixed_launcher_code)
    
    print("✅ Created run_obs_fixed.py")

def create_comprehensive_test():
    """Create a comprehensive test to verify all components"""
    
    print("\n🔧 Creating comprehensive component test...")
    
    test_code = '''#!/usr/bin/env python3
"""
Comprehensive component test for PlayaTewsIdentityMasker
"""

import sys
import os
from pathlib import Path

def setup_local_python_environment():
    script_dir = Path(__file__).parent.absolute()
    local_site_packages = script_dir / "Python311" / "site-packages"
    local_scripts = script_dir / "Python311" / "Scripts"
    
    if str(local_site_packages) not in sys.path:
        sys.path.insert(0, str(local_site_packages))
    
    os.environ['PYTHONPATH'] = str(local_site_packages) + os.pathsep + os.environ.get('PYTHONPATH', '')
    os.environ['PATH'] = str(local_scripts) + os.pathsep + os.environ.get('PATH', '')
    
    return True

def test_all_components():
    print("🚀 Comprehensive Component Test")
    print("=" * 50)
    
    components = [
        ("Basic PyQt5", "from PyQt5.QtWidgets import QApplication"),
        ("xlib.qt", "from xlib import qt as qtx"),
        ("Backend Components", "from apps.PlayaTewsIdentityMasker.backend import BackendDB, BackendWeakHeap"),
        ("UI Components", "from apps.PlayaTewsIdentityMasker.ui.QFileSource import QFileSource"),
        ("OBS UI", "from apps.PlayaTewsIdentityMasker.ui.QOBSStyleUI import QOBSStyleUI"),
        ("Enhanced Stream Output", "from apps.PlayaTewsIdentityMasker.backend.EnhancedStreamOutput import EnhancedStreamOutput"),
        ("CSW Components", "from xlib.mp import csw as lib_csw"),
    ]
    
    results = {}
    
    for name, import_statement in components:
        try:
            exec(import_statement)
            print(f"✅ {name}")
            results[name] = True
        except Exception as e:
            print(f"❌ {name}: {e}")
            results[name] = False
    
    print("\\n📊 Test Results:")
    passed = sum(results.values())
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All components working!")
        return True
    else:
        print("⚠️ Some components have issues")
        return False

if __name__ == "__main__":
    setup_local_python_environment()
    test_all_components()
'''
    
    with open('test_all_components.py', 'w') as f:
        f.write(test_code)
    
    print("✅ Created test_all_components.py")

def main():
    """Main fix function"""
    
    print("🔧 PlayaTewsIdentityMasker - Comprehensive Fix Script")
    print("=" * 60)
    
    if not setup_local_python_environment():
        print("❌ Failed to set up local Python environment")
        return 1
    
    install_missing_dependencies()
    create_fixed_obs_launcher()
    create_comprehensive_test()
    
    print("\n" + "=" * 60)
    print("✅ Comprehensive fix completed!")
    print("\n🎯 Next steps:")
    print("1. Test components: python test_all_components.py")
    print("2. Try fixed OBS interface: python run_obs_fixed.py")
    print("3. Use traditional interface: python run_traditional_only.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 