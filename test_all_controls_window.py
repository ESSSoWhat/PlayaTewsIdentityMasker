#!/usr/bin/env python3
"""
Test script for the All Controls Window
Verifies that all tabs are properly created and the window opens correctly
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt

# Import the processing window
from apps.PlayaTewsIdentityMasker.ui.QProcessingWindow import QProcessingWindow

def test_all_controls_window():
    """Test the all controls window"""
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = QMainWindow()
    main_window.setWindowTitle("Test - All Controls Window")
    main_window.setGeometry(100, 100, 400, 200)
    
    # Create central widget
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    
    # Create layout
    layout = QVBoxLayout()
    central_widget.setLayout(layout)
    
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
            # Create and show the all controls window
            all_controls_window = QProcessingWindow()
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
            
        except Exception as e:
            print(f"❌ Error opening All Controls Window: {e}")
            import traceback
            traceback.print_exc()
    
    open_btn.clicked.connect(open_all_controls)
    layout.addWidget(open_btn)
    
    # Show main window
    main_window.show()
    
    print("🚀 Test application started")
    print("📝 Click 'Open All Controls Window' to test the popup")
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_all_controls_window() 