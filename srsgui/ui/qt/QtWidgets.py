"""
Adapter module for QtWidgets package for both PyQt5 and PySide2.
"""

from . import QT_BINDER, PYQT5, PYSIDE2

if QT_BINDER == PYQT5:
    from PyQt5.QtWidgets import *

elif QT_BINDER == PYSIDE2:
    from PySide2.QtWidgets import *

else:
    raise Exception('QT_BINDER is not defined')
