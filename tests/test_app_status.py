#!/usr/bin/env python3
"""
Simple test to check if PlayaTewsIdentityMasker app is running
"""

import psutil
import os
import sys

def check_app_status():
    """Check if PlayaTewsIdentityMasker app is running"""
    print("🔍 Checking PlayaTewsIdentityMasker App Status")
    print("=" * 50)
    
    # Look for Python processes that might be running the app
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe':
                cmdline = proc.info['cmdline']
                if cmdline and any('PlayaTewsIdentityMasker' in arg for arg in cmdline):
                    python_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if python_processes:
        print(f"✅ Found {len(python_processes)} PlayaTewsIdentityMasker processes:")
        for proc in python_processes:
            try:
                cmdline = ' '.join(proc.info['cmdline'])
                print(f"   PID {proc.info['pid']}: {cmdline}")
            except:
                print(f"   PID {proc.info['pid']}: [Command line not accessible]")
        
        print("\n🎉 PlayaTewsIdentityMasker app is RUNNING!")
        print("📱 You should see the OBS-style interface with:")
        print("   • Left panel: Scenes and Sources")
        print("   • Center panel: Preview and Controls")
        print("   • Global Face Swap button: 'Face Swap: ON' (green)")
        print("   • All Controls button to access detailed settings")
        
    else:
        print("❌ No PlayaTewsIdentityMasker processes found")
        print("💡 Try running: python main.py run PlayaTewsIdentityMasker")
    
    # Check for global face swap state file
    state_file = "settings/global_face_swap_state.json"
    if os.path.exists(state_file):
        print(f"\n✅ Global face swap state file found: {state_file}")
    else:
        print(f"\n⚠️  Global face swap state file not found: {state_file}")

if __name__ == "__main__":
    check_app_status() 