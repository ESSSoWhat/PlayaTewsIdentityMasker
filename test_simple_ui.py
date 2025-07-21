#!/usr/bin/env python3
"""
Simple UI Test Script
Tests basic Qt functionality without complex face swap components
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

def test_basic_qt():
    """Test basic Qt functionality"""
    app = QApplication(sys.argv)
    
    # Create a simple main window
    window = QMainWindow()
    window.setWindowTitle("Simple UI Test")
    window.setGeometry(100, 100, 800, 600)
    
    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # Create layout
    layout = QVBoxLayout()
    central_widget.setLayout(layout)
    
    # Add some test widgets
    label = QLabel("Basic Qt Test - If you can see this, Qt is working!")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)
    
    button = QPushButton("Test Button")
    layout.addWidget(button)
    
    # Show the window
    window.show()
    
    print("✅ Basic Qt test window should be visible")
    print("   If you can see the window, Qt is working correctly")
    
    # Run the app
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_basic_qt() 