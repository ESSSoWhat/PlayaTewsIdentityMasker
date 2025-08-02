#!/usr/bin/env python3
"""
Fix Main App Camera Native Integration for PlayaTewsIdentityMasker
Fixes the camera source so feed appears in the main app's preview area and processing views
"""

import cv2
import time
import numpy as np
from pathlib import Path
import sys
import os
import json
import shutil

def create_camera_settings_override():
    """Create camera settings that force DirectShow and proper initialization"""
    print("🔧 Creating Camera Settings Override...")
    print("=" * 50)
    
    # Create settings that force DirectShow backend
    camera_settings = {
        "device_idx": 0,
        "driver": 1,  # DirectShow
        "resolution": 3,  # 1280x720
        "fps": 30.0,
        "rotation": 0,
        "flip_horizontal": False,
        "settings_by_idx": {}
    }
    
    # Save to multiple locations to ensure it's picked up
    settings_files = [
        "settings/camera_override.json",
        "settings/global_face_swap_state.json",
        "demo_settings/settings/global_face_swap_state.json"
    ]
    
    for settings_file in settings_files:
        settings_path = Path(settings_file)
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        if "global_face_swap_state" in settings_file:
            # For global state files, include additional settings
            global_settings = {
                "enabled": True,
                "camera_backend": "DirectShow",
                "camera_index": 0,
                "timestamp": str(time.time())
            }
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(global_settings, f, indent=2)
        else:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(camera_settings, f, indent=2)
        
        print(f"✅ Created: {settings_path}")
    
    return settings_files

def create_patched_camera_source():
    """Create a patched camera source that forces DirectShow and proper initialization"""
    print("\n🔧 Creating Patched Camera Source...")
    print("=" * 50)
    
    # Read the original camera source
    original_file = "apps/PlayaTewsIdentityMasker/backend/CameraSource.py"
    backup_file = "apps/PlayaTewsIdentityMasker/backend/CameraSource.py.backup"
    
    # Create backup
    if not Path(backup_file).exists():
        shutil.copy2(original_file, backup_file)
        print(f"✅ Created backup: {backup_file}")
    
    # Read original content
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create patched content with forced DirectShow
    patched_content = content.replace(
        "cv_api = {_DriverType.COMPATIBLE: cv2.CAP_ANY,",
        """# Force DirectShow backend for compatibility
            cv_api = cv2.CAP_DSHOW  # Force DirectShow
            print(f"🔧 Forcing DirectShow backend for camera {state.device_idx}")
            # cv_api = {_DriverType.COMPATIBLE: cv2.CAP_ANY,"""
    )
    
    # Add enhanced initialization
    patched_content = patched_content.replace(
        "vcap = cv2.VideoCapture(state.device_idx, cv_api)",
        """# Enhanced camera initialization with retry logic
            max_retries = 3
            vcap = None
            
            for attempt in range(max_retries):
                try:
                    print(f"🔧 Camera initialization attempt {attempt + 1}/{max_retries}")
                    vcap = cv2.VideoCapture(state.device_idx, cv_api)
                    
                    if vcap.isOpened():
                        print(f"✅ Camera {state.device_idx} opened successfully with DirectShow")
                        break
                    else:
                        print(f"❌ Failed to open camera {state.device_idx}, attempt {attempt + 1}")
                        if vcap:
                            vcap.release()
                        time.sleep(1)
                except Exception as e:
                    print(f"❌ Camera initialization error: {e}")
                    if vcap:
                        vcap.release()
                    time.sleep(1)
            
            if vcap is None or not vcap.isOpened():
                print(f"❌ Failed to open camera {state.device_idx} after {max_retries} attempts")
                vcap = cv2.VideoCapture(state.device_idx, cv_api)  # Fallback to original method"""
    )
    
    # Add enhanced frame reading
    patched_content = patched_content.replace(
        "ret, img = self.vcap.read()",
        """# Enhanced frame reading with validation
            ret, img = self.vcap.read()
            if ret:
                # Validate frame
                if img is not None and img.size > 0:
                    print(f"📹 Camera frame read successful: {img.shape}" if self.bcd_uid % 30 == 0 else "", end="")
                else:
                    print(f"⚠️ Invalid frame received from camera")
                    ret = False"""
    )
    
    # Write patched content
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(patched_content)
    
    print(f"✅ Patched: {original_file}")
    return original_file

def create_enhanced_main_app():
    """Create an enhanced main app that ensures camera is properly initialized"""
    print("\n🔧 Creating Enhanced Main App...")
    print("=" * 50)
    
    # Read the original main app
    original_file = "apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerApp.py"
    backup_file = "apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerApp.py.backup"
    
    # Create backup
    if not Path(backup_file).exists():
        shutil.copy2(original_file, backup_file)
        print(f"✅ Created backup: {backup_file}")
    
    # Read original content
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add camera initialization enhancement
    camera_init_code = """
        # Enhanced camera source initialization
        print("🔧 Initializing camera source with DirectShow backend...")
        camera_source = self.camera_source = backend.CameraSource(weak_heap=backend_weak_heap, bc_out=multi_sources_bc_out, backend_db=backend_db)
        
        # Force camera to start with DirectShow
        try:
            camera_source.start()
            print("✅ Camera source started successfully")
            
            # Wait a moment for camera to initialize
            time.sleep(2)
            
            # Check if camera is working
            if hasattr(camera_source, 'is_started') and camera_source.is_started():
                print("✅ Camera source is running")
            else:
                print("⚠️ Camera source may not be running properly")
        except Exception as e:
            print(f"❌ Error starting camera source: {e}")
        """
    
    # Replace the camera source initialization
    content = content.replace(
        "camera_source  = self.camera_source  = backend.CameraSource (weak_heap=backend_weak_heap, bc_out=multi_sources_bc_out, backend_db=backend_db)",
        camera_init_code
    )
    
    # Write enhanced content
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Enhanced: {original_file}")
    return original_file

def create_camera_test_launcher():
    """Create a launcher that tests the main app with camera fixes"""
    print("\n🔧 Creating Camera Test Launcher...")
    print("=" * 50)
    
    launcher_code = '''#!/usr/bin/env python3
"""
Camera Test Launcher for PlayaTewsIdentityMasker
Tests the main app with camera fixes applied
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def test_main_app_camera():
    """Test the main app with camera fixes"""
    print("🎬 Testing Main App Camera Integration...")
    print("=" * 50)
    
    try:
        # Start the main app
        print("🚀 Starting PlayaTewsIdentityMasker with camera fixes...")
        print("   Camera feed should now appear in the preview area")
        print("   Processing views should show camera data")
        print()
        
        # Run the main app
        result = subprocess.run([
            sys.executable, "main.py", "run", "PlayaTewsIdentityMasker"
        ], capture_output=False, text=True)
        
        print("✅ Main app test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing main app: {e}")
        return False

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Test Launcher")
    print("=" * 60)
    print()
    
    success = test_main_app_camera()
    
    print("\\n📊 Results:")
    print("=" * 40)
    if success:
        print("✅ Main app camera test completed")
        print("   Check if camera feed appears in preview area")
    else:
        print("❌ Main app camera test failed")
    
    print("\\n💡 If camera feed still doesn't appear:")
    print("   1. Check camera permissions")
    print("   2. Ensure virtual camera app is running")
    print("   3. Try restarting the application")

if __name__ == "__main__":
    main()
'''
    
    with open("test_main_app_camera.py", 'w', encoding='utf-8') as f:
        f.write(launcher_code)
    
    print("✅ Created: test_main_app_camera.py")
    print("   Run this to test the main app with camera fixes")

def create_restore_backup_script():
    """Create a script to restore original files if needed"""
    print("\n🔧 Creating Restore Backup Script...")
    print("=" * 50)
    
    restore_code = '''#!/usr/bin/env python3
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
    
    print("\\n✅ Backup restoration completed")
    print("   Original files have been restored")

if __name__ == "__main__":
    restore_backups()
'''
    
    with open("restore_backups.py", 'w', encoding='utf-8') as f:
        f.write(restore_code)
    
    print("✅ Created: restore_backups.py")
    print("   Run this if you need to restore original files")

def main():
    print("🎬 PlayaTewsIdentityMasker - Main App Camera Native Fix")
    print("=" * 60)
    print()
    print("🔍 Issue: Camera feed not appearing in main app preview area")
    print("🎯 Solution: Fix main app camera source for native integration")
    print()
    
    try:
        # Create camera settings override
        create_camera_settings_override()
        
        # Create patched camera source
        create_patched_camera_source()
        
        # Create enhanced main app
        create_enhanced_main_app()
        
        # Create test launcher
        create_camera_test_launcher()
        
        # Create restore script
        create_restore_backup_script()
        
        print("\n🎉 Main App Camera Native Fix Complete!")
        print("=" * 40)
        print()
        print("📋 What was created:")
        print("   ✅ Camera settings overrides (multiple locations)")
        print("   ✅ Patched camera source with DirectShow forcing")
        print("   ✅ Enhanced main app with better initialization")
        print("   ✅ test_main_app_camera.py - Test launcher")
        print("   ✅ restore_backups.py - Restore script")
        print()
        print("🚀 Next steps:")
        print("   1. Run: python test_main_app_camera.py")
        print("   2. Camera feed should now appear in main app preview area")
        print("   3. Processing views should show camera data")
        print("   4. If issues occur, run: python restore_backups.py")
        print()
        print("💡 The fix addresses:")
        print("   - Forces DirectShow backend for camera compatibility")
        print("   - Enhances camera initialization with retry logic")
        print("   - Improves frame reading validation")
        print("   - Ensures camera data reaches preview area")
        
    except Exception as e:
        print(f"❌ Error creating main app camera fix: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 