#!/usr/bin/env python3
"""
Demo Face Application
Works without camera and provides face detection demo
"""

import sys
import time
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QWidget, QGroupBox, QCheckBox,
                            QComboBox, QSpinBox, QSlider, QTabWidget, QTextEdit,
                            QMessageBox, QProgressBar, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QImage
import cv2
import numpy as np

class DemoFaceApp(QMainWindow):
    """Demo face application with sample images and face detection"""
    
    def __init__(self):
        super().__init__()
        self.userdata_path = Path("demo_settings")
        self.userdata_path.mkdir(exist_ok=True)
        
        # Demo state
        self.current_image = None
        self.is_processing = False
        self.face_cascade = None
        
        # UI components
        self.image_label = None
        self.status_label = None
        self.progress_bar = None
        
        self.setup_ui()
        self.setup_face_detection()
        self.setup_connections()
        self.load_demo_image()
        
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("Demo Face Detection Application")
        self.setGeometry(100, 100, 1000, 700)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Demo Face Detection Application")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Image tab
        image_tab = self.create_image_tab()
        tab_widget.addTab(image_tab, "Image Processing")
        
        # Face Detection tab
        detection_tab = self.create_detection_tab()
        tab_widget.addTab(detection_tab, "Face Detection")
        
        # Demo tab
        demo_tab = self.create_demo_tab()
        tab_widget.addTab(demo_tab, "Demo")
        
        # Control panel
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status bar
        self.status_label = QLabel("Ready - Demo Mode")
        self.status_label.setStyleSheet("QLabel { background-color: #e0e0e0; padding: 5px; }")
        layout.addWidget(self.status_label)
        
        main_widget.setLayout(layout)
    
    def create_image_tab(self):
        """Create image processing tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Image display
        image_group = QGroupBox("Image Display")
        image_layout = QVBoxLayout()
        
        self.image_label = QLabel("No image loaded")
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setStyleSheet("QLabel { border: 2px solid #ccc; background-color: #f0f0f0; }")
        self.image_label.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(self.image_label)
        
        # Image controls
        image_controls = QHBoxLayout()
        
        load_image_btn = QPushButton("Load Image")
        load_image_btn.clicked.connect(self.load_image)
        image_controls.addWidget(load_image_btn)
        
        load_demo_btn = QPushButton("Load Demo Image")
        load_demo_btn.clicked.connect(self.load_demo_image)
        image_controls.addWidget(load_demo_btn)
        
        save_image_btn = QPushButton("Save Processed Image")
        save_image_btn.clicked.connect(self.save_image)
        image_controls.addWidget(save_image_btn)
        
        image_layout.addLayout(image_controls)
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_detection_tab(self):
        """Create face detection configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Face detection settings
        detection_group = QGroupBox("Face Detection Settings")
        detection_layout = QVBoxLayout()
        
        self.detection_threshold = QSlider(Qt.Horizontal)
        self.detection_threshold.setRange(1, 10)
        self.detection_threshold.setValue(3)
        detection_layout.addWidget(QLabel("Detection Sensitivity (1-10):"))
        detection_layout.addWidget(self.detection_threshold)
        
        self.min_face_size = QSpinBox()
        self.min_face_size.setRange(20, 200)
        self.min_face_size.setValue(30)
        detection_layout.addWidget(QLabel("Minimum Face Size:"))
        detection_layout.addWidget(self.min_face_size)
        
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)
        
        # Processing options
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout()
        
        self.draw_faces_cb = QCheckBox("Draw Face Rectangles")
        self.draw_faces_cb.setChecked(True)
        options_layout.addWidget(self.draw_faces_cb)
        
        self.draw_landmarks_cb = QCheckBox("Draw Face Landmarks")
        self.draw_landmarks_cb.setChecked(False)
        options_layout.addWidget(self.draw_landmarks_cb)
        
        self.show_stats_cb = QCheckBox("Show Detection Statistics")
        self.show_stats_cb.setChecked(True)
        options_layout.addWidget(self.show_stats_cb)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_demo_tab(self):
        """Create demo tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Demo information
        info_group = QGroupBox("Demo Information")
        info_layout = QVBoxLayout()
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(200)
        info_text.setText("""
🎯 Demo Face Detection Application

This application demonstrates face detection functionality without requiring a camera.

✅ Features:
• Load and process images
• Face detection using OpenCV
• Configurable detection parameters
• Real-time processing options
• Save processed images

🔧 How to use:
1. Load an image (or use demo image)
2. Adjust detection settings
3. Click "Start Face Detection"
4. View detected faces with green rectangles
5. Save the processed image

📁 Sample images with faces work best for testing.
        """)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Demo controls
        demo_controls = QHBoxLayout()
        
        process_demo_btn = QPushButton("Process Demo Image")
        process_demo_btn.clicked.connect(self.process_demo_image)
        demo_controls.addWidget(process_demo_btn)
        
        reset_demo_btn = QPushButton("Reset Demo")
        reset_demo_btn.clicked.connect(self.reset_demo)
        demo_controls.addWidget(reset_demo_btn)
        
        layout.addLayout(demo_controls)
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_control_panel(self):
        """Create main control panel"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Start/Stop processing
        self.start_processing_btn = QPushButton("Start Face Detection")
        self.start_processing_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.start_processing_btn)
        
        self.stop_processing_btn = QPushButton("Stop Face Detection")
        self.stop_processing_btn.clicked.connect(self.stop_processing)
        self.stop_processing_btn.setEnabled(False)
        layout.addWidget(self.stop_processing_btn)
        
        # Global controls
        self.global_enable_cb = QCheckBox("Enable Face Detection")
        self.global_enable_cb.stateChanged.connect(self.on_global_enable_changed)
        layout.addWidget(self.global_enable_cb)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def setup_face_detection(self):
        """Setup OpenCV face detection"""
        try:
            # Load OpenCV face cascade
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            if self.face_cascade.empty():
                self.status_label.setText("Warning: Face detection model not loaded")
            else:
                self.status_label.setText("Face detection ready (OpenCV)")
        except Exception as e:
            self.status_label.setText(f"Face detection setup failed: {e}")
    
    def setup_connections(self):
        """Setup signal connections"""
        pass
    
    def load_demo_image(self):
        """Load a demo image"""
        try:
            # Create a simple demo image with a face-like pattern
            demo_image = np.ones((480, 640, 3), dtype=np.uint8) * 200
            
            # Draw a simple face-like pattern
            # Head circle
            cv2.circle(demo_image, (320, 240), 100, (150, 150, 150), -1)
            # Eyes
            cv2.circle(demo_image, (290, 220), 15, (255, 255, 255), -1)
            cv2.circle(demo_image, (350, 220), 15, (255, 255, 255), -1)
            cv2.circle(demo_image, (290, 220), 8, (0, 0, 0), -1)
            cv2.circle(demo_image, (350, 220), 8, (0, 0, 0), -1)
            # Nose
            cv2.ellipse(demo_image, (320, 250), (10, 15), 0, 0, 180, (100, 100, 100), 2)
            # Mouth
            cv2.ellipse(demo_image, (320, 280), (30, 10), 0, 0, 180, (100, 100, 100), 2)
            
            self.current_image = demo_image
            self.show_image(demo_image)
            self.status_label.setText("Demo image loaded")
            
        except Exception as e:
            self.status_label.setText(f"Demo image load failed: {e}")
    
    def load_image(self):
        """Load image from file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
            )
            
            if file_path:
                image = cv2.imread(file_path)
                if image is not None:
                    self.current_image = image
                    self.show_image(image)
                    self.status_label.setText(f"Image loaded: {Path(file_path).name}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to load image")
                    
        except Exception as e:
            self.status_label.setText(f"Image load failed: {e}")
            QMessageBox.critical(self, "Error", f"Image load failed: {e}")
    
    def save_image(self):
        """Save processed image"""
        try:
            if self.current_image is None:
                QMessageBox.warning(self, "Save", "No image to save")
                return
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Image", "processed_image.png", "Image Files (*.png *.jpg *.jpeg *.bmp)"
            )
            
            if file_path:
                cv2.imwrite(file_path, self.current_image)
                self.status_label.setText(f"Image saved: {Path(file_path).name}")
                QMessageBox.information(self, "Success", "Image saved successfully")
                
        except Exception as e:
            self.status_label.setText(f"Image save failed: {e}")
            QMessageBox.critical(self, "Error", f"Image save failed: {e}")
    
    def show_image(self, image):
        """Display image in preview"""
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize for display
            height, width, channel = rgb_image.shape
            bytes_per_line = 3 * width
            q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # Scale to fit preview
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio)
            self.image_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            print(f"Image display error: {e}")
    
    def process_demo_image(self):
        """Process the demo image with face detection"""
        if self.current_image is None:
            QMessageBox.warning(self, "Processing", "No image to process")
            return
        
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.status_label.setText("Processing demo image...")
            
            # Process the image
            processed_image = self.process_image(self.current_image.copy())
            
            # Show the processed image
            self.current_image = processed_image
            self.show_image(processed_image)
            
            self.progress_bar.setVisible(False)
            self.status_label.setText("Demo image processed")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"Processing failed: {e}")
            QMessageBox.critical(self, "Error", f"Processing failed: {e}")
    
    def reset_demo(self):
        """Reset the demo"""
        self.load_demo_image()
        self.status_label.setText("Demo reset")
    
    def process_image(self, image):
        """Process image with face detection"""
        try:
            if self.face_cascade is None:
                return image
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=self.detection_threshold.value(),
                minSize=(self.min_face_size.value(), self.min_face_size.value())
            )
            
            # Draw face rectangles if enabled
            if self.draw_faces_cb.isChecked():
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(image, f'Face', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Show detection statistics if enabled
            if self.show_stats_cb.isChecked():
                stats_text = f"Faces detected: {len(faces)}"
                cv2.putText(image, stats_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            return image
            
        except Exception as e:
            print(f"Image processing error: {e}")
            return image
    
    def start_processing(self):
        """Start face processing"""
        if not self.is_processing:
            self.is_processing = True
            self.start_processing_btn.setEnabled(False)
            self.stop_processing_btn.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.status_label.setText("Face processing started")
            
            # Process current image
            if self.current_image is not None:
                processed_image = self.process_image(self.current_image.copy())
                self.current_image = processed_image
                self.show_image(processed_image)
    
    def stop_processing(self):
        """Stop face processing"""
        self.is_processing = False
        self.start_processing_btn.setEnabled(True)
        self.stop_processing_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Face processing stopped")
    
    def on_global_enable_changed(self, state):
        """Handle global enable checkbox"""
        enabled = state == Qt.Checked
        if enabled:
            self.status_label.setText("Face detection enabled")
        else:
            self.status_label.setText("Face detection disabled")

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = DemoFaceApp()
    window.show()
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 