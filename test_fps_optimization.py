#!/usr/bin/env python3
"""
Test script for FPS optimization and video loopback systems
Verifies functionality and integration capabilities
"""

import time
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_fps_optimizer():
    """Test FPS optimization system"""
    print("🧪 Testing FPS Optimization System...")
    
    try:
        from fps_optimizer import (
            FPSOptimizer, OptimizationSettings, OptimizationStrategy, 
            QualityLevel, get_fps_optimizer
        )
        
        # Test basic initialization
        optimizer = get_fps_optimizer()
        assert optimizer is not None, "Failed to get FPS optimizer"
        print("✅ FPS optimizer initialization: PASS")
        
        # Test settings configuration
        settings = OptimizationSettings(
            target_fps=30.0,
            min_fps=15.0,
            max_fps=60.0,
            strategy=OptimizationStrategy.ADAPTIVE,
            quality_level=QualityLevel.MEDIUM,
            auto_optimization=True
        )
        
        optimizer.settings = settings
        assert optimizer.settings.target_fps == 30.0, "Settings not applied correctly"
        print("✅ Settings configuration: PASS")
        
        # Test start/stop
        optimizer.start()
        assert optimizer.running, "Optimizer not started"
        print("✅ Start functionality: PASS")
        
        # Test frame recording
        for i in range(10):
            optimizer.record_frame(time.time(), queue_size=i % 3)
            time.sleep(0.1)
        
        # Test metrics
        metrics = optimizer.get_metrics()
        assert metrics is not None, "No metrics returned"
        print("✅ Frame recording and metrics: PASS")
        
        # Test performance summary
        summary = optimizer.get_performance_summary()
        assert 'current_fps' in summary, "Performance summary missing FPS"
        print("✅ Performance summary: PASS")
        
        # Test strategy changes
        optimizer.set_optimization_strategy(OptimizationStrategy.AGGRESSIVE)
        assert optimizer.settings.strategy == OptimizationStrategy.AGGRESSIVE, "Strategy not changed"
        print("✅ Strategy changes: PASS")
        
        optimizer.stop()
        assert not optimizer.running, "Optimizer not stopped"
        print("✅ Stop functionality: PASS")
        
        print("🎉 FPS Optimization System: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ FPS Optimization System test failed: {e}")
        return False

def test_video_loopback():
    """Test video loopback system"""
    print("\n🧪 Testing Video Loopback System...")
    
    try:
        from video_loopback_system import (
            VideoLoopbackSystem, LoopbackSettings, LoopbackMode,
            LoopbackSource, SourceType, get_loopback_system
        )
        
        # Test basic initialization
        loopback = get_loopback_system()
        assert loopback is not None, "Failed to get loopback system"
        print("✅ Loopback system initialization: PASS")
        
        # Test settings configuration
        settings = LoopbackSettings(
            mode=LoopbackMode.IMMEDIATE,
            detection_timeout=2.0,
            transition_duration=1.0,
            auto_recovery=True,
            recovery_delay=3.0
        )
        
        loopback.settings = settings
        assert loopback.settings.mode == LoopbackMode.IMMEDIATE, "Settings not applied correctly"
        print("✅ Settings configuration: PASS")
        
        # Test start/stop
        loopback.start()
        assert loopback.running, "Loopback system not started"
        print("✅ Start functionality: PASS")
        
        # Test feed heartbeat
        loopback.feed_heartbeat()
        assert loopback.feed_detected, "Feed heartbeat not working"
        print("✅ Feed heartbeat: PASS")
        
        # Test status
        status = loopback.get_status()
        assert 'running' in status, "Status missing running field"
        print("✅ Status reporting: PASS")
        
        # Test loopback activation (simulate feed loss)
        loopback.feed_loss_time = time.time() - 3.0  # Simulate 3 seconds ago
        loopback._detect_feed_loss()  # Force detection
        
        # Wait a moment for loopback to activate
        time.sleep(0.1)
        
        # Test loopback frame
        frame = loopback.get_loopback_frame()
        assert frame is not None, "No loopback frame available"
        print("✅ Loopback frame generation: PASS")
        
        # Test feed recovery
        loopback.feed_heartbeat()
        assert loopback.feed_detected, "Feed recovery not working"
        print("✅ Feed recovery: PASS")
        
        loopback.stop()
        assert not loopback.running, "Loopback system not stopped"
        print("✅ Stop functionality: PASS")
        
        print("🎉 Video Loopback System: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Video Loopback System test failed: {e}")
        return False

def test_integration():
    """Test integration between systems"""
    print("\n🧪 Testing System Integration...")
    
    try:
        from fps_optimizer import get_fps_optimizer
        from video_loopback_system import get_loopback_system
        
        # Initialize both systems
        fps_optimizer = get_fps_optimizer()
        loopback_system = get_loopback_system()
        
        # Start both systems
        fps_optimizer.start()
        loopback_system.start()
        
        # Simulate integrated operation
        for i in range(5):
            # Record frame for FPS optimization
            fps_optimizer.record_frame(time.time(), queue_size=i % 2)
            
            # Signal feed heartbeat
            loopback_system.feed_heartbeat()
            
            # Get metrics from both systems
            fps_metrics = fps_optimizer.get_performance_summary()
            loopback_status = loopback_system.get_status()
            
            assert fps_metrics is not None, "FPS metrics not available"
            assert loopback_status is not None, "Loopback status not available"
            
            time.sleep(0.1)
        
        # Stop both systems
        fps_optimizer.stop()
        loopback_system.stop()
        
        print("✅ System integration: PASS")
        print("🎉 System Integration: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ System Integration test failed: {e}")
        return False

def test_enhanced_stream_output():
    """Test enhanced StreamOutput integration"""
    print("\n🧪 Testing Enhanced StreamOutput Integration...")
    
    try:
        # Test if the enhanced StreamOutput can be imported
        import enhanced_stream_output_integrated
        
        # Check if the main classes are available
        assert hasattr(enhanced_stream_output_integrated, 'EnhancedStreamOutput'), "EnhancedStreamOutput not found"
        assert hasattr(enhanced_stream_output_integrated, 'EnhancedStreamOutputWorker'), "EnhancedStreamOutputWorker not found"
        
        print("✅ Enhanced StreamOutput import: PASS")
        print("✅ Enhanced StreamOutput classes: PASS")
        
        # Test if optimization systems are available
        if hasattr(enhanced_stream_output_integrated, 'OPTIMIZATION_AVAILABLE'):
            print(f"✅ Optimization availability: {enhanced_stream_output_integrated.OPTIMIZATION_AVAILABLE}")
        
        print("🎉 Enhanced StreamOutput Integration: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced StreamOutput Integration test failed: {e}")
        return False

def test_demo_script():
    """Test demo script functionality"""
    print("\n🧪 Testing Demo Script...")
    
    try:
        # Test if demo script can be imported
        import fps_optimization_demo
        
        # Check if main classes are available
        assert hasattr(fps_optimization_demo, 'PerformanceDemo'), "PerformanceDemo not found"
        assert hasattr(fps_optimization_demo, 'run_interactive_demo'), "run_interactive_demo not found"
        assert hasattr(fps_optimization_demo, 'run_benchmark_test'), "run_benchmark_test not found"
        
        print("✅ Demo script import: PASS")
        print("✅ Demo script classes: PASS")
        
        # Test PerformanceDemo initialization
        demo = fps_optimization_demo.PerformanceDemo()
        assert demo is not None, "PerformanceDemo initialization failed"
        print("✅ PerformanceDemo initialization: PASS")
        
        print("🎉 Demo Script: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Demo Script test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting FPS Optimization and Video Loopback System Tests")
    print("=" * 60)
    
    tests = [
        ("FPS Optimizer", test_fps_optimizer),
        ("Video Loopback", test_video_loopback),
        ("System Integration", test_integration),
        ("Enhanced StreamOutput", test_enhanced_stream_output),
        ("Demo Script", test_demo_script)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Systems are ready for use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

def main():
    """Main test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test - just check imports
        print("🔍 Quick Import Test")
        try:
            import fps_optimizer
            import video_loopback_system
            import enhanced_stream_output_integrated
            import fps_optimization_demo
            print("✅ All modules imported successfully")
            return True
        except ImportError as e:
            print(f"❌ Import failed: {e}")
            return False
    else:
        # Full test suite
        return run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)