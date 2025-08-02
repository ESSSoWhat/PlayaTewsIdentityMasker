#!/usr/bin/env python3
"""
Start Main App Properly for PlayaTewsIdentityMasker
Ensures the main app runs with correct Qt application context
"""

import sys
import os
import time
from pathlib import Path

def start_main_app():
    """Start the main app with proper Qt application context"""
    print("🚀 Starting PlayaTewsIdentityMasker with proper Qt context...")
    print("=" * 60)
    
    try:
        # Set up environment
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
        os.environ['QT_SCALE_FACTOR'] = '1'
        
        # Import the main app
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        # Create userdata path
        userdata_path = Path("userdata")
        userdata_path.mkdir(exist_ok=True)
        
        print(f"✅ Userdata path: {userdata_path}")
        print("✅ Main app imported successfully")
        
        # Create and start the application
        print("🔧 Creating main application...")
        app = PlayaTewsIdentityMaskerApp(userdata_path)
        
        print("🔧 Initializing application...")
        app.initialize()
        
        print("🔧 Showing application...")
        app.show()
        
        print("✅ Main application started successfully!")
        print("🎯 The camera feed should now appear in the preview area.")
        print("\n📱 What to look for:")
        print("1. Main PlayaTewsIdentityMasker window should be visible")
        print("2. Camera feed should appear in the preview area")
        print("3. Face swap functionality should be available")
        print("4. Real-time processing should be working")
        
        # Keep the app running
        print("\n⏳ Application is running... Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping application...")
            app.finalize()
            print("✅ Application stopped")
        
    except Exception as e:
        print(f"❌ Error starting main app: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🎬 PlayaTewsIdentityMasker - Proper Startup")
    print("=" * 50)
    print()
    
    start_main_app()

if __name__ == "__main__":
    main() 