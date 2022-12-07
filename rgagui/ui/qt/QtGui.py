
from . import QT_BINDER, PYQT5, PYSIDE2

if QT_BINDER == PYQT5:
    from PyQt5.QtGui import *

elif QT_BINDER == PYSIDE2:
    from PySide2.QtGui import *

else:
    raise Exception('QT_BINDER is not defined in')
