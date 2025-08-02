#!/usr/bin/env python3
"""
Simple Camera Preview Test
Tests the camera preview functionality
"""

import cv2
import json
import time

def test_camera_preview():
    """Test camera preview with the working configuration"""
    print("🎬 Camera Preview Test")
    print("=" * 40)
    
    try:
        # Load camera configuration
        with open("camera_config.json", "r") as f:
            config = json.load(f)
        
        backend_id = config["camera"]["backend_id"]
        camera_index = config["camera"]["index"]
        
        print(f"📹 Opening camera: {config['camera']['backend']}")
        print(f"📐 Resolution: {config['camera']['resolution']}")
        print(f"🎯 FPS: {config['camera']['fps']:.1f}")
        
        # Open camera
        cap = cv2.VideoCapture(camera_index, backend_id)
        if not cap.isOpened():
            print("❌ Failed to open camera")
            return False
        
        # Set properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        print("📸 Starting preview (press 'q' to quit)...")
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("❌ Failed to read frame")
                break
            
            frame_count += 1
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            if elapsed_time > 0:
                fps = frame_count / elapsed_time
            else:
                fps = 0
            
            # Add FPS text to frame
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Frame: {frame_count}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'q' to quit", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow("Camera Preview Test", frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"✅ Preview test completed!")
        print(f"📊 Frames captured: {frame_count}")
        print(f"📊 Average FPS: {fps:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Preview test error: {e}")
        return False

def main():
    """Main function"""
    print("🔧 PlayaTewsIdentityMasker - Camera Preview Test")
    print("=" * 50)
    
    success = test_camera_preview()
    
    if success:
        print("\n🎉 Camera preview is working correctly!")
        print("💡 You can now run your main application.")
    else:
        print("\n❌ Camera preview test failed.")
        print("💡 Try running the fix script again.")

if __name__ == "__main__":
    main() 