#!/usr/bin/env python3
"""
Quick Module Fix
Manually starts all backend components to make UI options visible
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def quick_fix():
    """Quick fix to start all backend components"""
    
    print("🔧 QUICK MODULE FIX")
    print("=" * 30)
    
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        # Create app
        userdata_path = project_root / "userdata"
        app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        
        # Get live swap
        live_swap = app.q_live_swap
        
        # List of backend components to start
        backend_names = [
            'camera_source', 'file_source', 'face_detector', 'face_marker',
            'face_aligner', 'face_animator', 'face_swapper', 'frame_adjuster',
            'face_merger', 'stream_output'
        ]
        
        print("🚀 Starting backend components...")
        
        for name in backend_names:
            if hasattr(live_swap, name):
                backend = getattr(live_swap, name)
                try:
                    if hasattr(backend, 'start'):
                        backend.start()
                        print(f"✅ {name} started")
                    else:
                        print(f"⚠️ {name} has no start method")
                except Exception as e:
                    print(f"❌ Error starting {name}: {e}")
            else:
                print(f"⚠️ {name} not found")
        
        print("\n🎉 Quick fix complete!")
        print("All modules should now show their options.")
        print("If they don't, try clicking the power buttons manually.")
        
        # Show the window
        if hasattr(app, 'main_window'):
            app.main_window.show()
        
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(quick_fix()) 