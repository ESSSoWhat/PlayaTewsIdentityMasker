#!/usr/bin/env python3
"""
Demonstration Script for Enhanced PlayaTewsIdentityMasker Optimizations
Shows how to use the new integrated optimization system
"""

import time
import logging
import asyncio
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demo_basic_optimization():
    """Demonstrate basic optimization setup"""
    print("=" * 60)
    print("DEMO: Basic Optimization Setup")
    print("=" * 60)
    
    try:
        from integrated_optimizer import optimize_for_performance, optimize_for_quality
        
        # Performance mode
        print("\n1. Setting up PERFORMANCE mode...")
        perf_optimizer = optimize_for_performance()
        
        # Get metrics
        metrics = perf_optimizer.get_metrics()
        config = perf_optimizer.get_config()
        
        print(f"   ✓ System profile: {config.system_profile.value}")
        print(f"   ✓ Optimization level: {config.optimization_level.value}")
        print(f"   ✓ Processing mode: {config.processing_mode.value}")
        print(f"   ✓ Target FPS: {config.target_processing_fps}")
        print(f"   ✓ Workers: {config.processing_workers}")
        
        # Quality mode
        print("\n2. Setting up QUALITY mode...")
        qual_optimizer = optimize_for_quality()
        
        config = qual_optimizer.get_config()
        print(f"   ✓ Optimization level: {config.optimization_level.value}")
        print(f"   ✓ Processing mode: {config.processing_mode.value}")
        print(f"   ✓ Memory compression: {config.memory_compression}")
        print(f"   ✓ Auto-tuning: {config.auto_tuning_enabled}")
        
        print("\n✅ Basic optimization demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Optimization modules not available: {e}")
        print("   Make sure all optimization files are in the same directory")

def demo_custom_configuration():
    """Demonstrate custom optimization configuration"""
    print("\n" + "=" * 60)
    print("DEMO: Custom Configuration")
    print("=" * 60)
    
    try:
        from integrated_optimizer import (
            OptimizationConfig, 
            OptimizationLevel, 
            SystemProfile,
            initialize_optimizations
        )
        from enhanced_async_processor import ProcessingMode, FrameSkipStrategy
        
        # Create custom configuration
        print("\n1. Creating custom configuration...")
        
        custom_config = OptimizationConfig(
            # UI settings
            ui_render_caching=True,
            ui_target_fps=45,
            ui_lazy_loading=True,
            
            # Memory settings
            gpu_memory_pool_size_mb=1024,
            model_cache_size_mb=256,
            memory_compression=True,
            
            # Processing settings
            processing_workers=6,
            processing_mode=ProcessingMode.BALANCED,
            skip_strategy=FrameSkipStrategy.ADAPTIVE,
            target_processing_fps=25.0,
            
            # System settings
            optimization_level=OptimizationLevel.AGGRESSIVE,
            system_profile=SystemProfile.HIGH_END,
            auto_tuning_enabled=True
        )
        
        # Initialize with custom config
        optimizer = initialize_optimizations(custom_config)
        
        print("   ✓ Custom configuration created")
        print(f"   ✓ UI target FPS: {custom_config.ui_target_fps}")
        print(f"   ✓ GPU memory pool: {custom_config.gpu_memory_pool_size_mb} MB")
        print(f"   ✓ Processing workers: {custom_config.processing_workers}")
        print(f"   ✓ System profile: {custom_config.system_profile.value}")
        
        # Save configuration
        config_file = Path("demo_optimization_config.json")
        optimizer.save_config(config_file)
        print(f"   ✓ Configuration saved to {config_file}")
        
        # Load configuration (demo)
        if optimizer.load_config(config_file):
            print(f"   ✓ Configuration loaded from {config_file}")
        
        print("\n✅ Custom configuration demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Optimization modules not available: {e}")

def demo_ui_optimization():
    """Demonstrate UI optimization features"""
    print("\n" + "=" * 60)
    print("DEMO: UI Optimization Features")
    print("=" * 60)
    
    try:
        from ui_optimizer import (
            get_ui_optimizer, 
            optimize_widget_rendering,
            create_optimized_layout,
            enable_lazy_loading
        )
        
        print("\n1. Setting up UI optimizer...")
        ui_optimizer = get_ui_optimizer()
        ui_optimizer.enable_optimizations()
        
        print("   ✓ UI optimizer enabled")
        print("   ✓ Render caching active")
        print("   ✓ Update scheduling active")
        
        # Demonstrate optimized layout
        print("\n2. Creating optimized layouts...")
        v_layout = create_optimized_layout('vertical')
        h_layout = create_optimized_layout('horizontal')
        
        if v_layout and h_layout:
            print("   ✓ Optimized vertical layout created")
            print("   ✓ Optimized horizontal layout created")
        
        # Widget optimization decorator demo
        print("\n3. Widget optimization decorator...")
        
        # This would normally be used with actual Qt widgets
        class MockWidget:
            def __init__(self):
                self.optimization_enabled = True
            
            def paintEvent(self, event):
                pass
        
        @optimize_widget_rendering
        class OptimizedMockWidget(MockWidget):
            pass
        
        widget = OptimizedMockWidget()
        print("   ✓ Widget optimization decorator applied")
        
        print("\n✅ UI optimization demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ UI optimization modules not available: {e}")

def demo_memory_optimization():
    """Demonstrate memory optimization features"""
    print("\n" + "=" * 60)
    print("DEMO: Memory Optimization Features")
    print("=" * 60)
    
    try:
        from enhanced_memory_manager import (
            get_enhanced_memory_manager,
            MemoryPriority
        )
        
        print("\n1. Setting up enhanced memory manager...")
        memory_manager = get_enhanced_memory_manager()
        
        # Get memory statistics
        stats = memory_manager.get_memory_stats()
        
        print("   ✓ Enhanced memory manager initialized")
        print(f"   ✓ GPU pool size: {stats['gpu_pool']['total_size_mb']:.1f} MB")
        print(f"   ✓ Model cache size: {stats['model_cache']['max_size_mb']:.1f} MB")
        print(f"   ✓ System memory: {stats['system']['available_memory_mb']:.1f} MB available")
        
        # Demonstrate memory context
        print("\n2. Memory context manager...")
        with memory_manager.memory_context(MemoryPriority.HIGH):
            print("   ✓ High-priority memory context active")
            # Simulated memory operations would go here
            time.sleep(0.1)
        
        # Optimization modes
        print("\n3. Memory optimization modes...")
        memory_manager.optimize_for_inference()
        print("   ✓ Optimized for inference")
        
        memory_manager.optimize_for_training()
        print("   ✓ Optimized for training")
        
        print("\n✅ Memory optimization demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Memory optimization modules not available: {e}")

async def demo_async_processing():
    """Demonstrate async processing optimization"""
    print("\n" + "=" * 60)
    print("DEMO: Async Processing Optimization")
    print("=" * 60)
    
    try:
        from enhanced_async_processor import (
            get_global_processor,
            ProcessingMode,
            FrameSkipStrategy,
            optimize_for_realtime,
            optimize_for_quality
        )
        import numpy as np
        
        print("\n1. Setting up enhanced async processor...")
        processor = get_global_processor()
        
        # Configure for demo
        processor.set_processing_mode(ProcessingMode.BALANCED)
        processor.set_skip_strategy(FrameSkipStrategy.ADAPTIVE)
        processor.set_target_fps(30.0)
        
        print("   ✓ Async processor configured")
        print(f"   ✓ Processing mode: {processor.processing_mode.value}")
        print(f"   ✓ Skip strategy: {processor.skip_strategy.value}")
        print(f"   ✓ Target FPS: {processor.target_fps}")
        
        # Add a simple processor function
        def simple_processor(frame, metadata):
            # Simulate processing
            return frame
        
        processor.add_processor(simple_processor)
        
        # Start processing
        await processor.start()
        print("   ✓ Async processor started")
        
        # Process some demo frames
        print("\n2. Processing demo frames...")
        for i in range(10):
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            success = await processor.process_frame(frame, {'frame_id': i})
            if success:
                print(f"   ✓ Frame {i} queued for processing")
        
        # Get some processed frames
        processed_count = 0
        for _ in range(5):
            result = await processor.get_processed_frame(timeout=1.0)
            if result:
                processed_count += 1
        
        print(f"   ✓ Retrieved {processed_count} processed frames")
        
        # Get statistics
        stats = processor.get_stats()
        quality_info = processor.get_quality_info()
        
        print(f"\n3. Processing statistics:")
        print(f"   ✓ Frames processed: {stats.frames_processed}")
        print(f"   ✓ Frames dropped: {stats.frames_dropped}")
        print(f"   ✓ Effective FPS: {stats.effective_fps:.1f}")
        print(f"   ✓ Current quality: {quality_info['current_quality']:.2f}")
        
        # Cleanup
        await processor.stop()
        print("   ✓ Async processor stopped")
        
        print("\n✅ Async processing demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Async processing modules not available: {e}")

def demo_performance_monitoring():
    """Demonstrate performance monitoring"""
    print("\n" + "=" * 60)
    print("DEMO: Performance Monitoring")
    print("=" * 60)
    
    try:
        from integrated_optimizer import get_integrated_optimizer
        
        print("\n1. Getting performance metrics...")
        optimizer = get_integrated_optimizer()
        
        if hasattr(optimizer, 'metrics'):
            metrics = optimizer.get_metrics()
            
            print("   Current Performance Metrics:")
            print(f"   ✓ Startup time: {metrics.startup_time:.2f}s")
            print(f"   ✓ Average frame time: {metrics.avg_frame_time:.2f}ms")
            print(f"   ✓ Processing FPS: {metrics.processing_fps:.1f}")
            print(f"   ✓ Memory usage: {metrics.memory_usage_mb:.1f} MB")
            print(f"   ✓ Frame drops: {metrics.frame_drops}")
            print(f"   ✓ Cache hit rate: {metrics.cache_hit_rate:.2%}")
        
        # Auto-tuning demo
        print("\n2. Auto-tuning system...")
        if hasattr(optimizer, 'auto_tuner'):
            tuner = optimizer.auto_tuner
            print(f"   ✓ Auto-tuning enabled: {tuner.tuning_enabled}")
            print(f"   ✓ Target FPS: {tuner.target_fps}")
            print(f"   ✓ Metrics history: {len(tuner.metrics_history)} entries")
        
        print("\n✅ Performance monitoring demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Performance monitoring modules not available: {e}")

def main():
    """Run all optimization demos"""
    print("🚀 PlayaTewsIdentityMasker Enhanced Optimization System Demo")
    print("This demo showcases the new optimization features")
    
    # Run demos
    demo_basic_optimization()
    demo_custom_configuration()
    demo_ui_optimization()
    demo_memory_optimization()
    
    # Run async demo
    try:
        asyncio.run(demo_async_processing())
    except Exception as e:
        print(f"❌ Async processing demo failed: {e}")
    
    demo_performance_monitoring()
    
    print("\n" + "=" * 60)
    print("🎉 ALL DEMOS COMPLETED!")
    print("=" * 60)
    print("\nTo use these optimizations in your application:")
    print("1. Import the optimization modules")
    print("2. Choose an optimization mode (performance/quality/balanced)")
    print("3. Initialize the integrated optimizer")
    print("4. Let the auto-tuning system optimize performance automatically")
    print("\nExample usage:")
    print("  python optimized_main.py run PlayaTewsIdentityMasker --optimization-mode performance")
    print("  python optimized_main.py run PlayaTewsIdentityMasker --optimization-mode quality")
    print("  python optimized_main.py run PlayaTewsIdentityMasker --optimization-mode balanced")

if __name__ == '__main__':
    main()