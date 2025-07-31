#!/usr/bin/env python3
"""
Integration test script for enhanced UI components
Tests all the new UI/UX improvements with mock data
"""

import sys
import os
from pathlib import Path
import numpy as np
import time
import random

# Add the application path to Python path
current_dir = Path(__file__).parent
app_path = current_dir / 'apps' / 'PlayaTewsIdentityMasker'
sys.path.insert(0, str(app_path))

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox, QListWidgetItem
    from PyQt5.QtCore import QTimer, QThread, pyqtSignal
    from PyQt5.QtGui import QPixmap, QImage
except ImportError as e:
    print(f"Error importing PyQt5: {e}")
    print("Please install PyQt5: pip install PyQt5")
    sys.exit(1)

# Import enhanced UI components
try:
    from apps.PlayaTewsIdentityMasker.ui.QEnhancedMainUI import QEnhancedMainUI
    from apps.PlayaTewsIdentityMasker.ui.QOptimizedVideoDisplay import QOptimizedVideoDisplay
    from apps.PlayaTewsIdentityMasker.ui.QModernControlPanel import QModernControlPanel
except ImportError as e:
    print(f"Error importing enhanced UI components: {e}")
    print("Please ensure all UI files are in the correct locations")
    sys.exit(1)


class MockStreamOutput:
    """Mock stream output for testing video display"""
    def __init__(self):
        self.frame_ready = None
        self.is_streaming = False
        self.is_recording = False
        
    def get_test_frame(self, frame_number=0):
        """Generate a test video frame with animated content"""
        # Create a test image (640x480 with animated pattern)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Animated elements
        time_offset = frame_number * 0.1
        
        # Moving rectangle
        x_pos = int(100 + 50 * np.sin(time_offset))
        y_pos = int(200 + 30 * np.cos(time_offset))
        frame[y_pos:y_pos+100, x_pos:x_pos+200] = [255, 0, 0]  # Red rectangle
        
        # Color-changing circle
        circle_x = int(400 + 100 * np.sin(time_offset * 2))
        circle_y = int(300 + 50 * np.cos(time_offset * 2))
        color = [
            int(128 + 127 * np.sin(time_offset)),
            int(128 + 127 * np.cos(time_offset)),
            int(128 + 127 * np.sin(time_offset * 1.5))
        ]
        
        # Draw simple circle
        for i in range(max(0, circle_y-50), min(480, circle_y+50)):
            for j in range(max(0, circle_x-50), min(640, circle_x+50)):
                if (i-circle_y)**2 + (j-circle_x)**2 < 2500:  # radius 50
                    frame[i, j] = color
        
        # Animated text pattern
        for i in range(0, 480, 60):
            line_pos = int(i + 20 * np.sin(time_offset + i * 0.01))
            if 0 <= line_pos < 480:
                frame[line_pos:line_pos+5, :] = [128, 128, 128]
        
        # Add frame counter
        frame[10:30, 10:150] = [0, 0, 0]
        # Simple text rendering (simplified)
        for i in range(10):
            frame[15+i, 15:15+len(f"Frame: {frame_number}")*8] = [255, 255, 255]
        
        return frame
    
    def start_streaming(self):
        """Start mock streaming"""
        self.is_streaming = True
        print("Mock streaming started")
    
    def stop_streaming(self):
        """Stop mock streaming"""
        self.is_streaming = False
        print("Mock streaming stopped")
    
    def start_recording(self):
        """Start mock recording"""
        self.is_recording = True
        print("Mock recording started")
    
    def stop_recording(self):
        """Stop mock recording"""
        self.is_recording = False
        print("Mock recording stopped")


class MockComponent:
    """Mock component for testing"""
    def __init__(self, name):
        self.name = name
        self.enabled = False
        self.status = "Ready"
    
    def get_status(self):
        return f"{self.name}: {'Enabled' if self.enabled else 'Disabled'}"
    
    def enable(self):
        self.enabled = True
        self.status = "Running"
    
    def disable(self):
        self.enabled = False
        self.status = "Stopped"


class PerformanceSimulator(QThread):
    """Simulate performance metrics"""
    metrics_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def run(self):
        """Simulate performance metrics"""
        while self.running:
            metrics = {
                'fps': random.randint(25, 35),
                'memory_gb': random.uniform(1.5, 3.0),
                'cpu_percent': random.randint(30, 70),
                'gpu_percent': random.randint(20, 80),
                'latency_ms': random.randint(10, 50)
            }
            self.metrics_updated.emit(metrics)
            time.sleep(1)
    
    def stop(self):
        self.running = False


class IntegrationTest:
    """Main integration test class"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("PlayaTews Enhanced UI Test")
        self.app.setApplicationVersion("2.0")
        
        # Create test data paths
        self.userdata_path = Path('./test_userdata')
        self.userdata_path.mkdir(exist_ok=True)
        
        # Create mock components
        self.setup_mock_components()
        
        # Create enhanced UI
        self.setup_enhanced_ui()
        
        # Setup test timers
        self.setup_test_timers()
        
        # Setup performance simulator
        self.setup_performance_simulator()
        
        # Frame counter for animation
        self.frame_counter = 0
        
    def setup_mock_components(self):
        """Setup mock backend components"""
        self.mock_stream_output = MockStreamOutput()
        
        self.mock_face_swap_components = {
            'face_detector': MockComponent('Face Detector'),
            'face_aligner': MockComponent('Face Aligner'),
            'face_swapper': MockComponent('Face Swapper'),
            'face_merger': MockComponent('Face Merger')
        }
        
        self.mock_viewers_components = {
            'input_viewer': MockComponent('Input Viewer'),
            'output_viewer': MockComponent('Output Viewer'),
            'merged_viewer': MockComponent('Merged Viewer')
        }
        
        self.mock_voice_changer = MockComponent('Voice Changer')
        
    def setup_enhanced_ui(self):
        """Setup the enhanced UI"""
        try:
            self.main_window = QEnhancedMainUI(
                stream_output_backend=self.mock_stream_output,
                userdata_path=self.userdata_path,
                face_swap_components=self.mock_face_swap_components,
                viewers_components=self.mock_viewers_components,
                voice_changer_backend=self.mock_voice_changer
            )
            
            # Connect UI signals to mock components
            self.connect_ui_signals()
            
            print("Enhanced UI created successfully")
            
        except Exception as e:
            print(f"Error creating enhanced UI: {e}")
            raise
    
    def connect_ui_signals(self):
        """Connect UI signals to mock components"""
        try:
            # Connect streaming controls
            if hasattr(self.main_window.left_panel, 'stream_btn'):
                self.main_window.left_panel.stream_btn.clicked.connect(self.on_stream_toggle)
            
            if hasattr(self.main_window.left_panel, 'record_btn'):
                self.main_window.left_panel.record_btn.clicked.connect(self.on_record_toggle)
            
            if hasattr(self.main_window.left_panel, 'face_swap_btn'):
                self.main_window.left_panel.face_swap_btn.toggled.connect(self.on_face_swap_toggle)
            
            print("UI signals connected successfully")
            
        except Exception as e:
            print(f"Error connecting UI signals: {e}")
    
    def setup_test_timers(self):
        """Setup timers for testing"""
        # Video frame update timer (30 FPS)
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_video_frame)
        self.video_timer.start(33)  # ~30 FPS
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)  # Every 2 seconds
        
    def setup_performance_simulator(self):
        """Setup performance metrics simulator"""
        self.performance_simulator = PerformanceSimulator()
        self.performance_simulator.metrics_updated.connect(self.update_performance_metrics)
        self.performance_simulator.start()
    
    def update_video_frame(self):
        """Update video frame for testing"""
        try:
            frame = self.mock_stream_output.get_test_frame(self.frame_counter)
            self.main_window.update_video_frame(frame)
            self.frame_counter += 1
            
        except Exception as e:
            print(f"Error updating video frame: {e}")
    
    def update_status(self):
        """Update status messages"""
        status_messages = [
            "System ready",
            "Video processing active",
            "Face detection running",
            "Streaming optimized",
            "Performance monitoring active"
        ]
        
        message = random.choice(status_messages)
        self.main_window.show_status_message(message)
    
    def update_performance_metrics(self, metrics):
        """Update performance metrics display"""
        try:
            # Update performance indicators in the UI
            if hasattr(self.main_window, 'fps_indicator'):
                self.main_window.fps_indicator.setText(f"FPS: {metrics['fps']}")
            
            if hasattr(self.main_window, 'memory_indicator'):
                self.main_window.memory_indicator.setText(f"Memory: {metrics['memory_gb']:.1f} GB")
            
            if hasattr(self.main_window, 'cpu_indicator'):
                self.main_window.cpu_indicator.setText(f"CPU: {metrics['cpu_percent']}%")
            
            # Update video display metrics
            if hasattr(self.main_window, 'video_display'):
                self.main_window.video_display.update_performance_metrics(
                    metrics['fps'], 
                    "HD"
                )
                
        except Exception as e:
            print(f"Error updating performance metrics: {e}")
    
    def on_stream_toggle(self):
        """Handle streaming toggle"""
        if self.mock_stream_output.is_streaming:
            self.mock_stream_output.stop_streaming()
        else:
            self.mock_stream_output.start_streaming()
    
    def on_record_toggle(self):
        """Handle recording toggle"""
        if self.mock_stream_output.is_recording:
            self.mock_stream_output.stop_recording()
        else:
            self.mock_stream_output.start_recording()
    
    def on_face_swap_toggle(self, enabled):
        """Handle face swap toggle"""
        for component in self.mock_face_swap_components.values():
            if enabled:
                component.enable()
            else:
                component.disable()
    
    def show_test_instructions(self):
        """Show test instructions to user"""
        instructions = """
        🎯 Enhanced UI Integration Test
        
        ✅ Features to test:
        
        1. 📹 Video Display:
           - Video feed occupies 80%+ of center panel
           - Stretch-fit mode is default
           - Try different fit modes (Stretch, Fit, Fill, Original)
           - Test fullscreen toggle (F11)
        
        2. 📱 Responsive Layout:
           - Resize window to test responsive behavior
           - Panels adjust automatically
           - Minimum/maximum sizes respected
        
        3. ⌨️ Accessibility:
           - Keyboard shortcuts: F11, Ctrl+S, Ctrl+R, Ctrl+F
           - Tab navigation works
           - Color contrast and readability
        
        4. 🎨 Modern Controls:
           - Collapsible settings panels
           - Hover effects on buttons
           - Performance indicators update
        
        5. 🎮 Interactive Features:
           - Click buttons to test functionality
           - Watch animated test video
           - Monitor performance metrics
        
        Press OK to start testing!
        """
        
        msg = QMessageBox()
        msg.setWindowTitle("Enhanced UI Test Instructions")
        msg.setText(instructions)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def run_test(self):
        """Run the integration test"""
        try:
            # Show instructions
            self.show_test_instructions()
            
            # Show the main window
            self.main_window.show()
            
            print("🎉 Enhanced UI Integration Test Started!")
            print("📋 Test Features:")
            print("   - Video display with stretch-fit")
            print("   - Fullscreen toggle (F11)")
            print("   - Responsive layout (resize window)")
            print("   - Keyboard shortcuts (Ctrl+S, Ctrl+R, Ctrl+F)")
            print("   - Collapsible settings panels")
            print("   - Performance indicators")
            print("   - Animated test video")
            print("   - Mock backend integration")
            
            # Run the application
            return self.app.exec_()
            
        except Exception as e:
            print(f"❌ Error running test: {e}")
            return 1
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'performance_simulator'):
                self.performance_simulator.stop()
                self.performance_simulator.wait()
            
            if hasattr(self, 'video_timer'):
                self.video_timer.stop()
            
            if hasattr(self, 'status_timer'):
                self.status_timer.stop()
                
            print("🧹 Test cleanup completed")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")


def main():
    """Main function"""
    print("🚀 Starting PlayaTews Enhanced UI Integration Test")
    print("=" * 60)
    
    # Check dependencies
    try:
        import cv2
        print("✅ OpenCV available")
    except ImportError:
        print("⚠️ OpenCV not available - some features may not work")
    
    try:
        import numpy as np
        print("✅ NumPy available")
    except ImportError:
        print("❌ NumPy required but not available")
        return 1
    
    # Run the test
    test = IntegrationTest()
    
    try:
        result = test.run_test()
    finally:
        test.cleanup()
    
    print("=" * 60)
    print("🏁 Enhanced UI Integration Test completed")
    
    return result


if __name__ == '__main__':
    sys.exit(main()) 