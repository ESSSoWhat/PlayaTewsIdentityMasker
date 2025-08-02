#!/usr/bin/env python3
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
    
    print("\n📊 Results:")
    print("=" * 40)
    if success:
        print("✅ Main app camera test completed")
        print("   Check if camera feed appears in preview area")
    else:
        print("❌ Main app camera test failed")
    
    print("\n💡 If camera feed still doesn't appear:")
    print("   1. Check camera permissions")
    print("   2. Ensure virtual camera app is running")
    print("   3. Try restarting the application")

if __name__ == "__main__":
    main()
