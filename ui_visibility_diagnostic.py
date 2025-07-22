#!/usr/bin/env python3
"""
UI Visibility Diagnostic Script
Checks if all UI components are properly accessible and visible
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ui_component_imports():
    """Test if all UI components can be imported"""
    logger.info("🧪 Testing UI component imports...")
    
    components_to_test = [
        ('QFileSource', 'apps.PlayaTewsIdentityMasker.ui.QFileSource'),
        ('QCameraSource', 'apps.PlayaTewsIdentityMasker.ui.QCameraSource'),
        ('QFaceDetector', 'apps.PlayaTewsIdentityMasker.ui.QFaceDetector'),
        ('QFaceAligner', 'apps.PlayaTewsIdentityMasker.ui.QFaceAligner'),
        ('QFaceMarker', 'apps.PlayaTewsIdentityMasker.ui.QFaceMarker'),
        ('QFaceAnimator', 'apps.PlayaTewsIdentityMasker.ui.QFaceAnimator'),
        ('QFaceSwapInsight', 'apps.PlayaTewsIdentityMasker.ui.QFaceSwapInsight'),
        ('QFaceSwapDFM', 'apps.PlayaTewsIdentityMasker.ui.QFaceSwapDFM'),
        ('QFrameAdjuster', 'apps.PlayaTewsIdentityMasker.ui.QFrameAdjuster'),
        ('QFaceMerger', 'apps.PlayaTewsIdentityMasker.ui.QFaceMerger'),
        ('QStreamOutput', 'apps.PlayaTewsIdentityMasker.ui.QStreamOutput'),
        ('QVoiceChanger', 'apps.PlayaTewsIdentityMasker.ui.QVoiceChanger'),
        ('QEnhancedStreamOutput', 'apps.PlayaTewsIdentityMasker.ui.QEnhancedStreamOutput'),
        ('QBCFrameViewer', 'apps.PlayaTewsIdentityMasker.ui.widgets.QBCFrameViewer'),
        ('QBCFaceAlignViewer', 'apps.PlayaTewsIdentityMasker.ui.widgets.QBCFaceAlignViewer'),
        ('QBCFaceSwapViewer', 'apps.PlayaTewsIdentityMasker.ui.widgets.QBCFaceSwapViewer'),
        ('QBCMergedFrameViewer', 'apps.PlayaTewsIdentityMasker.ui.widgets.QBCMergedFrameViewer'),
    ]
    
    results = []
    for component_name, import_path in components_to_test:
        try:
            module = __import__(import_path, fromlist=[component_name])
            component_class = getattr(module, component_name)
            logger.info(f"✅ {component_name}: Imported successfully")
            results.append((component_name, True, None))
        except Exception as e:
            logger.error(f"❌ {component_name}: Import failed - {e}")
            results.append((component_name, False, str(e)))
    
    return results

def test_optimized_app_components():
    """Test if optimized app can access all components"""
    logger.info("🧪 Testing optimized app component access...")
    
    try:
        from apps.PlayaTewsIdentityMasker.QOptimizedPlayaTewsIdentityMaskerApp import (
            OptimizedPlayaTewsIdentityMaskerApp
        )
        logger.info("✅ OptimizedPlayaTewsIdentityMaskerApp: Imported successfully")
        
        # Test instantiation without full initialization
        userdata_path = Path("userdata")
        app = OptimizedPlayaTewsIdentityMaskerApp(userdata_path)
        logger.info("✅ OptimizedPlayaTewsIdentityMaskerApp: Instantiated successfully")
        
        return True
    except Exception as e:
        logger.error(f"❌ OptimizedPlayaTewsIdentityMaskerApp: Failed - {e}")
        return False

def test_ui_manager():
    """Test UI manager functionality"""
    logger.info("🧪 Testing UI manager...")
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.QOptimizedUIManager import get_ui_manager
        ui_manager = get_ui_manager()
        logger.info("✅ UI Manager: Created successfully")
        
        # Test component registration
        ui_manager.register_component('test_component', lambda: None, load_priority=1)
        logger.info("✅ UI Manager: Component registration works")
        
        return True
    except Exception as e:
        logger.error(f"❌ UI Manager: Failed - {e}")
        return False

def main():
    """Run all UI visibility diagnostics"""
    logger.info("🔍 Starting UI Visibility Diagnostics...")
    
    tests = [
        ("UI Component Imports", test_ui_component_imports),
        ("Optimized App Components", test_optimized_app_components),
        ("UI Manager", test_ui_manager),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("📊 DIAGNOSTIC SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All UI components are accessible!")
        return True
    else:
        logger.error("⚠️  Some UI components have issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 