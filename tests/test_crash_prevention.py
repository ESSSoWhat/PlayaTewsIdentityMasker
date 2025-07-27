#!/usr/bin/env python3
"""
Test script for crash prevention in the All Controls Window
Verifies that the popup window opens without crashing even with missing components
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt

# Import the processing window
from apps.PlayaTewsIdentityMasker.ui.QProcessingWindow import QProcessingWindow

def test_crash_prevention():
    """Test crash prevention with various component scenarios"""
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = QMainWindow()
    main_window.setWindowTitle("Test - Crash Prevention")
    main_window.setGeometry(100, 100, 600, 400)
    
    # Create central widget
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    
    # Create layout
    layout = QVBoxLayout()
    central_widget.setLayout(layout)
    
    # Add info label
    info_label = QLabel("Crash Prevention Test\n\nTesting various scenarios to ensure the popup window doesn't crash.")
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
    
    # Test 1: No components
    test1_btn = QPushButton("Test 1: No Components (None)")
    test1_btn.setMinimumHeight(40)
    test1_btn.setStyleSheet("""
        QPushButton {
            background-color: #e74c3c;
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #c0392b;
        }
    """)
    
    def test_no_components():
        """Test with no components"""
        try:
            print("🧪 Testing with no components...")
            all_controls_window = QProcessingWindow(None)
            all_controls_window.show()
            print("✅ Test 1 PASSED: No components handled correctly")
        except Exception as e:
            print(f"❌ Test 1 FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    test1_btn.clicked.connect(test_no_components)
    layout.addWidget(test1_btn)
    
    # Test 2: Empty components
    test2_btn = QPushButton("Test 2: Empty Components ({})")
    test2_btn.setMinimumHeight(40)
    test2_btn.setStyleSheet("""
        QPushButton {
            background-color: #f39c12;
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #d68910;
        }
    """)
    
    def test_empty_components():
        """Test with empty components dict"""
        try:
            print("🧪 Testing with empty components...")
            all_controls_window = QProcessingWindow({})
            all_controls_window.show()
            print("✅ Test 2 PASSED: Empty components handled correctly")
        except Exception as e:
            print(f"❌ Test 2 FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    test2_btn.clicked.connect(test_empty_components)
    layout.addWidget(test2_btn)
    
    # Test 3: Partial components
    test3_btn = QPushButton("Test 3: Partial Components (some missing)")
    test3_btn.setMinimumHeight(40)
    test3_btn.setStyleSheet("""
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
    """)
    
    def test_partial_components():
        """Test with partial components"""
        try:
            print("🧪 Testing with partial components...")
            partial_components = {
                'file_source': QLabel("Mock File Source"),
                'face_detector': QLabel("Mock Face Detector"),
                # Missing other components
            }
            all_controls_window = QProcessingWindow(partial_components)
            all_controls_window.show()
            print("✅ Test 3 PASSED: Partial components handled correctly")
        except Exception as e:
            print(f"❌ Test 3 FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    test3_btn.clicked.connect(test_partial_components)
    layout.addWidget(test3_btn)
    
    # Test 4: Invalid components
    test4_btn = QPushButton("Test 4: Invalid Components (None values)")
    test4_btn.setMinimumHeight(40)
    test4_btn.setStyleSheet("""
        QPushButton {
            background-color: #9b59b6;
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #8e44ad;
        }
    """)
    
    def test_invalid_components():
        """Test with invalid components"""
        try:
            print("🧪 Testing with invalid components...")
            invalid_components = {
                'file_source': None,
                'face_detector': "Not a widget",
                'face_aligner': 123,
                'face_marker': QLabel("Valid Widget")
            }
            all_controls_window = QProcessingWindow(invalid_components)
            all_controls_window.show()
            print("✅ Test 4 PASSED: Invalid components handled correctly")
        except Exception as e:
            print(f"❌ Test 4 FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    test4_btn.clicked.connect(test_invalid_components)
    layout.addWidget(test4_btn)
    
    # Show main window
    main_window.show()
    
    print("🚀 Crash Prevention Test started")
    print("📝 Click buttons to test different scenarios")
    print("🎯 All tests should open popup windows without crashing")
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_crash_prevention() 