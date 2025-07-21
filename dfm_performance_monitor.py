#!/usr/bin/env python3
"""
DFM Face Swap Performance Monitor
Monitors FPS and provides optimization recommendations
"""

import time
import psutil
import threading
from typing import Dict, List, Optional
import numpy as np


class DFMPerformanceMonitor:
    def __init__(self):
        self.fps_history = []
        self.processing_times = []
        self.memory_usage = []
        self.cpu_usage = []
        self.gpu_usage = []
        
        self.start_time = time.time()
        self.frame_count = 0
        self.last_fps_update = self.start_time
        
        self.monitoring = False
        self.monitor_thread = None
        
        # Performance thresholds
        self.target_fps = 30
        self.min_acceptable_fps = 15
        self.max_memory_usage = 80  # percentage
        self.max_cpu_usage = 90     # percentage
        
        # Optimization recommendations
        self.recommendations = []
        
    def start_monitoring(self):
        """Start performance monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("🚀 DFM Performance Monitor Started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        print("⏹️ DFM Performance Monitor Stopped")
    
    def record_frame(self, processing_time: float = None):
        """Record a processed frame"""
        current_time = time.time()
        self.frame_count += 1
        
        # Update FPS
        if current_time - self.last_fps_update >= 1.0:
            current_fps = self.frame_count / (current_time - self.start_time)
            self.fps_history.append(current_fps)
            
            # Keep only last 60 seconds of history
            if len(self.fps_history) > 60:
                self.fps_history.pop(0)
            
            self.frame_count = 0
            self.start_time = current_time
            self.last_fps_update = current_time
        
        # Record processing time
        if processing_time is not None:
            self.processing_times.append(processing_time)
            if len(self.processing_times) > 100:
                self.processing_times.pop(0)
    
    def get_current_fps(self) -> float:
        """Get current FPS"""
        if self.fps_history:
            return self.fps_history[-1]
        return 0.0
    
    def get_average_fps(self) -> float:
        """Get average FPS over the last minute"""
        if self.fps_history:
            return np.mean(self.fps_history)
        return 0.0
    
    def get_system_stats(self) -> Dict:
        """Get current system statistics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_usage.append(cpu_percent)
            if len(self.cpu_usage) > 60:
                self.cpu_usage.pop(0)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_usage.append(memory_percent)
            if len(self.memory_usage) > 60:
                self.memory_usage.pop(0)
            
            # GPU usage (if available)
            gpu_percent = self._get_gpu_usage()
            if gpu_percent is not None:
                self.gpu_usage.append(gpu_percent)
                if len(self.gpu_usage) > 60:
                    self.gpu_usage.pop(0)
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_available': memory.available / (1024**3),  # GB
                'gpu_percent': gpu_percent,
                'gpu_memory_used': self._get_gpu_memory_usage()
            }
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return {}
    
    def _get_gpu_usage(self) -> Optional[float]:
        """Get GPU usage percentage"""
        try:
            # Try to get GPU usage using nvidia-smi
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        return None
    
    def _get_gpu_memory_usage(self) -> Optional[float]:
        """Get GPU memory usage in GB"""
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip()) / 1024  # Convert MB to GB
        except:
            pass
        return None
    
    def analyze_performance(self) -> List[str]:
        """Analyze performance and generate recommendations"""
        recommendations = []
        current_fps = self.get_current_fps()
        avg_fps = self.get_average_fps()
        system_stats = self.get_system_stats()
        
        # FPS Analysis
        if current_fps < self.min_acceptable_fps:
            recommendations.append("🚨 CRITICAL: FPS too low! Consider reducing model resolution or enabling frame skipping.")
        elif current_fps < self.target_fps * 0.8:
            recommendations.append("⚠️ WARNING: FPS below target. Try enabling caching or reducing quality settings.")
        elif current_fps > self.target_fps * 1.2:
            recommendations.append("✅ GOOD: FPS above target. You can increase quality settings for better results.")
        
        # System Resource Analysis
        if system_stats.get('cpu_percent', 0) > self.max_cpu_usage:
            recommendations.append("🔥 HIGH CPU: Close other applications or reduce processing load.")
        
        if system_stats.get('memory_percent', 0) > self.max_memory_usage:
            recommendations.append("💾 HIGH MEMORY: Close applications or use smaller models.")
        
        if system_stats.get('gpu_percent', 0) and system_stats['gpu_percent'] > 90:
            recommendations.append("🎮 HIGH GPU: GPU is at maximum capacity. Consider reducing model resolution.")
        
        # Processing Time Analysis
        if self.processing_times:
            avg_processing_time = np.mean(self.processing_times)
            if avg_processing_time > 50:  # ms
                recommendations.append("⏱️ SLOW PROCESSING: Consider enabling caching or using faster models.")
        
        # Specific Recommendations
        if current_fps < 20:
            recommendations.extend([
                "🎯 QUICK FIXES:",
                "  • Set Frame Skip Rate to 1 (skip every other frame)",
                "  • Disable Two-Pass Processing",
                "  • Use 256x256 or smaller model resolution",
                "  • Enable Caching"
            ])
        
        if current_fps < 15:
            recommendations.extend([
                "🚀 AGGRESSIVE OPTIMIZATION:",
                "  • Set Frame Skip Rate to 2 (skip 2 out of 3 frames)",
                "  • Use 128x128 model resolution",
                "  • Disable all gamma corrections",
                "  • Close all other applications"
            ])
        
        return recommendations
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        current_fps = self.get_current_fps()
        avg_fps = self.get_average_fps()
        system_stats = self.get_system_stats()
        
        # Calculate statistics
        fps_stats = {
            'current': current_fps,
            'average': avg_fps,
            'min': min(self.fps_history) if self.fps_history else 0,
            'max': max(self.fps_history) if self.fps_history else 0,
            'stability': np.std(self.fps_history) if len(self.fps_history) > 1 else 0
        }
        
        processing_stats = {
            'average_time': np.mean(self.processing_times) if self.processing_times else 0,
            'max_time': max(self.processing_times) if self.processing_times else 0,
            'min_time': min(self.processing_times) if self.processing_times else 0
        }
        
        return {
            'fps': fps_stats,
            'processing': processing_stats,
            'system': system_stats,
            'recommendations': self.analyze_performance(),
            'status': self._get_performance_status(current_fps, avg_fps)
        }
    
    def _get_performance_status(self, current_fps: float, avg_fps: float) -> str:
        """Get overall performance status"""
        if current_fps < self.min_acceptable_fps:
            return "CRITICAL"
        elif current_fps < self.target_fps * 0.8:
            return "POOR"
        elif current_fps < self.target_fps:
            return "FAIR"
        elif current_fps < self.target_fps * 1.2:
            return "GOOD"
        else:
            return "EXCELLENT"
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Update system stats
                self.get_system_stats()
                
                # Generate recommendations
                recommendations = self.analyze_performance()
                
                # Print status every 5 seconds
                if int(time.time()) % 5 == 0:
                    self._print_status()
                
                time.sleep(1)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(1)
    
    def _print_status(self):
        """Print current performance status"""
        summary = self.get_performance_summary()
        
        print("\n" + "="*60)
        print("🎭 DFM Face Swap Performance Monitor")
        print("="*60)
        
        # FPS Information
        fps = summary['fps']
        print(f"📊 FPS: Current={fps['current']:.1f} | Avg={fps['average']:.1f} | Min={fps['min']:.1f} | Max={fps['max']:.1f}")
        
        # Processing Information
        proc = summary['processing']
        if proc['average_time'] > 0:
            print(f"⏱️ Processing: Avg={proc['average_time']:.1f}ms | Max={proc['max_time']:.1f}ms")
        
        # System Information
        sys_stats = summary['system']
        print(f"💻 System: CPU={sys_stats.get('cpu_percent', 0):.1f}% | RAM={sys_stats.get('memory_percent', 0):.1f}% | GPU={sys_stats.get('gpu_percent', 0):.1f}%")
        
        # Status
        print(f"🎯 Status: {summary['status']}")
        
        # Recommendations
        if summary['recommendations']:
            print("\n💡 Recommendations:")
            for rec in summary['recommendations']:
                print(f"  {rec}")
        
        print("="*60)
    
    def export_report(self, filename: str = "dfm_performance_report.txt"):
        """Export performance report to file"""
        summary = self.get_performance_summary()
        
        with open(filename, 'w') as f:
            f.write("DFM Face Swap Performance Report\n")
            f.write("="*40 + "\n\n")
            
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # FPS Section
            fps = summary['fps']
            f.write("FPS Statistics:\n")
            f.write(f"  Current: {fps['current']:.1f}\n")
            f.write(f"  Average: {fps['average']:.1f}\n")
            f.write(f"  Min: {fps['min']:.1f}\n")
            f.write(f"  Max: {fps['max']:.1f}\n")
            f.write(f"  Stability: {fps['stability']:.2f}\n\n")
            
            # Processing Section
            proc = summary['processing']
            f.write("Processing Statistics:\n")
            f.write(f"  Average Time: {proc['average_time']:.1f}ms\n")
            f.write(f"  Max Time: {proc['max_time']:.1f}ms\n")
            f.write(f"  Min Time: {proc['min_time']:.1f}ms\n\n")
            
            # System Section
            sys_stats = summary['system']
            f.write("System Statistics:\n")
            f.write(f"  CPU Usage: {sys_stats.get('cpu_percent', 0):.1f}%\n")
            f.write(f"  Memory Usage: {sys_stats.get('memory_percent', 0):.1f}%\n")
            f.write(f"  Available Memory: {sys_stats.get('memory_available', 0):.1f}GB\n")
            f.write(f"  GPU Usage: {sys_stats.get('gpu_percent', 0):.1f}%\n")
            f.write(f"  GPU Memory: {sys_stats.get('gpu_memory_used', 0):.1f}GB\n\n")
            
            # Recommendations
            f.write("Recommendations:\n")
            for rec in summary['recommendations']:
                f.write(f"  {rec}\n")
        
        print(f"📄 Performance report exported to: {filename}")


# Example usage
if __name__ == "__main__":
    monitor = DFMPerformanceMonitor()
    
    print("🎭 DFM Performance Monitor Demo")
    print("Press Ctrl+C to stop")
    
    try:
        monitor.start_monitoring()
        
        # Simulate frame processing
        while True:
            # Simulate processing time (random between 10-50ms)
            processing_time = np.random.uniform(10, 50)
            time.sleep(processing_time / 1000)  # Convert to seconds
            
            # Record frame
            monitor.record_frame(processing_time)
            
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        
        # Export final report
        monitor.export_report()
        
        print("\n👋 Monitoring stopped. Check the performance report for details!") 