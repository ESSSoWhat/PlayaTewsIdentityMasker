#!/usr/bin/env python3
"""
Diagnostic script to check camera data flow and UI component status
"""

import sys
import os
import time
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_camera_settings():
    """Check camera settings in configuration files"""
    print("🔍 Checking camera settings...")
    
    settings_files = [
        "settings/camera_override.json",
        "settings/global_face_swap_state.json", 
        "demo_settings/settings/global_face_swap_state.json"
    ]
    
    for file_path in settings_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'camera' in data:
                        print(f"✅ {file_path}: Camera settings found")
                        print(f"   Device: {data['camera'].get('device_idx', 'Not set')}")
                        print(f"   Driver: {data['camera'].get('driver', 'Not set')}")
                        print(f"   Resolution: {data['camera'].get('resolution', 'Not set')}")
                    else:
                        print(f"❌ {file_path}: No camera settings found")
            except Exception as e:
                print(f"❌ {file_path}: Error reading file - {e}")
        else:
            print(f"❌ {file_path}: File not found")

def check_camera_source_status():
    """Check if camera source is working"""
    print("\n🔍 Checking camera source status...")
    
    try:
        import cv2
        
        # Test camera access
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Camera 0 (DirectShow): Working - Frame size: {frame.shape}")
            else:
                print("❌ Camera 0 (DirectShow): No frame data")
            cap.release()
        else:
            print("❌ Camera 0 (DirectShow): Cannot open camera")
            
    except Exception as e:
        print(f"❌ Camera test failed: {e}")

def check_backend_components():
    """Check backend component status"""
    print("\n🔍 Checking backend components...")
    
    try:
        # Import backend components
        from apps.PlayaTewsIdentityMasker.backend import CameraSource, BackendBase
        from xlib import lib_csw
        
        print("✅ Backend components imported successfully")
        
        # Check if we can create a backend connection
        try:
            bc = lib_csw.BackendConnection()
            print("✅ BackendConnection created successfully")
        except Exception as e:
            print(f"❌ BackendConnection creation failed: {e}")
            
    except Exception as e:
        print(f"❌ Backend component import failed: {e}")

def check_ui_components():
    """Check UI component status"""
    print("\n🔍 Checking UI components...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from apps.PlayaTewsIdentityMasker.ui.QUnifiedLiveSwap import QUnifiedLiveSwap
        from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFrameViewer import QBCFrameViewer
        
        print("✅ UI components imported successfully")
        
        # Check if QApplication exists
        app = QApplication.instance()
        if app:
            print("✅ QApplication instance found")
        else:
            print("❌ No QApplication instance found")
            
    except Exception as e:
        print(f"❌ UI component import failed: {e}")

def check_data_flow():
    """Check if data is flowing through the system"""
    print("\n🔍 Checking data flow...")
    
    try:
        # Check if there are any backend connection files
        temp_dir = os.path.expanduser("~/AppData/Local/Temp")
        dep_files = [f for f in os.listdir(temp_dir) if f.startswith('dep-') and f.endswith('.d')]
        
        if dep_files:
            print(f"✅ Found {len(dep_files)} backend connection files in temp directory")
            # Check if any are readable
            readable_count = 0
            for dep_file in dep_files[:5]:  # Check first 5
                try:
                    with open(os.path.join(temp_dir, dep_file), 'rb') as f:
                        data = f.read()
                        if len(data) > 0:
                            readable_count += 1
                except:
                    pass
            print(f"   {readable_count} out of 5 tested files contain data")
        else:
            print("❌ No backend connection files found")
            
    except Exception as e:
        print(f"❌ Data flow check failed: {e}")

def main():
    print("🚀 Camera UI Flow Diagnostic")
    print("=" * 50)
    
    check_camera_settings()
    check_camera_source_status()
    check_backend_components()
    check_ui_components()
    check_data_flow()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("- If camera settings are missing, run: python fix_camera_settings.py")
    print("- If camera source fails, check camera permissions")
    print("- If UI components fail, ensure QApplication is running")
    print("- If data flow fails, restart the main app")

if __name__ == "__main__":
    main() 