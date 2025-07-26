#!/usr/bin/env python3
"""
Shadcn UI Components Demo for PlayaTewsIdentityMasker
Demonstrates modern UI design principles applied to PyQt5
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QGroupBox, 
                             QTabWidget, QScrollArea, QFrame, QSplitter)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont

# Import our Shadcn UI components
from xlib.qt.widgets.QXShadcnButton import (
    QXShadcnButton, ButtonVariant, ButtonSize,
    create_primary_button, create_destructive_button, create_outline_button,
    create_secondary_button, create_ghost_button, create_link_button
)

class ShadcnUIDemo(QMainWindow):
    """Demo window showcasing Shadcn UI principles"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shadcn UI Components Demo - PlayaTewsIdentityMasker")
        self.setMinimumSize(1000, 700)
        
        # Setup central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Component showcase
        left_panel = self.create_component_showcase()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Live preview
        right_panel = self.create_live_preview()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([600, 400])
        main_layout.addWidget(content_splitter)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Setup demo timer for loading states
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.cycle_loading_states)
        self.demo_timer.start(3000)  # Cycle every 3 seconds
        
        self.loading_buttons = []
    
    def create_header(self):
        """Create the demo header"""
        header = QFrame()
        header.setFrameStyle(QFrame.StyledPanel)
        header.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(header)
        
        # Title
        title = QLabel("🎨 Shadcn UI Principles Demo")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Modern UI Design Principles Applied to PyQt5")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 16px;
                font-weight: normal;
            }
        """)
        layout.addWidget(subtitle)
        
        return header
    
    def create_component_showcase(self):
        """Create the component showcase panel"""
        showcase = QWidget()
        layout = QVBoxLayout(showcase)
        
        # Create scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # Button Variants Section
        button_section = self.create_button_variants_section()
        scroll_layout.addWidget(button_section)
        
        # Button Sizes Section
        size_section = self.create_button_sizes_section()
        scroll_layout.addWidget(size_section)
        
        # Interactive Features Section
        interactive_section = self.create_interactive_features_section()
        scroll_layout.addWidget(interactive_section)
        
        # Accessibility Section
        accessibility_section = self.create_accessibility_section()
        scroll_layout.addWidget(accessibility_section)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return showcase
    
    def create_button_variants_section(self):
        """Create button variants showcase"""
        section = QGroupBox("🎨 Button Variants")
        section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        
        layout = QVBoxLayout(section)
        
        # Variant grid
        grid = QGridLayout()
        grid.setSpacing(10)
        
        variants = [
            ("Primary", ButtonVariant.DEFAULT),
            ("Destructive", ButtonVariant.DESTRUCTIVE),
            ("Outline", ButtonVariant.OUTLINE),
            ("Secondary", ButtonVariant.SECONDARY),
            ("Ghost", ButtonVariant.GHOST),
            ("Link", ButtonVariant.LINK)
        ]
        
        for i, (name, variant) in enumerate(variants):
            # Label
            label = QLabel(name)
            label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
            grid.addWidget(label, i, 0)
            
            # Button
            button = QXShadcnButton(f"{name} Button", variant=variant)
            button.clicked.connect(lambda checked, v=name: self.on_button_clicked(v))
            grid.addWidget(button, i, 1)
        
        layout.addLayout(grid)
        return section
    
    def create_button_sizes_section(self):
        """Create button sizes showcase"""
        section = QGroupBox("📏 Button Sizes")
        section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        
        layout = QVBoxLayout(section)
        
        # Size grid
        grid = QGridLayout()
        grid.setSpacing(10)
        
        sizes = [
            ("Small", ButtonSize.SM),
            ("Medium", ButtonSize.MD),
            ("Large", ButtonSize.LG)
        ]
        
        for i, (name, size) in enumerate(sizes):
            # Label
            label = QLabel(name)
            label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
            grid.addWidget(label, i, 0)
            
            # Button
            button = QXShadcnButton(f"{name} Button", size=size)
            button.clicked.connect(lambda checked, s=name: self.on_button_clicked(s))
            grid.addWidget(button, i, 1)
        
        layout.addLayout(grid)
        return section
    
    def create_interactive_features_section(self):
        """Create interactive features showcase"""
        section = QGroupBox("⚡ Interactive Features")
        section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        
        layout = QVBoxLayout(section)
        
        # Loading state demo
        loading_label = QLabel("🔄 Loading States")
        loading_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(loading_label)
        
        loading_layout = QHBoxLayout()
        
        # Loading button
        self.loading_button = QXShadcnButton("Loading...", loading=True)
        self.loading_buttons.append(self.loading_button)
        loading_layout.addWidget(self.loading_button)
        
        # Toggle loading button
        toggle_loading_btn = QXShadcnButton("Toggle Loading", variant=ButtonVariant.SECONDARY)
        toggle_loading_btn.clicked.connect(self.toggle_loading)
        loading_layout.addWidget(toggle_loading_btn)
        
        layout.addLayout(loading_layout)
        
        # Disabled state demo
        disabled_label = QLabel("🚫 Disabled States")
        disabled_label.setStyleSheet("font-weight: bold; margin: 20px 0 10px 0;")
        layout.addWidget(disabled_label)
        
        disabled_layout = QHBoxLayout()
        
        # Disabled buttons
        disabled_primary = QXShadcnButton("Disabled Primary", disabled=True)
        disabled_layout.addWidget(disabled_primary)
        
        disabled_outline = QXShadcnButton("Disabled Outline", variant=ButtonVariant.OUTLINE, disabled=True)
        disabled_layout.addWidget(disabled_outline)
        
        layout.addLayout(disabled_layout)
        
        return section
    
    def create_accessibility_section(self):
        """Create accessibility features showcase"""
        section = QGroupBox("♿ Accessibility Features")
        section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        
        layout = QVBoxLayout(section)
        
        # Accessibility info
        info_text = """
        <h3>♿ Accessibility Features Implemented:</h3>
        <ul>
            <li><strong>Keyboard Navigation:</strong> Tab through buttons, Enter/Space to activate</li>
            <li><strong>Screen Reader Support:</strong> Proper accessible names and descriptions</li>
            <li><strong>Focus Indicators:</strong> Clear focus rings for keyboard users</li>
            <li><strong>High Contrast:</strong> Optimized colors for visibility</li>
            <li><strong>Semantic Structure:</strong> Proper widget hierarchy</li>
        </ul>
        
        <p><strong>Try:</strong> Use Tab to navigate between buttons, then press Enter or Space to activate them.</p>
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            QLabel {
                background: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 15px;
                line-height: 1.5;
            }
        """)
        layout.addWidget(info_label)
        
        return section
    
    def create_live_preview(self):
        """Create live preview panel"""
        preview = QWidget()
        layout = QVBoxLayout(preview)
        
        # Preview header
        preview_header = QLabel("👁️ Live Preview")
        preview_header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #4CAF50;
            }
        """)
        layout.addWidget(preview_header)
        
        # Preview area
        self.preview_area = QFrame()
        self.preview_area.setFrameStyle(QFrame.StyledPanel)
        self.preview_area.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 2px solid #404040;
                border-radius: 8px;
                min-height: 400px;
            }
        """)
        
        preview_layout = QVBoxLayout(self.preview_area)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        
        # Preview content
        self.preview_content = QLabel("Click buttons in the left panel to see interactions here!")
        self.preview_content.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 14px;
                text-align: center;
                padding: 20px;
            }
        """)
        self.preview_content.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.preview_content)
        
        layout.addWidget(self.preview_area)
        
        return preview
    
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
                color: #ffffff;
            }
            QWidget {
                background-color: #0a0a0a;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #404040;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #505050;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
    def on_button_clicked(self, button_name):
        """Handle button clicks"""
        self.preview_content.setText(f"🎯 {button_name} button clicked!\n\nThis demonstrates the interactive feedback and accessibility features.")
        self.preview_content.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 16px;
                text-align: center;
                padding: 20px;
                background: #1e1e1e;
                border-radius: 8px;
                border: 2px solid #4CAF50;
            }
        """)
    
    def toggle_loading(self):
        """Toggle loading state of demo button"""
        current_loading = self.loading_button.loading
        self.loading_button.set_loading(not current_loading)
        
        if not current_loading:
            self.preview_content.setText("🔄 Loading state activated!\n\nNotice the animated spinner and disabled interaction.")
        else:
            self.preview_content.setText("✅ Loading state deactivated!\n\nButton is now interactive again.")
    
    def cycle_loading_states(self):
        """Cycle through loading states for demo"""
        for button in self.loading_buttons:
            current_loading = button.loading
            button.set_loading(not current_loading)


def main():
    """Main function to run the demo"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Shadcn UI Demo")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PlayaTewsIdentityMasker")
    
    # Create and show demo window
    demo = ShadcnUIDemo()
    demo.show()
    
    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 