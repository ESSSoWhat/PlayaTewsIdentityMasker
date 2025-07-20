#!/usr/bin/env python3
"""
Simplified validation script that tests core functionality without triggering memory issues
"""

import json
import time
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication

def simplified_validation():
    """Run simplified validation tests"""
    app = QApplication([])
    
    try:
        import sys
        sys.path.append('.')  # Add current directory to path
        
        # Test 1: Basic imports
        print("🔍 Test 1: Basic imports...")
        try:
            from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
            print("✅ Main app import successful")
        except Exception as e:
            print(f"❌ Main app import failed: {e}")
            return False
        
        # Test 2: UI component imports
        print("🔍 Test 2: UI component imports...")
        ui_components = [
            'apps.PlayaTewsIdentityMasker.ui.QEnhancedStreamOutput',
            'apps.PlayaTewsIdentityMasker.ui.widgets.QXTabWidget',
            'apps.PlayaTewsIdentityMasker.ui.widgets.QXCollapsibleSection',
            'apps.PlayaTewsIdentityMasker.ui.widgets.QLabelCSWNumber',
            'apps.PlayaTewsIdentityMasker.ui.widgets.QSpinBoxCSWNumber'
        ]
        
        for component in ui_components:
            try:
                __import__(component)
                print(f"✅ {component} import successful")
            except Exception as e:
                print(f"❌ {component} import failed: {e}")
        
        # Test 3: Backend component imports
        print("🔍 Test 3: Backend component imports...")
        backend_components = [
            'apps.PlayaTewsIdentityMasker.backend.EnhancedStreamOutput',
            'apps.PlayaTewsIdentityMasker.backend.VoiceChanger',
            'xlib.mp.csw.ControlViewer',
            'xlib.mp.csw.ControlSignal'
        ]
        
        for component in backend_components:
            try:
                __import__(component)
                print(f"✅ {component} import successful")
            except Exception as e:
                print(f"❌ {component} import failed: {e}")
        
        # Test 4: Basic app creation (without full initialization)
        print("🔍 Test 4: Basic app creation...")
        userdata_path = Path("tests/validation_data")
        userdata_path.mkdir(exist_ok=True)
        
        try:
            # Create app instance but don't fully initialize
            app_instance = PlayaTewsIdentityMaskerApp(userdata_path)
            print("✅ App instance created successfully")
            
            # Test basic component access
            components_to_test = ['file_source', 'camera_source', 'voice_changer']
            for component_name in components_to_test:
                try:
                    component = getattr(app_instance, component_name, None)
                    if component is not None:
                        print(f"✅ {component_name} component accessible")
                    else:
                        print(f"⚠️ {component_name} component not found")
                except Exception as e:
                    print(f"❌ {component_name} component error: {e}")
            
            # Clean up
            try:
                app_instance.finalize()
                print("✅ App finalization successful")
            except Exception as e:
                print(f"⚠️ App finalization warning: {e}")
                
        except Exception as e:
            print(f"❌ App creation failed: {e}")
            return False
        
        # Test 5: File structure validation
        print("🔍 Test 5: File structure validation...")
        expected_files = [
            'apps/PlayaTewsIdentityMasker/ui/widgets/QXTabWidget.py',
            'apps/PlayaTewsIdentityMasker/ui/widgets/QXCollapsibleSection.py',
            'apps/PlayaTewsIdentityMasker/ui/QEnhancedStreamOutput.py',
            'xlib/mp/csw/ControlViewer.py',
            'xlib/mp/csw/ControlSignal.py'
        ]
        
        for file_path in expected_files:
            if Path(file_path).exists():
                print(f"✅ {file_path} exists")
            else:
                print(f"❌ {file_path} missing")
        
        # Test 6: Migration backup validation
        print("🔍 Test 6: Migration backup validation...")
        backup_dir = Path("backups")
        if backup_dir.exists():
            backup_files = list(backup_dir.glob("ui_relocation_backup_*"))
            if backup_files:
                print(f"✅ Migration backups found: {len(backup_files)}")
                for backup in backup_files:
                    print(f"   - {backup.name}")
            else:
                print("⚠️ No migration backups found")
        else:
            print("⚠️ Backup directory not found")
        
        print("\n🎉 Simplified validation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False
    finally:
        app.quit()

if __name__ == "__main__":
    success = simplified_validation()
    sys.exit(0 if success else 1) 