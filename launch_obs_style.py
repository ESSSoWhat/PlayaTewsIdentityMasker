#!/usr/bin/env python3
"""
Launch script for OBS-Style DeepFaceLive

This script provides an easy way to launch the OBS Studio-style interface
with streaming and recording capabilities.
"""

import argparse
import sys
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Launch OBS-Style DeepFaceLive with streaming capabilities"
    )
    
    parser.add_argument(
        '--userdata-dir', 
        type=str,
        default='./workspace',
        help="Directory to store user data (default: ./workspace)"
    )
    
    parser.add_argument(
        '--no-cuda', 
        action='store_true',
        help="Disable CUDA acceleration"
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help="Enable debug mode with verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup paths
    userdata_path = Path(args.userdata_dir)
    userdata_path.mkdir(parents=True, exist_ok=True)
    
    # Add current directory to Python path
    sys.path.insert(0, str(Path(__file__).parent))
    
    # Set environment variables
    if args.no_cuda:
        os.environ['NO_CUDA'] = '1'
        
    if args.debug:
        os.environ['DEBUG'] = '1'
        print("Debug mode enabled")
    
    # Import and run the application
    try:
        from apps.DeepFaceLive.OBSStyleApp import OBSStyleDeepFaceLiveApp
        
        print("Starting OBS-Style DeepFaceLive...")
        print(f"User data directory: {userdata_path.absolute()}")
        
        app = OBSStyleDeepFaceLiveApp(userdata_path=userdata_path)
        app.run()
        
    except ImportError as e:
        print(f"Error importing application: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements_minimal.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()