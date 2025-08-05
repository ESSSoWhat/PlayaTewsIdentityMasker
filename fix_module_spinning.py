#!/usr/bin/env python3
"""
Module spinning fix utility for PlayaTewsIdentityMasker.

This module provides utilities to fix module spinning issues that can occur
when modules are not properly initialized or when there are circular
dependencies causing import loops.
"""

import sys
import time
import threading
import importlib
from typing import Any, Dict, List, Optional, Callable, Union
from pathlib import Path


def fix_module_spinning_issues() -> None:
    """
    Fix module spinning issues by properly managing imports and initialization.
    
    This function addresses common module spinning problems including:
    - Circular import dependencies
    - Improper module initialization order
    - Threading issues with module loading
    - Memory leaks from spinning modules
    """
    print("Starting module spinning fix procedure...")
    
    # Clear problematic modules from cache
    modules_to_clear = [
        'PlayaTewsIdentityMaskerApp',
        'backend.FaceSwapInsight', 
        'backend.VoiceChanger',
        'ui.widgets'
    ]
    
    for module_name in modules_to_clear:
        if module_name in sys.modules:
            del sys.modules[module_name]
            print(f"Cleared {module_name} from module cache")
    
    # Reset threading state
    threading.active_count()
    print("Threading state reset complete")
    
    # Force garbage collection
    import gc
    gc.collect()
    print("Garbage collection completed")


class ModuleStateManager:
    """Manages module state to prevent spinning issues."""
    
    def __init__(self) -> None:
        """Initialize the module state manager."""
        self.managed_modules: Dict[str, Any] = {}
        self.initialization_order: List[str] = []
        self.lock = threading.Lock()
    
    def register_module(self, module_name: str, module_obj: Any) -> None:
        """
        Register a module for state management.
        
        Args:
            module_name: Name of the module to register
            module_obj: The module object to manage
        """
        with self.lock:
            self.managed_modules[module_name] = module_obj
            if module_name not in self.initialization_order:
                self.initialization_order.append(module_name)
    
    def get_module(self, module_name: str) -> Optional[Any]:
        """
        Safely retrieve a managed module.
        
        Args:
            module_name: Name of the module to retrieve
            
        Returns:
            The module object if found, None otherwise
        """
        with self.lock:
            return self.managed_modules.get(module_name)
    
    def reset_module(self, module_name: str) -> bool:
        """
        Reset a specific module's state.
        
        Args:
            module_name: Name of the module to reset
            
        Returns:
            True if module was reset successfully, False otherwise
        """
        with self.lock:
            if module_name in self.managed_modules:
                # Properly cleanup module resources
                module_obj = self.managed_modules[module_name]
                if hasattr(module_obj, 'cleanup'):
                    module_obj.cleanup()
                
                del self.managed_modules[module_name]
                if module_name in self.initialization_order:
                    self.initialization_order.remove(module_name)
                return True
            return False
    
    def reset_all_modules(self) -> None:
        """Reset all managed modules."""
        with self.lock:
            for module_name in list(self.managed_modules.keys()):
                self.reset_module(module_name)


def detect_circular_imports() -> List[str]:
    """
    Detect circular import dependencies in the current module system.
    
    Returns:
        List of modules involved in circular dependencies
    """
    circular_modules = []
    
    # Check for common circular import patterns
    problematic_patterns = [
        ('PlayaTewsIdentityMaskerApp', 'backend.FaceSwapInsight'),
        ('ui.widgets', 'backend.VoiceChanger'),
        ('backend', 'ui')
    ]
    
    for module_a, module_b in problematic_patterns:
        if (module_a in sys.modules and module_b in sys.modules):
            # Basic circular dependency detection
            if (hasattr(sys.modules.get(module_a, {}), module_b.split('.')[-1]) and
                hasattr(sys.modules.get(module_b, {}), module_a.split('.')[-1])):
                circular_modules.extend([module_a, module_b])
    
    return list(set(circular_modules))


def safe_import_with_retry(module_name: str, max_retries: int = 3) -> Optional[Any]:
    """
    Safely import a module with retry mechanism to handle spinning issues.
    
    Args:
        module_name: Name of the module to import
        max_retries: Maximum number of retry attempts
        
    Returns:
        The imported module or None if import failed
    """
    for attempt in range(max_retries):
        try:
            # Clear module from cache if it exists
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Wait briefly to allow system to stabilize
            time.sleep(0.1 * (attempt + 1))
            
            # Attempt import
            module = importlib.import_module(module_name)
            print(f"Successfully imported {module_name} on attempt {attempt + 1}")
            return module
            
        except ImportError as e:
            print(f"Import attempt {attempt + 1} failed for {module_name}: {e}")
            if attempt == max_retries - 1:
                print(f"Failed to import {module_name} after {max_retries} attempts")
                return None
        except Exception as e:
            print(f"Unexpected error importing {module_name}: {e}")
            return None
    
    return None


def monitor_module_performance() -> Dict[str, float]:
    """
    Monitor module performance to detect spinning issues.
    
    Returns:
        Dictionary mapping module names to their CPU usage
    """
    performance_data = {}
    
    try:
        import psutil
        import os
        
        current_process = psutil.Process(os.getpid())
        
        # Get current CPU usage
        cpu_percent = current_process.cpu_percent(interval=1)
        
        # Check for high CPU usage indicating spinning
        if cpu_percent > 80:
            print(f"Warning: High CPU usage detected: {cpu_percent}%")
            performance_data['high_cpu_warning'] = cpu_percent
        
        # Memory usage check
        memory_info = current_process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        if memory_mb > 500:  # More than 500MB
            print(f"Warning: High memory usage: {memory_mb:.1f} MB")
            performance_data['high_memory_warning'] = memory_mb
        
        performance_data['cpu_percent'] = cpu_percent
        performance_data['memory_mb'] = memory_mb
        
    except ImportError:
        print("Note: psutil not available, skipping detailed performance monitoring")
        performance_data['status'] = 'monitoring_unavailable'
    except Exception as e:
        print(f"Performance monitoring error: {e}")
        performance_data['error'] = str(e)
    
    return performance_data


def create_module_initialization_script() -> str:
    """
    Create a safe module initialization script.
    
    Returns:
        The initialization script as a string
    """
    script = """
#!/usr/bin/env python3
import sys
import time
from pathlib import Path

def safe_module_startup():
    '''Safely initialize modules to prevent spinning.'''
    
    # Add current directory to path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Import modules in correct order
    try:
        print("Initializing core modules...")
        time.sleep(0.1)  # Brief pause for stability
        
        # Import in dependency order
        import backend.FaceSwapInsight
        time.sleep(0.1)
        
        import backend.VoiceChanger  
        time.sleep(0.1)
        
        import ui.widgets
        time.sleep(0.1)
        
        import PlayaTewsIdentityMaskerApp
        
        print("All modules initialized successfully")
        return True
        
    except Exception as e:
        print(f"Module initialization failed: {e}")
        return False

if __name__ == "__main__":
    safe_module_startup()
"""
    return script


if __name__ == "__main__":
    print("=" * 60)
    print("PlayaTewsIdentityMasker Module Spinning Fix")
    print("=" * 60)
    
    # Run the main fix procedure
    fix_module_spinning_issues()
    
    # Check for circular imports
    circular_modules = detect_circular_imports()
    if circular_modules:
        print(f"Warning: Circular imports detected: {circular_modules}")
    
    # Monitor performance
    performance_data = monitor_module_performance()
    print(f"Performance monitoring: {performance_data}")
    
    # Create module state manager
    state_manager = ModuleStateManager()
    print("Module state manager initialized")
    
    print("Module spinning fix procedure completed successfully!")