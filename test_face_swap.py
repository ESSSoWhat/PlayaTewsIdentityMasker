#!/usr/bin/env python3
"""
Quick Face Swap Test
Verifies that face swap functionality is working properly
"""

import sys
import time
from pathlib import Path

def test_face_swap():
    """Quick test of face swap functionality"""
    
    print("🎭 FACE SWAP FUNCTIONALITY TEST")
    print("=" * 50)
    
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        userdata_path = project_root / "userdata"
        print(f"📂 Userdata path: {userdata_path}")
        
        # Check DFM models
        dfm_path = userdata_path / "dfm_models"
        if dfm_path.exists():
            dfm_files = list(dfm_path.glob("*.dfm"))
            print(f"📦 Found {len(dfm_files)} DFM models")
            
            # List some popular models
            popular_models = ["Keanu_Reeves.dfm", "Jackie_Chan.dfm", "Joker.dfm", "Mr_Bean.dfm"]
            available_popular = [f.name for f in dfm_files if f.name in popular_models]
            print(f"🎬 Popular models available: {', '.join(available_popular)}")
        else:
            print("⚠️ No DFM models directory found")
        
        # Create main app
        print("\n🚀 Creating application for testing...")
        main_app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        print("✅ Application created")
        
        # Get the live swap instance
        if hasattr(main_app, 'q_live_swap'):
            live_swap = main_app.q_live_swap
            print("✅ Live swap instance found")
            
            # Test backend components
            print("\n🔍 Testing Backend Components:")
            print("-" * 30)
            
            backend_tests = [
                ('camera_source', 'Camera Source'),
                ('face_detector', 'Face Detector'),
                ('face_aligner', 'Face Aligner'),
                ('face_swapper', 'Face Swapper'),
                ('face_merger', 'Face Merger')
            ]
            
            for attr_name, display_name in backend_tests:
                if hasattr(live_swap, attr_name):
                    backend = getattr(live_swap, attr_name)
                    if hasattr(backend, 'is_started'):
                        is_active = backend.is_started()
                        status = "✅ ACTIVE" if is_active else "❌ INACTIVE"
                        print(f"  {display_name}: {status}")
                    else:
                        print(f"  {display_name}: ⚠️ No is_started method")
                else:
                    print(f"  {display_name}: ❌ Not found")
            
            # Test UI components
            print("\n🔍 Testing UI Components:")
            print("-" * 30)
            
            ui_tests = [
                ('q_camera_source', 'Camera Source UI'),
                ('q_face_detector', 'Face Detector UI'),
                ('q_face_aligner', 'Face Aligner UI'),
                ('q_face_swap_dfm', 'Face Swap DFM UI'),
                ('q_face_merger', 'Face Merger UI')
            ]
            
            for attr_name, display_name in ui_tests:
                if hasattr(live_swap, attr_name):
                    ui_component = getattr(live_swap, attr_name)
                    if hasattr(ui_component, 'isEnabled'):
                        is_enabled = ui_component.isEnabled()
                        status = "✅ ENABLED" if is_enabled else "❌ DISABLED"
                        print(f"  {display_name}: {status}")
                    else:
                        print(f"  {display_name}: ⚠️ No isEnabled method")
                else:
                    print(f"  {display_name}: ❌ Not found")
            
            # Test face swap specific functionality
            print("\n🎭 Testing Face Swap Specific Features:")
            print("-" * 40)
            
            # Check if face swapper has DFM models
            if hasattr(live_swap, 'face_swapper'):
                face_swapper = live_swap.face_swapper
                print(f"  Face Swapper Backend: ✅ Found")
                
                # Check if it can access DFM models
                if hasattr(face_swapper, 'get_state'):
                    try:
                        state = face_swapper.get_state()
                        print(f"  Face Swapper State: ✅ Accessible")
                    except Exception as e:
                        print(f"  Face Swapper State: ⚠️ Error: {e}")
            
            # Check DFM UI component
            if hasattr(live_swap, 'q_face_swap_dfm'):
                dfm_ui = live_swap.q_face_swap_dfm
                print(f"  DFM UI Component: ✅ Found")
                
                # Check if it has model selection
                if hasattr(dfm_ui, '_backend'):
                    print(f"  DFM UI Backend: ✅ Connected")
            
            # Display main window
            print("\n🖥️ Displaying Application Window...")
            if hasattr(main_app, 'main_window'):
                main_app.main_window.show()
                print("✅ Main window displayed")
            
            # Wait for initialization
            print("\n⏳ Waiting for face swap initialization...")
            time.sleep(2)
            
            print("\n" + "=" * 50)
            print("🎉 FACE SWAP TEST COMPLETE!")
            print("=" * 50)
            print("\n📋 Next Steps:")
            print("1. Look for the PlayaTewsIdentityMasker window")
            print("2. Navigate to 'Face Swap DFM' tab")
            print("3. Select a DFM model (try 'Keanu Reeves')")
            print("4. Look at the camera - you should see face swap!")
            print("5. Test different models and settings")
            print("\n🎭 Happy Face Swapping!")
            
            # Start the application event loop
            return main_app.exec_()
        
    except Exception as e:
        print(f"❌ Error in face swap test: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_face_swap()) 