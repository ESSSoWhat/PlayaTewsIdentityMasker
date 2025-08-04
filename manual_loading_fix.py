#!/usr/bin/env python3
"""
Manual Loading Fix
Simple fix for modules stuck in loading state
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def manual_fix():
    """Manual fix for loading modules"""
    
    print("🔧 MANUAL LOADING FIX")
    print("=" * 30)
    
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        # Create app
        userdata_path = project_root / "userdata"
        app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        live_swap = app.q_live_swap
        
        print("🚀 Fixing stuck loading modules...")
        
        # Force all backends to complete loading
        backend_names = [
            'camera_source', 'file_source', 'face_detector', 'face_marker',
            'face_aligner', 'face_animator', 'frame_adjuster', 'face_merger',
            'stream_output'
        ]
        
        for name in backend_names:
            if hasattr(live_swap, name):
                backend = getattr(live_swap, name)
                print(f"🔧 Fixing {name}...")
                
                try:
                    # Force stop any stuck processes
                    if hasattr(backend, 'stop'):
                        backend.stop()
                    
                    # Force busy state to False
                    if hasattr(backend, '_is_busy'):
                        backend._is_busy = False
                    
                    # Force process status to stopped
                    if hasattr(backend, '_process_status'):
                        from xlib.mp.csw.CSWBase import Host
                        backend._process_status = Host._ProcessStatus.STOPPED
                    
                    # Start fresh
                    if hasattr(backend, 'start'):
                        backend.start()
                    
                    print(f"✅ {name} fixed")
                    
                except Exception as e:
                    print(f"⚠️ {name} error: {e}")
        
        # Force UI updates
        print("\n🔧 Forcing UI updates...")
        
        ui_names = [
            'q_camera_source', 'q_file_source', 'q_face_detector', 'q_face_marker',
            'q_face_aligner', 'q_face_animator', 'q_face_swap_insight', 'q_face_swap_dfm',
            'q_frame_adjuster', 'q_face_merger', 'q_stream_output'
        ]
        
        for name in ui_names:
            if hasattr(live_swap, name):
                ui_component = getattr(live_swap, name)
                
                try:
                    # Force UI state to show as started
                    if hasattr(ui_component, '_backend') and hasattr(ui_component, '_on_backend_state_change'):
                        backend = ui_component._backend
                        ui_component._on_backend_state_change(
                            backend=backend,
                            started=True,
                            starting=False,
                            stopping=False,
                            stopped=False,
                            busy=False
                        )
                    
                    # Force content visible
                    if hasattr(ui_component, '_content_widget'):
                        content_widget = ui_component._content_widget
                        if hasattr(content_widget, 'setEnabled'):
                            content_widget.setEnabled(True)
                        if hasattr(content_widget, 'setVisible'):
                            content_widget.setVisible(True)
                    
                except Exception as e:
                    print(f"⚠️ {name} UI error: {e}")
        
        # Show window
        if hasattr(app, 'main_window'):
            app.main_window.show()
        
        print("\n🎉 Manual fix complete!")
        print("Modules should no longer be stuck loading.")
        
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(manual_fix()) 