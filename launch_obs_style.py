#!/usr/bin/env python3
"""
Launch script for OBS-Style DeepFaceLive

This script provides an easy way to launch the OBS Studio-style interface
with streaming and recording capabilities.
"""

import argparse
import sys
import os
import subprocess
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
        "apps/DeepFaceLive/OBSStyleApp.py",
        "requirements_minimal.txt",
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
    parser = argparse.ArgumentParser(
        description="Launch OBS-Style DeepFaceLive with streaming capabilities"
    )
    
    parser.add_argument(
        '--userdata-dir', 
        type=str,
        default='./workspace',
        help="Directory to store user data (default: ./workspace)"
    )
    
    parser.add_argument(
        '--no-cuda', 
        action='store_true',
        help="Disable CUDA acceleration"
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help="Enable debug mode with verbose logging"
    )
    
    parser.add_argument(
        '--skip-resource-check',
        action='store_true',
        help="Skip the resource check on startup"
    )
    
    args = parser.parse_args()
    
    # Check launch resources first (unless skipped)
    if not args.skip_resource_check:
        check_launch_resources()
    
    # Setup paths
    userdata_path = Path(args.userdata_dir)
    userdata_path.mkdir(parents=True, exist_ok=True)
    
    # Add current directory to Python path
    sys.path.insert(0, str(Path(__file__).parent))
    
    # Set environment variables
    if args.no_cuda:
        os.environ['NO_CUDA'] = '1'
        
    if args.debug:
        os.environ['DEBUG'] = '1'
        print("Debug mode enabled")
    
    # Import and run the application
    try:
        from apps.DeepFaceLive.OBSStyleApp import OBSStyleDeepFaceLiveApp
        
        print("Starting OBS-Style DeepFaceLive...")
        print(f"User data directory: {userdata_path.absolute()}")
        
        app = OBSStyleDeepFaceLiveApp(userdata_path=userdata_path)
        app.run()
        
    except ImportError as e:
        print(f"Error importing application: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements_minimal.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()