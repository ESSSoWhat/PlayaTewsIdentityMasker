#!/usr/bin/env python3
"""
Shadcn UI-Inspired Button Component for PlayaTewsIdentityMasker
Implements modern button design principles with variants, sizes, and animations
"""

from enum import Enum
from typing import Optional, Union
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPainter, QColor, QFont, QPixmap
from PyQt5.QtWidgets import QPushButton, QWidget, QSizePolicy

class ButtonVariant(Enum):
    """Button variant options"""
    DEFAULT = "default"
    DESTRUCTIVE = "destructive"
    OUTLINE = "outline"
    SECONDARY = "secondary"
    GHOST = "ghost"
    LINK = "link"

class ButtonSize(Enum):
    """Button size options"""
    SM = "sm"
    MD = "md"
    LG = "lg"

class QXShadcnButton(QPushButton):
    """
    Shadcn UI-inspired button component with modern design principles
    
    Features:
    - Multiple variants (default, destructive, outline, secondary, ghost, link)
    - Multiple sizes (sm, md, lg)
    - Smooth animations and transitions
    - Loading state support
    - Icon support
    - Accessibility features
    """
    
    # CSS Variables for theming
    CSS_VARIABLES = """
        :root {
            --background: #0a0a0a;
            --foreground: #ffffff;
            --primary: #0078d4;
            --primary-foreground: #ffffff;
            --primary-hover: #106ebe;
            --secondary: #404040;
            --secondary-foreground: #ffffff;
            --secondary-hover: #505050;
            --muted: #2b2b2b;
            --muted-foreground: #a1a1aa;
            --accent: #4CAF50;
            --accent-foreground: #ffffff;
            --destructive: #ef4444;
            --destructive-foreground: #ffffff;
            --destructive-hover: #dc2626;
            --border: #404040;
            --input: #1e1e1e;
            --ring: #0078d4;
            --radius: 6px;
        }
    """
    
    # Variant styles
    VARIANT_STYLES = {
        ButtonVariant.DEFAULT: {
            "background": "var(--primary)",
            "color": "var(--primary-foreground)",
            "border": "none",
            "hover_background": "var(--primary-hover)",
            "focus_ring": "var(--ring)"
        },
        ButtonVariant.DESTRUCTIVE: {
            "background": "var(--destructive)",
            "color": "var(--destructive-foreground)",
            "border": "none",
            "hover_background": "var(--destructive-hover)",
            "focus_ring": "var(--destructive)"
        },
        ButtonVariant.OUTLINE: {
            "background": "transparent",
            "color": "var(--foreground)",
            "border": "1px solid var(--border)",
            "hover_background": "var(--accent)",
            "hover_color": "var(--accent-foreground)",
            "focus_ring": "var(--ring)"
        },
        ButtonVariant.SECONDARY: {
            "background": "var(--secondary)",
            "color": "var(--secondary-foreground)",
            "border": "none",
            "hover_background": "var(--secondary-hover)",
            "focus_ring": "var(--ring)"
        },
        ButtonVariant.GHOST: {
            "background": "transparent",
            "color": "var(--foreground)",
            "border": "none",
            "hover_background": "var(--accent)",
            "hover_color": "var(--accent-foreground)",
            "focus_ring": "var(--ring)"
        },
        ButtonVariant.LINK: {
            "background": "transparent",
            "color": "var(--primary)",
            "border": "none",
            "text_decoration": "underline",
            "hover_color": "var(--primary-hover)",
            "focus_ring": "var(--ring)"
        }
    }
    
    # Size styles
    SIZE_STYLES = {
        ButtonSize.SM: {
            "height": "32px",
            "padding": "0 12px",
            "font_size": "12px",
            "border_radius": "4px"
        },
        ButtonSize.MD: {
            "height": "40px",
            "padding": "0 16px",
            "font_size": "14px",
            "border_radius": "6px"
        },
        ButtonSize.LG: {
            "height": "48px",
            "padding": "0 24px",
            "font_size": "16px",
            "border_radius": "8px"
        }
    }
    
    def __init__(self, 
                 text: str = "",
                 variant: ButtonVariant = ButtonVariant.DEFAULT,
                 size: ButtonSize = ButtonSize.MD,
                 icon: Optional[QIcon] = None,
                 loading: bool = False,
                 disabled: bool = False,
                 parent: Optional[QWidget] = None):
        """
        Initialize the Shadcn UI-inspired button
        
        Args:
            text: Button text
            variant: Button variant (default, destructive, outline, etc.)
            size: Button size (sm, md, lg)
            icon: Optional icon
            loading: Whether button is in loading state
            disabled: Whether button is disabled
            parent: Parent widget
        """
        super().__init__(text, parent)
        
        self.variant = variant
        self.size = size
        self.icon = icon
        self.loading = loading
        self.disabled = disabled
        
        # Animation properties
        self.animation = None
        self.hover_animation = None
        self.click_animation = None
        
        # Loading animation
        self.loading_angle = 0
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_animation)
        
        # Setup the button
        self.setup_ui()
        self.setup_animations()
        self.setup_accessibility()
        
        # Apply initial state
        self.setEnabled(not disabled)
        if loading:
            self.set_loading(True)
    
    def setup_ui(self):
        """Setup button UI and styling"""
        # Set icon if provided
        if self.icon:
            self.setIcon(self.icon)
        
        # Apply size policy
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        # Apply styles
        self.apply_styles()
        
        # Connect signals
        self.clicked.connect(self.on_clicked)
    
    def apply_styles(self):
        """Apply CSS styles based on variant and size"""
        variant_style = self.VARIANT_STYLES[self.variant]
        size_style = self.SIZE_STYLES[self.size]
        
        # Build CSS
        css = f"""
        QPushButton {{
            background-color: {variant_style['background']};
            color: {variant_style['color']};
            border: {variant_style.get('border', 'none')};
            border-radius: {size_style['border_radius']};
            padding: {size_style['padding']};
            font-size: {size_style['font_size']};
            font-weight: 500;
            height: {size_style['height']};
            min-height: {size_style['height']};
            max-height: {size_style['height']};
            text-align: center;
            transition: all 0.2s ease;
        }}
        
        QPushButton:hover {{
            background-color: {variant_style.get('hover_background', variant_style['background'])};
            color: {variant_style.get('hover_color', variant_style['color'])};
            transform: translateY(-1px);
        }}
        
        QPushButton:pressed {{
            transform: translateY(0px);
            background-color: {variant_style.get('pressed_background', variant_style.get('hover_background', variant_style['background']))};
        }}
        
        QPushButton:focus {{
            outline: 2px solid {variant_style.get('focus_ring', 'var(--ring)')};
            outline-offset: 2px;
        }}
        
        QPushButton:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }}
        """
        
        # Add text decoration for link variant
        if self.variant == ButtonVariant.LINK:
            css += """
            QPushButton {
                text-decoration: underline;
            }
            """
        
        self.setStyleSheet(css)
    
    def setup_animations(self):
        """Setup button animations"""
        # Hover animation
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(150)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Click animation
        self.click_animation = QPropertyAnimation(self, b"geometry")
        self.click_animation.setDuration(100)
        self.click_animation.setEasingCurve(QEasingCurve.OutBack)
    
    def setup_accessibility(self):
        """Setup accessibility features"""
        # Set accessible name
        self.setAccessibleName(self.text())
        
        # Set accessible description
        description = f"Button with {self.variant.value} variant and {self.size.value} size"
        if self.icon:
            description += " and icon"
        self.setAccessibleDescription(description)
        
        # Set focus policy
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Set tab order
        self.setTabOrder(self, self)
    
    def set_loading(self, loading: bool):
        """Set loading state"""
        self.loading = loading
        
        if loading:
            # Start loading animation
            self.loading_timer.start(16)  # 60 FPS
            self.setEnabled(False)
            self.setText("")
        else:
            # Stop loading animation
            self.loading_timer.stop()
            self.setEnabled(True)
            self.setText(self.property("original_text") or "")
    
    def update_loading_animation(self):
        """Update loading spinner animation"""
        self.loading_angle = (self.loading_angle + 10) % 360
        self.update()
    
    def set_variant(self, variant: ButtonVariant):
        """Change button variant"""
        self.variant = variant
        self.apply_styles()
    
    def set_size(self, size: ButtonSize):
        """Change button size"""
        self.size = size
        self.apply_styles()
    
    def set_icon(self, icon: QIcon):
        """Set button icon"""
        self.icon = icon
        super().setIcon(icon)
    
    def set_text(self, text: str):
        """Set button text"""
        # Store original text for loading state
        self.setProperty("original_text", text)
        super().setText(text)
    
    def on_clicked(self):
        """Handle button click with animation"""
        if not self.loading and self.isEnabled():
            # Trigger click animation
            self.trigger_click_animation()
    
    def trigger_click_animation(self):
        """Trigger click animation"""
        if self.click_animation:
            # Create a subtle scale animation
            current_geometry = self.geometry()
            center = current_geometry.center()
            
            # Scale down slightly
            scaled_width = int(current_geometry.width() * 0.95)
            scaled_height = int(current_geometry.height() * 0.95)
            scaled_x = center.x() - scaled_width // 2
            scaled_y = center.y() - scaled_height // 2
            
            self.click_animation.setStartValue(current_geometry)
            self.click_animation.setEndValue(current_geometry)
            
            # Quick scale down and up
            self.click_animation.setKeyValueAt(0.5, self.geometry().adjusted(
                scaled_x - current_geometry.x(),
                scaled_y - current_geometry.y(),
                scaled_width - current_geometry.width(),
                scaled_height - current_geometry.height()
            ))
            
            self.click_animation.start()
    
    def paintEvent(self, event):
        """Custom paint event for loading animation"""
        if self.loading:
            self.paint_loading_spinner(event)
        else:
            super().paintEvent(event)
    
    def paint_loading_spinner(self, event):
        """Paint loading spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get button colors from current variant
        variant_style = self.VARIANT_STYLES[self.variant]
        color = QColor(variant_style['color'].replace('var(--', '').replace(')', ''))
        
        # Draw spinner
        center = self.rect().center()
        radius = min(self.width(), self.height()) // 4
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        
        # Draw 8 dots in a circle
        for i in range(8):
            angle = (self.loading_angle + i * 45) % 360
            x = center.x() + radius * 0.7 * (angle / 360.0)
            y = center.y() + radius * 0.7 * (angle / 360.0)
            
            # Fade dots based on angle
            alpha = 255 - int((angle % 360) / 360.0 * 200)
            color.setAlpha(alpha)
            painter.setBrush(color)
            
            painter.drawEllipse(int(x - 2), int(y - 2), 4, 4)
    
    def enterEvent(self, event):
        """Handle mouse enter event"""
        super().enterEvent(event)
        if not self.loading and self.isEnabled():
            # Trigger hover animation
            self.trigger_hover_animation(True)
    
    def leaveEvent(self, event):
        """Handle mouse leave event"""
        super().leaveEvent(event)
        if not self.loading and self.isEnabled():
            # Trigger hover animation
            self.trigger_hover_animation(False)
    
    def trigger_hover_animation(self, entering: bool):
        """Trigger hover animation"""
        if self.hover_animation:
            current_geometry = self.geometry()
            
            if entering:
                # Slight scale up
                scale_factor = 1.02
                new_width = int(current_geometry.width() * scale_factor)
                new_height = int(current_geometry.height() * scale_factor)
                new_x = current_geometry.x() - (new_width - current_geometry.width()) // 2
                new_y = current_geometry.y() - (new_height - current_geometry.height()) // 2
                
                self.hover_animation.setStartValue(current_geometry)
                self.hover_animation.setEndValue(current_geometry.adjusted(
                    new_x - current_geometry.x(),
                    new_y - current_geometry.y(),
                    new_width - current_geometry.width(),
                    new_height - current_geometry.height()
                ))
            else:
                # Return to original size
                self.hover_animation.setStartValue(self.geometry())
                self.hover_animation.setEndValue(current_geometry)
            
            self.hover_animation.start()
    
    def keyPressEvent(self, event):
        """Handle keyboard events for accessibility"""
        if event.key() in [Qt.Key_Return, Qt.Key_Space]:
            self.click()
        else:
            super().keyPressEvent(event)


# Convenience functions for creating buttons
def create_button(text: str = "", 
                  variant: ButtonVariant = ButtonVariant.DEFAULT,
                  size: ButtonSize = ButtonSize.MD,
                  icon: Optional[QIcon] = None,
                  **kwargs) -> QXShadcnButton:
    """Create a Shadcn UI-inspired button"""
    return QXShadcnButton(text=text, variant=variant, size=size, icon=icon, **kwargs)


def create_primary_button(text: str = "", **kwargs) -> QXShadcnButton:
    """Create a primary button"""
    return create_button(text=text, variant=ButtonVariant.DEFAULT, **kwargs)


def create_destructive_button(text: str = "", **kwargs) -> QXShadcnButton:
    """Create a destructive button"""
    return create_button(text=text, variant=ButtonVariant.DESTRUCTIVE, **kwargs)


def create_outline_button(text: str = "", **kwargs) -> QXShadcnButton:
    """Create an outline button"""
    return create_button(text=text, variant=ButtonVariant.OUTLINE, **kwargs)


def create_secondary_button(text: str = "", **kwargs) -> QXShadcnButton:
    """Create a secondary button"""
    return create_button(text=text, variant=ButtonVariant.SECONDARY, **kwargs)


def create_ghost_button(text: str = "", **kwargs) -> QXShadcnButton:
    """Create a ghost button"""
    return create_button(text=text, variant=ButtonVariant.GHOST, **kwargs)


def create_link_button(text: str = "", **kwargs) -> QXShadcnButton:
    """Create a link button"""
    return create_button(text=text, variant=ButtonVariant.LINK, **kwargs) 