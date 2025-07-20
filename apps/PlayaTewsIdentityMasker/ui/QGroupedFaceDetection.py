#!/usr/bin/env python3
"""
Grouped Face Detection and Alignment Component
Combines related functionality for better organization
"""

from xlib import qt as qtx
from xlib.qt.widgets.QXCollapsibleSection import QXCollapsibleSection


class QGroupedFaceDetection(QXCollapsibleSection):
    """Grouped face detection and alignment components"""
    
    def __init__(self, face_detector, face_aligner):
        content_layout = qtx.QXVBoxLayout()
        
        # Add components with spacing
        content_layout.addWidget(face_detector)
        content_layout.addWidget(face_aligner)
        
        super().__init__(
            "Face Detection & Alignment",
            content_layout,
            False,  # vertical
            True,   # is_opened
            True    # allow_open_close
        ) 