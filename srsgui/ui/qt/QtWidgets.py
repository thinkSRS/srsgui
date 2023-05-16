##! 
##! Coptright(c) 2022, 2023 Stanford Research Systems, All right reserved
##! Subject to the MIT License
##! 

"""
Adapter module for QtWidgets package for PySide6, PySide2 and PyQt5
"""

# For full extension, use QtPy package

from . import QT_BINDER, PYSIDE6, PYSIDE2, PYQT6, PYQT5

if QT_BINDER == PYSIDE6:
    from PySide6.QtWidgets import *
    from PySide6.QtGui import QAction
    from PySide6.QtGui import QShortcut
    
elif QT_BINDER == PYSIDE2:
    from PySide2.QtWidgets import *

elif QT_BINDER == PYQT6:
    from PyQt6.QtWidgets import *
    from PyQt6.QtGui import QAction
    from PyQt6.QtGui import QShortcut

elif QT_BINDER == PYQT5:
    from PyQt5.QtWidgets import *

else:
    raise Exception('QT_BINDER is not defined')
