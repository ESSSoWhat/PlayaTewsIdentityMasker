#!/usr/bin/env python3
"""
Test script to verify processing window functionality
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_processing_window():
    """Test that the processing window opens and components work"""
    print("Testing PlayaTewsIdentityMasker Processing Window...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Import the processing window
        from apps.PlayaTewsIdentityMasker.ui.QProcessingWindow import QProcessingWindow
        
        print("✅ QProcessingWindow imported successfully")
        
        # Create mock face-swapping components for testing
        mock_components = {
            'file_source': create_mock_component("File Source"),
            'camera_source': create_mock_component("Camera Source"),
            'face_detector': create_mock_component("Face Detector"),
            'face_aligner': create_mock_component("Face Aligner"),
            'face_marker': create_mock_component("Face Marker"),
            'face_animator': create_mock_component("Face Animator"),
            'face_swap_insight': create_mock_component("Face Swap Insight"),
            'face_swap_dfm': create_mock_component("Face Swap DFM"),
            'frame_adjuster': create_mock_component("Frame Adjuster"),
            'face_merger': create_mock_component("Face Merger"),
            'stream_output': create_mock_component("Stream Output")
        }
        
        print("✅ Mock components created")
        
        # Create processing window
        processing_window = QProcessingWindow(mock_components, None)
        print("✅ Processing window created")
        
        # Show the window
        processing_window.show()
        print("✅ Processing window displayed")
        
        # Check window properties
        print(f"  - Window title: {processing_window.windowTitle()}")
        print(f"  - Window size: {processing_window.size().width()}x{processing_window.size().height()}")
        print(f"  - Is visible: {processing_window.isVisible()}")
        print(f"  - Tab count: {processing_window.processing_tabs.count()}")
        
        # List available tabs
        for i in range(processing_window.processing_tabs.count()):
            tab_name = processing_window.processing_tabs.tabText(i)
            print(f"  - Tab {i}: {tab_name}")
        
        print("\n✅ Processing window test completed successfully!")
        print("The window should be visible on your screen.")
        print("You can interact with it to test the interface.")
        
        # Keep the window open for testing
        return app.exec_()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

def create_mock_component(name):
    """Create a mock component widget for testing"""
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
    from PyQt5.QtCore import Qt
    
    widget = QWidget()
    layout = QVBoxLayout()
    
    # Add a label with the component name
    label = QLabel(name)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("""
        QLabel {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 5px;
            color: #ffffff;
            font-weight: bold;
            padding: 10px;
        }
    """)
    
    # Add a mock power button
    power_btn = QPushButton("Power")
    power_btn.setStyleSheet("""
        QPushButton {
            background-color: #e74c3c;
            color: white;
            border: none;
            border-radius: 3px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #c0392b;
        }
    """)
    
    layout.addWidget(label)
    layout.addWidget(power_btn)
    layout.addStretch()
    
    widget.setLayout(layout)
    widget.setMinimumHeight(100)
    
    return widget

if __name__ == "__main__":
    sys.exit(test_processing_window()) 