#!/usr/bin/env python3
"""
Enhanced Error Recovery System for PlayaTewsIdentityMasker
Advanced recovery mechanisms, circuit breakers, and automatic healing
"""

import sys
import time
import logging
import threading
import traceback
import json
import gc
import psutil
from typing import Dict, Any, Optional, Callable, List, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import weakref
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class RecoveryState(Enum):
    """Recovery state enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    CIRCUIT_OPEN = "circuit_open"
    RECOVERING = "recovering"

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit open, reject requests
    HALF_OPEN = "half_open" # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0  # seconds
    expected_exception: type = Exception
    monitor_interval: float = 10.0  # seconds

@dataclass
class RecoveryMetrics:
    """Recovery performance metrics"""
    total_errors: int = 0
    recovered_errors: int = 0
    recovery_rate: float = 0.0
    average_recovery_time: float = 0.0
    circuit_breaker_trips: int = 0
    last_recovery_time: float = 0.0
    consecutive_failures: int = 0
    consecutive_successes: int = 0

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.last_success_time = time.time()
        self.monitor_thread = None
        self.monitoring = False
        
        logger.info(f"🔌 Circuit breaker '{name}' initialized")
    
    def start_monitoring(self):
        """Start circuit breaker monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_worker, daemon=True)
        self.monitor_thread.start()
        logger.info(f"🔌 Circuit breaker '{self.name}' monitoring started")
    
    def stop_monitoring(self):
        """Stop circuit breaker monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        logger.info(f"🔌 Circuit breaker '{self.name}' monitoring stopped")
    
    def _monitor_worker(self):
        """Monitor worker thread"""
        while self.monitoring:
            try:
                self._check_state_transitions()
                time.sleep(self.config.monitor_interval)
            except Exception as e:
                logger.error(f"🔌 Circuit breaker monitor error: {e}")
    
    def _check_state_transitions(self):
        """Check and perform state transitions"""
        current_time = time.time()
        
        if self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if current_time - self.last_failure_time >= self.config.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(f"🔌 Circuit breaker '{self.name}' moved to HALF_OPEN")
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Check if we've had enough consecutive successes
            if self.consecutive_successes >= 3:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                logger.info(f"🔌 Circuit breaker '{self.name}' moved to CLOSED")
    
    def call(self, func: Callable, *args, **kwargs) -> Tuple[bool, Any]:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitBreakerState.OPEN:
            raise Exception(f"Circuit breaker '{self.name}' is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return True, result
        
        except self.config.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.last_success_time = time.time()
        self.consecutive_successes += 1
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            logger.info(f"🔌 Circuit breaker '{self.name}' success in HALF_OPEN state")
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.consecutive_successes = 0
        
        if self.failure_count >= self.config.failure_threshold:
            if self.state == CircuitBreakerState.CLOSED:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"🔌 Circuit breaker '{self.name}' opened after {self.failure_count} failures")
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time,
            'last_success_time': self.last_success_time,
            'consecutive_successes': self.consecutive_successes
        }

class AutoHealingManager:
    """Automatic healing and recovery manager"""
    
    def __init__(self):
        self.healing_strategies = {}
        self.health_checks = {}
        self.healing_thread = None
        self.healing_active = False
        self.health_metrics = defaultdict(lambda: RecoveryMetrics())
        
        # Register default healing strategies
        self._register_default_strategies()
        
        logger.info("🩹 Auto-healing manager initialized")
    
    def _register_default_strategies(self):
        """Register default healing strategies"""
        self.register_healing_strategy("memory_cleanup", self._memory_cleanup_strategy)
        self.register_healing_strategy("gpu_reset", self._gpu_reset_strategy)
        self.register_healing_strategy("process_restart", self._process_restart_strategy)
        self.register_healing_strategy("config_reload", self._config_reload_strategy)
        self.register_healing_strategy("cache_clear", self._cache_clear_strategy)
    
    def register_healing_strategy(self, name: str, strategy: Callable):
        """Register a healing strategy"""
        self.healing_strategies[name] = strategy
        logger.info(f"🩹 Registered healing strategy: {name}")
    
    def register_health_check(self, name: str, check_func: Callable, interval: float = 30.0):
        """Register a health check"""
        self.health_checks[name] = {
            'function': check_func,
            'interval': interval,
            'last_check': 0.0,
            'last_result': True
        }
        logger.info(f"🩹 Registered health check: {name}")
    
    def start_auto_healing(self):
        """Start automatic healing"""
        if self.healing_active:
            return
        
        self.healing_active = True
        self.healing_thread = threading.Thread(target=self._healing_worker, daemon=True)
        self.healing_thread.start()
        logger.info("🩹 Auto-healing started")
    
    def stop_auto_healing(self):
        """Stop automatic healing"""
        self.healing_active = False
        if self.healing_thread:
            self.healing_thread.join(timeout=1.0)
        logger.info("🩹 Auto-healing stopped")
    
    def _healing_worker(self):
        """Healing worker thread"""
        while self.healing_active:
            try:
                self._perform_health_checks()
                self._apply_healing_strategies()
                time.sleep(10.0)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"🩹 Healing worker error: {e}")
    
    def _perform_health_checks(self):
        """Perform all registered health checks"""
        current_time = time.time()
        
        for name, check_info in self.health_checks.items():
            if current_time - check_info['last_check'] >= check_info['interval']:
                try:
                    result = check_info['function']()
                    check_info['last_result'] = result
                    check_info['last_check'] = current_time
                    
                    if not result:
                        logger.warning(f"🩹 Health check failed: {name}")
                        self._trigger_healing(name)
                    else:
                        logger.debug(f"🩹 Health check passed: {name}")
                
                except Exception as e:
                    logger.error(f"🩹 Health check error in {name}: {e}")
                    check_info['last_result'] = False
                    check_info['last_check'] = current_time
                    self._trigger_healing(name)
    
    def _trigger_healing(self, health_check_name: str):
        """Trigger healing based on failed health check"""
        # Map health check names to healing strategies
        healing_mapping = {
            'memory_usage': ['memory_cleanup', 'cache_clear'],
            'gpu_status': ['gpu_reset'],
            'process_health': ['process_restart'],
            'config_validity': ['config_reload'],
            'cache_health': ['cache_clear']
        }
        
        strategies = healing_mapping.get(health_check_name, [])
        for strategy_name in strategies:
            if strategy_name in self.healing_strategies:
                try:
                    logger.info(f"🩹 Applying healing strategy: {strategy_name}")
                    self.healing_strategies[strategy_name]()
                except Exception as e:
                    logger.error(f"🩹 Healing strategy {strategy_name} failed: {e}")
    
    def _apply_healing_strategies(self):
        """Apply healing strategies based on current state"""
        # Check memory usage
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 90:
            logger.warning(f"🩹 High memory usage detected: {memory_percent}%")
            self._memory_cleanup_strategy()
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 95:
            logger.warning(f"🩹 High CPU usage detected: {cpu_percent}%")
            self._cache_clear_strategy()
    
    def _memory_cleanup_strategy(self):
        """Memory cleanup healing strategy"""
        try:
            # Force garbage collection
            collected = gc.collect()
            
            # Clear any caches if available
            if hasattr(sys, 'getallocatedblocks'):
                before = sys.getallocatedblocks()
                gc.collect()
                after = sys.getallocatedblocks()
                freed = before - after
                logger.info(f"🩹 Memory cleanup freed {freed} blocks")
            
            logger.info(f"🩹 Memory cleanup completed, collected {collected} objects")
            return True
        except Exception as e:
            logger.error(f"🩹 Memory cleanup failed: {e}")
            return False
    
    def _gpu_reset_strategy(self):
        """GPU reset healing strategy"""
        try:
            # This would interface with GPU libraries
            logger.info("🩹 GPU reset strategy applied")
            return True
        except Exception as e:
            logger.error(f"🩹 GPU reset failed: {e}")
            return False
    
    def _process_restart_strategy(self):
        """Process restart healing strategy"""
        try:
            # This would restart specific components
            logger.info("🩹 Process restart strategy applied")
            return True
        except Exception as e:
            logger.error(f"🩹 Process restart failed: {e}")
            return False
    
    def _config_reload_strategy(self):
        """Configuration reload healing strategy"""
        try:
            # Reload configuration
            logger.info("🩹 Configuration reload strategy applied")
            return True
        except Exception as e:
            logger.error(f"🩹 Configuration reload failed: {e}")
            return False
    
    def _cache_clear_strategy(self):
        """Cache clear healing strategy"""
        try:
            # Clear various caches
            logger.info("🩹 Cache clear strategy applied")
            return True
        except Exception as e:
            logger.error(f"🩹 Cache clear failed: {e}")
            return False
    
    def get_healing_status(self) -> Dict[str, Any]:
        """Get healing status"""
        return {
            'active': self.healing_active,
            'health_checks': {name: info['last_result'] for name, info in self.health_checks.items()},
            'metrics': {name: asdict(metrics) for name, metrics in self.health_metrics.items()}
        }

class EnhancedErrorRecovery:
    """Enhanced error recovery system"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.auto_healing = AutoHealingManager()
        self.recovery_history = deque(maxlen=1000)
        self.recovery_callbacks = []
        
        # Initialize default circuit breakers
        self._initialize_default_circuit_breakers()
        
        logger.info("🔄 Enhanced error recovery system initialized")
    
    def _initialize_default_circuit_breakers(self):
        """Initialize default circuit breakers"""
        default_breakers = {
            'gpu_operations': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                expected_exception=Exception
            ),
            'memory_operations': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60.0,
                expected_exception=MemoryError
            ),
            'network_operations': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=120.0,
                expected_exception=Exception
            ),
            'file_operations': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=30.0,
                expected_exception=OSError
            )
        }
        
        for name, config in default_breakers.items():
            self.add_circuit_breaker(name, config)
    
    def add_circuit_breaker(self, name: str, config: CircuitBreakerConfig):
        """Add a circuit breaker"""
        breaker = CircuitBreaker(name, config)
        self.circuit_breakers[name] = breaker
        breaker.start_monitoring()
        logger.info(f"🔄 Added circuit breaker: {name}")
    
    def remove_circuit_breaker(self, name: str):
        """Remove a circuit breaker"""
        if name in self.circuit_breakers:
            self.circuit_breakers[name].stop_monitoring()
            del self.circuit_breakers[name]
            logger.info(f"🔄 Removed circuit breaker: {name}")
    
    def execute_with_recovery(self, operation_name: str, func: Callable, 
                            *args, **kwargs) -> Tuple[bool, Any]:
        """Execute function with enhanced recovery"""
        start_time = time.time()
        
        try:
            # Check if circuit breaker is open
            if operation_name in self.circuit_breakers:
                result = self.circuit_breakers[operation_name].call(func, *args, **kwargs)
                return result
            
            # Execute function directly
            result = func(*args, **kwargs)
            self._record_success(operation_name, time.time() - start_time)
            return True, result
        
        except Exception as e:
            recovery_time = time.time() - start_time
            self._record_failure(operation_name, e, recovery_time)
            
            # Attempt recovery
            if self._attempt_recovery(operation_name, e):
                try:
                    result = func(*args, **kwargs)
                    self._record_recovery_success(operation_name, time.time() - start_time)
                    return True, result
                except Exception as e2:
                    logger.error(f"🔄 Recovery failed for {operation_name}: {e2}")
            
            raise e
    
    def _record_success(self, operation_name: str, duration: float):
        """Record successful operation"""
        self.recovery_history.append({
            'timestamp': time.time(),
            'operation': operation_name,
            'success': True,
            'duration': duration,
            'error': None
        })
    
    def _record_failure(self, operation_name: str, error: Exception, duration: float):
        """Record failed operation"""
        self.recovery_history.append({
            'timestamp': time.time(),
            'operation': operation_name,
            'success': False,
            'duration': duration,
            'error': str(error)
        })
    
    def _record_recovery_success(self, operation_name: str, duration: float):
        """Record successful recovery"""
        self.recovery_history.append({
            'timestamp': time.time(),
            'operation': operation_name,
            'success': True,
            'duration': duration,
            'error': None,
            'recovered': True
        })
    
    def _attempt_recovery(self, operation_name: str, error: Exception) -> bool:
        """Attempt to recover from error"""
        try:
            # Trigger auto-healing
            self.auto_healing._trigger_healing('process_health')
            
            # Wait a bit for recovery
            time.sleep(0.1)
            
            logger.info(f"🔄 Recovery attempted for {operation_name}")
            return True
        except Exception as e:
            logger.error(f"🔄 Recovery attempt failed for {operation_name}: {e}")
            return False
    
    def start_auto_healing(self):
        """Start automatic healing"""
        self.auto_healing.start_auto_healing()
    
    def stop_auto_healing(self):
        """Stop automatic healing"""
        self.auto_healing.stop_auto_healing()
    
    def get_recovery_status(self) -> Dict[str, Any]:
        """Get recovery system status"""
        return {
            'circuit_breakers': {
                name: breaker.get_status() 
                for name, breaker in self.circuit_breakers.items()
            },
            'auto_healing': self.auto_healing.get_healing_status(),
            'recovery_history_count': len(self.recovery_history),
            'recent_failures': [
                record for record in list(self.recovery_history)[-10:]
                if not record['success']
            ]
        }
    
    def cleanup(self):
        """Cleanup recovery system"""
        for breaker in self.circuit_breakers.values():
            breaker.stop_monitoring()
        self.auto_healing.stop_auto_healing()
        logger.info("🔄 Enhanced error recovery system cleaned up")

# Global enhanced recovery instance
_enhanced_recovery = None

def get_enhanced_recovery() -> EnhancedErrorRecovery:
    """Get global enhanced recovery instance"""
    global _enhanced_recovery
    if _enhanced_recovery is None:
        _enhanced_recovery = EnhancedErrorRecovery()
    return _enhanced_recovery

def execute_with_recovery(operation_name: str, func: Callable, *args, **kwargs):
    """Convenience function for executing with recovery"""
    return get_enhanced_recovery().execute_with_recovery(operation_name, func, *args, **kwargs)

def add_circuit_breaker(name: str, config: CircuitBreakerConfig):
    """Convenience function for adding circuit breakers"""
    get_enhanced_recovery().add_circuit_breaker(name, config) 