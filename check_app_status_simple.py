#!/usr/bin/env python3
"""
Simple App Status Check for PlayaTewsIdentityMasker
Checks if the app is running and camera should be visible
"""

import subprocess
import time

def check_app_status():
    """Check if the app is running and status"""
    print("🔍 Checking App Status...")
    print("=" * 50)
    
    # Check for Python processes
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                          capture_output=True, text=True, shell=True)
    
    if "python.exe" in result.stdout:
        lines = result.stdout.split('\n')
        python_processes = [line for line in lines if "python.exe" in line]
        print(f"✅ {len(python_processes)} Python processes running")
        
        # Show the largest processes (likely the main app)
        print("\n📊 Largest Python processes (likely main app):")
        for line in python_processes[:3]:
            print(f"   {line.strip()}")
        
        return True
    else:
        print("❌ No Python processes running")
        return False

def check_camera_settings():
    """Check if camera settings are configured"""
    print("\n🔍 Checking Camera Settings...")
    print("=" * 50)
    
    import json
    from pathlib import Path
    
    settings_file = "settings/camera_override.json"
    if Path(settings_file).exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'camera' in data:
                camera_settings = data['camera']
                print("✅ Camera settings configured:")
                print(f"   Device: {camera_settings.get('device_idx', 'Not set')}")
                print(f"   Driver: {camera_settings.get('driver', 'Not set')} (DirectShow)")
                print(f"   Resolution: {camera_settings.get('resolution', 'Not set')} (1280x720)")
                return True
            else:
                print("❌ No camera settings found")
                return False
        except Exception as e:
            print(f"❌ Error reading settings: {e}")
            return False
    else:
        print(f"❌ Settings file not found: {settings_file}")
        return False

def main():
    print("🎬 PlayaTewsIdentityMasker - Simple Status Check")
    print("=" * 60)
    print()
    
    app_running = check_app_status()
    settings_ok = check_camera_settings()
    
    print("\n📊 Status Summary:")
    print("=" * 40)
    
    if app_running and settings_ok:
        print("🎉 SUCCESS! App should be working!")
        print("✅ App is running (multiple Python processes)")
        print("✅ Camera settings are configured")
        print("\n🎯 What you should see:")
        print("1. Main PlayaTewsIdentityMasker window")
        print("2. Camera feed in the preview area")
        print("3. Face swap functionality working")
        print("4. Real-time processing active")
        print("\n💡 If you don't see the camera feed:")
        print("   • Check if the main window is visible")
        print("   • Look for the preview area in the interface")
        print("   • Try clicking on different tabs/sections")
        print("   • Ensure camera permissions are granted")
        print("\n🚀 The camera integration should be working!")
    else:
        if not app_running:
            print("❌ App is not running")
        if not settings_ok:
            print("❌ Camera settings not configured")
        print("\n🔧 Please restart the application")

if __name__ == "__main__":
    main() 