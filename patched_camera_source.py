#!/usr/bin/env python3
"""
Patched Camera Source for PlayaTewsIdentityMasker
Fixes the camera integration issue where data doesn't reach backend connection
"""

import cv2
import time
import numpy as np
from pathlib import Path
import sys
import os

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def create_fixed_camera_source():
    """Create a fixed camera source that properly connects to backend"""
    try:
        from apps.PlayaTewsIdentityMasker.backend.CameraSource import CameraSource, CameraSourceWorker, Sheet, WorkerState
        from apps.PlayaTewsIdentityMasker import backend
        
        # Create a fixed camera source worker
        class FixedCameraSourceWorker(CameraSourceWorker):
            def on_start(self, weak_heap, bc_out):
                super().on_start(weak_heap, bc_out)
                
                print("🔧 Fixed Camera Source Worker starting...")
                
                # Force DirectShow backend
                state, cs = self.get_state(), self.get_control_sheet()
                
                # Set DirectShow backend
                state.driver = 1  # DirectShow
                state.device_idx = 0
                state.resolution = 3  # 1280x720
                state.fps = 30.0
                state.rotation = 0
                state.flip_horizontal = False
                
                # Save state
                self.save_state()
                
                # Initialize camera with enhanced retry logic
                success = self._init_camera_with_enhanced_retry()
                
                if success:
                    print("✅ Fixed camera source initialized successfully")
                else:
                    print("❌ Fixed camera source initialization failed")
            
            def _init_camera_with_enhanced_retry(self, max_retries=5):
                """Initialize camera with enhanced retry logic"""
                for attempt in range(max_retries):
                    try:
                        print(f"🔧 Camera initialization attempt {attempt + 1}/{max_retries}")
                        
                        # Force DirectShow backend
                        cv_api = cv2.CAP_DSHOW
                        
                        # Open camera
                        vcap = cv2.VideoCapture(0, cv_api)
                        
                        if vcap.isOpened():
                            print("✅ Camera opened successfully")
                            
                            # Set resolution
                            vcap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                            vcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                            vcap.set(cv2.CAP_PROP_FPS, 30)
                            
                            # Test frame reading multiple times
                            success_count = 0
                            for i in range(5):
                                ret, frame = vcap.read()
                                if ret:
                                    success_count += 1
                                    print(f"✅ Frame {i+1} read successful: {frame.shape}")
                                else:
                                    print(f"❌ Frame {i+1} read failed")
                                time.sleep(0.1)
                            
                            if success_count >= 3:  # At least 3 out of 5 frames
                                print(f"✅ Frame reading test passed: {success_count}/5 frames")
                                self.set_vcap(vcap)
                                return True
                            else:
                                print(f"❌ Frame reading test failed: {success_count}/5 frames")
                                vcap.release()
                        else:
                            print("❌ Failed to open camera")
                        
                        time.sleep(2)  # Wait longer before retry
                        
                    except Exception as e:
                        print(f"❌ Camera initialization error: {e}")
                        time.sleep(2)
                
                print("❌ All camera initialization attempts failed")
                return False
            
            def on_tick(self):
                """Enhanced tick method with better error handling"""
                try:
                    if self.vcap is not None and not self.vcap.isOpened():
                        print("⚠️ Camera connection lost, attempting to reconnect...")
                        self.set_vcap(None)
                        self._init_camera_with_enhanced_retry(max_retries=3)
                        return

                    if self.vcap is not None:
                        state, cs = self.get_state(), self.get_control_sheet()

                        self.start_profile_timing()
                        ret, img = self.vcap.read()
                        if ret:
                            timestamp = time.time()
                            fps = state.fps
                            if fps == 0 or ((timestamp - self.last_timestamp) > 1.0 / fps):

                                if fps != 0:
                                    if timestamp - self.last_timestamp >= 1.0:
                                        self.last_timestamp = timestamp
                                    else:
                                        self.last_timestamp += 1.0 / fps

                                # Process image
                                from xlib.image import ImageProcessor
                                ip = ImageProcessor(img)
                                ip.ch(3).to_uint8()

                                # Set resolution
                                w, h = (1280, 720)  # Force 1280x720
                                ip.fit_in(TW=w)

                                # Apply transformations
                                if state.rotation == 1:  # 90 degrees
                                    ip.rotate90()
                                elif state.rotation == 2:  # 180 degrees
                                    ip.rotate180()
                                elif state.rotation == 3:  # 270 degrees
                                    ip.rotate270()

                                if state.flip_horizontal:
                                    ip.flip_horizontal()

                                img = ip.get_image('HWC')

                                # Create backend connection data
                                bcd_uid = self.bcd_uid = self.bcd_uid + 1
                                bcd = backend.BackendConnectionData(uid=bcd_uid)

                                bcd.assign_weak_heap(self.weak_heap)
                                frame_name = f'Camera_{state.device_idx}_{bcd_uid:06}'
                                bcd.set_frame_image_name(frame_name)
                                bcd.set_frame_num(bcd_uid)
                                bcd.set_frame_timestamp(timestamp)
                                bcd.set_image(frame_name, img)
                                self.stop_profile_timing()
                                self.pending_bcd = bcd

                                # Debug output
                                if bcd_uid % 30 == 0:  # Every 30 frames
                                    print(f"📹 Camera frame {bcd_uid} processed and sent to backend")

                    if self.pending_bcd is not None:
                        if self.bc_out.is_full_read(1):
                            self.bc_out.write(self.pending_bcd)
                            self.pending_bcd = None

                    time.sleep(0.001)
                    
                except Exception as e:
                    print(f"❌ Error in camera tick: {e}")
                    time.sleep(0.1)  # Wait before retry
        
        # Create a fixed camera source
        class FixedCameraSource(CameraSource):
            def __init__(self, weak_heap, bc_out, backend_db=None):
                super().__init__(backend_db=backend_db,
                                 sheet_cls=Sheet,
                                 worker_cls=FixedCameraSourceWorker,
                                 worker_state_cls=WorkerState,
                                 worker_start_args=[weak_heap, bc_out])
        
        print("✅ Fixed camera source created")
        return FixedCameraSource
        
    except Exception as e:
        print(f"❌ Error creating fixed camera source: {e}")
        return None

def test_fixed_camera_integration():
    """Test the fixed camera integration"""
    print("\n🔍 Testing Fixed Camera Integration...")
    print("=" * 50)
    
    try:
        from apps.PlayaTewsIdentityMasker import backend
        
        # Create backend components
        backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)
        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        
        # Get fixed camera source
        FixedCameraSource = create_fixed_camera_source()
        if FixedCameraSource is None:
            return False
        
        # Create camera source
        camera_source = FixedCameraSource(
            weak_heap=backend_weak_heap,
            bc_out=multi_sources_bc_out,
            backend_db=None
        )
        
        print("✅ Fixed camera source created")
        
        # Start camera source
        camera_source.start()
        print("✅ Fixed camera source started")
        
        # Wait for data with longer timeout
        print("⏳ Waiting for camera data (up to 10 seconds)...")
        start_time = time.time()
        
        while time.time() - start_time < 10:
            bcd_id = multi_sources_bc_out.get_write_id()
            if bcd_id > 0:
                bcd = multi_sources_bc_out.get_by_id(bcd_id)
                if bcd is not None:
                    bcd.assign_weak_heap(backend_weak_heap)
                    frame_image_name = bcd.get_frame_image_name()
                    frame_image = bcd.get_image(frame_image_name)
                    
                    if frame_image is not None:
                        print(f"✅ Camera data received!")
                        print(f"   Frame name: {frame_image_name}")
                        print(f"   Frame shape: {frame_image.shape}")
                        print(f"   Frame type: {frame_image.dtype}")
                        print(f"   Time to receive: {time.time() - start_time:.2f} seconds")
                        camera_source.stop()
                        return True
            
            time.sleep(0.5)
            print(f"⏳ Still waiting... ({time.time() - start_time:.1f}s)")
        
        print("❌ No camera data received within timeout")
        camera_source.stop()
        return False
        
    except Exception as e:
        print(f"❌ Error testing fixed camera integration: {e}")
        return False

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Integration Fix")
    print("=" * 60)
    print()
    
    # Create camera integration fix
    fix_file = create_camera_integration_fix()
    
    # Test fixed camera integration
    success = test_fixed_camera_integration()
    
    print("\n📊 Results:")
    print("=" * 40)
    if success:
        print("✅ Camera integration fix successful!")
        print("   Camera data is now reaching the backend connection")
        print("   Preview area should now show camera feed")
    else:
        print("❌ Camera integration fix failed")
        print("   Additional debugging needed")
    
    print("\n🚀 Next Steps:")
    print("   1. Restart the main application")
    print("   2. Camera feed should now appear in preview area")
    print("   3. If still not working, check camera permissions")

if __name__ == "__main__":
    main()
