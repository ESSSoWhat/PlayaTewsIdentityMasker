"""
Structured Logging for MLOps Best Practices

This module provides structured logging utilities with:
- JSON-formatted logs
- Correlation IDs for request tracing
- Log level configuration
- Log rotation and retention
- Integration with monitoring systems
"""

import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from pythonjsonlogger import jsonlogger


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None,
    correlation_id: Optional[str] = None
) -> None:
    """
    Setup structured logging with correlation IDs
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json, text)
        log_file: Optional log file path
        correlation_id: Optional correlation ID for request tracing
    """
    try:
        # Set correlation ID if provided
        if correlation_id:
            structlog.contextvars.clear_contextvars()
            structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        
        # Configure structlog processors
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]
        
        # Add correlation ID processor
        processors.insert(0, structlog.contextvars.merge_contextvars)
        
        # Add output formatting
        if log_format.lower() == "json":
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())
        
        # Configure structlog
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Configure standard library logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, log_level.upper())
        )
        
        # Add file handler if specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level.upper()))
            
            # Use JSON formatter for file logging
            formatter = jsonlogger.JsonFormatter(
                fmt='%(timestamp)s %(level)s %(name)s %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            logging.getLogger().addHandler(file_handler)
        
        logger = structlog.get_logger()
        logger.info("Logging setup completed", 
                   log_level=log_level,
                   log_format=log_format,
                   log_file=log_file)
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        # Fallback to basic logging
        logging.basicConfig(level=logging.INFO)


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name
        
    Returns:
        structlog.BoundLogger: Structured logger instance
    """
    return structlog.get_logger(name)


def set_correlation_id(correlation_id: str) -> None:
    """
    Set correlation ID for current context
    
    Args:
        correlation_id: Correlation ID for request tracing
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)


def get_correlation_id() -> Optional[str]:
    """
    Get current correlation ID
    
    Returns:
        Optional[str]: Current correlation ID
    """
    try:
        return structlog.contextvars.get_contextvars().get('correlation_id')
    except:
        return None


def generate_correlation_id() -> str:
    """
    Generate a new correlation ID
    
    Returns:
        str: New correlation ID
    """
    return str(uuid.uuid4())


class CorrelationIdMiddleware:
    """Middleware to automatically add correlation IDs to requests"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # Generate correlation ID for each request
        correlation_id = generate_correlation_id()
        set_correlation_id(correlation_id)
        
        # Add correlation ID to environment
        environ['HTTP_X_CORRELATION_ID'] = correlation_id
        
        def custom_start_response(status, headers, exc_info=None):
            headers.append(('X-Correlation-ID', correlation_id))
            return start_response(status, headers, exc_info)
        
        return self.app(environ, custom_start_response)


class StructuredLogger:
    """
    Enhanced structured logger with additional utilities
    """
    
    def __init__(self, name: str = None):
        self.logger = get_logger(name)
        self.correlation_id = get_correlation_id()
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        self.logger.info(message, correlation_id=self.correlation_id, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data"""
        self.logger.warning(message, correlation_id=self.correlation_id, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with structured data"""
        self.logger.error(message, correlation_id=self.correlation_id, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data"""
        self.logger.debug(message, correlation_id=self.correlation_id, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with structured data"""
        self.logger.critical(message, correlation_id=self.correlation_id, **kwargs)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        self.logger.info(
            "Performance measurement",
            operation=operation,
            duration=duration,
            correlation_id=self.correlation_id,
            **kwargs
        )
    
    def log_prediction(self, model_version: str, features: list, prediction: Any, **kwargs):
        """Log model prediction"""
        self.logger.info(
            "Model prediction",
            model_version=model_version,
            features=features,
            prediction=prediction,
            correlation_id=self.correlation_id,
            **kwargs
        )
    
    def log_data_quality(self, data_path: str, quality_metrics: Dict, **kwargs):
        """Log data quality metrics"""
        self.logger.info(
            "Data quality check",
            data_path=data_path,
            quality_metrics=quality_metrics,
            correlation_id=self.correlation_id,
            **kwargs
        )


def log_function_call(func):
    """Decorator to log function calls with timing"""
    def wrapper(*args, **kwargs):
        logger = get_logger()
        func_name = func.__name__
        
        logger.info("Function call started", function=func_name)
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info("Function call completed", 
                       function=func_name,
                       duration=duration,
                       success=True)
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.error("Function call failed", 
                        function=func_name,
                        duration=duration,
                        error=str(e),
                        success=False)
            
            raise
    
    return wrapper


def log_pipeline_step(step_name: str):
    """Decorator to log pipeline step execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger()
            
            logger.info("Pipeline step started", step=step_name)
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                
                logger.info("Pipeline step completed", 
                           step=step_name,
                           duration=duration,
                           success=True)
                
                return result
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                
                logger.error("Pipeline step failed", 
                            step=step_name,
                            duration=duration,
                            error=str(e),
                            success=False)
                
                raise
        
        return wrapper
    return decorator


def configure_log_rotation(
    log_file: str,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Configure log rotation for file logging
    
    Args:
        log_file: Log file path
        max_bytes: Maximum file size before rotation
        backup_count: Number of backup files to keep
    """
    try:
        from logging.handlers import RotatingFileHandler
        
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler
        handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        
        # Use JSON formatter
        formatter = jsonlogger.JsonFormatter(
            fmt='%(timestamp)s %(level)s %(name)s %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add to root logger
        logging.getLogger().addHandler(handler)
        
        logger = get_logger()
        logger.info("Log rotation configured", 
                   log_file=log_file,
                   max_bytes=max_bytes,
                   backup_count=backup_count)
        
    except Exception as e:
        print(f"Failed to configure log rotation: {e}")


def log_exception(logger: structlog.BoundLogger, exception: Exception, context: Dict = None):
    """
    Log exception with full context
    
    Args:
        logger: Logger instance
        exception: Exception to log
        context: Additional context
    """
    try:
        import traceback
        
        error_context = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc(),
            "correlation_id": get_correlation_id()
        }
        
        if context:
            error_context.update(context)
        
        logger.error("Exception occurred", **error_context)
        
    except Exception as e:
        print(f"Failed to log exception: {e}")


# Initialize default logging
if not logging.getLogger().handlers:
    setup_logging()