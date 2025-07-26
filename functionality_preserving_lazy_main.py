#!/usr/bin/env python3
"""
Functionality-Preserving Lazy Loading Main Entry Point for DeepFaceLive
Maintains ALL original functionality while adding lazy loading benefits
"""

import argparse
import os
import platform
import sys
import time
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
from enum import Enum

# Conditional import for onnxruntime
try:
    import onnxruntime
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

# Setup logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('playatewsidentitymasker_lazy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LoadingPriority(Enum):
    """Loading priority levels for components"""
    CRITICAL = 0      # Load immediately (core functionality)
    HIGH = 1          # Load early (essential features)
    MEDIUM = 2        # Load on demand (common features)
    LOW = 3           # Load when accessed (rare features)
    BACKGROUND = 4    # Load in background (optional features)

class LazyLoadingManager:
    """Manages lazy loading while preserving original functionality"""
    
    def __init__(self):
        self.components: Dict[str, Dict[str, Any]] = {}
        self.loaded_components: Dict[str, Any] = {}
        self.loading_queue: List[str] = []
        self.loading_in_progress = False
        self.background_tasks: List[asyncio.Task] = []
        
    def register_component(self, name: str, loader_func: Callable, priority: LoadingPriority = LoadingPriority.MEDIUM, 
                          dependencies: List[str] = None, auto_load: bool = False):
        """Register a component for lazy loading"""
        self.components[name] = {
            'loader': loader_func,
            'priority': priority,
            'dependencies': dependencies or [],
            'auto_load': auto_load,
            'loaded': False,
            'loading': False,
            'error': None
        }
        
        if auto_load:
            self.loading_queue.append(name)
        
        logger.info(f"Registered component: {name} (priority: {priority.name})")
    
    async def load_component(self, name: str) -> Any:
        """Load a specific component"""
        if name in self.loaded_components:
            return self.loaded_components[name]
        
        if name not in self.components:
            raise ValueError(f"Component '{name}' not registered")
        
        component_info = self.components[name]
        
        if component_info['loading']:
            # Wait for component to finish loading
            while component_info['loading']:
                await asyncio.sleep(0.1)
            return self.loaded_components.get(name)
        
        if component_info['error']:
            raise component_info['error']
        
        # Check dependencies
        for dep in component_info['dependencies']:
            await self.load_component(dep)
        
        # Load the component
        component_info['loading'] = True
        try:
            logger.info(f"Loading component: {name}")
            start_time = time.time()
            
            if asyncio.iscoroutinefunction(component_info['loader']):
                component = await component_info['loader']()
            else:
                component = component_info['loader']()
            
            load_time = time.time() - start_time
            self.loaded_components[name] = component
            component_info['loaded'] = True
            
            logger.info(f"✅ Component {name} loaded in {load_time:.2f}s")
            return component
            
        except Exception as e:
            component_info['error'] = e
            logger.error(f"❌ Failed to load component {name}: {e}")
            raise
        finally:
            component_info['loading'] = False
    
    async def load_priority_components(self, max_priority: LoadingPriority = LoadingPriority.HIGH):
        """Load all components up to a certain priority level"""
        priority_components = [
            name for name, info in self.components.items()
            if info['priority'].value <= max_priority.value and not info['loaded']
        ]
        
        if priority_components:
            logger.info(f"Loading priority components: {priority_components}")
            await asyncio.gather(*[self.load_component(name) for name in priority_components], 
                               return_exceptions=True)
    
    def get_component(self, name: str) -> Optional[Any]:
        """Get a component (load if necessary)"""
        if name in self.loaded_components:
            return self.loaded_components[name]
        return None
    
    def is_component_loaded(self, name: str) -> bool:
        """Check if a component is loaded"""
        return name in self.loaded_components
    
    def get_loading_stats(self) -> Dict[str, Any]:
        """Get loading statistics"""
        total = len(self.components)
        loaded = len(self.loaded_components)
        loading = sum(1 for info in self.components.values() if info['loading'])
        errors = sum(1 for info in self.components.values() if info['error'])
        
        return {
            'total_components': total,
            'loaded_components': loaded,
            'loading_components': loading,
            'error_components': errors,
            'load_percentage': (loaded / total * 100) if total > 0 else 0
        }

# Performance monitoring
class StartupTimer:
    """Track startup performance"""
    def __init__(self):
        self.start_time = time.time()
        self.stages = {}
    
    def mark_stage(self, stage_name: str):
        """Mark a startup stage completion"""
        self.stages[stage_name] = time.time() - self.start_time
        logger.info(f"✅ {stage_name} completed in {self.stages[stage_name]:.2f}s")
    
    def get_summary(self) -> Dict[str, float]:
        """Get startup performance summary"""
        return self.stages.copy()

# Global startup timer
startup_timer = StartupTimer()

# Lazy import optimization
def lazy_import(module_name: str, fallback: Optional[str] = None):
    """Lazy import with fallback support"""
    try:
        return __import__(module_name)
    except ImportError as e:
        if fallback:
            logger.warning(f"Failed to import {module_name}, trying {fallback}: {e}")
            try:
                return __import__(fallback)
            except ImportError as e2:
                logger.error(f"Failed to import fallback {fallback}: {e2}")
        else:
            logger.error(f"Failed to import {module_name}: {e}")
        return None

class FunctionalityPreservingLazyDeepFaceLiveApp:
    """DeepFaceLive application with lazy loading that preserves ALL original functionality"""
    
    def __init__(self, userdata_path: Path, no_cuda: bool = False, optimization_mode: str = "balanced"):
        self.userdata_path = userdata_path
        self.no_cuda = no_cuda
        self.optimization_mode = optimization_mode
        self.initialized = False
        
        # Initialize lazy loading manager
        self.lazy_manager = LazyLoadingManager()
        
        # Register all components with lazy loading
        self._register_components()
        
        logger.info(f"🚀 Initializing FunctionalityPreservingLazyDeepFaceLiveApp with userdata: {userdata_path}")
        logger.info(f"Optimization mode: {optimization_mode}")
    
    def _register_components(self):
        """Register all application components for lazy loading"""
        
        # Critical components (load immediately)
        self.lazy_manager.register_component(
            'xlib_appargs',
            self._load_xlib_appargs,
            LoadingPriority.CRITICAL,
            auto_load=True
        )
        
        # High priority components (load early)
        self.lazy_manager.register_component(
            'localization',
            self._load_localization,
            LoadingPriority.HIGH,
            auto_load=True
        )
        
        # Medium priority components (load on demand)
        self.lazy_manager.register_component(
            'playatewsidentitymasker_app',
            self._load_playatewsidentitymasker_app,
            LoadingPriority.MEDIUM,
            dependencies=['xlib_appargs', 'localization']
        )
        
        self.lazy_manager.register_component(
            'playatewsidentitymasker_obs_app',
            self._load_playatewsidentitymasker_obs_app,
            LoadingPriority.MEDIUM,
            dependencies=['xlib_appargs', 'localization']
        )
        
        self.lazy_manager.register_component(
            'dev_scripts',
            self._load_dev_scripts,
            LoadingPriority.LOW
        )
    
    def _load_xlib_appargs(self):
        """Load xlib.appargs module"""
        logger.info("Loading xlib.appargs module...")
        
        try:
            from xlib import appargs as lib_appargs
            logger.info("✅ xlib.appargs loaded successfully")
            return lib_appargs
        except ImportError as e:
            logger.warning(f"Could not import xlib.appargs: {e}")
            return None
    
    def _load_localization(self):
        """Load localization system"""
        logger.info("Loading localization system...")
        
        try:
            from localization import L, Localization
            logger.info("✅ Localization system loaded successfully")
            return {'L': L, 'Localization': Localization}
        except ImportError as e:
            logger.error(f"Failed to load localization: {e}")
            return None
    
    def _load_playatewsidentitymasker_app(self):
        """Load PlayaTewsIdentityMaskerApp"""
        logger.info("Loading PlayaTewsIdentityMaskerApp...")
        
        try:
            from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
            logger.info("✅ PlayaTewsIdentityMaskerApp loaded successfully")
            return PlayaTewsIdentityMaskerApp
        except ImportError as e:
            logger.error(f"Failed to load PlayaTewsIdentityMaskerApp: {e}")
            return None
    
    def _load_playatewsidentitymasker_obs_app(self):
        """Load PlayaTewsIdentityMaskerOBSStyleApp"""
        logger.info("Loading PlayaTewsIdentityMaskerOBSStyleApp...")
        
        try:
            from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerOBSStyleApp import PlayaTewsIdentityMaskerOBSStyleApp
            logger.info("✅ PlayaTewsIdentityMaskerOBSStyleApp loaded successfully")
            return PlayaTewsIdentityMaskerOBSStyleApp
        except ImportError as e:
            logger.error(f"Failed to load PlayaTewsIdentityMaskerOBSStyleApp: {e}")
            return None
    
    def _load_dev_scripts(self):
        """Load development scripts"""
        logger.info("Loading development scripts...")
        
        try:
            from scripts import dev
            logger.info("✅ Development scripts loaded successfully")
            return dev
        except ImportError as e:
            logger.error(f"Failed to load development scripts: {e}")
            return None
    
    async def initialize_async(self):
        """Initialize the application with lazy loading"""
        if self.initialized:
            return True
        
        logger.info("Starting functionality-preserving lazy loading initialization...")
        init_start_time = time.time()
        
        try:
            # Load critical and high priority components
            await self.lazy_manager.load_priority_components(LoadingPriority.HIGH)
            
            self.initialized = True
            init_time = time.time() - init_start_time
            
            # Log initialization statistics
            stats = self.lazy_manager.get_loading_stats()
            logger.info(f"✅ Functionality-preserving lazy loading initialization completed in {init_time:.2f} seconds")
            logger.info(f"Components loaded: {stats['loaded_components']}/{stats['total_components']} ({stats['load_percentage']:.1f}%)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    def run_playatewsidentitymasker(self, userdata_path: Path, no_cuda: bool = False):
        """Run PlayaTewsIdentityMasker with original functionality"""
        startup_timer.mark_stage("args_parsed")
        
        # Set CUDA environment
        if self.lazy_manager.get_component('xlib_appargs'):
            self.lazy_manager.get_component('xlib_appargs').set_arg_bool('NO_CUDA', no_cuda)
        else:
            os.environ['NO_CUDA'] = str(no_cuda).lower()
        
        logger.info(f"🚀 Starting PlayaTewsIdentityMasker with userdata: {userdata_path}")
        
        try:
            # Load the app component
            PlayaTewsIdentityMaskerApp = self.lazy_manager.get_component('playatewsidentitymasker_app')
            if not PlayaTewsIdentityMaskerApp:
                # Load it if not already loaded
                PlayaTewsIdentityMaskerApp = asyncio.run(self.lazy_manager.load_component('playatewsidentitymasker_app'))
            
            if not PlayaTewsIdentityMaskerApp:
                raise ImportError("Failed to load PlayaTewsIdentityMaskerApp")
            
            startup_timer.mark_stage("app_imported")
            
            app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
            startup_timer.mark_stage("app_created")
            
            app.run()
            startup_timer.mark_stage("app_completed")
            
            # Log startup performance
            summary = startup_timer.get_summary()
            logger.info(f"📊 Startup performance: {summary}")
            
        except ImportError as e:
            logger.error(f"❌ Failed to import PlayaTewsIdentityMaskerApp: {e}")
            logger.error("Please ensure all dependencies are installed: pip install -r requirements-unified.txt")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Application failed to start: {e}")
            sys.exit(1)
    
    def run_playatewsidentitymasker_obs(self, userdata_path: Path, no_cuda: bool = False, traditional: bool = False):
        """Run PlayaTewsIdentityMasker with OBS interface choice"""
        startup_timer.mark_stage("args_parsed")
        
        # Set CUDA environment
        if self.lazy_manager.get_component('xlib_appargs'):
            self.lazy_manager.get_component('xlib_appargs').set_arg_bool('NO_CUDA', no_cuda)
        else:
            os.environ['NO_CUDA'] = str(no_cuda).lower()
        
        if traditional:
            logger.info(f"🚀 Starting PlayaTewsIdentityMasker with traditional UI: {userdata_path}")
            self.run_playatewsidentitymasker(userdata_path, no_cuda)
        else:
            logger.info(f"🚀 Starting PlayaTewsIdentityMasker with OBS-style streaming interface: {userdata_path}")
            
            try:
                # Load the OBS app component
                PlayaTewsIdentityMaskerOBSStyleApp = self.lazy_manager.get_component('playatewsidentitymasker_obs_app')
                if not PlayaTewsIdentityMaskerOBSStyleApp:
                    # Load it if not already loaded
                    PlayaTewsIdentityMaskerOBSStyleApp = asyncio.run(self.lazy_manager.load_component('playatewsidentitymasker_obs_app'))
                
                if not PlayaTewsIdentityMaskerOBSStyleApp:
                    raise ImportError("Failed to load PlayaTewsIdentityMaskerOBSStyleApp")
                
                startup_timer.mark_stage("app_imported")
                
                app = PlayaTewsIdentityMaskerOBSStyleApp(userdata_path=userdata_path)
                startup_timer.mark_stage("app_created")
                
                app.run()
                startup_timer.mark_stage("app_completed")
                
                # Log startup performance
                summary = startup_timer.get_summary()
                logger.info(f"📊 Startup performance: {summary}")
                
            except ImportError as e:
                logger.error(f"❌ Failed to import PlayaTewsIdentityMaskerOBSStyleApp: {e}")
                logger.error("Please ensure all dependencies are installed: pip install -r requirements-unified.txt")
                sys.exit(1)
            except Exception as e:
                logger.error(f"❌ Application failed to start: {e}")
                sys.exit(1)
    
    def run_dev_split_large_files(self):
        """Run development split_large_files command"""
        try:
            dev_scripts = self.lazy_manager.get_component('dev_scripts')
            if not dev_scripts:
                dev_scripts = asyncio.run(self.lazy_manager.load_component('dev_scripts'))
            
            if dev_scripts:
                dev_scripts.split_large_files()
                logger.info("✅ Large files split successfully")
            else:
                raise ImportError("Failed to load development scripts")
        except Exception as e:
            logger.error(f"❌ Failed to split large files: {e}")
            sys.exit(1)
    
    def run_dev_merge_large_files(self, delete_parts: bool = False):
        """Run development merge_large_files command"""
        try:
            dev_scripts = self.lazy_manager.get_component('dev_scripts')
            if not dev_scripts:
                dev_scripts = asyncio.run(self.lazy_manager.load_component('dev_scripts'))
            
            if dev_scripts:
                dev_scripts.merge_large_files(delete_parts=delete_parts)
                logger.info("✅ Large files merged successfully")
            else:
                raise ImportError("Failed to load development scripts")
        except Exception as e:
            logger.error(f"❌ Failed to merge large files: {e}")
            sys.exit(1)
    
    def run_dev_extract_facesynthetics(self, input_dir: Path, faceset_path: Path):
        """Run development extract_FaceSynthetics command"""
        try:
            dev_scripts = self.lazy_manager.get_component('dev_scripts')
            if not dev_scripts:
                dev_scripts = asyncio.run(self.lazy_manager.load_component('dev_scripts'))
            
            if dev_scripts:
                if not input_dir.exists():
                    raise FileNotFoundError(f"Input directory not found: {input_dir}")
                
                dev_scripts.extract_FaceSynthetics(input_dir, faceset_path)
                logger.info(f"✅ FaceSynthetics extracted to {faceset_path}")
            else:
                raise ImportError("Failed to load development scripts")
        except Exception as e:
            logger.error(f"❌ Failed to extract FaceSynthetics: {e}")
            sys.exit(1)

class fixPathAction(argparse.Action):
    """Enhanced path action with validation"""
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            return
        
        try:
            # Expand user and make absolute
            expanded_path = os.path.expanduser(values)
            absolute_path = os.path.abspath(expanded_path)
            
            # Validate path
            if not os.path.exists(absolute_path):
                logger.warning(f"⚠️  Path does not exist: {absolute_path}")
                # Create directory if it's a reasonable path
                if not absolute_path.endswith(('.dfs', '.mp4', '.avi', '.mov')):
                    try:
                        os.makedirs(absolute_path, exist_ok=True)
                        logger.info(f"📁 Created directory: {absolute_path}")
                    except Exception as e:
                        logger.warning(f"⚠️  Could not create directory: {e}")
            
            setattr(namespace, self.dest, absolute_path)
        except Exception as e:
            logger.error(f"❌ Invalid path '{values}': {e}")
            raise argparse.ArgumentTypeError(f"Invalid path: {e}")

def main():
    """Enhanced main function with lazy loading and functionality preservation"""
    startup_timer.mark_stage("main_start")
    
    try:
        parser = argparse.ArgumentParser(
            description="PlayaTewsIdentityMasker - Real-time face masking application (Lazy Loading Enhanced)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s run PlayaTewsIdentityMasker --userdata-dir ./workspace
  %(prog)s run PlayaTewsIdentityMaskerOBS --userdata-dir ./workspace --no-cuda
  %(prog)s dev split_large_files
            """
        )
        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Run command
        run_parser = subparsers.add_parser("run", help="Run the application.")
        run_subparsers = run_parser.add_subparsers(dest='app_type', help='Application type')

        # Primary OBS-style app parser (now the main interface)
        p = run_subparsers.add_parser('PlayaTewsIdentityMasker', help="Run PlayaTewsIdentityMasker with OBS-style streaming interface")
        p.add_argument('--userdata-dir', default=None, action=fixPathAction, help="Workspace directory.")
        p.add_argument('--no-cuda', action="store_true", default=False, help="Disable CUDA.")
        p.add_argument('--verbose', '-v', action="store_true", default=False, help="Enable verbose logging.")
        p.add_argument('--traditional', action="store_true", default=False, help="Use traditional interface instead of OBS-style.")

        # Legacy traditional app parser (for backward compatibility)
        p = run_subparsers.add_parser('PlayaTewsIdentityMaskerTraditional', help="Run PlayaTewsIdentityMasker with traditional UI (legacy)")
        p.add_argument('--userdata-dir', default=None, action=fixPathAction, help="Workspace directory.")
        p.add_argument('--no-cuda', action="store_true", default=False, help="Disable CUDA.")
        p.add_argument('--verbose', '-v', action="store_true", default=False, help="Enable verbose logging.")

        # Alias for OBS-style (backward compatibility)
        p = run_subparsers.add_parser('PlayaTewsIdentityMaskerOBS', help="Run PlayaTewsIdentityMasker with OBS-style UI (alias)")
        p.add_argument('--userdata-dir', default=None, action=fixPathAction, help="Workspace directory.")
        p.add_argument('--no-cuda', action="store_true", default=False, help="Disable CUDA.")
        p.add_argument('--verbose', '-v', action="store_true", default=False, help="Enable verbose logging.")

        # Development commands
        dev_parser = subparsers.add_parser("dev", help="Development utilities")
        dev_subparsers = dev_parser.add_subparsers(dest='dev_command', help='Development commands')

        # Development command parsers
        p = dev_subparsers.add_parser('split_large_files', help="Split large files for version control")

        p = dev_subparsers.add_parser('merge_large_files', help="Merge split large files")
        p.add_argument('--delete-parts', action="store_true", default=False, help="Delete part files after merging")

        p = dev_subparsers.add_parser('extract_FaceSynthetics', help="Extract FaceSynthetics dataset")
        p.add_argument('--input-dir', default=None, action=fixPathAction, help="FaceSynthetics directory.")
        p.add_argument('--faceset-path', default=None, action=fixPathAction, help="output .dfs path")

        # Parse arguments
        args = parser.parse_args()
        
        # Handle verbose logging
        if hasattr(args, 'verbose') and args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Verbose logging enabled")
        
        # Initialize lazy loading app
        userdata_path = Path(args.userdata_dir) if hasattr(args, 'userdata_dir') and args.userdata_dir else Path.cwd()
        no_cuda = getattr(args, 'no_cuda', False)
        
        app = FunctionalityPreservingLazyDeepFaceLiveApp(
            userdata_path=userdata_path,
            no_cuda=no_cuda,
            optimization_mode="balanced"
        )
        
        # Initialize async
        asyncio.run(app.initialize_async())
        
        # Execute command
        if args.command == "run":
            if args.app_type == "PlayaTewsIdentityMasker":
                traditional = getattr(args, 'traditional', False)
                app.run_playatewsidentitymasker_obs(userdata_path, no_cuda, traditional)
            elif args.app_type == "PlayaTewsIdentityMaskerTraditional":
                app.run_playatewsidentitymasker(userdata_path, no_cuda)
            elif args.app_type == "PlayaTewsIdentityMaskerOBS":
                app.run_playatewsidentitymasker_obs(userdata_path, no_cuda, False)
        elif args.command == "dev":
            if args.dev_command == "split_large_files":
                app.run_dev_split_large_files()
            elif args.dev_command == "merge_large_files":
                delete_parts = getattr(args, 'delete_parts', False)
                app.run_dev_merge_large_files(delete_parts)
            elif args.dev_command == "extract_FaceSynthetics":
                input_dir = Path(args.input_dir) if args.input_dir else None
                faceset_path = Path(args.faceset_path) if args.faceset_path else None
                if input_dir and faceset_path:
                    app.run_dev_extract_facesynthetics(input_dir, faceset_path)
                else:
                    logger.error("Both --input-dir and --faceset-path are required for extract_FaceSynthetics")
                    sys.exit(1)
        else:
            parser.print_help()
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("🛑 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()