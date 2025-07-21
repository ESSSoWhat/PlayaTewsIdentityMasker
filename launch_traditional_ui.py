#!/usr/bin/env python3
"""
PlayaTewsIdentityMasker Traditional UI Launcher
This is the LEGACY interface for advanced users who prefer the traditional layout.
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the traditional UI (legacy interface)"""
    print("🚀 PlayaTewsIdentityMasker Traditional UI Launcher")
    print("📋 This is the LEGACY interface for advanced users")
    print("🔧 Provides traditional panel-based layout")
    print()
    
    # Import and run the traditional application
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        # Use current directory as userdata path
        userdata_path = Path.cwd()
        
        print(f"📁 Using workspace: {userdata_path}")
        print("🔄 Starting traditional interface...")
        print()
        
        app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        app.run()
        
    except ImportError as e:
        print(f"❌ Error: Could not import traditional application: {e}")
        print("💡 Make sure you have all dependencies installed:")
        print("   pip install -r requirements-unified.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()