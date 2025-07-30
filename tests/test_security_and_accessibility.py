#!/usr/bin/env python3
"""
Test suite for Security Validation and Accessibility Features
Comprehensive testing of security hardening and accessibility improvements
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Import the modules we're testing
from security_validator import (
    SecurityManager, InputValidator, ModelValidator, ConfigValidator,
    validate_input, validate_file, get_security_manager
)
from accessibility_manager import (
    AccessibilityManager, CircuitBreaker, AutoHealingManager,
    get_accessibility_manager, announce, register_focusable_element
)
from enhanced_error_recovery import (
    EnhancedErrorRecovery, CircuitBreakerConfig, RecoveryState,
    get_enhanced_recovery, execute_with_recovery
)

class TestSecurityValidation:
    """Test security validation functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.security_manager = SecurityManager()
        self.input_validator = InputValidator()
    
    def test_validate_filename_safe(self):
        """Test safe filename validation"""
        safe_filenames = [
            "test.jpg",
            "my_video.mp4",
            "model.dfm",
            "config.json",
            "file_with_underscores.txt"
        ]
        
        for filename in safe_filenames:
            assert self.input_validator.validate_filename(filename), f"Safe filename rejected: {filename}"
    
    def test_validate_filename_dangerous(self):
        """Test dangerous filename validation"""
        dangerous_filenames = [
            "../../../etc/passwd",
            "file;rm -rf /",
            "script.sh",
            "cmd.exe",
            "file with spaces and ..",
            "~/.bashrc"
        ]
        
        for filename in dangerous_filenames:
            assert not self.input_validator.validate_filename(filename), f"Dangerous filename accepted: {filename}"
    
    def test_validate_file_path_safe(self):
        """Test safe file path validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            safe_paths = [
                Path(temp_dir) / "test.jpg",
                Path(temp_dir) / "subdir" / "file.txt",
                Path.cwd() / "workspace" / "config.json"
            ]
            
            for path in safe_paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
                assert self.input_validator.validate_file_path(path), f"Safe path rejected: {path}"
    
    def test_validate_file_path_dangerous(self):
        """Test dangerous file path validation"""
        dangerous_paths = [
            "/etc/passwd",
            "/var/log/system.log",
            "/proc/self/environ",
            "~/.ssh/id_rsa",
            "../../../etc/shadow"
        ]
        
        for path_str in dangerous_paths:
            assert not self.input_validator.validate_file_path(path_str), f"Dangerous path accepted: {path_str}"
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        dangerous_inputs = [
            ("test;rm -rf /", "testrm -rf /"),
            ("file<script>alert('xss')</script>", "filealert('xss')"),
            ("path/../etc/passwd", "path/etc/passwd"),
            ("normal text", "normal text"),
            ("", "")
        ]
        
        for input_str, expected in dangerous_inputs:
            result = self.input_validator.sanitize_string(input_str)
            assert result == expected, f"Sanitization failed: {input_str} -> {result}"
    
    def test_validate_json_input_safe(self):
        """Test safe JSON input validation"""
        safe_json_inputs = [
            '{"name": "test", "value": 123}',
            '{"config": {"enabled": true}}',
            '{"array": [1, 2, 3]}'
        ]
        
        for json_str in safe_json_inputs:
            assert self.input_validator.validate_json_input(json_str), f"Safe JSON rejected: {json_str}"
    
    def test_validate_json_input_dangerous(self):
        """Test dangerous JSON input validation"""
        dangerous_json_inputs = [
            '{"__import__": "os"}',
            '{"eval": "print(\'hello\')"}',
            '{"exec": "import os"}',
            '{"open": "/etc/passwd"}'
        ]
        
        for json_str in dangerous_json_inputs:
            assert not self.input_validator.validate_json_input(json_str), f"Dangerous JSON accepted: {json_str}"
    
    def test_validate_url_safe(self):
        """Test safe URL validation"""
        safe_urls = [
            "https://example.com",
            "http://api.github.com",
            "https://www.google.com/search?q=test"
        ]
        
        for url in safe_urls:
            assert self.input_validator.validate_url(url), f"Safe URL rejected: {url}"
    
    def test_validate_url_dangerous(self):
        """Test dangerous URL validation"""
        dangerous_urls = [
            "file:///etc/passwd",
            "ftp://malicious.com",
            "http://localhost:8080",
            "http://127.0.0.1/admin"
        ]
        
        for url in dangerous_urls:
            assert not self.input_validator.validate_url(url), f"Dangerous URL accepted: {url}"
    
    def test_model_validation(self):
        """Test model file validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock DFM file
            dfm_file = Path(temp_dir) / "test.dfm"
            with open(dfm_file, 'wb') as f:
                f.write(b'DFM\x00\x01\x02\x03')  # Mock DFM header
            
            success, message = ModelValidator.validate_model_file(dfm_file)
            assert success, f"Valid model file rejected: {message}"
    
    def test_config_validation(self):
        """Test configuration validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a valid config file
            config_file = Path(temp_dir) / "config.json"
            config_data = {"setting1": "value1", "setting2": 123}
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f)
            
            success, message = ConfigValidator.validate_config_file(config_file)
            assert success, f"Valid config file rejected: {message}"
    
    def test_security_manager_file_upload(self):
        """Test security manager file upload validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test image file
            image_file = Path(temp_dir) / "test.jpg"
            image_file.touch()
            
            success, message = self.security_manager.validate_file_upload(image_file, "image")
            assert success, f"Valid image file rejected: {message}"
    
    def test_security_manager_user_input(self):
        """Test security manager user input validation"""
        # Test safe input
        success, sanitized = self.security_manager.validate_user_input("normal text", "general")
        assert success, "Safe input rejected"
        assert sanitized == "normal text"
        
        # Test dangerous input
        success, sanitized = self.security_manager.validate_user_input("test;rm -rf /", "general")
        assert success, "Input should be sanitized"
        assert ";" not in sanitized, "Dangerous character not sanitized"

class TestAccessibilityManager:
    """Test accessibility manager functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.accessibility_manager = AccessibilityManager()
    
    def test_announce(self):
        """Test announcement functionality"""
        test_message = "Test announcement"
        self.accessibility_manager.announce(test_message)
        
        # Check if message was added to queue
        assert len(self.accessibility_manager.screen_reader_queue) == 1
        assert self.accessibility_manager.screen_reader_queue[0]['message'] == test_message
    
    def test_register_focusable_element(self):
        """Test focusable element registration"""
        element_id = "test_button"
        element_type = "button"
        description = "Test button for accessibility"
        
        self.accessibility_manager.register_focusable_element(element_id, element_type, description)
        
        # Check if element was registered
        assert len(self.accessibility_manager.focusable_elements) == 1
        assert self.accessibility_manager.focusable_elements[0]['id'] == element_id
    
    def test_set_focus(self):
        """Test focus setting"""
        # Register an element
        self.accessibility_manager.register_focusable_element("test_button", "button", "Test button")
        
        # Set focus
        success = self.accessibility_manager.set_focus("test_button")
        assert success, "Focus setting failed"
        
        # Check if element is focused
        focused_element = next((e for e in self.accessibility_manager.focusable_elements if e['focused']), None)
        assert focused_element is not None
        assert focused_element['id'] == "test_button"
    
    def test_next_focus(self):
        """Test next focus navigation"""
        # Register multiple elements
        self.accessibility_manager.register_focusable_element("button1", "button", "Button 1")
        self.accessibility_manager.register_focusable_element("button2", "button", "Button 2")
        
        # Set initial focus
        self.accessibility_manager.set_focus("button1")
        
        # Move to next focus
        self.accessibility_manager.next_focus()
        
        # Check if focus moved to second element
        focused_element = next((e for e in self.accessibility_manager.focusable_elements if e['focused']), None)
        assert focused_element['id'] == "button2"
    
    def test_previous_focus(self):
        """Test previous focus navigation"""
        # Register multiple elements
        self.accessibility_manager.register_focusable_element("button1", "button", "Button 1")
        self.accessibility_manager.register_focusable_element("button2", "button", "Button 2")
        
        # Set initial focus to second element
        self.accessibility_manager.set_focus("button2")
        
        # Move to previous focus
        self.accessibility_manager.previous_focus()
        
        # Check if focus moved to first element
        focused_element = next((e for e in self.accessibility_manager.focusable_elements if e['focused']), None)
        assert focused_element['id'] == "button1"
    
    def test_toggle_high_contrast_mode(self):
        """Test high contrast mode toggle"""
        initial_state = self.accessibility_manager.high_contrast_mode
        
        self.accessibility_manager.toggle_high_contrast_mode()
        
        assert self.accessibility_manager.high_contrast_mode != initial_state
        assert self.accessibility_manager.settings['high_contrast_mode'] == self.accessibility_manager.high_contrast_mode
    
    def test_toggle_large_text_mode(self):
        """Test large text mode toggle"""
        initial_state = self.accessibility_manager.large_text_mode
        
        self.accessibility_manager.toggle_large_text_mode()
        
        assert self.accessibility_manager.large_text_mode != initial_state
        assert self.accessibility_manager.settings['large_text_mode'] == self.accessibility_manager.large_text_mode
    
    def test_keyboard_event_handling(self):
        """Test keyboard event handling"""
        # Test F1 help key
        handled = self.accessibility_manager.handle_keyboard_event('F1')
        assert handled, "F1 key not handled"
        
        # Test Tab key
        handled = self.accessibility_manager.handle_keyboard_event('Tab')
        assert handled, "Tab key not handled"
        
        # Test unknown key
        handled = self.accessibility_manager.handle_keyboard_event('X')
        assert not handled, "Unknown key should not be handled"
    
    def test_get_accessibility_status(self):
        """Test accessibility status retrieval"""
        status = self.accessibility_manager.get_accessibility_status()
        
        required_keys = [
            'enabled', 'screen_reader_support', 'keyboard_navigation',
            'high_contrast_mode', 'large_text_mode', 'voice_feedback',
            'focusable_elements_count', 'current_focus_index', 'navigation_mode'
        ]
        
        for key in required_keys:
            assert key in status, f"Missing key in status: {key}"
    
    def test_cleanup(self):
        """Test accessibility manager cleanup"""
        # Start screen reader
        self.accessibility_manager.start_screen_reader()
        
        # Cleanup
        self.accessibility_manager.cleanup()
        
        # Check if screen reader stopped
        assert not self.accessibility_manager.screen_reader_running

class TestEnhancedErrorRecovery:
    """Test enhanced error recovery functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.recovery_system = EnhancedErrorRecovery()
    
    def test_circuit_breaker_creation(self):
        """Test circuit breaker creation"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0
        )
        
        self.recovery_system.add_circuit_breaker("test_breaker", config)
        
        assert "test_breaker" in self.recovery_system.circuit_breakers
        breaker = self.recovery_system.circuit_breakers["test_breaker"]
        assert breaker.name == "test_breaker"
        assert breaker.config.failure_threshold == 3
    
    def test_circuit_breaker_execution_success(self):
        """Test circuit breaker with successful execution"""
        config = CircuitBreakerConfig(failure_threshold=3)
        self.recovery_system.add_circuit_breaker("test_breaker", config)
        
        def successful_function():
            return "success"
        
        success, result = self.recovery_system.execute_with_recovery("test_breaker", successful_function)
        
        assert success
        assert result == "success"
    
    def test_circuit_breaker_execution_failure(self):
        """Test circuit breaker with failed execution"""
        config = CircuitBreakerConfig(failure_threshold=2)
        self.recovery_system.add_circuit_breaker("test_breaker", config)
        
        def failing_function():
            raise Exception("Test failure")
        
        # First failure
        with pytest.raises(Exception):
            self.recovery_system.execute_with_recovery("test_breaker", failing_function)
        
        # Second failure should open circuit
        with pytest.raises(Exception):
            self.recovery_system.execute_with_recovery("test_breaker", failing_function)
        
        # Third attempt should fail due to open circuit
        with pytest.raises(Exception) as exc_info:
            self.recovery_system.execute_with_recovery("test_breaker", failing_function)
        
        assert "Circuit breaker 'test_breaker' is OPEN" in str(exc_info.value)
    
    def test_auto_healing_registration(self):
        """Test auto-healing strategy registration"""
        def test_strategy():
            return True
        
        self.recovery_system.auto_healing.register_healing_strategy("test_strategy", test_strategy)
        
        assert "test_strategy" in self.recovery_system.auto_healing.healing_strategies
    
    def test_auto_healing_health_check(self):
        """Test auto-healing health check registration"""
        def health_check():
            return True
        
        self.recovery_system.auto_healing.register_health_check("test_check", health_check, interval=5.0)
        
        assert "test_check" in self.recovery_system.auto_healing.health_checks
        check_info = self.recovery_system.auto_healing.health_checks["test_check"]
        assert check_info['interval'] == 5.0
    
    def test_recovery_status(self):
        """Test recovery status retrieval"""
        status = self.recovery_system.get_recovery_status()
        
        required_keys = ['circuit_breakers', 'auto_healing', 'recovery_history_count']
        
        for key in required_keys:
            assert key in status, f"Missing key in recovery status: {key}"
    
    def test_cleanup(self):
        """Test recovery system cleanup"""
        # Add a circuit breaker
        config = CircuitBreakerConfig()
        self.recovery_system.add_circuit_breaker("test_breaker", config)
        
        # Start auto-healing
        self.recovery_system.start_auto_healing()
        
        # Cleanup
        self.recovery_system.cleanup()
        
        # Check if everything is cleaned up
        assert not self.recovery_system.auto_healing.healing_active

class TestIntegration:
    """Integration tests for security and accessibility features"""
    
    def test_security_with_accessibility_integration(self):
        """Test integration between security and accessibility features"""
        security_manager = get_security_manager()
        accessibility_manager = get_accessibility_manager()
        
        # Test secure input with accessibility announcement
        user_input = "test_input"
        success, sanitized = security_manager.validate_user_input(user_input, "general")
        
        assert success
        accessibility_manager.announce(f"Input validated: {sanitized}")
        
        # Check if announcement was made
        assert len(accessibility_manager.screen_reader_queue) > 0
    
    def test_error_recovery_with_accessibility(self):
        """Test error recovery with accessibility features"""
        recovery_system = get_enhanced_recovery()
        accessibility_manager = get_accessibility_manager()
        
        def failing_function():
            raise Exception("Test error")
        
        # Register accessibility callback for errors
        def error_callback(error_info):
            accessibility_manager.announce(f"Error occurred: {error_info.error_message}", priority="high")
        
        # Test error recovery with accessibility
        try:
            recovery_system.execute_with_recovery("test_operation", failing_function)
        except Exception:
            pass
        
        # Check if error was announced
        high_priority_announcements = [
            a for a in accessibility_manager.screen_reader_queue
            if a.get('priority') == 'high'
        ]
        assert len(high_priority_announcements) > 0
    
    def test_comprehensive_workflow(self):
        """Test comprehensive workflow with all features"""
        # Initialize all systems
        security_manager = get_security_manager()
        accessibility_manager = get_accessibility_manager()
        recovery_system = get_enhanced_recovery()
        
        # Simulate a complete workflow
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. Validate file upload
            test_file = Path(temp_dir) / "test.jpg"
            test_file.touch()
            
            success, message = security_manager.validate_file_upload(test_file, "image")
            assert success
            
            # 2. Announce successful validation
            accessibility_manager.announce(f"File validated: {message}")
            
            # 3. Register UI element
            accessibility_manager.register_focusable_element("upload_button", "button", "Upload file")
            
            # 4. Set focus
            accessibility_manager.set_focus("upload_button")
            
            # 5. Execute with recovery
            def upload_function():
                return "File uploaded successfully"
            
            success, result = recovery_system.execute_with_recovery("file_upload", upload_function)
            assert success
            
            # 6. Announce completion
            accessibility_manager.announce(f"Operation completed: {result}")
            
            # Verify all systems worked together
            assert len(accessibility_manager.focusable_elements) == 1
            assert len(accessibility_manager.screen_reader_queue) > 0
            assert len(recovery_system.recovery_history) > 0

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 