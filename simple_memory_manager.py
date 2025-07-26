import gc
import threading
import time
import logging

logger = logging.getLogger(__name__)

class SimpleMemoryManager:
    def __init__(self):
        self.monitoring_enabled = True
        self.monitor_thread = None
        self._stop_monitoring = False
        
    def start_monitoring(self):
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self._stop_monitoring = False
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("✅ Memory monitoring started")
    
    def stop_monitoring(self):
        self._stop_monitoring = True
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        logger.info("✅ Memory monitoring stopped")
    
    def _monitor_loop(self):
        while not self._stop_monitoring:
            try:
                # Force garbage collection every 30 seconds
                gc.collect()
                time.sleep(30.0)
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                time.sleep(5.0)

_memory_manager = None

def get_memory_manager():
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = SimpleMemoryManager()
    return _memory_manager

def start_memory_monitoring():
    get_memory_manager().start_monitoring()

def stop_memory_monitoring():
    get_memory_manager().stop_monitoring()
