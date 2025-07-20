#!/usr/bin/env python3
"""
Simple test for lazy loading system without QWidget creation
"""

import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_lazy_loader_core():
    """Test the core lazy loading functionality without widgets"""
    logger.info("🧪 Testing lazy loader core functionality...")
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.QSimpleLazyLoader import QSimpleLazyLoader
        
        # Create lazy loader
        lazy_loader = QSimpleLazyLoader()
        logger.info("✅ Lazy loader created successfully")
        
        # Test component registration
        def test_factory():
            return {"name": "Test Component", "type": "mock"}
        
        # Register component (this should work without QApplication)
        lazy_loader.register_component('test_component', test_factory, load_priority=1)
        logger.info("✅ Component registration successful")
        
        # Test stats
        stats = lazy_loader.get_stats()
        logger.info(f"✅ Initial stats: {stats}")
        
        # Test component loading
        component = lazy_loader.get_component('test_component')
        if component:
            logger.info(f"✅ Component loaded: {component}")
        else:
            logger.error("❌ Component loading failed")
            return False
        
        # Test updated stats
        stats_after = lazy_loader.get_stats()
        logger.info(f"✅ Stats after loading: {stats_after}")
        
        # Cleanup
        lazy_loader.clear()
        logger.info("✅ Cleanup successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Lazy loader core test failed: {e}")
        return False

def test_optimized_app_import():
    """Test if optimized app can be imported"""
    logger.info("🧪 Testing optimized app import...")
    
    try:
        from apps.PlayaTewsIdentityMasker.QOptimizedPlayaTewsIdentityMaskerApp import (
            OptimizedPlayaTewsIdentityMaskerApp
        )
        logger.info("✅ Optimized app import successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Optimized app import failed: {e}")
        return False

def main():
    """Run simple lazy loading tests"""
    logger.info("🚀 Starting Simple Lazy Loading Tests...")
    
    tests = [
        ("Lazy Loader Core", test_lazy_loader_core),
        ("Optimized App Import", test_optimized_app_import),
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
    logger.info("📊 SIMPLE LAZY LOADING TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 Lazy loading core functionality is working!")
        return True
    else:
        logger.error("⚠️  Some lazy loading tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 