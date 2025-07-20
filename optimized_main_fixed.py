
#!/usr/bin/env python3
"""
Optimized Main Entry Point for DeepFaceLive
Includes all fixes and optimizations
"""

import sys
import asyncio
import argparse
import logging
import time
from pathlib import Path
from typing import Optional

# Import our fixed optimization modules
try:
    from enhanced_memory_manager_fixed import get_memory_manager, start_memory_monitoring
    from performance_optimizer_fixed import get_performance_optimizer, start_performance_monitoring
    OPTIMIZATION_AVAILABLE = True
except ImportError:
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

class OptimizedDeepFaceLiveApp:
    """Optimized DeepFaceLive application with all fixes applied"""
    
    def __init__(self, userdata_path: Path, no_cuda: bool = False, optimization_mode: str = "balanced"):
        self.userdata_path = userdata_path
        self.no_cuda = no_cuda
        self.optimization_mode = optimization_mode
        self.initialized = False
        
        # Initialize optimization systems
        if OPTIMIZATION_AVAILABLE:
            self.memory_manager = get_memory_manager()
            self.performance_optimizer = get_performance_optimizer()
        
        logger.info(f"🚀 Initializing OptimizedDeepFaceLiveApp with userdata: {userdata_path}")
        logger.info(f"Optimization mode: {optimization_mode}")
    
    async def initialize_async(self):
        """Enhanced asynchronous initialization"""
        if self.initialized:
            return True
        
        logger.info("Starting optimized initialization...")
        init_start_time = time.time()
        
        try:
            # Start optimization systems
            if OPTIMIZATION_AVAILABLE:
                start_memory_monitoring()
                start_performance_monitoring()
                logger.info("✅ Optimization systems started")
            
            # Initialize modules in parallel
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
            
            self.initialized = True
            init_time = time.time() - init_start_time
            
            logger.info(f"✅ Optimized initialization completed in {init_time:.2f} seconds")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def _init_gpu_detection(self):
        """Detect and initialize GPU resources"""
        logger.info("Detecting GPU capabilities...")
        
        if self.no_cuda:
            logger.info("CUDA disabled by user")
            return {'gpu_available': False, 'provider': 'cpu'}
        
        gpu_info = {'gpu_available': False, 'provider': 'cpu'}
        
        try:
            # Try ONNX Runtime first
            import onnxruntime as ort
            providers = ort.get_available_providers()
            if 'CUDAExecutionProvider' in providers:
                gpu_info['gpu_available'] = True
                gpu_info['provider'] = 'onnx-gpu'
                logger.info("✅ ONNX Runtime GPU provider available")
            else:
                logger.info("ONNX Runtime GPU provider not available")
        except ImportError:
            logger.warning("ONNX Runtime not available")
        
        return gpu_info
    
    async def _init_models_lazy(self):
        """Lazy load models"""
        logger.info("Initializing models (lazy loading)...")
        
        # Check for modelhub availability
        try:
            import modelhub.onnx
            available_models = dir(modelhub.onnx)
            logger.info(f"Available models: {available_models}")
            
            # Check for InsightFaceSwap specifically
            if 'InsightFaceSwap' in available_models:
                logger.info("✅ InsightFaceSwap model available")
            else:
                logger.warning("❌ InsightFaceSwap model not available")
                
        except ImportError as e:
            logger.error(f"❌ Cannot import modelhub: {e}")
        
        return True
    
    async def _init_video_processing(self):
        """Initialize video processing"""
        logger.info("Initializing video processing...")
        
        # Apply performance optimizations based on mode
        if OPTIMIZATION_AVAILABLE:
            if self.optimization_mode == "performance":
                self.performance_optimizer.optimize_for_performance()
            elif self.optimization_mode == "quality":
                self.performance_optimizer.optimize_for_quality()
        
        return True
    
    async def _init_gui_components(self):
        """Initialize GUI components"""
        logger.info("Initializing GUI components...")
        
        # Load localization
        try:
            from localization import load_localization
            load_localization()
            logger.info("✅ Localization loaded")
        except Exception as e:
            logger.warning(f"Localization loading failed: {e}")
        
        return True
    
    def run(self):
        """Run the optimized application"""
        try:
            # Run async initialization
            asyncio.run(self.initialize_async())
            
            if self.initialized:
                logger.info("🚀 Starting optimized DeepFaceLive application...")
                
                # Start the main application loop
                self._run_main_loop()
            else:
                logger.error("❌ Failed to initialize application")
                return False
                
        except KeyboardInterrupt:
            logger.info("🛑 Application interrupted by user")
        except Exception as e:
            logger.error(f"❌ Application error: {e}")
            return False
        finally:
            self._cleanup()
        
        return True
    
    def _run_main_loop(self):
        """Run the main application loop"""
        logger.info("🔄 Starting main application loop...")
        
        # Simulate main loop for demonstration
        try:
            while True:
                # Get performance metrics
                if OPTIMIZATION_AVAILABLE:
                    perf_metrics = self.performance_optimizer.get_performance_metrics()
                    memory_metrics = self.memory_manager.get_memory_usage()
                    
                    # Log performance every 10 seconds
                    if int(time.time()) % 10 == 0:
                        logger.info(f"Performance: {perf_metrics['current_fps']:.1f} FPS, "
                                  f"Memory: {memory_metrics['percent']:.1f}%")
                
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            logger.info("🛑 Main loop interrupted")
    
    def _cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up resources...")
        
        if OPTIMIZATION_AVAILABLE:
            self.memory_manager.stop_monitoring()
            self.performance_optimizer.stop_monitoring()
        
        logger.info("✅ Cleanup completed")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Optimized DeepFaceLive Application")
    parser.add_argument('--userdata-dir', type=Path, default=Path.cwd(), help="User data directory")
    parser.add_argument('--no-cuda', action='store_true', help="Disable CUDA")
    parser.add_argument('--optimization-mode', choices=['performance', 'quality', 'balanced'], 
                       default='balanced', help="Optimization mode")
    parser.add_argument('--debug', action='store_true', help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run optimized application
    app = OptimizedDeepFaceLiveApp(
        userdata_path=args.userdata_dir,
        no_cuda=args.no_cuda,
        optimization_mode=args.optimization_mode
    )
    
    return app.run()

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
