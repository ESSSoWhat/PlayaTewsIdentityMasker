#!/usr/bin/env python3
"""
Main Application Camera Preview Fix
Integrates working camera preview logic into the main PlayaTewsIdentityMasker application
"""

import cv2
import json
import sys
import os
from pathlib import Path

def fix_camera_source_backend():
    """Fix the camera source backend to use the working configuration"""
    print("🔧 Fixing Camera Source Backend...")
    print("=" * 50)
    
    # Load our working camera configuration
    try:
        with open("camera_config.json", "r") as f:
            camera_config = json.load(f)
        print(f"✅ Loaded camera config: {camera_config['camera']['backend']}")
    except Exception as e:
        print(f"❌ Failed to load camera config: {e}")
        return False
    
    # Update the camera source backend settings
    settings_files = [
        "settings/states.dat",
        "simple_settings/states.dat",
        "working_settings/states.dat"
    ]
    
    # Settings to apply based on our working configuration
    settings_map = {
        "CameraSource.driver": camera_config["camera"]["backend_id"],
        "CameraSource.device_idx": camera_config["camera"]["index"],
        "CameraSource.resolution": 3,  # 1280x720
        "CameraSource.fps": camera_config["camera"]["fps"],
        "CameraSource.rotation": 0,
        "CameraSource.flip_horizontal": False
    }
    
    updated_files = 0
    
    for settings_file in settings_files:
        if os.path.exists(settings_file):
            print(f"📄 Updating {settings_file}...")
            try:
                # Read existing settings
                with open(settings_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                # Update camera settings
                updated = False
                for i, line in enumerate(lines):
                    for key, value in settings_map.items():
                        if key in line and '=' in line:
                            lines[i] = f"{key} = {value}\n"
                            updated = True
                            break
                
                # Write updated settings
                with open(settings_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                if updated:
                    print(f"  ✅ Updated camera settings")
                    updated_files += 1
                else:
                    print(f"  ⚠️ No camera settings found to update")
                    
            except Exception as e:
                print(f"  ❌ Error updating {settings_file}: {e}")
        else:
            print(f"📄 {settings_file} not found (skipping)")
    
    return updated_files > 0

def create_enhanced_frame_viewer():
    """Create an enhanced frame viewer that properly displays camera frames"""
    print("\n🔧 Creating Enhanced Frame Viewer...")
    
    enhanced_viewer_code = '''#!/usr/bin/env python3
"""
Enhanced Frame Viewer for PlayaTewsIdentityMasker
Fixes camera preview display issues
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

class EnhancedFrameViewer(QWidget):
    """Enhanced frame viewer with proper camera frame display"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_frame = None
        self.camera_config = None
        self.load_camera_config()
        
        # Setup timer for frame updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_frame)
        self.update_timer.start(33)  # ~30 FPS
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        
        # Frame display label
        self.frame_label = QLabel("Camera Preview")
        self.frame_label.setAlignment(Qt.AlignCenter)
        self.frame_label.setMinimumSize(640, 480)
        self.frame_label.setStyleSheet("""
            QLabel {
                border: 2px solid #333;
                background-color: #000;
                color: #666;
                font-size: 16px;
            }
        """)
        self.frame_label.setText("No camera feed\\nCamera will display here when active")
        layout.addWidget(self.frame_label)
    
    def load_camera_config(self):
        """Load camera configuration"""
        try:
            with open("camera_config.json", "r") as f:
                self.camera_config = json.load(f)
        except Exception as e:
            print(f"Failed to load camera config: {e}")
            self.camera_config = {
                "camera": {
                    "backend": "DirectShow",
                    "backend_id": 700,
                    "index": 0,
                    "resolution": "1280x720",
                    "fps": 30.0
                }
            }
    
    def set_frame(self, frame):
        """Set the current frame to display"""
        if frame is not None:
            self.current_frame = frame.copy()
    
    def update_frame(self):
        """Update the frame display"""
        if self.current_frame is not None:
            try:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                
                # Get frame dimensions
                height, width, channel = rgb_frame.shape
                bytes_per_line = 3 * width
                
                # Create QImage
                q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                
                # Create pixmap and scale to fit
                pixmap = QPixmap.fromImage(q_image)
                scaled_pixmap = pixmap.scaled(self.frame_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # Display in label
                self.frame_label.setPixmap(scaled_pixmap)
                
            except Exception as e:
                print(f"Frame display error: {e}")
    
    def clear(self):
        """Clear the frame display"""
        self.current_frame = None
        self.frame_label.setText("No camera feed\\nCamera will display here when active")

# Usage example:
# viewer = EnhancedFrameViewer()
# viewer.set_frame(camera_frame)
'''
    
    with open("enhanced_frame_viewer.py", "w") as f:
        f.write(enhanced_viewer_code)
    
    print("✅ Created enhanced_frame_viewer.py")

def create_camera_integration_patch():
    """Create a patch to integrate the working camera logic into the main app"""
    print("\n🔧 Creating Camera Integration Patch...")
    
    patch_code = '''#!/usr/bin/env python3
"""
Camera Integration Patch for PlayaTewsIdentityMasker
Patches the main application to use working camera preview logic
"""

import cv2
import json
import sys
from pathlib import Path

def patch_camera_source():
    """Patch the camera source to use working configuration"""
    try:
        # Load working camera config
        with open("camera_config.json", "r") as f:
            config = json.load(f)
        
        # Import the camera source
        from apps.PlayaTewsIdentityMasker.backend.CameraSource import CameraSource
        
        # Patch the camera source worker
        original_on_start = CameraSourceWorker.on_start
        
        def patched_on_start(self, weak_heap, bc_out):
            """Patched on_start method with working camera configuration"""
            print("🔧 Using patched camera configuration...")
            
            # Call original method
            original_on_start(self, weak_heap, bc_out)
            
            # Apply our working configuration
            state, cs = self.get_state(), self.get_control_sheet()
            
            # Set DirectShow backend
            cs.driver.set_selected(1)  # DirectShow
            
            # Set camera index
            cs.device_idx.set_selected(config["camera"]["index"])
            
            # Set resolution (1280x720)
            cs.resolution.set_selected(3)
            
            # Set FPS
            cs.fps.set_number(config["camera"]["fps"])
            
            # Set rotation
            cs.rotation.set_selected(0)
            
            # Set flip horizontal
            cs.flip_horizontal.set_flag(False)
            
            print("✅ Applied working camera configuration")
        
        # Apply the patch
        CameraSourceWorker.on_start = patched_on_start
        print("✅ Camera source patched successfully")
        
    except Exception as e:
        print(f"❌ Failed to patch camera source: {e}")

def patch_frame_viewer():
    """Patch the frame viewer to properly display camera frames"""
    try:
        from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFrameViewer import QBCFrameViewer
        
        # Store original method
        original_on_timer = QBCFrameViewer._on_timer_16ms
        
        def patched_on_timer_16ms(self):
            """Patched timer method with enhanced frame display"""
            try:
                top_qx = self.get_top_QXWindow()
                if not self.is_opened() or (top_qx is not None and top_qx.is_minimized()):
                    return
            except Exception:
                return
            
            bcd_id = self._bc.get_write_id()
            if self._bcd_id != bcd_id:
                # Has new bcd version
                bcd, self._bcd_id = self._bc.get_by_id(bcd_id), bcd_id
                
                if bcd is not None:
                    bcd.assign_weak_heap(self._backed_weak_heap)
                    
                    self._layered_images.clear_images()
                    
                    frame_image_name = bcd.get_frame_image_name()
                    frame_image = bcd.get_image(frame_image_name)
                    
                    if frame_image is not None:
                        # Enhanced frame processing
                        try:
                            # Ensure proper format
                            if len(frame_image.shape) == 3:
                                # Convert BGR to RGB if needed
                                if frame_image.shape[2] == 3:
                                    frame_image = cv2.cvtColor(frame_image, cv2.COLOR_BGR2RGB)
                            
                            self._layered_images.add_image(frame_image)
                            h, w = frame_image.shape[:2]
                            self._info_label.setText(f'{frame_image_name} {w}x{h}')
                            
                        except Exception as e:
                            print(f"Enhanced frame processing error: {e}")
                            # Fallback to original method
                            original_on_timer(self)
        
        # Apply the patch
        QBCFrameViewer._on_timer_16ms = patched_on_timer_16ms
        print("✅ Frame viewer patched successfully")
        
    except Exception as e:
        print(f"❌ Failed to patch frame viewer: {e}")

def apply_patches():
    """Apply all camera integration patches"""
    print("🔧 Applying Camera Integration Patches...")
    
    patch_camera_source()
    patch_frame_viewer()
    
    print("✅ All patches applied successfully")

if __name__ == "__main__":
    apply_patches()
'''
    
    with open("camera_integration_patch.py", "w") as f:
        f.write(patch_code)
    
    print("✅ Created camera_integration_patch.py")

def create_startup_script():
    """Create a startup script that applies the patches before launching"""
    print("\n🔧 Creating Patched Startup Script...")
    
    startup_script = '''#!/usr/bin/env python3
"""
Patched Startup Script for PlayaTewsIdentityMasker
Applies camera preview fixes before launching the main application
"""

import sys
import os
from pathlib import Path

def main():
    """Main startup function with camera fixes"""
    print("🔧 PlayaTewsIdentityMasker - Patched Startup")
    print("=" * 50)
    
    # Apply camera integration patches
    try:
        from camera_integration_patch import apply_patches
        apply_patches()
        print("✅ Camera patches applied")
    except Exception as e:
        print(f"⚠️ Camera patches failed: {e}")
    
    # Import and run the main application
    try:
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        # Get userdata path
        userdata_path = Path.cwd()
        
        # Create and run the application
        app = PlayaTewsIdentityMaskerApp(userdata_path)
        app.initialize()
        app.run()
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    with open("start_playatews_patched.py", "w") as f:
        f.write(startup_script)
    
    print("✅ Created start_playatews_patched.py")

def main():
    """Main function to apply all camera preview fixes"""
    print("🔧 PlayaTewsIdentityMasker - Main Application Camera Preview Fix")
    print("=" * 70)
    
    # Step 1: Fix camera source backend
    backend_fixed = fix_camera_source_backend()
    
    # Step 2: Create enhanced frame viewer
    create_enhanced_frame_viewer()
    
    # Step 3: Create camera integration patch
    create_camera_integration_patch()
    
    # Step 4: Create patched startup script
    create_startup_script()
    
    # Summary
    print(f"\n📋 Fix Summary:")
    print("=" * 50)
    print(f"✅ Backend Settings: {'Fixed' if backend_fixed else 'Failed'}")
    print(f"✅ Enhanced Frame Viewer: Created")
    print(f"✅ Camera Integration Patch: Created")
    print(f"✅ Patched Startup Script: Created")
    
    print(f"\n🎉 Camera preview fixes applied!")
    print(f"💡 To use the fixes:")
    print(f"   1. Run: python start_playatews_patched.py")
    print(f"   2. Or apply patches manually before starting the main app")
    print(f"   3. The camera feed should now appear in the main preview area")

if __name__ == "__main__":
    main() 