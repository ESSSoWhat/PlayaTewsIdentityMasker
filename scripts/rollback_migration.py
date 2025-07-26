#!/usr/bin/env python3
"""
Automated rollback system for UI migrations
"""

import shutil
import json
import sys
from pathlib import Path
from datetime import datetime

class MigrationRollback:
    """Handles rollback of UI migrations"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.rollback_log = []
    
    def create_backup(self, migration_name: str):
        """Create backup before migration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{migration_name}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # Files to backup
        files_to_backup = [
            "apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerApp.py",
            "apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerOBSStyleApp.py",
            "apps/PlayaTewsIdentityMasker/QOptimizedPlayaTewsIdentityMaskerApp.py",
            "apps/PlayaTewsIdentityMasker/ui/QOBSStyleUI.py",
            "apps/PlayaTewsIdentityMasker/ui/QOptimizedUIManager.py",
            "main.py",
            "optimized_main_ui.py"
        ]
        
        backup_path.mkdir(exist_ok=True)
        
        for file_path in files_to_backup:
            src_path = Path(file_path)
            if src_path.exists():
                dst_path = backup_path / src_path.name
                shutil.copy2(src_path, dst_path)
                self.rollback_log.append(f"Backed up: {file_path}")
        
        # Save backup metadata
        metadata = {
            'timestamp': timestamp,
            'migration_name': migration_name,
            'files_backed_up': files_to_backup,
            'rollback_log': self.rollback_log
        }
        
        metadata_file = backup_path / "backup_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    
    def rollback(self, backup_path: Path):
        """Rollback to backup"""
        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_path}")
            return False
        
        # Load backup metadata
        metadata_file = backup_path / "backup_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        else:
            print(f"⚠️ No metadata found in backup: {backup_path}")
            metadata = {'files_backed_up': []}
        
        # Restore files
        restored_count = 0
        for file_name in metadata.get('files_backed_up', []):
            src_path = backup_path / Path(file_name).name
            dst_path = Path(file_name)
            
            if src_path.exists():
                # Create directory if needed
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Restore file
                shutil.copy2(src_path, dst_path)
                print(f"✅ Restored: {file_name}")
                restored_count += 1
            else:
                print(f"⚠️ Backup file not found: {src_path}")
        
        print(f"✅ Rollback completed from: {backup_path}")
        print(f"📊 Files restored: {restored_count}")
        return True
    
    def list_backups(self):
        """List all available backups"""
        backup_dirs = list(self.backup_dir.glob("*"))
        if not backup_dirs:
            print("No backups found.")
            return
        
        print("Available backups:")
        for backup_dir in sorted(backup_dirs, key=lambda x: x.name, reverse=True):
            metadata_file = backup_dir / "backup_metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    timestamp = metadata.get('timestamp', 'Unknown')
                    migration_name = metadata.get('migration_name', 'Unknown')
                    print(f"  {backup_dir.name} - {migration_name} ({timestamp})")
                except:
                    print(f"  {backup_dir.name} - Invalid metadata")
            else:
                print(f"  {backup_dir.name} - No metadata")

def main():
    """Main rollback function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rollback UI migration")
    parser.add_argument("--backup", help="Backup directory to rollback to")
    parser.add_argument("--create-backup", help="Create backup before migration")
    parser.add_argument("--list", action="store_true", help="List all available backups")
    
    args = parser.parse_args()
    
    rollback = MigrationRollback()
    
    if args.list:
        rollback.list_backups()
    elif args.create_backup:
        rollback.create_backup(args.create_backup)
    elif args.backup:
        success = rollback.rollback(Path(args.backup))
        sys.exit(0 if success else 1)
    else:
        print("Usage:")
        print("  python rollback_migration.py --create-backup <name>")
        print("  python rollback_migration.py --backup <path>")
        print("  python rollback_migration.py --list")

if __name__ == "__main__":
    main() 