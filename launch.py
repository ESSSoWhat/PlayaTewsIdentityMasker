#!/usr/bin/env python3
"""
PlayaTewsIdentityMasker - Quick Launch Script

This is the simplest way to launch PlayaTewsIdentityMasker with the OBS-style interface.
Just run: python launch.py
"""

import subprocess
import sys
import os
from pathlib import Path

def check_launch_resources():
    """Check for most up-to-date launch resources"""
    print("🔍 Checking for most up-to-date launch resources...")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    
    # Check if git is available and this is a git repository
    try:
        # Check if git is available
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        
        # Check if we're in a git repository
        result = subprocess.run(["git", "rev-parse", "--git-dir"], 
                              capture_output=True, text=True, cwd=script_dir)
        
        if result.returncode == 0:
            print("📦 Git repository detected. Checking for updates...")
            
            # Fetch latest changes from remote
            try:
                subprocess.run(["git", "fetch", "--quiet"], check=True, cwd=script_dir)
                
                # Check if local is behind remote
                result = subprocess.run(["git", "rev-list", "HEAD...origin/main", "--count"], 
                                      capture_output=True, text=True, cwd=script_dir)
                
                if result.returncode == 0:
                    behind_count = int(result.stdout.strip())
                    if behind_count > 0:
                        print(f"⚠️  Warning: Local repository is {behind_count} commits behind remote")
                        print("Consider running 'git pull' to update to the latest version")
                        print()
                        
                        update_choice = input("Do you want to update now? (y/n): ").lower().strip()
                        if update_choice in ['y', 'yes']:
                            print("🔄 Updating repository...")
                            try:
                                subprocess.run(["git", "pull"], check=True, cwd=script_dir)
                                print("✅ Repository updated successfully")
                            except subprocess.CalledProcessError:
                                print("❌ Error: Failed to update repository")
                                print("Continuing with current version...")
                    else:
                        print("✅ Repository is up to date")
                else:
                    print("ℹ️  Could not determine if repository is up to date")
                    
            except subprocess.CalledProcessError:
                print("⚠️  Warning: Could not fetch latest changes from remote repository")
        else:
            print("ℹ️  Not a git repository - skipping update check")
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ℹ️  Git not available - skipping update check")
    
    # Check for critical resource files
    print("\n📁 Checking critical resource files...")
    
    critical_files = [
        "run_obs_style.py",
        "requirements.txt",
        "config_manager.py"
    ]
    
    missing_files = []
    for file_name in critical_files:
        file_path = script_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"⚠️  Warning: Missing critical files: {', '.join(missing_files)}")
        print("Some functionality may not work properly")
    else:
        print("✅ All critical files found")
    
    print("Resource check completed.")
    print("=" * 60)
    print()

def main():
    """Launch PlayaTewsIdentityMasker with OBS-style interface"""
    
    # Check launch resources first
    check_launch_resources()
    
    print("🚀 Starting PlayaTewsIdentityMasker with OBS-Style Interface...")
    print("=" * 60)
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Build the command to run the OBS-style launcher
    launcher_script = script_dir / "run_obs_style.py"
    
    if not launcher_script.exists():
        print(f"❌ Error: {launcher_script} not found")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)
    
    # Run the OBS-style launcher
    try:
        cmd = [sys.executable, str(launcher_script)]
        
        # Pass through any command line arguments
        if len(sys.argv) > 1:
            cmd.extend(sys.argv[1:])
        
        print(f"📋 Command: {' '.join(cmd)}")
        print("=" * 60)
        
        # Execute the launcher
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running launcher: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()