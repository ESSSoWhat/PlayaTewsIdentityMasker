import time
import threading
import logging

logger = logging.getLogger(__name__)

class SimplePerformanceOptimizer:
    def __init__(self):
        self.target_fps = 30.0
        self.frame_drops = 0
        self.last_frame_time = time.time()
        self.monitor_thread = None
        self._stop_monitoring = False
        
    def start_monitoring(self):
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self._stop_monitoring = False
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("✅ Performance monitoring started")
    
    def stop_monitoring(self):
        self._stop_monitoring = True
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        logger.info("✅ Performance monitoring stopped")
    
    def _monitor_loop(self):
        while not self._stop_monitoring:
            try:
                current_time = time.time()
                frame_time = current_time - self.last_frame_time
                
                if frame_time > 0:
                    current_fps = 1.0 / frame_time
                    if current_fps < self.target_fps * 0.9:
                        self.frame_drops += 1
                        logger.warning(f"Performance issue: {current_fps:.1f} FPS")
                
                self.last_frame_time = current_time
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                time.sleep(1.0)
    
    def get_performance_metrics(self):
        return {
            'target_fps': self.target_fps,
            'frame_drops': self.frame_drops
        }

_performance_optimizer = None

def get_performance_optimizer():
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = SimplePerformanceOptimizer()
    return _performance_optimizer

def start_performance_monitoring():
    get_performance_optimizer().start_monitoring()

def stop_performance_monitoring():
    get_performance_optimizer().stop_monitoring()
