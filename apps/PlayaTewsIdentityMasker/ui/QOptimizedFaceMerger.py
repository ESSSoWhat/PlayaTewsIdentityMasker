#!/usr/bin/env python3
"""
Optimized Face Merger Component
Uses collapsible wrapper for better space utilization
"""

from .QFaceMerger import QFaceMerger
from .widgets.QCollapsibleComponentWrapper import QCollapsibleComponentWrapper


class QOptimizedFaceMerger(QCollapsibleComponentWrapper):
    """Optimized face merger with collapsible interface"""
    
    def __init__(self, backend):
        face_merger = QFaceMerger(backend)
        super().__init__(
            component=face_merger,
            title="Face Merger",
            is_opened=False,  # Start collapsed since it's small (3 settings)
            auto_collapse_threshold=4
        ) 