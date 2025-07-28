#!/usr/bin/env python3
"""
Quick DFM Setup Helper
Helps you set up downloaded DFM models
"""

import os
import shutil
from pathlib import Path

def setup_downloaded_model(model_file_path):
    """Set up a downloaded DFM model"""
    model_file = Path(model_file_path)
    
    if not model_file.exists():
        print(f"❌ File not found: {model_file_path}")
        return False
    
    # Check file size
    file_size_mb = model_file.stat().st_size / (1024 * 1024)
    if file_size_mb < 10:
        print(f"⚠️  File seems too small ({file_size_mb:.1f}MB). Real DFM files are 50-200MB.")
        return False
    
    model_name = model_file.stem
    dfm_models_dir = Path("dfm_models")
    universal_models_dir = Path("universal_dfm/models/prebuilt")
    
    # Create directories
    dfm_models_dir.mkdir(exist_ok=True)
    universal_models_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy to both locations
    dest1 = dfm_models_dir / f"{model_name}.dfm"
    dest2 = universal_models_dir / f"{model_name}.dfm"
    
    shutil.copy2(model_file, dest1)
    shutil.copy2(model_file, dest2)
    
    print(f"✅ {model_name} set up successfully!")
    print(f"   Size: {file_size_mb:.1f}MB")
    print(f"   Location 1: {dest1}")
    print(f"   Location 2: {dest2}")
    
    return True

def main():
    """Main function"""
    print("🔧 Quick DFM Setup Helper")
    print("=" * 40)
    print("This script helps you set up downloaded DFM models.")
    print()
    print("Usage:")
    print("1. Download a .dfm file (50-200MB)")
    print("2. Run: python quick_dfm_setup.py")
    print("3. Enter the path to your downloaded .dfm file")
    print()
    
    while True:
        file_path = input("Enter path to downloaded .dfm file (or 'quit' to exit): ").strip()
        
        if file_path.lower() in ['quit', 'exit', 'q']:
            break
        
        if setup_downloaded_model(file_path):
            print("🎉 Model is ready to use! Restart the app to see it.")
        else:
            print("❌ Setup failed. Please check the file path and try again.")
        
        print()

if __name__ == "__main__":
    main()
