#!/usr/bin/env python3
"""
Simple Optimized Main Entry Point for DeepFaceLive
"""

import sys
import asyncio
import argparse
import logging
import time
from pathlib import Path

# Import our simple optimization modules
try:
    from simple_memory_manager import start_memory_monitoring, stop_memory_monitoring
    from simple_performance_optimizer import start_performance_monitoring, stop_performance_monitoring
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deepfacelive_simple_optimized.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SimpleOptimizedDeepFaceLiveApp:
    def __init__(self, userdata_path: Path, no_cuda: bool = False):
        self.userdata_path = userdata_path
        self.no_cuda = no_cuda
        self.initialized = False
        
        logger.info(f"🚀 Initializing SimpleOptimizedDeepFaceLiveApp with userdata: {userdata_path}")
    
    async def initialize_async(self):
        if self.initialized:
            return True
        
        logger.info("Starting simple optimized initialization...")
        init_start_time = time.time()
        
        try:
            # Start optimization systems
            if OPTIMIZATION_AVAILABLE:
                start_memory_monitoring()
                start_performance_monitoring()
                logger.info("✅ Simple optimization systems started")
            
            # Initialize basic components
            await self._init_basic_components()
            
            self.initialized = True
            init_time = time.time() - init_start_time
            
            logger.info(f"✅ Simple optimized initialization completed in {init_time:.2f} seconds")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def _init_basic_components(self):
        """Initialize basic components"""
        logger.info("Initializing basic components...")
        
        # Check for modelhub availability
        try:
            import modelhub.onnx
            available_models = dir(modelhub.onnx)
            logger.info(f"Available models: {available_models}")
            
            if 'InsightFaceSwap' in available_models:
                logger.info("✅ InsightFaceSwap model available")
            else:
                logger.warning("❌ InsightFaceSwap model not available")
                
        except ImportError as e:
            logger.error(f"❌ Cannot import modelhub: {e}")
        
        return True
    
    def run(self):
        """Run the optimized application"""
        try:
            # Run async initialization
            asyncio.run(self.initialize_async())
            
            if self.initialized:
                logger.info("🚀 Starting simple optimized DeepFaceLive application...")
                
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
        
        try:
            while True:
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            logger.info("🛑 Main loop interrupted")
    
    def _cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up resources...")
        
        if OPTIMIZATION_AVAILABLE:
            stop_memory_monitoring()
            stop_performance_monitoring()
        
        logger.info("✅ Cleanup completed")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Simple Optimized DeepFaceLive Application")
    parser.add_argument('--userdata-dir', type=Path, default=Path.cwd(), help="User data directory")
    parser.add_argument('--no-cuda', action='store_true', help="Disable CUDA")
    parser.add_argument('--debug', action='store_true', help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run optimized application
    app = SimpleOptimizedDeepFaceLiveApp(
        userdata_path=args.userdata_dir,
        no_cuda=args.no_cuda
    )
    
    return app.run()

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
