#!/usr/bin/env python3
"""
Clear UI State Script
This script clears any saved state that might be causing the UI to revert to traditional interface.
"""

import os
import shutil
from pathlib import Path

def clear_ui_state():
    """Clear any saved UI state files"""
    print("🧹 Clearing UI State Files")
    print("📋 This will reset any saved preferences that might cause UI reversion")
    print()
    
    # Common locations where state files might be stored
    state_locations = [
        Path.cwd() / 'states.dat',
        Path.cwd() / 'settings' / 'states.dat',
        Path.cwd() / 'userdata' / 'states.dat',
        Path.home() / '.playatewsidentitymasker' / 'states.dat',
        Path.home() / '.config' / 'playatewsidentitymasker' / 'states.dat',
    ]
    
    cleared_files = []
    
    for location in state_locations:
        if location.exists():
            try:
                # Create backup
                backup_path = location.with_suffix('.dat.backup')
                shutil.copy2(location, backup_path)
                print(f"💾 Backed up: {location} -> {backup_path}")
                
                # Remove the file
                location.unlink()
                cleared_files.append(str(location))
                print(f"🗑️  Cleared: {location}")
                
            except Exception as e:
                print(f"⚠️  Could not clear {location}: {e}")
    
    # Also check for any Qt settings
    qt_settings_dirs = [
        Path.home() / '.config' / 'Qt',
        Path.home() / '.config' / 'QtProject',
    ]
    
    for qt_dir in qt_settings_dirs:
        if qt_dir.exists():
            print(f"📁 Found Qt settings directory: {qt_dir}")
            print("   (Qt settings are usually safe to keep)")
    
    if cleared_files:
        print()
        print("✅ Successfully cleared the following state files:")
        for file in cleared_files:
            print(f"   - {file}")
        print()
        print("🔄 Next time you launch the app, it will use the default OBS-style interface")
        print("💡 If you need to restore the old settings, look for .backup files")
    else:
        print()
        print("ℹ️  No state files found to clear")
        print("   The UI reversion might be caused by command line arguments or launcher choice")
    
    print()
    print("🎯 To ensure OBS-style UI, use:")
    print("   python launch_obs_ui.py")

if __name__ == "__main__":
    clear_ui_state()