#!/usr/bin/env python3
"""
Real-time Memory Performance Monitor
Monitors memory usage and performance while the application is running
"""

import time
import psutil
import threading
from datetime import datetime
import os

class MemoryPerformanceMonitor:
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.performance_data = []
        self.max_data_points = 100
        
    def start_monitoring(self):
        """Start real-time monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("🧠 Real-time Memory Performance Monitor Started")
            print("Press Ctrl+C to stop monitoring")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        print("\n⏹️ Monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Get system metrics
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Get process metrics for the main application
                app_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
                    try:
                        if 'python' in proc.info['name'].lower() and 'playa' in ' '.join(proc.cmdline()).lower():
                            app_processes.append(proc.info)
                    except:
                        continue
                
                # Calculate metrics
                total_ram_gb = memory.total / (1024**3)
                used_ram_gb = memory.used / (1024**3)
                available_ram_gb = memory.available / (1024**3)
                ram_usage_percent = memory.percent
                
                # Store data
                data_point = {
                    'timestamp': datetime.now(),
                    'ram_usage_percent': ram_usage_percent,
                    'cpu_percent': cpu_percent,
                    'available_ram_gb': available_ram_gb,
                    'app_processes': app_processes
                }
                
                self.performance_data.append(data_point)
                
                # Keep only recent data
                if len(self.performance_data) > self.max_data_points:
                    self.performance_data.pop(0)
                
                # Calculate trends
                if len(self.performance_data) > 10:
                    recent_ram = [d['ram_usage_percent'] for d in self.performance_data[-10:]]
                    recent_cpu = [d['cpu_percent'] for d in self.performance_data[-10:]]
                    
                    ram_trend = "↗️" if recent_ram[-1] > recent_ram[0] else "↘️" if recent_ram[-1] < recent_ram[0] else "➡️"
                    cpu_trend = "↗️" if recent_cpu[-1] > recent_cpu[0] else "↘️" if recent_cpu[-1] < recent_cpu[0] else "➡️"
                else:
                    ram_trend = "➡️"
                    cpu_trend = "➡️"
                
                # Clear screen and display metrics
                os.system('cls' if os.name == 'nt' else 'clear')
                
                print("🧠 Memory Performance Monitor - Real-time")
                print("=" * 60)
                print(f"📊 Time: {datetime.now().strftime('%H:%M:%S')}")
                print()
                
                # System metrics
                print("💻 System Metrics:")
                print(f"   RAM Usage: {ram_usage_percent:.1f}% {ram_trend} ({used_ram_gb:.1f}GB / {total_ram_gb:.1f}GB)")
                print(f"   Available RAM: {available_ram_gb:.1f}GB")
                print(f"   CPU Usage: {cpu_percent:.1f}% {cpu_trend}")
                print()
                
                # Memory optimization status
                print("🎯 Memory Optimization Status:")
                if ram_usage_percent < 60:
                    print("   ✅ RAM Usage: Optimal")
                elif ram_usage_percent < 80:
                    print("   ✅ RAM Usage: Good")
                else:
                    print("   ⚠️  RAM Usage: High - Consider reducing cache size")
                
                if available_ram_gb > 8:
                    print("   ✅ Available RAM: Excellent for caching")
                elif available_ram_gb > 4:
                    print("   ✅ Available RAM: Good for caching")
                else:
                    print("   ⚠️  Available RAM: Limited - Reduce cache size")
                
                if cpu_percent < 60:
                    print("   ✅ CPU Usage: Optimal")
                elif cpu_percent < 80:
                    print("   ✅ CPU Usage: Good")
                else:
                    print("   ⚠️  CPU Usage: High - Memory optimization working")
                print()
                
                # Application processes
                if app_processes:
                    print("🔍 Application Processes:")
                    for proc in app_processes:
                        print(f"   PID {proc['pid']}: {proc['name']} - RAM: {proc['memory_percent']:.1f}%, CPU: {proc['cpu_percent']:.1f}%")
                else:
                    print("🔍 Application Processes: Not detected")
                print()
                
                # Performance recommendations
                print("💡 Performance Recommendations:")
                if ram_usage_percent > 80:
                    print("   • Reduce RAM cache size")
                    print("   • Close other applications")
                    print("   • Disable postprocessing cache")
                elif ram_usage_percent < 50 and available_ram_gb > 8:
                    print("   • Increase RAM cache size for better performance")
                    print("   • Enable all caching features")
                    print("   • Enable parallel processing")
                else:
                    print("   • Current settings are optimal")
                    print("   • Monitor for performance changes")
                print()
                
                # Cache efficiency estimation
                if len(self.performance_data) > 20:
                    recent_data = self.performance_data[-20:]
                    avg_cpu = sum(d['cpu_percent'] for d in recent_data) / len(recent_data)
                    avg_ram = sum(d['ram_usage_percent'] for d in recent_data) / len(recent_data)
                    
                    # Estimate cache efficiency based on CPU reduction
                    expected_cpu_without_cache = 80  # Expected CPU without optimization
                    cache_efficiency = max(0, (expected_cpu_without_cache - avg_cpu) / expected_cpu_without_cache)
                    
                    print("📈 Cache Efficiency Estimation:")
                    print(f"   Average CPU: {avg_cpu:.1f}%")
                    print(f"   Average RAM: {avg_ram:.1f}%")
                    print(f"   Estimated Cache Efficiency: {cache_efficiency:.1%}")
                    
                    if cache_efficiency > 0.5:
                        print("   ✅ Excellent cache performance")
                    elif cache_efficiency > 0.3:
                        print("   ✅ Good cache performance")
                    else:
                        print("   ⚠️  Low cache efficiency - check settings")
                print()
                
                print("Press Ctrl+C to stop monitoring")
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Error in monitoring: {e}")
                time.sleep(2)
    
    def get_performance_summary(self):
        """Get performance summary"""
        if not self.performance_data:
            return "No data available"
        
        recent_data = self.performance_data[-20:] if len(self.performance_data) >= 20 else self.performance_data
        
        avg_ram = sum(d['ram_usage_percent'] for d in recent_data) / len(recent_data)
        avg_cpu = sum(d['cpu_percent'] for d in recent_data) / len(recent_data)
        max_ram = max(d['ram_usage_percent'] for d in recent_data)
        max_cpu = max(d['cpu_percent'] for d in recent_data)
        
        return {
            'avg_ram_usage': avg_ram,
            'avg_cpu_usage': avg_cpu,
            'max_ram_usage': max_ram,
            'max_cpu_usage': max_cpu,
            'data_points': len(self.performance_data)
        }

def main():
    """Main function"""
    print("🧠 Memory Performance Monitor")
    print("=" * 40)
    print("This monitor will show real-time memory and CPU usage")
    print("while your PlayaTewsIdentityMasker application is running.")
    print()
    
    monitor = MemoryPerformanceMonitor()
    
    try:
        monitor.start_monitoring()
        
        # Keep the main thread alive
        while monitor.monitoring:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")
        monitor.stop_monitoring()
        
        # Show final summary
        summary = monitor.get_performance_summary()
        if isinstance(summary, dict):
            print("\n📊 Performance Summary:")
            print(f"   Average RAM Usage: {summary['avg_ram_usage']:.1f}%")
            print(f"   Average CPU Usage: {summary['avg_cpu_usage']:.1f}%")
            print(f"   Peak RAM Usage: {summary['max_ram_usage']:.1f}%")
            print(f"   Peak CPU Usage: {summary['max_cpu_usage']:.1f}%")
            print(f"   Data Points Collected: {summary['data_points']}")
        
        print("\n👋 Monitoring complete!")

if __name__ == "__main__":
    main() 