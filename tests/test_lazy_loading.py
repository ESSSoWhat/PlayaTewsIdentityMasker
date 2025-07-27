#!/usr/bin/env python3
"""
Test script for the new lazy loading system
"""

import sys
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_lazy_loader_import():
    """Test if lazy loader can be imported"""
    logger.info("🧪 Testing lazy loader import...")
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.QSimpleLazyLoader import (
            QSimpleLazyLoader, QLazyLoadPlaceholder, get_lazy_loader, cleanup_lazy_loader
        )
        logger.info("✅ Lazy loader imports successful")
        return True
    except Exception as e:
        logger.error(f"❌ Lazy loader import failed: {e}")
        return False

def test_lazy_loader_functionality():
    """Test lazy loader basic functionality"""
    logger.info("🧪 Testing lazy loader functionality...")
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.QSimpleLazyLoader import get_lazy_loader, cleanup_lazy_loader
        
        # Get lazy loader
        lazy_loader = get_lazy_loader()
        logger.info("✅ Lazy loader created successfully")
        
        # Test component registration (without creating actual widgets)
        def test_factory():
            # Return a simple object instead of a widget for testing
            class MockComponent:
                def __init__(self):
                    self.name = "Test Component"
                    self.is_loaded = True
            return MockComponent()
        
        placeholder = lazy_loader.register_component('test_component', test_factory, load_priority=1)
        logger.info("✅ Component registration successful")
        
        # Test stats
        stats = lazy_loader.get_stats()
        logger.info(f"✅ Stats: {stats}")
        
        # Test component loading
        component = lazy_loader.get_component('test_component')
        if component:
            logger.info("✅ Component loading successful")
        else:
            logger.error("❌ Component loading failed")
            return False
        
        # Test updated stats
        stats_after = lazy_loader.get_stats()
        logger.info(f"✅ Stats after loading: {stats_after}")
        
        # Cleanup
        cleanup_lazy_loader()
        logger.info("✅ Cleanup successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Lazy loader functionality test failed: {e}")
        return False

def test_optimized_app_with_lazy_loading():
    """Test optimized app with lazy loading"""
    logger.info("🧪 Testing optimized app with lazy loading...")
    
    try:
        from apps.PlayaTewsIdentityMasker.QOptimizedPlayaTewsIdentityMaskerApp import (
            OptimizedPlayaTewsIdentityMaskerApp
        )
        logger.info("✅ Optimized app import successful")
        
        # Test instantiation (without full initialization)
        userdata_path = Path("userdata")
        app = OptimizedPlayaTewsIdentityMaskerApp(userdata_path)
        logger.info("✅ Optimized app instantiation successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Optimized app test failed: {e}")
        return False

def main():
    """Run all lazy loading tests"""
    logger.info("🚀 Starting Lazy Loading System Tests...")
    
    tests = [
        ("Lazy Loader Import", test_lazy_loader_import),
        ("Lazy Loader Functionality", test_lazy_loader_functionality),
        ("Optimized App with Lazy Loading", test_optimized_app_with_lazy_loading),
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
    logger.info("📊 LAZY LOADING TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 Lazy loading system is working correctly!")
        return True
    else:
        logger.error("⚠️  Some lazy loading tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 