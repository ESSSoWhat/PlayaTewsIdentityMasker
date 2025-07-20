#!/usr/bin/env python3
"""
Test script for UI Layout Backup functionality
"""

import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from apps.PlayaTewsIdentityMasker.ui.UILayoutBackupManager import UILayoutBackupManager


def test_backup_manager():
    """Test the backup manager functionality"""
    print("🧪 Testing UI Layout Backup Manager...")
    
    # Setup test paths
    test_userdata = Path("test_userdata")
    test_settings = Path("test_settings")
    
    # Create test directories
    test_userdata.mkdir(exist_ok=True)
    test_settings.mkdir(exist_ok=True)
    
    try:
        # Initialize backup manager
        backup_manager = UILayoutBackupManager(test_settings, test_userdata)
        print("✅ Backup manager initialized successfully")
        
        # Test creating a backup
        print("\n📦 Creating test backup...")
        backup_name = backup_manager.create_backup("test_backup", "Test backup for UI layout")
        
        if backup_name:
            print(f"✅ Backup created: {backup_name}")
        else:
            print("❌ Failed to create backup")
            return False
        
        # Test listing backups
        print("\n📋 Listing backups...")
        backups = backup_manager.list_backups()
        print(f"✅ Found {len(backups)} backups:")
        for backup in backups:
            print(f"  - {backup['name']}: {backup['description']}")
        
        # Test backup metadata
        print("\n📊 Backup metadata:")
        for backup in backups:
            print(f"  - {backup['name']}:")
            print(f"    Timestamp: {backup['timestamp']}")
            print(f"    Widget count: {backup['widget_count']}")
            print(f"    File size: {backup['file_size']} bytes")
        
        # Test export functionality
        print("\n📤 Testing export...")
        export_path = test_userdata / "exported_backup.json"
        success = backup_manager.export_backup(backup_name, export_path)
        
        if success:
            print(f"✅ Backup exported to: {export_path}")
        else:
            print("❌ Failed to export backup")
        
        # Test import functionality
        print("\n📥 Testing import...")
        imported_name = backup_manager.import_backup(export_path, "imported_backup")
        
        if imported_name:
            print(f"✅ Backup imported as: {imported_name}")
        else:
            print("❌ Failed to import backup")
        
        # Test cleanup
        print("\n🧹 Testing cleanup...")
        success = backup_manager.delete_backup(backup_name)
        
        if success:
            print(f"✅ Backup deleted: {backup_name}")
        else:
            print("❌ Failed to delete backup")
        
        # Final backup count
        final_backups = backup_manager.list_backups()
        print(f"\n📊 Final backup count: {len(final_backups)}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup test directories
        import shutil
        if test_userdata.exists():
            shutil.rmtree(test_userdata)
        if test_settings.exists():
            shutil.rmtree(test_settings)


def test_backup_file_structure():
    """Test the backup file structure and format"""
    print("\n🔍 Testing backup file structure...")
    
    # Setup test paths
    test_userdata = Path("test_userdata_structure")
    test_settings = Path("test_settings_structure")
    
    # Create test directories
    test_userdata.mkdir(exist_ok=True)
    test_settings.mkdir(exist_ok=True)
    
    try:
        # Initialize backup manager
        backup_manager = UILayoutBackupManager(test_settings, test_userdata)
        
        # Create a test backup
        backup_name = backup_manager.create_backup("structure_test", "Testing backup structure")
        
        if not backup_name:
            print("❌ Failed to create test backup")
            return False
        
        # Check backup file
        backup_file = backup_manager.backup_dir / f"{backup_name}.json"
        
        if not backup_file.exists():
            print("❌ Backup file not found")
            return False
        
        print(f"✅ Backup file created: {backup_file}")
        
        # Check file content
        import json
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Verify required fields
        required_fields = ['timestamp', 'version', 'widgets', 'layout_config', 'custom_settings']
        for field in required_fields:
            if field not in backup_data:
                print(f"❌ Missing required field: {field}")
                return False
        
        print("✅ All required fields present in backup file")
        
        # Check metadata file
        metadata_file = backup_manager.backup_dir / 'backup_metadata.dat'
        if metadata_file.exists():
            print("✅ Backup metadata file created")
        else:
            print("⚠️ Backup metadata file not found")
        
        print("🎉 Backup file structure test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup test directories
        import shutil
        if test_userdata.exists():
            shutil.rmtree(test_userdata)
        if test_settings.exists():
            shutil.rmtree(test_settings)


def main():
    """Main test function"""
    print("🚀 Starting UI Layout Backup Manager Tests")
    print("=" * 50)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run tests
    test1_success = test_backup_manager()
    test2_success = test_backup_file_structure()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Backup Manager Test: {'✅ PASSED' if test1_success else '❌ FAILED'}")
    print(f"  File Structure Test: {'✅ PASSED' if test2_success else '❌ FAILED'}")
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! UI Layout Backup Manager is working correctly.")
        return 0
    else:
        print("\n💥 Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 