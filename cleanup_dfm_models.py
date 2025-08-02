#!/usr/bin/env python3
"""
Cleanup DFM Models
Fixes double .dfm extensions and removes placeholder files
"""

import os
import shutil
from pathlib import Path

def cleanup_dfm_models():
    """Clean up DFM models directory"""
    dfm_dir = Path("dfm_models")
    
    print("🧹 Cleaning up DFM models directory...")
    
    # Fix double .dfm extensions
    double_dfm_files = list(dfm_dir.glob("*.dfm.dfm"))
    print(f"🔧 Found {len(double_dfm_files)} files with double .dfm extension")
    
    for double_file in double_dfm_files:
        # Remove the extra .dfm extension
        correct_name = double_file.name.replace('.dfm.dfm', '.dfm')
        correct_path = double_file.parent / correct_name
        
        # Check if the correct file already exists (might be a placeholder)
        if correct_path.exists():
            correct_size = correct_path.stat().st_size
            double_size = double_file.stat().st_size
            
            # If the existing file is small (placeholder) and double file is large (real model)
            if correct_size < 1000 and double_size > 100 * 1024 * 1024:
                print(f"🔄 Replacing placeholder {correct_path.name} with real model...")
                correct_path.unlink()  # Remove placeholder
                double_file.rename(correct_path)  # Rename to correct name
                print(f"✅ Fixed {double_file.name} -> {correct_path.name}")
            else:
                print(f"⚠️  Skipping {double_file.name} - target file already exists and appears valid")
        else:
            # No conflict, safe to rename
            double_file.rename(correct_path)
            print(f"✅ Fixed {double_file.name} -> {correct_path.name}")
    
    # Remove placeholder files (small .dfm files)
    print("\n🗑️  Removing placeholder files...")
    placeholder_count = 0
    for dfm_file in dfm_dir.glob("*.dfm"):
        size = dfm_file.stat().st_size
        if size < 1000:  # Less than 1KB = placeholder
            print(f"🗑️  Removing placeholder: {dfm_file.name} ({size}B)")
            dfm_file.unlink()
            placeholder_count += 1
    
    print(f"✅ Removed {placeholder_count} placeholder files")
    
    # Show final status
    print("\n📊 Final DFM Models Status:")
    dfm_files = list(dfm_dir.glob("*.dfm"))
    real_models = []
    
    for dfm_file in sorted(dfm_files):
        size = dfm_file.stat().st_size
        if size > 100 * 1024 * 1024:  # More than 100MB
            real_models.append(dfm_file)
            print(f"✅ {dfm_file.name} ({size / (1024*1024):.1f}MB)")
        else:
            print(f"⚠️  {dfm_file.name} ({size}B) - Small file")
    
    print(f"\n🎉 Total real DFM models: {len(real_models)}")
    
    # List all real models
    if real_models:
        print("\n📋 Available DFM Models:")
        for i, model in enumerate(real_models, 1):
            size_mb = model.stat().st_size / (1024*1024)
            print(f"  {i:2d}. {model.name} ({size_mb:.1f}MB)")

if __name__ == "__main__":
    cleanup_dfm_models() 