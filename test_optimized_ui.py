#!/usr/bin/env python3
"""
Test script for the optimized PlayaTewsIdentityMasker UI
Tests the new optimized components and layout
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_optimized_components():
    """Test the optimized components"""
    print("Testing optimized components...")
    
    try:
        # Test collapsible component wrapper
        from apps.PlayaTewsIdentityMasker.ui.widgets.QCollapsibleComponentWrapper import (
            QCollapsibleComponentWrapper,
            QSmartCollapsibleGroup,
            make_collapsible,
            group_small_components
        )
        print("✓ Collapsible component wrapper imported successfully")
        
        # Test optimized components
        from apps.PlayaTewsIdentityMasker.ui.QOptimizedFrameAdjuster import QOptimizedFrameAdjuster
        from apps.PlayaTewsIdentityMasker.ui.QOptimizedFaceMarker import QOptimizedFaceMarker
        from apps.PlayaTewsIdentityMasker.ui.QOptimizedFaceAnimator import QOptimizedFaceAnimator
        from apps.PlayaTewsIdentityMasker.ui.QOptimizedFaceMerger import QOptimizedFaceMerger
        print("✓ Optimized components imported successfully")
        
        # Test grouped components
        from apps.PlayaTewsIdentityMasker.ui.QGroupedFaceDetection import QGroupedFaceDetection
        from apps.PlayaTewsIdentityMasker.ui.QGroupedInputSources import QGroupedInputSources
        print("✓ Grouped components imported successfully")
        
        # Test optimized processing window
        from apps.PlayaTewsIdentityMasker.ui.QOptimizedProcessingWindow import QOptimizedProcessingWindow
        print("✓ Optimized processing window imported successfully")
        
        # Test optimized OBS-style UI
        from apps.PlayaTewsIdentityMasker.ui.QOptimizedOBSStyleUI import QOptimizedOBSStyleUI
        print("✓ Optimized OBS-style UI imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_optimized_app():
    """Test the optimized app"""
    print("Testing optimized app...")
    
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerOptimizedApp import PlayaTewsIdentityMaskerOptimizedApp
        print("✓ Optimized app imported successfully")
        
        # Create test userdata path
        test_userdata = Path("test_userdata")
        test_userdata.mkdir(exist_ok=True)
        
        # Create app instance
        app = PlayaTewsIdentityMaskerOptimizedApp(test_userdata)
        print("✓ Optimized app created successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def run_optimized_app():
    """Run the optimized app"""
    print("Starting optimized PlayaTewsIdentityMasker...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerOptimizedApp import PlayaTewsIdentityMaskerOptimizedApp
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create test userdata path
        test_userdata = Path("test_userdata")
        test_userdata.mkdir(exist_ok=True)
        
        # Create and run optimized app
        optimized_app = PlayaTewsIdentityMaskerOptimizedApp(test_userdata)
        optimized_app.initialize()
        
        print("✓ Optimized app started successfully")
        print("Press Ctrl+C to exit")
        
        # Run the application
        sys.exit(app.exec_())
        
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Error running optimized app: {e}")
        sys.exit(1)

def main():
    """Main test function"""
    print("=" * 60)
    print("PlayaTewsIdentityMasker UI Optimization Test")
    print("=" * 60)
    
    # Test 1: Component imports
    print("\n1. Testing component imports...")
    if not test_optimized_components():
        print("Component test failed. Exiting.")
        return False
    
    # Test 2: App creation
    print("\n2. Testing app creation...")
    if not test_optimized_app():
        print("App test failed. Exiting.")
        return False
    
    print("\n" + "=" * 60)
    print("All tests passed! Starting optimized app...")
    print("=" * 60)
    
    # Run the optimized app
    run_optimized_app()

if __name__ == "__main__":
    main() 