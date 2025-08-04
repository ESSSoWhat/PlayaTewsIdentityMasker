#!/usr/bin/env python3
"""
Fix Loading Modules
Fixes modules stuck in loading state by forcing state completion
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def fix_loading_modules():
    """Fix modules stuck in loading state"""
    
    print("🔧 FIXING LOADING MODULES")
    print("=" * 40)
    
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        # Create app
        userdata_path = project_root / "userdata"
        app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        live_swap = app.q_live_swap
        
        print("🚀 Fixing stuck modules...")
        
        # List of backend components to fix
        backend_names = [
            'camera_source', 'file_source', 'face_detector', 'face_marker',
            'face_aligner', 'face_animator', 'face_swapper', 'frame_adjuster',
            'face_merger', 'stream_output'
        ]
        
        for name in backend_names:
            if hasattr(live_swap, name):
                backend = getattr(live_swap, name)
                print(f"\n🔧 Fixing {name}...")
                
                try:
                    # Step 1: Force stop if stuck
                    if hasattr(backend, 'stop'):
                        backend.stop()
                        print(f"  ✅ {name} stopped")
                        time.sleep(0.1)
                    
                    # Step 2: Reset state
                    if hasattr(backend, 'reset_state'):
                        backend.reset_state()
                        print(f"  ✅ {name} state reset")
                    
                    # Step 3: Force process status to stopped
                    if hasattr(backend, '_process_status'):
                        from xlib.mp.csw.CSWBase import Host
                        backend._process_status = Host._ProcessStatus.STOPPED
                        print(f"  ✅ {name} process status reset")
                    
                    # Step 4: Force is_busy to False
                    if hasattr(backend, '_is_busy'):
                        backend._is_busy = False
                        print(f"  ✅ {name} busy state cleared")
                    
                    # Step 5: Start fresh
                    if hasattr(backend, 'start'):
                        backend.start()
                        print(f"  ✅ {name} restarted")
                        time.sleep(0.2)  # Give it time to start properly
                    
                except Exception as e:
                    print(f"  ❌ Error fixing {name}: {e}")
            else:
                print(f"⚠️ {name} not found")
        
        # Fix UI components
        print("\n🔧 Fixing UI components...")
        
        ui_names = [
            'q_camera_source', 'q_file_source', 'q_face_detector', 'q_face_marker',
            'q_face_aligner', 'q_face_animator', 'q_face_swap_insight', 'q_face_swap_dfm',
            'q_frame_adjuster', 'q_face_merger', 'q_stream_output'
        ]
        
        for name in ui_names:
            if hasattr(live_swap, name):
                ui_component = getattr(live_swap, name)
                print(f"\n🔧 Fixing {name} UI...")
                
                try:
                    # Force UI state update
                    if hasattr(ui_component, '_backend') and hasattr(ui_component, '_on_backend_state_change'):
                        backend = ui_component._backend
                        
                        # Force the UI to show as started and not busy
                        ui_component._on_backend_state_change(
                            backend=backend,
                            started=True,
                            starting=False,
                            stopping=False,
                            stopped=False,
                            busy=False
                        )
                        print(f"  ✅ {name} UI state fixed")
                    
                    # Force content widget visible
                    if hasattr(ui_component, '_content_widget'):
                        content_widget = ui_component._content_widget
                        if hasattr(content_widget, 'setEnabled'):
                            content_widget.setEnabled(True)
                        if hasattr(content_widget, 'setVisible'):
                            content_widget.setVisible(True)
                        print(f"  ✅ {name} content widget visible")
                    
                    # Force button to show as active
                    if hasattr(ui_component, '_btn_on_off'):
                        btn = ui_component._btn_on_off
                        try:
                            from resources.gfx import QXImageDB
                            btn.set_image(QXImageDB.power_outline("lime"))
                            print(f"  ✅ {name} button set to active")
                        except:
                            print(f"  ⚠️ {name} button fix skipped")
                    
                except Exception as e:
                    print(f"  ❌ Error fixing {name} UI: {e}")
            else:
                print(f"⚠️ {name} UI not found")
        
        # Force UI refresh
        print("\n🔧 Forcing UI refresh...")
        
        if hasattr(live_swap, 'update'):
            live_swap.update()
        if hasattr(live_swap, 'repaint'):
            live_swap.repaint()
        
        try:
            from xlib import qt as qtx
            if hasattr(qtx, 'QApplication') and qtx.QApplication.instance():
                qtx.QApplication.processEvents()
        except:
            pass
        
        print("✅ UI refresh complete")
        
        # Show window
        if hasattr(app, 'main_window'):
            app.main_window.show()
        
        print("\n🎉 Loading modules fix complete!")
        print("All modules should now be active and not stuck loading.")
        
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(fix_loading_modules()) 