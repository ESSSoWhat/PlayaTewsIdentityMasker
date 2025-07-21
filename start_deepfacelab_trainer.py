#!/usr/bin/env python3
"""
DeepFaceLab Trainer Startup Script
This script provides an easy way to start the DeepFaceLab trainer with common configurations.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=== DeepFaceLab Trainer Startup ===")
    print()
    
    # Get the DeepFaceLab directory
    deepfacelab_dir = Path(__file__).parent / "DeepFaceLab"
    
    if not deepfacelab_dir.exists():
        print("Error: DeepFaceLab directory not found!")
        print(f"Expected location: {deepfacelab_dir}")
        return 1
    
    # Check if workspace exists
    workspace_dir = deepfacelab_dir / "workspace"
    if not workspace_dir.exists():
        print("Error: Workspace directory not found!")
        print(f"Expected location: {workspace_dir}")
        return 1
    
    # Check for training data
    src_aligned = workspace_dir / "data_src" / "aligned"
    dst_aligned = workspace_dir / "data_dst" / "aligned"
    model_dir = workspace_dir / "model"
    
    print("Checking training data...")
    print(f"Source aligned faces: {src_aligned}")
    print(f"Destination aligned faces: {dst_aligned}")
    print(f"Model directory: {model_dir}")
    print()
    
    # Check if source aligned faces exist
    if not src_aligned.exists() or not any(src_aligned.iterdir()):
        print("Warning: No source aligned faces found!")
        print("You need to extract faces from source images first.")
        print("Run: python main.py extract --input-dir workspace/data_src --output-dir workspace/data_src/aligned --detector s3fd")
        print()
    
    # Check if destination aligned faces exist
    if not dst_aligned.exists() or not any(dst_aligned.iterdir()):
        print("Warning: No destination aligned faces found!")
        print("You need to extract faces from destination images first.")
        print("Run: python main.py extract --input-dir workspace/data_dst --output-dir workspace/data_dst/aligned --detector s3fd")
        print()
    
    # Ask user for model type
    print("Available models:")
    print("1. SAEHD (Recommended for most cases)")
    print("2. Quick96 (Fast training, lower quality)")
    print("3. AMP (Advanced)")
    print("4. XSeg (For segmentation)")
    print()
    
    model_choice = input("Select model type (1-4, default=1): ").strip()
    if not model_choice:
        model_choice = "1"
    
    model_map = {
        "1": "SAEHD",
        "2": "Quick96", 
        "3": "AMP",
        "4": "XSeg"
    }
    
    model_type = model_map.get(model_choice, "SAEHD")
    print(f"Selected model: {model_type}")
    print()
    
    # Build the command
    cmd = [
        sys.executable, "main.py", "train",
        "--training-data-src-dir", "workspace/data_src/aligned",
        "--training-data-dst-dir", "workspace/data_dst/aligned", 
        "--model-dir", "workspace/model",
        "--model", model_type,
        "--silent-start"
    ]
    
    print("Starting DeepFaceLab trainer...")
    print(f"Command: {' '.join(cmd)}")
    print()
    print("Note: The trainer will ask for a model name if no saved models are found.")
    print("Press Ctrl+C to stop training.")
    print()
    
    try:
        # Change to DeepFaceLab directory and run the trainer
        os.chdir(deepfacelab_dir)
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nTraining interrupted by user.")
    except subprocess.CalledProcessError as e:
        print(f"\nError running trainer: {e}")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return 1
    
    print("\nDeepFaceLab training completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 