#!/usr/bin/env python3
"""
FPS Optimization and Video Loopback Demo
Demonstrates the enhanced performance optimization and fallback systems
"""

import time
import threading
import logging
import cv2
import numpy as np
from pathlib import Path
import argparse
import json
from typing import Dict, Any, Optional

# Import our optimization systems
try:
    from fps_optimizer import (
        FPSOptimizer, OptimizationSettings, OptimizationStrategy, 
        QualityLevel, get_fps_optimizer, start_fps_optimization
    )
    from video_loopback_system import (
        VideoLoopbackSystem, LoopbackSettings, LoopbackMode,
        LoopbackSource, SourceType, get_loopback_system, start_loopback_system
    )
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False
    print("Warning: Optimization systems not available")

class PerformanceDemo:
    """Demonstration of FPS optimization and video loopback systems"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.running = False
        self.demo_thread = None
        
        # Performance tracking
        self.performance_history = []
        self.optimization_events = []
        self.loopback_events = []
        
        # Demo state
        self.simulate_load = False
        self.simulate_feed_loss = False
        self.demo_mode = "normal"
        
        # Initialize systems
        self._initialize_systems()
        
        self.logger = logging.getLogger(__name__)
    
    def _initialize_systems(self):
        """Initialize optimization and loopback systems"""
        if not OPTIMIZATION_AVAILABLE:
            self.logger.error("Optimization systems not available")
            return
        
        try:
            # Initialize FPS optimizer
            fps_settings = OptimizationSettings(
                target_fps=self.config.get('target_fps', 30.0),
                min_fps=self.config.get('min_fps', 15.0),
                max_fps=self.config.get('max_fps', 60.0),
                strategy=OptimizationStrategy.ADAPTIVE,
                quality_level=QualityLevel.MEDIUM,
                auto_optimization=True
            )
            
            self.fps_optimizer = get_fps_optimizer()
            self.fps_optimizer.settings = fps_settings
            
            # Set up callbacks
            self.fps_optimizer.on_quality_change = self._on_quality_change
            self.fps_optimizer.on_fps_warning = self._on_fps_warning
            self.fps_optimizer.on_performance_alert = self._on_performance_alert
            
            # Initialize loopback system
            loopback_settings = LoopbackSettings(
                mode=LoopbackMode.IMMEDIATE,
                detection_timeout=self.config.get('loopback_timeout', 2.0),
                transition_duration=1.0,
                auto_recovery=True,
                recovery_delay=3.0
            )
            
            self.loopback_system = get_loopback_system()
            self.loopback_system.settings = loopback_settings
            
            # Set up callbacks
            self.loopback_system.on_feed_loss = self._on_feed_loss
            self.loopback_system.on_feed_recovery = self._on_feed_recovery
            self.loopback_system.on_source_change = self._on_source_change
            
            # Add custom loopback sources
            self._add_demo_loopback_sources()
            
            self.logger.info("Demo systems initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize demo systems: {e}")
    
    def _add_demo_loopback_sources(self):
        """Add demonstration loopback sources"""
        if not hasattr(self, 'loopback_system'):
            return
        
        # Add a test video file if available
        test_video_path = Path("demo_video.mp4")
        if test_video_path.exists():
            video_config = LoopbackSource(
                name="demo_video",
                source_type=SourceType.VIDEO_FILE.value,
                path=test_video_path,
                priority=1,
                loop=True
            )
            self.loopback_system.add_source(video_config)
        
        # Add image sequence if available
        image_dir = Path("demo_images")
        if image_dir.exists() and image_dir.is_dir():
            image_config = LoopbackSource(
                name="demo_images",
                source_type=SourceType.IMAGE_SEQUENCE.value,
                path=image_dir,
                priority=2,
                loop=True
            )
            self.loopback_system.add_source(image_config)
        
        # Add static image if available
        static_image_path = Path("demo_image.jpg")
        if static_image_path.exists():
            static_config = LoopbackSource(
                name="demo_static",
                source_type=SourceType.STATIC_IMAGE.value,
                path=static_image_path,
                priority=3
            )
            self.loopback_system.add_source(static_config)
    
    def start_demo(self, duration: int = 60):
        """Start the performance demonstration"""
        if self.running:
            self.logger.warning("Demo already running")
            return
        
        self.running = True
        self.demo_thread = threading.Thread(target=self._demo_loop, args=(duration,), daemon=True)
        self.demo_thread.start()
        
        # Start optimization systems
        if OPTIMIZATION_AVAILABLE:
            if hasattr(self, 'fps_optimizer'):
                self.fps_optimizer.start()
            if hasattr(self, 'loopback_system'):
                self.loopback_system.start()
        
        self.logger.info(f"Performance demo started for {duration} seconds")
    
    def stop_demo(self):
        """Stop the performance demonstration"""
        self.running = False
        
        if self.demo_thread:
            self.demo_thread.join(timeout=2.0)
        
        # Stop optimization systems
        if OPTIMIZATION_AVAILABLE:
            if hasattr(self, 'fps_optimizer'):
                self.fps_optimizer.stop()
            if hasattr(self, 'loopback_system'):
                self.loopback_system.stop()
        
        self.logger.info("Performance demo stopped")
    
    def _demo_loop(self, duration: int):
        """Main demo loop"""
        start_time = time.time()
        frame_count = 0
        
        while self.running and (time.time() - start_time) < duration:
            loop_start = time.time()
            
            # Simulate frame processing
            self._simulate_frame_processing()
            
            # Record frame for FPS optimization
            if OPTIMIZATION_AVAILABLE and hasattr(self, 'fps_optimizer'):
                self.fps_optimizer.record_frame(loop_start)
            
            # Simulate feed heartbeat (or loss)
            if OPTIMIZATION_AVAILABLE and hasattr(self, 'loopback_system'):
                if not self.simulate_feed_loss:
                    self.loopback_system.feed_heartbeat()
            
            # Demo scenarios
            elapsed_time = time.time() - start_time
            
            # Simulate load at 30 seconds
            if elapsed_time > 30 and not self.simulate_load:
                self.simulate_load = True
                self.logger.info("🔄 Simulating high load scenario")
            
            # Simulate feed loss at 45 seconds
            if elapsed_time > 45 and not self.simulate_feed_loss:
                self.simulate_feed_loss = True
                self.logger.info("⚠️ Simulating feed loss scenario")
            
            # Recover feed at 50 seconds
            if elapsed_time > 50 and self.simulate_feed_loss:
                self.simulate_feed_loss = False
                self.logger.info("✅ Simulating feed recovery")
            
            frame_count += 1
            
            # Maintain target frame rate
            frame_time = time.time() - loop_start
            target_frame_time = 1.0 / 30.0  # 30 FPS
            if frame_time < target_frame_time:
                time.sleep(target_frame_time - frame_time)
    
    def _simulate_frame_processing(self):
        """Simulate frame processing with variable load"""
        if self.simulate_load:
            # Simulate high CPU load
            processing_time = 0.05 + (np.random.random() * 0.1)  # 50-150ms
        else:
            # Normal processing
            processing_time = 0.01 + (np.random.random() * 0.02)  # 10-30ms
        
        time.sleep(processing_time)
    
    def _on_quality_change(self, new_quality: float):
        """Handle quality level changes"""
        event = {
            'timestamp': time.time(),
            'type': 'quality_change',
            'quality': new_quality
        }
        self.optimization_events.append(event)
        self.logger.info(f"🎛️ Quality adjusted to {new_quality:.2f}")
    
    def _on_fps_warning(self, fps: float):
        """Handle FPS warnings"""
        event = {
            'timestamp': time.time(),
            'type': 'fps_warning',
            'fps': fps
        }
        self.optimization_events.append(event)
        self.logger.warning(f"⚠️ Low FPS detected: {fps:.1f}")
    
    def _on_performance_alert(self, alert_type: str, data: Any):
        """Handle performance alerts"""
        event = {
            'timestamp': time.time(),
            'type': 'performance_alert',
            'alert_type': alert_type,
            'data': data
        }
        self.optimization_events.append(event)
        self.logger.warning(f"🚨 Performance alert: {alert_type}")
    
    def _on_feed_loss(self):
        """Handle main feed loss"""
        event = {
            'timestamp': time.time(),
            'type': 'feed_loss'
        }
        self.loopback_events.append(event)
        self.logger.warning("📺 Main feed lost, loopback activated")
    
    def _on_feed_recovery(self):
        """Handle main feed recovery"""
        event = {
            'timestamp': time.time(),
            'type': 'feed_recovery'
        }
        self.loopback_events.append(event)
        self.logger.info("✅ Main feed recovered")
    
    def _on_source_change(self, source_name: str):
        """Handle loopback source changes"""
        event = {
            'timestamp': time.time(),
            'type': 'source_change',
            'source': source_name
        }
        self.loopback_events.append(event)
        self.logger.info(f"🔄 Loopback source changed to: {source_name}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not OPTIMIZATION_AVAILABLE:
            return {"error": "Optimization systems not available"}
        
        fps_summary = {}
        loopback_summary = {}
        
        if hasattr(self, 'fps_optimizer'):
            fps_summary = self.fps_optimizer.get_performance_summary()
        
        if hasattr(self, 'loopback_system'):
            loopback_summary = self.loopback_system.get_status()
        
        return {
            'fps_optimization': fps_summary,
            'loopback_system': loopback_summary,
            'optimization_events': len(self.optimization_events),
            'loopback_events': len(self.loopback_events),
            'performance_history': len(self.performance_history)
        }
    
    def export_results(self, filepath: str):
        """Export demo results to JSON file"""
        results = {
            'summary': self.get_performance_summary(),
            'optimization_events': self.optimization_events,
            'loopback_events': self.loopback_events,
            'performance_history': self.performance_history,
            'config': self.config
        }
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Demo results exported to {filepath}")

def run_interactive_demo():
    """Run interactive demonstration"""
    print("🎬 FPS Optimization and Video Loopback Demo")
    print("=" * 50)
    
    if not OPTIMIZATION_AVAILABLE:
        print("❌ Optimization systems not available")
        return
    
    # Configuration
    config = {
        'target_fps': 30.0,
        'min_fps': 15.0,
        'max_fps': 60.0,
        'loopback_timeout': 2.0
    }
    
    demo = PerformanceDemo(config)
    
    try:
        print("\n🚀 Starting performance demo...")
        demo.start_demo(duration=60)
        
        print("\n📊 Demo running for 60 seconds...")
        print("   - 0-30s: Normal operation")
        print("   - 30-45s: High load simulation")
        print("   - 45-50s: Feed loss simulation")
        print("   - 50-60s: Feed recovery")
        
        # Monitor progress
        for i in range(60):
            time.sleep(1)
            if not demo.running:
                break
            
            # Print status every 10 seconds
            if (i + 1) % 10 == 0:
                summary = demo.get_performance_summary()
                fps_info = summary.get('fps_optimization', {})
                current_fps = fps_info.get('current_fps', 0)
                quality = fps_info.get('quality_level', 0)
                print(f"   {i+1}s: FPS={current_fps:.1f}, Quality={quality:.2f}")
        
        print("\n✅ Demo completed!")
        
        # Show final results
        summary = demo.get_performance_summary()
        print("\n📈 Final Results:")
        print(f"   Current FPS: {summary['fps_optimization'].get('current_fps', 0):.1f}")
        print(f"   Quality Level: {summary['fps_optimization'].get('quality_level', 0):.2f}")
        print(f"   Frame Drops: {summary['fps_optimization'].get('frame_drops', 0)}")
        print(f"   Optimization Events: {summary['optimization_events']}")
        print(f"   Loopback Events: {summary['loopback_events']}")
        
        # Export results
        demo.export_results("demo_results.json")
        print("\n💾 Results exported to demo_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    finally:
        demo.stop_demo()

def run_benchmark_test():
    """Run benchmark test"""
    print("🏃 Running FPS optimization benchmark...")
    
    if not OPTIMIZATION_AVAILABLE:
        print("❌ Optimization systems not available")
        return
    
    # Test different optimization strategies
    strategies = [
        ('aggressive', OptimizationStrategy.AGGRESSIVE),
        ('balanced', OptimizationStrategy.BALANCED),
        ('conservative', OptimizationStrategy.CONSERVATIVE),
        ('adaptive', OptimizationStrategy.ADAPTIVE)
    ]
    
    results = {}
    
    for strategy_name, strategy in strategies:
        print(f"\n🧪 Testing {strategy_name} strategy...")
        
        config = {
            'target_fps': 30.0,
            'min_fps': 15.0,
            'max_fps': 60.0
        }
        
        demo = PerformanceDemo(config)
        
        # Set strategy
        demo.fps_optimizer.set_optimization_strategy(strategy)
        
        # Run test
        demo.start_demo(duration=30)
        time.sleep(30)
        demo.stop_demo()
        
        # Get results
        summary = demo.get_performance_summary()
        results[strategy_name] = summary['fps_optimization']
        
        print(f"   Average FPS: {summary['fps_optimization'].get('current_fps', 0):.1f}")
        print(f"   Quality Level: {summary['fps_optimization'].get('quality_level', 0):.2f}")
        print(f"   Frame Drops: {summary['fps_optimization'].get('frame_drops', 0)}")
    
    # Export benchmark results
    with open("benchmark_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Benchmark results exported to benchmark_results.json")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="FPS Optimization and Video Loopback Demo")
    parser.add_argument("--mode", choices=["interactive", "benchmark"], default="interactive",
                       help="Demo mode")
    parser.add_argument("--duration", type=int, default=60,
                       help="Demo duration in seconds")
    parser.add_argument("--target-fps", type=float, default=30.0,
                       help="Target FPS")
    parser.add_argument("--strategy", choices=["aggressive", "balanced", "conservative", "adaptive"],
                       default="adaptive", help="Optimization strategy")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if args.mode == "interactive":
        run_interactive_demo()
    elif args.mode == "benchmark":
        run_benchmark_test()
    else:
        print("Invalid mode specified")

if __name__ == "__main__":
    main()