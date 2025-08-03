"""
QEnhancedPreviewWidget - Enhanced preview widget for displaying output
This widget provides a large, prominent preview area for the enhanced output window.
"""

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QPainter
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, 
    QWidget, QSizePolicy, QScrollArea
)

from xlib import qt as qtx


class QEnhancedPreviewWidget(QWidget):
    """
    Enhanced preview widget that provides a large, prominent display area
    for the output window with additional controls and features.
    """
    
    # Signals
    fullscreen_requested = pyqtSignal()
    maximize_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    
    def __init__(self, title="Enhanced Output Preview", parent=None):
        super().__init__(parent)
        
        self.title = title
        self.is_fullscreen = False
        self.is_maximized = False
        
        self.setup_ui()
        self.apply_styling()
        
        # Setup timer for status updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
        
    def setup_ui(self):
        """Setup the enhanced preview UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header section
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # Main preview area
        preview_widget = self.create_preview_area()
        main_layout.addWidget(preview_widget, 1)  # Take most of the space
        
        # Control panel
        control_widget = self.create_control_panel()
        main_layout.addWidget(control_widget)
        
        self.setLayout(main_layout)
        
    def create_header(self):
        """Create the header section with title and status"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #2a2a2a);
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel(f"🎬 {self.title}")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: transparent;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("⏸️ Ready")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                background-color: #1a1a1a;
                padding: 8px 12px;
                border-radius: 15px;
                border: 1px solid #00ff00;
            }
        """)
        header_layout.addWidget(self.status_label)
        
        header_frame.setLayout(header_layout)
        return header_frame
        
    def create_preview_area(self):
        """Create the main preview display area"""
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.StyledPanel)
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border: 2px solid #666666;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        preview_layout = QVBoxLayout()
        
        # Preview display area
        self.preview_display = QLabel("📺 Preview Area\n\nOutput will be displayed here")
        self.preview_display.setAlignment(Qt.AlignCenter)
        self.preview_display.setFont(QFont("Arial", 12))
        self.preview_display.setStyleSheet("""
            QLabel {
                color: #888888;
                background-color: #111111;
                border: 1px dashed #444444;
                border-radius: 5px;
                padding: 20px;
            }
        """)
        self.preview_display.setMinimumSize(640, 480)
        self.preview_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        preview_layout.addWidget(self.preview_display)
        
        # Preview info bar
        info_bar = self.create_info_bar()
        preview_layout.addWidget(info_bar)
        
        preview_frame.setLayout(preview_layout)
        return preview_frame
        
    def create_info_bar(self):
        """Create information bar below preview"""
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        info_layout = QHBoxLayout()
        
        # Resolution info
        self.resolution_label = QLabel("Resolution: 1920x1080")
        self.resolution_label.setStyleSheet("color: #cccccc;")
        info_layout.addWidget(self.resolution_label)
        
        info_layout.addStretch()
        
        # FPS info
        self.fps_label = QLabel("FPS: 30.0")
        self.fps_label.setStyleSheet("color: #cccccc;")
        info_layout.addWidget(self.fps_label)
        
        info_layout.addStretch()
        
        # Frame count
        self.frame_label = QLabel("Frames: 0")
        self.frame_label.setStyleSheet("color: #cccccc;")
        info_layout.addWidget(self.frame_label)
        
        info_frame.setLayout(info_layout)
        return info_frame
        
    def create_control_panel(self):
        """Create the control panel with action buttons"""
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.StyledPanel)
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        control_layout = QHBoxLayout()
        
        # Left side - Quick actions
        quick_actions = QHBoxLayout()
        
        # Fullscreen button
        fullscreen_btn = QPushButton("🖥️ Fullscreen")
        fullscreen_btn.setStyleSheet(self.get_button_style())
        fullscreen_btn.clicked.connect(self.request_fullscreen)
        quick_actions.addWidget(fullscreen_btn)
        
        # Maximize button
        maximize_btn = QPushButton("📺 Maximize")
        maximize_btn.setStyleSheet(self.get_button_style())
        maximize_btn.clicked.connect(self.request_maximize)
        quick_actions.addWidget(maximize_btn)
        
        # Settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setStyleSheet(self.get_button_style())
        settings_btn.clicked.connect(self.request_settings)
        quick_actions.addWidget(settings_btn)
        
        control_layout.addLayout(quick_actions)
        control_layout.addStretch()
        
        # Right side - Status controls
        status_actions = QHBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(self.get_button_style())
        refresh_btn.clicked.connect(self.refresh_preview)
        status_actions.addWidget(refresh_btn)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setStyleSheet(self.get_button_style())
        clear_btn.clicked.connect(self.clear_preview)
        status_actions.addWidget(clear_btn)
        
        control_layout.addLayout(status_actions)
        
        control_frame.setLayout(control_layout)
        return control_frame
        
    def get_button_style(self):
        """Get the standard button style"""
        return """
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border: 1px solid #777777;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """
        
    def apply_styling(self):
        """Apply styling to the widget"""
        self.setStyleSheet("""
            QEnhancedPreviewWidget {
                background-color: #1e1e1e;
                border: 2px solid #444444;
                border-radius: 10px;
            }
        """)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(800, 600)
        
    def update_status(self):
        """Update status information"""
        # This would be connected to actual backend data
        pass
        
    def set_preview_image(self, image):
        """Set the preview image"""
        if image is not None:
            # Convert image to QPixmap and display
            # This is a placeholder - actual implementation would convert numpy array to QPixmap
            self.preview_display.setText("📺 Image Displayed")
            self.update_status_display("🟢 Live", "#00ff00")
        else:
            self.preview_display.setText("📺 No Image")
            self.update_status_display("🔴 No Signal", "#ff0000")
            
    def update_status_display(self, text, color="#00ff00"):
        """Update the status display"""
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background-color: #1a1a1a;
                padding: 8px 12px;
                border-radius: 15px;
                border: 1px solid {color};
            }}
        """)
        
    def request_fullscreen(self):
        """Request fullscreen mode"""
        self.fullscreen_requested.emit()
        self.update_status_display("🖥️ Fullscreen", "#ffff00")
        
    def request_maximize(self):
        """Request maximize mode"""
        self.maximize_requested.emit()
        self.update_status_display("📺 Maximized", "#00ffff")
        
    def request_settings(self):
        """Request settings dialog"""
        self.settings_requested.emit()
        self.update_status_display("⚙️ Settings", "#ff00ff")
        
    def refresh_preview(self):
        """Refresh the preview"""
        self.update_status_display("🔄 Refreshing...", "#ffff00")
        
    def clear_preview(self):
        """Clear the preview"""
        self.preview_display.setText("📺 Preview Cleared")
        self.update_status_display("🗑️ Cleared", "#888888") 