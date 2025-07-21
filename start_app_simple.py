#!/usr/bin/env python3
"""
Simple PlayaTewsIdentityMasker App Starter
"""

import sys
import os
from pathlib import Path

def start_app():
    """Start the PlayaTewsIdentityMasker app"""
    print("🎯 Starting PlayaTewsIdentityMasker...")
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        # Try to import the app
        print("📦 Importing application...")
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        # Set up userdata path
        userdata_path = current_dir / "userdata"
        userdata_path.mkdir(exist_ok=True)
        
        print(f"📁 Using userdata path: {userdata_path}")
        
        # Create and run the app
        print("🚀 Creating application...")
        app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        
        print("✅ Application created successfully!")
        print("🪟 The app window should appear shortly...")
        print("💡 If you don't see it, check your taskbar or try Alt+Tab")
        
        # Run the app
        app.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        print("💡 Check the log file: playatewsidentitymasker.log")
        return False
    
    return True

if __name__ == "__main__":
    success = start_app()
    if not success:
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Python is installed")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check the log file for detailed errors")
        print("4. Try running as Administrator")
        
        input("\nPress Enter to exit...") 