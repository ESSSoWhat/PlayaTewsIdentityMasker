#!/usr/bin/env python3
"""
Restore Backup Script for PlayaTewsIdentityMasker
Restores original files if camera fixes cause issues
"""

import shutil
from pathlib import Path

def restore_backups():
    """Restore original files from backups"""
    print("🔧 Restoring Original Files...")
    print("=" * 50)
    
    backups = [
        ("apps/PlayaTewsIdentityMasker/backend/CameraSource.py.backup", 
         "apps/PlayaTewsIdentityMasker/backend/CameraSource.py"),
        ("apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerApp.py.backup", 
         "apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerApp.py")
    ]
    
    for backup_file, original_file in backups:
        backup_path = Path(backup_file)
        original_path = Path(original_file)
        
        if backup_path.exists():
            shutil.copy2(backup_path, original_path)
            print(f"✅ Restored: {original_file}")
        else:
            print(f"⚠️ Backup not found: {backup_file}")
    
    print("\n✅ Backup restoration completed")
    print("   Original files have been restored")

if __name__ == "__main__":
    restore_backups()
