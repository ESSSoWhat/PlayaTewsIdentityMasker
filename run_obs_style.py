#!/usr/bin/env python3
"""
PlayaTewsIdentityMasker - Primary OBS-Style Interface Launcher

This is the main launcher for PlayaTewsIdentityMasker with the professional 
OBS-style streaming interface. This interface is now the primary and recommended 
way to run the application, providing enhanced streaming, recording, and 
face-swapping capabilities.

This application is built upon the excellent work of the open source community:

Core Technologies:
- DeepFaceLive by @iperov (https://github.com/iperov/DeepFaceLive.git) - Real-time face swap technology
- DeepFaceLab by @iperov (https://github.com/iperov/DeepFaceLab) - Face model training framework
- Voice Changer Technology - Real-time audio processing and effects

For complete attribution information, see CREDITS_AND_ATTRIBUTIONS.md

License: GPL-3.0 (based on DeepFaceLive)
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('playatewsidentitymasker.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description='PlayaTewsIdentityMasker - Professional Face-Swapping & Streaming',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🚀 Quick Start Examples:
  python run_obs_style.py                          # Launch with OBS-style interface (default)
  python run_obs_style.py --userdata-dir /workspace # Use specific workspace
  python run_obs_style.py --no-cuda               # Disable GPU acceleration
  python run_obs_style.py --traditional           # Use legacy interface

🎯 Features:
  • Professional OBS-style streaming interface
  • Multi-platform streaming (Twitch, YouTube, Facebook)
  • Advanced recording capabilities
  • Real-time face swapping and enhancement
  • Scene management and transitions
  • Audio/video controls and monitoring

📖 For detailed documentation, see:
  - OBS_STYLE_UI_README.md
  - QUICK_START_OBS.md
        """
    )
    
    parser.add_argument(
        '--userdata-dir',
        type=str,
        default=None,
        help='Workspace directory for storing user data and models (default: current directory)'
    )
    
    parser.add_argument(
        '--no-cuda',
        action='store_true',
        help='Disable CUDA/GPU acceleration (use CPU only)'
    )
    
    parser.add_argument(
        '--traditional',
        action='store_true',
        help='Launch with legacy traditional interface instead of OBS-style'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging for debugging'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Set up userdata directory
    if args.userdata_dir:
        userdata_path = Path(args.userdata_dir).resolve()
    else:
        userdata_path = Path.cwd()
    
    # Ensure userdata directory exists
    userdata_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Using workspace: {userdata_path}")
    
    # Set environment variables
    if args.no_cuda:
        os.environ['NO_CUDA'] = '1'
        logger.info("CUDA disabled - using CPU acceleration")
    
    # Import and run the appropriate application
    try:
        if args.traditional:
            logger.info("🔄 Launching PlayaTewsIdentityMasker with legacy traditional interface...")
            print("=" * 60)
            print("🔄 LEGACY MODE: Traditional Interface")
            print("💡 Tip: Remove --traditional flag for the new OBS-style interface")
            print("=" * 60)
            from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
            app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        else:
            logger.info("Launching PlayaTewsIdentityMasker with OBS-style streaming interface...")
            print("=" * 60)
            print("🎬 OBS-STYLE INTERFACE - Professional Streaming Mode")
            print("📺 Features: Multi-platform streaming, recording, scene management")
            print("🎯 Ready for Twitch, YouTube, Facebook Live streaming")
            print("=" * 60)
            from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerOBSStyleApp import PlayaTewsIdentityMaskerOBSStyleApp
            app = PlayaTewsIdentityMaskerOBSStyleApp(userdata_path=userdata_path)
        
        # Run the application
        logger.info("Application initialized successfully")
        app.run()
        
    except ImportError as e:
        logger.error(f"❌ Import Error: Could not import required modules: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're running this script from the project root directory")
        print("2. Install dependencies: pip install -r requirements-unified.txt")
        print("3. Check if all app modules are present in apps/PlayaTewsIdentityMasker/")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()