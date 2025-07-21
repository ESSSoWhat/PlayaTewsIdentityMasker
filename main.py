import argparse
import os
import platform
import sys
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

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
        logging.FileHandler('playatewsidentitymasker.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

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

# Performance monitoring
class StartupTimer:
    """Track startup performance"""
    def __init__(self):
        self.start_time = time.time()
        self.stages = {}
    
    def mark_stage(self, stage_name: str):
        """Mark a startup stage completion"""
        self.stages[stage_name] = time.time() - self.start_time
        logger.info(f"[OK] {stage_name} completed in {self.stages[stage_name]:.2f}s")
    
    def get_summary(self) -> Dict[str, float]:
        """Get startup performance summary"""
        return self.stages.copy()

# Global startup timer
startup_timer = StartupTimer()

def main():
    """Enhanced main function with performance monitoring and error handling"""
    startup_timer.mark_stage("main_start")
    
    try:
        parser = argparse.ArgumentParser(
            description="PlayaTewsIdentityMasker - Real-time face masking application",
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

        def run_PlayaTewsIdentityMasker(args):
            """Run standard PlayaTewsIdentityMasker with enhanced error handling"""
            startup_timer.mark_stage("args_parsed")
            
            userdata_path = Path(args.userdata_dir) if args.userdata_dir else Path.cwd()
            
            # Lazy import xlib modules
            try:
                from xlib import appargs as lib_appargs
                lib_appargs.set_arg_bool('NO_CUDA', args.no_cuda)
            except ImportError as e:
                logger.warning(f"Could not import xlib.appargs: {e}")
                # Set default CUDA behavior
                os.environ['NO_CUDA'] = str(args.no_cuda).lower()
            logger.info(f"[START] Starting PlayaTewsIdentityMasker with userdata: {userdata_path}")
            
            try:
                # Lazy import the app
                from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
                startup_timer.mark_stage("app_imported")
                
                app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
                startup_timer.mark_stage("app_created")
                
                app.run()
                startup_timer.mark_stage("app_completed")
                
                # Log startup performance
                summary = startup_timer.get_summary()
                logger.info(f"📊 Startup performance: {summary}")
                
            except ImportError as e:
                logger.error(f"[ERROR] Failed to import PlayaTewsIdentityMaskerApp: {e}")
                logger.error("Please ensure all dependencies are installed: pip install -r requirements-unified.txt")
                sys.exit(1)
            except Exception as e:
                logger.error(f"[ERROR] Application failed to start: {e}")
                sys.exit(1)

        def run_PlayaTewsIdentityMaskerOBS(args):
            """Run PlayaTewsIdentityMasker with interface choice (OBS by default, traditional if flagged)"""
            startup_timer.mark_stage("args_parsed")
            
            userdata_path = Path(args.userdata_dir) if args.userdata_dir else Path.cwd()
            
            # Lazy import xlib modules
            try:
                from xlib import appargs as lib_appargs
                lib_appargs.set_arg_bool('NO_CUDA', args.no_cuda)
            except ImportError as e:
                logger.warning(f"Could not import xlib.appargs: {e}")
                # Set default CUDA behavior
                os.environ['NO_CUDA'] = str(args.no_cuda).lower()

            # Check if traditional interface is requested
            use_traditional = getattr(args, 'traditional', False)
            
            if use_traditional:
                logger.info(f"🚀 Starting PlayaTewsIdentityMasker with traditional UI: {userdata_path}")
                try:
                    from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
                    startup_timer.mark_stage("app_imported")
                    
                    app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
                    startup_timer.mark_stage("app_created")
                    
                    app.run()
                    startup_timer.mark_stage("app_completed")
                except ImportError as e:
                    logger.error(f"[ERROR] Failed to import PlayaTewsIdentityMaskerApp: {e}")
                    logger.error("Please ensure all dependencies are installed: pip install -r requirements-unified.txt")
                    sys.exit(1)
            else:
                logger.info(f"🚀 Starting PlayaTewsIdentityMasker with OBS-style streaming interface: {userdata_path}")
                try:
                    from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerOBSStyleApp import PlayaTewsIdentityMaskerOBSStyleApp
                    startup_timer.mark_stage("app_imported")
                    
                    app = PlayaTewsIdentityMaskerOBSStyleApp(userdata_path=userdata_path)
                    startup_timer.mark_stage("app_created")
                    
                    app.run()
                    startup_timer.mark_stage("app_completed")
                except ImportError as e:
                    logger.error(f"[ERROR] Failed to import PlayaTewsIdentityMaskerOBSStyleApp: {e}")
                    logger.error("Please ensure all dependencies are installed: pip install -r requirements-unified.txt")
                    sys.exit(1)
            
            try:
                # Log startup performance
                summary = startup_timer.get_summary()
                logger.info(f"[PERF] Startup performance: {summary}")
                
            except Exception as e:
                logger.error(f"[ERROR] Application failed to start: {e}")
                sys.exit(1)

        def run_PlayaTewsIdentityMaskerOptimized(args):
            """Run optimized PlayaTewsIdentityMasker with voice changer integration"""
            startup_timer.mark_stage("args_parsed")
            
            userdata_path = Path(args.userdata_dir) if args.userdata_dir else Path.cwd()
            
            # Lazy import xlib modules
            try:
                from xlib import appargs as lib_appargs
                lib_appargs.set_arg_bool('NO_CUDA', args.no_cuda)
            except ImportError as e:
                logger.warning(f"Could not import xlib.appargs: {e}")
                # Set default CUDA behavior
                os.environ['NO_CUDA'] = str(args.no_cuda).lower()

            logger.info(f"[START] Starting PlayaTewsIdentityMasker with optimized UI: {userdata_path}")
            try:
                from apps.PlayaTewsIdentityMasker.QOptimizedPlayaTewsIdentityMaskerApp import OptimizedPlayaTewsIdentityMaskerApp
                startup_timer.mark_stage("app_imported")
                
                app = OptimizedPlayaTewsIdentityMaskerApp(userdata_path)
                startup_timer.mark_stage("app_created")
                
                app.run()
                startup_timer.mark_stage("app_completed")
                
                # Log startup performance
                summary = startup_timer.get_summary()
                logger.info(f"📊 Startup performance: {summary}")
                
            except ImportError as e:
                logger.error(f"[ERROR] Failed to import OptimizedPlayaTewsIdentityMaskerApp: {e}")
                logger.error("Please ensure all dependencies are installed: pip install -r requirements-unified.txt")
                sys.exit(1)
            except Exception as e:
                logger.error(f"[ERROR] Application failed to start: {e}")
                sys.exit(1)

        # Primary OBS-style app parser (now the main interface)
        p = run_subparsers.add_parser('PlayaTewsIdentityMasker', help="Run PlayaTewsIdentityMasker with OBS-style streaming interface")
        p.add_argument('--userdata-dir', default=None, action=fixPathAction, help="Workspace directory.")
        p.add_argument('--no-cuda', action="store_true", default=False, help="Disable CUDA.")
        p.add_argument('--verbose', '-v', action="store_true", default=False, help="Enable verbose logging.")
        p.add_argument('--traditional', action="store_true", default=False, help="Use traditional interface instead of OBS-style.")
        p.set_defaults(func=run_PlayaTewsIdentityMaskerOBS)

        # Legacy traditional app parser (for backward compatibility)
        p = run_subparsers.add_parser('PlayaTewsIdentityMaskerTraditional', help="Run PlayaTewsIdentityMasker with traditional UI (legacy)")
        p.add_argument('--userdata-dir', default=None, action=fixPathAction, help="Workspace directory.")
        p.add_argument('--no-cuda', action="store_true", default=False, help="Disable CUDA.")
        p.add_argument('--verbose', '-v', action="store_true", default=False, help="Enable verbose logging.")
        p.set_defaults(func=run_PlayaTewsIdentityMasker)

        # Alias for OBS-style (backward compatibility)
        p = run_subparsers.add_parser('PlayaTewsIdentityMaskerOBS', help="Run PlayaTewsIdentityMasker with OBS-style UI (alias)")
        p.add_argument('--userdata-dir', default=None, action=fixPathAction, help="Workspace directory.")
        p.add_argument('--no-cuda', action="store_true", default=False, help="Disable CUDA.")
        p.add_argument('--verbose', '-v', action="store_true", default=False, help="Enable verbose logging.")
        p.set_defaults(func=run_PlayaTewsIdentityMaskerOBS)

        # Optimized app parser
        p = run_subparsers.add_parser('PlayaTewsIdentityMaskerOptimized', help="Run PlayaTewsIdentityMasker with optimized UI and voice changer")
        p.add_argument('--userdata-dir', default=None, action=fixPathAction, help="Workspace directory.")
        p.add_argument('--no-cuda', action="store_true", default=False, help="Disable CUDA.")
        p.add_argument('--verbose', '-v', action="store_true", default=False, help="Enable verbose logging.")
        p.set_defaults(func=run_PlayaTewsIdentityMaskerOptimized)

        # Development commands
        dev_parser = subparsers.add_parser("dev", help="Development utilities")
        dev_subparsers = dev_parser.add_subparsers(dest='dev_command', help='Development commands')

        def run_split_large_files(args):
            """Split large files with error handling"""
            try:
                from scripts import dev
                dev.split_large_files()
                logger.info("✅ Large files split successfully")
            except Exception as e:
                logger.error(f"❌ Failed to split large files: {e}")
                sys.exit(1)

        def run_merge_large_files(args):
            """Merge large files with error handling"""
            try:
                from scripts import dev
                dev.merge_large_files(delete_parts=args.delete_parts)
                logger.info("✅ Large files merged successfully")
            except Exception as e:
                logger.error(f"❌ Failed to merge large files: {e}")
                sys.exit(1)

        def run_extract_FaceSynthetics(args):
            """Extract FaceSynthetics with error handling"""
            try:
                from scripts import dev
                inputdir_path = Path(args.input_dir)
                faceset_path = Path(args.faceset_path)
                
                if not inputdir_path.exists():
                    raise FileNotFoundError(f"Input directory not found: {inputdir_path}")
                
                dev.extract_FaceSynthetics(inputdir_path, faceset_path)
                logger.info(f"✅ FaceSynthetics extracted to {faceset_path}")
            except Exception as e:
                logger.error(f"❌ Failed to extract FaceSynthetics: {e}")
                sys.exit(1)

        # Development command parsers
        p = dev_subparsers.add_parser('split_large_files', help="Split large files for version control")
        p.set_defaults(func=run_split_large_files)

        p = dev_subparsers.add_parser('merge_large_files', help="Merge split large files")
        p.add_argument('--delete-parts', action="store_true", default=False, help="Delete part files after merging")
        p.set_defaults(func=run_merge_large_files)

        p = dev_subparsers.add_parser('extract_FaceSynthetics', help="Extract FaceSynthetics dataset")
        p.add_argument('--input-dir', default=None, action=fixPathAction, help="FaceSynthetics directory.")
        p.add_argument('--faceset-path', default=None, action=fixPathAction, help="output .dfs path")
        p.set_defaults(func=run_extract_FaceSynthetics)

        # Parse arguments
        args = parser.parse_args()
        
        # Handle verbose logging
        if hasattr(args, 'verbose') and args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Verbose logging enabled")
        
        # Execute command
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("🛑 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
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

if __name__ == '__main__':
    main() 