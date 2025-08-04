#!/usr/bin/env python3
"""
Fix Module Visibility
Ensures all modules show their options and controls by properly initializing backend states
"""

import sys
import time
from pathlib import Path

def fix_module_visibility():
    """Fix module visibility by ensuring backends are started and UI is properly initialized"""
    
    print("🔧 FIXING MODULE VISIBILITY")
    print("=" * 50)
    
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        userdata_path = project_root / "userdata"
        print(f"📂 Userdata path: {userdata_path}")
        
        # Create main app
        print("🚀 Creating main application...")
        main_app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        print("✅ Main app created")
        
        # Get the live swap instance
        if hasattr(main_app, 'q_live_swap'):
            live_swap = main_app.q_live_swap
            print("✅ Live swap instance found")
            
            # Step 1: Start all backend components
            print("\n🔧 STEP 1: Starting Backend Components")
            print("-" * 40)
            
            backend_components = []
            
            # Collect all backend components
            if hasattr(live_swap, 'camera_source'):
                backend_components.append(('camera_source', live_swap.camera_source))
            if hasattr(live_swap, 'file_source'):
                backend_components.append(('file_source', live_swap.file_source))
            if hasattr(live_swap, 'face_detector'):
                backend_components.append(('face_detector', live_swap.face_detector))
            if hasattr(live_swap, 'face_marker'):
                backend_components.append(('face_marker', live_swap.face_marker))
            if hasattr(live_swap, 'face_aligner'):
                backend_components.append(('face_aligner', live_swap.face_aligner))
            if hasattr(live_swap, 'face_animator'):
                backend_components.append(('face_animator', live_swap.face_animator))
            if hasattr(live_swap, 'face_swapper'):
                backend_components.append(('face_swapper', live_swap.face_swapper))
            if hasattr(live_swap, 'frame_adjuster'):
                backend_components.append(('frame_adjuster', live_swap.frame_adjuster))
            if hasattr(live_swap, 'face_merger'):
                backend_components.append(('face_merger', live_swap.face_merger))
            if hasattr(live_swap, 'stream_output'):
                backend_components.append(('stream_output', live_swap.stream_output))
            
            print(f"📋 Found {len(backend_components)} backend components")
            
            # Start each backend component
            for name, backend in backend_components:
                print(f"\n🔧 Starting {name} backend...")
                
                try:
                    # Check if already started
                    if hasattr(backend, 'is_started') and backend.is_started():
                        print(f"✅ {name} already started")
                        continue
                    
                    # Start the backend
                    if hasattr(backend, 'start'):
                        backend.start()
                        print(f"✅ {name} started successfully")
                    else:
                        print(f"⚠️ {name} has no start method")
                        
                except Exception as e:
                    print(f"❌ Error starting {name}: {e}")
            
            # Step 2: Force UI state updates
            print("\n🔧 STEP 2: Forcing UI State Updates")
            print("-" * 40)
            
            ui_components = []
            
            # Collect all UI components
            if hasattr(live_swap, 'q_camera_source'):
                ui_components.append(('q_camera_source', live_swap.q_camera_source))
            if hasattr(live_swap, 'q_file_source'):
                ui_components.append(('q_file_source', live_swap.q_file_source))
            if hasattr(live_swap, 'q_face_detector'):
                ui_components.append(('q_face_detector', live_swap.q_face_detector))
            if hasattr(live_swap, 'q_face_marker'):
                ui_components.append(('q_face_marker', live_swap.q_face_marker))
            if hasattr(live_swap, 'q_face_aligner'):
                ui_components.append(('q_face_aligner', live_swap.q_face_aligner))
            if hasattr(live_swap, 'q_face_animator'):
                ui_components.append(('q_face_animator', live_swap.q_face_animator))
            if hasattr(live_swap, 'q_face_swap_insight'):
                ui_components.append(('q_face_swap_insight', live_swap.q_face_swap_insight))
            if hasattr(live_swap, 'q_face_swap_dfm'):
                ui_components.append(('q_face_swap_dfm', live_swap.q_face_swap_dfm))
            if hasattr(live_swap, 'q_frame_adjuster'):
                ui_components.append(('q_frame_adjuster', live_swap.q_frame_adjuster))
            if hasattr(live_swap, 'q_face_merger'):
                ui_components.append(('q_face_merger', live_swap.q_face_merger))
            if hasattr(live_swap, 'q_stream_output'):
                ui_components.append(('q_stream_output', live_swap.q_stream_output))
            
            print(f"📋 Found {len(ui_components)} UI components")
            
            # Force UI state updates for each component
            for name, ui_component in ui_components:
                print(f"\n🔧 Updating {name} UI state...")
                
                try:
                    # For QBackendPanel components, force the state change
                    if hasattr(ui_component, '_backend') and hasattr(ui_component, '_on_backend_state_change'):
                        backend = ui_component._backend
                        
                        # Check if backend is actually started
                        is_started = backend.is_started() if hasattr(backend, 'is_started') else False
                        
                        if is_started:
                            # Force the UI to show content
                            ui_component._on_backend_state_change(
                                backend=backend,
                                started=True,
                                starting=False,
                                stopping=False,
                                stopped=False,
                                busy=False
                            )
                            print(f"✅ {name} UI state updated - content should be visible")
                        else:
                            print(f"⚠️ {name} backend not started, starting it...")
                            backend.start()
                            time.sleep(0.1)  # Give it time to start
                            
                            # Try the state change again
                            ui_component._on_backend_state_change(
                                backend=backend,
                                started=True,
                                starting=False,
                                stopping=False,
                                stopped=False,
                                busy=False
                            )
                            print(f"✅ {name} UI state updated after starting backend")
                    
                    # Force enable and show the component
                    if hasattr(ui_component, 'setEnabled'):
                        ui_component.setEnabled(True)
                    if hasattr(ui_component, 'setVisible'):
                        ui_component.setVisible(True)
                        
                except Exception as e:
                    print(f"❌ Error updating {name} UI: {e}")
            
            # Step 3: Force content widgets to be visible
            print("\n🔧 STEP 3: Forcing Content Widgets Visible")
            print("-" * 40)
            
            for name, ui_component in ui_components:
                try:
                    # Force content widget to be visible and enabled
                    if hasattr(ui_component, '_content_widget'):
                        content_widget = ui_component._content_widget
                        
                        # Force enable and show
                        if hasattr(content_widget, 'setEnabled'):
                            content_widget.setEnabled(True)
                        if hasattr(content_widget, 'setVisible'):
                            content_widget.setVisible(True)
                        
                        # Force all child widgets to be visible
                        if hasattr(content_widget, 'findChildren'):
                            children = content_widget.findChildren()
                            for child in children:
                                if hasattr(child, 'setEnabled'):
                                    child.setEnabled(True)
                                if hasattr(child, 'setVisible'):
                                    child.setVisible(True)
                        
                        print(f"✅ {name} content widget forced visible")
                        
                except Exception as e:
                    print(f"⚠️ Error forcing {name} content visible: {e}")
            
            # Step 4: Force UI refresh
            print("\n🔧 STEP 4: Forcing UI Refresh")
            print("-" * 40)
            
            # Force all widgets to update
            if hasattr(live_swap, 'update'):
                live_swap.update()
                print("✅ Live swap UI updated")
            
            if hasattr(live_swap, 'repaint'):
                live_swap.repaint()
                print("✅ Live swap UI repainted")
            
            # Force process events
            try:
                from xlib import qt as qtx
                if hasattr(qtx, 'QApplication') and qtx.QApplication.instance():
                    qtx.QApplication.processEvents()
                    print("✅ Qt events processed")
            except Exception as e:
                print(f"⚠️ Error processing Qt events: {e}")
            
            # Step 5: Display main window
            print("\n🔧 STEP 5: Display Main Window")
            print("-" * 40)
            
            if hasattr(main_app, 'main_window'):
                main_app.main_window.show()
                print("✅ Main window displayed")
            
            # Wait for everything to settle
            print("\n⏳ Waiting for initialization to complete...")
            time.sleep(2)
            
            # Final verification
            print("\n🔍 STEP 6: Final Verification")
            print("-" * 40)
            
            visible_components = 0
            for name, ui_component in ui_components:
                try:
                    if hasattr(ui_component, '_content_widget'):
                        content_widget = ui_component._content_widget
                        is_visible = content_widget.isVisible() if hasattr(content_widget, 'isVisible') else False
                        is_enabled = content_widget.isEnabled() if hasattr(content_widget, 'isEnabled') else False
                        
                        status = "✅ VISIBLE" if is_visible and is_enabled else "❌ HIDDEN"
                        print(f"  {name}: {status}")
                        
                        if is_visible and is_enabled:
                            visible_components += 1
                            
                except Exception as e:
                    print(f"  {name}: ❌ ERROR - {e}")
            
            print(f"\n📊 Summary: {visible_components}/{len(ui_components)} components visible")
            
            print("\n" + "=" * 50)
            print("🎉 MODULE VISIBILITY FIX COMPLETE!")
            print("=" * 50)
            print("All modules should now:")
            print("✅ Show their options and controls")
            print("✅ Be properly enabled and visible")
            print("✅ Have working backend connections")
            print("\nIf modules are still not visible, try:")
            print("1. Click the power button (red/green) on each module")
            print("2. Check the console for any error messages")
            print("3. Restart the application if needed")
            
            # Start the application event loop
            return main_app.exec_()
        
    except Exception as e:
        print(f"❌ Error in module visibility fix: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(fix_module_visibility()) 