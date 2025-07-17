#!/usr/bin/env python3
"""
Enhanced Optimized PlayaTewsIdentityMasker Application Entry Point
Features: Integrated optimization system, auto-tuning, advanced performance management
"""

import sys
import asyncio
import argparse
import logging
import time
from pathlib import Path
from typing import Optional

# Import comprehensive optimization system
try:
    from integrated_optimizer import (
        get_integrated_optimizer, 
        optimize_for_performance, 
        optimize_for_quality,
        OptimizationConfig,
        OptimizationLevel,
        SystemProfile
    )
    from enhanced_memory_manager import MemoryPriority
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    # Fallback to original optimization modules
    from performance_monitor import get_performance_monitor, start_performance_monitoring
    from memory_manager import get_memory_manager, start_memory_monitoring
    from async_processor import AsyncVideoProcessor
    OPTIMIZATION_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deepfacelive_optimized.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class OptimizedPlayaTewsIdentityMaskerApp:
    """Enhanced optimized PlayaTewsIdentityMasker application with integrated optimization system"""
    
    def __init__(self, userdata_path: Path, no_cuda: bool = False, optimization_mode: str = "balanced"):
        self.userdata_path = userdata_path
        self.no_cuda = no_cuda
        self.optimization_mode = optimization_mode
        self.app_modules = {}
        self.initialized = False
        
        # Initialize integrated optimization system
        if OPTIMIZATION_AVAILABLE:
            self.optimizer = get_integrated_optimizer()
            self._setup_optimization_config()
        else:
            # Fallback to original optimization modules
            self.perf_monitor = get_performance_monitor()
            self.memory_manager = get_memory_manager()
            self.video_processor: Optional[AsyncVideoProcessor] = None
        
        logger.info(f"Initializing Enhanced OptimizedPlayaTewsIdentityMasker with userdata: {userdata_path}")
        logger.info(f"Optimization mode: {optimization_mode}")
    
    def _setup_optimization_config(self):
        """Setup optimization configuration based on mode"""
        if not OPTIMIZATION_AVAILABLE:
            return
            
        if self.optimization_mode == "performance":
            # Maximum performance configuration
            from integrated_optimizer import ProcessingMode, FrameSkipStrategy
            config = OptimizationConfig(
                optimization_level=OptimizationLevel.AGGRESSIVE,
                processing_mode=ProcessingMode.REALTIME,
                skip_strategy=FrameSkipStrategy.ADAPTIVE,
                ui_target_fps=60,
                processing_workers=6,
                frame_buffer_size=5,
                memory_compression=True,
                auto_tuning_enabled=True,
                system_profile=SystemProfile.AUTO
            )
        elif self.optimization_mode == "quality":
            # Maximum quality configuration
            from integrated_optimizer import ProcessingMode, FrameSkipStrategy
            config = OptimizationConfig(
                optimization_level=OptimizationLevel.CONSERVATIVE,
                processing_mode=ProcessingMode.QUALITY,
                skip_strategy=FrameSkipStrategy.NONE,
                ui_target_fps=45,
                processing_workers=4,
                frame_buffer_size=8,
                memory_compression=False,
                auto_tuning_enabled=False,
                system_profile=SystemProfile.AUTO
            )
        else:  # balanced (default)
            # Balanced configuration
            from integrated_optimizer import ProcessingMode, FrameSkipStrategy
            config = OptimizationConfig(
                optimization_level=OptimizationLevel.BALANCED,
                processing_mode=ProcessingMode.BALANCED,
                skip_strategy=FrameSkipStrategy.ADAPTIVE,
                ui_target_fps=60,
                processing_workers=4,
                frame_buffer_size=5,
                memory_compression=True,
                auto_tuning_enabled=True,
                system_profile=SystemProfile.AUTO
            )
        
        self.optimizer.update_config(config)
    
    async def initialize_async(self):
        """Enhanced asynchronous initialization with integrated optimization"""
        if self.initialized:
            return True
        
        logger.info("Starting enhanced optimized initialization...")
        init_start_time = time.time()
        
        try:
            if OPTIMIZATION_AVAILABLE:
                # Initialize integrated optimization system
                self.optimizer.initialize()
                self.optimizer.start_optimization()
                logger.info("Integrated optimization system started")
            else:
                # Fallback to original optimization
                start_performance_monitoring()
                start_memory_monitoring()
            
            # Initialize modules in parallel with optimization
            init_tasks = [
                self._init_gpu_detection(),
                self._init_models_lazy(),
                self._init_video_processing(),
                self._init_gui_components()
            ]
            
            results = await asyncio.gather(*init_tasks, return_exceptions=True)
            
            # Check for initialization errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Initialization task {i} failed: {result}")
                    return False
            
            # Mark startup complete
            if OPTIMIZATION_AVAILABLE:
                pass  # Integrated optimizer handles completion automatically
            else:
                self.perf_monitor.mark_startup_complete()
            
            self.initialized = True
            
            init_time = time.time() - init_start_time
            
            # Enhanced logging with optimization metrics
            if OPTIMIZATION_AVAILABLE:
                metrics = self.optimizer.get_metrics()
                config = self.optimizer.get_config()
                logger.info(f"Enhanced initialization completed in {init_time:.2f} seconds")
                logger.info(f"System profile: {config.system_profile.value}")
                logger.info(f"Optimization level: {config.optimization_level.value}")
                logger.info(f"Processing mode: {config.processing_mode.value}")
            else:
                logger.info(f"Optimized initialization completed in {init_time:.2f} seconds")
            
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    async def _init_gpu_detection(self):
        """Detect and initialize GPU resources"""
        logger.info("Detecting GPU capabilities...")
        
        if self.no_cuda:
            logger.info("CUDA disabled by user")
            return {'gpu_available': False, 'provider': 'cpu'}
        
        # Lazy import to avoid loading heavy libraries during startup
        gpu_info = {'gpu_available': False, 'provider': 'cpu'}
        
        try:
            # Try ONNX Runtime first (lighter)
            import onnxruntime as ort
            providers = ort.get_available_providers()
            if 'CUDAExecutionProvider' in providers:
                gpu_info['gpu_available'] = True
                gpu_info['provider'] = 'onnx-gpu'
                logger.info("ONNX Runtime GPU provider available")
        except ImportError:
            logger.warning("ONNX Runtime not available")
        
        # Fallback to PyTorch if needed
        if not gpu_info['gpu_available']:
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_info['gpu_available'] = True
                    gpu_info['provider'] = 'pytorch-gpu'
                    logger.info("PyTorch GPU provider available")
            except ImportError:
                logger.warning("PyTorch not available")
        
        self.app_modules['gpu_info'] = gpu_info
        return gpu_info
    
    async def _init_models_lazy(self):
        """Initialize model loading system with lazy loading"""
        logger.info("Setting up model caching system...")
        
        # Configure model cache based on available memory
        memory_summary = self.memory_manager.get_memory_summary()
        
        # Adjust cache size based on available GPU memory
        if memory_summary['gpu_memory_total_mb'] > 6000:  # 6GB+
            max_models = 3
        elif memory_summary['gpu_memory_total_mb'] > 4000:  # 4GB+
            max_models = 2
        else:
            max_models = 1
        
        logger.info(f"Configured model cache for {max_models} models")
        self.app_modules['model_cache_size'] = max_models
        
        return {'model_cache_configured': True, 'max_models': max_models}
    
    async def _init_video_processing(self):
        """Initialize asynchronous video processing pipeline"""
        logger.info("Setting up video processing pipeline...")
        
        # Configure based on system capabilities
        gpu_info = self.app_modules.get('gpu_info', {'gpu_available': False})
        
        if gpu_info['gpu_available']:
            buffer_size = 3
            max_workers = 2
        else:
            buffer_size = 2
            max_workers = 1
        
        self.video_processor = AsyncVideoProcessor(
            buffer_size=buffer_size,
            max_workers=max_workers,
            drop_frames=True  # For real-time performance
        )
        
        logger.info(f"Video processor configured: {max_workers} workers, buffer size {buffer_size}")
        return {'video_processor_ready': True}
    
    async def _init_gui_components(self):
        """Initialize GUI components (placeholder for actual implementation)"""
        logger.info("Initializing GUI components...")
        
        # This would initialize the actual PlayaTewsIdentityMasker GUI
        # For now, just simulate the loading time
        await asyncio.sleep(0.5)  # Simulate GUI initialization
        
        return {'gui_initialized': True}
    
    def run(self):
        """Run the optimized application"""
        logger.info("Starting OptimizedPlayaTewsIdentityMasker...")
        
        # Use asyncio for the main application loop
        try:
            asyncio.run(self._run_async())
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            self._cleanup()
    
    async def _run_async(self):
        """Main asynchronous application loop"""
        # Initialize
        if not await self.initialize_async():
            logger.error("Failed to initialize application")
            return
        
        logger.info("Application ready - starting main loop")
        
        # Start video processing if available
        if self.video_processor:
            await self.video_processor.start_processing()
        
        # Main application loop
        try:
            # In a real implementation, this would handle the GUI event loop
            # For now, just run for demonstration
            await self._demo_processing_loop()
            
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
        finally:
            # Cleanup
            if self.video_processor:
                await self.video_processor.stop_processing()
    
    async def _demo_processing_loop(self):
        """Demo processing loop for testing"""
        import numpy as np
        
        logger.info("Running demo processing loop...")
        
        # Simulate video frames
        for i in range(100):
            if not self.video_processor:
                break
            
            # Create dummy frame
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # Process frame
            start_time = time.time()
            processed_frame = await self.video_processor.process_frame_async(frame)
            
            # Record performance
            self.perf_monitor.record_frame_processing(start_time)
            
            if i % 30 == 0:  # Log every 30 frames
                stats = self.video_processor.get_performance_stats()
                perf_summary = self.perf_monitor.get_performance_summary()
                logger.info(f"Frame {i}: FPS={perf_summary['current']['fps']:.1f}, "
                          f"Latency={stats.get('avg_processing_time_ms', 0):.1f}ms")
            
            await asyncio.sleep(0.033)  # ~30 FPS
    
    def _cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        
        # Stop monitoring
        self.perf_monitor.stop_monitoring()
        self.memory_manager.stop_monitoring()
        
        # Force memory cleanup
        self.memory_manager.force_cleanup()
        
        # Export performance metrics
        try:
            self.perf_monitor.export_metrics('performance_report.json')
            logger.info("Performance report exported")
        except Exception as e:
            logger.warning(f"Failed to export performance report: {e}")

def main():
    """Main entry point with optimized argument parsing"""
    parser = argparse.ArgumentParser(description="Optimized PlayaTewsIdentityMasker Application")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command')
    
    # Run command
    run_parser = subparsers.add_parser('run', help="Run the optimized application")
    run_subparsers = run_parser.add_subparsers(dest='app_type')
    
    # PlayaTewsIdentityMasker app
    dfl_parser = run_subparsers.add_parser('PlayaTewsIdentityMasker', help="Run Enhanced PlayaTewsIdentityMasker")
    dfl_parser.add_argument('--userdata-dir', 
                           default='./userdata',
                           type=Path,
                           help="Workspace directory")
    dfl_parser.add_argument('--no-cuda', 
                           action='store_true',
                           help="Disable CUDA acceleration")
    dfl_parser.add_argument('--optimization-mode',
                           choices=['performance', 'quality', 'balanced'],
                           default='balanced',
                           help="Optimization mode: performance (speed), quality (accuracy), balanced (default)")
    dfl_parser.add_argument('--system-profile',
                           choices=['auto', 'low_end', 'medium', 'high_end', 'workstation'],
                           default='auto',
                           help="System profile for optimization (auto-detects by default)")
    dfl_parser.add_argument('--profile', 
                           action='store_true',
                           help="Enable detailed performance profiling")
    dfl_parser.add_argument('--save-config',
                           type=Path,
                           help="Save optimization configuration to file")
    dfl_parser.add_argument('--load-config',
                           type=Path,
                           help="Load optimization configuration from file")
    
    # Performance test command
    test_parser = subparsers.add_parser('test', help="Run performance tests")
    test_parser.add_argument('--duration', 
                            type=int, 
                            default=60,
                            help="Test duration in seconds")
    
    # Benchmark command
    bench_parser = subparsers.add_parser('benchmark', help="Run performance benchmark")
    bench_parser.add_argument('--output', 
                             type=Path,
                             default='benchmark_results.json',
                             help="Output file for benchmark results")
    
    args = parser.parse_args()
    
    if args.command == 'run' and args.app_type == 'PlayaTewsIdentityMasker':
        # Run enhanced optimized PlayaTewsIdentityMasker
        app = OptimizedPlayaTewsIdentityMaskerApp(
            userdata_path=args.userdata_dir,
            no_cuda=args.no_cuda,
            optimization_mode=args.optimization_mode
        )
        
        # Handle configuration loading/saving
        if hasattr(args, 'load_config') and args.load_config and OPTIMIZATION_AVAILABLE:
            if app.optimizer.load_config(args.load_config):
                logger.info(f"Loaded configuration from {args.load_config}")
        
        # Run the application
        app.run()
        
        # Save configuration if requested
        if hasattr(args, 'save_config') and args.save_config and OPTIMIZATION_AVAILABLE:
            app.optimizer.save_config(args.save_config)
            logger.info(f"Saved configuration to {args.save_config}")
        
    elif args.command == 'test':
        # Run performance tests
        run_performance_test(args.duration)
        
    elif args.command == 'benchmark':
        # Run benchmark
        run_benchmark(args.output)
        
    else:
        parser.print_help()

def run_performance_test(duration: int):
    """Run performance test"""
    logger.info(f"Running performance test for {duration} seconds...")
    
    async def test():
        from async_processor import AsyncVideoProcessor
        import numpy as np
        
        processor = AsyncVideoProcessor(buffer_size=3, max_workers=2)
        await processor.start_processing()
        
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            await processor.process_frame_async(frame)
            frame_count += 1
            await asyncio.sleep(0.001)
        
        await processor.stop_processing()
        
        stats = processor.get_performance_stats()
        logger.info(f"Test completed: {frame_count} frames, "
                   f"avg processing time: {stats.get('avg_processing_time_ms', 0):.1f}ms")
    
    asyncio.run(test())

def run_benchmark(output_file: Path):
    """Run comprehensive benchmark"""
    logger.info("Running comprehensive benchmark...")
    
    # Implementation would run various performance tests
    results = {
        'timestamp': time.time(),
        'system_info': {},
        'benchmark_results': {},
        'recommendations': []
    }
    
    # Save results
    import json
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Benchmark results saved to {output_file}")

if __name__ == '__main__':
    main()