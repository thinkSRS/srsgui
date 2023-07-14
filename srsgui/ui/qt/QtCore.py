##! 
##! Copyright(c) 2022, 2023 Stanford Research Systems, All rights reserved
##! Subject to the MIT License
##! 

"""
Adapter module for QtCore package for PySide6, PySide2 and PyQt5.
"""

# For full extension, use QtPy package

from . import QT_BINDER, PYSIDE6, PYSIDE2, PYQT6, PYQT5

if QT_BINDER == PYSIDE6:
    from PySide6.QtCore import *

elif QT_BINDER == PYSIDE2:
    from PySide2.QtCore import *

elif QT_BINDER == PYQT6:
    from PyQt6.QtCore import *
    from PyQt6.QtCore import pyqtSignal as Signal
    from PyQt6.QtCore import pyqtSlot as Slot

elif QT_BINDER == PYQT5:
    from PyQt5.QtCore import *
    from PyQt5.QtCore import pyqtSignal as Signal
    from PyQt5.QtCore import pyqtSlot as Slot

else:
    raise Exception('QT_BINDER is not defined')
