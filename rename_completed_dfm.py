#!/usr/bin/env python3
"""
Rename Completed DFM Models
Renames completed .part files to .dfm files
"""

import os
import shutil
from pathlib import Path

def rename_completed_models():
    """Rename completed .part files to .dfm files"""
    dfm_dir = Path("dfm_models")
    
    print("🔍 Checking for completed .part files...")
    
    # Find all .part files
    part_files = list(dfm_dir.glob("*.part"))
    
    if not part_files:
        print("✅ No .part files found to rename")
        return
    
    print(f"📁 Found {len(part_files)} .part files:")
    
    renamed_count = 0
    for part_file in part_files:
        # Get the target .dfm filename
        dfm_file = part_file.with_suffix('.dfm')
        
        # Check if the .dfm file already exists (might be a placeholder)
        if dfm_file.exists():
            dfm_size = dfm_file.stat().st_size
            part_size = part_file.stat().st_size
            
            # If the .dfm file is small (placeholder) and .part is large (real model)
            if dfm_size < 1000 and part_size > 100 * 1024 * 1024:  # Less than 1KB vs more than 100MB
                print(f"🔄 Replacing placeholder {dfm_file.name} with real model...")
                # Remove the placeholder
                dfm_file.unlink()
                # Rename .part to .dfm
                part_file.rename(dfm_file)
                print(f"✅ Renamed {part_file.name} -> {dfm_file.name}")
                renamed_count += 1
            else:
                print(f"⚠️  Skipping {part_file.name} - .dfm file already exists and appears valid")
        else:
            # No .dfm file exists, safe to rename
            part_file.rename(dfm_file)
            print(f"✅ Renamed {part_file.name} -> {dfm_file.name}")
            renamed_count += 1
    
    print(f"\n🎉 Renamed {renamed_count} files successfully!")
    
    # Show final status
    print("\n📊 Final DFM Models Status:")
    dfm_files = list(dfm_dir.glob("*.dfm"))
    for dfm_file in sorted(dfm_files):
        size = dfm_file.stat().st_size
        if size > 100 * 1024 * 1024:  # More than 100MB
            print(f"✅ {dfm_file.name} ({size / (1024*1024):.1f}MB)")
        else:
            print(f"⚠️  {dfm_file.name} ({size}B) - Placeholder")

if __name__ == "__main__":
    rename_completed_models() 