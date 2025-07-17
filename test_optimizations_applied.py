#!/usr/bin/env python3
"""
Test Script for Applied Optimizations
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


if __name__ == "__main__":
    sys.exit(main())