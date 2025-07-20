#!/usr/bin/env python3
"""
Test script to check file permissions and identify access denied issues
"""

import os
import sys
from pathlib import Path

def test_directory_permissions():
    """Test directory creation and write permissions"""
    print("🔍 Testing directory permissions...")
    
    test_dirs = [
        "userdata/ui_backups",
        "userdata/test_write",
        "settings/test_write"
    ]
    
    for test_dir in test_dirs:
        try:
            path = Path(test_dir)
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {test_dir}")
            
            # Test write permission
            test_file = path / "test_write.txt"
            with open(test_file, 'w') as f:
                f.write("test")
            print(f"✅ Write test passed: {test_file}")
            
            # Clean up
            test_file.unlink()
            print(f"✅ Delete test passed: {test_file}")
            
        except PermissionError as e:
            print(f"❌ Permission denied: {test_dir} - {e}")
        except Exception as e:
            print(f"❌ Error with {test_dir}: {e}")

def test_backup_manager_permissions():
    """Test backup manager permissions"""
    print("\n🔍 Testing backup manager permissions...")
    
    # Add the project root to the Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.UILayoutBackupManager import UILayoutBackupManager
        
        # Test with different paths
        test_paths = [
            (Path("userdata"), Path("settings")),
            (Path("userdata/ui_backups"), Path("settings")),
            (Path("."), Path("."))
        ]
        
        for userdata_path, settings_path in test_paths:
            try:
                print(f"Testing with userdata={userdata_path}, settings={settings_path}")
                backup_manager = UILayoutBackupManager(settings_path, userdata_path)
                print(f"✅ Backup manager initialized successfully")
                
                # Test backup creation
                backup_name = backup_manager.create_backup("test_permission", "Testing permissions")
                if backup_name:
                    print(f"✅ Backup created: {backup_name}")
                    
                    # Test listing
                    backups = backup_manager.list_backups()
                    print(f"✅ Listed {len(backups)} backups")
                    
                    # Clean up
                    backup_manager.delete_backup(backup_name)
                    print(f"✅ Backup deleted: {backup_name}")
                else:
                    print("❌ Failed to create backup")
                    
            except PermissionError as e:
                print(f"❌ Permission denied: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_application_startup():
    """Test application startup"""
    print("\n🔍 Testing application startup...")
    
    # Add the project root to the Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        # Test main app import
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        print("✅ Main app import successful")
        
        # Test OBS app import
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerOBSStyleApp import PlayaTewsIdentityMaskerOBSStyleApp
        print("✅ OBS app import successful")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Permission Tests")
    print("=" * 50)
    
    test_directory_permissions()
    test_backup_manager_permissions()
    test_application_startup()
    
    print("\n" + "=" * 50)
    print("📊 Permission test completed")
    
    # Check if running as administrator
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        print(f"Running as administrator: {'Yes' if is_admin else 'No'}")
    except:
        print("Could not determine admin status")

if __name__ == "__main__":
    main() 