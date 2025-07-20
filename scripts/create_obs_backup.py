#!/usr/bin/env python3
"""
Script to create a UI backup for the OBS layout
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from apps.PlayaTewsIdentityMasker.ui.UILayoutBackupManager import UILayoutBackupManager


def create_obs_backup():
    """Create a backup of the OBS UI layout"""
    print("🎬 Creating OBS UI Layout Backup...")
    
    # Setup paths
    userdata_path = Path("userdata")
    settings_path = Path("settings")
    
    # Ensure directories exist
    userdata_path.mkdir(exist_ok=True)
    settings_path.mkdir(exist_ok=True)
    
    try:
        # Initialize backup manager
        backup_manager = UILayoutBackupManager(settings_path, userdata_path)
        print("✅ Backup manager initialized")
        
        # Create backup with descriptive name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"obs_layout_backup_{timestamp}"
        description = "OBS-style UI layout backup with face-swapping components"
        
        print(f"📦 Creating backup: {backup_name}")
        print(f"📝 Description: {description}")
        
        # Create the backup
        success = backup_manager.create_backup(backup_name, description)
        
        if success:
            print(f"✅ Backup created successfully: {backup_name}")
            
            # List all backups
            backups = backup_manager.list_backups()
            print(f"\n📋 Available backups ({len(backups)} total):")
            for backup in backups:
                print(f"  - {backup['name']}: {backup['description']}")
                print(f"    Created: {backup['timestamp']}")
                print(f"    Widgets: {backup['widget_count']}")
                print(f"    Size: {backup['file_size']} bytes")
            
            # Show backup location
            backup_file = backup_manager.backup_dir / f"{backup_name}.json"
            print(f"\n💾 Backup saved to: {backup_file}")
            
            return True
        else:
            print("❌ Failed to create backup")
            return False
            
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("🚀 OBS UI Layout Backup Creator")
    print("=" * 50)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create the backup
    success = create_obs_backup()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 OBS UI layout backup completed successfully!")
        print("\nTo restore this backup:")
        print("1. Launch the OBS app: python main.py run PlayaTewsIdentityMasker")
        print("2. Go to File → Restore UI Layout")
        print("3. Select the backup from the list")
    else:
        print("💥 Backup creation failed. Check the error messages above.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 