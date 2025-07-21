#!/usr/bin/env python3
"""
Test script for the All Controls Window with face swap components
Verifies that the popup window opens correctly with the required arguments
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt

# Import the processing window
from apps.PlayaTewsIdentityMasker.ui.QProcessingWindow import QProcessingWindow

def test_popup_window_with_components():
    """Test the all controls window with face swap components"""
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = QMainWindow()
    main_window.setWindowTitle("Test - All Controls Window with Components")
    main_window.setGeometry(100, 100, 500, 300)
    
    # Create central widget
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    
    # Create layout
    layout = QVBoxLayout()
    central_widget.setLayout(layout)
    
    # Add info label
    info_label = QLabel("Test Application for All Controls Window\n\nThis tests the popup window with face swap components.")
    info_label.setAlignment(Qt.AlignCenter)
    info_label.setStyleSheet("""
        QLabel {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 5px;
            color: #ffffff;
            font-size: 12px;
            padding: 20px;
        }
    """)
    layout.addWidget(info_label)
    
    # Create button to open all controls window
    open_btn = QPushButton("Open All Controls Window")
    open_btn.setMinimumHeight(50)
    open_btn.setStyleSheet("""
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
    """)
    
    def open_all_controls():
        """Open the all controls window"""
        try:
            # Create mock face swap components for testing
            mock_components = {
                'file_source': QLabel("Mock File Source Component"),
                'camera_source': QLabel("Mock Camera Source Component"),
                'face_detector': QLabel("Mock Face Detector Component"),
                'face_marker': QLabel("Mock Face Marker Component"),
                'face_aligner': QLabel("Mock Face Aligner Component"),
                'face_animator': QLabel("Mock Face Animator Component"),
                'face_swap_insight': QLabel("Mock Face Swap Insight Component"),
                'face_swap_dfm': QLabel("Mock Face Swap DFM Component"),
                'frame_adjuster': QLabel("Mock Frame Adjuster Component"),
                'face_merger': QLabel("Mock Face Merger Component"),
                'stream_output': QLabel("Mock Stream Output Component")
            }
            
            # Create and show the all controls window
            all_controls_window = QProcessingWindow(mock_components)
            all_controls_window.show()
            
            # Print tab information
            print("✅ All Controls Window opened successfully!")
            print(f"📋 Number of tabs: {all_controls_window.processing_tabs.count()}")
            
            tab_names = []
            for i in range(all_controls_window.processing_tabs.count()):
                tab_name = all_controls_window.processing_tabs.tabText(i)
                tab_names.append(tab_name)
                print(f"   Tab {i+1}: {tab_name}")
            
            print(f"\n🎯 All tabs created successfully: {', '.join(tab_names)}")
            print("✅ Face swap components passed correctly!")
            
        except Exception as e:
            print(f"❌ Error opening All Controls Window: {e}")
            import traceback
            traceback.print_exc()
    
    open_btn.clicked.connect(open_all_controls)
    layout.addWidget(open_btn)
    
    # Show main window
    main_window.show()
    
    print("🚀 Test application started")
    print("📝 Click 'Open All Controls Window' to test the popup with components")
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_popup_window_with_components() 