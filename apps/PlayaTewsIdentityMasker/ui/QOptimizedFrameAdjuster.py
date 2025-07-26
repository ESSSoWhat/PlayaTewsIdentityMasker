#!/usr/bin/env python3
"""
Optimized Frame Adjuster Component
Uses collapsible wrapper for better space utilization
"""

from .QFrameAdjuster import QFrameAdjuster
from .widgets.QCollapsibleComponentWrapper import QCollapsibleComponentWrapper


class QOptimizedFrameAdjuster(QCollapsibleComponentWrapper):
    """Optimized frame adjuster with collapsible interface"""
    
    def __init__(self, backend):
        frame_adjuster = QFrameAdjuster(backend)
        super().__init__(
            component=frame_adjuster,
            title="Frame Adjuster",
            is_opened=False,  # Start collapsed since it's small (2 sliders)
            auto_collapse_threshold=4
        ) 