from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .QXWindow import QXWindow


class QXSplashWindow(QXWindow):
    def __init__(self, **kwargs):
        """
        represents top widget which has no parent
        """
        super().__init__(**kwargs)
        self.setWindowFlags(Qt.WindowType.SplashScreen)
