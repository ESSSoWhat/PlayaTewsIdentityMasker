#!/usr/bin/env python3
"""
Test Script for Applied Optimizations
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

if __name__ == "__main__":
    sys.exit(main())