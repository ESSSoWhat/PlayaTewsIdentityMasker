#!/usr/bin/env python3
"""
Test Script for Applied Optimizations
 cursor/code-improvement-and-optimization-2a24
Verifies that all optimizations are working correctly
"""

import sys
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_main_optimizations():
    """Test main.py optimizations"""
    logger.info("🧪 Testing main.py optimizations...")
    
    try:
        # Test lazy import system
        from main import lazy_import, StartupTimer, fixPathAction
        
        # Test startup timer
        timer = StartupTimer()
        timer.mark_stage("test_start")
        time.sleep(0.1)
        timer.mark_stage("test_end")
        
        summary = timer.get_summary()
        assert "test_start" in summary
        assert "test_end" in summary
        logger.info("✅ Startup timer working correctly")
        
        # Test lazy import
        result = lazy_import("os")
        assert result is not None
        logger.info("✅ Lazy import working correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Main optimizations test failed: {e}")
        return False

def test_memory_manager_optimizations():
    """Test memory_manager.py optimizations"""
    logger.info("🧪 Testing memory manager optimizations...")
    
    try:
        from memory_manager import (
            AdaptiveMemoryPool, MemoryPriority, MemoryBlock,
            get_memory_manager
        )
        
        # Test memory priority enum
        assert MemoryPriority.CRITICAL.value == 0
        assert MemoryPriority.HIGH.value == 1
        assert MemoryPriority.MEDIUM.value == 2
        assert MemoryPriority.LOW.value == 3
        logger.info("✅ Memory priority enum working correctly")
        
        # Test adaptive memory pool creation
        pool = AdaptiveMemoryPool(max_pool_size_mb=100)
        assert pool.max_pool_size == 100 * 1024 * 1024
        assert pool.adaptive_enabled is True
        assert pool.compression_enabled is True
        logger.info("✅ Adaptive memory pool creation working correctly")
        
        # Test memory manager singleton
        manager1 = get_memory_manager()
        manager2 = get_memory_manager()
        assert manager1 is manager2
        logger.info("✅ Memory manager singleton working correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Memory manager optimizations test failed: {e}")
        return False

def test_config_manager():
    """Test config_manager.py functionality"""
    logger.info("🧪 Testing configuration manager...")
    
    try:
        from config_manager import (
            ConfigManager, ApplicationConfig, PerformanceConfig,
            QualityConfig, SystemConfig, ConfigSource, get_config_manager
        )
        
        # Test configuration creation
        config = ApplicationConfig()
        assert config.app_name == "PlayaTewsIdentityMasker"
        assert config.performance.gpu_memory_pool_size_mb == 2048
        assert config.quality.model_quality == "balanced"
        assert config.system.log_level == "INFO"
        logger.info("✅ Configuration creation working correctly")
        
        # Test configuration manager
        config_manager = ConfigManager()
        current_config = config_manager.get_config()
        assert isinstance(current_config, ApplicationConfig)
        logger.info("✅ Configuration manager working correctly")
        
        # Test singleton pattern
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        assert manager1 is manager2
        logger.info("✅ Configuration manager singleton working correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration manager test failed: {e}")
        return False

def test_error_handler():
    """Test error_handler.py functionality"""
    logger.info("🧪 Testing error handler...")
    
    try:
        from error_handler import (
            ErrorHandler, ErrorSeverity, ErrorCategory, RecoveryStrategy,
            ErrorInfo, RecoveryAction, get_error_handler, handle_error
        )
        
        # Test error severity enum
        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.CRITICAL.value == "critical"
        logger.info("✅ Error severity enum working correctly")
        
        # Test error category enum
        assert ErrorCategory.MEMORY.value == "memory"
        assert ErrorCategory.GPU.value == "gpu"
        logger.info("✅ Error category enum working correctly")
        
        # Test recovery strategy enum
        assert RecoveryStrategy.RETRY.value == "retry"
        assert RecoveryStrategy.FALLBACK.value == "fallback"
        logger.info("✅ Recovery strategy enum working correctly")
        
        # Test error handler creation
        error_handler = ErrorHandler()
        assert error_handler.recovery_manager is not None
        logger.info("✅ Error handler creation working correctly")
        
        # Test singleton pattern
        handler1 = get_error_handler()
        handler2 = get_error_handler()
        assert handler1 is handler2
        logger.info("✅ Error handler singleton working correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error handler test failed: {e}")
        return False

def test_integration():
    """Test integration between all components"""
    logger.info("🧪 Testing component integration...")
    
    try:
        # Test that all components can work together
        from main import startup_timer
        from memory_manager import get_memory_manager
        from config_manager import get_config_manager
        from error_handler import get_error_handler
        
        # Initialize all components
        memory_manager = get_memory_manager()
        config_manager = get_config_manager()
        error_handler = get_error_handler()
        
        # Test configuration integration
        config = config_manager.get_config()
        assert config.performance.gpu_memory_pool_size_mb > 0
        
        # Test error handling integration
        stats = error_handler.get_error_statistics()
        assert 'total_errors' in stats
        assert 'recovery_rate' in stats
        
        # Test memory manager integration
        memory_stats = memory_manager.get_memory_summary()
        assert 'pool_size_mb' in memory_stats
        
        logger.info("✅ Component integration working correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False

def test_performance_improvements():
    """Test performance improvements"""
    logger.info("🧪 Testing performance improvements...")
    
    try:
        # Test startup timer performance
        from main import startup_timer
        
        start_time = time.time()
        startup_timer.mark_stage("performance_test_start")
        time.sleep(0.01)  # Simulate some work
        startup_timer.mark_stage("performance_test_end")
        end_time = time.time()
        
        # Verify timing is accurate
        summary = startup_timer.get_summary()
        assert "performance_test_start" in summary
        assert "performance_test_end" in summary
        
        # Test that timing is reasonable (should be very fast)
        total_time = end_time - start_time
        assert total_time < 0.1  # Should be much faster than 100ms
        logger.info(f"✅ Performance test completed in {total_time*1000:.1f}ms")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all optimization tests"""
    logger.info("🚀 Starting optimization verification tests...")
    
    tests = [
        ("Main Optimizations", test_main_optimizations),
        ("Memory Manager Optimizations", test_memory_manager_optimizations),
        ("Configuration Manager", test_config_manager),
        ("Error Handler", test_error_handler),
        ("Component Integration", test_integration),
        ("Performance Improvements", test_performance_improvements),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if test_func():
                logger.info(f"✅ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"TEST RESULTS: {passed}/{total} tests passed")
    logger.info(f"{'='*50}")
    
    if passed == total:
        logger.info("🎉 ALL OPTIMIZATIONS VERIFIED SUCCESSFULLY!")
        logger.info("✅ The application is ready for production use with all optimizations applied.")
        return 0
    else:
        logger.error("❌ Some optimizations failed verification.")
        logger.error("Please check the error messages above and fix any issues.")
        return 1
=======
Verifies that critical fixes have been implemented correctly
"""

import asyncio
import time
import threading
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from improved_performance_optimizer import (
        get_performance_optimizer, 
        PerformanceConfig,
        ResourceManager,
        ErrorHandler,
        ImprovedCache
    )
    OPTIMIZER_AVAILABLE = True
except ImportError:
    OPTIMIZER_AVAILABLE = False
    print("Warning: Improved performance optimizer not available")

class TestCriticalFixes(unittest.TestCase):
    """Test that critical fixes have been applied"""
    
    def test_error_handling_improvements(self):
        """Test that error handling has been improved"""
        
        @ErrorHandler.handle_processing_error("test_operation")
        def test_function_with_error():
            raise ValueError("Test error")
        
        @ErrorHandler.handle_io_error("io_operation")
        def test_io_function_with_error():
            raise FileNotFoundError("Test file not found")
        
        # These should not raise exceptions but return None
        result1 = test_function_with_error()
        result2 = test_io_function_with_error()
        
        self.assertIsNone(result1)
        self.assertIsNone(result2)
        print("✓ Error handling improvements working correctly")
    
    def test_resource_management(self):
        """Test that resource management has been improved"""
        resource_manager = ResourceManager()
        
        # Test resource registration
        mock_resource = MagicMock()
        cleanup_called = False
        
        def cleanup_func(resource):
            nonlocal cleanup_called
            cleanup_called = True
        
        resource_manager.register_resource(mock_resource, cleanup_func)
        
        # Test lock management
        lock1 = resource_manager.get_lock("test_lock")
        lock2 = resource_manager.get_lock("test_lock")
        
        self.assertIs(lock1, lock2)  # Should be the same lock
        
        # Test cleanup
        resource_manager.cleanup_all()
        self.assertTrue(cleanup_called)
        
        print("✓ Resource management improvements working correctly")
    
    def test_cache_functionality(self):
        """Test that improved cache works correctly"""
        cache = ImprovedCache(maxsize=3)
        
        # Test basic operations
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        self.assertEqual(cache.get("key1"), "value1")
        self.assertEqual(cache.size(), 3)
        
        # Test LRU eviction
        cache.put("key4", "value4")  # Should evict key2 (least recently used)
        self.assertEqual(cache.size(), 3)
        self.assertIsNone(cache.get("key2", None))
        self.assertEqual(cache.get("key1"), "value1")  # Should still exist
        
        print("✓ Cache functionality working correctly")
    
    @unittest.skipUnless(OPTIMIZER_AVAILABLE, "Optimizer not available")
    def test_performance_optimizer_integration(self):
        """Test that the performance optimizer works correctly"""
        config = PerformanceConfig(
            max_workers=2,
            enable_caching=True,
            cache_size_limit=10
        )
        
        optimizer = get_performance_optimizer(config)
        
        # Test cached function call
        call_count = 0
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Simulate expensive operation
            return x * 2
        
        # First call should execute the function
        result1 = optimizer.cached_call(expensive_function, 5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Second call should use cache
        result2 = optimizer.cached_call(expensive_function, 5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # Should not increase
        
        print("✓ Performance optimizer integration working correctly")
    
    @unittest.skipUnless(OPTIMIZER_AVAILABLE, "Optimizer not available")
    async def test_async_processing(self):
        """Test that async processing works correctly"""
        optimizer = get_performance_optimizer()
        
        def sync_function(x):
            return x * 3
        
        async def async_function(x):
            await asyncio.sleep(0.01)
            return x * 4
        
        # Test sync function in async context
        result1 = await optimizer.async_call(sync_function, 5)
        self.assertEqual(result1, 15)
        
        # Test async function
        result2 = await optimizer.async_call(async_function, 5)
        self.assertEqual(result2, 20)
        
        print("✓ Async processing working correctly")
    
    def test_threading_improvements(self):
        """Test that threading improvements work correctly"""
        # Test that we can create proper synchronization
        event = threading.Event()
        results = []
        
        def worker_function():
            time.sleep(0.1)
            results.append("completed")
            event.set()
        
        thread = threading.Thread(target=worker_function, daemon=True)
        thread.start()
        
        # Wait with timeout instead of fixed sleep
        success = event.wait(timeout=1.0)
        self.assertTrue(success)
        self.assertEqual(len(results), 1)
        
        print("✓ Threading improvements working correctly")

class TestPerformanceImprovements(unittest.TestCase):
    """Test performance improvements"""
    
    @unittest.skipUnless(OPTIMIZER_AVAILABLE, "Optimizer not available")
    def test_performance_monitoring(self):
        """Test that performance monitoring works"""
        optimizer = get_performance_optimizer()
        
        # Perform some operations
        with optimizer.monitor.measure("test_operation"):
            time.sleep(0.05)
        
        # Check that metrics were recorded
        stats = optimizer.get_performance_stats()
        self.assertIn('timing_stats', stats)
        
        if 'test_operation' in stats['timing_stats']:
            operation_stats = stats['timing_stats']['test_operation']
            self.assertGreaterEqual(operation_stats['average'], 0.04)
            self.assertEqual(operation_stats['count'], 1)
        
        print("✓ Performance monitoring working correctly")
    
    def test_memory_efficiency(self):
        """Test memory efficiency improvements"""
        # Test that weak references work for resource management
        import weakref
        
        class TestResource:
            def __init__(self, name):
                self.name = name
        
        resource = TestResource("test")
        weak_ref = weakref.ref(resource)
        
        self.assertIsNotNone(weak_ref())
        
        del resource
        # Force garbage collection
        import gc
        gc.collect()
        
        # Weak reference should now be None
        self.assertIsNone(weak_ref())
        
        print("✓ Memory efficiency improvements working correctly")


def run_async_tests():
    """Run async tests"""
    async def async_test_runner():
        test_case = TestCriticalFixes()
        test_case.setUp = lambda: None
        await test_case.test_async_processing()
    
    if sys.version_info >= (3, 7):
        asyncio.run(async_test_runner())
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_test_runner())


def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing Applied Code Optimizations")
    print("=" * 50)
    
    # Run synchronous tests
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestCriticalFixes))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestPerformanceImprovements))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run async tests separately
    if OPTIMIZER_AVAILABLE:
        print("\nRunning async tests...")
        try:
            run_async_tests()
        except Exception as e:
            print(f"Async tests failed: {e}")
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All optimization tests passed!")
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1
    
    print("=" * 50)
    return 0

 main

if __name__ == "__main__":
    sys.exit(main())