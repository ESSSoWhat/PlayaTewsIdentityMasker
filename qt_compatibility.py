"""
Qt Compatibility Layer for PyQt5/PyQt6 Migration

This module provides a compatibility layer that supports both PyQt5 and PyQt6,
allowing for smooth migration between the two versions.
"""

import sys

# Try to import PyQt5 first (preferred for compatibility)
try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtOpenGL import *
    PYQT_VERSION = 5
    print("Using PyQt5 for compatibility")
except ImportError:
    try:
        from PyQt6.QtWidgets import *
        from PyQt6.QtCore import *
        from PyQt6.QtGui import *
        from PyQt6.QtOpenGL import *
        PYQT_VERSION = 6
        print("Using PyQt6 (fallback)")
    except ImportError:
        raise ImportError("Neither PyQt5 nor PyQt6 is available. Please install one of them.")

# Compatibility constants for alignment flags
if PYQT_VERSION == 6:
    # PyQt6 alignment flags (enum-based)
    AlignLeft = Qt.AlignmentFlag.AlignLeft
    AlignLeading = Qt.AlignmentFlag.AlignLeading
    AlignRight = Qt.AlignmentFlag.AlignRight
    AlignTrailing = Qt.AlignmentFlag.AlignTrailing
    AlignHCenter = Qt.AlignmentFlag.AlignHCenter
    AlignJustify = Qt.AlignmentFlag.AlignJustify
    AlignAbsolute = Qt.AlignmentFlag.AlignAbsolute
    AlignHorizontal_Mask = Qt.AlignmentFlag.AlignHorizontal_Mask
    AlignTop = Qt.AlignmentFlag.AlignTop
    AlignBottom = Qt.AlignmentFlag.AlignBottom
    AlignVCenter = Qt.AlignmentFlag.AlignVCenter
    AlignVertical_Mask = Qt.AlignmentFlag.AlignVertical_Mask
    AlignCenter = Qt.AlignmentFlag.AlignCenter
    AlignBaseline = Qt.AlignmentFlag.AlignBaseline
else:
    # PyQt5 alignment constants (direct)
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

# Compatibility functions
def get_qt_version():
    """Get the current Qt version being used"""
    return PYQT_VERSION

def is_pyqt5():
    """Check if PyQt5 is being used"""
    return PYQT_VERSION == 5

def is_pyqt6():
    """Check if PyQt6 is being used"""
    return PYQT_VERSION == 6

def get_alignment_constant(alignment_name):
    """Get alignment constant by name, compatible with both PyQt5 and PyQt6"""
    alignment_map = {
        'AlignLeft': AlignLeft,
        'AlignLeading': AlignLeading,
        'AlignRight': AlignRight,
        'AlignTrailing': AlignTrailing,
        'AlignHCenter': AlignHCenter,
        'AlignJustify': AlignJustify,
        'AlignAbsolute': AlignAbsolute,
        'AlignHorizontal_Mask': AlignHorizontal_Mask,
        'AlignTop': AlignTop,
        'AlignBottom': AlignBottom,
        'AlignVCenter': AlignVCenter,
        'AlignVertical_Mask': AlignVertical_Mask,
        'AlignCenter': AlignCenter,
        'AlignBaseline': AlignBaseline,
    }
    return alignment_map.get(alignment_name, AlignLeft)

# Export all Qt classes and constants
__all__ = [
    # Qt classes
    'QWidget', 'QVBoxLayout', 'QHBoxLayout', 'QGroupBox', 'QLabel', 'QSlider',
    'QComboBox', 'QCheckBox', 'QSpinBox', 'QDoubleSpinBox', 'QPushButton',
    'QTabWidget', 'QGridLayout', 'QApplication', 'QMainWindow', 'QDialog',
    'QMessageBox', 'QFileDialog', 'QColorDialog', 'QFontDialog',
    'QTextEdit', 'QLineEdit', 'QTextBrowser', 'QProgressBar', 'QStatusBar',
    'QMenuBar', 'QToolBar', 'QMenu', 'QAction', 'QToolButton', 'QRadioButton',
    'QListWidget', 'QTreeWidget', 'QTableWidget', 'QScrollArea', 'QSplitter',
    'QFrame', 'QStackedWidget', 'QCalendarWidget', 'QDateEdit', 'QTimeEdit',
    'QDateTimeEdit', 'QSlider', 'QScrollBar', 'QDial', 'QLCDNumber',
    'QOpenGLWidget', 'QOpenGLContext', 'QOpenGLFunctions',
    
    # Qt core classes
    'Qt', 'pyqtSignal', 'pyqtSlot', 'QObject', 'QThread', 'QTimer', 'QEvent',
    'QEventLoop', 'QCoreApplication', 'QSettings', 'QDir', 'QFile', 'QFileInfo',
    'QUrl', 'QPoint', 'QPointF', 'QSize', 'QSizeF', 'QRect', 'QRectF',
    'QDateTime', 'QDate', 'QTime', 'QStringListModel', 'QStandardItemModel',
    'QAbstractItemModel', 'QModelIndex', 'QPersistentModelIndex',
    
    # Qt GUI classes
    'QFont', 'QPalette', 'QColor', 'QBrush', 'QPen', 'QPixmap', 'QImage',
    'QIcon', 'QCursor', 'QPainter', 'QPainterPath', 'QRegion', 'QPolygon',
    'QPolygonF', 'QTransform', 'QMatrix', 'QFontMetrics', 'QFontInfo',
    'QFontDatabase', 'QClipboard', 'QDrag', 'QDropEvent', 'QDragEnterEvent',
    'QDragLeaveEvent', 'QDragMoveEvent', 'QDropEvent',
    
    # Alignment constants
    'AlignLeft', 'AlignLeading', 'AlignRight', 'AlignTrailing', 'AlignHCenter',
    'AlignJustify', 'AlignAbsolute', 'AlignHorizontal_Mask', 'AlignTop',
    'AlignBottom', 'AlignVCenter', 'AlignVertical_Mask', 'AlignCenter',
    'AlignBaseline',
    
    # Compatibility functions
    'get_qt_version', 'is_pyqt5', 'is_pyqt6', 'get_alignment_constant',
    'PYQT_VERSION'
]