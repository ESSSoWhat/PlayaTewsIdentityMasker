#!/usr/bin/env python3
"""
Minimal test script to isolate the QTabWidget error
"""

from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel

def test_basic_widgets():
    """Test basic widget creation"""
    print("Testing basic widgets...")
    
    # Test QXLabel
    try:
        label = QXLabel(text="Test Label")
        print("✓ QXLabel created successfully")
    except Exception as e:
        print(f"✗ QXLabel failed: {e}")
    
    # Test QXFrame
    try:
        from xlib.qt.widgets.QXFrame import QXFrame
        frame = QXFrame()
        print("✓ QXFrame created successfully")
    except Exception as e:
        print(f"✗ QXFrame failed: {e}")
    
    # Test QXCollapsibleSection
    try:
        from xlib.qt.widgets.QXCollapsibleSection import QXCollapsibleSection
        from xlib.qt.widgets.QXVBoxLayout import QXVBoxLayout
        
        content_layout = QXVBoxLayout()
        collapsible = QXCollapsibleSection("Test Section", content_layout)
        print("✓ QXCollapsibleSection created successfully")
    except Exception as e:
        print(f"✗ QXCollapsibleSection failed: {e}")

def test_collapsible_wrapper():
    """Test collapsible wrapper"""
    print("\nTesting collapsible wrapper...")
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.widgets.QCollapsibleComponentWrapper import QCollapsibleComponentWrapper
        
        # Create a simple test widget
        test_widget = QWidget()
        test_layout = QVBoxLayout()
        test_layout.addWidget(QLabel("Test Component"))
        test_widget.setLayout(test_layout)
        
        # Create collapsible wrapper
        wrapper = QCollapsibleComponentWrapper(
            component=test_widget,
            title="Test Component",
            is_opened=False
        )
        print("✓ QCollapsibleComponentWrapper created successfully")
    except Exception as e:
        print(f"✗ QCollapsibleComponentWrapper failed: {e}")

def test_optimized_components():
    """Test optimized components"""
    print("\nTesting optimized components...")
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.QOptimizedFaceMarker import QOptimizedFaceMarker
        print("✓ QOptimizedFaceMarker imported successfully")
    except Exception as e:
        print(f"✗ QOptimizedFaceMarker import failed: {e}")

if __name__ == "__main__":
    # Create QApplication
    app = QApplication([])
    
    print("=== Minimal Optimized App Test ===")
    
    test_basic_widgets()
    test_collapsible_wrapper()
    test_optimized_components()
    
    print("\n=== Test Complete ===") 