#!/usr/bin/env python3
"""
PlayaTewsIdentityMasker OBS-Style UI Launcher
This is the DEFAULT and RECOMMENDED interface for streaming and modern usage.
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the OBS-style UI (default interface)"""
    print("🚀 PlayaTewsIdentityMasker OBS-Style UI Launcher")
    print("📋 This is the DEFAULT and RECOMMENDED interface")
    print("🎯 Optimized for streaming and modern usage")
    print()
    
    # Import and run the OBS-style application
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerOBSStyleApp import PlayaTewsIdentityMaskerOBSStyleApp
        
        # Use current directory as userdata path
        userdata_path = Path.cwd()
        
        print(f"📁 Using workspace: {userdata_path}")
        print("🔄 Starting OBS-style interface...")
        print()
        
        app = PlayaTewsIdentityMaskerOBSStyleApp(userdata_path=userdata_path)
        app.run()
        
    except ImportError as e:
        print(f"❌ Error: Could not import OBS-style application: {e}")
        print("💡 Make sure you have all dependencies installed:")
        print("   pip install -r requirements-unified.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()