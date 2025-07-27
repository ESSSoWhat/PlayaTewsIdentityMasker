#!/usr/bin/env python3
"""
Standalone demo script for Global Face Swap Control functionality
This demonstrates the core logic without complex dependencies
"""

import json
import time
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QWidget, QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys

class MockFaceSwapComponent:
    """Mock face swap component for testing"""
    def __init__(self, name):
        self.name = name
        self._backend = MockBackend()
        self.enabled = True
    
    def findChildren(self, widget_type):
        """Mock findChildren method"""
        if widget_type.__name__ == 'QCheckBox':
            return [MockCheckBox(self.enabled)]
        return []

class MockBackend:
    """Mock backend for testing"""
    def __init__(self):
        self.running = True
    
    def start(self):
        self.running = True
        print(f"Mock backend started")
    
    def stop(self):
        self.running = False
        print(f"Mock backend stopped")
    
    def is_started(self):
        return self.running
    
    def is_running(self):
        return self.running

class MockCheckBox:
    """Mock checkbox for testing"""
    def __init__(self, checked=True):
        self._checked = checked
    
    def isCheckable(self):
        return True
    
    def setChecked(self, checked):
        self._checked = checked
        print(f"Mock checkbox set to: {checked}")

class GlobalFaceSwapControlDemo(QMainWindow):
    """Demo window for global face swap control"""
    
    def __init__(self):
        super().__init__()
        self.userdata_path = Path("demo_settings")
        self.face_swap_components = {}
        self.setup_mock_components()
        self.setup_ui()
        self.setup_connections()
        self.initialize_global_face_swap_state()
        
    def setup_mock_components(self):
        """Setup mock face swap components"""
        component_names = [
            'face_detector', 'face_marker', 'face_aligner', 
            'face_animator', 'face_swap_insight', 'face_swap_dfm',
            'frame_adjuster', 'face_merger'
        ]
        
        for name in component_names:
            self.face_swap_components[name] = MockFaceSwapComponent(name)
    
    def setup_ui(self):
        """Setup the demo UI"""
        self.setWindowTitle("Global Face Swap Control Demo")
        self.setGeometry(100, 100, 600, 400)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Global Face Swap Control Demo")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Global control section
        control_group = QGroupBox("Global Face Swap Control")
        control_layout = QVBoxLayout()
        
        # Global face swap button
        self.global_face_swap_btn = QPushButton("Face Swap: ON")
        self.global_face_swap_btn.setMinimumHeight(40)
        self.global_face_swap_btn.setCheckable(True)
        self.global_face_swap_btn.setChecked(True)
        self.global_face_swap_btn.setToolTip("Click to toggle all face swap components on/off\nGreen = ON, Red = OFF")
        self.global_face_swap_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:checked {
                background-color: #27ae60;
            }
            QPushButton:!checked {
                background-color: #e74c3c;
            }
        """)
        control_layout.addWidget(self.global_face_swap_btn)
        
        # Status label
        self.status_label = QLabel("Status: All components ENABLED")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        control_layout.addWidget(self.status_label)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Component status section
        status_group = QGroupBox("Component Status")
        status_layout = QVBoxLayout()
        
        self.component_labels = {}
        for component_name in self.face_swap_components.keys():
            label = QLabel(f"{component_name.replace('_', ' ').title()}: ENABLED")
            label.setStyleSheet("color: #27ae60;")
            self.component_labels[component_name] = label
            status_layout.addWidget(label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # State persistence info
        info_group = QGroupBox("State Persistence")
        info_layout = QVBoxLayout()
        
        self.state_info = QLabel("State will be saved to: demo_settings/settings/global_face_swap_state.json")
        self.state_info.setWordWrap(True)
        info_layout.addWidget(self.state_info)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        main_widget.setLayout(layout)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.global_face_swap_btn.toggled.connect(self.on_global_face_swap_toggled)
    
    def on_global_face_swap_toggled(self, enabled):
        """Handle global face swap enable/disable"""
        try:
            if enabled:
                self.global_face_swap_btn.setText("Face Swap: ON")
                self.global_face_swap_btn.setToolTip("Face swap is ENABLED\nAll components are running\nClick to disable")
                self.status_label.setText("Status: All components ENABLED")
                self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                self.enable_all_face_swap_components()
                print("Global face swap enabled")
            else:
                self.global_face_swap_btn.setText("Face Swap: OFF")
                self.global_face_swap_btn.setToolTip("Face swap is DISABLED\nAll components are stopped\nClick to enable")
                self.status_label.setText("Status: All components DISABLED")
                self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
                self.disable_all_face_swap_components()
                print("Global face swap disabled")
            
            # Save the state
            self.save_global_face_swap_state(enabled)
            
        except Exception as e:
            print(f"Error toggling global face swap: {e}")
    
    def enable_all_face_swap_components(self):
        """Enable all face swap components"""
        if not self.face_swap_components:
            return
        
        components_to_enable = [
            'face_detector', 'face_marker', 'face_aligner', 
            'face_animator', 'face_swap_insight', 'face_swap_dfm',
            'frame_adjuster', 'face_merger'
        ]
        
        for component_name in components_to_enable:
            if component_name in self.face_swap_components:
                component = self.face_swap_components[component_name]
                try:
                    # Enable the component
                    component.enabled = True
                    if hasattr(component, '_backend') and hasattr(component._backend, 'start'):
                        component._backend.start()
                    
                    # Update UI
                    if component_name in self.component_labels:
                        self.component_labels[component_name].setText(f"{component_name.replace('_', ' ').title()}: ENABLED")
                        self.component_labels[component_name].setStyleSheet("color: #27ae60;")
                    
                    # Enable checkboxes
                    self._enable_component_checkboxes(component, True)
                except Exception as e:
                    print(f"Error enabling {component_name}: {e}")
    
    def disable_all_face_swap_components(self):
        """Disable all face swap components"""
        if not self.face_swap_components:
            return
        
        components_to_disable = [
            'face_detector', 'face_marker', 'face_aligner', 
            'face_animator', 'face_swap_insight', 'face_swap_dfm',
            'frame_adjuster', 'face_merger'
        ]
        
        for component_name in components_to_disable:
            if component_name in self.face_swap_components:
                component = self.face_swap_components[component_name]
                try:
                    # Disable the component
                    component.enabled = False
                    if hasattr(component, '_backend') and hasattr(component._backend, 'stop'):
                        component._backend.stop()
                    
                    # Update UI
                    if component_name in self.component_labels:
                        self.component_labels[component_name].setText(f"{component_name.replace('_', ' ').title()}: DISABLED")
                        self.component_labels[component_name].setStyleSheet("color: #e74c3c;")
                    
                    # Disable checkboxes
                    self._enable_component_checkboxes(component, False)
                except Exception as e:
                    print(f"Error disabling {component_name}: {e}")
    
    def _enable_component_checkboxes(self, component, enabled):
        """Enable or disable checkboxes in a component"""
        try:
            checkboxes = component.findChildren(type(QCheckBox()))
            for checkbox in checkboxes:
                if checkbox.isCheckable():
                    checkbox.setChecked(enabled)
        except Exception as e:
            print(f"Error setting checkboxes in component: {e}")
    
    def save_global_face_swap_state(self, enabled):
        """Save the global face swap state to persistent storage"""
        try:
            # Create settings directory if it doesn't exist
            settings_dir = self.userdata_path / 'settings'
            settings_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to a JSON file
            state_file = settings_dir / 'global_face_swap_state.json'
            state_data = {
                'enabled': enabled,
                'timestamp': str(time.time())
            }
            
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            print(f"State saved to: {state_file}")
                
        except Exception as e:
            print(f"Error saving global face swap state: {e}")
    
    def load_global_face_swap_state(self):
        """Load the global face swap state from persistent storage"""
        try:
            state_file = self.userdata_path / 'settings' / 'global_face_swap_state.json'
            
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                
                enabled = state_data.get('enabled', True)
                print(f"State loaded from: {state_file}")
                return enabled
            else:
                print("No saved state found, using default (enabled)")
                return True
                
        except Exception as e:
            print(f"Error loading global face swap state: {e}")
            return True
    
    def initialize_global_face_swap_state(self):
        """Initialize the global face swap state on startup"""
        try:
            enabled = self.load_global_face_swap_state()
            self.global_face_swap_btn.setChecked(enabled)
            self.on_global_face_swap_toggled(enabled)
        except Exception as e:
            print(f"Error initializing global face swap state: {e}")

def main():
    """Main function to run the demo"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the demo window
    demo = GlobalFaceSwapControlDemo()
    demo.show()
    
    print("🚀 Global Face Swap Control Demo Started")
    print("📋 Features demonstrated:")
    print("   ✅ Single button control for all face swap components")
    print("   ✅ Visual feedback (Green=ON, Red=OFF)")
    print("   ✅ State persistence across app restarts")
    print("   ✅ Dynamic tooltips with status information")
    print("   ✅ Component status display")
    print("   ✅ Error handling and graceful fallbacks")
    print("\n🎛️ Instructions:")
    print("   1. Click the 'Face Swap: ON' button to toggle")
    print("   2. Watch the component status updates")
    print("   3. Check the console for backend operations")
    print("   4. State is automatically saved to demo_settings/")
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 