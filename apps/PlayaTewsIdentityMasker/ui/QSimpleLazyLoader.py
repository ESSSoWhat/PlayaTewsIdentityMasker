#!/usr/bin/env python3
"""
Simple Lazy Loading System for PlayaTewsIdentityMasker
Provides performance benefits without widget hierarchy issues
"""

import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from resources.fonts import QXFontDB
from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel


class QLazyLoadPlaceholder(qtx.QXWidget):
    """Placeholder widget that loads the real component when clicked"""

    def __init__(
        self, component_name: str, component_factory: Callable, load_priority: int = 1
    ):
        super().__init__()

        self.component_name = component_name
        self.component_factory = component_factory
        self.load_priority = load_priority
        self.is_loaded = False
        self.real_component = None
        self.load_start_time = None

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the placeholder UI"""
        self.setFixedSize(250, 120)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                margin: 2px;
            }
            QWidget:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
        """
        )

        # Main label
        self.name_label = QXLabel(text=f"Click to load {self.component_name}")
        self.name_label.setAlignment(qtx.AlignCenter)
        self.name_label.setStyleSheet(
            """
            color: #495057;
            font-weight: bold;
            font-size: 12px;
        """
        )

        # Status label
        self.status_label = QXLabel(text="Ready to load")
        self.status_label.setAlignment(qtx.AlignCenter)
        self.status_label.setStyleSheet(
            """
            color: #6c757d;
            font-size: 10px;
        """
        )

        # Priority indicator
        priority_text = (
            "High"
            if self.load_priority <= 2
            else "Medium" if self.load_priority <= 4 else "Low"
        )
        self.priority_label = QXLabel(text=f"Priority: {priority_text}")
        self.priority_label.setAlignment(qtx.AlignCenter)
        self.priority_label.setStyleSheet(
            """
            color: #28a745;
            font-size: 9px;
            font-style: italic;
        """
        )

        # Layout
        layout = qtx.QXVBoxLayout(
            [
                (self.name_label, qtx.AlignCenter),
                (self.status_label, qtx.AlignCenter),
                (self.priority_label, qtx.AlignCenter),
            ]
        )
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        self.setLayout(layout)

    def create_placeholder(self, component_name: str):
        """Create a placeholder widget for lazy loading"""
        from xlib.qt.widgets.QXLabel import QXLabel

        placeholder = QXLabel(f"Loading {component_name}...")
        placeholder.setStyleSheet("QLabel { color: gray; font-style: italic; }")
        return placeholder

    def setup_connections(self):
        """Setup click event for lazy loading"""
        self.mousePressEvent = self.on_click

    def on_click(self, event):
        """Handle click to load component"""
        if not self.is_loaded:
            self.load_component()

    def load_component(self):
        """Load the real component"""
        try:
            self.load_start_time = time.time()
            self.status_label.setText("Loading...")
            self.status_label.setStyleSheet("color: #ffc107; font-size: 10px;")

            # Create the real component
            self.real_component = self.component_factory()

            # Replace placeholder with real component
            self.replace_with_real_component()

            load_time = time.time() - self.load_start_time
            self.logger.info(f"Loaded {self.component_name} in {load_time:.2f}s")

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)[:30]}")
            self.status_label.setStyleSheet("color: #dc3545; font-size: 10px;")
            self.logger.error(f"Failed to load {self.component_name}: {e}")

    def replace_with_real_component(self):
        """Replace placeholder with the real component"""
        if not self.real_component:
            return

        try:
            # Get parent layout
            parent = self.parent()
            if parent and parent.layout():
                parent_layout = parent.layout()
                placeholder_index = parent_layout.indexOf(self)

                if placeholder_index >= 0:
                    # Remove placeholder
                    parent_layout.removeWidget(self)
                    self.hide()

                    # Insert real component
                    parent_layout.insertWidget(placeholder_index, self.real_component)
                    self.real_component.show()

                    # Mark as loaded
                    self.is_loaded = True

                    # Update parent widget
                    parent.update()

                else:
                    self.logger.warning(
                        f"Could not find placeholder index for {self.component_name}"
                    )
            else:
                self.logger.error(f"No parent layout found for {self.component_name}")

        except Exception as e:
            self.logger.error(
                f"Error replacing placeholder for {self.component_name}: {e}"
            )

    @property
    def logger(self):
        return logging.getLogger(f"{__name__}.{self.component_name}")


class QSimpleLazyLoader:
    """Simple lazy loading manager"""

    def __init__(self):
        self.components: Dict[str, QLazyLoadPlaceholder] = {}
        self.loaded_components: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

    def register_component(
        self, name: str, factory: Callable, load_priority: int = 1
    ) -> QLazyLoadPlaceholder:
        """Register a component for lazy loading"""
        # Store component info without creating placeholder immediately
        self.components[name] = {
            "factory": factory,
            "priority": load_priority,
            "placeholder": None,  # Will be created when needed
        }
        self.logger.info(f"Registered component: {name} (priority: {load_priority})")
        return None  # Return None for now, placeholder will be created on demand

    def get_component(self, name: str) -> Optional[Any]:
        """Get a component (loads if necessary)"""
        if name in self.loaded_components:
            return self.loaded_components[name]

        if name in self.components:
            component_info = self.components[name]
            # Create the component directly
            component = component_info["factory"]()
            if component:
                self.loaded_components[name] = component
                return component

        return None

    def get_placeholder(self, name: str, parent=None) -> Optional[QLazyLoadPlaceholder]:
        """Get the placeholder for a component (creates if needed)"""
        if name not in self.components:
            return None

        component_info = self.components[name]
        if component_info["placeholder"] is None:
            # Create placeholder on demand with proper parent
            placeholder = QLazyLoadPlaceholder(
                name, component_info["factory"], component_info["priority"]
            )
            if parent:
                placeholder.setParent(parent)
            component_info["placeholder"] = placeholder

        return component_info["placeholder"]

    def preload_components(self, component_names: list, max_concurrent: int = 2):
        """Preload components in background"""
        import threading

        def preload_worker():
            for name in component_names:
                if name in self.components and name not in self.loaded_components:
                    try:
                        self.get_component(name)
                        time.sleep(0.1)  # Small delay to prevent UI blocking
                    except Exception as e:
                        self.logger.error(f"Preload failed for {name}: {e}")

        thread = threading.Thread(target=preload_worker, daemon=True)
        thread.start()

    def get_stats(self) -> Dict[str, Any]:
        """Get loading statistics"""
        total = len(self.components)
        loaded = len(self.loaded_components)

        return {
            "total_components": total,
            "loaded_components": loaded,
            "loading_progress": loaded / total if total > 0 else 0,
            "components": list(self.components.keys()),
        }

    def clear(self):
        """Clear all components"""
        self.components.clear()
        self.loaded_components.clear()


# Global lazy loader instance
_lazy_loader = None


def get_lazy_loader() -> QSimpleLazyLoader:
    """Get the global lazy loader instance"""
    global _lazy_loader
    if _lazy_loader is None:
        _lazy_loader = QSimpleLazyLoader()
    return _lazy_loader


def cleanup_lazy_loader():
    """Clean up the global lazy loader"""
    global _lazy_loader
    if _lazy_loader:
        _lazy_loader.clear()
        _lazy_loader = None
