#!/usr/bin/env python3
"""
Collapsible Component Wrapper
Wraps any UI component to make it collapsible for better space utilization
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from xlib import qt as qtx
from xlib.qt.widgets.QXCollapsibleSection import QXCollapsibleSection


class QCollapsibleComponentWrapper(QXCollapsibleSection):
    """Wrapper to make any component collapsible for better space utilization"""

    def __init__(
        self, component, title=None, is_opened=False, auto_collapse_threshold=4
    ):
        """
        Initialize collapsible wrapper

        Args:
            component: The UI component to wrap
            title: Optional title for the section (defaults to component title)
            is_opened: Whether section starts opened (defaults to False for small components)
            auto_collapse_threshold: Auto-collapse if component has fewer than this many settings
        """
        self.component = component
        self.auto_collapse_threshold = auto_collapse_threshold

        # Get the component's layout
        if hasattr(component, "layout"):
            content_layout = component.layout()
        else:
            # Create a wrapper layout
            content_layout = qtx.QXVBoxLayout()
            content_layout.addWidget(component)

        # Determine title
        if title is None:
            title = self._extract_component_title(component)

        # Auto-collapse small components
        if self._count_component_settings(component) <= auto_collapse_threshold:
            is_opened = False

        super().__init__(
            title,
            content_layout,
            False,  # vertical
            is_opened,  # is_opened
            True,  # allow_open_close
        )

    def _extract_component_title(self, component):
        """Extract title from component"""
        if hasattr(component, "windowTitle"):
            title = component.windowTitle()
            if title:
                return title

        if hasattr(component, "_title"):
            return component._title

        if hasattr(component, "title"):
            return component.title

        # Try to get from backend if available
        if hasattr(component, "_backend"):
            backend = component._backend
            if hasattr(backend, "__class__"):
                return backend.__class__.__name__.replace("Backend", "")

        return "Component"

    def _count_component_settings(self, component):
        """Count the number of settings in a component"""
        count = 0

        # Try to count widgets in the component
        if hasattr(component, "findChildren"):
            try:
                from PyQt5.QtWidgets import (
                    QCheckBox,
                    QComboBox,
                    QLineEdit,
                    QSlider,
                    QSpinBox,
                )

                # Count various types of input widgets
                spinboxes = len(component.findChildren(QSpinBox))
                comboboxes = len(component.findChildren(QComboBox))
                checkboxes = len(component.findChildren(QCheckBox))
                sliders = len(component.findChildren(QSlider))
                lineedits = len(component.findChildren(QLineEdit))

                count = spinboxes + comboboxes + checkboxes + sliders + lineedits
            except Exception:
                # Fallback if findChildren fails
                count = 0

        return count

    def get_component(self):
        """Get the wrapped component"""
        return self.component

    def set_auto_collapse(self, enabled=True):
        """Enable/disable auto-collapse based on component size"""
        if (
            enabled
            and self._count_component_settings(self.component)
            <= self.auto_collapse_threshold
        ):
            self.close()
        elif not enabled:
            self.open()


class QSmartCollapsibleGroup(QXCollapsibleSection):
    """Smart collapsible group that automatically manages multiple small components"""

    def __init__(self, title, components, max_visible_components=3):
        """
        Initialize smart collapsible group

        Args:
            title: Group title
            components: List of (component, component_title) tuples
            max_visible_components: Maximum components to show before collapsing
        """
        self.components = components
        self.max_visible_components = max_visible_components

        # Create content layout
        content_layout = qtx.QXVBoxLayout()

        # Add components
        for component, component_title in components:
            if component_title:
                # Create collapsible wrapper for each component
                wrapper = QCollapsibleComponentWrapper(
                    component=component,
                    title=component_title,
                    is_opened=len(components) <= max_visible_components,
                )
                content_layout.addWidget(wrapper)
            else:
                content_layout.addWidget(component)

        super().__init__(
            title,
            content_layout,
            False,  # vertical
            len(components) <= max_visible_components,  # is_opened
            True,  # allow_open_close
        )

    def add_component(self, component, title=None):
        """Add a component to the group"""
        self.components.append((component, title))

        # Recreate layout with new component
        self._recreate_layout()

    def remove_component(self, component):
        """Remove a component from the group"""
        self.components = [(c, t) for c, t in self.components if c != component]

        # Recreate layout without the component
        self._recreate_layout()

    def _recreate_layout(self):
        """Recreate the content layout with current components"""
        # Clear existing layout
        if hasattr(self, "frame") and self.frame.layout():
            qtx.QXWidget.clear_layout(self.frame.layout())

        # Recreate layout
        content_layout = qtx.QXVBoxLayout()

        for component, component_title in self.components:
            if component_title:
                wrapper = QCollapsibleComponentWrapper(
                    component=component,
                    title=component_title,
                    is_opened=len(self.components) <= self.max_visible_components,
                )
                content_layout.addWidget(wrapper)
            else:
                content_layout.addWidget(component)

        # Update frame layout
        if hasattr(self, "frame"):
            self.frame.setLayout(content_layout)

        # Update collapse state
        if len(self.components) > self.max_visible_components:
            self.close()
        else:
            self.open()


# Factory functions for easy component wrapping


def make_collapsible(component, title=None, auto_collapse=True):
    """Factory function to make any component collapsible"""
    return QCollapsibleComponentWrapper(
        component=component, title=title, is_opened=not auto_collapse
    )


def group_small_components(title, components, max_visible=3):
    """Factory function to group small components"""
    return QSmartCollapsibleGroup(
        title=title, components=components, max_visible_components=max_visible
    )


def create_optimized_face_processing_group(
    face_marker, face_animator, face_swap_insight, face_swap_dfm
):
    """Create optimized group for face processing components"""
    components = [
        (face_marker, "Face Marker"),
        (face_animator, "Face Animator"),
        (face_swap_insight, "Face Swap Insight"),
        (face_swap_dfm, "Face Swap DFM"),
    ]

    return QSmartCollapsibleGroup(
        title="Face Processing",
        components=components,
        max_visible_components=2,  # Show 2 by default, collapse the rest
    )


def create_optimized_frame_processing_group(frame_adjuster, face_merger):
    """Create optimized group for frame processing components"""
    components = [(frame_adjuster, "Frame Adjuster"), (face_merger, "Face Merger")]

    return QSmartCollapsibleGroup(
        title="Frame Processing", components=components, max_visible_components=2
    )
