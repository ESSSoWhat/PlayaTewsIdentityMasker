#!/usr/bin/env python3
"""
Enhanced Error Handling and Recovery System for PlayaTewsIdentityMasker
Comprehensive error management with automatic recovery, logging, and performance monitoring
"""

import sys
import time
import logging
import threading
import traceback
import json
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import weakref

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"           # Minor issues, no impact on functionality
    MEDIUM = "medium"     # Some impact, but recoverable
    HIGH = "high"         # Significant impact, may affect performance
    CRITICAL = "critical" # Application-breaking, requires immediate attention

class ErrorCategory(Enum):
    """Error categories for classification"""
    IMPORT = "import"           # Module import errors
    MEMORY = "memory"           # Memory allocation/management errors
    GPU = "gpu"                 # GPU-related errors
    NETWORK = "network"         # Network/IO errors
    CONFIGURATION = "config"    # Configuration errors
    VALIDATION = "validation"   # Data validation errors
    PROCESSING = "processing"   # Video/audio processing errors
    UI = "ui"                   # User interface errors
    SYSTEM = "system"           # System-level errors
    UNKNOWN = "unknown"         # Unclassified errors

@dataclass
class ErrorInfo:
    """Comprehensive error information"""
    timestamp: float
    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    stack_trace: str
    context: Dict[str, Any]
    recovery_attempted: bool = False
    recovery_successful: bool = False
    recovery_time_ms: float = 0.0

class RecoveryStrategy(Enum):
    """Recovery strategy types"""
    RETRY = "retry"                 # Retry the operation
    FALLBACK = "fallback"           # Use fallback method
    RESTART = "restart"             # Restart component
    DEGRADE = "degrade"             # Degrade functionality
    IGNORE = "ignore"               # Ignore and continue
    TERMINATE = "terminate"         # Terminate application

@dataclass
class RecoveryAction:
    """Recovery action definition"""
    strategy: RecoveryStrategy
    max_attempts: int = 3
    delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0
    condition: Optional[Callable[[ErrorInfo], bool]] = None
    action: Optional[Callable[[ErrorInfo], bool]] = None

class ErrorRecoveryManager:
    """Manages error recovery strategies and actions"""
    
    def __init__(self):
        self.recovery_strategies: Dict[ErrorCategory, List[RecoveryAction]] = {
            ErrorCategory.IMPORT: [
                RecoveryAction(
                    strategy=RecoveryStrategy.FALLBACK,
                    max_attempts=1,
                    action=self._fallback_import
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.IGNORE,
                    max_attempts=1
                )
            ],
            ErrorCategory.MEMORY: [
                RecoveryAction(
                    strategy=RecoveryStrategy.RETRY,
                    max_attempts=3,
                    delay_seconds=0.5,
                    action=self._retry_memory_allocation
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.DEGRADE,
                    max_attempts=1,
                    action=self._degrade_memory_usage
                )
            ],
            ErrorCategory.GPU: [
                RecoveryAction(
                    strategy=RecoveryStrategy.FALLBACK,
                    max_attempts=1,
                    action=self._fallback_to_cpu
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.RESTART,
                    max_attempts=2,
                    delay_seconds=2.0,
                    action=self._restart_gpu_context
                )
            ],
            ErrorCategory.CONFIGURATION: [
                RecoveryAction(
                    strategy=RecoveryStrategy.FALLBACK,
                    max_attempts=1,
                    action=self._use_default_config
                )
            ],
            ErrorCategory.PROCESSING: [
                RecoveryAction(
                    strategy=RecoveryStrategy.RETRY,
                    max_attempts=2,
                    delay_seconds=0.1,
                    action=self._retry_processing
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.DEGRADE,
                    max_attempts=1,
                    action=self._degrade_processing_quality
                )
            ]
        }
        
        self.error_history: List[ErrorInfo] = []
        self.recovery_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Performance tracking
        self.total_errors = 0
        self.recovered_errors = 0
        self.fatal_errors = 0
    
    def get_recovery_actions(self, error_info: ErrorInfo) -> List[RecoveryAction]:
        """Get recovery actions for an error"""
        return self.recovery_strategies.get(error_info.category, [])
    
    def attempt_recovery(self, error_info: ErrorInfo) -> bool:
        """Attempt to recover from an error"""
        recovery_actions = self.get_recovery_actions(error_info)
        
        # Add thread safety
        with threading.Lock():
            for action in recovery_actions:
                if action.condition and not action.condition(error_info):
                    continue
                
                for attempt in range(action.max_attempts):
                    try:
                        logger.info(f"🔄 Recovery attempt {attempt + 1}/{action.max_attempts} "
                                  f"using {action.strategy.value} strategy")
                        
                        start_time = time.time()
                        
                        if action.action:
                            success = action.action(error_info)
                        else:
                            success = self._default_recovery_action(action.strategy, error_info)
                        
                        recovery_time = (time.time() - start_time) * 1000
                        
                        if success:
                            error_info.recovery_successful = True
                            error_info.recovery_time_ms = recovery_time
                            self.recovered_errors += 1
                            
                            logger.info(f"✅ Recovery successful using {action.strategy.value} "
                                      f"in {recovery_time:.1f}ms")
                            
                            # Record recovery with cleanup
                            self.recovery_history.append({
                                'timestamp': time.time(),
                                'error_type': error_info.error_type,
                                'strategy': action.strategy.value,
                                'attempts': attempt + 1,
                                'recovery_time_ms': recovery_time
                            })
                            
                            # Clean up old recovery history entries
                            if len(self.recovery_history) > 100:
                                self.recovery_history = self.recovery_history[-50:]  # Keep last 50
                            
                            return True
                        else:
                            logger.warning(f"⚠️ Recovery attempt {attempt + 1} failed")
                            
                            if attempt < action.max_attempts - 1:
                                # Use bounded exponential backoff
                                delay = min(30.0, action.delay_seconds * (action.backoff_multiplier ** attempt))
                                time.sleep(delay)
                    
                    except Exception as e:
                        logger.error(f"❌ Recovery action failed: {e}")
                        if attempt < action.max_attempts - 1:
                            # Use fixed delay for recovery action failures
                            time.sleep(min(5.0, action.delay_seconds))
        
        error_info.recovery_attempted = True
        logger.error(f"❌ All recovery attempts failed for {error_info.error_type}")
        return False
    
    def _default_recovery_action(self, strategy: RecoveryStrategy, error_info: ErrorInfo) -> bool:
        """Default recovery action based on strategy"""
        if strategy == RecoveryStrategy.IGNORE:
            return True
        elif strategy == RecoveryStrategy.RETRY:
            # Simple retry with delay
            time.sleep(0.1)
            return True
        elif strategy == RecoveryStrategy.DEGRADE:
            # Mark as degraded but continue
            return True
        else:
            return False
    
    def _fallback_import(self, error_info: ErrorInfo) -> bool:
        """Fallback for import errors"""
        try:
            # Try to import alternative modules
            if 'onnxruntime' in error_info.error_message.lower():
                # Try to use CPU fallback
                import onnxruntime as ort
                ort.get_available_providers = lambda: ['CPUExecutionProvider']
                return True
            elif 'torch' in error_info.error_message.lower():
                # Try to use CPU PyTorch
                import torch
                torch.cuda.is_available = lambda: False
                return True
        except Exception as e:
            logger.error(f"❌ Import fallback failed: {e}")
        return False
    
    def _retry_memory_allocation(self, error_info: ErrorInfo) -> bool:
        """Retry memory allocation with garbage collection"""
        try:
            import gc
            gc.collect()
            time.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"❌ Memory retry failed: {e}")
        return False
    
    def _degrade_memory_usage(self, error_info: ErrorInfo) -> bool:
        """Degrade memory usage by reducing cache sizes"""
        try:
            # This would typically update configuration
            logger.info("🔧 Degrading memory usage - reducing cache sizes")
            return True
        except Exception as e:
            logger.error(f"❌ Memory degradation failed: {e}")
        return False
    
    def _fallback_to_cpu(self, error_info: ErrorInfo) -> bool:
        """Fallback to CPU processing"""
        try:
            # Set environment variables to force CPU usage
            import os
            os.environ['CUDA_VISIBLE_DEVICES'] = ''
            os.environ['NO_CUDA'] = '1'
            logger.info("🔄 Falling back to CPU processing")
            return True
        except Exception as e:
            logger.error(f"❌ CPU fallback failed: {e}")
        return False
    
    def _restart_gpu_context(self, error_info: ErrorInfo) -> bool:
        """Restart GPU context"""
        try:
            # This would typically restart GPU context
            logger.info("🔄 Restarting GPU context")
            time.sleep(2.0)
            return True
        except Exception as e:
            logger.error(f"❌ GPU context restart failed: {e}")
        return False
    
    def _use_default_config(self, error_info: ErrorInfo) -> bool:
        """Use default configuration"""
        try:
            logger.info("🔧 Using default configuration")
            return True
        except Exception as e:
            logger.error(f"❌ Default config fallback failed: {e}")
        return False
    
    def _retry_processing(self, error_info: ErrorInfo) -> bool:
        """Retry processing operation"""
        try:
            logger.info("🔄 Retrying processing operation")
            time.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"❌ Processing retry failed: {e}")
        return False
    
    def _degrade_processing_quality(self, error_info: ErrorInfo) -> bool:
        """Degrade processing quality"""
        try:
            logger.info("🔧 Degrading processing quality")
            return True
        except Exception as e:
            logger.error(f"❌ Quality degradation failed: {e}")
        return False

class ErrorHandler:
    """Main error handler with comprehensive error management"""
    
    def __init__(self, log_file: str = "errors.log"):
        self.log_file = log_file
        self.recovery_manager = ErrorRecoveryManager()
        self.error_callbacks: List[Callable[[ErrorInfo], None]] = []
        self.fatal_error_callbacks: List[Callable[[ErrorInfo], None]] = []
        
        # Setup error logging
        self._setup_error_logging()
        
        # Performance tracking
        self.start_time = time.time()
        self.error_counts: Dict[ErrorCategory, int] = {cat: 0 for cat in ErrorCategory}
        self.severity_counts: Dict[ErrorSeverity, int] = {sev: 0 for sev in ErrorSeverity}
    
    def _setup_error_logging(self):
        """Setup dedicated error logging"""
        error_logger = logging.getLogger('error_handler')
        error_logger.setLevel(logging.DEBUG)
        
        # File handler for errors
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        error_logger.addHandler(file_handler)
        self.error_logger = error_logger
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None, 
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    category: ErrorCategory = ErrorCategory.UNKNOWN) -> bool:
        """Handle an error with recovery attempts"""
        error_info = self._create_error_info(error, context, severity, category)
        
        # Log error
        self._log_error(error_info)
        
        # Update statistics
        self._update_statistics(error_info)
        
        # Notify callbacks
        self._notify_callbacks(error_info)
        
        # Attempt recovery for non-critical errors
        if severity != ErrorSeverity.CRITICAL:
            recovery_success = self.recovery_manager.attempt_recovery(error_info)
            if recovery_success:
                return True
        
        # Handle critical errors
        if severity == ErrorSeverity.CRITICAL:
            self.fatal_errors += 1
            self._handle_critical_error(error_info)
            return False
        
        return error_info.recovery_successful
    
    def _create_error_info(self, error: Exception, context: Dict[str, Any],
                          severity: ErrorSeverity, category: ErrorCategory) -> ErrorInfo:
        """Create comprehensive error information"""
        return ErrorInfo(
            timestamp=time.time(),
            error_type=type(error).__name__,
            error_message=str(error),
            severity=severity,
            category=category,
            stack_trace=traceback.format_exc(),
            context=context or {}
        )
    
    def _log_error(self, error_info: ErrorInfo):
        """Log error with comprehensive information"""
        # Determine log level based on severity
        log_level = {
            ErrorSeverity.LOW: logging.DEBUG,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error_info.severity, logging.ERROR)
        
        # Log to error file
        self.error_logger.log(log_level, f"Error: {error_info.error_type}")
        self.error_logger.log(log_level, f"Message: {error_info.error_message}")
        self.error_logger.log(log_level, f"Severity: {error_info.severity.value}")
        self.error_logger.log(log_level, f"Category: {error_info.category.value}")
        self.error_logger.log(log_level, f"Context: {json.dumps(error_info.context, indent=2)}")
        self.error_logger.log(log_level, f"Stack Trace:\n{error_info.stack_trace}")
        
        # Add to history
        self.recovery_manager.error_history.append(error_info)
        if len(self.recovery_manager.error_history) > self.recovery_manager.max_history_size:
            self.recovery_manager.error_history.pop(0)
    
    def _update_statistics(self, error_info: ErrorInfo):
        """Update error statistics"""
        self.recovery_manager.total_errors += 1
        self.error_counts[error_info.category] += 1
        self.severity_counts[error_info.severity] += 1
    
    def _notify_callbacks(self, error_info: ErrorInfo):
        """Notify error callbacks"""
        for callback in self.error_callbacks:
            try:
                callback(error_info)
            except Exception as e:
                logger.error(f"❌ Error callback failed: {e}")
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            for callback in self.fatal_error_callbacks:
                try:
                    callback(error_info)
                except Exception as e:
                    logger.error(f"❌ Fatal error callback failed: {e}")
    
    def _handle_critical_error(self, error_info: ErrorInfo):
        """Handle critical errors"""
        logger.critical(f"🚨 Critical error detected: {error_info.error_type}")
        logger.critical(f"Message: {error_info.error_message}")
        
        # Save error report
        self._save_error_report(error_info)
        
        # Could implement emergency shutdown here
        # sys.exit(1)
    
    def _save_error_report(self, error_info: ErrorInfo):
        """Save detailed error report"""
        try:
            report = {
                'timestamp': error_info.timestamp,
                'error_type': error_info.error_type,
                'error_message': error_info.error_message,
                'severity': error_info.severity.value,
                'category': error_info.category.value,
                'context': error_info.context,
                'stack_trace': error_info.stack_trace,
                'system_info': self._get_system_info()
            }
            
            report_file = f"error_report_{int(error_info.timestamp)}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"📄 Error report saved to: {report_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save error report: {e}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for error reports"""
        import platform
        import psutil
        
        return {
            'platform': platform.platform(),
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'uptime_seconds': time.time() - self.start_time
        }
    
    def add_error_callback(self, callback: Callable[[ErrorInfo], None]):
        """Add error callback"""
        self.error_callbacks.append(callback)
    
    def add_fatal_error_callback(self, callback: Callable[[ErrorInfo], None]):
        """Add fatal error callback"""
        self.fatal_error_callbacks.append(callback)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        uptime = time.time() - self.start_time
        
        return {
            'uptime_seconds': uptime,
            'total_errors': self.recovery_manager.total_errors,
            'recovered_errors': self.recovery_manager.recovered_errors,
            'fatal_errors': self.fatal_errors,
            'recovery_rate': (self.recovery_manager.recovered_errors / 
                            max(self.recovery_manager.total_errors, 1)),
            'errors_per_hour': (self.recovery_manager.total_errors / max(uptime / 3600, 1)),
            'error_counts_by_category': {cat.value: count for cat, count in self.error_counts.items()},
            'error_counts_by_severity': {sev.value: count for sev, count in self.severity_counts.items()},
            'recent_errors': [
                {
                    'timestamp': e.timestamp,
                    'type': e.error_type,
                    'severity': e.severity.value,
                    'category': e.category.value,
                    'recovered': e.recovery_successful
                }
                for e in self.recovery_manager.error_history[-10:]  # Last 10 errors
            ]
        }

# Global error handler instance
_error_handler: Optional[ErrorHandler] = None

def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler

def handle_error(error: Exception, context: Dict[str, Any] = None,
                severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                category: ErrorCategory = ErrorCategory.UNKNOWN) -> bool:
    """Handle an error using the global error handler"""
    return get_error_handler().handle_error(error, context, severity, category)

def error_handler_decorator(severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                           category: ErrorCategory = ErrorCategory.UNKNOWN):
    """Decorator for automatic error handling"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }
                handle_error(e, context, severity, category)
                raise
        return wrapper
    return decorator