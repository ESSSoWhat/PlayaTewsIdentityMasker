#!/usr/bin/env python3
"""
Test Camera Data Flow for PlayaTewsIdentityMasker
Focused test to verify camera data flows through backend connections
"""

import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.append('.')

def test_camera_data_flow():
    """Test camera data flow through backend connections"""
    print("🔍 Testing Camera Data Flow...")
    print("=" * 50)
    
    try:
        # Import backend components
        from apps.PlayaTewsIdentityMasker import backend
        
        # Create backend components
        backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)
        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        
        # Create camera source
        camera_source = backend.CameraSource(
            weak_heap=backend_weak_heap, 
            bc_out=multi_sources_bc_out, 
            backend_db=None
        )
        
        # Start camera source
        camera_source.start()
        print("✅ Camera source started")
        
        # Wait for initialization and data flow
        print("⏳ Waiting for camera data flow...")
        time.sleep(5)
        
        # Check for data in backend connection multiple times
        for i in range(10):
            bcd_id = multi_sources_bc_out.get_write_id()
            print(f"Check {i+1}: Backend connection write ID = {bcd_id}")
            
            if bcd_id > 0:
                bcd = multi_sources_bc_out.get_by_id(bcd_id)
                if bcd is not None:
                    bcd.assign_weak_heap(backend_weak_heap)
                    frame_image_name = bcd.get_frame_image_name()
                    frame_image = bcd.get_image(frame_image_name)
                    
                    if frame_image is not None:
                        print(f"✅ Camera data flowing: {frame_image.shape}")
                        print(f"   Frame name: {frame_image_name}")
                        print(f"   Frame number: {bcd.get_frame_num()}")
                        print(f"   Timestamp: {bcd.get_frame_timestamp()}")
                        break
                    else:
                        print(f"❌ No frame image in backend connection (attempt {i+1})")
                else:
                    print(f"❌ No backend connection data (attempt {i+1})")
            else:
                print(f"❌ No data in backend connection (attempt {i+1})")
            
            time.sleep(1)
        else:
            print("❌ No camera data detected after 10 attempts")
        
        # Stop camera source
        camera_source.stop()
        print("✅ Camera source stopped")
        
    except Exception as e:
        print(f"❌ Camera data flow test error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🎬 PlayaTewsIdentityMasker - Camera Data Flow Test")
    print("=" * 60)
    print()
    
    test_camera_data_flow()
    
    print("\n📊 Test Complete!")
    print("=" * 40)

if __name__ == "__main__":
    main() 