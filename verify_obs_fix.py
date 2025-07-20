#!/usr/bin/env python3
"""
Verification script for OBS interface fixes
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

def verify_obs_interface():
    """Verify that the OBS interface fixes are working"""
    
    print("🔍 Verifying OBS Interface Fixes")
    print("=" * 50)
    
    # Test 1: Basic imports
    print("\n1. Testing basic imports...")
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerOBSStyleApp import PlayaTewsIdentityMaskerOBSStyleApp
        print("✅ PlayaTewsIdentityMaskerOBSStyleApp import successful")
    except Exception as e:
        print(f"❌ PlayaTewsIdentityMaskerOBSStyleApp import failed: {e}")
        return False
    
    # Test 2: OBS UI import
    print("\n2. Testing OBS UI import...")
    try:
        from apps.PlayaTewsIdentityMasker.ui.QOBSStyleUI import QOBSStyleUI
        print("✅ QOBSStyleUI import successful")
    except Exception as e:
        print(f"❌ QOBSStyleUI import failed: {e}")
        return False
    
    # Test 3: Enhanced Stream Output
    print("\n3. Testing Enhanced Stream Output...")
    try:
        from apps.PlayaTewsIdentityMasker.backend.EnhancedStreamOutput import EnhancedStreamOutput
        print("✅ EnhancedStreamOutput import successful")
    except Exception as e:
        print(f"❌ EnhancedStreamOutput import failed: {e}")
        return False
    
    # Test 4: UI Components
    print("\n4. Testing UI components...")
    try:
        from apps.PlayaTewsIdentityMasker.ui.QEnhancedStreamOutput import QEnhancedStreamOutput
        print("✅ QEnhancedStreamOutput import successful")
    except Exception as e:
        print(f"❌ QEnhancedStreamOutput import failed: {e}")
        return False
    
    # Test 5: CSW Components
    print("\n5. Testing CSW components...")
    try:
        from xlib.mp import csw as lib_csw
        from apps.PlayaTewsIdentityMasker.ui.widgets.QLabelCSWNumber import QLabelCSWNumber
        print("✅ CSW components import successful")
    except Exception as e:
        print(f"❌ CSW components import failed: {e}")
        return False
    
    # Test 6: Application initialization
    print("\n6. Testing application initialization...")
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        userdata_path = Path.cwd()
        obs_app = PlayaTewsIdentityMaskerOBSStyleApp(userdata_path=userdata_path)
        print("✅ Application initialization successful")
        
        # Clean up
        if app.instance():
            app.quit()
            
    except Exception as e:
        print(f"❌ Application initialization failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All OBS interface fixes verified successfully!")
    print("\n✅ Status: OBS Interface is ready to use")
    print("\n🚀 Launch options:")
    print("  - OBS Style: python run_obs_fixed.py")
    print("  - Traditional: python run_traditional_only.py")
    print("  - Test Components: python test_all_components.py")
    
    return True

if __name__ == "__main__":
    setup_local_python_environment()
    success = verify_obs_interface()
    sys.exit(0 if success else 1) 