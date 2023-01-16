"""
Adapter module for QtCore package for both PyQt5 and PySide2.
"""

# For full extension, use QtPy

from . import QT_BINDER, PYQT5, PYSIDE2

if QT_BINDER == PYQT5:
    from PyQt5.QtCore import *
    from PyQt5.QtCore import pyqtSignal as Signal
    from PyQt5.QtCore import pyqtSlot as Slot

elif QT_BINDER == PYSIDE2:
    from PySide2.QtCore import *

else:
    raise Exception('QT_BINDER is not defined')
