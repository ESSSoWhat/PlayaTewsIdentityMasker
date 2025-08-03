#!/usr/bin/env python3
"""
Optimized Face Marker Component
Uses collapsible wrapper for better space utilization
"""

from .QFaceMarker import QFaceMarker
from .widgets.QCollapsibleComponentWrapper import QCollapsibleComponentWrapper


class QOptimizedFaceMarker(QCollapsibleComponentWrapper):
    """Optimized face marker with collapsible interface"""

    def __init__(self, backend):
        face_marker = QFaceMarker(backend)
        super().__init__(
            component=face_marker,
            title="Face Marker",
            is_opened=False,  # Start collapsed since it's small (4 settings)
            auto_collapse_threshold=4,
        )
