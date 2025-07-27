#!/usr/bin/env python3
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
    
    print("\n📊 Test Results:")
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