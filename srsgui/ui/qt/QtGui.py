"""
Adapter module for QtGui package for  PySide6, PySide2 and PyQt5
"""

# For full extension, use QtPy package

from . import QT_BINDER, PYSIDE6, PYSIDE2, PYQT6, PYQT5

if QT_BINDER == PYSIDE6:
    from PySide6.QtGui import *
    del QAction
    del QShortcut
    
elif QT_BINDER == PYSIDE2:
    from PySide2.QtGui import *

elif QT_BINDER == PYQT6:
    from PyQt6.QtGui import *
    del QAction
    del QShortcut

elif QT_BINDER == PYQT5:
    from PyQt5.QtGui import *

else:
    raise Exception('QT_BINDER is not defined in')
