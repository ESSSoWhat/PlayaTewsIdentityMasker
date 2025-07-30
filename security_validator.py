#!/usr/bin/env python3
"""
Security Validator for PlayaTewsIdentityMasker
Comprehensive input validation, sanitization, and security checks
"""

import os
import re
import hashlib
import logging
from pathlib import Path, PurePath
from typing import Union, List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse
import json
import yaml

logger = logging.getLogger(__name__)

class SecurityValidationError(Exception):
    """Security validation error"""
    pass

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # Dangerous patterns for path traversal and command injection
    DANGEROUS_PATTERNS = [
        '..', '~', '/etc', '/var', '/proc', '/sys', '/dev',
        ';', '&', '|', '`', '$', '(', ')', '<', '>', '"', "'",
        'cmd', 'powershell', 'bash', 'sh', 'exec', 'system'
    ]
    
    # Allowed file extensions for different operations
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    ALLOWED_MODEL_EXTENSIONS = {'.dfm', '.pb', '.onnx', '.pth', '.h5', '.hdf5', '.model', '.weights', '.ckpt', '.safetensors'}
    ALLOWED_CONFIG_EXTENSIONS = {'.json', '.yaml', '.yml', '.ini', '.cfg', '.conf'}
    
    # Maximum file sizes (in bytes)
    MAX_IMAGE_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_VIDEO_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
    MAX_MODEL_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
    MAX_CONFIG_SIZE = 1 * 1024 * 1024  # 1MB
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Validate filename for security"""
        if not isinstance(filename, str) or not filename.strip():
            return False
        
        # Check for dangerous patterns
        filename_lower = filename.lower()
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if pattern in filename_lower:
                logger.warning(f"⚠️ Dangerous pattern detected in filename: {pattern}")
                return False
        
        # Check for valid filename characters
        if not re.match(r'^[a-zA-Z0-9._\-/\\]+$', filename):
            logger.warning(f"⚠️ Invalid characters in filename: {filename}")
            return False
        
        return True
    
    @staticmethod
    def validate_file_path(filepath: Union[str, Path]) -> bool:
        """Validate file path for security"""
        try:
            path = Path(filepath) if isinstance(filepath, str) else filepath
            
            # Check for path traversal attempts
            path_str = str(path).lower()
            for pattern in InputValidator.DANGEROUS_PATTERNS:
                if pattern in path_str:
                    logger.warning(f"⚠️ Path traversal attempt detected: {pattern}")
                    return False
            
            # Ensure path is within allowed directories
            allowed_dirs = [
                Path.cwd(),
                Path.home(),
                Path("./workspace"),
                Path("./userdata"),
                Path("./dfm_models"),
                Path("./models")
            ]
            
            path_resolved = path.resolve()
            is_allowed = any(path_resolved.is_relative_to(allowed_dir) for allowed_dir in allowed_dirs)
            
            if not is_allowed:
                logger.warning(f"⚠️ Path outside allowed directories: {path_resolved}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Path validation error: {e}")
            return False
    
    @staticmethod
    def validate_file_extension(filepath: Union[str, Path], allowed_extensions: set) -> bool:
        """Validate file extension"""
        try:
            path = Path(filepath) if isinstance(filepath, str) else filepath
            extension = path.suffix.lower()
            
            if extension not in allowed_extensions:
                logger.warning(f"⚠️ Disallowed file extension: {extension}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Extension validation error: {e}")
            return False
    
    @staticmethod
    def validate_file_size(filepath: Union[str, Path], max_size: int) -> bool:
        """Validate file size"""
        try:
            path = Path(filepath) if isinstance(filepath, str) else filepath
            
            if not path.exists():
                logger.warning(f"⚠️ File does not exist: {path}")
                return False
            
            file_size = path.stat().st_size
            if file_size > max_size:
                logger.warning(f"⚠️ File too large: {file_size} bytes (max: {max_size})")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ File size validation error: {e}")
            return False
    
    @staticmethod
    def sanitize_string(input_str: str) -> str:
        """Sanitize string input"""
        if not isinstance(input_str, str):
            return ""
        
        # Remove dangerous characters
        sanitized = input_str
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            sanitized = sanitized.replace(pattern, "")
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        # Limit length
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]
        
        return sanitized.strip()
    
    @staticmethod
    def validate_json_input(json_str: str) -> bool:
        """Validate JSON input"""
        try:
            # Check for dangerous patterns before parsing
            json_lower = json_str.lower()
            dangerous_json_patterns = ['__import__', 'eval', 'exec', 'open', 'file']
            
            for pattern in dangerous_json_patterns:
                if pattern in json_lower:
                    logger.warning(f"⚠️ Dangerous JSON pattern detected: {pattern}")
                    return False
            
            # Try to parse JSON
            json.loads(json_str)
            return True
            
        except Exception as e:
            logger.error(f"❌ JSON validation error: {e}")
            return False
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL for security"""
        try:
            parsed = urlparse(url)
            
            # Check for dangerous protocols
            dangerous_protocols = ['file', 'ftp', 'gopher', 'dict', 'ldap']
            if parsed.scheme.lower() in dangerous_protocols:
                logger.warning(f"⚠️ Dangerous protocol detected: {parsed.scheme}")
                return False
            
            # Check for localhost/127.0.0.1 access
            if parsed.hostname in ['localhost', '127.0.0.1', '::1']:
                logger.warning(f"⚠️ Localhost access detected: {parsed.hostname}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ URL validation error: {e}")
            return False

class ModelValidator:
    """Model file validation and security checks"""
    
    @staticmethod
    def validate_model_file(filepath: Union[str, Path]) -> Tuple[bool, str]:
        """Validate model file for security and integrity"""
        try:
            path = Path(filepath) if isinstance(filepath, str) else filepath
            
            # Basic validation
            if not InputValidator.validate_file_path(path):
                return False, "Invalid file path"
            
            if not InputValidator.validate_file_extension(path, InputValidator.ALLOWED_MODEL_EXTENSIONS):
                return False, "Invalid file extension"
            
            if not InputValidator.validate_file_size(path, InputValidator.MAX_MODEL_SIZE):
                return False, "File too large"
            
            # Check file header for known model formats
            if not ModelValidator._validate_model_header(path):
                return False, "Invalid model file header"
            
            return True, "Valid model file"
            
        except Exception as e:
            logger.error(f"❌ Model validation error: {e}")
            return False, f"Validation error: {e}"
    
    @staticmethod
    def _validate_model_header(filepath: Path) -> bool:
        """Validate model file header"""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(1024)  # Read first 1KB
            
            # Check for common model file signatures
            if filepath.suffix.lower() == '.dfm':
                # DFM files should have specific header
                return b'DFM' in header[:100]
            elif filepath.suffix.lower() == '.onnx':
                # ONNX files should start with specific bytes
                return header.startswith(b'\x08\x00')
            elif filepath.suffix.lower() == '.pth':
                # PyTorch files should have pickle signature
                return header.startswith(b'\x80\x02')
            
            return True  # Allow other formats
            
        except Exception as e:
            logger.error(f"❌ Header validation error: {e}")
            return False

class ConfigValidator:
    """Configuration validation and security checks"""
    
    @staticmethod
    def validate_config_file(filepath: Union[str, Path]) -> Tuple[bool, str]:
        """Validate configuration file"""
        try:
            path = Path(filepath) if isinstance(filepath, str) else filepath
            
            # Basic validation
            if not InputValidator.validate_file_path(path):
                return False, "Invalid file path"
            
            if not InputValidator.validate_file_extension(path, InputValidator.ALLOWED_CONFIG_EXTENSIONS):
                return False, "Invalid file extension"
            
            if not InputValidator.validate_file_size(path, InputValidator.MAX_CONFIG_SIZE):
                return False, "File too large"
            
            # Validate content based on extension
            if path.suffix.lower() in ['.json']:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not InputValidator.validate_json_input(content):
                        return False, "Invalid JSON content"
            
            return True, "Valid config file"
            
        except Exception as e:
            logger.error(f"❌ Config validation error: {e}")
            return False, f"Validation error: {e}"
    
    @staticmethod
    def validate_config_data(config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate configuration data"""
        errors = []
        
        try:
            # Check for dangerous keys
            dangerous_keys = ['__import__', 'eval', 'exec', 'open', 'file', 'system']
            for key in config_data.keys():
                if any(dangerous in str(key).lower() for dangerous in dangerous_keys):
                    errors.append(f"Dangerous key detected: {key}")
            
            # Validate paths in config
            path_keys = ['userdata_dir', 'log_file', 'model_path', 'output_path']
            for key in path_keys:
                if key in config_data:
                    value = config_data[key]
                    if isinstance(value, str) and not InputValidator.validate_file_path(value):
                        errors.append(f"Invalid path in {key}: {value}")
            
            # Validate URLs in config
            url_keys = ['api_url', 'stream_url', 'download_url']
            for key in url_keys:
                if key in config_data:
                    value = config_data[key]
                    if isinstance(value, str) and not InputValidator.validate_url(value):
                        errors.append(f"Invalid URL in {key}: {value}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"❌ Config data validation error: {e}")
            return False, [f"Validation error: {e}"]

class SecurityManager:
    """Main security manager for the application"""
    
    def __init__(self):
        self.input_validator = InputValidator()
        self.model_validator = ModelValidator()
        self.config_validator = ConfigValidator()
        self.security_log = []
    
    def validate_file_upload(self, filepath: Union[str, Path], file_type: str = "general") -> Tuple[bool, str]:
        """Validate file upload for security"""
        try:
            path = Path(filepath) if isinstance(filepath, str) else filepath
            
            # Basic validation
            if not self.input_validator.validate_file_path(path):
                return False, "Invalid file path"
            
            # Type-specific validation
            if file_type == "image":
                if not self.input_validator.validate_file_extension(path, self.input_validator.ALLOWED_IMAGE_EXTENSIONS):
                    return False, "Invalid image file extension"
                if not self.input_validator.validate_file_size(path, self.input_validator.MAX_IMAGE_SIZE):
                    return False, "Image file too large"
            
            elif file_type == "video":
                if not self.input_validator.validate_file_extension(path, self.input_validator.ALLOWED_VIDEO_EXTENSIONS):
                    return False, "Invalid video file extension"
                if not self.input_validator.validate_file_size(path, self.input_validator.MAX_VIDEO_SIZE):
                    return False, "Video file too large"
            
            elif file_type == "model":
                return self.model_validator.validate_model_file(path)
            
            elif file_type == "config":
                return self.config_validator.validate_config_file(path)
            
            return True, "File upload validated"
            
        except Exception as e:
            logger.error(f"❌ File upload validation error: {e}")
            return False, f"Validation error: {e}"
    
    def validate_user_input(self, user_input: str, input_type: str = "general") -> Tuple[bool, str]:
        """Validate user input for security"""
        try:
            # Sanitize input
            sanitized = self.input_validator.sanitize_string(user_input)
            
            if input_type == "json":
                if not self.input_validator.validate_json_input(sanitized):
                    return False, "Invalid JSON input"
            
            elif input_type == "url":
                if not self.input_validator.validate_url(sanitized):
                    return False, "Invalid URL"
            
            elif input_type == "filename":
                if not self.input_validator.validate_filename(sanitized):
                    return False, "Invalid filename"
            
            return True, sanitized
            
        except Exception as e:
            logger.error(f"❌ User input validation error: {e}")
            return False, f"Validation error: {e}"
    
    def log_security_event(self, event_type: str, details: str, severity: str = "INFO"):
        """Log security events"""
        event = {
            'timestamp': str(Path().cwd()),
            'type': event_type,
            'details': details,
            'severity': severity
        }
        self.security_log.append(event)
        logger.info(f"🔒 Security event: {event_type} - {details}")
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get security report"""
        return {
            'total_events': len(self.security_log),
            'events_by_severity': self._count_events_by_severity(),
            'recent_events': self.security_log[-10:] if self.security_log else [],
            'security_status': 'SECURE' if not self._has_critical_events() else 'WARNING'
        }
    
    def _count_events_by_severity(self) -> Dict[str, int]:
        """Count events by severity"""
        counts = {'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0}
        for event in self.security_log:
            counts[event['severity']] += 1
        return counts
    
    def _has_critical_events(self) -> bool:
        """Check if there are critical security events"""
        return any(event['severity'] in ['ERROR', 'CRITICAL'] for event in self.security_log)

# Global security manager instance
_security_manager = None

def get_security_manager() -> SecurityManager:
    """Get global security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager

def validate_input(input_data: Any, input_type: str = "general") -> Tuple[bool, str]:
    """Convenience function for input validation"""
    return get_security_manager().validate_user_input(str(input_data), input_type)

def validate_file(filepath: Union[str, Path], file_type: str = "general") -> Tuple[bool, str]:
    """Convenience function for file validation"""
    return get_security_manager().validate_file_upload(filepath, file_type) 