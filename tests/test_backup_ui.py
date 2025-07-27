#!/usr/bin/env python3
"""
Test Backup UI Script
Tests the backup QOBSStyleUI to see if it works without widget hierarchy issues
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

def test_backup_ui():
    """Test the backup UI"""
    app = QApplication(sys.argv)
    
    # Create a simple main window
    window = QMainWindow()
    window.setWindowTitle("Backup UI Test")
    window.setGeometry(100, 100, 1200, 800)
    
    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # Create layout
    layout = QVBoxLayout()
    central_widget.setLayout(layout)
    
    try:
        # Try to import and use the backup UI
        sys.path.insert(0, str(Path.cwd() / "apps" / "PlayaTewsIdentityMasker" / "ui"))
        from QOBSStyleUI_backup import QOBSStyleUI
        
        # Create a mock stream output backend
        class MockStreamOutput:
            def __init__(self):
                self.name = "MockStreamOutput"
        
        # Create the OBS UI
        obs_ui = QOBSStyleUI(
            stream_output_backend=MockStreamOutput(),
            userdata_path=Path.cwd(),
            face_swap_components={},
            viewers_components={}
        )
        
        layout.addWidget(obs_ui)
        print("✅ Backup UI loaded successfully!")
        
    except Exception as e:
        print(f"❌ Failed to load backup UI: {e}")
        import traceback
        traceback.print_exc()
        
        # Add a fallback widget
        from PyQt5.QtWidgets import QLabel
        fallback = QLabel("Backup UI failed to load\nError: " + str(e))
        fallback.setAlignment(Qt.AlignCenter)
        layout.addWidget(fallback)
    
    # Show the window
    window.show()
    
    print("✅ Backup UI test window should be visible")
    
    # Run the app
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_backup_ui() 