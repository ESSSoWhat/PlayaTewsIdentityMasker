#!/usr/bin/env python3
"""
Enhanced Configuration Manager for PlayaTewsIdentityMasker
Centralized configuration management with validation, performance monitoring, and hot-reloading
"""

import os
import json
import yaml
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, asdict, field
from enum import Enum
import weakref

logger = logging.getLogger(__name__)

class ConfigSource(Enum):
    """Configuration source types"""
    ENV = "environment"
    FILE = "file"
    DEFAULT = "default"
    RUNTIME = "runtime"

class ConfigValidationError(Exception):
    """Configuration validation error"""
    pass

@dataclass
class PerformanceConfig:
    """Performance-related configuration"""
    # GPU Settings
    gpu_memory_pool_size_mb: int = 2048
    enable_gpu_compression: bool = True
    gpu_cleanup_threshold: float = 0.8
    
    # Processing Settings
    max_processing_workers: int = 4
    frame_buffer_size: int = 5
    target_fps: float = 30.0
    enable_frame_skipping: bool = True
    
    # Memory Settings
    model_cache_size_mb: int = 512
    enable_memory_monitoring: bool = True
    memory_cleanup_interval: float = 300.0
    
    # UI Settings
    ui_target_fps: int = 60
    enable_ui_caching: bool = True
    ui_update_batching: bool = True

@dataclass
class QualityConfig:
    """Quality-related configuration"""
    # Model Settings
    model_quality: str = "balanced"  # low, balanced, high
    enable_model_optimization: bool = True
    model_precision: str = "float16"  # float16, float32
    
    # Processing Quality
    face_detection_confidence: float = 0.8
    face_landmark_quality: str = "medium"  # low, medium, high
    enable_face_enhancement: bool = True
    
    # Output Quality
    output_resolution: str = "auto"  # auto, 720p, 1080p, 4k
    output_bitrate: int = 5000  # kbps
    enable_quality_monitoring: bool = True

@dataclass
class SystemConfig:
    """System-related configuration"""
    # Hardware Detection
    auto_detect_gpu: bool = True
    preferred_gpu_provider: str = "auto"  # auto, onnx, torch, cpu
    enable_cuda_optimization: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "playatewsidentitymasker.log"
    enable_performance_logging: bool = True
    
    # Development
    enable_debug_mode: bool = False
    enable_profiling: bool = False
    enable_hot_reload: bool = False

@dataclass
class ApplicationConfig:
    """Main application configuration"""
    # Core Settings
    app_name: str = "PlayaTewsIdentityMasker"
    version: str = "1.0.0"
    userdata_dir: str = "./workspace"
    
    # Performance Configuration
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Quality Configuration
    quality: QualityConfig = field(default_factory=QualityConfig)
    
    # System Configuration
    system: SystemConfig = field(default_factory=SystemConfig)
    
    # Runtime Configuration
    _runtime_config: Dict[str, Any] = field(default_factory=dict)
    _config_sources: Dict[str, ConfigSource] = field(default_factory=dict)
    _last_modified: float = field(default_factory=time.time)

class ConfigValidator:
    """Configuration validation and sanitization"""
    
    @staticmethod
    def validate_performance_config(config: PerformanceConfig) -> List[str]:
        """Validate performance configuration"""
        errors = []
        
        if config.gpu_memory_pool_size_mb < 256:
            errors.append("GPU memory pool size must be at least 256MB")
        
        if config.gpu_memory_pool_size_mb > 16384:
            errors.append("GPU memory pool size cannot exceed 16GB")
        
        if config.gpu_cleanup_threshold < 0.1 or config.gpu_cleanup_threshold > 0.95:
            errors.append("GPU cleanup threshold must be between 0.1 and 0.95")
        
        if config.max_processing_workers < 1 or config.max_processing_workers > 16:
            errors.append("Max processing workers must be between 1 and 16")
        
        if config.frame_buffer_size < 1 or config.frame_buffer_size > 20:
            errors.append("Frame buffer size must be between 1 and 20")
        
        if config.target_fps < 1.0 or config.target_fps > 120.0:
            errors.append("Target FPS must be between 1.0 and 120.0")
        
        if config.ui_target_fps < 30 or config.ui_target_fps > 144:
            errors.append("UI target FPS must be between 30 and 144")
        
        return errors
    
    @staticmethod
    def validate_quality_config(config: QualityConfig) -> List[str]:
        """Validate quality configuration"""
        errors = []
        
        if config.model_quality not in ["low", "balanced", "high"]:
            errors.append("Model quality must be one of: low, balanced, high")
        
        if config.model_precision not in ["float16", "float32"]:
            errors.append("Model precision must be one of: float16, float32")
        
        if config.face_detection_confidence < 0.1 or config.face_detection_confidence > 1.0:
            errors.append("Face detection confidence must be between 0.1 and 1.0")
        
        if config.face_landmark_quality not in ["low", "medium", "high"]:
            errors.append("Face landmark quality must be one of: low, medium, high")
        
        if config.output_bitrate < 100 or config.output_bitrate > 50000:
            errors.append("Output bitrate must be between 100 and 50000 kbps")
        
        return errors
    
    @staticmethod
    def validate_system_config(config: SystemConfig) -> List[str]:
        """Validate system configuration"""
        errors = []
        
        if config.preferred_gpu_provider not in ["auto", "onnx", "torch", "cpu"]:
            errors.append("Preferred GPU provider must be one of: auto, onnx, torch, cpu")
        
        if config.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            errors.append("Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")
        
        return errors
    
    @staticmethod
    def sanitize_config(config: ApplicationConfig) -> ApplicationConfig:
        """Sanitize configuration values"""
        # Ensure userdata directory exists
        userdata_path = Path(config.userdata_dir)
        if not userdata_path.exists():
            try:
                userdata_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 Created userdata directory: {userdata_path}")
            except Exception as e:
                logger.warning(f"⚠️ Could not create userdata directory: {e}")
        
        # Ensure log file directory exists
        log_path = Path(config.system.log_file)
        if log_path.parent != Path("."):
            log_path.parent.mkdir(parents=True, exist_ok=True)
        
        return config

class ConfigManager:
    """Enhanced configuration manager with validation and hot-reloading"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config = ApplicationConfig()
        self.validators = ConfigValidator()
        self._lock = threading.RLock()
        self._observers: List[weakref.ref] = []
        
        # File monitoring
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._last_file_check = time.time()
        self._file_check_interval = 1.0  # Check every second
        
        # Load configuration
        self._load_config()
        
        # Start file monitoring if enabled
        if self.config.system.enable_hot_reload and self.config_file:
            self._start_file_monitoring()
    
    def _load_config(self):
        """Load configuration from multiple sources"""
        logger.info("🔧 Loading configuration...")
        
        # Load from file first
        if self.config_file:
            self._load_from_file()
        
        # Override with environment variables
        self._load_from_environment()
        
        # Validate configuration
        self._validate_config()
        
        # Sanitize configuration
        self.config = self.validators.sanitize_config(self.config)
        
        logger.info("✅ Configuration loaded successfully")
    
    def _load_from_file(self):
        """Load configuration from file"""
        if not self.config_file or not os.path.exists(self.config_file):
            logger.warning(f"⚠️ Configuration file not found: {self.config_file}")
            return
        
        try:
            file_path = Path(self.config_file)
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
            else:
                logger.warning(f"⚠️ Unsupported configuration file format: {file_path.suffix}")
                return
            
            # Update configuration from file data
            self._update_config_from_dict(data, ConfigSource.FILE)
            logger.info(f"📄 Configuration loaded from file: {self.config_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load configuration from file: {e}")
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_mappings = {
            # Performance settings
            'PTIM_GPU_MEMORY_POOL_SIZE': ('performance.gpu_memory_pool_size_mb', int),
            'PTIM_MAX_WORKERS': ('performance.max_processing_workers', int),
            'PTIM_TARGET_FPS': ('performance.target_fps', float),
            'PTIM_UI_FPS': ('performance.ui_target_fps', int),
            
            # Quality settings
            'PTIM_MODEL_QUALITY': ('quality.model_quality', str),
            'PTIM_MODEL_PRECISION': ('quality.model_precision', str),
            'PTIM_FACE_CONFIDENCE': ('quality.face_detection_confidence', float),
            
            # System settings
            'PTIM_LOG_LEVEL': ('system.log_level', str),
            'PTIM_DEBUG_MODE': ('system.enable_debug_mode', lambda x: x.lower() == 'true'),
            'PTIM_GPU_PROVIDER': ('system.preferred_gpu_provider', str),
        }
        
        for env_var, (config_path, converter) in env_mappings.items():
            if env_var in os.environ:
                try:
                    value = converter(os.environ[env_var])
                    self._set_nested_config(config_path, value, ConfigSource.ENV)
                except Exception as e:
                    logger.warning(f"⚠️ Invalid environment variable {env_var}: {e}")
    
    def _update_config_from_dict(self, data: Dict[str, Any], source: ConfigSource):
        """Update configuration from dictionary"""
        for key, value in data.items():
            if hasattr(self.config, key):
                if isinstance(value, dict) and hasattr(getattr(self.config, key), '__dict__'):
                    # Handle nested configuration objects
                    nested_obj = getattr(self.config, key)
                    for nested_key, nested_value in value.items():
                        if hasattr(nested_obj, nested_key):
                            setattr(nested_obj, nested_key, nested_value)
                            self._config_sources[f"{key}.{nested_key}"] = source
                else:
                    setattr(self.config, key, value)
                    self._config_sources[key] = source
    
    def _set_nested_config(self, path: str, value: Any, source: ConfigSource):
        """Set nested configuration value"""
        parts = path.split('.')
        obj = self.config
        
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                logger.warning(f"⚠️ Invalid configuration path: {path}")
                return
        
        if hasattr(obj, parts[-1]):
            setattr(obj, parts[-1], value)
            self._config_sources[path] = source
        else:
            logger.warning(f"⚠️ Invalid configuration path: {path}")
    
    def _validate_config(self):
        """Validate configuration and raise errors if invalid"""
        errors = []
        
        # Validate performance configuration
        perf_errors = self.validators.validate_performance_config(self.config.performance)
        errors.extend([f"Performance: {e}" for e in perf_errors])
        
        # Validate quality configuration
        qual_errors = self.validators.validate_quality_config(self.config.quality)
        errors.extend([f"Quality: {e}" for e in qual_errors])
        
        # Validate system configuration
        sys_errors = self.validators.validate_system_config(self.config.system)
        errors.extend([f"System: {e}" for e in sys_errors])
        
        if errors:
            error_msg = "\n".join(errors)
            logger.error(f"❌ Configuration validation failed:\n{error_msg}")
            raise ConfigValidationError(f"Configuration validation failed:\n{error_msg}")
    
    def get_config(self) -> ApplicationConfig:
        """Get current configuration"""
        with self._lock:
            return self.config
    
    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration"""
        return self.config.performance
    
    def get_quality_config(self) -> QualityConfig:
        """Get quality configuration"""
        return self.config.quality
    
    def get_system_config(self) -> SystemConfig:
        """Get system configuration"""
        return self.config.system
    
    def update_config(self, updates: Dict[str, Any], source: ConfigSource = ConfigSource.RUNTIME):
        """Update configuration with validation"""
        with self._lock:
            try:
                self._update_config_from_dict(updates, source)
                self._validate_config()
                self.config = self.validators.sanitize_config(self.config)
                self._notify_observers()
                logger.info(f"✅ Configuration updated from {source.value}")
            except Exception as e:
                logger.error(f"❌ Configuration update failed: {e}")
                raise
    
    def save_config(self, filepath: Optional[str] = None) -> bool:
        """Save configuration to file"""
        try:
            save_path = filepath or self.config_file
            if not save_path:
                logger.error("❌ No filepath specified for configuration save")
                return False
            
            # Convert configuration to dictionary
            config_dict = asdict(self.config)
            
            # Remove runtime-only fields
            config_dict.pop('_runtime_config', None)
            config_dict.pop('_config_sources', None)
            config_dict.pop('_last_modified', None)
            
            # Save based on file extension
            file_path = Path(save_path)
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                with open(file_path, 'w') as f:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'w') as f:
                    json.dump(config_dict, f, indent=2)
            else:
                logger.error(f"❌ Unsupported file format: {file_path.suffix}")
                return False
            
            logger.info(f"💾 Configuration saved to: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")
            return False
    
    def add_observer(self, callback: callable):
        """Add configuration change observer"""
        self._observers.append(weakref.ref(callback))
    
    def remove_observer(self, callback: callable):
        """Remove configuration change observer"""
        for i, observer in enumerate(self._observers):
            if observer() == callback:
                del self._observers[i]
                break
    
    def _notify_observers(self):
        """Notify all observers of configuration changes"""
        # Clean up dead references
        self._observers = [ref for ref in self._observers if ref() is not None]
        
        # Notify observers
        for observer_ref in self._observers:
            observer = observer_ref()
            if observer:
                try:
                    observer(self.config)
                except Exception as e:
                    logger.error(f"❌ Observer notification failed: {e}")
    
    def _start_file_monitoring(self):
        """Start file monitoring for hot-reload"""
        if self._monitoring:
            return
        
        self._monitoring = True
        
        def monitor_file():
            while self._monitoring:
                try:
                    if self.config_file and os.path.exists(self.config_file):
                        current_time = time.time()
                        if current_time - self._last_file_check > self._file_check_interval:
                            file_mtime = os.path.getmtime(self.config_file)
                            if file_mtime > self.config._last_modified:
                                logger.info("🔄 Configuration file changed, reloading...")
                                self._load_config()
                                self._notify_observers()
                                self.config._last_modified = file_mtime
                            self._last_file_check = current_time
                except Exception as e:
                    logger.error(f"❌ File monitoring error: {e}")
                
                # Sleep with interruption check
                for _ in range(10):  # Check every 0.1 seconds
                    if not self._monitoring:
                        break
                    time.sleep(0.1)
        
        self._monitor_thread = threading.Thread(target=monitor_file, daemon=True)
        self._monitor_thread.start()
        logger.info("👁️ File monitoring started for hot-reload")
    
    def stop_file_monitoring(self):
        """Stop file monitoring"""
        if not self._monitoring:
            return
        
        self._monitoring = False
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2.0)
            if self._monitor_thread.is_alive():
                logger.warning("⚠️ File monitoring thread did not stop gracefully")
        
        logger.info("👁️ File monitoring stopped")
    
    def __del__(self):
        """Cleanup when config manager is destroyed"""
        self.stop_file_monitoring()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for debugging"""
        return {
            'app_name': self.config.app_name,
            'version': self.config.version,
            'userdata_dir': self.config.userdata_dir,
            'performance': {
                'gpu_memory_pool_size_mb': self.config.performance.gpu_memory_pool_size_mb,
                'max_processing_workers': self.config.performance.max_processing_workers,
                'target_fps': self.config.performance.target_fps,
                'ui_target_fps': self.config.performance.ui_target_fps,
            },
            'quality': {
                'model_quality': self.config.quality.model_quality,
                'model_precision': self.config.quality.model_precision,
                'face_detection_confidence': self.config.quality.face_detection_confidence,
            },
            'system': {
                'log_level': self.config.system.log_level,
                'enable_debug_mode': self.config.system.enable_debug_mode,
                'preferred_gpu_provider': self.config.system.preferred_gpu_provider,
            },
            'config_file': self.config_file,
            'sources': dict(self._config_sources)
        }

# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None

def get_config_manager(config_file: Optional[str] = None) -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_file)
    return _config_manager

def get_config() -> ApplicationConfig:
    """Get current configuration"""
    return get_config_manager().get_config()

def update_config(updates: Dict[str, Any], source: ConfigSource = ConfigSource.RUNTIME):
    """Update configuration"""
    get_config_manager().update_config(updates, source)

def save_config(filepath: Optional[str] = None) -> bool:
    """Save configuration to file"""
    return get_config_manager().save_config(filepath)