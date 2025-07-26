#!/usr/bin/env python3
"""
FaceAligner Trainer - Standalone Script
This script runs the FaceAligner trainer independently of the main DeepFaceLive application.
"""

import sys
import argparse
from pathlib import Path

# Add the current directory to Python path to find the apps module
sys.path.insert(0, str(Path(__file__).parent))

from xlib import os as lib_os
from apps.trainers.FaceAligner.FaceAlignerTrainerApp import FaceAlignerTrainerApp


def main():
    parser = argparse.ArgumentParser(description="FaceAligner Trainer - Standalone")
    parser.add_argument('--workspace-dir', default='./workspace', type=str, 
                       help="Workspace directory (default: ./workspace)")
    parser.add_argument('--faceset-path', default='./faceset.dfs', type=str,
                       help="Faceset file path (default: ./faceset.dfs)")
    
    args = parser.parse_args()
    
    # Convert to Path objects
    workspace_path = Path(args.workspace_dir).resolve()
    faceset_path = Path(args.faceset_path).resolve()
    
    print(f"Starting FaceAligner Trainer...")
    print(f"Workspace Directory: {workspace_path}")
    print(f"Faceset Path: {faceset_path}")
    print()
    
    # Set process priority to idle for training
    lib_os.set_process_priority(lib_os.ProcessPriority.IDLE)
    
    # Create workspace directory if it doesn't exist
    workspace_path.mkdir(parents=True, exist_ok=True)
    
    # Check if faceset file exists
    if not faceset_path.exists():
        print(f"Warning: Faceset file not found at {faceset_path}")
        print("Please ensure you have a valid faceset file before training.")
        print()
    
    try:
        # Start the trainer
        FaceAlignerTrainerApp(workspace_path=workspace_path, faceset_path=faceset_path)
    except KeyboardInterrupt:
        print("\nTraining interrupted by user.")
    except Exception as e:
        print(f"\nError during training: {e}")
        sys.exit(1)
    
    print("\nFaceAligner training completed.")


if __name__ == '__main__':
    main()