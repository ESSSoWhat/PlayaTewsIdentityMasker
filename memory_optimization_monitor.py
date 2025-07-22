#!/usr/bin/env python3
"""
Memory Optimization Monitor for DFM Face Swap
Tracks RAM usage and provides optimization recommendations
"""

import time
import psutil
import threading
from typing import Dict, List, Optional
import numpy as np
import os


class MemoryOptimizationMonitor:
    def __init__(self):
        self.memory_history = []
        self.cpu_history = []
        self.cache_stats = []
        self.performance_metrics = []
        
        self.monitoring = False
        self.monitor_thread = None
        
        # Memory optimization settings
        self.target_cache_size_gb = 2.0
        self.max_memory_usage = 80  # percentage
        self.min_available_ram = 2.0  # GB
        
        # Performance tracking
        self.fps_history = []
        self.processing_times = []
        
        # Optimization recommendations
        self.recommendations = []
        
    def start_monitoring(self):
        """Start memory optimization monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("🧠 Memory Optimization Monitor Started")
    
    def stop_monitoring(self):
        """Stop memory optimization monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        print("⏹️ Memory Optimization Monitor Stopped")
    
    def record_performance(self, fps: float = None, processing_time: float = None):
        """Record performance metrics"""
        if fps is not None:
            self.fps_history.append(fps)
            if len(self.fps_history) > 60:
                self.fps_history.pop(0)
        
        if processing_time is not None:
            self.processing_times.append(processing_time)
            if len(self.processing_times) > 100:
                self.processing_times.pop(0)
    
    def get_memory_stats(self) -> Dict:
        """Get comprehensive memory statistics"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Calculate memory metrics
            total_ram_gb = memory.total / (1024**3)
            used_ram_gb = memory.used / (1024**3)
            available_ram_gb = memory.available / (1024**3)
            ram_usage_percent = memory.percent
            
            # Cache efficiency metrics
            cache_efficiency = self._calculate_cache_efficiency()
            
            # Memory pressure indicators
            memory_pressure = self._calculate_memory_pressure(memory, swap)
            
            return {
                'total_ram_gb': total_ram_gb,
                'used_ram_gb': used_ram_gb,
                'available_ram_gb': available_ram_gb,
                'ram_usage_percent': ram_usage_percent,
                'swap_used_gb': swap.used / (1024**3),
                'swap_total_gb': swap.total / (1024**3),
                'cache_efficiency': cache_efficiency,
                'memory_pressure': memory_pressure,
                'optimal_cache_size_gb': self._calculate_optimal_cache_size(memory),
                'memory_bottleneck': self._detect_memory_bottleneck(memory, swap)
            }
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {}
    
    def _calculate_cache_efficiency(self) -> float:
        """Calculate cache efficiency based on performance metrics"""
        if not self.fps_history or not self.processing_times:
            return 0.0
        
        # Calculate efficiency based on FPS stability and processing time reduction
        fps_stability = 1.0 - (np.std(self.fps_history) / np.mean(self.fps_history)) if np.mean(self.fps_history) > 0 else 0
        processing_efficiency = 1.0 - (np.mean(self.processing_times) / 100) if np.mean(self.processing_times) < 100 else 0
        
        return (fps_stability + processing_efficiency) / 2
    
    def _calculate_memory_pressure(self, memory, swap) -> str:
        """Calculate memory pressure level"""
        ram_usage = memory.percent
        swap_usage = (swap.used / swap.total * 100) if swap.total > 0 else 0
        
        if ram_usage > 90 or swap_usage > 50:
            return "CRITICAL"
        elif ram_usage > 80 or swap_usage > 20:
            return "HIGH"
        elif ram_usage > 70:
            return "MODERATE"
        else:
            return "LOW"
    
    def _calculate_optimal_cache_size(self, memory) -> float:
        """Calculate optimal cache size based on available memory"""
        total_ram_gb = memory.total / (1024**3)
        available_ram_gb = memory.available / (1024**3)
        
        # Conservative approach: use 25% of available RAM for cache
        optimal_cache = min(available_ram_gb * 0.25, total_ram_gb * 0.4)
        
        # Ensure minimum and maximum bounds
        optimal_cache = max(0.5, min(optimal_cache, 8.0))
        
        return optimal_cache
    
    def _detect_memory_bottleneck(self, memory, swap) -> Dict:
        """Detect memory-related bottlenecks"""
        bottlenecks = {
            'ram_insufficient': False,
            'swap_heavy': False,
            'cache_too_large': False,
            'memory_fragmentation': False
        }
        
        # Check RAM insufficiency
        if memory.available / (1024**3) < self.min_available_ram:
            bottlenecks['ram_insufficient'] = True
        
        # Check heavy swap usage
        if swap.total > 0 and (swap.used / swap.total) > 0.3:
            bottlenecks['swap_heavy'] = True
        
        # Check if cache is too large
        if self.target_cache_size_gb > memory.available / (1024**3) * 0.5:
            bottlenecks['cache_too_large'] = True
        
        # Check memory fragmentation (simplified)
        if memory.percent > 85 and memory.available / memory.total < 0.1:
            bottlenecks['memory_fragmentation'] = True
        
        return bottlenecks
    
    def analyze_memory_optimization(self) -> List[str]:
        """Analyze memory usage and generate optimization recommendations"""
        recommendations = []
        memory_stats = self.get_memory_stats()
        
        if not memory_stats:
            return ["❌ Unable to get memory statistics"]
        
        # Memory usage analysis
        ram_usage = memory_stats['ram_usage_percent']
        available_ram = memory_stats['available_ram_gb']
        memory_pressure = memory_stats['memory_pressure']
        bottlenecks = memory_stats['memory_bottleneck']
        
        # RAM usage recommendations
        if ram_usage > 90:
            recommendations.append("🚨 CRITICAL: RAM usage too high! Close applications or reduce cache size.")
        elif ram_usage > 80:
            recommendations.append("⚠️ HIGH: RAM usage elevated. Consider reducing cache size or closing apps.")
        elif ram_usage < 50:
            recommendations.append("✅ GOOD: RAM usage is optimal. You can increase cache size for better performance.")
        
        # Available RAM recommendations
        if available_ram < 1.0:
            recommendations.append("💾 LOW: Available RAM is very low. Reduce cache size immediately.")
        elif available_ram < 2.0:
            recommendations.append("⚠️ WARNING: Available RAM is low. Consider reducing cache size.")
        elif available_ram > 8.0:
            recommendations.append("🚀 EXCELLENT: Plenty of RAM available. You can maximize cache size.")
        
        # Memory pressure recommendations
        if memory_pressure == "CRITICAL":
            recommendations.append("🔥 CRITICAL: Memory pressure is critical! Reduce cache size and close applications.")
        elif memory_pressure == "HIGH":
            recommendations.append("🔥 HIGH: Memory pressure is high. Consider reducing cache size.")
        
        # Bottleneck-specific recommendations
        if bottlenecks['ram_insufficient']:
            recommendations.append("💾 INSUFFICIENT RAM: Add more RAM or reduce cache size to 1GB or less.")
        
        if bottlenecks['swap_heavy']:
            recommendations.append("💿 HEAVY SWAP: System is using too much swap. Add more RAM or reduce cache.")
        
        if bottlenecks['cache_too_large']:
            recommendations.append("📦 CACHE TOO LARGE: Reduce cache size to prevent memory issues.")
        
        if bottlenecks['memory_fragmentation']:
            recommendations.append("🧩 MEMORY FRAGMENTATION: Restart application to defragment memory.")
        
        # Cache optimization recommendations
        optimal_cache = memory_stats['optimal_cache_size_gb']
        current_cache = self.target_cache_size_gb
        
        if optimal_cache > current_cache + 0.5:
            recommendations.append(f"📈 OPTIMIZE: Increase cache size to {optimal_cache:.1f}GB for better performance.")
        elif optimal_cache < current_cache - 0.5:
            recommendations.append(f"📉 REDUCE: Decrease cache size to {optimal_cache:.1f}GB to prevent memory issues.")
        
        # Performance-based recommendations
        cache_efficiency = memory_stats['cache_efficiency']
        if cache_efficiency < 0.5:
            recommendations.append("🎯 LOW EFFICIENCY: Cache efficiency is low. Check for dynamic content or increase cache size.")
        elif cache_efficiency > 0.8:
            recommendations.append("✅ HIGH EFFICIENCY: Cache is working well. Performance is optimized.")
        
        # System-specific recommendations
        total_ram = memory_stats['total_ram_gb']
        if total_ram < 8:
            recommendations.extend([
                "💻 LOW RAM SYSTEM:",
                "  • Set cache size to 1GB or less",
                "  • Disable postprocessing cache",
                "  • Close other applications",
                "  • Consider adding more RAM"
            ])
        elif total_ram < 16:
            recommendations.extend([
                "💻 MEDIUM RAM SYSTEM:",
                "  • Set cache size to 2GB",
                "  • Enable preprocessing cache",
                "  • Enable postprocessing cache",
                "  • Monitor memory usage"
            ])
        else:
            recommendations.extend([
                "💻 HIGH RAM SYSTEM:",
                "  • Set cache size to 4GB or more",
                "  • Enable all caching features",
                "  • Enable parallel processing",
                "  • Maximize performance settings"
            ])
        
        return recommendations
    
    def get_optimization_summary(self) -> Dict:
        """Get comprehensive memory optimization summary"""
        memory_stats = self.get_memory_stats()
        recommendations = self.analyze_memory_optimization()
        
        # Calculate performance metrics
        avg_fps = np.mean(self.fps_history) if self.fps_history else 0
        avg_processing_time = np.mean(self.processing_times) if self.processing_times else 0
        
        return {
            'memory': memory_stats,
            'performance': {
                'average_fps': avg_fps,
                'average_processing_time': avg_processing_time,
                'cache_efficiency': memory_stats.get('cache_efficiency', 0) if memory_stats else 0
            },
            'recommendations': recommendations,
            'status': self._get_optimization_status(memory_stats) if memory_stats else "UNKNOWN"
        }
    
    def _get_optimization_status(self, memory_stats: Dict) -> str:
        """Get overall optimization status"""
        ram_usage = memory_stats.get('ram_usage_percent', 0)
        memory_pressure = memory_stats.get('memory_pressure', 'UNKNOWN')
        cache_efficiency = memory_stats.get('cache_efficiency', 0)
        
        if memory_pressure == "CRITICAL" or ram_usage > 90:
            return "CRITICAL"
        elif memory_pressure == "HIGH" or ram_usage > 80:
            return "POOR"
        elif ram_usage > 70 or cache_efficiency < 0.5:
            return "FAIR"
        elif ram_usage < 60 and cache_efficiency > 0.7:
            return "GOOD"
        else:
            return "EXCELLENT"
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Update memory statistics
                memory_stats = self.get_memory_stats()
                if memory_stats:
                    self.memory_history.append(memory_stats['ram_usage_percent'])
                    if len(self.memory_history) > 60:
                        self.memory_history.pop(0)
                
                # Update CPU statistics
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_history.append(cpu_percent)
                if len(self.cpu_history) > 60:
                    self.cpu_history.pop(0)
                
                # Generate recommendations
                recommendations = self.analyze_memory_optimization()
                
                # Print status every 10 seconds
                if int(time.time()) % 10 == 0:
                    self._print_status()
                
                time.sleep(1)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(1)
    
    def _print_status(self):
        """Print current memory optimization status"""
        summary = self.get_optimization_summary()
        
        print("\n" + "="*70)
        print("🧠 Memory Optimization Monitor")
        print("="*70)
        
        # Memory Information
        memory = summary['memory']
        print(f"💾 RAM: {memory['used_ram_gb']:.1f}GB/{memory['total_ram_gb']:.1f}GB ({memory['ram_usage_percent']:.1f}%) | Available: {memory['available_ram_gb']:.1f}GB")
        print(f"💿 Swap: {memory['swap_used_gb']:.1f}GB/{memory['swap_total_gb']:.1f}GB | Pressure: {memory['memory_pressure']}")
        
        # Cache Information
        print(f"📦 Cache: {self.target_cache_size_gb:.1f}GB | Optimal: {memory['optimal_cache_size_gb']:.1f}GB | Efficiency: {memory['cache_efficiency']:.1%}")
        
        # Performance Information
        perf = summary['performance']
        print(f"📊 Performance: FPS={perf['average_fps']:.1f} | Processing={perf['average_processing_time']:.1f}ms")
        
        # Status
        print(f"🎯 Status: {summary['status']}")
        
        # Bottlenecks
        bottlenecks = memory['memory_bottleneck']
        if any(bottlenecks.values()):
            print("\n🚨 Bottlenecks Detected:")
            for bottleneck, active in bottlenecks.items():
                if active:
                    print(f"  • {bottleneck.replace('_', ' ').title()}")
        
        # Recommendations
        if summary['recommendations']:
            print("\n💡 Recommendations:")
            for rec in summary['recommendations'][:5]:  # Show top 5
                print(f"  {rec}")
        
        print("="*70)
    
    def export_report(self, filename: str = "memory_optimization_report.txt"):
        """Export memory optimization report to file"""
        summary = self.get_optimization_summary()
        
        with open(filename, 'w') as f:
            f.write("Memory Optimization Report for DFM Face Swap\n")
            f.write("="*50 + "\n\n")
            
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Memory Section
            memory = summary['memory']
            f.write("Memory Statistics:\n")
            f.write(f"  Total RAM: {memory['total_ram_gb']:.1f}GB\n")
            f.write(f"  Used RAM: {memory['used_ram_gb']:.1f}GB\n")
            f.write(f"  Available RAM: {memory['available_ram_gb']:.1f}GB\n")
            f.write(f"  RAM Usage: {memory['ram_usage_percent']:.1f}%\n")
            f.write(f"  Swap Used: {memory['swap_used_gb']:.1f}GB\n")
            f.write(f"  Memory Pressure: {memory['memory_pressure']}\n")
            f.write(f"  Cache Efficiency: {memory['cache_efficiency']:.1%}\n")
            f.write(f"  Optimal Cache Size: {memory['optimal_cache_size_gb']:.1f}GB\n\n")
            
            # Performance Section
            perf = summary['performance']
            f.write("Performance Statistics:\n")
            f.write(f"  Average FPS: {perf['average_fps']:.1f}\n")
            f.write(f"  Average Processing Time: {perf['average_processing_time']:.1f}ms\n")
            f.write(f"  Cache Efficiency: {perf['cache_efficiency']:.1%}\n\n")
            
            # Bottlenecks Section
            bottlenecks = memory['memory_bottleneck']
            f.write("Memory Bottlenecks:\n")
            for bottleneck, active in bottlenecks.items():
                f.write(f"  {bottleneck.replace('_', ' ').title()}: {'Yes' if active else 'No'}\n")
            f.write("\n")
            
            # Recommendations Section
            f.write("Optimization Recommendations:\n")
            for rec in summary['recommendations']:
                f.write(f"  {rec}\n")
        
        print(f"📄 Memory optimization report exported to: {filename}")


# Example usage
if __name__ == "__main__":
    monitor = MemoryOptimizationMonitor()
    
    print("🧠 Memory Optimization Monitor Demo")
    print("Press Ctrl+C to stop")
    
    try:
        monitor.start_monitoring()
        
        # Simulate performance data
        while True:
            # Simulate FPS and processing time
            fps = np.random.uniform(20, 40)
            processing_time = np.random.uniform(10, 50)
            
            monitor.record_performance(fps, processing_time)
            time.sleep(1)
            
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        
        # Export final report
        monitor.export_report()
        
        print("\n👋 Monitoring stopped. Check the memory optimization report for details!") 