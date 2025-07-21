#!/usr/bin/env python3
"""
PlayaTewsIdentityMasker - Traditional Interface Only Launcher

This script launches the application with only the traditional interface,
bypassing the OBS-style components that might be causing issues.
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

def main():
    """Main function to launch the traditional interface"""
    
    print("🚀 PlayaTewsIdentityMasker - Traditional Interface Only")
    print("=" * 60)
    
    # Set up local Python environment
    if not setup_local_python_environment():
        print("❌ Failed to set up local Python environment")
        return 1
    
    # Test that we can import key packages from local directory
    print("\n🔍 Testing local package imports...")
    
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
    
    print("\n🎯 Launching PlayaTewsIdentityMasker with Traditional Interface...")
    print("=" * 60)
    
    # Import and run the traditional application
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        # Set up userdata path
        userdata_path = Path.cwd()
        
        # Create and run the application
        app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        app.run()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure all dependencies are installed in the local Python311 directory")
        print("2. Run: Python311\\Scripts\\pip.exe install --target=Python311\\site-packages -r requirements_minimal.txt")
        return 1
    except Exception as e:
        print(f"❌ Application Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 