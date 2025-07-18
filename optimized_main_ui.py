#!/usr/bin/env python3
"""
Optimized DeepFaceLive Main Entry Point
Features: UI optimizations, performance monitoring, lazy loading
"""

import sys
import asyncio
import argparse
import logging
import time
import os
from pathlib import Path
from typing import Optional

# Import optimization modules
from performance_monitor import get_performance_monitor, start_performance_monitoring, stop_performance_monitoring
from memory_manager import get_memory_manager, start_memory_monitoring, stop_memory_monitoring
from async_processor import AsyncVideoProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('playatewsidentitymasker_optimized_ui.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class OptimizedPlayaTewsIdentityMaskerUI:
    """Optimized DeepFaceLive UI application with performance enhancements"""
    
    def __init__(self, userdata_path: Path, no_cuda: bool = False, debug: bool = False):
        self.userdata_path = userdata_path
        self.no_cuda = no_cuda
        self.debug = debug
        self.app = None
        self.initialized = False
        
        # Performance monitoring
        self.perf_monitor = get_performance_monitor()
        self.memory_manager = get_memory_manager()
        
        # Set log level
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
        
        logger.info(f"Initializing OptimizedDeepFaceLive UI with userdata: {userdata_path}")
    
    async def initialize_async(self):
        """Asynchronous initialization with progress tracking"""
        if self.initialized:
            return True
        
        logger.info("Starting optimized UI initialization...")
        init_start_time = time.time()
        
        try:
            # Start monitoring systems
            start_performance_monitoring()
            start_memory_monitoring()
            
            # Initialize modules in parallel
            init_tasks = [
                self._init_gpu_detection(),
                self._init_ui_components(),
                self._init_performance_optimizations()
            ]
            
            results = await asyncio.gather(*init_tasks, return_exceptions=True)
            
            # Check for initialization errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Initialization task {i} failed: {result}")
                    return False
            
            # Mark startup complete
            self.perf_monitor.mark_startup_complete()
            self.initialized = True
            
            init_time = time.time() - init_start_time
            logger.info(f"Optimized UI initialization completed in {init_time:.2f} seconds")
            
            return True
            
        except Exception as e:
            logger.error(f"UI initialization failed: {e}")
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
        
        return gpu_info
    
    async def _init_ui_components(self):
        """Initialize UI components with lazy loading"""
        logger.info("Setting up UI component system...")
        
        # Import the optimized application
        try:
            from apps.PlayaTewsIdentityMasker.QOptimizedPlayaTewsIdentityMaskerApp import OptimizedPlayaTewsIdentityMaskerApp
            self.OptimizedPlayaTewsIdentityMaskerApp = OptimizedPlayaTewsIdentityMaskerApp
            logger.info("Optimized UI components ready")
            return {'ui_components_ready': True}
        except ImportError as e:
            logger.error(f"Failed to import optimized UI components: {e}")
            return {'ui_components_ready': False}
    
    async def _init_performance_optimizations(self):
        """Initialize performance optimization systems"""
        logger.info("Setting up performance optimizations...")
        
        # Configure memory management based on system capabilities
        memory_summary = self.memory_manager.get_memory_summary()
        
        # Adjust settings based on available memory
        if memory_summary['gpu_memory_total_mb'] > 6000:  # 6GB+
            max_loaded_components = 12
            gpu_pool_size_mb = 2048
        elif memory_summary['gpu_memory_total_mb'] > 4000:  # 4GB+
            max_loaded_components = 8
            gpu_pool_size_mb = 1024
        else:
            max_loaded_components = 6
            gpu_pool_size_mb = 512
        
        logger.info(f"Performance optimization configured: {max_loaded_components} max components, {gpu_pool_size_mb}MB GPU pool")
        
        return {
            'performance_optimized': True,
            'max_loaded_components': max_loaded_components,
            'gpu_pool_size_mb': gpu_pool_size_mb
        }
    
    def run(self):
        """Run the optimized UI application"""
        logger.info("Starting OptimizedDeepFaceLive UI...")
        
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
        
        # Create and run the optimized application
        try:
            self.app = self.OptimizedDeepFaceLiveApp(self.userdata_path)
            self.app.initialize()
            
            # Keep the application running
            logger.info("Optimized DeepFaceLive UI is running...")
            
            # Run the Qt event loop
            from PyQt5.QtWidgets import QApplication
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            # Start the application
            sys.exit(app.exec())
            
        except Exception as e:
            logger.error(f"Failed to start optimized application: {e}")
    
    def _cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up optimized UI application...")
        
        try:
            # Stop monitoring
            stop_performance_monitoring()
            stop_memory_monitoring()
            
            # Finalize application
            if self.app:
                self.app.finalize()
            
            # Export final performance metrics
            if self.perf_monitor:
                self.perf_monitor.export_metrics('final_performance_metrics.json')
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Optimized DeepFaceLive UI Application')
    parser.add_argument('--userdata-dir', type=str, default='.',
                       help='User data directory (default: current directory)')
    parser.add_argument('--no-cuda', action='store_true',
                       help='Disable CUDA/GPU acceleration')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    parser.add_argument('--performance-test', type=int, metavar='DURATION',
                       help='Run performance test for specified duration (seconds)')
    parser.add_argument('--benchmark', type=str, metavar='OUTPUT_FILE',
                       help='Run benchmark and save results to file')
    
    args = parser.parse_args()
    
    # Convert userdata directory to Path
    userdata_path = Path(args.userdata_dir).resolve()
    userdata_path.mkdir(parents=True, exist_ok=True)
    
    # Handle special modes
    if args.performance_test:
        run_performance_test(args.performance_test)
        return
    
    if args.benchmark:
        run_benchmark(Path(args.benchmark))
        return
    
    # Create and run optimized application
    app = OptimizedDeepFaceLiveUI(
        userdata_path=userdata_path,
        no_cuda=args.no_cuda,
        debug=args.debug
    )
    
    app.run()


def run_performance_test(duration: int):
    """Run performance test for specified duration"""
    logger.info(f"Running performance test for {duration} seconds...")
    
    async def test():
        app = OptimizedDeepFaceLiveUI(Path('.'))
        await app.initialize_async()
        
        start_time = time.time()
        while time.time() - start_time < duration:
            # Simulate some processing
            await asyncio.sleep(0.1)
            
            # Log performance metrics
            if int(time.time() - start_time) % 5 == 0:
                perf_stats = app.perf_monitor.get_performance_summary()
                logger.info(f"Performance: {perf_stats}")
        
        app._cleanup()
    
    asyncio.run(test())
    logger.info("Performance test completed")


def run_benchmark(output_file: Path):
    """Run comprehensive benchmark"""
    logger.info(f"Running benchmark, results will be saved to {output_file}")
    
    async def benchmark():
        app = OptimizedDeepFaceLiveUI(Path('.'))
        
        # Measure initialization time
        init_start = time.time()
        await app.initialize_async()
        init_time = time.time() - init_start
        
        # Measure memory usage
        memory_stats = app.memory_manager.get_memory_summary()
        
        # Measure performance metrics
        perf_stats = app.perf_monitor.get_performance_summary()
        
        # Compile results
        results = {
            'initialization_time_seconds': init_time,
            'memory_usage': memory_stats,
            'performance_metrics': perf_stats,
            'timestamp': time.time(),
            'system_info': {
                'python_version': sys.version,
                'platform': sys.platform
            }
        }
        
        # Save results
        import json
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        app._cleanup()
        logger.info(f"Benchmark completed, results saved to {output_file}")
    
    asyncio.run(benchmark())


if __name__ == '__main__':
    main()