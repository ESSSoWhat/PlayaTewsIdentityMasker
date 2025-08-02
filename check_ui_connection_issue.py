#!/usr/bin/env python3
"""
Check UI Connection Issue for PlayaTewsIdentityMasker
Identifies why camera data isn't appearing in UI despite flowing to backend
"""

import sys
import time
from pathlib import Path

def check_ui_component_connection():
    """Check if UI components can connect to camera data"""
    print("🔍 Checking UI Component Connection...")
    print("=" * 50)
    
    try:
        # Import backend components
        sys.path.append('.')
        from apps.PlayaTewsIdentityMasker import backend
        
        # Create backend components
        backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)
        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        
        # Create camera source and get data
        camera_source = backend.CameraSource(
            weak_heap=backend_weak_heap, 
            bc_out=multi_sources_bc_out, 
            backend_db=None
        )
        
        camera_source.start()
        time.sleep(3)
        
        # Get camera data
        bcd_id = multi_sources_bc_out.get_write_id()
        print(f"Camera data available: write ID {bcd_id}")
        
        if bcd_id > 0:
            bcd = multi_sources_bc_out.get_by_id(bcd_id)
            if bcd is not None:
                bcd.assign_weak_heap(backend_weak_heap)
                frame_image_name = bcd.get_frame_image_name()
                frame_image = bcd.get_image(frame_image_name)
                
                if frame_image is not None:
                    print(f"✅ Camera data: {frame_image.shape}")
                    
                    # Test UI component creation
                    try:
                        from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFrameViewer import QBCFrameViewer
                        
                        # Create UI component with the same backend connection
                        frame_viewer = QBCFrameViewer(backend_weak_heap, multi_sources_bc_out)
                        print("✅ QBCFrameViewer created successfully")
                        
                        # Check if component has access to data
                        if hasattr(frame_viewer, 'get_frame_image_name'):
                            viewer_frame_name = frame_viewer.get_frame_image_name()
                            print(f"   Viewer frame name: {viewer_frame_name}")
                        
                        if hasattr(frame_viewer, 'get_image'):
                            viewer_image = frame_viewer.get_image(frame_image_name)
                            if viewer_image is not None:
                                print(f"   Viewer can access image: {viewer_image.shape}")
                            else:
                                print("   ❌ Viewer cannot access image")
                        
                        print("✅ UI component connection test successful")
                        
                    except Exception as e:
                        print(f"❌ UI component test error: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print("❌ No frame image available")
            else:
                print("❌ No backend connection data")
        else:
            print("❌ No camera data available")
        
        camera_source.stop()
        
    except Exception as e:
        print(f"❌ UI connection check error: {e}")
        import traceback
        traceback.print_exc()

def check_app_process_conflict():
    """Check if there's a process conflict with the running app"""
    print("\n🔍 Checking App Process Conflict...")
    print("=" * 50)
    
    import subprocess
    
    # Check for Python processes
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                          capture_output=True, text=True, shell=True)
    
    if "python.exe" in result.stdout:
        lines = result.stdout.split('\n')
        python_processes = [line for line in lines if "python.exe" in line]
        print(f"Found {len(python_processes)} Python processes running")
        
        # Check if any are using significant memory (likely the main app)
        main_app_processes = []
        for line in python_processes:
            if "MB" in line or "K" in line:
                parts = line.split()
                if len(parts) >= 5:
                    memory = parts[4]
                    if "MB" in memory or int(memory.replace(',', '')) > 1000000:  # > 1GB
                        main_app_processes.append(line.strip())
        
        if main_app_processes:
            print("⚠️ Main app processes detected:")
            for proc in main_app_processes:
                print(f"   {proc}")
            print("\n💡 The running app might be using the camera exclusively")
            print("   Try stopping the app and testing camera again")
            return True
        else:
            print("✅ No main app processes detected")
            return False
    else:
        print("✅ No Python processes running")
        return False

def check_camera_exclusive_access():
    """Check if camera is being used exclusively by another process"""
    print("\n🔍 Checking Camera Exclusive Access...")
    print("=" * 50)
    
    try:
        import cv2
        
        # Try to open camera
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print("✅ Camera is accessible")
                cap.release()
                return False
            else:
                print("⚠️ Camera opened but no frame - might be in use")
                cap.release()
                return True
        else:
            print("❌ Camera cannot be opened - might be in use")
            return True
            
    except Exception as e:
        print(f"❌ Camera access check error: {e}")
        return True

def main():
    print("🎬 PlayaTewsIdentityMasker - UI Connection Issue Check")
    print("=" * 60)
    print()
    
    check_ui_component_connection()
    has_conflict = check_app_process_conflict()
    camera_in_use = check_camera_exclusive_access()
    
    print("\n📊 Issue Analysis:")
    print("=" * 40)
    
    if has_conflict:
        print("⚠️ Process conflict detected!")
        print("   The running app might be using the camera exclusively")
        print("   This could prevent the UI from accessing camera data")
        print("\n🔧 Solution: Stop the main app and restart it")
    elif camera_in_use:
        print("⚠️ Camera access issue detected!")
        print("   Camera might be locked by another application")
        print("   This could prevent proper camera data flow")
        print("\n🔧 Solution: Close other camera applications")
    else:
        print("✅ No obvious conflicts detected")
        print("   The issue might be in the UI component configuration")
        print("   or the Qt application context")
        print("\n🔧 Solution: Check UI component settings")

if __name__ == "__main__":
    main() 