#!/usr/bin/env python3
"""
PlayaTewsIdentityMasker - Quick Launch Script

This is the simplest way to launch PlayaTewsIdentityMasker with the OBS-style interface.
Just run: python launch.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch PlayaTewsIdentityMasker with OBS-style interface"""
    
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