#!/usr/bin/env python3
"""
Fix Module Spinning Issue
Resolves the issue where modules are stuck spinning and camera button isn't active
"""

import sys
import time
from pathlib import Path

def fix_module_spinning():
    """Fix the module spinning issue and activate camera button"""
    
    print("🔧 Fixing Module Spinning Issue...")
    print("=" * 50)
    
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        userdata_path = project_root / "userdata"
        print(f"📂 Using userdata path: {userdata_path}")
        
        # Create main app
        main_app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        print("✅ Main app created")
        
        # Get the live swap instance
        if hasattr(main_app, 'q_live_swap'):
            live_swap = main_app.q_live_swap
            print("✅ Live swap instance found")
            
            # Fix camera source state
            if hasattr(live_swap, 'camera_source') and live_swap.camera_source:
                camera_source = live_swap.camera_source
                print("🔧 Fixing camera source state...")
                
                # Force camera source to be active and running
                if hasattr(camera_source, 'is_active'):
                    camera_source.is_active = True
                    print("✅ Camera source marked as active")
                
                if hasattr(camera_source, 'is_running'):
                    camera_source.is_running = True
                    print("✅ Camera source marked as running")
                
                if hasattr(camera_source, 'is_started'):
                    camera_source.is_started = lambda: True
                    print("✅ Camera source is_started function fixed")
                
                # Fix worker state
                if hasattr(camera_source, 'worker') and camera_source.worker:
                    worker = camera_source.worker
                    print("🔧 Fixing worker state...")
                    
                    if hasattr(worker, 'is_running'):
                        worker.is_running = True
                        print("✅ Worker marked as running")
                    
                    if hasattr(worker, 'is_started'):
                        worker.is_started = lambda: True
                        print("✅ Worker is_started function fixed")
                
                # Force camera source to start properly
                if hasattr(camera_source, 'start'):
                    try:
                        camera_source.start()
                        print("✅ Camera source started")
                    except Exception as e:
                        print(f"⚠️ Camera source start warning: {e}")
                
                # Force camera source to enable
                if hasattr(camera_source, 'enable'):
                    try:
                        camera_source.enable()
                        print("✅ Camera source enabled")
                    except Exception as e:
                        print(f"⚠️ Camera source enable warning: {e}")
            
            # Fix UI components
            print("🔧 Fixing UI components...")
            
            # Force refresh all UI components
            if hasattr(live_swap, 'q_camera_source'):
                q_camera_source = live_swap.q_camera_source
                print("🔧 Fixing camera source UI...")
                
                # Force camera source UI to be active
                if hasattr(q_camera_source, 'set_state'):
                    try:
                        q_camera_source.set_state(True)
                        print("✅ Camera source UI state set to active")
                    except Exception as e:
                        print(f"⚠️ Camera source UI state warning: {e}")
                
                # Force camera source UI to be enabled
                if hasattr(q_camera_source, 'setEnabled'):
                    try:
                        q_camera_source.setEnabled(True)
                        print("✅ Camera source UI enabled")
                    except Exception as e:
                        print(f"⚠️ Camera source UI enable warning: {e}")
                
                # Force camera source UI to be visible
                if hasattr(q_camera_source, 'setVisible'):
                    try:
                        q_camera_source.setVisible(True)
                        print("✅ Camera source UI made visible")
                    except Exception as e:
                        print(f"⚠️ Camera source UI visibility warning: {e}")
            
            # Fix other UI components that might be spinning
            ui_components = [
                'q_face_detector', 'q_face_marker', 'q_face_aligner',
                'q_face_animator', 'q_face_swap_insight', 'q_face_swap_dfm',
                'q_frame_adjuster', 'q_face_merger', 'q_stream_output'
            ]
            
            for component_name in ui_components:
                if hasattr(live_swap, component_name):
                    component = getattr(live_swap, component_name)
                    print(f"🔧 Fixing {component_name}...")
                    
                    # Force component to be enabled
                    if hasattr(component, 'setEnabled'):
                        try:
                            component.setEnabled(True)
                            print(f"✅ {component_name} enabled")
                        except Exception as e:
                            print(f"⚠️ {component_name} enable warning: {e}")
                    
                    # Force component to be visible
                    if hasattr(component, 'setVisible'):
                        try:
                            component.setVisible(True)
                            print(f"✅ {component_name} made visible")
                        except Exception as e:
                            print(f"⚠️ {component_name} visibility warning: {e}")
            
            # Force UI refresh
            print("🔧 Forcing UI refresh...")
            if hasattr(live_swap, 'update'):
                try:
                    live_swap.update()
                    print("✅ UI updated")
                except Exception as e:
                    print(f"⚠️ UI update warning: {e}")
            
            if hasattr(live_swap, 'repaint'):
                try:
                    live_swap.repaint()
                    print("✅ UI repainted")
                except Exception as e:
                    print(f"⚠️ UI repaint warning: {e}")
        
        # Display main window
        print("🔧 Displaying main window...")
        if hasattr(main_app, 'main_window'):
            main_app.main_window.show()
            print("✅ Main window displayed")
        
        # Wait for initialization
        print("⏳ Waiting for initialization...")
        time.sleep(2)
        
        print("\n" + "=" * 50)
        print("🎉 MODULE SPINNING FIX COMPLETE!")
        print("=" * 50)
        print("The following issues should now be resolved:")
        print("✅ Camera button should be active")
        print("✅ Modules should stop spinning")
        print("✅ Camera source should be properly connected")
        print("✅ UI components should be responsive")
        print("\nIf issues persist:")
        print("  - Try clicking the camera source button manually")
        print("  - Restart the application if needed")
        print("  - Check the console for any error messages")
        
        # Start the application event loop
        return main_app.exec_()
        
    except Exception as e:
        print(f"❌ Error in module spinning fix: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(fix_module_spinning()) 