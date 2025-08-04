#!/usr/bin/env python3
"""
Test script for the new layout UI
Demonstrates the three-panel design as specified in the ASCII art
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# Add the apps directory to the path
sys.path.insert(0, str(Path(__file__).parent / "apps" / "PlayaTewsIdentityMasker"))

try:
    # Import the new layout UI
    from apps.PlayaTewsIdentityMasker.ui.QNewLayoutUI import QNewLayoutUI
    
    # Create a mock StreamOutput class since we can't import the real one
    class MockStreamOutput:
        def __init__(self):
            self.is_streaming = False
            self.is_recording = False

        def start_stream(self):
            self.is_streaming = True

        def stop_stream(self):
            self.is_streaming = False

        def start_recording(self):
            self.is_recording = True

        def stop_recording(self):
            self.is_recording = False

    def main() -> None:
        """Main function to test the new layout UI"""
        app = QApplication(sys.argv)
        
        # Create the new layout UI
        userdata_path = Path("userdata")
        userdata_path.mkdir(exist_ok=True)
        
        ui = QNewLayoutUI(
            stream_output_backend=MockStreamOutput(),
            userdata_path=userdata_path,
            face_swap_components={},
            viewers_components={},
            voice_changer_backend=None
        )
        
        # Show the UI
        ui.show()
        
        print("✅ New Layout UI loaded successfully!")
        print("📋 Layout Features:")
        print("   • LEFT PANEL: DFM Quick Access, Input Sources, Voice Changer")
        print("   • CENTER PANEL: Processing Components, Enhanced Output Preview")
        print("   • RIGHT PANEL: Settings, Additional Controls")
        print("   • Large preview area with fullscreen support")
        print("   • Modern dark theme with responsive design")
        
        # Start the application
        sys.exit(app.exec_())
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error running the application: {e}")
    sys.exit(1) 