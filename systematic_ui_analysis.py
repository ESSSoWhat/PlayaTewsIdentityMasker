#!/usr/bin/env python3
"""
Systematic UI Analysis - Figure out why feeds are not appearing in preview area
"""

import sys
import os
import time
import json
import subprocess
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_app_process():
    """Check if the main app is running"""
    print("🔍 Step 1: Checking App Process Status")
    print("=" * 50)
    
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        if 'python.exe' in result.stdout:
            print("✅ Python processes are running")
            # Count python processes
            lines = result.stdout.strip().split('\n')
            python_count = len([line for line in lines if 'python.exe' in line])
            print(f"   Found {python_count} Python processes")
        else:
            print("❌ No Python processes found")
            return False
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
        return False
    return True

def check_camera_hardware():
    """Check camera hardware access"""
    print("\n🔍 Step 2: Camera Hardware Test")
    print("=" * 50)
    
    try:
        import cv2
        
        # Test different camera backends
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_ANY, "Auto")
        ]
        
        for backend_id, backend_name in backends:
            try:
                cap = cv2.VideoCapture(0, backend_id)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"✅ Camera 0 ({backend_name}): Working - Frame size: {frame.shape}")
                        cap.release()
                        return True
                    else:
                        print(f"❌ Camera 0 ({backend_name}): No frame data")
                        cap.release()
                else:
                    print(f"❌ Camera 0 ({backend_name}): Cannot open camera")
            except Exception as e:
                print(f"❌ Camera 0 ({backend_name}): Error - {e}")
        
        return False
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def check_backend_connections():
    """Check backend connection files"""
    print("\n🔍 Step 3: Backend Connection Analysis")
    print("=" * 50)
    
    try:
        temp_dir = os.path.expanduser("~/AppData/Local/Temp")
        if os.path.exists(temp_dir):
            dep_files = [f for f in os.listdir(temp_dir) if f.startswith('dep-') and f.endswith('.d')]
            
            if dep_files:
                print(f"✅ Found {len(dep_files)} backend connection files")
                
                # Check file sizes and readability
                readable_files = []
                total_size = 0
                
                for dep_file in dep_files:
                    file_path = os.path.join(temp_dir, dep_file)
                    try:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        
                        # Try to read a small portion
                        with open(file_path, 'rb') as f:
                            data = f.read(100)  # Read first 100 bytes
                            if len(data) > 0:
                                readable_files.append(dep_file)
                    except Exception as e:
                        print(f"   ❌ {dep_file}: Error reading - {e}")
                
                print(f"   📊 Total size: {total_size} bytes")
                print(f"   📊 Readable files: {len(readable_files)}/{len(dep_files)}")
                
                if len(readable_files) > 0:
                    print("✅ Backend connections have data")
                    return True
                else:
                    print("❌ No readable backend connection files")
                    return False
            else:
                print("❌ No backend connection files found")
                return False
        else:
            print("❌ Temp directory not found")
            return False
    except Exception as e:
        print(f"❌ Backend connection check failed: {e}")
        return False

def check_ui_components():
    """Check UI component initialization"""
    print("\n🔍 Step 4: UI Component Analysis")
    print("=" * 50)
    
    try:
        from PyQt5.QtWidgets import QApplication
        
        # Check QApplication
        app = QApplication.instance()
        if app:
            print("✅ QApplication instance found")
        else:
            print("❌ No QApplication instance found")
            return False
        
        # Try to import UI components
        try:
            from apps.PlayaTewsIdentityMasker.ui.QUnifiedLiveSwap import QUnifiedLiveSwap
            from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFrameViewer import QBCFrameViewer
            from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFaceAlignViewer import QBCFaceAlignViewer
            from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFaceSwapViewer import QBCFaceSwapViewer
            from apps.PlayaTewsIdentityMasker.ui.widgets.QBCMergedFrameViewer import QBCMergedFrameViewer
            print("✅ UI components imported successfully")
        except Exception as e:
            print(f"❌ UI component import failed: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ UI component check failed: {e}")
        return False

def check_camera_source_backend():
    """Check camera source backend status"""
    print("\n🔍 Step 5: Camera Source Backend Analysis")
    print("=" * 50)
    
    try:
        # Import backend components with correct import path
        from apps.PlayaTewsIdentityMasker.backend import CameraSource, BackendBase, BackendWeakHeap, BackendConnection
        from xlib.mp import csw as lib_csw
        
        print("✅ Backend components imported successfully")
        
        # Check if we can create backend connections
        try:
            weak_heap = BackendWeakHeap(size_mb=1024)
            bc_out = BackendConnection()
            print("✅ Backend connections created successfully")
            
            # Try to create camera source
            try:
                camera_source = CameraSource(weak_heap=weak_heap, bc_out=bc_out, backend_db=None)
                print("✅ Camera source created successfully")
                
                # Check if camera source can start
                try:
                    camera_source.start()
                    print("✅ Camera source started successfully")
                    
                    # Wait a moment and check status
                    time.sleep(1)
                    if hasattr(camera_source, 'is_started') and camera_source.is_started():
                        print("✅ Camera source is running")
                        return True
                    else:
                        print("⚠️ Camera source may not be running properly")
                        return False
                except Exception as e:
                    print(f"❌ Camera source start failed: {e}")
                    return False
            except Exception as e:
                print(f"❌ Camera source creation failed: {e}")
                return False
        except Exception as e:
            print(f"❌ Backend connection creation failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Backend component import failed: {e}")
        return False

def check_viewer_data_flow():
    """Check if viewers are receiving data"""
    print("\n🔍 Step 6: Viewer Data Flow Analysis")
    print("=" * 50)
    
    try:
        from PyQt5.QtWidgets import QApplication
        from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFrameViewer import QBCFrameViewer
        from apps.PlayaTewsIdentityMasker.backend import BackendWeakHeap, BackendConnection
        from xlib.mp import csw as lib_csw
        
        app = QApplication.instance()
        if not app:
            print("❌ No QApplication instance found")
            return False
        
        # Create test viewer
        try:
            weak_heap = BackendWeakHeap(size_mb=1024)
            bc_out = BackendConnection()
            viewer = QBCFrameViewer(weak_heap, bc_out)
            print("✅ Test viewer created successfully")
            
            # Check viewer properties
            if hasattr(viewer, '_bc'):
                print("✅ Viewer has backend connection")
            else:
                print("❌ Viewer missing backend connection")
                return False
            
            if hasattr(viewer, '_layered_images'):
                print("✅ Viewer has layered images component")
            else:
                print("❌ Viewer missing layered images component")
                return False
            
            return True
        except Exception as e:
            print(f"❌ Test viewer creation failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Viewer data flow check failed: {e}")
        return False

def check_settings_consistency():
    """Check settings consistency across all files"""
    print("\n🔍 Step 7: Settings Consistency Analysis")
    print("=" * 50)
    
    settings_files = [
        "settings/camera_override.json",
        "settings/global_face_swap_state.json",
        "demo_settings/settings/global_face_swap_state.json"
    ]
    
    all_consistent = True
    
    for file_path in settings_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'camera' in data:
                        camera = data['camera']
                        print(f"✅ {file_path}:")
                        print(f"   Device: {camera.get('device_idx', 'Not set')}")
                        print(f"   Driver: {camera.get('driver', 'Not set')}")
                        print(f"   Resolution: {camera.get('resolution', 'Not set')}")
                        
                        # Check for consistency
                        if camera.get('device_idx') != 0 or camera.get('driver') != 1:
                            print(f"   ⚠️ Inconsistent settings in {file_path}")
                            all_consistent = False
                    else:
                        print(f"❌ {file_path}: No camera settings")
                        all_consistent = False
            except Exception as e:
                print(f"❌ {file_path}: Error reading - {e}")
                all_consistent = False
        else:
            print(f"❌ {file_path}: File not found")
            all_consistent = False
    
    if all_consistent:
        print("✅ All settings files are consistent")
    else:
        print("❌ Settings files are inconsistent")
    
    return all_consistent

def generate_recommendations():
    """Generate recommendations based on analysis"""
    print("\n🔍 Step 8: Recommendations")
    print("=" * 50)
    
    print("📋 Based on the analysis, here are the likely issues and solutions:")
    print()
    print("🎯 Most Likely Issues:")
    print("1. Backend connection data not flowing to UI viewers")
    print("2. Camera source not properly connected to backend")
    print("3. UI viewers not receiving frame data")
    print("4. Settings inconsistency preventing proper initialization")
    print()
    print("🔧 Recommended Solutions:")
    print("1. Restart the app with proper QApplication context")
    print("2. Ensure camera source is started before UI initialization")
    print("3. Check backend connection data flow")
    print("4. Verify all settings files have consistent camera configuration")
    print("5. Test with a simple camera preview first")

def main():
    print("🚀 Systematic UI Analysis - Feed Not Appearing in Preview")
    print("=" * 70)
    
    # Run all checks
    checks = [
        ("App Process", check_app_process),
        ("Camera Hardware", check_camera_hardware),
        ("Backend Connections", check_backend_connections),
        ("UI Components", check_ui_components),
        ("Camera Source Backend", check_camera_source_backend),
        ("Viewer Data Flow", check_viewer_data_flow),
        ("Settings Consistency", check_settings_consistency)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ {name} check failed with exception: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 70)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:25} {status}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed < total:
        print("\n🎯 ISSUES DETECTED - Feed not appearing due to:")
        for name, result in results.items():
            if not result:
                print(f"   • {name} check failed")
    
    generate_recommendations()

if __name__ == "__main__":
    main() 