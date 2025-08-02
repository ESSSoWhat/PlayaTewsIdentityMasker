#!/usr/bin/env python3
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
        from apps.PlayaTewsIdentityMasker.backend.CameraSource import CameraSource, CameraSourceWorker
        
        # Patch the camera source worker
        original_on_start = CameraSourceWorker.on_start
        
        def patched_on_start(self, weak_heap, bc_out):
            """Patched on_start method with working camera configuration"""
            print("Using patched camera configuration...")
            
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
            
            print("Applied working camera configuration")
        
        # Apply the patch
        CameraSourceWorker.on_start = patched_on_start
        print("Camera source patched successfully")
        
    except Exception as e:
        print(f"Failed to patch camera source: {e}")

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
        print("Frame viewer patched successfully")
        
    except Exception as e:
        print(f"Failed to patch frame viewer: {e}")

def apply_patches():
    """Apply all camera integration patches"""
    print("Applying Camera Integration Patches...")
    
    patch_camera_source()
    patch_frame_viewer()
    
    print("All patches applied successfully")

if __name__ == "__main__":
    apply_patches()
