"""
QEnhancedStreamOutput - Enhanced streaming output UI component
This module provides an enhanced version of QStreamOutput with additional features.
"""

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame

from xlib import qt as qtx
from .QStreamOutput import QStreamOutput


class QEnhancedStreamOutput(QStreamOutput):
    """
    Enhanced streaming output UI component that extends QStreamOutput
    with additional features and capabilities for better preview display.
    """
    
    def __init__(self, backend):
        """
        Initialize the enhanced streaming output UI
        
        Args:
            backend: The StreamOutput backend instance
        """
        super().__init__(backend)
        
        # Store the original layout
        self.original_layout = self.layout()
        
        # Create enhanced layout
        self.setup_enhanced_layout()
        
        # Apply enhanced styling
        self.apply_enhanced_styling()
        
    def setup_enhanced_layout(self):
        """Setup enhanced layout with better preview display"""
        # Create main enhanced layout
        enhanced_layout = QVBoxLayout()
        
        # Add title
        title_label = QLabel("🎬 Enhanced Output Preview")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #2d2d2d;
                padding: 8px;
                border-radius: 5px;
                margin-bottom: 5px;
            }
        """)
        enhanced_layout.addWidget(title_label)
        
        # Add status indicator
        self.status_label = QLabel("⏸️ Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                background-color: #1a1a1a;
                padding: 5px;
                border-radius: 3px;
                margin-bottom: 10px;
            }
        """)
        enhanced_layout.addWidget(self.status_label)
        
        # Add the original stream output controls in a scrollable area
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.StyledPanel)
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.create_controls_widget())
        controls_frame.setLayout(controls_layout)
        
        enhanced_layout.addWidget(controls_frame)
        
        # Add quick action buttons
        self.setup_quick_actions(enhanced_layout)
        
        # Set the enhanced layout
        self.setLayout(enhanced_layout)
        
    def create_controls_widget(self):
        """Create a widget containing the original stream output controls"""
        controls_widget = qtx.QXWidget()
        
        # Recreate the original grid layout
        if self.original_layout:
            controls_widget.setLayout(self.original_layout)
        
        return controls_widget
        
    def setup_quick_actions(self, layout):
        """Setup quick action buttons for enhanced functionality"""
        actions_frame = QFrame()
        actions_frame.setFrameStyle(QFrame.StyledPanel)
        actions_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        actions_layout = QHBoxLayout()
        
        # Fullscreen button
        fullscreen_btn = QPushButton("🖥️ Fullscreen")
        fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border: 1px solid #777777;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        actions_layout.addWidget(fullscreen_btn)
        
        # Maximize preview button
        maximize_btn = QPushButton("📺 Maximize Preview")
        maximize_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border: 1px solid #777777;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        maximize_btn.clicked.connect(self.maximize_preview)
        actions_layout.addWidget(maximize_btn)
        
        # Settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border: 1px solid #777777;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        settings_btn.clicked.connect(self.open_settings)
        actions_layout.addWidget(settings_btn)
        
        actions_frame.setLayout(actions_layout)
        layout.addWidget(actions_frame)
        
    def apply_enhanced_styling(self):
        """Apply enhanced styling to the component"""
        self.setStyleSheet("""
            QEnhancedStreamOutput {
                background-color: #1e1e1e;
                border: 2px solid #444444;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        # Set minimum size for better visibility
        self.setMinimumSize(400, 600)
        
    def toggle_fullscreen(self):
        """Toggle fullscreen mode for the output window"""
        # This would integrate with the backend to toggle fullscreen
        print("🎬 Toggling fullscreen mode...")
        self.status_label.setText("🖥️ Fullscreen Mode")
        
    def maximize_preview(self):
        """Maximize the preview area"""
        print("📺 Maximizing preview area...")
        self.status_label.setText("📺 Preview Maximized")
        
    def open_settings(self):
        """Open enhanced settings dialog"""
        print("⚙️ Opening enhanced settings...")
        self.status_label.setText("⚙️ Settings Open")
        
    def update_status(self, status_text, status_color="#00ff00"):
        """Update the status display"""
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {status_color};
                background-color: #1a1a1a;
                padding: 5px;
                border-radius: 3px;
                margin-bottom: 10px;
            }}
        """) 