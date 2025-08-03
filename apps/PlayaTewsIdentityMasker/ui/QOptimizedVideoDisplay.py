#!/usr/bin/env python3
"""
Optimized Video Display Component
Maximizes space allocation for merged video feed with stretch-fit and modern UI
"""

import cv2  # Added missing import for cv2
import numpy as np
from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QImage, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStyleFactory,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class QOptimizedVideoDisplay(QWidget):
    """Optimized video display with 80%+ space allocation and stretch-fit capabilities"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_fullscreen = False
        self.original_geometry = None
        self.fit_mode = "Stretch"  # Stretch, Fit, Fill, Original
        self.controls_visible = False

        self.setup_ui()
        self.setup_styles()
        self.setup_animations()

    def setup_ui(self):
        """Setup the optimized video display UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main video display area (80%+ of available space)
        self.video_container = QWidget()
        self.video_container.setObjectName("video-container")
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Video label with stretch-fit
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("Video Feed\n\nClick to enter fullscreen mode")
        self.video_label.setObjectName("video-display")
        self.video_label.setCursor(Qt.PointingHandCursor)

        # Floating control panel (appears on hover)
        self.control_panel = self.create_control_panel()
        self.control_panel.setVisible(False)

        # Add to container
        container_layout.addWidget(self.video_label)
        container_layout.addWidget(self.control_panel)

        self.video_container.setLayout(container_layout)
        layout.addWidget(self.video_container, 1)  # Takes all available space

        self.setLayout(layout)

        # Setup event handling
        self.video_container.enterEvent = self.on_container_enter
        self.video_container.leaveEvent = self.on_container_leave
        self.video_label.mousePressEvent = self.on_video_click

    def create_control_panel(self):
        """Create floating control panel"""
        panel = QWidget()
        panel.setObjectName("control-panel")
        panel.setMaximumHeight(60)

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # Fullscreen button
        self.fullscreen_btn = QToolButton()
        try:
            self.fullscreen_btn.setIcon(
                self.style().standardIcon(QStyleFactory.SP_TitleBarMaxButton)
            )
        except:
            # Fallback for older PyQt5 versions
            self.fullscreen_btn.setText("⛶")
        self.fullscreen_btn.setToolTip("Toggle Fullscreen (F11)")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        self.fullscreen_btn.setObjectName("fullscreen-btn")

        # Fit mode selector
        self.fit_combo = QComboBox()
        self.fit_combo.addItems(["Stretch", "Fit", "Fill", "Original"])
        self.fit_combo.setCurrentText("Stretch")
        self.fit_combo.currentTextChanged.connect(self.on_fit_mode_changed)
        self.fit_combo.setObjectName("fit-mode-combo")
        self.fit_combo.setToolTip("Video fit mode")

        # Quality indicator
        self.quality_label = QLabel("HD")
        self.quality_label.setObjectName("quality-label")

        # FPS indicator
        self.fps_label = QLabel("30 FPS")
        self.fps_label.setObjectName("fps-label")

        layout.addWidget(self.fullscreen_btn)
        layout.addWidget(QLabel("Fit:"))
        layout.addWidget(self.fit_combo)
        layout.addStretch()
        layout.addWidget(self.quality_label)
        layout.addWidget(self.fps_label)

        panel.setLayout(layout)
        return panel

    def setup_styles(self):
        """Setup modern video display styles"""
        self.setStyleSheet(
            """
            QWidget#video-container {
                background-color: #0a0a0a;
                border: none;
            }
            
            QLabel#video-display {
                background-color: #1a1a1a;
                border: 2px solid #404040;
                border-radius: 8px;
                color: #ffffff;
                font-size: 16px;
                font-weight: 500;
                padding: 20px;
            }
            
            QLabel#video-display:hover {
                border-color: #606060;
            }
            
            QWidget#control-panel {
                background-color: rgba(0, 0, 0, 0.8);
                border-radius: 8px;
                margin: 8px;
            }
            
            QToolButton#fullscreen-btn {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                padding: 8px;
                color: white;
                min-width: 32px;
                min-height: 32px;
            }
            
            QToolButton#fullscreen-btn:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            QComboBox#fit-mode-combo {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                padding: 6px 12px;
                color: white;
                min-width: 80px;
                font-size: 12px;
            }
            
            QComboBox#fit-mode-combo::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox#fit-mode-combo::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid white;
            }
            
            QLabel#quality-label, QLabel#fps-label {
                color: #00ff00;
                font-weight: 600;
                font-size: 12px;
                padding: 4px 8px;
                background-color: rgba(0, 255, 0, 0.1);
                border-radius: 4px;
            }
        """
        )

    def setup_animations(self):
        """Setup smooth animations for controls"""
        self.fade_animation = QPropertyAnimation(self.control_panel, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

    def on_container_enter(self, event):
        """Show controls on hover"""
        if not self.is_fullscreen:
            self.show_controls()

    def on_container_leave(self, event):
        """Hide controls when not hovering"""
        if not self.is_fullscreen:
            self.hide_controls()

    def on_video_click(self, event):
        """Handle video click for fullscreen"""
        if event.button() == Qt.LeftButton:
            self.toggle_fullscreen()

    def show_controls(self):
        """Show control panel with animation"""
        if not self.controls_visible:
            self.controls_visible = True
            self.fade_animation.setStartValue(0.0)
            self.fade_animation.setEndValue(1.0)
            self.control_panel.setVisible(True)
            self.fade_animation.start()

    def hide_controls(self):
        """Hide control panel with animation"""
        if self.controls_visible:
            self.controls_visible = False
            self.fade_animation.setStartValue(1.0)
            self.fade_animation.setEndValue(0.0)
            self.fade_animation.finished.connect(
                lambda: self.control_panel.setVisible(False)
            )
            self.fade_animation.start()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if not self.is_fullscreen:
            self.enter_fullscreen()
        else:
            self.exit_fullscreen()

    def enter_fullscreen(self):
        """Enter fullscreen mode"""
        self.original_geometry = self.geometry()
        self.is_fullscreen = True
        self.showFullScreen()
        self.show_controls()  # Keep controls visible in fullscreen

    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        self.is_fullscreen = False
        self.showNormal()
        if self.original_geometry:
            self.setGeometry(self.original_geometry)
        self.hide_controls()

    def on_fit_mode_changed(self, mode):
        """Handle fit mode changes"""
        self.fit_mode = mode
        # Re-apply current frame with new fit mode
        if hasattr(self, "_current_frame"):
            self.update_video_frame(self._current_frame)

    def update_video_frame(self, frame):
        """Update the video display with a new frame"""
        if frame is not None:
            self._current_frame = frame

            # Convert numpy array to QImage
            if frame.dtype != np.uint8:
                frame = (frame * 255).astype(np.uint8)

            height, width, channel = frame.shape
            bytes_per_line = 3 * width

            # Convert BGR to RGB if needed
            if channel == 3:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                frame_rgb = frame

            q_image = QImage(
                frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888
            )
            q_pixmap = QPixmap.fromImage(q_image)

            # Apply fit mode
            scaled_pixmap = self.apply_fit_mode(q_pixmap, self.video_label.size())
            self.video_label.setPixmap(scaled_pixmap)

    def apply_fit_mode(self, pixmap, target_size):
        """Apply the selected fit mode to the pixmap"""
        if self.fit_mode == "Stretch":
            return pixmap.scaled(
                target_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )
        elif self.fit_mode == "Fit":
            return pixmap.scaled(
                target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        elif self.fit_mode == "Fill":
            return pixmap.scaled(
                target_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
        else:  # Original
            return pixmap

    def update_performance_metrics(self, fps=None, quality=None):
        """Update performance indicators"""
        if fps is not None:
            self.fps_label.setText(f"{fps:.0f} FPS")
        if quality is not None:
            self.quality_label.setText(quality)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape and self.is_fullscreen:
            self.exit_fullscreen()
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        """Handle responsive resizing"""
        super().resizeEvent(event)
        # Re-apply current frame with new size
        if hasattr(self, "_current_frame"):
            self.update_video_frame(self._current_frame)
