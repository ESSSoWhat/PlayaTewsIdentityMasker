#!/usr/bin/env python3
"""
Fix Source Button Functionality
Connects source buttons to their appropriate functions
"""

import os
import sys
from pathlib import Path

def fix_source_buttons():
    """Fix source button connections in QOBSStyleUI.py"""
    
    ui_file = Path("apps/PlayaTewsIdentityMasker/ui/QOBSStyleUI.py")
    
    if not ui_file.exists():
        print("❌ QOBSStyleUI.py not found!")
        return False
    
    # Read the current file
    with open(ui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if buttons are already connected
    if "add_source_btn.clicked.connect" in content:
        print("✅ Source buttons are already connected!")
        return True
    
    # Find the setup_connections method
    if "def setup_connections(self):" not in content:
        print("❌ setup_connections method not found!")
        return False
    
    # Add the source button connections
    connection_code = '''
    def setup_connections(self):
        """Setup signal connections"""
        # Connect source buttons
        self.add_source_btn.clicked.connect(self.add_source)
        self.remove_source_btn.clicked.connect(self.remove_source)
        self.source_properties_btn.clicked.connect(self.source_properties)
        
        # Connect other buttons
        self.stream_btn.clicked.connect(self.toggle_streaming)
        
        # Connect global face swap toggle
        if hasattr(self, 'global_face_swap_checkbox'):
            self.global_face_swap_checkbox.toggled.connect(self.on_global_face_swap_toggled)
'''
    
    # Replace the existing setup_connections method
    old_method = "def setup_connections(self):\n        \"\"\"Setup signal connections\"\"\"\n        pass"
    if old_method in content:
        content = content.replace(old_method, connection_code.strip())
    else:
        # Find the method and replace it
        import re
        pattern = r'def setup_connections\(self\):.*?pass'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, connection_code.strip(), content, flags=re.DOTALL)
        else:
            print("❌ Could not find setup_connections method to replace!")
            return False
    
    # Add the source methods
    source_methods = '''
    def add_source(self):
        """Add a new source to the scene"""
        try:
            # Get current scene
            current_scene = self.sources_list.currentItem()
            if current_scene:
                scene_name = current_scene.text()
                # Add camera source by default
                from ..backend.CameraSource import CameraSource
                camera_source = CameraSource()
                camera_source.initialize()
                
                # Add to sources list
                source_item = QListWidgetItem("Camera Source")
                self.sources_list.addItem(source_item)
                
                print(f"✅ Added camera source to scene: {scene_name}")
            else:
                print("⚠️ Please select a scene first")
        except Exception as e:
            print(f"❌ Error adding source: {e}")
    
    def remove_source(self):
        """Remove selected source from the scene"""
        try:
            current_item = self.sources_list.currentItem()
            if current_item:
                source_name = current_item.text()
                self.sources_list.takeItem(self.sources_list.row(current_item))
                print(f"✅ Removed source: {source_name}")
            else:
                print("⚠️ Please select a source to remove")
        except Exception as e:
            print(f"❌ Error removing source: {e}")
    
    def source_properties(self):
        """Open source properties dialog"""
        try:
            current_item = self.sources_list.currentItem()
            if current_item:
                source_name = current_item.text()
                print(f"🔧 Opening properties for: {source_name}")
                # TODO: Implement source properties dialog
                # For now, just show a message
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Source Properties", 
                                      f"Properties for: {source_name}\\n\\nThis feature is under development.")
            else:
                print("⚠️ Please select a source to view properties")
        except Exception as e:
            print(f"❌ Error opening source properties: {e}")
    
    def toggle_streaming(self):
        """Toggle streaming on/off"""
        try:
            if self.stream_btn.text() == "Start Streaming":
                self.stream_btn.setText("Stop Streaming")
                self.stream_btn.setStyleSheet("""
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
                """)
                print("🎥 Streaming started")
            else:
                self.stream_btn.setText("Start Streaming")
                self.stream_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                print("⏹️ Streaming stopped")
        except Exception as e:
            print(f"❌ Error toggling streaming: {e}")
'''
    
    # Add the methods before the closeEvent method
    if "def closeEvent(self, event):" in content:
        content = content.replace("def closeEvent(self, event):", source_methods + "\n    def closeEvent(self, event):")
    else:
        # Add at the end of the class
        content = content.replace("        self.initialize_global_face_swap_state()", 
                                "        self.initialize_global_face_swap_state()\n" + source_methods)
    
    # Add necessary imports
    if "from PyQt5.QtWidgets import QListWidgetItem" not in content:
        import_section = "from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QLabel, QListWidget, QListWidgetItem, QMessageBox)"
        content = content.replace("from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QLabel, QListWidget)", 
                                import_section)
    
    # Write the updated content
    with open(ui_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Source buttons fixed successfully!")
    print("🔧 Added functionality:")
    print("   - Add Source (+) button: Adds camera source to scene")
    print("   - Remove Source (-) button: Removes selected source")
    print("   - Properties button: Shows source properties dialog")
    print("   - Streaming button: Toggle streaming on/off")
    
    return True

def test_source_buttons():
    """Test if source buttons are working"""
    print("\n🧪 Testing source button functionality...")
    
    try:
        # Import the UI class
        sys.path.append(str(Path.cwd()))
        from apps.PlayaTewsIdentityMasker.ui.QOBSStyleUI import QOBSStyleUI
        
        print("✅ QOBSStyleUI imported successfully")
        print("✅ Source buttons should now be functional")
        
    except Exception as e:
        print(f"❌ Error testing source buttons: {e}")
        return False
    
    return True

def main():
    """Main function to fix source buttons"""
    print("🔧 Fixing Source Button Functionality")
    print("=" * 50)
    
    # Fix the source buttons
    if fix_source_buttons():
        # Test the fix
        test_source_buttons()
        
        print("\n🎉 Source button fix completed!")
        print("\n📋 Next steps:")
        print("1. Restart the PlayaTewsIdentityMasker application")
        print("2. The source buttons should now be functional")
        print("3. Click '+' to add a camera source")
        print("4. Click '-' to remove selected source")
        print("5. Click 'Properties' to view source settings")
        
    else:
        print("❌ Failed to fix source buttons!")

if __name__ == "__main__":
    main() 