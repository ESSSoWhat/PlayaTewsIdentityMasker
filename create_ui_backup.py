#!/usr/bin/env python3
"""
UI Backup Management Script
Creates a new backup of the current UI state and manages old backups
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

def create_ui_backup():
    """Create a new backup of the current UI state"""
    
    # Define paths
    project_root = Path(__file__).parent
    backups_dir = project_root / "backups"
    current_ui_dir = project_root / "apps" / "PlayaTewsIdentityMasker" / "ui"
    
    # Create timestamp for new backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"ui_crash_fixed_backup_{timestamp}"
    new_backup_dir = backups_dir / backup_name
    
    # Create backup directory
    new_backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Files to backup
    files_to_backup = [
        "QOBSStyleUI.py",
        "QProcessingWindow.py",
        "QOptimizedPlayaTewsIdentityMaskerApp.py",
        "PlayaTewsIdentityMaskerOBSStyleApp.py",
        "PlayaTewsIdentityMaskerApp.py"
    ]
    
    # Copy UI files
    print(f"📁 Creating backup: {backup_name}")
    for file_name in files_to_backup:
        source_file = current_ui_dir / file_name
        if source_file.exists():
            shutil.copy2(source_file, new_backup_dir / file_name)
            print(f"   ✅ Copied: {file_name}")
        else:
            print(f"   ⚠️  Not found: {file_name}")
    
    # Copy main application files
    main_files = [
        "main.py",
        "run_obs_fixed.py"
    ]
    
    for file_name in main_files:
        source_file = project_root / file_name
        if source_file.exists():
            shutil.copy2(source_file, new_backup_dir / file_name)
            print(f"   ✅ Copied: {file_name}")
        else:
            print(f"   ⚠️  Not found: {file_name}")
    
    # Copy xlib fixes
    xlib_files = [
        "xlib/qt/widgets/QXFixedLayeredImages.py",
        "xlib/qt/widgets/QFaceDetector.py",
        "xlib/qt/widgets/QBCFrameViewer.py",
        "xlib/qt/widgets/QBCMergedFrameViewer.py",
        "xlib/qt/widgets/QBCFaceAlignViewer.py",
        "xlib/qt/widgets/QBCFaceSwapViewer.py",
        "xlib/qt/widgets/QOptimizedFrameViewer.py"
    ]
    
    for file_path in xlib_files:
        source_file = project_root / file_path
        if source_file.exists():
            # Create subdirectories if needed
            target_dir = new_backup_dir / Path(file_path).parent
            target_dir.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source_file, new_backup_dir / file_path)
            print(f"   ✅ Copied: {file_path}")
        else:
            print(f"   ⚠️  Not found: {file_path}")
    
    # Create backup metadata
    metadata = {
        "backup_name": backup_name,
        "timestamp": timestamp,
        "created_at": datetime.now().isoformat(),
        "description": "UI backup after crash fixes and component reorganization",
        "fixes_applied": [
            "Fixed QRect float arguments in QXFixedLayeredImages",
            "Added comprehensive error handling for face swap components",
            "Made QProcessingWindow constructor safe with optional parameters",
            "Moved all UI controls to popup window",
            "Fixed top_QXWindow errors in viewer components",
            "Cleaned up old UI component references"
        ],
        "files_backed_up": files_to_backup + main_files + xlib_files,
        "backup_version": "2.0"
    }
    
    with open(new_backup_dir / "backup_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"   ✅ Created metadata: backup_metadata.json")
    
    return new_backup_dir

def delete_oldest_backup():
    """Delete the oldest backup directory"""
    
    project_root = Path(__file__).parent
    backups_dir = project_root / "backups"
    
    if not backups_dir.exists():
        print("📁 No backups directory found")
        return
    
    # Get all backup directories
    backup_dirs = [d for d in backups_dir.iterdir() if d.is_dir() and d.name.startswith("ui_")]
    
    if len(backup_dirs) <= 1:
        print("📁 Only one backup exists, keeping it")
        return
    
    # Find the oldest backup
    oldest_backup = min(backup_dirs, key=lambda x: x.stat().st_mtime)
    
    print(f"🗑️  Deleting oldest backup: {oldest_backup.name}")
    
    # Delete the oldest backup
    try:
        shutil.rmtree(oldest_backup)
        print(f"   ✅ Deleted: {oldest_backup.name}")
    except Exception as e:
        print(f"   ❌ Error deleting {oldest_backup.name}: {e}")

def list_backups():
    """List all existing backups"""
    
    project_root = Path(__file__).parent
    backups_dir = project_root / "backups"
    
    if not backups_dir.exists():
        print("📁 No backups directory found")
        return
    
    backup_dirs = [d for d in backups_dir.iterdir() if d.is_dir() and d.name.startswith("ui_")]
    
    if not backup_dirs:
        print("📁 No UI backups found")
        return
    
    print("📁 Existing UI backups:")
    for backup_dir in sorted(backup_dirs, key=lambda x: x.stat().st_mtime):
        size = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
        size_mb = size / (1024 * 1024)
        print(f"   📦 {backup_dir.name} ({size_mb:.1f} MB)")

def main():
    """Main backup management function"""
    
    print("🚀 UI Backup Management")
    print("=" * 50)
    
    # List existing backups
    list_backups()
    print()
    
    # Create new backup
    new_backup = create_ui_backup()
    print()
    
    # Delete oldest backup
    delete_oldest_backup()
    print()
    
    # List backups again
    list_backups()
    print()
    
    print(f"✅ Backup management completed!")
    print(f"📁 New backup created: {new_backup.name}")

if __name__ == "__main__":
    main() 