#!/usr/bin/env python3
"""
Grouped Input Sources Component
Combines file and camera sources for better organization
"""

from xlib import qt as qtx
from xlib.qt.widgets.QXCollapsibleSection import QXCollapsibleSection


class QGroupedInputSources(QXCollapsibleSection):
    """Grouped input sources (file and camera)"""
    
    def __init__(self, file_source, camera_source):
        content_layout = qtx.QXVBoxLayout()
        
        # Add components with spacing
        content_layout.addWidget(file_source)
        content_layout.addWidget(camera_source)
        
        super().__init__(
            "Input Sources",
            content_layout,
            False,  # vertical
            True,   # is_opened
            True    # allow_open_close
        ) 