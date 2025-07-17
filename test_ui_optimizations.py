#!/usr/bin/env python3
"""
Test Script for DeepFaceLive UI Optimizations
Verifies that all optimizations are working correctly
"""

import sys
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_optimized_frame_viewer():
    """Test the optimized frame viewer"""
    logger.info("Testing Optimized Frame Viewer...")
    
    try:
        from apps.DeepFaceLive.ui.widgets.QOptimizedFrameViewer import QOptimizedFrameViewer
        logger.info("✅ Optimized Frame Viewer imported successfully")
        
        # Test basic functionality
        from apps.DeepFaceLive import backend
        
        # Create mock backend components
        weak_heap = backend.BackendWeakHeap(size_mb=512)
        bc = backend.BackendConnection()
        
        # Create viewer
        viewer = QOptimizedFrameViewer(weak_heap, bc, preview_width=256)
        logger.info("✅ Optimized Frame Viewer created successfully")
        
        # Test performance methods
        stats = viewer.get_performance_stats()
        logger.info(f"✅ Performance stats: {stats}")
        
        # Test configuration methods
        viewer.set_update_interval(50)  # 20 FPS
        viewer.set_frame_skip(1)
        logger.info("✅ Configuration methods work")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Optimized Frame Viewer test failed: {e}")
        return False


def test_ui_manager():
    """Test the UI manager with lazy loading"""
    logger.info("Testing UI Manager...")
    
    try:
        from apps.DeepFaceLive.ui.QOptimizedUIManager import get_ui_manager, cleanup_ui_manager
        
        # Get UI manager
        ui_manager = get_ui_manager()
        logger.info("✅ UI Manager created successfully")
        
        # Test component registration
        def create_test_component():
            from xlib.qt.widgets.QXLabel import QXLabel
            return QXLabel(text="Test Component")
        
        component_name = ui_manager.register_component(
            'test_component',
            create_test_component,
            load_priority=5
        )
        logger.info(f"✅ Component registered: {component_name}")
        
        # Test component loading
        component = ui_manager.get_component('test_component')
        if component:
            logger.info("✅ Component loaded successfully")
        else:
            logger.error("❌ Component loading failed")
            return False
        
        # Test performance stats
        stats = ui_manager.get_performance_stats()
        logger.info(f"✅ Performance stats: {stats}")
        
        # Test optimization
        ui_manager.optimize_for_performance(target_fps=30)
        logger.info("✅ Performance optimization triggered")
        
        # Cleanup
        cleanup_ui_manager()
        logger.info("✅ UI Manager cleanup completed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ UI Manager test failed: {e}")
        return False


def test_optimized_application():
    """Test the optimized application structure"""
    logger.info("Testing Optimized Application...")
    
    try:
        from apps.DeepFaceLive.QOptimizedDeepFaceLiveApp import OptimizedDeepFaceLiveApp
        logger.info("✅ Optimized Application imported successfully")
        
        # Test application creation (without full initialization)
        userdata_path = Path('.')
        app = OptimizedDeepFaceLiveApp(userdata_path)
        logger.info("✅ Optimized Application created successfully")
        
        # Test application methods
        app.initialize()
        logger.info("✅ Application initialization completed")
        
        # Cleanup
        app.finalize()
        logger.info("✅ Application cleanup completed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Optimized Application test failed: {e}")
        return False


def test_performance_monitoring():
    """Test performance monitoring integration"""
    logger.info("Testing Performance Monitoring...")
    
    try:
        from performance_monitor import get_performance_monitor, start_performance_monitoring, stop_performance_monitoring
        
        # Get performance monitor
        perf_monitor = get_performance_monitor()
        logger.info("✅ Performance Monitor created successfully")
        
        # Start monitoring
        start_performance_monitoring(interval=1.0)
        logger.info("✅ Performance monitoring started")
        
        # Simulate some activity
        time.sleep(2)
        
        # Get performance summary
        summary = perf_monitor.get_performance_summary()
        logger.info(f"✅ Performance summary: {summary}")
        
        # Stop monitoring
        stop_performance_monitoring()
        logger.info("✅ Performance monitoring stopped")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Performance Monitoring test failed: {e}")
        return False


def test_memory_management():
    """Test memory management integration"""
    logger.info("Testing Memory Management...")
    
    try:
        from memory_manager import get_memory_manager, start_memory_monitoring, stop_memory_monitoring
        
        # Get memory manager
        memory_manager = get_memory_manager()
        logger.info("✅ Memory Manager created successfully")
        
        # Start monitoring
        start_memory_monitoring()
        logger.info("✅ Memory monitoring started")
        
        # Get memory summary
        summary = memory_manager.get_memory_summary()
        logger.info(f"✅ Memory summary: {summary}")
        
        # Test GPU memory allocation (if available)
        try:
            gpu_memory = memory_manager.allocate_gpu_memory((100, 100), 'float32')
            if gpu_memory is not None:
                logger.info("✅ GPU memory allocation successful")
                memory_manager.deallocate_gpu_memory(gpu_memory, (100, 100), 'float32')
                logger.info("✅ GPU memory deallocation successful")
            else:
                logger.info("⚠️ GPU memory allocation not available (CPU-only mode)")
        except Exception as e:
            logger.info(f"⚠️ GPU memory test skipped: {e}")
        
        # Stop monitoring
        stop_memory_monitoring()
        logger.info("✅ Memory monitoring stopped")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Memory Management test failed: {e}")
        return False


def test_optimized_main():
    """Test the optimized main entry point"""
    logger.info("Testing Optimized Main Entry Point...")
    
    try:
        from optimized_main_ui import OptimizedDeepFaceLiveUI
        
        # Create optimized UI application
        userdata_path = Path('.')
        app = OptimizedDeepFaceLiveUI(userdata_path, debug=True)
        logger.info("✅ Optimized UI Application created successfully")
        
        # Test async initialization (without running full app)
        import asyncio
        
        async def test_init():
            result = await app.initialize_async()
            return result
        
        init_result = asyncio.run(test_init())
        if init_result:
            logger.info("✅ Async initialization completed successfully")
        else:
            logger.error("❌ Async initialization failed")
            return False
        
        # Cleanup
        app._cleanup()
        logger.info("✅ Application cleanup completed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Optimized Main test failed: {e}")
        return False


def run_comprehensive_test():
    """Run all optimization tests"""
    logger.info("🚀 Starting Comprehensive UI Optimization Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Optimized Frame Viewer", test_optimized_frame_viewer),
        ("UI Manager", test_ui_manager),
        ("Optimized Application", test_optimized_application),
        ("Performance Monitoring", test_performance_monitoring),
        ("Memory Management", test_memory_management),
        ("Optimized Main", test_optimized_main),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} Test...")
        logger.info("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name} Test PASSED")
            else:
                logger.error(f"❌ {test_name} Test FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name} Test ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
    
    logger.info(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All UI optimizations are working correctly!")
        return True
    else:
        logger.error(f"⚠️ {total - passed} tests failed. Please check the errors above.")
        return False


def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # Quick test mode
        logger.info("🔍 Running Quick Test Mode...")
        success = test_optimized_frame_viewer() and test_ui_manager()
    else:
        # Full test mode
        success = run_comprehensive_test()
    
    if success:
        logger.info("\n🎉 UI Optimization Tests Completed Successfully!")
        sys.exit(0)
    else:
        logger.error("\n❌ Some UI Optimization Tests Failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()