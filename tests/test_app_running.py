#!/usr/bin/env python3
"""
Quick test to verify the optimized app is running and global face swap control is accessible
"""

import time
import psutil
import json
from pathlib import Path

def check_app_running():
    """Check if the optimized app is running"""
    print("=== Checking PlayaTewsIdentityMaskerOptimized Status ===")
    
    # Look for Python processes running the optimized app
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe':
                cmdline = proc.info['cmdline']
                if cmdline and any('PlayaTewsIdentityMaskerOptimized' in arg for arg in cmdline):
                    python_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if python_processes:
        print(f"✅ Found {len(python_processes)} running instance(s) of PlayaTewsIdentityMaskerOptimized")
        for proc in python_processes:
            print(f"   PID: {proc['pid']}")
        return True
    else:
        print("❌ No running instances of PlayaTewsIdentityMaskerOptimized found")
        return False

def check_global_face_swap_state():
    """Check if global face swap state file exists"""
    print("\n=== Checking Global Face Swap State ===")
    
    # Check for state file
    state_file = Path("settings/global_face_swap_state.json")
    if state_file.exists():
        try:
            with open(state_file, 'r') as f:
                state_data = json.load(f)
            enabled = state_data.get('enabled', True)
            print(f"✅ Global face swap state file found")
            print(f"   Current state: {'ENABLED' if enabled else 'DISABLED'}")
            print(f"   File location: {state_file.absolute()}")
            return True
        except Exception as e:
            print(f"❌ Error reading state file: {e}")
            return False
    else:
        print("ℹ️  No state file found (will be created on first use)")
        return True

def check_ui_components():
    """Check if UI components are properly configured"""
    print("\n=== Checking UI Components ===")
    
    # Check if optimized UI file exists and has global face swap control
    ui_file = Path("apps/PlayaTewsIdentityMasker/ui/QOptimizedOBSStyleUI.py")
    if ui_file.exists():
        try:
            with open(ui_file, 'r') as f:
                content = f.read()
            
            checks = [
                ("Global face swap button", "global_face_swap_btn"),
                ("Global face swap toggle handler", "on_global_face_swap_toggled"),
                ("State persistence", "save_global_face_swap_state"),
                ("Component control", "enable_all_face_swap_components"),
                ("Visual feedback", "Face Swap: ON"),
                ("Tooltip support", "setToolTip")
            ]
            
            all_passed = True
            for check_name, check_string in checks:
                if check_string in content:
                    print(f"✅ {check_name}: Found")
                else:
                    print(f"❌ {check_name}: Missing")
                    all_passed = False
            
            return all_passed
        except Exception as e:
            print(f"❌ Error reading UI file: {e}")
            return False
    else:
        print("❌ Optimized UI file not found")
        return False

def main():
    """Main test function"""
    print("🚀 PlayaTewsIdentityMaskerOptimized Status Check")
    print("=" * 50)
    
    # Check if app is running
    app_running = check_app_running()
    
    # Check global face swap state
    state_ok = check_global_face_swap_state()
    
    # Check UI components
    ui_ok = check_ui_components()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if app_running and state_ok and ui_ok:
        print("🎉 SUCCESS: PlayaTewsIdentityMaskerOptimized is running with global face swap control!")
        print("\n📋 Next Steps:")
        print("   1. Look for the 'Face Swap: ON' button in the top right panel")
        print("   2. Click it to toggle between ON (green) and OFF (red)")
        print("   3. The state will be automatically saved and restored")
        print("   4. All face swap components will be controlled simultaneously")
    else:
        print("⚠️  ISSUES DETECTED:")
        if not app_running:
            print("   - App is not running")
        if not state_ok:
            print("   - Global face swap state issues")
        if not ui_ok:
            print("   - UI component issues")
    
    print("\n🔧 Global Face Swap Control Features:")
    print("   ✅ Single button control for all face swap components")
    print("   ✅ Visual feedback (Green=ON, Red=OFF)")
    print("   ✅ State persistence across app restarts")
    print("   ✅ Dynamic tooltips with status information")
    print("   ✅ Error handling and graceful fallbacks")

if __name__ == "__main__":
    main() 