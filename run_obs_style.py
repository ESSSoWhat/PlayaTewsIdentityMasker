#!/usr/bin/env python3
"""
DeepFaceLive OBS-Style Launcher

This script launches DeepFaceLive with the new OBS-style interface.
It provides a simple way to start the application with the enhanced
streaming and recording capabilities.
"""

import sys
import os
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description='Launch DeepFaceLive with OBS-style interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_obs_style.py
  python run_obs_style.py --userdata-dir /path/to/workspace
  python run_obs_style.py --no-cuda
        """
    )
    
    parser.add_argument(
        '--userdata-dir',
        type=str,
        default=None,
        help='Workspace directory (default: current directory)'
    )
    
    parser.add_argument(
        '--no-cuda',
        action='store_true',
        help='Disable CUDA acceleration'
    )
    
    parser.add_argument(
        '--traditional',
        action='store_true',
        help='Launch with traditional interface instead of OBS-style'
    )
    
    args = parser.parse_args()
    
    # Set up userdata directory
    if args.userdata_dir:
        userdata_path = Path(args.userdata_dir).resolve()
    else:
        userdata_path = Path.cwd()
    
    # Ensure userdata directory exists
    userdata_path.mkdir(parents=True, exist_ok=True)
    
    # Set environment variables
    if args.no_cuda:
        os.environ['NO_CUDA'] = '1'
    
    # Import and run the appropriate application
    try:
        if args.traditional:
            print("Launching DeepFaceLive with traditional interface...")
            from apps.DeepFaceLive.DeepFaceLiveApp import DeepFaceLiveApp
            app = DeepFaceLiveApp(userdata_path=userdata_path)
        else:
            print("Launching DeepFaceLive with OBS-style interface...")
            from apps.DeepFaceLive.DeepFaceLiveOBSStyleApp import DeepFaceLiveOBSStyleApp
            app = DeepFaceLiveOBSStyleApp(userdata_path=userdata_path)
        
        app.run()
        
    except ImportError as e:
        print(f"Error: Could not import required modules: {e}")
        print("Make sure you're running this script from the DeepFaceLive root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Error launching application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()