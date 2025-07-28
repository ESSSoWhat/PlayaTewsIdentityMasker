#!/usr/bin/env python3
"""
Live Face Detection Application
Simplified version that works with real camera but bypasses CSW system issues
"""
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QPushButton, QLabel, 
                             QComboBox, QSlider, QSpinBox, QCheckBox, QGroupBox,
                             QFileDialog, QMessageBox, QProgressBar)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont

class CameraThread(QThread):
    """Thread for camera capture to prevent UI freezing"""
    frame_ready = pyqtSignal(np.ndarray)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.cap = None
        
    def run(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                self.error_occurred.emit(f"Failed to open camera {self.camera_index}")
                return
                
            self.running = True
            while self.running:
                ret, frame = self.cap.read()
                if ret:
                    self.frame_ready.emit(frame)
                else:
                    break
                    
        except Exception as e:
            self.error_occurred.emit(f"Camera error: {str(e)}")
        finally:
            if self.cap:
                self.cap.release()
    
    def stop(self):
        self.running = False
        self.wait()

class LiveFaceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Face Detection Application")
        self.setGeometry(100, 100, 1200, 800)
        
        # Camera and detection variables
        self.camera_thread = None
        self.current_frame = None
        self.face_cascade = None
        self.eye_cascade = None
        self.detection_enabled = True
        self.show_rectangles = True
        self.show_landmarks = False
        self.detection_sensitivity = 5
        self.min_face_size = 30
        
        # Statistics
        self.faces_detected = 0
        self.fps_counter = 0
        self.fps = 0
        
        self.setup_ui()
        self.setup_face_detection()
        self.setup_camera_list()
        
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Camera view
        camera_panel = QWidget()
        camera_layout = QVBoxLayout(camera_panel)
        
        # Camera display
        self.camera_label = QLabel("Camera Feed")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("border: 2px solid gray; background-color: black;")
        camera_layout.addWidget(self.camera_label)
        
        # Camera controls
        camera_controls = QGroupBox("Camera Controls")
        camera_controls_layout = QVBoxLayout(camera_controls)
        
        # Camera selection
        camera_select_layout = QHBoxLayout()
        camera_select_layout.addWidget(QLabel("Camera:"))
        self.camera_combo = QComboBox()
        self.camera_combo.currentIndexChanged.connect(self.on_camera_changed)
        camera_select_layout.addWidget(self.camera_combo)
        
        # Camera buttons
        camera_buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setEnabled(False)
        
        camera_buttons_layout.addWidget(self.start_button)
        camera_buttons_layout.addWidget(self.stop_button)
        
        camera_controls_layout.addLayout(camera_select_layout)
        camera_controls_layout.addLayout(camera_buttons_layout)
        camera_layout.addWidget(camera_controls)
        
        # Status
        self.status_label = QLabel("Ready to start camera")
        self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        camera_layout.addWidget(self.status_label)
        
        main_layout.addWidget(camera_panel)
        
        # Right panel - Controls
        controls_panel = QWidget()
        controls_layout = QVBoxLayout(controls_panel)
        
        # Detection settings
        detection_group = QGroupBox("Face Detection Settings")
        detection_layout = QVBoxLayout(detection_group)
        
        # Detection sensitivity
        sensitivity_layout = QHBoxLayout()
        sensitivity_layout.addWidget(QLabel("Detection Sensitivity:"))
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(5)
        self.sensitivity_slider.valueChanged.connect(self.on_sensitivity_changed)
        sensitivity_layout.addWidget(self.sensitivity_slider)
        self.sensitivity_label = QLabel("5")
        sensitivity_layout.addWidget(self.sensitivity_label)
        detection_layout.addLayout(sensitivity_layout)
        
        # Minimum face size
        face_size_layout = QHBoxLayout()
        face_size_layout.addWidget(QLabel("Min Face Size:"))
        self.face_size_spin = QSpinBox()
        self.face_size_spin.setRange(10, 200)
        self.face_size_spin.setValue(30)
        self.face_size_spin.valueChanged.connect(self.on_face_size_changed)
        face_size_layout.addWidget(self.face_size_spin)
        detection_layout.addLayout(face_size_layout)
        
        # Detection options
        self.detection_checkbox = QCheckBox("Enable Face Detection")
        self.detection_checkbox.setChecked(True)
        self.detection_checkbox.toggled.connect(self.on_detection_toggled)
        detection_layout.addWidget(self.detection_checkbox)
        
        self.rectangles_checkbox = QCheckBox("Show Face Rectangles")
        self.rectangles_checkbox.setChecked(True)
        self.rectangles_checkbox.toggled.connect(self.on_rectangles_toggled)
        detection_layout.addWidget(self.rectangles_checkbox)
        
        self.landmarks_checkbox = QCheckBox("Show Eye Landmarks")
        self.landmarks_checkbox.setChecked(False)
        self.landmarks_checkbox.toggled.connect(self.on_landmarks_toggled)
        detection_layout.addWidget(self.landmarks_checkbox)
        
        controls_layout.addWidget(detection_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.fps_label = QLabel("FPS: 0")
        self.faces_label = QLabel("Faces Detected: 0")
        self.resolution_label = QLabel("Resolution: --")
        
        stats_layout.addWidget(self.fps_label)
        stats_layout.addWidget(self.faces_label)
        stats_layout.addWidget(self.resolution_label)
        
        controls_layout.addWidget(stats_group)
        
        # Image controls
        image_group = QGroupBox("Image Controls")
        image_layout = QVBoxLayout(image_group)
        
        self.save_button = QPushButton("Save Current Frame")
        self.save_button.clicked.connect(self.save_frame)
        self.save_button.setEnabled(False)
        image_layout.addWidget(self.save_button)
        
        self.load_button = QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)
        image_layout.addWidget(self.load_button)
        
        controls_layout.addWidget(image_group)
        
        # FPS timer
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self.update_fps)
        self.fps_timer.start(1000)  # Update every second
        
        main_layout.addWidget(controls_panel)
        
    def setup_face_detection(self):
        """Setup face detection cascades"""
        try:
            # Load OpenCV face detection cascades
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            
            if self.face_cascade.empty():
                raise Exception("Failed to load face cascade")
            if self.eye_cascade.empty():
                raise Exception("Failed to load eye cascade")
                
            self.status_label.setText("Face detection ready (OpenCV)")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            
        except Exception as e:
            self.status_label.setText(f"Face detection error: {str(e)}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def setup_camera_list(self):
        """Populate camera list"""
        self.camera_combo.clear()
        
        # Test cameras 0-9
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.camera_combo.addItem(f"Camera {i}")
                cap.release()
            else:
                cap.release()
        
        if self.camera_combo.count() == 0:
            self.camera_combo.addItem("No cameras found")
            self.start_button.setEnabled(False)
    
    def start_camera(self):
        """Start camera capture"""
        if self.camera_thread and self.camera_thread.isRunning():
            return
            
        camera_index = self.camera_combo.currentIndex()
        if camera_index < 0:
            QMessageBox.warning(self, "Error", "No camera selected")
            return
            
        self.camera_thread = CameraThread(camera_index)
        self.camera_thread.frame_ready.connect(self.process_frame)
        self.camera_thread.error_occurred.connect(self.on_camera_error)
        self.camera_thread.start()
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.status_label.setText("Camera started")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
    
    def stop_camera(self):
        """Stop camera capture"""
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None
            
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.status_label.setText("Camera stopped")
        self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        
        # Clear display
        self.camera_label.setText("Camera Feed")
        self.camera_label.setStyleSheet("border: 2px solid gray; background-color: black;")
    
    def process_frame(self, frame):
        """Process camera frame with face detection"""
        self.current_frame = frame.copy()
        self.fps_counter += 1
        
        if self.detection_enabled and self.face_cascade is not None:
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            scale_factor = 1.0 + (self.detection_sensitivity - 5) * 0.1
            min_neighbors = max(1, 6 - self.detection_sensitivity)
            
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=scale_factor, 
                minNeighbors=min_neighbors,
                minSize=(self.min_face_size, self.min_face_size)
            )
            
            self.faces_detected = len(faces)
            
            # Draw face rectangles
            if self.show_rectangles:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Detect eyes within face region
                    if self.show_landmarks and self.eye_cascade is not None:
                        roi_gray = gray[y:y+h, x:x+w]
                        eyes = self.eye_cascade.detectMultiScale(roi_gray)
                        for (ex, ey, ew, eh) in eyes:
                            cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (255, 0, 0), 1)
        
        # Convert frame to Qt format
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        
        # Scale to fit display
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.camera_label.setPixmap(scaled_pixmap)
        
        # Update resolution
        self.resolution_label.setText(f"Resolution: {width}x{height}")
    
    def on_camera_error(self, error_msg):
        """Handle camera errors"""
        self.status_label.setText(f"Camera error: {error_msg}")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.stop_camera()
    
    def on_camera_changed(self, index):
        """Handle camera selection change"""
        if self.camera_thread and self.camera_thread.isRunning():
            self.stop_camera()
    
    def on_sensitivity_changed(self, value):
        """Handle detection sensitivity change"""
        self.detection_sensitivity = value
        self.sensitivity_label.setText(str(value))
    
    def on_face_size_changed(self, value):
        """Handle minimum face size change"""
        self.min_face_size = value
    
    def on_detection_toggled(self, checked):
        """Handle detection enable/disable"""
        self.detection_enabled = checked
    
    def on_rectangles_toggled(self, checked):
        """Handle rectangle display toggle"""
        self.show_rectangles = checked
    
    def on_landmarks_toggled(self, checked):
        """Handle landmarks display toggle"""
        self.show_landmarks = checked
    
    def update_fps(self):
        """Update FPS display"""
        self.fps = self.fps_counter
        self.fps_counter = 0
        self.fps_label.setText(f"FPS: {self.fps}")
        self.faces_label.setText(f"Faces Detected: {self.faces_detected}")
    
    def save_frame(self):
        """Save current frame"""
        if self.current_frame is None:
            QMessageBox.warning(self, "Error", "No frame to save")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Frame", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if filename:
            try:
                cv2.imwrite(filename, self.current_frame)
                QMessageBox.information(self, "Success", f"Frame saved to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save frame: {str(e)}")
    
    def load_image(self):
        """Load image from file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if filename:
            try:
                frame = cv2.imread(filename)
                if frame is not None:
                    self.process_frame(frame)
                    self.status_label.setText(f"Image loaded: {filename}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to load image")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def closeEvent(self, event):
        """Handle application close"""
        self.stop_camera()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Live Face Detection")
    
    window = LiveFaceApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 