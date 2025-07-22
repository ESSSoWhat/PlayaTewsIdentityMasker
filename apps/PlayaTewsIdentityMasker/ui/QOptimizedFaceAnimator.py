#!/usr/bin/env python3
"""
Optimized Face Animator Component
Uses collapsible wrapper for better space utilization
"""

from .QFaceAnimator import QFaceAnimator
from .widgets.QCollapsibleComponentWrapper import QCollapsibleComponentWrapper


class QOptimizedFaceAnimator(QCollapsibleComponentWrapper):
    """Optimized face animator with collapsible interface"""
    
    def __init__(self, backend, animatables_path=None):
        face_animator = QFaceAnimator(backend, animatables_path=animatables_path)
        super().__init__(
            component=face_animator,
            title="Face Animator",
            is_opened=False,  # Start collapsed since it's small (3 settings)
            auto_collapse_threshold=4
        ) 