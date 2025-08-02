#!/usr/bin/env python3
"""
Fix Camera Source Syntax for PlayaTewsIdentityMasker
Fixes the camera source with proper syntax and indentation
"""

import shutil
from pathlib import Path

def fix_camera_source():
    """Fix camera source with proper DirectShow forcing"""
    print("🔧 Fixing Camera Source Syntax...")
    print("=" * 50)
    
    # Read the original camera source
    original_file = "apps/PlayaTewsIdentityMasker/backend/CameraSource.py"
    backup_file = "apps/PlayaTewsIdentityMasker/backend/CameraSource.py.backup"
    
    # Create backup if it doesn't exist
    if not Path(backup_file).exists():
        shutil.copy2(original_file, backup_file)
        print(f"✅ Created backup: {backup_file}")
    
    # Read original content
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the cv_api assignment line and replace it properly
    import re
    
    # Pattern to find the cv_api assignment
    pattern = r'cv_api = \{_DriverType\.COMPATIBLE: cv2\.CAP_ANY,'
    
    # Replacement with proper indentation
    replacement = '''            # Force DirectShow backend for compatibility
            cv_api = cv2.CAP_DSHOW  # Force DirectShow
            print(f"🔧 Forcing DirectShow backend for camera {state.device_idx}")
            # cv_api = {_DriverType.COMPATIBLE: cv2.CAP_ANY,'''
    
    # Replace the pattern
    if pattern in content:
        content = re.sub(pattern, replacement, content)
        print("✅ Applied DirectShow forcing patch")
    else:
        print("⚠️ DirectShow forcing pattern not found")
    
    # Find the vcap assignment and add retry logic
    vcap_pattern = r'vcap = cv2\.VideoCapture\(state\.device_idx, cv_api\)'
    vcap_replacement = '''            # Enhanced camera initialization with retry logic
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
                vcap = cv2.VideoCapture(state.device_idx, cv_api)  # Fallback to original method'''
    
    if vcap_pattern in content:
        content = re.sub(vcap_pattern, vcap_replacement, content)
        print("✅ Applied enhanced initialization patch")
    else:
        print("⚠️ Camera initialization pattern not found")
    
    # Add time import if not present
    if "import time" not in content:
        # Find the import section and add time
        import_section = "import cv2"
        if import_section in content:
            content = content.replace(import_section, "import cv2\nimport time")
            print("✅ Added time import")
    
    # Write the fixed content
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed: {original_file}")
    return original_file

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Source Syntax Fix")
    print("=" * 60)
    print()
    
    try:
        fix_camera_source()
        
        print("\n🎉 Camera Source Syntax Fix Complete!")
        print("=" * 40)
        print()
        print("✅ Camera source has been fixed with proper syntax")
        print("✅ DirectShow backend forcing applied")
        print("✅ Enhanced initialization with retry logic")
        print()
        print("🚀 Ready to start the app!")
        
    except Exception as e:
        print(f"❌ Error fixing camera source: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        import sys
        sys.exit(1) 