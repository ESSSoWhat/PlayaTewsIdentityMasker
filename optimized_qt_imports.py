#!/usr/bin/env python3
"""
Optimized Qt Imports Module
Replaces wildcard imports with specific imports and lazy loading for better performance
"""

# Import only essential Qt components at module level
from PyQt5.QtCore import (
    Qt, QTimer, QTimeLine, QObject, QThread, pyqtSignal, pyqtSlot,
    QRect, QRectF, QPoint, QPointF, QSize, QSizeF,
    QMargins, QMarginsF, QUrl, QDateTime, QDate, QTime,
    QPropertyAnimation, QEasingCurve, QVariantAnimation,
    QAbstractAnimation, QSequentialAnimationGroup, QParallelAnimationGroup
)

from PyQt5.QtGui import (
    QIcon, QPixmap, QImage, QPainter, QPen, QBrush, QColor, QFont,
    QFontMetrics, QPalette, QLinearGradient, QRadialGradient,
    QKeySequence, QAction, QMouseEvent, QKeyEvent, QPaintEvent,
    QResizeEvent, QCloseEvent, QShowEvent, QHideEvent
)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QRadioButton, QSlider, QProgressBar, QScrollArea,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QStackedLayout,
    QSizePolicy, QSpacerItem, QGroupBox, QTabWidget, QSplitter,
    QMenuBar, QMenu, QToolBar, QStatusBar, QDialog, QMessageBox,
    QFileDialog, QColorDialog, QFontDialog
)

# Alignment constants (optimized)
AlignLeft = Qt.AlignLeft
AlignLeading = Qt.AlignLeading
AlignRight = Qt.AlignRight
AlignTrailing = Qt.AlignTrailing
AlignHCenter = Qt.AlignHCenter
AlignJustify = Qt.AlignJustify
AlignAbsolute = Qt.AlignAbsolute
AlignHorizontal_Mask = Qt.AlignHorizontal_Mask
AlignTop = Qt.AlignTop
AlignBottom = Qt.AlignBottom
AlignVCenter = Qt.AlignVCenter
AlignVertical_Mask = Qt.AlignVertical_Mask
AlignCenter = Qt.AlignCenter
AlignBaseline = Qt.AlignBaseline

# Lazy loading for heavy custom widgets
_custom_widgets = {}

def _lazy_import(module_name, class_name):
    """Lazy import helper for custom widgets"""
    if class_name not in _custom_widgets:
        try:
            module = __import__(f"xlib.qt.{module_name}", fromlist=[class_name])
            _custom_widgets[class_name] = getattr(module, class_name)
        except ImportError as e:
            print(f"Warning: Could not import {class_name}: {e}")
            return None
    return _custom_widgets[class_name]

# Lazy loading properties for custom widgets
@property
def QXTimeLine():
    return _lazy_import("core.QXTimeLine", "QXTimeLine")

@property
def QXTimer():
    return _lazy_import("core.QXTimer", "QXTimer")

@property
def QXCheckBox():
    return _lazy_import("widgets.QXCheckBox", "QXCheckBox")

@property
def QXCollapsibleSection():
    return _lazy_import("widgets.QXCollapsibleSection", "QXCollapsibleSection")

@property
def QXComboBox():
    return _lazy_import("widgets.QXComboBox", "QXComboBox")

@property
def QXDirDialog():
    return _lazy_import("widgets.QXDirDialog", "QXDirDialog")

@property
def QXDoubleSpinBox():
    return _lazy_import("widgets.QXDoubleSpinBox", "QXDoubleSpinBox")

@property
def QXFileDialog():
    return _lazy_import("widgets.QXFileDialog", "QXFileDialog")

@property
def QXFixedLayeredImages():
    return _lazy_import("widgets.QXFixedLayeredImages", "QXFixedLayeredImages")

@property
def QXFrame():
    return _lazy_import("widgets.QXFrame", "QXFrame")

@property
def QXFrameHBox():
    return _lazy_import("widgets.QXFrameHBox", "QXFrameHBox")

@property
def QXFrameVBox():
    return _lazy_import("widgets.QXFrameVBox", "QXFrameVBox")

@property
def QXGridLayout():
    return _lazy_import("widgets.QXGridLayout", "QXGridLayout")

@property
def QXHBoxLayout():
    return _lazy_import("widgets.QXHBoxLayout", "QXHBoxLayout")

@property
def QXHorizontalLine():
    return _lazy_import("widgets.QXHorizontalLine", "QXHorizontalLine")

@property
def QXLabel():
    return _lazy_import("widgets.QXLabel", "QXLabel")

@property
def QXLineEdit():
    return _lazy_import("widgets.QXLineEdit", "QXLineEdit")

@property
def QXMainApplication():
    return _lazy_import("widgets.QXMainApplication", "QXMainApplication")

@property
def QXMenuBar():
    return _lazy_import("widgets.QXMenuBar", "QXMenuBar")

@property
def QXOpenGLWidget():
    return _lazy_import("widgets.QXOpenGLWidget", "QXOpenGLWidget")

@property
def QXPopupWindow():
    return _lazy_import("widgets.QXPopupWindow", "QXPopupWindow")

@property
def QXProgressBar():
    return _lazy_import("widgets.QXProgressBar", "QXProgressBar")

@property
def QXPushButton():
    return _lazy_import("widgets.QXPushButton", "QXPushButton")

@property
def QXRadioButton():
    return _lazy_import("widgets.QXRadioButton", "QXRadioButton")

@property
def QXSaveableComboBox():
    return _lazy_import("widgets.QXSaveableComboBox", "QXSaveableComboBox")

@property
def QXScrollArea():
    return _lazy_import("widgets.QXScrollArea", "QXScrollArea")

@property
def QXSlider():
    return _lazy_import("widgets.QXSlider", "QXSlider")

@property
def QXSpinBox():
    return _lazy_import("widgets.QXSpinBox", "QXSpinBox")

@property
def QXSplashWindow():
    return _lazy_import("widgets.QXSplashWindow", "QXSplashWindow")

@property
def QXTextEdit():
    return _lazy_import("widgets.QXTextEdit", "QXTextEdit")

@property
def QXToolButton():
    return _lazy_import("widgets.QXToolButton", "QXToolButton")

@property
def QXVBoxLayout():
    return _lazy_import("widgets.QXVBoxLayout", "QXVBoxLayout")

@property
def QXVerticalLine():
    return _lazy_import("widgets.QXVerticalLine", "QXVerticalLine")

@property
def QXWidget():
    return _lazy_import("widgets.QXWidget", "QXWidget")

@property
def QXWidgetHBox():
    return _lazy_import("widgets.QXWidgetHBox", "QXWidgetHBox")

@property
def QXWidgetVBox():
    return _lazy_import("widgets.QXWidgetVBox", "QXWidgetVBox")

@property
def QXWindow():
    return _lazy_import("widgets.QXWindow", "QXWindow")

# Helper functions for widget manipulation
def BlockSignals(obj):
    """Block signals for an object temporarily"""
    from .core.widget import BlockSignals as _BlockSignals
    return _BlockSignals(obj)

def disable(widget):
    """Disable a widget"""
    widget.setEnabled(False)

def enable(widget):
    """Enable a widget"""
    widget.setEnabled(True)

def hide(widget):
    """Hide a widget"""
    widget.hide()

def show(widget):
    """Show a widget"""
    widget.show()

def hide_and_disable(widget):
    """Hide and disable a widget"""
    widget.hide()
    widget.setEnabled(False)

def show_and_enable(widget):
    """Show and enable a widget"""
    widget.show()
    widget.setEnabled(True)

# Image and pixmap helpers
def QIcon_from_file(filepath):
    """Load QIcon from file"""
    from .gui.from_file import QIcon_from_file as _QIcon_from_file
    return _QIcon_from_file(filepath)

def QPixmap_from_file(filepath):
    """Load QPixmap from file"""
    from .gui.from_file import QPixmap_from_file as _QPixmap_from_file
    return _QPixmap_from_file(filepath)

def QXImage_from_file(filepath):
    """Load QXImage from file"""
    from .gui.from_file import QXImage_from_file as _QXImage_from_file
    return _QXImage_from_file(filepath)

def QXPixmap_from_file(filepath):
    """Load QXPixmap from file"""
    from .gui.from_file import QXPixmap_from_file as _QXPixmap_from_file
    return _QXPixmap_from_file(filepath)

def QImage_ARGB32_from_buffer(buffer, width, height):
    """Create QImage from buffer"""
    from .gui.from_np import QImage_ARGB32_from_buffer as _QImage_ARGB32_from_buffer
    return _QImage_ARGB32_from_buffer(buffer, width, height)

def QImage_BGR888_from_buffer(buffer, width, height):
    """Create QImage from BGR buffer"""
    from .gui.from_np import QImage_BGR888_from_buffer as _QImage_BGR888_from_buffer
    return _QImage_BGR888_from_buffer(buffer, width, height)

def QPixmap_from_np(array):
    """Create QPixmap from numpy array"""
    from .gui.from_np import QPixmap_from_np as _QPixmap_from_np
    return _QPixmap_from_np(array)

# Image sequence support
@property
def QXImageSequence():
    return _lazy_import("gui.QXImageSequence", "QXImageSequence")

@property
def QXPixmap():
    return _lazy_import("gui.QXPixmap", "QXPixmap")

__all__ = [
    # Core Qt classes
    'Qt', 'QTimer', 'QTimeLine', 'QObject', 'QThread', 'pyqtSignal', 'pyqtSlot',
    'QRect', 'QRectF', 'QPoint', 'QPointF', 'QSize', 'QSizeF',
    'QMargins', 'QMarginsF', 'QUrl', 'QDateTime', 'QDate', 'QTime',
    'QPropertyAnimation', 'QEasingCurve', 'QVariantAnimation',
    'QAbstractAnimation', 'QSequentialAnimationGroup', 'QParallelAnimationGroup',
    
    # GUI classes
    'QIcon', 'QPixmap', 'QImage', 'QPainter', 'QPen', 'QBrush', 'QColor', 'QFont',
    'QFontMetrics', 'QPalette', 'QLinearGradient', 'QRadialGradient',
    'QKeySequence', 'QAction', 'QMouseEvent', 'QKeyEvent', 'QPaintEvent',
    'QResizeEvent', 'QCloseEvent', 'QShowEvent', 'QHideEvent',
    
    # Widget classes
    'QApplication', 'QMainWindow', 'QWidget', 'QFrame', 'QLabel', 'QPushButton',
    'QLineEdit', 'QTextEdit', 'QComboBox', 'QSpinBox', 'QDoubleSpinBox',
    'QCheckBox', 'QRadioButton', 'QSlider', 'QProgressBar', 'QScrollArea',
    'QVBoxLayout', 'QHBoxLayout', 'QGridLayout', 'QFormLayout', 'QStackedLayout',
    'QSizePolicy', 'QSpacerItem', 'QGroupBox', 'QTabWidget', 'QSplitter',
    'QMenuBar', 'QMenu', 'QToolBar', 'QStatusBar', 'QDialog', 'QMessageBox',
    'QFileDialog', 'QColorDialog', 'QFontDialog',
    
    # Alignment constants
    'AlignLeft', 'AlignLeading', 'AlignRight', 'AlignTrailing', 'AlignHCenter',
    'AlignJustify', 'AlignAbsolute', 'AlignHorizontal_Mask', 'AlignTop',
    'AlignBottom', 'AlignVCenter', 'AlignVertical_Mask', 'AlignCenter', 'AlignBaseline',
    
    # Helper functions
    'BlockSignals', 'disable', 'enable', 'hide', 'show', 'hide_and_disable', 'show_and_enable',
    'QIcon_from_file', 'QPixmap_from_file', 'QXImage_from_file', 'QXPixmap_from_file',
    'QImage_ARGB32_from_buffer', 'QImage_BGR888_from_buffer', 'QPixmap_from_np',
]