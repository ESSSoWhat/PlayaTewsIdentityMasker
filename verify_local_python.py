#!/usr/bin/env python3
"""
Verify Local Python Environment for PlayaTewsIdentityMasker

This script checks that all required packages are available from the local Python311 directory.
"""

import sys
import os
from pathlib import Path

def check_local_python_setup():
    """Check if local Python environment is properly set up"""
    
    script_dir = Path(__file__).parent.absolute()
    local_site_packages = script_dir / "Python311" / "site-packages"
    
    print("🔍 Verifying Local Python Environment")
    print("=" * 50)
    
    # Check if local directory exists
    if not local_site_packages.exists():
        print(f"❌ Local site-packages directory not found: {local_site_packages}")
        return False
    
    print(f"✅ Local site-packages directory found: {local_site_packages}")
    
    # Check if it's in Python path
    if str(local_site_packages) in sys.path:
        print("✅ Local site-packages is in Python path")
    else:
        print("⚠️  Local site-packages is not in Python path (will be added)")
        sys.path.insert(0, str(local_site_packages))
    
    return True

def test_package_imports():
    """Test importing key packages from local directory"""
    
    packages_to_test = [
        ("numpy", "NumPy"),
        ("cv2", "OpenCV"),
        ("PyQt5", "PyQt5"),
        ("PIL", "Pillow"),
        ("psutil", "psutil"),
        ("yaml", "PyYAML"),
        ("ffmpeg", "ffmpeg-python"),
    ]
    
    print("\n📦 Testing Package Imports")
    print("-" * 30)
    
    all_success = True
    
    for module_name, display_name in packages_to_test:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {display_name} {version}")
        except ImportError as e:
            print(f"❌ {display_name}: {e}")
            all_success = False
    
    return all_success

def test_application_imports():
    """Test importing application modules"""
    
    print("\n🎯 Testing Application Imports")
    print("-" * 30)
    
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerOBSStyleApp import PlayaTewsIdentityMaskerOBSStyleApp
        print("✅ PlayaTewsIdentityMaskerOBSStyleApp")
    except ImportError as e:
        print(f"❌ PlayaTewsIdentityMaskerOBSStyleApp: {e}")
        return False
    
    try:
        from xlib.qt.widgets.QXMainApplication import QXMainApplication
        print("✅ QXMainApplication")
    except ImportError as e:
        print(f"❌ QXMainApplication: {e}")
        return False
    
    return True

def main():
    """Main verification function"""
    
    print("🚀 PlayaTewsIdentityMasker - Local Python Environment Verification")
    print("=" * 70)
    
    # Check setup
    if not check_local_python_setup():
        print("\n❌ Local Python setup failed!")
        return 1
    
    # Test packages
    if not test_package_imports():
        print("\n⚠️  Some packages failed to import!")
        print("   Try running: Python311\\Scripts\\pip.exe install --target=Python311\\site-packages package_name")
    
    # Test application
    if not test_application_imports():
        print("\n❌ Application imports failed!")
        return 1
    
    print("\n" + "=" * 70)
    print("✅ Local Python Environment Verification Complete!")
    print("\n🎯 Ready to start the application:")
    print("   python run_with_local_python.py")
    print("   or")
    print("   start_app_local_python.bat")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 